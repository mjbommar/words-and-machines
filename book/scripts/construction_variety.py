#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pydetex>=1.1.1",
#     "nupunkt>=0.6.0",
# ]
# ///
"""Sentence-construction variety: openers, length shapes, branching.

The syntax sibling of `make vocab`. Where vocab_variety.py finds words
you over-use, this finds *shapes* you over-use — the sentence openers,
length bands, and clause architectures a draft keeps reaching for.
Machine-assisted prose converges hard here: the same subject-first
declarative at the same length, or a wall of "However, ..." /
"Building on that, ..." openers (STYLE-AI-TELLS Part 6, tell 2.x).

Three things are measured per sentence:

  opener      one of a fixed inventory of opener classes (below), chosen
              by a documented priority order so every sentence lands in
              exactly one class
  length      band: very-short <=8, short 9-15, medium 16-24,
              long 25-35, very-long 36+ words
  architecture  gross clause shape, POS-lite:
              LB   left-branching / suspended — opens with a
                   subordinate, participial or infinitive clause
              CUM  cumulative — a free modifier trails the final comma
              ;:   semicolon or colon present
              poly polysyndeton density (same coordinator 3+ times)

Reported per chapter: the opener distribution, an opener-diversity index
(odi — normalized Shannon entropy over the 15-class inventory, 0..1),
the length bands, over-represented patterns with example sentences and
line numbers, and consecutive-repeat runs (3+ sentences opening the same
way — the classic tell). If
scripts/data/ontology/syntactic_constructions.json exists, the report
closes with a few seeded constructions to reach for instead; without it
the report is simply shorter.

Read odi one-way. Low odi means monotony; high odi does NOT certify
variety, because a wall of "However, ... / Moreover, ... / Building on
that, ..." spreads across many classes and scores high. Subject-first is
the unmarked order of English, so healthy prose is dominated by it: this
template's edited chapters sit at odi 0.25-0.36 with subject-first
69-81%, which is why the defaults (odi >= 0.20, subject-first <= 85%)
sit below them with margin. The run and over-representation checks carry
most of the signal; treat odi as context.

Complements check_prose.py's `opener-run`, which matches on the literal
first *word*; this matches on the opener *type*, so "However, ... /
Instead, ... / Later, ..." reads as a 3-run here and as nothing there.

Everything is advisory: exit 0 unless --strict, which fails on
--max-run / --max-subject-run / --min-odi.

POS-lite by design: word lists and suffix rules, no tagger, no spaCy.
Known misses are listed under LIMITS at the bottom of this docstring.

Usage:
    uv run scripts/construction_variety.py                  # per-chapter table
    uv run scripts/construction_variety.py --detail         # + examples/runs
    uv run scripts/construction_variety.py --chapter ch02 --detail
    uv run scripts/construction_variety.py --text draft.txt # plain prose
    uv run scripts/construction_variety.py --root ../other-book
    uv run scripts/construction_variety.py --json
    uv run scripts/construction_variety.py --strict

LIMITS
  - Ambiguous openers ("As", "Since", "Before", "After") are read as
    subordinators only when a comma follows within 15 words; otherwise
    they fall to `prepositional`. Comma-less initial clauses are missed.
  - `imperative` is a curated verb list, so unusual imperatives read as
    `subject-first`.
  - Left-branching detection needs the comma; "Because he left we ate"
    is missed.
  - No coordination-depth or embedding-depth measure; "architecture" here
    is gross shape only.
  - Runs must sit inside one paragraph; a habit that straddles a
    paragraph break is reported as two shorter runs.
  - Units under --min-sents (15) sentences are skipped — colophons and
    copyright pages produce meaningless distributions.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
import statistics
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------- corpus

# same corpus recipe as check_prose.py / prose_metrics.py / vocab_variety.py
SUBDIRS = ("chapters", "frontmatter", "front-matter", "backmatter", "back-matter")
DROP_ENVS = (
    "tikzpicture", "figure", "table", "tabular", "tabularx", "lstlisting",
    "verbatim", "Verbatim", "equation", "align", "alignat", "gather",
    "definitionbox", "tryitbox", "examplebox", "codelisting", "promptcode",
    "outputcode",
)
# commands whose braced argument is not body prose
DROP_ARG_CMDS = (
    "chapter", "section", "subsection", "subsubsection", "paragraph",
    "subparagraph", "part", "title", "subtitle", "author", "caption",
    "attribution", "label", "ref", "autoref", "cref", "Cref", "vref",
    "eqref", "pageref", "nameref", "index", "input", "include",
    "includegraphics", "bibliography", "addbibresource", "url", "cite",
    "citep", "citet", "parencite", "parencites", "autocite", "autocites",
    "textcite", "textcites", "footcite", "nocite", "smartcite",
    "supercite", "fullcite", "citeauthor", "citeyear", "citetitle",
    "usepackage", "documentclass", "hypersetup", "setlength", "newcommand",
    "renewcommand",
)
EXPAND = {
    r"\LaTeX": "LaTeX", r"\TeX": "TeX", r"\BibTeX": "BibTeX",
    r"\ldots": "...", r"\dots": "...",
}
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'\u2019-]*")


def _blank(m: re.Match) -> str:
    """Erase a span but keep its newlines, so line numbers survive."""
    return re.sub(r"[^\n]", " ", m.group(0))


def _drop_cmd_args(text: str, names: tuple[str, ...]) -> str:
    """Remove `\\cmd[opt]{...}{...}` — command and every following braced
    group — with brace matching, newline-preserving."""
    pattern = re.compile(r"\\(?:" + "|".join(names) + r")\*?")
    out, i = [], 0
    while True:
        m = pattern.search(text, i)
        if not m:
            out.append(text[i:])
            break
        out.append(text[i:m.start()])
        j = m.end()
        while j < len(text):
            k = j
            while k < len(text) and text[k] in " \t":
                k += 1
            if k < len(text) and text[k] == "[":
                depth, k2 = 1, k + 1
                while k2 < len(text) and depth:
                    depth += (text[k2] == "[") - (text[k2] == "]")
                    k2 += 1
                j = k2
                continue
            if k < len(text) and text[k] == "{":
                depth, k2 = 1, k + 1
                while k2 < len(text) and depth:
                    depth += (text[k2] == "{") - (text[k2] == "}")
                    k2 += 1
                j = k2
                continue
            break
        out.append(re.sub(r"[^\n]", " ", text[m.start():j]))
        i = j
    return "".join(out)


def strip_latex_lines(source: str) -> str:
    """Detex while preserving line numbering (regex-only, like
    prose_metrics.light_detex, plus brace-matched argument removal)."""
    text = source
    for esc, sent in ((r"\%", "\x00P"), (r"\&", "\x00A"), (r"\$", "\x00D"),
                      (r"\#", "\x00H"), (r"\_", "\x00U")):
        text = text.replace(esc, sent)
    text = re.sub(r"%[^\n]*", "", text)
    for env in DROP_ENVS:
        text = re.sub(rf"\\begin\{{{env}\*?\}}.*?\\end\{{{env}\*?\}}",
                      _blank, text, flags=re.DOTALL)
    text = re.sub(r"\\\[.*?\\\]", _blank, text, flags=re.DOTALL)
    text = re.sub(r"\$\$.*?\$\$", _blank, text, flags=re.DOTALL)
    text = re.sub(r"\$[^$\n]*\$", _blank, text)
    text = re.sub(r"\\href\{[^}]*\}", " ", text)        # keep the link text
    text = _drop_cmd_args(text, DROP_ARG_CMDS)
    text = re.sub(r"\\(?:begin|end)\{[A-Za-z*]+\}(?:\[[^\]]*\])?"
                  r"(?:\{[^}]*\})*", " ", text)
    for macro, plain in EXPAND.items():
        text = text.replace(macro + "{}", plain).replace(macro, plain)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", text)
    text = re.sub(r"\\[^A-Za-z\n]", " ", text)
    text = text.replace("``", '"').replace("''", '"').replace("`", "'")
    text = text.replace("---", "\u2014").replace("--", "\u2013")
    text = re.sub(r"[{}~^]", " ", text)
    for sent, plain in (("\x00P", "%"), ("\x00A", "&"), ("\x00D", "$"),
                        ("\x00H", "#"), ("\x00U", "_")):
        text = text.replace(sent, plain)
    return re.sub(r"[ \t]+", " ", text)


@dataclass
class Sent:
    text: str
    line: int
    para: int
    words: list[str] = field(default_factory=list)


def sentences_of(text: str, tok, min_words: int) -> list[Sent]:
    """Split line-preserved text into sentences carrying source lines."""
    lines = text.split("\n")
    out: list[Sent] = []
    para_idx = 0
    buf: list[tuple[int, str]] = []

    def flush(buf: list[tuple[int, str]], para_idx: int) -> None:
        if not buf:
            return
        joined, offsets = "", []
        for lineno, content in buf:
            if joined:
                joined += " "
            offsets.append((len(joined), lineno))
            joined += content
        if len(joined.split()) < 4:
            return
        cursor = 0
        for raw in tok.tokenize(joined):
            s = raw.strip()
            if not s:
                continue
            idx = joined.find(s, cursor)
            if idx < 0:
                idx = cursor
            cursor = idx + len(s)
            line = offsets[0][1]
            for off, lineno in offsets:
                if off <= idx:
                    line = lineno
                else:
                    break
            words = TOKEN_RE.findall(s)
            if len(words) < min_words:
                continue
            out.append(Sent(text=s, line=line, para=para_idx, words=words))

    for i, raw in enumerate(lines, start=1):
        content = raw.strip()
        if content:
            buf.append((i, content))
        else:
            flush(buf, para_idx)
            if buf:
                para_idx += 1
            buf = []
    flush(buf, para_idx)
    return out


def discover(root: Path) -> list[Path]:
    files: list[Path] = []
    for name in SUBDIRS:
        d = root / "latex" / name
        if d.exists():
            files += sorted(d.glob("*.tex"))
    if not files:
        # --root may point at the chapters dir itself (rhythm_audit pattern)
        files = sorted(root.glob("*.tex"))
    return files


# ------------------------------------------------------- POS-lite lexicons

COORD = {"and", "but", "or", "nor", "yet", "so", "for"}
# unambiguously subordinating — no comma required
SUB_HARD = {
    "although", "though", "because", "if", "unless", "whereas", "while",
    "whether", "wherever", "whenever", "albeit", "lest", "provided",
    "supposing", "insofar", "inasmuch",
}
# also prepositions — need a following comma to read as a clause opener
SUB_SOFT = {
    "as", "since", "when", "after", "before", "until", "till", "once",
    "where",
}
EXPLETIVE_BE = {"is", "was", "are", "were", "will", "would", "has", "had",
                "can", "could", "may", "might", "must", "seems", "seemed",
                "remains", "remained", "turns", "turned", "comes", "came",
                "appears", "appeared", "used"}
INTERROG = {
    "who", "whom", "whose", "what", "which", "when", "where", "why", "how",
    "is", "are", "was", "were", "do", "does", "did", "can", "could",
    "should", "would", "will", "shall", "may", "might", "must", "have",
    "has", "had", "am", "aren't", "isn't", "don't", "doesn't", "didn't",
}
PREPOSITIONS = {
    "about", "above", "across", "after", "against", "along", "amid",
    "among", "around", "at", "before", "behind", "below", "beneath",
    "beside", "besides", "between", "beyond", "by", "despite", "down",
    "during", "except", "for", "from", "in", "inside", "into", "near",
    "of", "off", "on", "onto", "opposite", "out", "outside", "over",
    "past", "per", "since", "through", "throughout", "till", "to",
    "toward", "towards", "under", "underneath", "unlike", "until", "up",
    "upon", "via", "with", "within", "without",
}
# discourse connectives — the AI-tell family; single words and phrases
TRANSITIONAL = {
    "however", "moreover", "furthermore", "additionally", "therefore",
    "thus", "hence", "consequently", "nevertheless", "nonetheless",
    "meanwhile", "conversely", "similarly", "likewise", "accordingly",
    "indeed", "ultimately", "notably", "importantly", "crucially",
    "critically", "significantly", "essentially", "fundamentally",
    "overall", "regardless", "instead", "besides", "still", "yet",
    "first", "firstly", "second", "secondly", "third", "thirdly",
    "finally", "lastly", "next",
}
TRANSITIONAL_PHRASES = (
    "in fact", "in short", "in other words", "in contrast", "in addition",
    "in particular", "in practice", "in theory", "in the end", "of course",
    "that said", "on the other hand", "on the contrary", "as a result",
    "at the same time", "for example", "for instance", "by contrast",
    "more broadly", "more precisely", "put differently", "even so",
    "above all", "after all", "to be clear", "to be fair", "in general",
)
ADVERB_WORDS = {
    "then", "now", "later", "soon", "often", "sometimes", "always",
    "never", "rarely", "seldom", "usually", "today", "tomorrow",
    "yesterday", "once", "twice", "again", "here", "there", "everywhere",
    "somewhere", "nowhere", "perhaps", "maybe", "certainly", "surely",
    "clearly", "obviously", "arguably", "presumably", "apparently",
    "eventually", "immediately", "suddenly", "gradually", "briefly",
    "recently", "originally", "initially",
}
IMPERATIVE_VERBS = {
    "consider", "note", "imagine", "look", "think", "see", "remember",
    "suppose", "take", "try", "compare", "ask", "read", "write", "run",
    "open", "use", "set", "add", "start", "stop", "keep", "let", "make",
    "give", "put", "call", "pick", "choose", "notice", "watch", "picture",
    "assume", "recall", "forget", "skip", "check", "build", "draw",
    "count", "measure", "begin", "do", "don't", "avoid", "treat",
    "change", "mark", "follow", "replace", "describe", "define", "install",
    "edit", "delete", "insert", "load", "send", "save", "copy",
}
RELATIVES = {"which", "who", "whom", "whose"}
POSSESSIVE_DET = {"the", "a", "an", "his", "her", "its", "their", "our",
                  "my", "your"}
DETERMINERS = {"the", "a", "an", "this", "that", "these", "those", "its",
               "his", "her", "their", "our", "your", "my", "some", "any",
               "each", "every", "no", "both", "either", "neither", "such"}
PRONOUNS = {"i", "we", "you", "he", "she", "it", "they", "one", "who",
            "which", "what", "nobody", "everyone", "someone", "anyone",
            "everything", "something", "nothing", "anything"}
# -ing / -ed words that are not participles in opener position
NOT_PARTICIPLE = {
    "during", "nothing", "everything", "something", "anything", "thing",
    "things", "king", "string", "spring", "morning", "evening", "ceiling",
    "meaning", "beginning", "ring", "wing", "bring", "sing", "swing",
    "indeed", "instead", "need", "speed", "seed", "deed", "breed",
    "exceed", "proceed", "succeed", "red", "bed", "hundred",
}
QUOTE_CHARS = "\"'\u201c\u2018\u00ab"

OPENER_CLASSES = (
    "subject-first", "prepositional", "adverbial", "transitional",
    "subordinator", "conjunction", "participial-ing", "participial-ed",
    "infinitive", "imperative", "expletive", "question", "quotation",
    "numeral", "other",
)
# classes whose repetition is a genuine monotony signal (subject-first is
# the unmarked English order, so it gets its own, looser threshold)
MARKED_CLASSES = tuple(c for c in OPENER_CLASSES if c != "subject-first")
# run detection collapses near-identical shapes: "Building on X, ... /
# Faced with Y, ..." is one four-sentence habit, not two two-sentence ones
RUN_FAMILY = {"participial-ing": "participial", "participial-ed": "participial",
              "infinitive": "participial"}

LENGTH_BANDS = (
    ("very-short", 0, 8), ("short", 9, 15), ("medium", 16, 24),
    ("long", 25, 35), ("very-long", 36, 10 ** 6),
)


def band_of(n: int) -> str:
    for name, lo, hi in LENGTH_BANDS:
        if lo <= n <= hi:
            return name
    return "very-long"


def classify_opener(s: Sent) -> str:
    """Assign one opener class, precision-first, in a fixed priority order."""
    text = s.text.strip()
    words = [w.lower() for w in s.words]
    if not words:
        return "other"
    w0 = words[0]
    lower = text.lower()
    # words before the first comma — the ambiguous cases need one, and it
    # has to come early enough to be an opening clause rather than a list
    seg = text.split(",")[0] if "," in text else ""
    comma_words = len(TOKEN_RE.findall(seg)) if seg else None
    comma_at = comma_words if (comma_words and comma_words <= 15) else None

    if text[:1] in QUOTE_CHARS:
        return "quotation"
    if text.rstrip().endswith("?") and w0 in INTERROG:
        return "question"
    for phrase in TRANSITIONAL_PHRASES:
        if lower.startswith(phrase + " ") or lower.startswith(phrase + ","):
            return "transitional"
    if w0 in TRANSITIONAL:
        return "transitional"
    if w0 in COORD:
        return "conjunction"
    if w0 in SUB_HARD:
        return "subordinator"
    if w0 in SUB_SOFT and comma_at:
        return "subordinator"
    if w0 in ("it", "there") and len(words) > 1 and words[1] in EXPLETIVE_BE:
        return "expletive"
    if (w0.endswith("ing") and len(w0) >= 5 and w0 not in NOT_PARTICIPLE
            and comma_at):
        return "participial-ing"
    if (w0.endswith("ed") and len(w0) >= 5 and w0 not in NOT_PARTICIPLE
            and comma_at):
        return "participial-ed"
    if w0 == "to" and comma_at and len(words) > 1 and words[1] not in DETERMINERS:
        return "infinitive"
    if w0 in IMPERATIVE_VERBS and text[:1].isupper() and (
            len(words) > 1 and words[1] not in EXPLETIVE_BE
            and words[1] not in ("of", "that", "which", "who")):
        return "imperative"
    if w0.endswith("ly") and len(w0) > 4:
        return "adverbial"
    if w0 in ADVERB_WORDS:
        return "adverbial"
    if w0 in PREPOSITIONS:
        return "prepositional"
    if re.match(r"^[\d(\[]", text):
        return "numeral"
    if w0[:1].isalpha():   # determiner / pronoun / noun phrase \u2014 unmarked
        return "subject-first"
    return "other"


def architecture(s: Sent) -> dict:
    """Gross clause shape: left-branching, cumulative tail, ;/:, polysyndeton."""
    text = s.text.strip()
    opener = s.opener  # type: ignore[attr-defined]
    left = opener in ("subordinator", "participial-ing", "participial-ed",
                      "infinitive")
    if not left and "," in text:
        head = text.split(",")[0]
        hw = [w.lower() for w in TOKEN_RE.findall(head)]
        # a hard subordinator in the first few words of a pre-comma head
        # ("Even though the build passes, ...") \u2014 medial ones don't count
        if 3 <= len(hw) <= 15 and (set(hw[:3]) & SUB_HARD):
            left = True

    def is_participle(w: str) -> bool:
        return ((w.endswith("ing") or w.endswith("ed")) and len(w) >= 5
                and w not in NOT_PARTICIPLE)

    cumulative = False
    if "," in text and not (left and text.count(",") == 1):
        # a single comma in a left-branching sentence just closes the
        # fronted clause; what follows is the main clause, not a modifier
        tail = text.rsplit(",", 1)[1].strip().rstrip(".!?\"'\u201d")
        tw = [w.lower() for w in TOKEN_RE.findall(tail)]
        if len(tw) >= 3 and tw[0] not in COORD:
            t0 = tw[0]
            cumulative = (
                is_participle(t0) or t0 in PREPOSITIONS or t0 in RELATIVES
                # absolute construction: "the pages still wet"
                or (t0 in POSSESSIVE_DET
                    and any(is_participle(w) for w in tw[1:5]))
            )
    # polysyndeton: repeated coordinator NOT introducing a comma-separated
    # list item ("bread and butter and jam"), which is the figure proper
    poly_hits = Counter()
    for m in re.finditer(r"(?i)(^|[^,])\s\b(and|or|nor)\b", text):
        poly_hits[m.group(2).lower()] += 1
    poly = bool(poly_hits and max(poly_hits.values()) >= 3)
    return {
        "left_branching": left,
        "cumulative": cumulative,
        "semicolon_colon": (";" in text) or (":" in text),
        "polysyndeton": poly,
        "dash": "\u2014" in text or "\u2013" in text,
    }


def norm_entropy(counts: Counter, k: int) -> float:
    total = sum(counts.values())
    if total <= 0 or k <= 1:
        return 0.0
    h = 0.0
    for n in counts.values():
        if n:
            p = n / total
            h -= p * math.log(p)
    return h / math.log(k)


# -------------------------------------------------------------- analysis

def analyze(name: str, text: str, tok, min_words: int,
            min_sents: int) -> dict | None:
    sents = sentences_of(text, tok, min_words)
    if len(sents) < min_sents:
        return None
    openers, bands, firsts = Counter(), Counter(), Counter()
    arch = Counter()
    lens = []
    for s in sents:
        s.opener = classify_opener(s)  # type: ignore[attr-defined]
        openers[s.opener] += 1
        n = len(s.words)
        lens.append(n)
        bands[band_of(n)] += 1
        firsts[s.words[0].lower()] += 1
        s.arch = architecture(s)  # type: ignore[attr-defined]
        for key, val in s.arch.items():  # type: ignore[attr-defined]
            if val:
                arch[key] += 1

    runs = []
    for kind, keyfn in (("class", lambda s: RUN_FAMILY.get(s.opener, s.opener)),
                        ("word", lambda s: s.words[0].lower())):
        i = 0
        while i < len(sents):
            j = i + 1
            while j < len(sents) and (keyfn(sents[j]) == keyfn(sents[i])
                                      and sents[j].para == sents[i].para):
                j += 1
            if j - i >= 3:
                runs.append({
                    "kind": kind, "key": keyfn(sents[i]), "length": j - i,
                    "line": sents[i].line,
                    "sentences": [{"line": s.line, "text": s.text}
                                  for s in sents[i:j]],
                })
            i = j
    runs.sort(key=lambda r: -r["length"])

    top_class, top_n = openers.most_common(1)[0]
    n = len(sents)
    return {
        "file": name,
        "sents": n,
        "words": sum(lens),
        "mean_len": round(statistics.mean(lens), 1),
        "odi": round(norm_entropy(openers, len(OPENER_CLASSES)), 3),
        "opener_entropy_observed": round(
            norm_entropy(openers, max(2, len(openers))), 3),
        "first_word_odi": round(norm_entropy(firsts, max(2, len(firsts))), 3),
        "top_class": top_class,
        "top_share": round(top_n / n, 3),
        "openers": dict(openers.most_common()),
        "bands": {b: bands.get(b, 0) for b, _, _ in LENGTH_BANDS},
        "architecture": {k: arch.get(k, 0) for k in
                         ("left_branching", "cumulative", "semicolon_colon",
                          "polysyndeton", "dash")},
        "first_words": dict(firsts.most_common(8)),
        "runs": runs,
        "max_run_marked": max([r["length"] for r in runs
                               if r["kind"] == "class"
                               and r["key"] != "subject-first"] or [0]),
        "max_run_subject": max([r["length"] for r in runs
                                if r["kind"] == "class"
                                and r["key"] == "subject-first"] or [0]),
        "_sents": sents,
    }


def warnings_for(m: dict, args) -> list[str]:
    w = []
    if m["odi"] < args.min_odi:
        w.append(f"opener-diversity {m['odi']} < {args.min_odi} — sentence "
                 "openers cluster in a few shapes")
    for cls, n in m["openers"].items():
        share = n / m["sents"]
        if cls in MARKED_CLASSES and share > args.overuse_share and n >= 5:
            w.append(f"{cls} opens {share:.0%} of sentences "
                     f"(> {args.overuse_share:.0%})")
    sub = m["openers"].get("subject-first", 0) / m["sents"]
    if sub > args.max_subject_share:
        w.append(f"subject-first opens {sub:.0%} of sentences "
                 f"(> {args.max_subject_share:.0%}) — vary the entry point")
    for r in m["runs"]:
        if r["kind"] != "class":
            continue
        limit = (args.max_subject_run if r["key"] == "subject-first"
                 else args.max_run)
        if r["length"] >= limit:
            w.append(f"line {r['line']}: {r['length']} consecutive "
                     f"{r['key']} openers (>= {limit})")
    return w


# -------------------------------------------------------------- ontology

def ontology_faults(wo) -> set[str]:
    """Names that are failure modes somewhere in the ontology.

    "Reach for instead" is a positive directive, so a fault must never appear
    in it (writing-ontology.md rule 3): a dangling participle or a misplaced
    modifier is not a cure for opener monotony. wo.is_fault decides on
    `polarity`, else on the category name; three adjustments: the branch name
    is prepended so every category of a fault branch counts, the token
    "device" is dropped first ("sound_devices" contains "vice"), and records
    whose own copy marks them as failures count too, since the data carries
    no `polarity` stamps yet. A name that is a fault anywhere is dropped
    everywhere, so aspect homonyms cannot leak through their other home.
    """
    names: set[str] = set()
    for branch in wo.available_branches():
        try:
            data = wo.load_branch(branch)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        for cat, entries in (data.get("categories") or {}).items():
            if not isinstance(entries, list):
                continue
            label = f"{branch}.{cat}".replace("device", "")
            for e in entries:
                copy = isinstance(e, dict) and (
                    str(e.get("example", "")).strip().lower().startswith(
                        "faulty")
                    or any(cue in f"{e.get('definition', '')} "
                                   f"{e.get('effect', '')}".lower()
                           for cue in ("as a diagnostic", "unintentional",
                                       "inadvertent")))
                if isinstance(e, dict) and e.get("polarity") == "virtue":
                    continue
                if wo.is_fault(e, label) or copy:
                    names.add(wo.entry_name(e).strip().lower())
    return names


def ontology_suggestions(overused: list[str], n: int, seed) -> list[str]:
    """Seeded 'reach for these instead' entries from the ontology, if built."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import writing_ontology
    except ImportError:
        return []
    if "syntactic_constructions" not in writing_ontology.available_branches():
        return []
    try:
        branch = writing_ontology.load_branch("syntactic_constructions")
        pool = writing_ontology.sample_entries(branch, n=n * 8, seed=seed)
        faults = ontology_faults(writing_ontology)
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return []
    out = []
    busy = " ".join(overused).lower()
    for e in pool:
        label = writing_ontology.entry_name(e)
        if label.strip().lower() in faults:   # never suggest a failure mode
            continue
        if label.lower() in busy:
            continue
        if isinstance(e, dict):
            line = f"{label} — {e.get('definition', '')}".strip(" —")
            if e.get("example"):
                line += f"\n      e.g. {e['example']}"
        else:
            line = label
        out.append(line)
        if len(out) >= n:
            break
    return out


