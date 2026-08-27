#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "nupunkt>=0.6.0",
#     "pydantic>=2.7",
#     "pydantic-ai-slim[openai,anthropic]>=1.0",
# ]
# ///
"""Promise/payoff ledger: what the book sets up, and whether it pays off.

Reads the corpus in order — chapters first, then front/back matter, the same
discovery `make metrics` uses — and records every *promise*, a debt the text
takes on with the reader. Then it searches the text that follows for the
payoff. Four promise kinds, all detected offline (no API key needed):

  question     an interrogative sentence the prose raises
  forward-ref  an explicit deferral ("we'll return to", "more on this later")
  term         a term introduced for the first time (\\term{}, \\keyterm{},
               or a quoted phrase followed by a definition cue)
  entity       a capitalized multiword name that appears exactly once, in
               the first half of the book — a Chekhov's-gun candidate:
               a gun on the mantel that is never fired

Payoff audit (heuristic):

  term     paid = two or more later mentions; uncertain = exactly one;
           unpaid = the term never returns
  entity   unpaid by construction (that is what makes it a candidate)
  question / forward-ref
           keyword overlap with later paragraphs, boosted when a payoff
           cue ("as promised", "the answer", "returning to") sits nearby.
           paid = 2+ shared keywords, or 1 keyword plus a payoff cue;
           uncertain = a single weak match; unpaid = nothing downstream

Statuses are advisory. An unpaid question can be deliberate (a book may
raise a question it means to leave open); the ledger's job is to make the
choice visible, not to make it for you.

--llm re-judges the unpaid/uncertain rows: the model sees the promise plus
the best candidate passages and decides. It uses the same provider pattern
as slop_audit.py (ANTHROPIC_API_KEY or OPENAI_API_KEY, --model to force
one). Without a key the script prints a note and stays fully heuristic.

Usage:
    uv run scripts/setup_payoff.py                       # whole book
    uv run scripts/setup_payoff.py --chapter ch02
    uv run scripts/setup_payoff.py --kind question,forward-ref
    uv run scripts/setup_payoff.py --status unpaid
    uv run scripts/setup_payoff.py --text draft.txt --json
    uv run scripts/setup_payoff.py --llm --model anthropic:claude-sonnet-5

Advisory: always exits 0 (use --strict to fail when unpaid promises exist).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

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
WORD_RE = re.compile(r"[a-z][a-z'-]*[a-z]|[a-z]")

STOP = {
    "the", "and", "that", "this", "with", "from", "have", "has", "had", "for",
    "but", "not", "are", "was", "were", "you", "your", "our", "its", "it's",
    "they", "them", "their", "what", "when", "where", "which", "who", "whom",
    "will", "would", "can", "could", "should", "there", "here", "then", "than",
    "into", "onto", "over", "under", "about", "after", "before", "because",
    "been", "being", "does", "did", "doing", "just", "only", "also", "more",
    "most", "some", "such", "same", "each", "every", "any", "all", "one", "two",
    "how", "why", "very", "much", "many", "still", "even", "own",
    "way", "ways", "thing", "things", "make", "makes", "made", "take", "takes",
    "get", "gets", "got", "like", "want", "need", "use", "used", "uses",
}


def light_detex(text: str) -> str:
    """Cheap regex detex (slop_audit.py's recipe) — keeps macro *arguments*,
    which is what a promise ledger needs (\\term{gutter} -> gutter)."""
    text = re.sub(r"(?<!\\)%.*", "", text)
    text = text.replace("---", "\u2014").replace("--", "\u2013")
    text = text.replace("``", "\u201c").replace("''", "\u201d")
    for env in DROP_ENVS:
        text = re.sub(rf"\\begin\{{{env}\*?\}}.*?\\end\{{{env}\*?\}}", " ",
                      text, flags=re.DOTALL)
    text = re.sub(r"\$[^$]*\$", " ", text)
    text = re.sub(r"\\(?:label|ref|cref|Cref|[A-Za-z]*cite[A-Za-z]*|input|include)\*?"
                  r"(?:\[[^\]]*\])?\{[^}]*\}", " ", text)
    # \begin{box}[title=A real question?] — keep titles (they carry prose),
    # drop key=value options like [importance=high]
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
    text: str            # readable prose
    raw: str             # source as written (LaTeX macros intact)
    index: int = 0       # position in reading order
    start_word: int = 0  # cumulative word offset in the corpus
    words: set[str] = field(default_factory=set)

    @property
    def loc(self) -> str:
        return f"{self.file}:{self.line}"


def parse_paragraphs(path: Path, detex: bool, min_words: int) -> list[Para]:
    source = path.read_text(encoding="utf-8")
    paras: list[Para] = []
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
                paras.append(Para(file=path.name, line=start, section=section,
                                  text=prose, raw=raw))
            buf = []
    return paras


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


def load_corpus(args) -> list[Para]:
    if args.text:
        path = Path(args.text)
        paras = parse_paragraphs(path, path.suffix == ".tex", args.min_words)
    else:
        files = discover(args.root, args.chapter)
        if not files:
            raise SystemExit(
                f"setup_payoff: no .tex files under {args.root}/latex/")
        paras = []
        for f in files:
            paras += parse_paragraphs(f, True, args.min_words)
    offset = 0
    for i, p in enumerate(paras):
        p.index = i
        p.start_word = offset
        p.words = set(WORD_RE.findall(p.text.lower()))
        offset += len(p.text.split())
    return paras


# ------------------------------------------------------------ promise cues

FORWARD_CUES = [
    r"we(?:'|\u2019)?ll (?:return|come back|get|turn) to",
    r"we will (?:return|come back|get|turn) to",
    r"we(?:'|\u2019)?ll (?:see|show|explain|unpack|explore|examine|meet|"
    r"revisit|take up|have more to say)",
    r"we will (?:see|show|explain|unpack|explore|examine|meet|revisit)",
    r"as we(?:'|\u2019)?ll see",
    r"as we will see",
    r"as we shall see",
    r"more on (?:this|that|it|which)",
    r"(?:later|shortly) in (?:this|the) (?:chapter|book|section|part)",
    r"in (?:the next|a later|the following) (?:chapter|section|part)",
    r"in chapter\s+\w+",
    r"see (?:chapter|section|part)\s+\w+",
    r"the (?:rest|remainder) of (?:this|the) (?:chapter|book)",
    r"in what follows",
    r"for (?:the )?now",
    r"set(?:ting)? (?:this|that) aside",
    r"put a pin in",
    r"we (?:take|pick) (?:this|that|it) up",
    r"(?:comes?|comes back|returns) (?:to this )?later",
    r"defer(?:red|ring)? (?:this|that|it)?",
    r"we(?:'|\u2019)?ll (?:answer|address) (?:this|that)",
    r"(?:that|this|the) (?:question|puzzle|thread) (?:will|is) (?:be )?"
    r"(?:answered|taken up|resolved)",
    r"coming (?:up|back) to",
    r"below,? we",
    r"stay with (?:this|that)",
]
FORWARD_RE = re.compile("|".join(f"(?:{c})" for c in FORWARD_CUES), re.I)

PAYOFF_CUES = [
    r"as promised", r"as (?:we|i) (?:saw|noted|said|promised|mentioned)",
    r"returning to", r"back to (?:the|that|our)", r"the answer",
    r"we can now", r"now we can", r"having (?:seen|established|shown)",
    r"to answer (?:that|the|this)", r"which answers", r"the promised",
    r"earlier (?:we|i)", r"that (?:question|thread|puzzle|point)",
    r"recall (?:that|the)", r"it turns out",
]
PAYOFF_RE = re.compile("|".join(f"(?:{c})" for c in PAYOFF_CUES), re.I)

TERM_MACRO_RE = re.compile(
    r"\\(?:key)?term\{([^}]{2,60})\}|\\newterm\{([^}]{2,60})\}")
QUOTED_DEF_RE = re.compile(
    r"[\u201c\"']([a-z][^\u201d\"']{2,48})[\u201d\"']\s*"
    r"(?:is|are|means|refers to|denotes|describes|names)\b")
# "called X" only counts when X is quoted \u2014 otherwise "called the manuscript a
# software project" reads as a definition. Bare naming needs a stronger cue.
CALLED_QUOTED_RE = re.compile(
    r"\b(?:called|known as|termed|dubbed|what (?:we|I) call)\s+"
    r"[\u201c\"']([a-z][^\u201d\"']{2,40})[\u201d\"']")
CALLED_BARE_RE = re.compile(
    r"\b(?:known as|termed|dubbed|what (?:we|I) call)\s+"
    r"(?!the\b|a\b|an\b|its\b|their\b)"
    r"([a-z][a-z\-]+(?:\s+[a-z][a-z\-]+){0,2})\b")
ENTITY_RE = re.compile(
    r"\b([A-Z][a-z][A-Za-z'\-]*(?:\s+(?:of|the|de|van|von|der|and)\s+)?"
    r"(?:\s*[A-Z][a-z][A-Za-z'\-]*)+)\b")
ENTITY_STOP = {
    "the", "a", "an", "but", "and", "if", "when", "what", "this", "that",
    "there", "here", "it", "its", "every", "no", "not", "for", "in", "on",
    "chapter", "section", "figure", "table", "part", "appendix", "page",
    "first", "second", "third", "next", "one", "two", "three", "you", "we",
}


def keywords_of(text: str, df: dict[str, int], n_paras: int,
                k: int = 12) -> list[str]:
    """Content words that can serve as a handle on the promise: skip stopwords
    and skip words so common in this corpus that a match means nothing.
    Rarest first, longer word wins ties (topic words beat filler)."""
    ceiling = max(2, int(0.5 * n_paras))
    seen: dict[str, int] = {}
    for w in WORD_RE.findall(text.lower()):
        if len(w) < 4 or w in STOP:
            continue
        d = df.get(w, 0)
        if d > ceiling:
            continue
        seen[w] = d
    ranked = sorted(seen.items(), key=lambda kv: (kv[1], -len(kv[0]), kv[0]))
    return [w for w, _ in ranked][:k]


# ------------------------------------------------------------ ledger records

@dataclass
class Promise:
    kind: str            # question | forward-ref | term | entity
    text: str            # the promising sentence / the term
    key: str             # normalized identity (dedup handle)
    file: str
    line: int
    section: str
    para_index: int
    keywords: list[str] = field(default_factory=list)
    status: str = "unpaid"          # paid | uncertain | unpaid
    where: str | None = None        # file:line of the payoff
    evidence: str = ""
    judged_by: str = "heuristic"

    @property
    def loc(self) -> str:
        return f"{self.file}:{self.line}"

    def as_dict(self) -> dict:
        return {
            "kind": self.kind, "promise": self.text, "key": self.key,
            "file": self.file, "line": self.line, "section": self.section,
            "keywords": self.keywords, "status": self.status,
            "paid_at": self.where, "evidence": self.evidence,
            "judged_by": self.judged_by,
        }


def collect_promises(paras: list[Para], tok, df: dict[str, int],
                     total_words: int) -> list[Promise]:
    n_paras = len(paras)
    promises: list[Promise] = []
    seen_terms: set[str] = set()

    for p in paras:
        sents = [s.strip() for s in tok.tokenize(p.text) if s.strip()]

        # 1. questions the prose raises
        for s in sents:
            if not s.endswith("?") or len(s.split()) < 4:
                continue
            promises.append(Promise(
                kind="question", text=s, key=s.lower()[:80], file=p.file,
                line=p.line, section=p.section, para_index=p.index,
                keywords=keywords_of(s, df, n_paras)))

        # 2. explicit forward references
        for s in sents:
            m = FORWARD_RE.search(s)
            if not m:
                continue
            promises.append(Promise(
                kind="forward-ref", text=s, key=m.group(0).lower(),
                file=p.file, line=p.line, section=p.section,
                para_index=p.index, keywords=keywords_of(s, df, n_paras)))
            break  # one deferral per paragraph is enough signal

        # 3. first introduction of a marked or defined term
        cands: list[str] = []
        for m in TERM_MACRO_RE.finditer(p.raw):
            cands.append(light_detex(m.group(1) or m.group(2) or ""))
        cands += [m.group(1) for m in QUOTED_DEF_RE.finditer(p.text)]
        cands += [m.group(1) for m in CALLED_QUOTED_RE.finditer(p.text)]
        cands += [m.group(1) for m in CALLED_BARE_RE.finditer(p.text)]
        for term in cands:
            norm = re.sub(r"\s+", " ", term.strip().lower())
            if len(norm) < 3 or norm in seen_terms:
                continue
            seen_terms.add(norm)
            promises.append(Promise(
                kind="term", text=term.strip(), key=norm, file=p.file,
                line=p.line, section=p.section, para_index=p.index,
                keywords=[norm]))

    # 4. Chekhov's-gun candidates: multiword names used exactly once, early
    counts: dict[str, int] = {}
    firsts: dict[str, Para] = {}
    for p in paras:
        for m in ENTITY_RE.finditer(p.text):
            name = re.sub(r"\s+", " ", m.group(1).strip())
            toks = name.split()
            if len(toks) < 2 or any(t.lower() in ENTITY_STOP for t in toks):
                continue
            counts[name] = counts.get(name, 0) + 1
            firsts.setdefault(name, p)
    half = total_words / 2
    for name, n in sorted(counts.items()):
        p = firsts[name]
        if n != 1 or p.start_word > half:
            continue
        promises.append(Promise(
            kind="entity", text=name, key=name.lower(), file=p.file,
            line=p.line, section=p.section, para_index=p.index,
            keywords=[name.lower()], status="unpaid",
            evidence="named once, in the first half, never again"))

    promises.sort(key=lambda pr: (pr.para_index, pr.kind, pr.text[:40]))
    return promises


# ------------------------------------------------------------- payoff audit

def mention_re(term: str) -> re.Pattern:
    body = re.escape(term).replace(r"\ ", r"\s+")
    return re.compile(rf"\b{body}(?:s|es|'s|\u2019s)?\b", re.I)


def candidates_for(pr: Promise, paras: list[Para]) -> list[tuple[float, Para, str]]:
    """Score later paragraphs as possible payoffs. Returns best-first."""
    out: list[tuple[float, Para, str]] = []
    kws = [k for k in pr.keywords if k]
    for p in paras:
        if p.index <= pr.para_index:
            continue
        hits = [k for k in kws if k in p.words or k in p.text.lower()]
        if not hits:
            continue
        cue = PAYOFF_RE.search(p.text)
        score = len(hits) + (1.5 if cue else 0.0)
        why = "keywords: " + ", ".join(hits[:4])
        if cue:
            why += f'; payoff cue "{cue.group(0)}"'
        out.append((score, p, why))
    out.sort(key=lambda t: (-t[0], t[1].index))
    return out


def audit(promises: list[Promise], paras: list[Para]) -> None:
    for pr in promises:
        if pr.kind == "entity":
            continue

        if pr.kind == "term":
            rx = mention_re(pr.key)
            later = [p for p in paras
                     if p.index > pr.para_index and rx.search(p.text)]
            if len(later) >= 2:
                pr.status, pr.where = "paid", later[0].loc
                pr.evidence = f"{len(later)} later mentions"
            elif len(later) == 1:
                pr.status, pr.where = "uncertain", later[0].loc
                pr.evidence = "mentioned once more, then dropped"
            else:
                pr.status, pr.where = "unpaid", None
                pr.evidence = "introduced but never used again"
            continue

        cands = candidates_for(pr, paras)
        if not cands:
            pr.status, pr.evidence = "unpaid", "no later passage shares its terms"
            continue
        score, p, why = cands[0]
        if score >= 2.0:
            pr.status, pr.where, pr.evidence = "paid", p.loc, why
        else:
            pr.status, pr.where, pr.evidence = "uncertain", p.loc, why


# ----------------------------------------------------------------- LLM pass

def resolve_model(explicit: str | None) -> str | None:
    """slop_audit.py's provider pattern: explicit wins, else pick by key."""
    if explicit:
        return explicit
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic:claude-sonnet-5"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai:gpt-5.6-terra"
    return None


LLM_INSTRUCTIONS = """\
You audit a book manuscript's promise/payoff ledger. A PROMISE is a debt the
prose takes on with the reader: a question it raises, an explicit deferral
("we'll return to this"), or a term it introduces. The manuscript pays the
promise off when later text answers, delivers, or genuinely uses it.

You get the promise, where it occurs, and the candidate later passages a
keyword search surfaced. Decide:

  paid       a candidate clearly discharges the promise
  uncertain  something related appears, but it does not settle the promise
  unpaid     nothing in the candidates delivers on it

Judge only what the candidates show; missing text means unpaid, not paid.
Set `where` to the location string of the paying candidate, or null.
Keep `why` to one sentence."""


def llm_review(promises: list[Promise], paras: list[Para], model: str,
               limit: int) -> None:
    from pydantic import BaseModel, Field
    from pydantic_ai import Agent

    class Verdict(BaseModel):
        status: str = Field(description="paid | uncertain | unpaid")
        where: str | None = None
        why: str = ""

    agent = Agent(model, output_type=Verdict, instructions=LLM_INSTRUCTIONS)
    todo = [p for p in promises
            if p.status in ("uncertain", "unpaid") and p.kind != "entity"][:limit]
    print(f"setup_payoff: re-judging {len(todo)} promise(s) with {model}…",
          file=sys.stderr)
    for i, pr in enumerate(todo, 1):
        cands = candidates_for(pr, paras)[:3]
        if not cands:
            continue
        blocks = "\n\n".join(
            f"[{p.loc}] {p.text[:900]}" for _s, p, _w in cands)
        prompt = (f"PROMISE ({pr.kind}) at {pr.loc}: {pr.text}\n\n"
                  f"CANDIDATE LATER PASSAGES:\n\n{blocks}")
        try:
            v = agent.run_sync(prompt).output
        except Exception as e:  # auth, rate limit, refusal — keep going
            print(f"  [{i}/{len(todo)}] {pr.loc} ERROR {e}", file=sys.stderr)
            continue
        if v.status in ("paid", "uncertain", "unpaid"):
            pr.status = v.status
            pr.where = v.where or pr.where
            pr.evidence = v.why or pr.evidence
            pr.judged_by = model


# ------------------------------------------------------------------ reports

KINDS = ("question", "forward-ref", "term", "entity")
STATUSES = ("paid", "uncertain", "unpaid")


def report(promises: list[Promise], all_promises: list[Promise],
           limit: int) -> None:
    if not promises:
        print("no promises matched the filters")
    else:
        w = max(len(p.loc) for p in promises)
        hdr = f"{'kind':11s} {'where':{w}s} {'status':9s} promise"
        print(hdr)
        print("-" * min(100, len(hdr) + 40))
        for pr in promises[:limit]:
            snippet = re.sub(r"\s+", " ", pr.text)[:64]
            print(f"{pr.kind:11s} {pr.loc:{w}s} {pr.status:9s} {snippet}")
            tail = []
            if pr.where and pr.status != "unpaid":
                tail.append(f"paid at {pr.where}")
            if pr.evidence:
                tail.append(pr.evidence)
            if pr.judged_by != "heuristic":
                tail.append(f"[{pr.judged_by}]")
            if tail:
                print(f"{'':11s} {'':{w}s} {'':9s} \u2514 " + "; ".join(tail))
        if len(promises) > limit:
            print(f"… {len(promises) - limit} more (raise --limit)")

    print()
    print(f"{'':11s} {'paid':>7s} {'uncert':>7s} {'unpaid':>7s} {'total':>7s}")
    for kind in KINDS:
        rows = [p for p in all_promises if p.kind == kind]
        if not rows:
            continue
        c = {s: sum(1 for p in rows if p.status == s) for s in STATUSES}
        print(f"{kind:11s} {c['paid']:7d} {c['uncertain']:7d} "
              f"{c['unpaid']:7d} {len(rows):7d}")
    c = {s: sum(1 for p in all_promises if p.status == s) for s in STATUSES}
    print(f"{'ALL':11s} {c['paid']:7d} {c['uncertain']:7d} "
          f"{c['unpaid']:7d} {len(all_promises):7d}")
    unpaid = [p for p in all_promises if p.status == "unpaid"]
    if unpaid:
        print(f"\nsetup_payoff: {len(unpaid)} unpaid promise(s) — a setup with "
              "no payoff is either a cut or a debt; decide which.")


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path,
                    default=Path(__file__).resolve().parent.parent,
                    help="book root (default: this repo)")
    ap.add_argument("--text", help="audit one plain-text or .tex file instead")
    ap.add_argument("--chapter", help="restrict to files starting with this")
    ap.add_argument("--kind", help=f"comma list: {', '.join(KINDS)}")
    ap.add_argument("--status", help=f"comma list: {', '.join(STATUSES)}")
    ap.add_argument("--min-words", type=int, default=12,
                    help="shortest block counted as a paragraph (default 12)")
    ap.add_argument("--limit", type=int, default=60,
                    help="ledger rows printed (default 60)")
    ap.add_argument("--json", action="store_true", help="machine-readable ledger")
    ap.add_argument("--llm", action="store_true",
                    help="re-judge unpaid/uncertain rows with a model")
    ap.add_argument("--model", default=None,
                    help="pydantic-ai model (default: from ANTHROPIC_API_KEY / "
                         "OPENAI_API_KEY)")
    ap.add_argument("--llm-limit", type=int, default=25,
                    help="most promises sent to the model (default 25)")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when any promise is unpaid")
    args = ap.parse_args()

    paras = load_corpus(args)
    if not paras:
        raise SystemExit("setup_payoff: no prose paragraphs found")

    from nupunkt import PunktSentenceTokenizer
    tok = PunktSentenceTokenizer()

    df: dict[str, int] = {}
    for p in paras:
        for w in p.words:
            df[w] = df.get(w, 0) + 1
    total_words = sum(len(p.text.split()) for p in paras)

    promises = collect_promises(paras, tok, df, total_words)
    audit(promises, paras)

    if args.llm:
        model = resolve_model(args.model)
        if model is None:
            print("setup_payoff: no ANTHROPIC_API_KEY or OPENAI_API_KEY — "
                  "staying heuristic (the ledger below is complete without it)",
                  file=sys.stderr)
        else:
            try:
                llm_review(promises, paras, model, args.llm_limit)
            except ImportError as e:
                print(f"setup_payoff: pydantic-ai unavailable ({e}); "
                      "staying heuristic", file=sys.stderr)

    shown = promises
    if args.kind:
        keep = {k.strip() for k in args.kind.split(",")}
        unknown = keep - set(KINDS)
        if unknown:
            raise SystemExit(f"setup_payoff: unknown kind(s) {sorted(unknown)}")
        shown = [p for p in shown if p.kind in keep]
    if args.status:
        keep = {s.strip() for s in args.status.split(",")}
        unknown = keep - set(STATUSES)
        if unknown:
            raise SystemExit(f"setup_payoff: unknown status(es) {sorted(unknown)}")
        shown = [p for p in shown if p.status in keep]

    if args.json:
        print(json.dumps({
            "paragraphs": len(paras), "words": total_words,
            "promises": [p.as_dict() for p in shown],
            "summary": {
                kind: {s: sum(1 for p in promises
                              if p.kind == kind and p.status == s)
                       for s in STATUSES}
                for kind in KINDS
            },
        }, indent=2))
    else:
        print(f"corpus: {len(paras)} paragraphs, {total_words:,} words, "
              f"{len(promises)} promise(s)\n", file=sys.stderr)
        report(shown, promises, args.limit)

    if args.strict and any(p.status == "unpaid" for p in promises):
        sys.exit(1)


if __name__ == "__main__":
    main()
