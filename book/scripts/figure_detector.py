#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pydetex>=1.1.1",
#     "nupunkt>=0.6.0",
# ]
# ///
"""Heuristic detector of rhetorical figures in prose.

Finds the schemes a writer can actually audit by eye — repetition,
balance, omission — and prints the matched text with line numbers, so
every hit is checkable in ten seconds. It answers two questions a draft
raises: *am I using any figures at all*, and *are they clumped* (all the
alliteration in chapter 1, none after).

Detected (all orthographic/lexical heuristics, no tagger, no phonetics):

  alliteration   3+ nearby content words sharing an initial consonant
                 cluster (ch/sh/th/ph/wh/qu treated as units)
  assonance      3+ nearby content words sharing a two-letter vowel
                 digraph (ee, ea, oo, ou, ai, oa, ...) — best effort
  anaphora       successive sentences opening with the same 1-3 words
  epistrophe     successive sentences ending with the same 1-3 words
  anadiplosis    a sentence (or clause) ends on the word the next begins
  tricolon       a three-item coordinated list: A, B, and C
  isocolon       3+ adjacent parallel members of equal length (or the two
                 unambiguous members of a detected tricolon)
  polysyndeton   the same coordinator 3+ times without list commas
  asyndeton      3+ similar trailing members and no coordinator at all
  epizeuxis      a word repeated immediately (never, never, never)
  question       interrogative sentence outside quoted speech

Precision beats recall here: a false hit costs a writer more than a
missed one, so every rule is deliberately narrow. Known misses are
listed under LIMITS at the bottom of this docstring.

If scripts/data/ontology/rhetorical_figures.json exists, the report
closes with a few seeded figures to try; without it the report is
simply shorter. Advisory: exit 0 unless --strict, which fails a unit
whose total figure density exceeds --max-density (over-figured prose).

Usage:
    uv run scripts/figure_detector.py                    # counts + matrix
    uv run scripts/figure_detector.py --detail           # + every snippet
    uv run scripts/figure_detector.py --figure anaphora  # one figure, verbose
    uv run scripts/figure_detector.py --chapter ch02 --detail
    uv run scripts/figure_detector.py --text draft.txt
    uv run scripts/figure_detector.py --root ../other-book --json
    uv run scripts/figure_detector.py --strict --max-density 12

LIMITS (deliberate misses, in the name of precision)
  - Alliteration is orthographic: "cat/kitten" and "phone/fake" are not
    matched, "circle/cat" is. Vowel-initial runs are left to assonance.
  - Assonance only fires on two-letter vowel digraphs; single-vowel
    assonance ("bad man ran") is not detected at all.
  - Anaphora/epistrophe are sentence-initial/final only and must sit in
    one paragraph; clause-level anaphora is caught only as a run of 3+
    clause-sized segments sharing a 2+ word prefix within one sentence.
  - A single-word anaphora needs a 3-sentence run and a non-stopword,
    so "The ... The ..." is left to construction_variety.py's opener runs.
  - Tricolon needs the list to end the sentence and its outer members to
    be coordinator-free; a tricolon buried mid-sentence is missed, and
    the first member's boundary is approximate (it inherits whatever
    precedes it in its comma segment), so its word count is a ceiling.
  - Isocolon is length-plus-first-word-class equality; genuinely
    parallel members of unequal length are missed, and so are two-member
    pairs outside a tricolon (too common by chance in ordinary lists).
  - Asyndeton needs 3+ trailing members of similar length (spread <= 4
    words, each <= 8) and rejects any sentence containing a semicolon or
    a coordinator, so a series whose first member carries the sentence's
    subject clause ("The build is the interior: exact trim, mirrored
    margins, black links") is missed — that first member is too long to
    look parallel.
  - `question` counts interrogatives; whether one is *rhetorical* is not
    machine-decidable, so read it as "questions asked of the reader".
  - No chiasmus, antimetabole, zeugma, or trope detection (metaphor,
    metonymy, irony) — those need semantics, not patterns.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import Counter, defaultdict
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


def sentences_of(text: str, tok, min_words: int = 3) -> list[Sent]:
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


# ------------------------------------------------------------- lexicons

STOPWORDS = {
    "a", "about", "after", "again", "all", "also", "am", "an", "and",
    "any", "are", "as", "at", "be", "because", "been", "before", "being",
    "both", "but", "by", "can", "could", "did", "do", "does", "doing",
    "done", "down", "each", "either", "else", "even", "ever", "every",
    "for", "from", "had", "has", "have", "having", "he", "her", "here",
    "hers", "him", "his", "how", "however", "i", "if", "in", "into", "is",
    "it", "its", "itself", "just", "may", "me", "might", "more", "most",
    "much", "must", "my", "neither", "no", "nor", "not", "now", "of",
    "off", "on", "once", "one", "only", "or", "other", "our", "out",
    "over", "own", "per", "quite", "rather", "same", "shall", "she",
    "should", "since", "so", "some", "still", "such", "than", "that",
    "the", "their", "them", "then", "there", "these", "they", "this",
    "those", "though", "through", "thus", "to", "too", "under", "until",
    "up", "upon", "us", "very", "via", "was", "we", "well", "were",
    "what", "when", "where", "which", "while", "who", "whom", "why",
    "will", "with", "within", "without", "would", "yet", "you", "your",
}
COORD = ("and", "or", "nor", "but")
COORD_RE = re.compile(r"(?i)\b(?:and|or|nor|but)\b")
ONSETS = ("ch", "sh", "th", "ph", "wh", "qu")
VOWEL_DIGRAPHS = ("ee", "ea", "oo", "ou", "ai", "ay", "oa", "ie", "au",
                  "aw", "oi", "oy", "ue", "ew", "igh")
QUOTE_CHARS = "\"'\u201c\u2018\u00ab"
# grammatical or typographic doubles, not epizeuxis
EPIZEUXIS_SKIP = {"had", "that", "this", "the", "and", "was", "is", "are",
                  "were", "has", "not", "one", "you", "she", "her", "his"}
# a phrase in this position modifies the series rather than joining it
TAIL_ADJUNCT = {"without", "with", "for", "in", "on", "at", "by", "from",
                "to", "of", "under", "over", "through", "against",
                "between", "during", "across", "along", "toward", "into"}

# density is meaningless on a dedication or a colophon
DENSITY_FLOOR = 200

FIGURES = ("alliteration", "assonance", "anaphora", "epistrophe",
           "anadiplosis", "tricolon", "isocolon", "polysyndeton",
           "asyndeton", "epizeuxis", "question")


def norm(word: str) -> str:
    return word.lower().strip("'\u2019-")


def onset(word: str) -> str | None:
    """Initial consonant cluster, digraph-aware; None for vowel-initial."""
    w = norm(word)
    if len(w) < 3 or not w[0].isalpha():
        return None
    if w[:2] in ONSETS:
        return w[:2]
    if w[0] in "aeiou":
        return None
    return w[0]


def vowel_key(word: str) -> str | None:
    """The earliest vowel digraph in the word, or None."""
    w = norm(word)
    best, at = None, len(w)
    for dg in VOWEL_DIGRAPHS:
        i = w.find(dg)
        if 0 <= i < at:
            best, at = dg, i
    return best


def clean_words(text: str) -> list[str]:
    return [norm(w) for w in TOKEN_RE.findall(text)]


# ------------------------------------------------------------- detectors

@dataclass
class Hit:
    figure: str
    line: int
    detail: str
    snippet: str


def _proximate_runs(keyed: list[tuple[int, str, str]], gap: int,
                    min_run: int) -> list[tuple[str, list[str]]]:
    """Group (position, key, word) triples by key into runs whose adjacent
    members sit within `gap` word positions of each other."""
    by_key: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for pos, key, word in keyed:
        by_key[key].append((pos, word))
    runs = []
    for key, items in by_key.items():
        cur = [items[0]]
        for prev, nxt in zip(items, items[1:], strict=False):
            if nxt[0] - prev[0] <= gap:
                cur.append(nxt)
            else:
                if len({w for _, w in cur}) >= min_run:
                    runs.append((key, [w for _, w in cur]))
                cur = [nxt]
        if len({w for _, w in cur}) >= min_run:
            runs.append((key, [w for _, w in cur]))
    return runs


def detect_sound(s: Sent, gap: int, min_run: int) -> list[Hit]:
    hits: list[Hit] = []
    words = [norm(w) for w in s.words]
    for figure, keyfn in (("alliteration", onset), ("assonance", vowel_key)):
        keyed = []
        for i, w in enumerate(words):
            if w in STOPWORDS or len(w) < 3:
                continue
            k = keyfn(w)
            if k:
                keyed.append((i, k, w))
        for key, picked in _proximate_runs(keyed, gap, min_run):
            hits.append(Hit(figure, s.line,
                            f"{len(set(picked))} words on /{key}/: "
                            + " ".join(dict.fromkeys(picked)),
                            s.text))
    return hits


def _shared_edge(a: list[str], b: list[str], end: bool) -> int:
    n = 0
    for i in range(1, 4):
        if len(a) < i or len(b) < i:
            break
        if end:
            if a[-i:] == b[-i:]:
                n = i
            else:
                break
        else:
            if a[:i] == b[:i]:
                n = i
            else:
                break
    return n


def detect_edge_repetition(para: list[Sent], figure: str) -> list[Hit]:
    """anaphora (shared opening) / epistrophe (shared ending) across
    successive sentences of one paragraph."""
    end = figure == "epistrophe"
    hits: list[Hit] = []
    i = 0
    while i < len(para):
        j, k = i + 1, 3
        while j < len(para):
            shared = _shared_edge(clean_words(para[i].text),
                                  clean_words(para[j].text), end)
            if shared == 0:
                break
            k = min(k, shared)
            j += 1
        run = para[i:j]
        if len(run) >= 2:
            words = clean_words(run[0].text)
            edge = words[-k:] if end else words[:k]
            ok = (k >= 2 and len(run) >= 2) or (
                k == 1 and len(run) >= 3
                and edge[0] not in STOPWORDS and len(edge[0]) >= 3)
            if ok:
                hits.append(Hit(
                    figure, run[0].line,
                    f"{len(run)} sentences share "
                    f"{'ending' if end else 'opening'} "
                    f"\u201c{' '.join(edge)}\u201d",
                    " / ".join(s.text[:60] for s in run)))
            i = j if j > i + 1 else i + 1
        else:
            i += 1
    return hits


def detect_anadiplosis(para: list[Sent]) -> list[Hit]:
    hits: list[Hit] = []
    for a, b in zip(para, para[1:], strict=False):
        aw, bw = clean_words(a.text), clean_words(b.text)
        if not aw or not bw:
            continue
        for n in (3, 2, 1):
            if len(aw) < n or len(bw) < n:
                continue
            if aw[-n:] == bw[:n] and (
                    n >= 2 or (aw[-1] not in STOPWORDS and len(aw[-1]) >= 4)):
                hits.append(Hit("anadiplosis", a.line,
                                f"sentence ends and next opens on "
                                f"\u201c{' '.join(aw[-n:])}\u201d",
                                a.text[-60:] + " || " + b.text[:60]))
                break
    return hits


def detect_clause_anadiplosis(s: Sent) -> list[Hit]:
    hits: list[Hit] = []
    segs = [seg for seg in re.split(r"[,;:\u2014]", s.text) if seg.strip()]
    for a, b in zip(segs, segs[1:], strict=False):
        aw, bw = clean_words(a), clean_words(b)
        # both sides must be clause-sized, or this just re-reports epizeuxis
        if len(aw) >= 3 and len(bw) >= 3 and aw[-1] == bw[0] \
                and aw[-1] not in STOPWORDS and len(aw[-1]) >= 4:
            hits.append(Hit("anadiplosis", s.line,
                            f"clause ends and next opens on "
                            f"\u201c{aw[-1]}\u201d", s.text))
    return hits


def detect_clause_anaphora(s: Sent) -> list[Hit]:
    """anaphora across clause boundaries inside one sentence — the
    'it was the best of times, it was the worst of times' shape that
    sentence-edge detection cannot see. Requires a run of 3+
    clause-sized segments sharing a 2+ word prefix."""
    hits: list[Hit] = []
    segs = [clean_words(seg)
            for seg in re.split(r"[,;:—]", s.text) if seg.strip()]
    segs = [w for w in segs if len(w) >= 3]
    i = 0
    while i < len(segs):
        j, k = i + 1, 3
        while j < len(segs):
            shared = 0
            for n in range(min(3, len(segs[i]), len(segs[j])), 1, -1):
                if segs[i][:n] == segs[j][:n]:
                    shared = n
                    break
            if shared < 2:
                break
            k = min(k, shared)
            j += 1
        if j - i >= 3:
            hits.append(Hit(
                "anaphora", s.line,
                f"{j - i} successive clauses share opening "
                f"“{' '.join(segs[i][:k])}”",
                s.text[:120]))
            i = j
        else:
            i += 1
    return hits


def detect_lists(s: Sent, min_item_words: int) -> list[Hit]:
    """tricolon (A, B, and C), isocolon (3+ equal-length parallel members),
    asyndeton (a comma series with no conjunction)."""
    hits: list[Hit] = []
    body = s.text.strip().rstrip(".!?\"'\u201d")
    segs = [seg.strip() for seg in body.split(",") if seg.strip()]

    # ---- tricolon: A, B, and C, with the list closing the sentence
    if len(segs) >= 3:
        lw = clean_words(segs[-1])
        if lw and lw[0] in COORD:
            def qualifies(seg: str) -> bool:
                w = clean_words(seg)
                return bool(w) and not COORD_RE.search(seg) and len(w) <= 12
            items, k = [lw[1:]], len(segs) - 2
            while k >= 0 and len(items) < 3 and qualifies(segs[k]):
                items.insert(0, clean_words(segs[k]))
                k -= 1
            more = k >= 0 and qualifies(segs[k])
            # the closing member must be a member, not a whole new clause
            tail_ok = (len(items[-1]) <= 12
                       and not COORD_RE.search(" ".join(items[-1])))
            if (len(items) == 3 and not more and tail_ok
                    and all(len(it) >= min_item_words for it in items)):
                snippet = ", ".join(segs[-3:])
                hits.append(Hit("tricolon", s.line,
                                "three coordinated members "
                                f"({'/'.join(str(len(i)) for i in items)} "
                                "words; first is approximate)", snippet))
                # inside a confirmed tricolon the parallel is structural,
                # so equal 2-word members already count as isocolon
                if len(items[1]) == len(items[2]) >= 2:
                    hits.append(Hit("isocolon", s.line,
                                    f"members of equal length "
                                    f"({len(items[1])} words)", snippet))

    # ---- asyndeton: a trailing series of similar members, no conjunction.
    # A semicolon means clause coordination, not a series, so it disqualifies.
    if ";" not in body and not COORD_RE.search(body):
        members = [m.strip() for m in re.split(r"[,\u2014]", body) if m.strip()]
        run: list[list[str]] = []
        for idx, seg in enumerate(reversed(members)):
            w = clean_words(seg)
            if idx == 0 and w and w[0] in TAIL_ADJUNCT:
                continue          # trailing adjunct phrase, not a member
            if not w or len(w) > 8 or len(w) < 2:
                break
            if w[0] in ("which", "who", "that", "if", "when", "because",
                        "though", "although", "while", "since", "after",
                        "before", "unless", "whereas"):
                break
            run.insert(0, w)
        if len(run) >= 3 and max(len(w) for w in run) - min(
                len(w) for w in run) <= 4:
            hits.append(Hit("asyndeton", s.line,
                            f"{len(run)} parallel members, no conjunction",
                            ", ".join(" ".join(w) for w in run)))

    # ---- isocolon: 3+ adjacent members of identical length in parallel
    parts = [p.strip() for p in re.split(r"[,;]", body) if p.strip()]
    pw = [clean_words(p) for p in parts]
    i = 0
    while i < len(pw) - 2:
        j = i + 1
        while j < len(pw) and len(pw[j]) == len(pw[i]) >= 3:
            j += 1
        run = pw[i:j]
        if len(run) >= 3:
            heads = [w[0] for w in run]
            func = [h for h in heads if h in STOPWORDS]
            same_func = len(set(heads)) == 1 and len(func) == len(heads)
            all_content = not func
            if same_func or all_content:
                hits.append(Hit("isocolon", s.line,
                                f"{len(run)} parallel members of "
                                f"{len(run[0])} words",
                                ", ".join(parts[i:j])))
            i = j
        else:
            i += 1
    return hits


def detect_syndeton(s: Sent, poly_min: int) -> list[Hit]:
    """polysyndeton: the same coordinator repeated without list commas."""
    counts = Counter()
    for m in re.finditer(r"(?i)(^|[^,])\s\b(and|or|nor)\b", s.text):
        counts[m.group(2).lower()] += 1
    hits = []
    for word, n in counts.items():
        if n >= poly_min:
            hits.append(Hit("polysyndeton", s.line,
                            f"'{word}' x{n} without list commas", s.text))
    return hits


def detect_epizeuxis(s: Sent) -> list[Hit]:
    hits = []
    words = [norm(w) for w in s.words]
    for a, b in zip(words, words[1:], strict=False):
        if a == b and len(a) >= 3 and a not in EPIZEUXIS_SKIP:
            hits.append(Hit("epizeuxis", s.line,
                            f"\u201c{a}\u201d repeated immediately", s.text))
    return hits


def detect_question(s: Sent) -> list[Hit]:
    if s.text.rstrip().endswith("?") and s.text[:1] not in QUOTE_CHARS:
        return [Hit("question", s.line, "interrogative sentence", s.text)]
    return []


def detect_all(sents: list[Sent], args) -> list[Hit]:
    hits: list[Hit] = []
    for s in sents:
        hits += detect_sound(s, args.gap, args.min_run)
        hits += detect_lists(s, args.min_item_words)
        hits += detect_syndeton(s, args.poly_min)
        hits += detect_epizeuxis(s)
        hits += detect_question(s)
        hits += detect_clause_anadiplosis(s)
        hits += detect_clause_anaphora(s)
    paras: dict[int, list[Sent]] = defaultdict(list)
    for s in sents:
        paras[s.para].append(s)
    for para in paras.values():
        if len(para) < 2:
            continue
        hits += detect_edge_repetition(para, "anaphora")
        hits += detect_edge_repetition(para, "epistrophe")
        hits += detect_anadiplosis(para)
    hits.sort(key=lambda h: (h.line, h.figure))
    return hits


# -------------------------------------------------------------- ontology

def ontology_faults(wo) -> set[str]:
    """Names that are failure modes somewhere in the ontology.

    "Figures to try" is a positive directive, so a fault must never appear in
    it (writing-ontology.md rule 3). wo.is_fault decides on `polarity`, else
    on the category name; three adjustments: the branch name is prepended so
    every category of a fault branch counts, the token "device" is dropped
    first ("sound_devices" contains "vice"), and records whose own copy marks
    them as failures count too, since the data carries no `polarity` stamps
    yet. A name that is a fault anywhere is dropped everywhere, which is how
    pleonasm-the-fault keeps pleonasm-the-figure out of the list.
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