# ---------------------------------------------------------------- output

def print_report(rows: list[dict], args, warns: list[tuple[str, str]]) -> None:
    hdr = (f"{'chapter':32s} {'sents':>5s} {'mean':>5s} {'odi':>5s} "
           f"{'top opener':>16s} {'top%':>5s} {'run':>3s} {'LB%':>4s} "
           f"{'CUM%':>5s} {'; :%':>5s}")
    print(hdr)
    print("-" * len(hdr))
    for m in rows:
        a, n = m["architecture"], m["sents"]
        flag = " !" if m["warnings"] else ""
        print(f"{m['file']:32s} {n:5d} {m['mean_len']:5.1f} {m['odi']:5.3f} "
              f"{m['top_class']:>16s} {m['top_share']*100:4.0f}% "
              f"{max(m['max_run_marked'], m['max_run_subject']):3d} "
              f"{100*a['left_branching']/n:4.0f} "
              f"{100*a['cumulative']/n:5.0f} "
              f"{100*a['semicolon_colon']/n:5.0f}{flag}")
    print()

    if args.detail:
        for m in rows:
            print(f"=== {m['file']}  ({m['sents']} sentences, "
                  f"{m['words']} words)")
            print("  openers:")
            for cls, n in m["openers"].items():
                bar = "#" * max(1, round(40 * n / m["sents"]))
                print(f"    {cls:16s} {n:4d} {100*n/m['sents']:5.1f}%  {bar}")
            print("  lengths:")
            for b, lo, hi in LENGTH_BANDS:
                n = m["bands"][b]
                rng = f"{lo}-{hi}" if hi < 10 ** 6 else f"{lo}+"
                print(f"    {b:12s} {rng:>7s} {n:4d} "
                      f"{100*n/m['sents']:5.1f}%")
            print("  architecture: " + ", ".join(
                f"{k}={v} ({100*v/m['sents']:.0f}%)"
                for k, v in m["architecture"].items()))
            print("  first words: " + ", ".join(
                f"{w} x{n}" for w, n in m["first_words"].items()))
            over = [(c, n) for c, n in m["openers"].items()
                    if c in MARKED_CLASSES
                    and n / m["sents"] > args.overuse_share and n >= 5]
            over.sort(key=lambda t: -t[1])
            rng = random.Random(args.seed)
            for cls, n in over[:args.top]:
                print(f"  over-represented: {cls} "
                      f"({n}/{m['sents']} = {100*n/m['sents']:.0f}%)")
                pool = [s for s in m["_sents"] if s.opener == cls]
                for s in rng.sample(pool, min(args.examples, len(pool))):
                    print(f"    L{s.line}: {s.text[:110]}")
            for r in m["runs"][:args.top]:
                if r["kind"] == "class" and r["key"] == "subject-first" \
                        and r["length"] < args.max_subject_run:
                    continue
                label = ("opener type" if r["kind"] == "class"
                         else "first word")
                print(f"  run: {r['length']} consecutive sentences, same "
                      f"{label} ({r['key']}) at L{r['line']}")
                for s in r["sentences"][:args.examples]:
                    print(f"    L{s['line']}: {s['text'][:110]}")
            print()

    for fname, w in warns:
        print(f"WARN {fname}: {w}")
    print(f"construction_variety: {len(rows)} unit(s), {len(warns)} warning(s)")

    overused = sorted({c for m in rows for c, n in m["openers"].items()
                       if c in MARKED_CLASSES
                       and n / m["sents"] > args.overuse_share})
    sugg = ontology_suggestions(overused, args.suggest, args.seed)
    if sugg:
        print("\nreach for instead (writing ontology, "
              f"seed={args.seed}, syntactic_constructions):")
        for line in sugg:
            print(f"  - {line}")


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, action="append", default=None,
                    help="book root; repeatable (default: this repo)")
    ap.add_argument("--text", type=Path, action="append", default=None,
                    help="plain-prose file to analyze instead of the corpus")
    ap.add_argument("--chapter", help="restrict to files starting with this")
    ap.add_argument("--detail", action="store_true",
                    help="per-chapter distributions, examples and runs")
    ap.add_argument("--json", action="store_true", help="machine-readable")
    ap.add_argument("--examples", type=int, default=3,
                    help="example sentences per pattern (default 3)")
    ap.add_argument("--top", type=int, default=4,
                    help="patterns/runs shown per chapter (default 4)")
    ap.add_argument("--suggest", type=int, default=3,
                    help="ontology constructions to suggest (default 3)")
    ap.add_argument("--seed", type=int, default=0,
                    help="seed for example sampling and ontology picks")
    ap.add_argument("--min-words", type=int, default=4,
                    help="ignore sentences shorter than this (default 4)")
    ap.add_argument("--min-sents", type=int, default=15,
                    help="skip units with fewer sentences (default 15 — "
                         "distributions are noise below that)")
    ap.add_argument("--min-odi", type=float, default=0.20,
                    help="opener-diversity floor (default 0.20)")
    ap.add_argument("--overuse-share", type=float, default=0.15,
                    help="marked-opener share that counts as overuse (0.15; "
                         "needs 5+ sentences too)")
    ap.add_argument("--max-subject-share", type=float, default=0.85,
                    help="subject-first share ceiling (default 0.85)")
    ap.add_argument("--max-run", type=int, default=4,
                    help="consecutive marked-opener run that warns (default 4)")
    ap.add_argument("--max-subject-run", type=int, default=7,
                    help="consecutive subject-first run that warns (default 7)")
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero if any unit has warnings")
    args = ap.parse_args()

    from nupunkt import PunktSentenceTokenizer
    tok = PunktSentenceTokenizer()

    units: list[tuple[str, str]] = []
    if args.text:
        for p in args.text:
            units.append((p.name, p.read_text()))
    else:
        roots = args.root or [Path(__file__).resolve().parent.parent]
        files: list[Path] = []
        for root in roots:
            files += discover(root)
        if args.chapter:
            files = [f for f in files if f.name.startswith(args.chapter)]
        if not files:
            raise SystemExit(f"construction_variety: no .tex files under {roots}")
        for f in files:
            units.append((f.name, strip_latex_lines(f.read_text())))

    rows, warns = [], []
    for name, text in units:
        m = analyze(name, text, tok, args.min_words, args.min_sents)
        if m is None:
            continue
        m["warnings"] = warnings_for(m, args)
        warns += [(name, w) for w in m["warnings"]]
        rows.append(m)
    if not rows:
        raise SystemExit("construction_variety: nothing long enough to analyze")

    if args.json:
        out = []
        for m in rows:
            d = {k: v for k, v in m.items() if k != "_sents"}
            d["runs"] = d["runs"][:args.top]
            out.append(d)
        print(json.dumps({"units": out}, indent=2))
    else:
        print_report(rows, args, warns)

    if args.strict and warns:
        sys.exit(1)


if __name__ == "__main__":
    main()
