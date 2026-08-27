#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "nupunkt>=0.6.0",
#     "pydantic>=2.7",
#     "pydantic-ai-slim[openai,anthropic]>=1.0",
# ]
# ///
"""Critical-question red team: fire argumentation schemes at your own claims.

Finds the draft's load-bearing assertions and, for each one, asks the
questions a trained opponent would ask. The questions are not invented here:
they are the *critical questions* attached to Walton-style argumentation
schemes in the ontology's argumentation_schemes branch, matched to each
claim by the kind of inference the claim is making.

  claim extraction  declaratives with assertion shape — causal verbs
                    ("causes", "leads to", "explains"), quantifiers ("all",
                    "never", "most"), evaluatives ("must", "essential",
                    "best"), source appeals ("studies show"), comparisons,
                    plain copular assertions. Hedges subtract; announcements
                    ("in this chapter we…") are not claims.
  scheme matching   causal claims draw causal schemes, "studies show" draws
                    source/expert schemes, comparisons draw analogy schemes,
                    quantified claims draw generalization schemes, and so on
                    — matched dynamically against each scheme's own name and
                    definition, never against hardcoded category names.
  instantiation     the scheme's variables (A, E, B…) are filled with the
                    claim's own subject and predicate, shown in [brackets]
                    so you can see what was substituted.

With no argumentation_schemes branch present, a built-in set of ten generic
critical questions is used instead, so the tool always runs.

--llm sharpens both halves: the model picks the genuinely load-bearing
claims out of the candidate pool and rewrites each critical question as a
concrete objection to *this* claim. Provider comes from ANTHROPIC_API_KEY or
OPENAI_API_KEY (slop_audit.py's pattern); --model forces one. Without a key
the script prints a note and runs fully heuristic.

Usage:
    uv run scripts/objection_engine.py                    # top 10 claims
    uv run scripts/objection_engine.py --chapter ch02 -n 5
    uv run scripts/objection_engine.py --text draft.txt --schemes 4
    uv run scripts/objection_engine.py --json --seed 7
    uv run scripts/objection_engine.py --llm -n 3

Advisory: always exits 0. Answer the questions in the draft, not here.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import writing_ontology as wo
except ImportError:  # standalone copy of the script
    wo = None

SCHEME_BRANCH = "argumentation_schemes"

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
class Block:
    file: str
    line: int
    section: str
    text: str
    raw: str


def parse_paragraphs(path: Path, detex: bool, min_words: int) -> list[Block]:
    source = path.read_text(encoding="utf-8")
    out: list[Block] = []
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
                out.append(Block(path.name, start, section, prose, raw))
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


# --------------------------------------------------------- claim extraction

FEATURE_PATTERNS: dict[str, tuple[float, re.Pattern]] = {
    "causal": (2.5, re.compile(
        r"\b(?:causes?|caused|causing|leads? to|led to|results? in|drives?|"
        r"produces?|produced|explains?|determines?|makes? it|because|"
        r"therefore|thus|hence|which is why|so that|means that|forces?)\b",
        re.I)),
    "generalization": (2.0, re.compile(
        r"\b(?:all|every|always|never|none|no one|nobody|most|majority|"
        r"invariably|universally|any|each|inevitably|everyone|everything)\b",
        re.I)),
    "normative": (2.0, re.compile(
        r"\b(?:must|should|ought|essential|necessary|critical|crucial|vital|"
        r"impossible|best|worst|better|superior|inferior|wrong|right|only way|"
        r"dangerous|indispensable|required)\b", re.I)),
    "source": (1.5, re.compile(
        r"\b(?:according to|studies? (?:show|find|suggest)|research (?:shows?|"
        r"finds?)|surveys?|the data|experts?|scholars?|reports?|argues?|"
        r"evidence (?:shows?|suggests?)|found that)\b", re.I)),
    "analogy": (1.0, re.compile(
        r"\b(?:just as|unlike|similar to|analogous|compared (?:to|with)|"
        r"the equivalent of|much like|in the same way|is like|are like)\b",
        re.I)),
    "statistical": (0.75, re.compile(r"\b\d[\d,.]*\s*(?:%|percent|per cent)?")),
    "assertion": (1.0, re.compile(
        r"\b(?:is|are|was|were|remains?|becomes?|means?)\b", re.I)),
    "booster": (1.0, re.compile(
        r"\b(?:clearly|obviously|undeniably|of course|certainly|plainly|"
        r"no doubt|in fact|the truth is|simply)\b", re.I)),
}
HEDGE_RE = re.compile(
    r"\b(?:may|might|perhaps|possibly|arguably|seems?|appears?|tends? to|"
    r"roughly|often|sometimes|can be|suggests?)\b", re.I)
META_RE = re.compile(
    r"\b(?:this (?:chapter|section|book)|in what follows|we will see|"
    r"the rest of this|figure|table|appendix|see chapter)\b", re.I)
COPULA_SPLIT_RE = re.compile(
    r"\b(?:is|are|was|were|remains|becomes|means|causes|leads to|results in|"
    r"produces|explains|drives|must|should|will)\b", re.I)
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*")


@dataclass
class Claim:
    text: str
    file: str
    line: int
    section: str
    strength: float
    features: list[str]
    paraphrase: str = ""
    source: str = "heuristic"
    objections: list[dict] = field(default_factory=list)

    @property
    def loc(self) -> str:
        return f"{self.file}:{self.line}"


CORE_FEATURES = ("causal", "generalization", "normative", "source", "analogy")


def score_sentence(s: str) -> tuple[float, list[str]]:
    score, feats = 0.0, []
    for name, (weight, rx) in FEATURE_PATTERNS.items():
        if name == "assertion":
            continue
        if rx.search(s):
            score += weight
            feats.append(name)
    # a plain copular assertion only counts when nothing sharper is present,
    # so "is/are" does not drag definition schemes onto every causal claim
    if not any(f in CORE_FEATURES for f in feats):
        weight, rx = FEATURE_PATTERNS["assertion"]
        if rx.search(s):
            score += weight
            feats.append("assertion")
    if HEDGE_RE.search(s):
        score -= 1.0
        feats.append("hedged")
    if META_RE.search(s):
        score -= 2.5
        feats.append("meta")
    n = len(s.split())
    if n < 8:
        score -= 1.0
    if n > 45:
        score -= 0.5
    return score, feats


def extract_claims(blocks: list[Block], tok, min_words: int) -> list[Claim]:
    claims: list[Claim] = []
    for b in blocks:
        for s in tok.tokenize(b.text):
            s = s.strip()
            if len(s.split()) < min_words or s.endswith("?") or s.endswith(":"):
                continue
            score, feats = score_sentence(s)
            if score <= 0:
                continue
            claims.append(Claim(s, b.file, b.line, b.section,
                                round(score, 2), feats))
    claims.sort(key=lambda c: (-c.strength, c.file, c.line))
    return claims


BECAUSE_RE = re.compile(r"\b(?:because|since|as a result of|thanks to)\b", re.I)
SO_RE = re.compile(
    r"\b(?:therefore|thus|hence|which is why|as a result|so that|and so)\b", re.I)
CAUSE_VERB_RE = re.compile(
    r"\b(?:causes?|caused|leads? to|led to|results? in|produces?|drives?|"
    r"explains?|determines?|forces?)\b", re.I)


def split_claim(s: str) -> tuple[str, str]:
    """(antecedent, consequent) for a causal claim, (subject, predicate)
    otherwise. Crude by design — it only has to read sensibly in brackets."""
    m = BECAUSE_RE.search(s)
    if m:  # "B because A" — the reason follows the connective
        return (s[m.end():].strip(" ,;\u2014"), s[:m.start()].strip(" ,;\u2014"))
    for rx in (SO_RE, CAUSE_VERB_RE):
        m = rx.search(s)
        if m:
            return (s[:m.start()].strip(" ,;\u2014"),
                    s[m.end():].strip(" ,;\u2014"))
    m = COPULA_SPLIT_RE.search(s)
    if not m:
        words = s.split()
        half = max(2, len(words) // 2)
        return " ".join(words[:half]), " ".join(words[half:])
    return s[:m.start()].strip(" ,;\u2014"), s[m.end():].strip(" ,;\u2014")


def shorten(text: str, n: int = 60) -> str:
    text = re.sub(r"\s+", " ", text).strip(" .,;:\u2014")
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0] + "\u2026"


# ------------------------------------------------------------------ schemes

GENERIC_QUESTIONS = [
    "What evidence supports this, and how strong is it on its own?",
    "What would have to be true for this to be false — and has that been ruled out?",
    "Who disagrees, and what is the strongest version of their case?",
    "Is the causal direction established, or only the co-occurrence?",
    "What is the source, and is that source in a position to know?",
    "How representative is the case being generalized from?",
    "Which words here are doing hidden work, and what happens under a stricter definition?",
    "What are the exceptions, and where exactly does the claim stop holding?",
    "What alternative explanation fits the same facts equally well?",
    "If this claim is wrong, what does it cost the reader who believed it?",
]

# Which words in a scheme's own name/definition mark it as belonging to a
# claim feature. Matched against the branch's data, not its category names.
FEATURE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "causal": ("cause", "causal", "effect", "consequence", "correlation",
               "sign", "explanation", "abduct"),
    "source": ("expert", "testimony", "witness", "source", "authority",
               "position to know", "evidence", "report"),
    "analogy": ("analog", "similar", "precedent", "classification",
                "example", "case", "comparison", "metaphor"),
    "generalization": ("generaliz", "sample", "population", "statistic",
                       "instance", "typical", "commitment"),
    "normative": ("practical", "value", "action", "goal", "means", "policy",
                  "ought", "consequence", "danger", "sunk"),
    "statistical": ("statistic", "sample", "correlation", "number", "data"),
    "assertion": ("burden", "presumption", "ignorance", "definition",
                  "classification", "position", "commitment"),
}


@dataclass
class Scheme:
    name: str
    definition: str
    questions: list[str]
    category: str = ""


def load_schemes(verbose: bool) -> tuple[list[Scheme], str]:
    """Every record in argumentation_schemes that carries critical questions."""
    if wo is None:
        return [], "writing_ontology unavailable"
    try:
        branch = wo.load_branch(SCHEME_BRANCH)
    except (OSError, ValueError) as e:
        if verbose:
            print(f"objection_engine: no {SCHEME_BRANCH} branch ({e}); "
                  "using the built-in generic critical questions",
                  file=sys.stderr)
        return [], f"no {SCHEME_BRANCH} branch"
    out: list[Scheme] = []
    for cat, entries in (branch.get("categories") or {}).items():
        for e in entries:
            if not isinstance(e, dict):
                continue
            qs = [q for q in (e.get("critical_questions") or [])
                  if isinstance(q, str) and q.strip()]
            if not qs:
                continue
            out.append(Scheme(str(e.get("name", "")).strip(),
                              str(e.get("definition", "")).strip(), qs, cat))
    if verbose:
        print(f"objection_engine: {len(out)} scheme(s) with critical questions "
              f"from {SCHEME_BRANCH}", file=sys.stderr)
    return out, SCHEME_BRANCH


def match_schemes(claim: Claim, schemes: list[Scheme], k: int,
                  rng: random.Random) -> list[Scheme]:
    scored: list[tuple[float, int, Scheme]] = []
    for i, sc in enumerate(schemes):
        name = sc.name.lower()
        body = f"{name} {sc.definition.lower()}"
        score = 0.0
        for feat in claim.features:
            for kw in FEATURE_KEYWORDS.get(feat, ()):
                if kw in name:
                    score += 2.0
                elif kw in body:
                    score += 1.0
        if score:
            scored.append((score, i, sc))
    scored.sort(key=lambda t: (-t[0], t[1]))
    picked = [sc for _s, _i, sc in scored[:k]]
    if len(picked) < k and schemes:  # top up so every claim gets a red team
        rest = [sc for sc in schemes if sc not in picked]
        picked += rng.sample(rest, min(k - len(picked), len(rest)))
    return picked


VAR_RE = re.compile(r"(?<![A-Za-z0-9])([A-Z])(?![A-Za-z0-9])")


def instantiate(question: str, claim: Claim) -> str:
    """Fill a scheme's variables with this claim's own words."""
    subject, predicate = split_claim(claim.text)
    head = shorten(subject or claim.text, 44)
    tail = shorten(predicate or claim.text, 44)
    if len(head.split()) < 3:      # a two-word subject explains nothing
        head = shorten(claim.text, 44)
    if len(tail.split()) < 3:
        tail = shorten(claim.text, 44)
    fillers = {
        "A": head, "P": head, "F": head, "W": head, "X": head,
        "B": tail, "C": tail, "Q": tail, "Y": tail,
        "D": "the claim's domain",
        "E": "the source behind the claim",
        "G": "the goal it serves",
        "V": "the value it appeals to",
        "R": "the rule it invokes",
    }

    def repl(m: re.Match) -> str:
        v = m.group(1)
        return f"[{fillers[v]}]" if v in fillers else v

    return VAR_RE.sub(repl, question)


def build_objections(claim: Claim, schemes: list[Scheme], k: int, max_q: int,
                     rng: random.Random) -> None:
    if schemes:
        for sc in match_schemes(claim, schemes, k, rng):
            claim.objections.append({
                "scheme": sc.name,
                "definition": sc.definition,
                "category": sc.category,
                "questions": [instantiate(q, claim) for q in sc.questions[:max_q]],
                "raw_questions": sc.questions[:max_q],
            })
    else:
        qs = GENERIC_QUESTIONS[:max(3, max_q)]
        claim.objections.append({
            "scheme": "generic critical questions",
            "definition": "built-in fallback: no argumentation_schemes branch",
            "category": "",
            "questions": qs,
            "raw_questions": qs,
        })


# ----------------------------------------------------------------- LLM pass

def resolve_model(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic:claude-sonnet-5"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai:gpt-5.6-terra"
    return None


CLAIM_INSTRUCTIONS = """\
You read candidate sentences from a book manuscript and pick the ones that
are load-bearing CLAIMS — assertions the argument would collapse without,
the kind a hostile reviewer would attack. Skip description, scene-setting,
signposting, and definitions that no one would dispute.

