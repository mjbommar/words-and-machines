#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pydetex>=1.1.1",
#     "nupunkt>=0.6.0",
#     "pydantic>=2.7",
#     "pydantic-ai-slim[openai,anthropic]>=1.0",
# ]
# ///
"""Multi-level slop audit: quantitative signals + taxonomy-driven LLM judge.

QUANTITATIVE PASS (offline, free) — signals from the slop/homogenization
literature at every granularity, all findings anchored file:line:

  file / section   slop-vocabulary density, contrast-frame rate, compression
  paragraph        compression-ratio z-outliers, slop density, constructions
  sentence         individual construction matches, quoted

Sources: sam-paech/slop-forensics lists (cached ~/.cache/slop-forensics/),
Wikipedia "Signs of AI writing" vocabulary, Antislop (arXiv:2510.15061),
compression ratio per Shaib et al. 2024 (arXiv:2403.00553).

LLM JUDGE (--llm) — audits sampled units against a ~50-tell taxonomy
(--list-tells prints it). Every tell can be switched on/off individually
or by group, and each verdict carries per-tell evidence quotes, so you
get specific results about specific violations plus a per-tell aggregate.

Units and sampling compose freely:

  --unit paragraph|sentence|line|section|file      what gets judged
  --sample worst|random|all                        how units are chosen
  --n N        N random units          --pct X     X percent of units
  --limit N    safety cap (default 50; 0 = uncapped, e.g. whole book)

The judge runs one unit at a time via pydantic-ai; the model is
provider-prefixed and works with BOTH OpenAI and Anthropic:

  --model anthropic:claude-sonnet-5    (default)
  --model anthropic:claude-fable-5
  --model openai:gpt-5.6-terra         (also -sol / -luna)

Examples:
  uv run scripts/slop_audit.py                          # quantitative audit
  uv run scripts/slop_audit.py --list-tells             # print the taxonomy
  uv run scripts/slop_audit.py --llm --sample random --n 3          # 3 paras
  uv run scripts/slop_audit.py --llm --unit file --sample random --n 1
  uv run scripts/slop_audit.py --llm --unit line --sample random --n 10
  uv run scripts/slop_audit.py --llm --unit sentence --pct 2  # 2% of sentences
  uv run scripts/slop_audit.py --llm --sample all --limit 0   # entire book
  uv run scripts/slop_audit.py --llm --tells semantic         # one group
  uv run scripts/slop_audit.py --llm --tells not-x-but-y,thesis-restatement
  uv run scripts/slop_audit.py --llm --skip-tells narrative --format jsonl

Advisory only — never a CI gate. `make check` handles the hard bans.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
import statistics
import sys
import urllib.request
import zlib
from dataclasses import dataclass, field
from pathlib import Path

CACHE = Path.home() / ".cache" / "slop-forensics"
SLOP_REPO_RAW = "https://raw.githubusercontent.com/sam-paech/slop-forensics/main/data"

SUBDIRS = ("chapters", "frontmatter", "front-matter", "backmatter", "back-matter")
DROP_ENVS = (
    "tikzpicture", "figure", "table", "tabular", "tabularx", "lstlisting",
    "verbatim", "Verbatim", "equation", "align", "alignat", "gather",
    "definitionbox", "tryitbox", "examplebox", "codelisting", "promptcode",
    "outputcode",
)
WORD_RE = re.compile(r"[a-z][a-z'-]*[a-z]|[a-z]")

# ------------------------------------------------------------- the taxonomy
# ~50 tells, synthesized from STYLE-AI-TELLS.md, Wikipedia's "Signs of AI
# writing", slop-forensics, and the Antislop paper. Each entry:
# id -> (group, one-line description the judge sees). Toggle by id or group
# via --tells / --skip-tells.

TAXONOMY: dict[str, tuple[str, str]] = {
    # -- syntactic
    "this-opener":          ("syntactic", "serial sentences opening with 'This is/means/allows...' (pointing monotone)"),
    "gerund-opener":        ("syntactic", "sentences opening with Having/Being/Recognizing/Understanding participles"),
    "as-x-y-opener":        ("syntactic", "stacked 'As the X grew, Y happened' clause openers"),
    "rule-of-three":        ("syntactic", "compulsive triads: three parallel items, adjectives, or First/Second/Third"),
    "not-x-but-y":          ("syntactic", "contrast frames: 'not X, but Y', 'It's not X, it's Y', 'isn't just'"),
    "no-no-just":           ("syntactic", "'no X, no Y, just Z' triple-negation frame"),
    "filler-transition":    ("syntactic", "sentence-initial However/Furthermore/Moreover/Additionally/Indeed"),
    "hedge-cluster":        ("syntactic", "stacked hedges: might possibly, could potentially, seems to suggest"),
    "hedged-intensifier":   ("syntactic", "self-cancelling intensity: quite significant, rather important"),
    "nominalization":       ("syntactic", "verbs dressed as nouns: make a decision, reach a conclusion"),
    "rhetorical-question":  ("syntactic", "question immediately self-answered as a transition device"),
    "summary-opener":       ("syntactic", "announcing instead of doing: 'In this section we will explore...'"),
    "passive-dodge":        ("syntactic", "'should be [done]' passives with no named actor"),
    "trailing-participle":  ("syntactic", "comma + ensuring/showcasing/highlighting clause asserting significance"),
    "copulative-dodge":     ("syntactic", "inflated linking verbs replacing is/are: boasts, serves as, stands as"),
    "uniform-rhythm":       ("syntactic", "consecutive sentences of near-identical length and shape (low burstiness)"),
    "monotonous-starts":    ("syntactic", "many nearby sentences opening with the same word or pattern"),
    "parallel-echo":        ("syntactic", "adjacent sentences with cloned grammatical skeletons"),
    # -- structural
    "uniform-paragraphs":   ("structural", "every paragraph the same size and topic-sentence shape"),
    "summary-close":        ("structural", "paragraph or section ends by restating what it just said"),
    "motivational-closer":  ("structural", "empty encouragement ending: 'Now you're equipped to...'"),
    "signposting":          ("structural", "'Having discussed X, we now turn to Y'; 'as mentioned earlier'"),
    "exhaustive-list":      ("structural", "listing every case instead of two or three telling examples"),
    "disclaimer-sludge":    ("structural", "front-loaded caveats before saying anything"),
    "hypothetical-example": ("structural", "invented tidy scenario ('Imagine a small town...') where a real one belongs"),
    "despite-challenges":   ("structural", "'Despite these challenges, X continues to...' outline-shaped closer"),
    "outline-residue":      ("structural", "prose that reads like converted bullet points or 'key takeaways'"),
    "section-symmetry":     ("structural", "sections/chapters cloned from one structural template"),
    # -- semantic
    "false-balance":        ("semantic", "'both perspectives have merit' mush instead of a position"),
    "both-true-closure":    ("semantic", "'Both were true at once' juxtaposition-labelling tic"),
    "weasel-attribution":   ("semantic", "'experts agree', 'studies show', 'observers have cited' without names"),
    "temporal-waffle":      ("semantic", "'in recent years', 'over time' where a date is knowable"),
    "value-neutral-praise": ("semantic", "impressive/remarkable/elegant with no demonstrating evidence"),
    "empty-significance":   ("semantic", "'a testament to', 'underscores the importance', 'plays a vital role'"),
    "superlative-pile":     ("semantic", "stacked qualifiers: 'arguably one of the most significant...'"),
    "empty-reassurance":    ("semantic", "'simply', 'just', 'easily' minimizing real difficulty"),
    "promotional-register": ("semantic", "brochure diction: vibrant, nestled, rich heritage, renowned"),
    "thesis-restatement":   ("semantic", "the argument re-stated in near-identical words yet again"),
    "vague-abstraction":    ("semantic", "gestures at meaning with no checkable specifics anywhere"),
    "unearned-profundity":  ("semantic", "'In the end, X is really about Y' pseudo-depth"),
    "overexplaining":       ("semantic", "telling the reader what they just read or are about to read"),
    "knowledge-hedge":      ("semantic", "needless 'as of this writing' / 'information may have changed'"),
    # -- lexical
    "ai-vocabulary":        ("lexical", "delve, tapestry, intricate, pivotal, meticulous, interplay-class words"),
    "vocabulary-rut":       ("lexical", "one content word leaned on repeatedly within the passage"),
    "metaphor-cliche":      ("lexical", "stock metaphors: journey, landscape, tapestry, beacon, symphony"),
    "elegant-variation":    ("lexical", "strained synonym rotation to avoid repeating a plain word"),
    # -- narrative (fiction / narrative-scene prose)
    "sensory-cliche":       ("narrative", "'voice barely above a whisper', 'heart pounding', 'let out a breath'"),
    "emotion-telling":      ("narrative", "'a profound sense of', felt/realized narration replacing shown detail"),
    # -- punctuation
    "em-dash-chain":        ("punctuation", "two or more em dashes per paragraph doing filler work"),
    "parenthetical-overuse": ("punctuation", "parentheses every few sentences for unintegrated info"),
    "scare-quotes":         ("punctuation", "repeated 'scare quotes' around ordinary terms"),
    # -- voice
    "chatbot-voice":        ("voice", "assistant register leaking in: 'let's explore', 'it's worth noting'"),
    "person-drift":         ("voice", "unmotivated shifts between I/we/you/one mid-passage"),
    "tense-drift":          ("voice", "unmotivated past/present tense wobble within a passage"),
}

GROUPS = sorted({g for g, _ in TAXONOMY.values()})

# Wikipedia "Signs of AI writing" era vocabulary (2023->2026 + Grok set).
AI_VOCAB = {
    "delve", "delves", "delving", "tapestry", "intricate", "intricacies",
    "meticulous", "meticulously", "pivotal", "crucial", "underscore",
    "underscores", "underscoring", "testament", "vibrant", "boasts",
    "bolster", "bolstered", "garner", "garnered", "interplay", "enduring",
    "landscape", "showcase", "showcases", "showcasing", "fostering",
    "emphasizing", "highlighting", "enhancing", "encompassing",
    "multifaceted", "nuanced", "paramount", "renowned", "nestled",
    "seamlessly", "leverage", "leveraging", "myriad", "plethora",
    "empirical", "causal", "correlate",
}

# Mechanically detectable constructions for the quantitative pass.
CONSTRUCTIONS = [
    ("not-x-but-y", re.compile(
        r"\b(?:it|this|that|she|he)?'?s?\s*not\s+(?:just|only|merely|simply)?"
        r"\s*[^.;:!?]{2,60}[,;—-]+\s*(?:but|it'?s)\b", re.IGNORECASE)),
    ("isnt-just", re.compile(r"\bisn'?t\s+just\b", re.IGNORECASE)),
    ("no-no-just", re.compile(
        r"\bno\s+\w[\w\s]{0,20},\s*no\s+\w[\w\s]{0,20}[,—-]+\s*(?:just|only)\b",
        re.IGNORECASE)),
    ("not-because", re.compile(
        r"\bnot\s+because\b[^.;:!?]{3,60}\bbut\s+because\b", re.IGNORECASE)),
    ("trailing-participle", re.compile(
        r",\s+(ensuring|showcasing|highlighting|underscoring|emphasizing|"
        r"cementing|solidifying|signaling|reflecting)\s+\w", re.IGNORECASE)),
    ("rule-of-three-adj", re.compile(
        r"\b(\w+ed|\w+ing|\w+ous|\w+ive|\w+al|\w+ful),\s+(\w+ed|\w+ing|\w+ous|"
        r"\w+ive|\w+al|\w+ful),\s+(?:and|or)\s+(\w+ed|\w+ing|\w+ous|\w+ive|"
        r"\w+al|\w+ful)\b", re.IGNORECASE)),
]


# ---------------------------------------------------------------- data layer

def fetch_slop_lists(refresh: bool = False) -> tuple[set[str], set[str], set[str]]:
    """slop-forensics canonical lists (words, bigrams, trigrams), cached."""
    CACHE.mkdir(parents=True, exist_ok=True)
    out: list[set[str]] = []
    for name in ("slop_list", "slop_list_bigrams", "slop_list_trigrams"):
        path = CACHE / f"{name}.json"
        if refresh or not path.exists():
            url = f"{SLOP_REPO_RAW}/{name}.json"
            try:
                with urllib.request.urlopen(url, timeout=30) as r:
                    path.write_bytes(r.read())
                print(f"fetched {url}", file=sys.stderr)
            except OSError as e:
                print(f"slop_audit: WARN could not fetch {url}: {e}",
                      file=sys.stderr)
                out.append(set())
                continue
        try:
            out.append({row[0] for row in json.loads(path.read_text())})
        except (json.JSONDecodeError, IndexError, TypeError):
            out.append(set())
    return out[0], out[1], out[2]


# -------------------------------------------------------------- corpus layer

def light_detex(text: str) -> str:
    text = re.sub(r"(?<!\\)%.*", "", text)
    # published typography — Pangram verdicts flip on --- vs real em dash
    # (REVIEW-QA §2 calibration), so normalize before any scoring
    text = text.replace("---", "\u2014").replace("--", "\u2013")
    text = text.replace("``", "\u201c").replace("''", "\u201d")
    for env in DROP_ENVS:
        text = re.sub(rf"\\begin\{{{env}\*?\}}.*?\\end\{{{env}\*?\}}", " ",
                      text, flags=re.DOTALL)
    text = re.sub(r"\$[^$]*\$", " ", text)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", text)
    text = re.sub(r"[{}~]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


HEADING_RE = re.compile(r"\\(chapter|section|subsection)\*?\{([^}]*)\}")


@dataclass
class Para:
    file: str
    line: int              # 1-based line of the paragraph's first line
    section: str           # nearest enclosing \chapter/\section title
    text: str              # detexed prose
    words: list[str] = field(default_factory=list)
    comp: float = 0.0      # zlib ratio (lower = more repetitive)
    comp_z: float = 0.0
    slop_hits: list[str] = field(default_factory=list)
    gram_hits: list[str] = field(default_factory=list)
    construction_hits: list[tuple[str, str]] = field(default_factory=list)
    score: float = 0.0


def parse_paragraphs(path: Path) -> list[Para]:
    """Blank-line-separated paragraphs with line anchors + section titles."""
    source = path.read_text()
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
            prose = light_detex("\n".join(buf))
            alpha = sum(c.isalpha() or c.isspace() for c in prose)
            # skip title-page kerning soup and other non-prose blocks
            if len(prose.split()) >= 20 and alpha / max(1, len(prose)) > 0.85:
                paras.append(Para(file=path.name, line=start,
                                  section=section, text=prose))
            buf = []
    return paras


def discover(root: Path, chapter: str | None) -> list[Path]:
    files: list[Path] = []
    for name in SUBDIRS:
        d = root / "latex" / name
        if d.exists():
            files += sorted(d.glob("*.tex"))
    if chapter:
        files = [f for f in files if f.name.startswith(chapter)]
    return files


# ------------------------------------------------------------ signal scoring

def analyze_paragraphs(paras: list[Para], slop_words: set[str],
                       slop_grams: set[str]) -> None:
    for p in paras:
        p.words = WORD_RE.findall(p.text.lower())
        raw = p.text.encode()
        p.comp = len(zlib.compress(raw, 9)) / max(1, len(raw))
        p.slop_hits = [w for w in p.words if w in slop_words or w in AI_VOCAB]
        toks = p.words
        grams = {" ".join(g) for n in (2, 3)
                 for g in zip(*(toks[i:] for i in range(n)), strict=False)}
        p.gram_hits = sorted(grams & slop_grams)
        for name, rx in CONSTRUCTIONS:
            for m in rx.finditer(p.text):
                p.construction_hits.append((name, m.group(0)[:80]))

    comps = [p.comp for p in paras if len(p.words) >= 40]
    mu = statistics.mean(comps) if comps else 0.0
    sd = statistics.stdev(comps) if len(comps) > 1 else 1.0
    for p in paras:
        p.comp_z = (p.comp - mu) / sd if sd else 0.0
        slop_density = 100 * len(p.slop_hits) / max(1, len(p.words))
        # weighted composite: constructions strongest, then vocabulary,
        # then repetitiveness (negative comp z)
        p.score = (2.0 * len(p.construction_hits)
                   + 1.0 * slop_density
                   + 1.0 * len(p.gram_hits)
                   + max(0.0, -p.comp_z))


def group_stats(paras: list[Para], sentences: int) -> dict:
    words = sum(len(p.words) for p in paras)
    slop = sum(len(p.slop_hits) for p in paras)
    cons = sum(len(p.construction_hits) for p in paras)
    text = " ".join(p.text for p in paras)
    comp = (len(zlib.compress(text.encode(), 9)) / max(1, len(text.encode()))
            if text else 0.0)
    return {
        "paras": len(paras), "words": words,
        "slop_per_1k": round(1000 * slop / words, 2) if words else 0.0,
        "constructions_per_100_sents": (
            round(100 * cons / sentences, 2) if sentences else 0.0),
        "comp": round(comp, 3),
    }


# ------------------------------------------------------------ judge units

@dataclass
class Unit:
    kind: str        # paragraph | sentence | line | section | file
    file: str
    line: int
    section: str
    text: str
    quant: float = 0.0


def build_units(kind: str, paras: list[Para], files: list[Path],
                max_chars: int) -> list[Unit]:
    if kind == "paragraph":
        return [Unit("paragraph", p.file, p.line, p.section, p.text, p.score)
                for p in paras]

    if kind == "sentence":
        from nupunkt import PunktSentenceTokenizer
        tok = PunktSentenceTokenizer()
        units = []
        for p in paras:
            for s in tok.tokenize(p.text):
                if len(s.split()) >= 5:
                    units.append(Unit("sentence", p.file, p.line,
                                      p.section, s, p.score))
        return units

    if kind == "line":
        units = []
        for f in files:
            for i, raw in enumerate(f.read_text().splitlines(), 1):
                if raw.lstrip().startswith(("%", "\\")):
                    continue
                prose = light_detex(raw)
                alpha = sum(c.isalpha() or c.isspace() for c in prose)
                if len(prose.split()) >= 6 and alpha / max(1, len(prose)) > 0.85:
                    units.append(Unit("line", f.name, i, "", prose))
        return units

    # section / file: concatenate paragraphs, cap text length
    groups: dict[tuple, list[Para]] = {}
    for p in paras:
        key = (p.file,) if kind == "file" else (p.file, p.section)
        groups.setdefault(key, []).append(p)
    units = []
    for _key, ps in groups.items():
        text = "\n\n".join(p.text for p in ps)
        if len(text) > max_chars:
            text = text[:max_chars] + " …[truncated]"
        units.append(Unit(kind, ps[0].file, ps[0].line,
                          ps[0].section if kind == "section" else "",
                          text, max(p.score for p in ps)))
    return units


def sample_units(units: list[Unit], *, sample: str, n: int | None,
                 pct: float | None, limit: int,
                 rng: random.Random) -> list[Unit]:
    pool = list(units)
    if sample == "worst":
        pool.sort(key=lambda u: u.quant, reverse=True)
    elif sample == "random":
        rng.shuffle(pool)
    # size selection: --pct beats --n; --sample all takes everything
    if pct is not None:
        size = max(1, math.ceil(len(pool) * pct / 100))
    elif n is not None:
        size = n
    elif sample == "all":
        size = len(pool)
    else:
        size = 10
    pool = pool[:size]
    if limit > 0:
        pool = pool[:limit]
    return pool


# -------------------------------------------------------------- LLM judge

def resolve_tells(only: str | None,
                  skip: str | None) -> dict[str, tuple[str, str]]:
    def expand(spec: str) -> set[str]:
        ids: set[str] = set()
        for tok in spec.split(","):
            tok = tok.strip().lower()
            if not tok:
                continue
            if tok in GROUPS:
                ids |= {t for t, (g, _) in TAXONOMY.items() if g == tok}
            elif tok in TAXONOMY:
                ids.add(tok)
            else:
                raise SystemExit(f"slop_audit: unknown tell or group {tok!r} "
                                 "(see --list-tells)")
        return ids

    enabled = set(TAXONOMY)
    if only:
        enabled = expand(only)
    if skip:
        enabled -= expand(skip)
    if not enabled:
        raise SystemExit("slop_audit: no tells enabled")
    return {t: TAXONOMY[t] for t in TAXONOMY if t in enabled}


def judge_instructions(tells: dict[str, tuple[str, str]]) -> str:
    lines = [f"  {tid} — {desc}" for tid, (_, desc) in tells.items()]
    return f"""\
