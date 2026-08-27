#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "nupunkt>=0.6.0",
#     "pydantic>=2.7",
#     "pydantic-ai-slim[openai,anthropic]>=1.0",
# ]
# ///
"""Discourse-move annotator: what job is each paragraph doing?

Labels every paragraph with the rhetorical move it performs, then reports
the shape of the sequence. Prose that is monotonous at the move level reads
flat even when its sentences vary: ten paragraphs of claim-claim-claim is a
lecture, not an argument, and no amount of sentence-length variety fixes it.

The classifier is a cue lexicon, offline and deterministic:

  forecast      "in this chapter", "what follows" — announces what is coming
  recap         "as we saw", "so far", "to sum up"
  question      an interrogative sentence, especially paragraph-initial
  definition    \\term{}/\\keyterm{}, "is a", "refers to", "known as"
  concession    "granted", "admittedly", "to be sure", "of course"
  contrast      "but", "however", "yet", "on the other hand"
  evidence      "for example", "studies show", "according to", figures
  cause         "because", "therefore", "as a result", "which is why"
  elaboration   "in other words", "more precisely", "in fact"
  comparison    "like", "just as", "similarly", "think of it as"
  enumeration   "first", "second", "finally", "another"
  narrative     past-tense verbs + pronoun density + dialogue (a scene)
  directive     "consider", "notice", "imagine", "run", second person
  attribution   \\cite/\\textcite, "argues", "writes", "according to X"
  qualification "may", "arguably", "roughly", "in principle"
  claim         the fallback: an assertion with no cue on it

If the ontology's discourse_moves branch is present, any record carrying a
"cues" list is merged into the lexicon at runtime, so growing the ontology
sharpens this tool without touching its code. Missing branch = built-ins only.

Reports, per chapter and for the book:
  sequence      the ordered move labels with line anchors
  distribution  how often each move is used
  gaps          moves in the inventory the chapter never uses
  monotony      runs of 3+ consecutive paragraphs with the same move

--llm relabels paragraphs with a model choosing from the built-in families
plus whichever ontology labels the cue pass actually reached (a 200-entry
branch would otherwise bury the prompt). Provider comes from
ANTHROPIC_API_KEY or OPENAI_API_KEY — slop_audit.py's pattern, --model to
force one. Without a key it prints a note and stays heuristic.

Usage:
    uv run scripts/move_annotator.py                     # whole book
    uv run scripts/move_annotator.py --chapter ch02
    uv run scripts/move_annotator.py --no-sequence       # tables only
    uv run scripts/move_annotator.py --text draft.txt --json
    uv run scripts/move_annotator.py --llm --limit 20
    uv run scripts/move_annotator.py --strict --min-coverage 0.4

Advisory: exits 0 unless --strict, which fails on any flagged monotony run
or on built-in move coverage below --min-coverage (default 50% of the 16
built-in families used somewhere in the book).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import writing_ontology as wo
except ImportError:  # standalone copy of the script
    wo = None

# ------------------------------------------------------------- corpus layer
# Same recipe as prose_metrics.py / slop_audit.py.

SUBDIRS = ("chapters", "frontmatter", "front-matter", "backmatter", "back-matter")
DROP_ENVS = (
    "tikzpicture", "figure", "table", "tabular", "tabularx", "lstlisting",
    "verbatim", "Verbatim", "equation", "align", "alignat", "gather",
    "definitionbox", "tryitbox", "examplebox", "codelisting", "promptcode",
    "outputcode",
)
HEADING_RE = re.compile(r"\\(chapter|section|subsection)\*?\{([^}]*)\}")


def light_detex(text: str) -> str:
    text = re.sub(r"(?<!\\)%.*", "", text)
    text = text.replace("---", "\u2014").replace("--", "\u2013")
    text = text.replace("``", "\u201c").replace("''", "\u201d")
    for env in DROP_ENVS:
        text = re.sub(rf"\\begin\{{{env}\*?\}}.*?\\end\{{{env}\*?\}}", " ",
                      text, flags=re.DOTALL)
    text = re.sub(r"\$[^$]*\$", " ", text)
    text = re.sub(r"\\(?:label|ref|cref|Cref|[A-Za-z]*cite[A-Za-z]*|input|include)\*?"
                  r"(?:\[[^\]]*\])?\{[^}]*\}", " ", text)
    text = re.sub(r"\\begin\{[^}]*\}\[title=([^\]]*)\]", r" \1 ", text)
    text = re.sub(r"\\begin\{[^}]*\}\[([^\]=]*)\]", r" \1 ", text)
    text = re.sub(r"\\begin\{[^}]*\}\[[^\]]*\]", " ", text)
    text = re.sub(r"\\(?:begin|end)\{[^}]*\}", " ", text)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", text)
    text = re.sub(r"[{}~]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


@dataclass
class Para:
    file: str
    line: int
    section: str
    text: str
    raw: str
    index: int = 0
    label: str = "claim"
    score: float = 0.0
    evidence: list[str] = field(default_factory=list)
    runner_up: str = ""
    labeled_by: str = "cues"

    @property
    def loc(self) -> str:
        return f"{self.file}:{self.line}"


def parse_paragraphs(path: Path, detex: bool, min_words: int) -> list[Para]:
    source = path.read_text(encoding="utf-8")
    out: list[Para] = []
    section = "(front)"
    buf: list[str] = []
    start = 1
    for i, line in enumerate(source.splitlines() + [""], 1):
        m = HEADING_RE.search(line)
        if m:
            section = m.group(2).strip() or section
        if line.strip():
            if not buf:
                start = i
            buf.append(line)
            continue
        if buf:
            raw = "\n".join(buf)
            prose = light_detex(raw) if detex else re.sub(r"\s+", " ", raw).strip()
            alpha = sum(c.isalpha() or c.isspace() for c in prose)
            if (len(prose.split()) >= min_words
                    and alpha / max(1, len(prose)) > 0.80):
                out.append(Para(file=path.name, line=start, section=section,
                                text=prose, raw=raw))
            buf = []
    return out


def discover(root: Path, chapter: str | None) -> list[Path]:
    files: list[Path] = []
    for name in SUBDIRS:
        d = root / "latex" / name
        if d.exists():
            files += sorted(d.glob("*.tex"))
    if not files:
        # --root may point at the chapters dir itself (rhythm_audit pattern)
        files = sorted(root.glob("*.tex"))
    if chapter:
        files = [f for f in files if f.name.startswith(chapter)]
    return files


# ------------------------------------------------------------- cue lexicon

BUILTIN: dict[str, tuple[str, list[str]]] = {
    "forecast": ("announces what the text is about to do", [
        "in this chapter", "this chapter", "in this section", "this book",
        "what follows", "in what follows", "we will see", "we'll see",
        "the rest of this", "our aim", "the plan", "we begin", "let us begin",
        "first, we", "i want to", "we turn now", "we now turn",
    ]),
    "recap": ("restates ground already covered", [
        "as we saw", "as we have seen", "we have seen", "so far", "to recap",
        "in summary", "to sum up", "as mentioned", "as noted", "as discussed",
        "having seen", "having established", "in short", "the upshot",
    ]),
    "question": ("raises a question for the reader", [
        "the question is", "the question becomes", "which raises",
        "consider whether", "one might ask", "why does", "what happens",
        "how do we", "what would", "who decides",
    ]),
    "definition": ("names and fixes the meaning of a term", [
        "refers to", "is defined as", "we call", "is called", "known as",
        "termed", "by which i mean", "by which we mean", "means that",
        "the term", "in other words, a",
    ]),
    "concession": ("grants ground to the other side", [
        "granted", "admittedly", "to be sure", "of course", "no doubt",
        "it is true", "it's true", "certainly", "fair enough", "concede",
        "there is something to", "critics are right", "even if",
    ]),
    "contrast": ("turns against what came before", [
        "but", "however", "yet", "on the other hand", "by contrast",
        "in contrast", "nevertheless", "nonetheless", "even so", "whereas",
        "instead", "rather than", "the trouble is", "the problem is",
    ]),
    "evidence": ("supplies data, a case, or an example", [
        "for example", "for instance", "consider the case", "in one study",
        "studies show", "research shows", "the data", "a survey",
        "according to", "in practice", "take the case", "e.g.", "such as",
        "measured", "per cent", "percent",
    ]),
    "cause": ("asserts a causal or inferential link", [
        "because", "therefore", "as a result", "consequently", "which is why",
        "hence", "thus", "so that", "leads to", "results in", "causes",
        "produces", "drives", "it follows that", "that is why",
    ]),
    "elaboration": ("expands, restates, or sharpens the previous point", [
        "in other words", "that is,", "put differently", "more precisely",
        "specifically", "in fact", "indeed", "moreover", "furthermore",
        "in addition", "what this means", "to put it another way",
    ]),
    "comparison": ("maps the point onto something else", [
        "just as", "similarly", "likewise", "compared to", "in the same way",
        "analogous", "the equivalent of", "think of it as", "is like",
        "as if it were", "much like",
    ]),
    "enumeration": ("counts off members of a set", [
        "first,", "second,", "third,", "fourth,", "finally,", "lastly",
        "one of", "another", "the other", "for one thing", "next,",
    ]),
    "narrative": ("tells what happened — a scene or an anecdote", [
        "one morning", "years later", "at the time", "that night",
        "he said", "she said", "they said", "in 19", "in 20", "then he",
        "then she", "recalled", "remembered",
    ]),
    "directive": ("tells the reader to do or notice something", [
        "note that", "notice", "imagine", "suppose", "consider",
        "try", "open the", "run the", "you can", "if you", "let's", "let us",
        "watch what", "keep in mind",
    ]),
    "attribution": ("hands the floor to a named source", [
        "argues", "writes", "observes", "points out", "reports",
        "in his", "in her", "in their", "quoted", "puts it", "calls it",
    ]),
    "qualification": ("limits the scope or confidence of a claim", [
        "may", "might", "arguably", "roughly", "in principle", "tends to",
        "for the most part", "with exceptions", "at least in", "so far as",
        "it seems", "suggests that", "not always", "up to a point",
    ]),
    "claim": ("asserts a position without a cue on it", []),
}

FALLBACK_LABEL = "claim"

IRREGULAR_PAST = {
    "was", "were", "had", "did", "said", "went", "came", "took", "saw",
    "knew", "thought", "found", "gave", "told", "became", "left", "felt",
    "put", "brought", "began", "kept", "held", "wrote", "stood", "heard",
    "let", "meant", "set", "met", "ran", "paid", "sat", "spoke", "lay",
}
NARRATIVE_PRONOUNS = {"he", "she", "him", "her", "his", "hers", "they",
                      "them", "their", "himself", "herself"}
SPEECH_VERBS = {"said", "asked", "replied", "answered", "shouted",
                "whispered", "muttered"}
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*")


# Single-word cues are weak evidence and function words are no evidence at
# all: the ontology legitimately lists "and" under additive transitions, but a
# paragraph containing "and" has told us nothing. Weight by specificity.
WEAK_CUES = {
    "and", "or", "but", "so", "yet", "as", "if", "then", "thus", "hence",
    "it", "this", "that", "these", "those", "there", "here", "also", "still",
    "now", "next", "first", "second", "third", "may", "might", "such",
    "while", "since", "because", "indeed", "however", "one", "another",
}


def cue_weight(cue: str) -> float:
    words = cue.split()
    if len(words) >= 3:
        return 1.4
    if len(words) == 2:
        return 1.0
    if cue.lower() in WEAK_CUES or len(cue) <= 3:
        return 0.3
    return 0.6


@dataclass
class Move:
    label: str
    desc: str
    cues: list[str]
    origin: str = "builtin"       # builtin | discourse_moves
    category: str = ""
    patterns: list[tuple[str, re.Pattern, float]] = field(default_factory=list)

    def compile(self) -> None:
        self.patterns = [
            (c, re.compile(r"(?<!\w)" + re.escape(c) + r"(?!\w)", re.I),
             cue_weight(c))
            for c in dict.fromkeys(self.cues) if c.strip()
        ]


def load_inventory(verbose: bool) -> dict[str, Move]:
    """Built-in families, then any discourse_moves records carrying cues."""
    moves = {label: Move(label, desc, list(cues))
             for label, (desc, cues) in BUILTIN.items()}
    merged, added = 0, 0
    if wo is not None:
        try:
            branch = wo.load_branch("discourse_moves")
        except (OSError, ValueError):
            branch = None
            if verbose:
                print("move_annotator: no discourse_moves branch in "
                      f"{wo.ONTOLOGY_DIR}; built-in cues only", file=sys.stderr)
        if branch:
            for cat, entries in (branch.get("categories") or {}).items():
                for e in entries:
                    if not isinstance(e, dict):
                        continue
                    cues = [c for c in (e.get("cues") or []) if isinstance(c, str)]
                    if not cues:
                        continue
                    label = str(e.get("name", "")).strip().lower()
                    if not label:
                        continue
                    if label in moves:
                        moves[label].cues += cues
                        merged += 1
                    else:
                        moves[label] = Move(label, e.get("definition", ""),
                                            cues, "discourse_moves", cat)
                        added += 1
            if verbose:
                print(f"move_annotator: discourse_moves merged — {added} new "
                      f"label(s), {merged} extended", file=sys.stderr)
    elif verbose:
        print("move_annotator: writing_ontology unavailable; built-in cues only",
              file=sys.stderr)
    for m in moves.values():
        m.compile()
    return moves


# ------------------------------------------------------------- classifier

def classify(p: Para, moves: dict[str, Move], tok) -> None:
    text = p.text
    words = [w.lower() for w in WORD_RE.findall(text)]
    n = max(1, len(words))
    scores: dict[str, float] = {}
    evidence: dict[str, list[str]] = {}

    for label, mv in moves.items():
        for cue, rx, weight in mv.patterns:
            hits = list(rx.finditer(text))
            if not hits:
                continue
            # a cue in the opening clause is doing the paragraph's steering
            position = 3.0 if hits[0].start() < 60 else 1.0
            scores[label] = scores.get(label, 0.0) + weight * (
                position + min(1.0, 0.5 * (len(hits) - 1)))
            evidence.setdefault(label, []).append(cue)

    def bump(label: str, amount: float, why: str) -> None:
        if label not in moves:
            return
        scores[label] = scores.get(label, 0.0) + amount
        evidence.setdefault(label, []).append(why)

    # structural signals the cue table cannot see
    sents = [s.strip() for s in tok.tokenize(text) if s.strip()]
    qs = [s for s in sents if s.endswith("?")]
    if qs:
        bump("question", 2.5 + (2.0 if sents and sents[0].endswith("?") else 0.0),
             f"{len(qs)} interrogative sentence(s)")
    if re.search(r"\\(?:key)?term\{|\\newterm\{", p.raw):
        bump("definition", 2.0, "\\term markup")
    if re.search(r"\\(?:auto|text|paren|foot)?cite\w*\{", p.raw):
        bump("attribution", 2.0, "citation")
    digits = sum(1 for w in text.split() if any(c.isdigit() for c in w))
    if digits >= 2:
        bump("evidence", 1.5, f"{digits} numeric tokens")
    past = sum(1 for w in words
               if w in IRREGULAR_PAST or (len(w) > 4 and w.endswith("ed")))
    pron = sum(1 for w in words if w in NARRATIVE_PRONOUNS)
    # a scene needs sustained past tense AND people in it; one historical
    # aside inside an argument paragraph should not read as narrative
    if past >= 4 and pron >= 3 and past / n > 0.05 and pron / n > 0.03:
        bump("narrative", 3.0, f"past-tense {100 * past / n:.0f}%, "
                               f"pronouns {100 * pron / n:.0f}%")
    if any(w in SPEECH_VERBS for w in words) and "\u201c" in text:
        bump("narrative", 2.0, "quoted dialogue")
    you = sum(1 for w in words if w in ("you", "your"))
    if you >= 3 and you / n > 0.025:
        bump("directive", 1.5, f"second person {100 * you / n:.0f}%")

    if not scores:
        p.label, p.score, p.evidence = FALLBACK_LABEL, 0.0, []
        return
    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    best, best_score = ranked[0]
    if best_score < 1.0:
        p.label, p.score = FALLBACK_LABEL, best_score
    else:
        p.label, p.score = best, best_score
    p.evidence = evidence.get(p.label, [])[:3]
    p.runner_up = ranked[1][0] if len(ranked) > 1 else ""


# ----------------------------------------------------------------- LLM pass

def resolve_model(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic:claude-sonnet-5"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai:gpt-5.6-terra"
    return None


def llm_instructions(moves: dict[str, Move]) -> str:
    lines = [f"  {label} — {mv.desc}" for label, mv in moves.items()]
    return f"""\