def ontology_suggestions(n: int, seed) -> list[str]:
    """Seeded 'try these' entries from the ontology, if it is built."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import writing_ontology
    except ImportError:
        return []
    if "rhetorical_figures" not in writing_ontology.available_branches():
        return []
    try:
        branch = writing_ontology.load_branch("rhetorical_figures")
        pool = writing_ontology.sample_entries(branch, n=n * 8, seed=seed)
        faults = ontology_faults(writing_ontology)
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return []
    out = []
    for e in pool:
        label = writing_ontology.entry_name(e)
        if label.strip().lower() in faults:   # never suggest a failure mode
            continue
        if label.lower() in FIGURES:      # already measured above
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


# ---------------------------------------------------------------- report

def analyze(name: str, text: str, tok, args) -> dict:
    sents = sentences_of(text, tok)
    hits = detect_all(sents, args)
    if args.figure:
        hits = [h for h in hits if h.figure == args.figure]
    words = sum(len(s.words) for s in sents)
    counts = Counter(h.figure for h in hits)
    per_k = {f: round(1000 * counts.get(f, 0) / words, 2) if words else 0.0
             for f in FIGURES}
    return {
        "file": name,
        "words": words,
        "sents": len(sents),
        "total": len(hits),
        "density": round(1000 * len(hits) / words, 2) if words else 0.0,
        "counts": {f: counts.get(f, 0) for f in FIGURES},
        "per_1000": per_k,
        "hits": [h.__dict__ for h in hits],
    }


def print_report(rows: list[dict], args) -> None:
    figures = [args.figure] if args.figure else list(FIGURES)
    hdr = f"{'chapter':32s} {'words':>6s} {'sents':>5s} {'figs':>5s} {'/1k':>6s}"
    print(hdr)
    print("-" * len(hdr))
    for m in rows:
        print(f"{m['file']:32s} {m['words']:6d} {m['sents']:5d} "
              f"{m['total']:5d} {m['density']:6.2f}")
    print()

    # figure x chapter matrix, with a concentration column: what share of
    # a figure's total sits in the single heaviest chapter
    width = max(12, max(len(f) for f in figures))
    cols = "".join(f"{m['file'][:9]:>10s}" for m in rows)
    print(f"{'figure':<{width}}{cols}{'total':>7s}{'conc':>6s}")
    print("-" * (width + 10 * len(rows) + 13))
    for f in figures:
        vals = [m["counts"][f] for m in rows]
        tot = sum(vals)
        conc = max(vals) / tot if tot else 0.0
        cells = "".join(f"{v:>10d}" for v in vals)
        mark = "  <- clumped" if tot >= 3 and conc >= 0.8 and len(rows) > 1 \
            else ""
        print(f"{f:<{width}}{cells}{tot:>7d}{conc:>6.2f}{mark}")
    print()

    if args.detail or args.figure:
        rng = random.Random(args.seed)
        for m in rows:
            shown = list(m["hits"])
            if not shown:
                continue
            print(f"=== {m['file']}")
            by_fig: dict[str, list[dict]] = defaultdict(list)
            for h in shown:
                by_fig[h["figure"]].append(h)
            for f in figures:
                group = by_fig.get(f, [])
                if not group:
                    continue
                print(f"  {f} ({len(group)}):")
                pick = group
                if len(group) > args.examples:
                    pick = sorted(rng.sample(group, args.examples),
                                  key=lambda h: h["line"])
                for h in pick:
                    print(f"    L{h['line']}: {h['detail']}")
                    print(f"      {h['snippet'][:150]}")
                if len(pick) < len(group):
                    print(f"    ... {len(group) - len(pick)} more "
                          f"(--examples N, seed={args.seed})")
            print()

    warns = [(m["file"], f"figure density {m['density']}/1k > "
                        f"{args.max_density}/1k — heavily figured prose")
             for m in rows
             if m["density"] > args.max_density and m["words"] >= DENSITY_FLOOR]
    for fname, w in warns:
        print(f"WARN {fname}: {w}")
    total = sum(m["total"] for m in rows)
    print(f"figure_detector: {len(rows)} unit(s), {total} figure(s), "
          f"{len(warns)} warning(s)")

    sugg = ontology_suggestions(args.suggest, args.seed)
    if sugg:
        print(f"\nfigures to try (writing ontology, seed={args.seed}, "
              "rhetorical_figures):")
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
    ap.add_argument("--figure", choices=FIGURES,
                    help="report only this figure (implies --detail)")
    ap.add_argument("--detail", action="store_true",
                    help="print matched snippets with line numbers")
    ap.add_argument("--json", action="store_true", help="machine-readable")
    ap.add_argument("--examples", type=int, default=4,
                    help="snippets shown per figure per unit (default 4)")
    ap.add_argument("--suggest", type=int, default=3,
                    help="ontology figures to suggest (default 3)")
    ap.add_argument("--seed", type=int, default=0,
                    help="seed for snippet sampling and ontology picks")
    ap.add_argument("--gap", type=int, default=3,
                    help="max word distance between sound-figure members (3)")
    ap.add_argument("--min-run", type=int, default=3,
                    help="distinct words needed for a sound figure (3)")
    ap.add_argument("--min-item-words", type=int, default=2,
                    help="words per tricolon member (default 2)")
    ap.add_argument("--poly-min", type=int, default=3,
                    help="repeats of one coordinator for polysyndeton (3)")
    ap.add_argument("--max-density", type=float, default=15.0,
                    help="figures per 1000 words that --strict fails on (15)")
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero if any unit exceeds --max-density")
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
            raise SystemExit(f"figure_detector: no .tex files under {roots}")
        for f in files:
            units.append((f.name, strip_latex_lines(f.read_text())))

    rows = [analyze(name, text, tok, args) for name, text in units]
    rows = [m for m in rows if m["words"]]
    if not rows:
        raise SystemExit("figure_detector: nothing to analyze")

    if args.json:
        print(json.dumps({"units": rows}, indent=2))
    else:
        print_report(rows, args)

    if args.strict and any(m["density"] > args.max_density
                           and m["words"] >= DENSITY_FLOOR for m in rows):
        sys.exit(1)


if __name__ == "__main__":
    main()