You audit prose from a book manuscript for "AI slop" — the statistical
fingerprints of unedited LLM writing. Judge only style, never the subject
matter or the claims. The unit may be a single sentence or line (judge only
what is judgeable at that size), a paragraph, or a whole section/file
(also judge cross-passage patterns like uniform rhythm or section symmetry).

Check ONLY for these tells, and use EXACTLY these ids as labels:

{chr(10).join(lines)}

Return:
- slop_score: 0 (clean, specific, human) to 10 (unmistakable machine filler).
  Concrete specifics, varied rhythm, no tells -> 0-2. Reserve 7+ for text an
  editor would rewrite from scratch.
- findings: one entry per tell actually present, each with the tell id and a
  short VERBATIM quote from the text as evidence. No entry for absent tells.
- rewrite: only when slop_score >= 5, one or two sentences showing the fix,
  preserving all facts. Otherwise null."""


def build_judge(model: str, tells: dict[str, tuple[str, str]]):
    from pydantic import BaseModel, Field
    from pydantic_ai import Agent

    class Finding(BaseModel):
        tell: str = Field(description="tell id from the provided list")
        quote: str = Field(description="short verbatim evidence quote")

    class Verdict(BaseModel):
        slop_score: int = Field(ge=0, le=10)
        findings: list[Finding] = Field(default_factory=list)
        rewrite: str | None = None

    return Agent(model, output_type=Verdict,
                 instructions=judge_instructions(tells))


def run_judge(units: list[Unit], model: str, fmt: str,
              tells: dict[str, tuple[str, str]]) -> None:
    agent = build_judge(model, tells)
    print(f"judging {len(units)} {units[0].kind if units else ''} unit(s) "
          f"with {model}, {len(tells)} tells enabled, one at a time…",
          file=sys.stderr)
    tally: dict[str, list[tuple[str, int, str]]] = {}
    scored = 0
    scores: list[int] = []
    for i, u in enumerate(units, 1):
        try:
            result = agent.run_sync(u.text[:8000])
        except Exception as e:  # auth, rate limit, refusal — keep going
            print(f"  [{i}/{len(units)}] {u.file}:{u.line} ERROR {e}",
                  file=sys.stderr)
            continue
        v = result.output
        findings = [f for f in v.findings if f.tell in tells]
        dropped = [f.tell for f in v.findings if f.tell not in tells]
        if dropped:
            print(f"  [{i}/{len(units)}] dropped unlisted tells: {dropped}",
                  file=sys.stderr)
        scored += 1
        scores.append(v.slop_score)
        for f in findings:
            tally.setdefault(f.tell, []).append((u.file, u.line, f.quote))
        loc = f"{u.file}:{u.line}"
        if fmt == "jsonl":
            print(json.dumps({
                "unit": u.kind, "file": u.file, "line": u.line,
                "section": u.section, "quant_score": round(u.quant, 2),
                "llm_score": v.slop_score,
                "findings": [{"tell": f.tell, "quote": f.quote}
                             for f in findings],
                "rewrite": v.rewrite, "model": model,
            }))
        else:
            flag = "!" * min(3, v.slop_score // 3)
            head = f"── {loc}"
            if u.section:
                head += f" [{u.section}]"
            print(f"{head}  llm={v.slop_score}/10 {flag}")
            for f in findings:
                print(f"   {f.tell}: “{f.quote[:90]}”")
            if v.rewrite:
                print(f"   rewrite: {v.rewrite}")
            print(f"   > {u.text[:160]}{'…' if len(u.text) > 160 else ''}")
            print()

    if fmt != "jsonl" and scored:
        print("=" * 60)
        print(f"aggregate: {scored} unit(s) judged by {model}; "
              f"mean slop {statistics.mean(scores):.1f}/10")
        for tell, hits in sorted(tally.items(), key=lambda kv: -len(kv[1])):
            locs = ", ".join(f"{f}:{ln}" for f, ln, _ in hits[:4])
            more = f" +{len(hits) - 4} more" if len(hits) > 4 else ""
            print(f"  {tell:22s} {len(hits):3d}x  ({locs}{more})")
        clean = [t for t in tells if t not in tally]
        if clean:
            print(f"  clean ({len(clean)}): {', '.join(sorted(clean)[:12])}"
                  + (" …" if len(clean) > 12 else ""))
    print(f"slop_audit: {scored}/{len(units)} unit(s) judged by {model}",
          file=sys.stderr)


# ------------------------------------------------------------------ reports

def report_paragraphs(paras: list[Para], top: int, fmt: str) -> None:
    ranked = sorted(paras, key=lambda p: p.score, reverse=True)[:top]
    for p in ranked:
        if p.score <= 0:
            continue
        if fmt == "jsonl":
            print(json.dumps({
                "file": p.file, "line": p.line, "section": p.section,
                "score": round(p.score, 2), "comp": round(p.comp, 3),
                "comp_z": round(p.comp_z, 2),
                "slop_words": sorted(set(p.slop_hits)),
                "slop_grams": p.gram_hits,
                "constructions": [n for n, _ in p.construction_hits],
            }))
        else:
            bits = []
            if p.construction_hits:
                bits.append("constructions: " + ", ".join(
                    f"{n} (“{s}”)" for n, s in p.construction_hits[:3]))
            if p.slop_hits:
                bits.append("slop words: "
                            + ", ".join(sorted(set(p.slop_hits))[:8]))
            if p.gram_hits:
                bits.append("slop n-grams: " + ", ".join(p.gram_hits[:4]))
            if p.comp_z < -2:
                bits.append(f"repetitive (comp {p.comp:.3f}, z={p.comp_z:.1f})")
            print(f"{p.file}:{p.line}  score={p.score:.1f}  [{p.section}]")
            for b in bits:
                print(f"   {b}")
            print(f"   ¶ {p.text[:160]}{'…' if len(p.text) > 160 else ''}")
            print()


def report_sentences(paras: list[Para], fmt: str) -> None:
    n = 0
    for p in paras:
        for name, snippet in p.construction_hits:
            n += 1
            if fmt == "jsonl":
                print(json.dumps({"file": p.file, "line": p.line,
                                  "construction": name, "match": snippet}))
            else:
                print(f"{p.file}:{p.line}  {name}:  “{snippet}”")
    if fmt != "jsonl":
        print(f"\n{n} construction match(es)")


def report_groups(paras: list[Para], sent_counts: dict[str, int],
                  by: str, fmt: str) -> None:
    groups: dict[str, list[Para]] = {}
    for p in paras:
        key = p.file if by == "file" else f"{p.file} § {p.section}"
        groups.setdefault(key, []).append(p)
    rows = []
    for key, ps in groups.items():
        sents = sent_counts.get(ps[0].file, 0) if by == "file" else max(
            1, round(sent_counts.get(ps[0].file, 0) * len(ps)
                     / max(1, len([q for q in paras if q.file == ps[0].file]))))
        rows.append((key, group_stats(ps, sents)))
    if fmt == "jsonl":
        for key, s in rows:
            print(json.dumps({by: key, **s}))
        return
    hdr = (f"{'unit':44s} {'paras':>5s} {'words':>7s} {'slop/1k':>8s} "
           f"{'cons/100s':>9s} {'comp':>6s}")
    print(hdr)
    print("-" * len(hdr))
    for key, s in sorted(rows, key=lambda r: -r[1]["slop_per_1k"]):
        print(f"{key[:44]:44s} {s['paras']:5d} {s['words']:7d} "
              f"{s['slop_per_1k']:8.2f} {s['constructions_per_100_sents']:9.2f} "
              f"{s['comp']:6.3f}")


# ---------------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list-tells", action="store_true",
                    help="print the tell taxonomy and exit")
    ap.add_argument("--level", choices=("summary", "file", "section",
                                        "paragraph", "sentence"),
                    default="summary",
                    help="quantitative report granularity")
    ap.add_argument("--top", type=int, default=15,
                    help="paragraphs shown at --level paragraph (default 15)")
    ap.add_argument("--llm", action="store_true",
                    help="run the taxonomy LLM judge on sampled units")
    ap.add_argument("--model", default="anthropic:claude-sonnet-5",
                    help="pydantic-ai model: anthropic:claude-sonnet-5, "
                         "anthropic:claude-fable-5, openai:gpt-5.6-terra, …")
    ap.add_argument("--unit", choices=("paragraph", "sentence", "line",
                                       "section", "file"),
                    default="paragraph", help="unit the judge sees")
    ap.add_argument("--sample", choices=("worst", "random", "all"),
                    default=None,
                    help="worst = quantitatively-flagged first (default); "
                         "random (default when --n/--pct given); "
                         "all = document order")
    ap.add_argument("--n", type=int, default=None,
                    help="number of units to judge (e.g. --sample random --n 3)")
    ap.add_argument("--pct", type=float, default=None,
                    help="percent of units to judge (e.g. --unit sentence "
                         "--pct 2)")
    ap.add_argument("--limit", type=int, default=50,
                    help="hard cap on judged units (default 50; 0 = uncapped, "
                         "for whole-book runs)")
    ap.add_argument("--tells", default=None,
                    help="comma list of tell ids and/or groups to enable "
                         f"(groups: {', '.join(GROUPS)})")
    ap.add_argument("--skip-tells", default=None,
                    help="comma list of tell ids and/or groups to disable")
    ap.add_argument("--max-chars", type=int, default=12000,
                    help="truncation for section/file units (default 12000)")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--chapter", help="restrict to files starting with this")
    ap.add_argument("--root", type=Path,
                    default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--format", choices=("pretty", "jsonl"), default="pretty")
    ap.add_argument("--refresh", action="store_true",
                    help="re-fetch the slop-forensics lists")
    args = ap.parse_args()

    if args.list_tells:
        for group in GROUPS:
            print(f"{group}:")
            for tid, (g, desc) in TAXONOMY.items():
                if g == group:
                    print(f"  {tid:22s} {desc}")
        print(f"\n{len(TAXONOMY)} tells; enable/disable by id or group with "
              "--tells / --skip-tells")
        return

    rng = random.Random(args.seed)
    files = discover(args.root, args.chapter)
    if not files:
        raise SystemExit(f"slop_audit: no .tex files under {args.root}/latex/")

    slop_words, slop_bi, slop_tri = fetch_slop_lists(args.refresh)
    slop_grams = slop_bi | slop_tri

    paras: list[Para] = []
    for f in files:
        paras += parse_paragraphs(f)
    if not paras:
        raise SystemExit("slop_audit: no prose paragraphs found")
    analyze_paragraphs(paras, slop_words, slop_grams)

    from nupunkt import PunktSentenceTokenizer
    tok = PunktSentenceTokenizer()
    sent_counts = {}
    for f in files:
        text = " ".join(p.text for p in paras if p.file == f.name)
        sent_counts[f.name] = len(tok.tokenize(text)) if text else 0

    print(f"corpus: {len(files)} files, {len(paras)} paragraphs, "
          f"{sum(len(p.words) for p in paras):,} words | slop lists: "
          f"{len(slop_words)} words, {len(slop_grams)} n-grams",
          file=sys.stderr)

    if args.llm:
        tells = resolve_tells(args.tells, args.skip_tells)
        units = build_units(args.unit, paras, files, args.max_chars)
        if args.sample is None:
            # --n / --pct read as "a sample of the book" -> random;
            # otherwise triage mode -> quantitatively-worst first
            args.sample = "random" if (args.n or args.pct) else "worst"
        if args.sample == "worst" and args.unit == "line":
            print("slop_audit: note: no quant ranking for line units; "
                  "using random", file=sys.stderr)
            args.sample = "random"
        picked = sample_units(units, sample=args.sample, n=args.n,
                              pct=args.pct, limit=args.limit, rng=rng)
        if not picked:
            raise SystemExit("slop_audit: no units selected")
        run_judge(picked, args.model, args.format, tells)
        return

    if args.level == "paragraph":
        report_paragraphs(paras, args.top, args.format)
    elif args.level == "sentence":
        report_sentences(paras, args.format)
    elif args.level in ("file", "section"):
        report_groups(paras, sent_counts, args.level, args.format)
    else:  # summary
        total_words = sum(len(p.words) for p in paras)
        total_slop = sum(len(p.slop_hits) for p in paras)
        total_cons = sum(len(p.construction_hits) for p in paras)
        total_sents = sum(sent_counts.values())
        flagged = [p for p in paras if p.score >= 3]
        print(f"book: {total_words:,} words, {total_sents:,} sentences")
        print(f"slop vocabulary: {total_slop} hits "
              f"({1000 * total_slop / total_words:.2f}/1k words)")
        print(f"constructions:   {total_cons} "
              f"({100 * total_cons / max(1, total_sents):.2f}/100 sentences; "
              f"human baseline for not-x-but-y is ~0.2)")
        print(f"paragraphs scoring >= 3: {len(flagged)} of {len(paras)}")
        print()
        report_paragraphs(paras, min(args.top, 8), args.format)
        print("drill down: --level paragraph|sentence|section|file; "
              "--llm --unit … --sample … for the judge; --list-tells")


if __name__ == "__main__":
    main()