Return the picked sentences VERBATIM as they were given (so they can be
located in the manuscript), each with a one-line neutral paraphrase of what
is being asserted. Return at most the requested number, strongest first."""

OBJECTION_INSTRUCTIONS = """\
You are a rigorous but fair critic red-teaming one claim from a book
manuscript. You are given the claim and an argumentation scheme with its
critical questions. Rewrite each critical question as a concrete objection
to THIS claim: name the actual entities, mechanisms, and alternatives at
stake instead of scheme variables. Keep each question to one sentence, keep
it answerable, and never invent facts about the manuscript. Attack the
argument, never the author."""


def llm_pick_claims(candidates: list[Claim], model: str, n: int) -> list[Claim]:
    from pydantic import BaseModel, Field
    from pydantic_ai import Agent

    class Picked(BaseModel):
        sentence: str = Field(description="the candidate sentence, verbatim")
        paraphrase: str = ""

    class Picks(BaseModel):
        claims: list[Picked] = Field(default_factory=list)

    agent = Agent(model, output_type=Picks, instructions=CLAIM_INSTRUCTIONS)
    pool = candidates[:max(3 * n, 15)]
    numbered = "\n".join(f"{i}. {c.text}" for i, c in enumerate(pool, 1))
    try:
        picks = agent.run_sync(
            f"Pick at most {n} load-bearing claims.\n\n{numbered}").output
    except Exception as e:
        print(f"objection_engine: claim selection failed ({e}); "
              "keeping the heuristic ranking", file=sys.stderr)
        return candidates[:n]
    out: list[Claim] = []
    for p in picks.claims[:n]:
        want = set(WORD_RE.findall(p.sentence.lower()))
        best, best_overlap = None, 0.0
        for c in pool:
            have = set(WORD_RE.findall(c.text.lower()))
            overlap = len(want & have) / max(1, len(want | have))
            if overlap > best_overlap:
                best, best_overlap = c, overlap
        if best is not None and best_overlap >= 0.4 and best not in out:
            best.paraphrase = p.paraphrase
            best.source = model
            out.append(best)
    return out or candidates[:n]


def llm_sharpen(claim: Claim, model: str) -> None:
    from pydantic import BaseModel, Field
    from pydantic_ai import Agent

    class Sharpened(BaseModel):
        questions: list[str] = Field(default_factory=list)

    agent = Agent(model, output_type=Sharpened,
                  instructions=OBJECTION_INSTRUCTIONS)
    for ob in claim.objections:
        qs = "\n".join(f"- {q}" for q in ob["raw_questions"])
        prompt = (f"CLAIM ({claim.loc}): {claim.text}\n\n"
                  f"SCHEME: {ob['scheme']} — {ob['definition']}\n\n"
                  f"CRITICAL QUESTIONS:\n{qs}")
        try:
            out = agent.run_sync(prompt).output
        except Exception as e:
            print(f"  {claim.loc} [{ob['scheme']}] ERROR {e}", file=sys.stderr)
            continue
        if out.questions:
            ob["questions"] = out.questions
            ob["sharpened_by"] = model


# ------------------------------------------------------------------ reports

def report(claims: list[Claim], source: str) -> None:
    for i, c in enumerate(claims, 1):
        feats = ", ".join(c.features) or "assertion"
        print(f"\nCLAIM {i}  {c.loc}  strength {c.strength}  [{feats}]")
        if c.section and c.section != "(front)":
            print(f"  \u00a7 {c.section}")
        print(f"  \u201c{c.text}\u201d")
        if c.paraphrase:
            print(f"  = {c.paraphrase}")
        for ob in c.objections:
            head = f"  scheme: {ob['scheme']}"
            if ob.get("sharpened_by"):
                head += f"  [{ob['sharpened_by']}]"
            print(head)
            if ob["definition"]:
                print(f"    ({shorten(ob['definition'], 96)})")
            for j, q in enumerate(ob["questions"], 1):
                print(f"    {j}. {q}")
    print(f"\nobjection_engine: {len(claims)} claim(s), "
          f"{sum(len(o['questions']) for c in claims for o in c.objections)} "
          f"question(s) from {source}. Answer them in the draft — "
          "an unanswered critical question is where a reviewer will land.")


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path,
                    default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--text", help="red-team one plain-text or .tex file")
    ap.add_argument("--chapter", help="restrict to files starting with this")
    ap.add_argument("-n", type=int, default=10, help="claims to attack (default 10)")
    ap.add_argument("--schemes", type=int, default=3,
                    help="schemes per claim (default 3)")
    ap.add_argument("--max-questions", type=int, default=4,
                    help="critical questions per scheme (default 4)")
    ap.add_argument("--min-words", type=int, default=8,
                    help="shortest sentence treated as a claim (default 8)")
    ap.add_argument("--min-para-words", type=int, default=15)
    ap.add_argument("--seed", type=int, default=None,
                    help="seed for scheme top-up sampling")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--llm", action="store_true",
                    help="model picks the claims and sharpens the questions")
    ap.add_argument("--model", default=None,
                    help="pydantic-ai model (default: from ANTHROPIC_API_KEY / "
                         "OPENAI_API_KEY)")
    args = ap.parse_args()

    if args.text:
        path = Path(args.text)
        blocks = parse_paragraphs(path, path.suffix == ".tex", args.min_para_words)
    else:
        files = discover(args.root, args.chapter)
        if not files:
            raise SystemExit(
                f"objection_engine: no .tex files under {args.root}/latex/")
        blocks = []
        for f in files:
            blocks += parse_paragraphs(f, True, args.min_para_words)
    if not blocks:
        raise SystemExit("objection_engine: no prose paragraphs found")

    from nupunkt import PunktSentenceTokenizer
    tok = PunktSentenceTokenizer()
    candidates = extract_claims(blocks, tok, args.min_words)
    if not candidates:
        raise SystemExit("objection_engine: no claim-shaped sentences found")

    rng = random.Random(args.seed)
    schemes, source = load_schemes(verbose=not args.json)
    if not schemes:
        source = "built-in generic critical questions"

    claims = candidates[:args.n]
    model = None
    if args.llm:
        model = resolve_model(args.model)
        if model is None:
            print("objection_engine: no ANTHROPIC_API_KEY or OPENAI_API_KEY — "
                  "staying heuristic (the objections below are complete "
                  "without it)", file=sys.stderr)
        else:
            try:
                claims = llm_pick_claims(candidates, model, args.n)
            except ImportError as e:
                print(f"objection_engine: pydantic-ai unavailable ({e}); "
                      "staying heuristic", file=sys.stderr)
                model = None

    for c in claims:
        build_objections(c, schemes, args.schemes, args.max_questions, rng)
    if model is not None:
        for c in claims:
            try:
                llm_sharpen(c, model)
            except ImportError:
                break

    if args.json:
        print(json.dumps({
            "source": source,
            "schemes_available": len(schemes),
            "candidates": len(candidates),
            "claims": [{
                "text": c.text, "file": c.file, "line": c.line,
                "section": c.section, "strength": c.strength,
                "features": c.features, "paraphrase": c.paraphrase,
                "selected_by": c.source, "objections": c.objections,
            } for c in claims],
        }, indent=2))
        return

    print(f"corpus: {len(blocks)} paragraph(s), {len(candidates)} claim "
          f"candidate(s); attacking the top {len(claims)}", file=sys.stderr)
    report(claims, source)


if __name__ == "__main__":
    main()