You label paragraphs of a book manuscript with the discourse move each one
performs — the job the paragraph does in the argument or the narrative, not
its subject matter. Choose EXACTLY ONE label from this inventory, using the
label string verbatim:

{chr(10).join(lines)}

Pick the paragraph's dominant move; a paragraph that concedes a point before
turning on it is a concession only if the concession is the point of the
paragraph. Give a one-clause reason and quote the cue you keyed on, if any."""


def llm_inventory(moves: dict[str, Move], paras: list[Para]) -> dict[str, Move]:
    """The label set the model chooses from: the built-in families plus any
    ontology labels the cue pass actually reached. A 200-label ontology
    branch would otherwise bury the prompt (and the taxonomy's own long tail
    is not reliably distinguishable at paragraph scale)."""
    used = {p.label for p in paras}
    return {lbl: mv for lbl, mv in moves.items()
            if mv.origin == "builtin" or lbl in used}


def llm_relabel(paras: list[Para], moves: dict[str, Move], model: str,
                limit: int) -> None:
    from pydantic import BaseModel, Field
    from pydantic_ai import Agent

    class Label(BaseModel):
        label: str = Field(description="one label from the inventory")
        why: str = ""

    agent = Agent(model, output_type=Label, instructions=llm_instructions(moves))
    todo = paras[:limit]
    print(f"move_annotator: relabeling {len(todo)} paragraph(s) with {model}…",
          file=sys.stderr)
    for i, p in enumerate(todo, 1):
        try:
            v = agent.run_sync(p.text[:6000]).output
        except Exception as e:  # auth, rate limit, refusal — keep going
            print(f"  [{i}/{len(todo)}] {p.loc} ERROR {e}", file=sys.stderr)
            continue
        label = v.label.strip().lower()
        if label not in moves:
            print(f"  [{i}/{len(todo)}] {p.loc} unlisted label {v.label!r}; "
                  "keeping cue label", file=sys.stderr)
            continue
        p.label, p.labeled_by = label, model
        if v.why:
            p.evidence = [v.why]


# ------------------------------------------------------------------ reports

def runs_of(paras: list[Para], min_len: int) -> list[tuple[str, int, int, int]]:
    """(label, start_index, end_index, length) for runs of the same label."""
    out = []
    i = 0
    while i < len(paras):
        j = i
        while j + 1 < len(paras) and paras[j + 1].label == paras[i].label:
            j += 1
        if j - i + 1 >= min_len:
            out.append((paras[i].label, i, j, j - i + 1))
        i = j + 1
    return out


def distribution(paras: list[Para]) -> list[tuple[str, int, float]]:
    counts: dict[str, int] = {}
    for p in paras:
        counts[p.label] = counts.get(p.label, 0) + 1
    total = max(1, len(paras))
    return sorted(((lbl, n, 100 * n / total) for lbl, n in counts.items()),
                  key=lambda t: (-t[1], t[0]))


def gaps_of(paras: list[Para], moves: dict[str, Move]) -> dict[str, list[str]]:
    used = {p.label for p in paras}
    out: dict[str, list[str]] = {"builtin": [], "ontology": []}
    for lbl, mv in moves.items():
        if lbl in used:
            continue
        out["builtin" if mv.origin == "builtin" else "ontology"].append(lbl)
    return {k: sorted(v) for k, v in out.items()}


def print_gaps(paras: list[Para], moves: dict[str, Move], indent: str) -> None:
    g = gaps_of(paras, moves)
    if g["builtin"]:
        print(f"{indent}never used: {', '.join(g['builtin'])}")
    if g["ontology"]:
        sample = ", ".join(g["ontology"][:6])
        print(f"{indent}unused ontology moves: {len(g['ontology'])} "
              f"(e.g. {sample}) — browse with "
              "`writing_ontology.py show discourse_moves`")


def report_file(name: str, paras: list[Para], moves: dict[str, Move],
                show_sequence: bool, run_len: int) -> None:
    print(f"\n{name} — {len(paras)} paragraph(s)")
    if show_sequence:
        w = max(len(p.label) for p in paras)
        for k, p in enumerate(paras, 1):
            ev = f"  [{'; '.join(p.evidence)}]" if p.evidence else ""
            snippet = p.text[:58] + ("…" if len(p.text) > 58 else "")
            print(f"  {k:3d} l.{p.line:<5d} {p.label:<{w}s} {snippet}{ev}")
    print("  distribution:")
    for lbl, n, pct in distribution(paras):
        bar = "\u2588" * max(1, round(pct / 5))
        print(f"    {lbl:<14s} {n:3d}  {pct:5.1f}%  {bar}")
    print_gaps(paras, moves, "  ")
    for lbl, i, j, ln in runs_of(paras, run_len):
        print(f"  monotony: \u00b6{i + 1}-\u00b6{j + 1} ({ln} in a row) all "
              f"'{lbl}' — l.{paras[i].line}")


def strict_violations(by_file: dict[str, list[Para]], moves: dict[str, Move],
                      run_len: int, floor: float) -> list[str]:
    """The --strict gate: what a release should not ship.

    Two conditions, both measured book-wide and both already reported:
    any monotony run the report flags (>= --run-length identical moves in a
    row), and built-in family coverage below --min-coverage. Coverage is
    counted over the built-in families only — the ontology's several hundred
    discourse moves are a menu, not a checklist, and requiring a share of
    them would fail every book.
    """
    out: list[str] = []
    for name, ps in by_file.items():
        for lbl, i, j, ln in runs_of(ps, run_len):
            out.append(f"{name}: {ln} consecutive '{lbl}' paragraphs "
                       f"(¶{i + 1}-¶{j + 1}, l.{ps[i].line})")
    builtin = {lbl for lbl, mv in moves.items() if mv.origin == "builtin"}
    if builtin:
        used = {p.label for ps in by_file.values() for p in ps} & builtin
        share = len(used) / len(builtin)
        if share < floor:
            missing = ", ".join(sorted(builtin - used))
            out.append(f"built-in move coverage {share:.0%} < {floor:.0%} "
                       f"({len(used)}/{len(builtin)}); never used: {missing}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path,
                    default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--text", help="annotate one plain-text or .tex file")
    ap.add_argument("--chapter", help="restrict to files starting with this")
    ap.add_argument("--min-words", type=int, default=15,
                    help="shortest block counted as a paragraph (default 15)")
    ap.add_argument("--run-length", type=int, default=3,
                    help="flag runs of N identical moves (default 3)")
    ap.add_argument("--no-sequence", dest="sequence", action="store_false",
                    help="tables only, no per-paragraph listing")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when the report flags a monotony run or "
                         "built-in move coverage falls below --min-coverage "
                         "(advisory otherwise: always exits 0)")
    ap.add_argument("--min-coverage", type=float, default=0.5, metavar="F",
                    help="--strict floor: share of the built-in move families "
                         "used at least once book-wide (default 0.5)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--llm", action="store_true",
                    help="relabel paragraphs with a model")
    ap.add_argument("--model", default=None,
                    help="pydantic-ai model (default: from ANTHROPIC_API_KEY / "
                         "OPENAI_API_KEY)")
    ap.add_argument("--limit", type=int, default=40,
                    help="most paragraphs sent to the model (default 40)")
    args = ap.parse_args()

    if args.text:
        path = Path(args.text)
        paras = parse_paragraphs(path, path.suffix == ".tex", args.min_words)
    else:
        files = discover(args.root, args.chapter)
        if not files:
            raise SystemExit(
                f"move_annotator: no .tex files under {args.root}/latex/")
        paras = []
        for f in files:
            paras += parse_paragraphs(f, True, args.min_words)
    if not paras:
        raise SystemExit("move_annotator: no prose paragraphs found")
    for i, p in enumerate(paras):
        p.index = i

    moves = load_inventory(verbose=not args.json)

    from nupunkt import PunktSentenceTokenizer
    tok = PunktSentenceTokenizer()
    for p in paras:
        classify(p, moves, tok)

    if args.llm:
        model = resolve_model(args.model)
        if model is None:
            print("move_annotator: no ANTHROPIC_API_KEY or OPENAI_API_KEY — "
                  "staying with the cue lexicon (fully functional)",
                  file=sys.stderr)
        else:
            try:
                llm_relabel(paras, llm_inventory(moves, paras), model,
                            args.limit)
            except ImportError as e:
                print(f"move_annotator: pydantic-ai unavailable ({e}); "
                      "staying with the cue lexicon", file=sys.stderr)

    by_file: dict[str, list[Para]] = {}
    for p in paras:
        by_file.setdefault(p.file, []).append(p)

    violations = (strict_violations(by_file, moves, args.run_length,
                                    args.min_coverage)
                  if args.strict else [])

    if args.json:
        print(json.dumps({
            "inventory": {lbl: {"description": mv.desc, "origin": mv.origin,
                                "category": mv.category, "cues": len(mv.cues)}
                          for lbl, mv in moves.items()},
            "paragraphs": [
                {"file": p.file, "line": p.line, "section": p.section,
                 "index": p.index, "move": p.label, "score": round(p.score, 2),
                 "runner_up": p.runner_up, "evidence": p.evidence,
                 "labeled_by": p.labeled_by, "text": p.text[:200]}
                for p in paras],
            "distribution": {
                "book": {lbl: n for lbl, n, _ in distribution(paras)},
                "by_file": {f: {lbl: n for lbl, n, _ in distribution(ps)}
                            for f, ps in by_file.items()},
            },
            "gaps": gaps_of(paras, moves),
            "monotony": [
                {"file": f, "move": lbl, "start_para": i + 1, "end_para": j + 1,
                 "length": ln, "line": ps[i].line}
                for f, ps in by_file.items()
                for lbl, i, j, ln in runs_of(ps, args.run_length)],
            "strict_violations": violations,
        }, indent=2))
        if violations:
            raise SystemExit(1)
        return

    print(f"corpus: {len(paras)} paragraph(s) in {len(by_file)} file(s); "
          f"{len(moves)} move label(s) in the inventory", file=sys.stderr)
    for name, ps in by_file.items():
        report_file(name, ps, moves, args.sequence, args.run_length)
    if len(by_file) > 1:
        print("\nBOOK — distribution")
        for lbl, n, pct in distribution(paras):
            print(f"    {lbl:<14s} {n:3d}  {pct:5.1f}%  "
                  + "\u2588" * max(1, round(pct / 5)))
        print_gaps(paras, moves, "  ")
    if violations:
        print("\nSTRICT \u2014 failing:")
        for v in violations:
            print(f"  {v}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
