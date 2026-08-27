#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pydantic>=2.7",
#     "pydantic-ai-slim[openai,anthropic]>=1.0",
# ]
# ///
"""Dialogue-game red team: a sparring agenda for one thesis.

Assembles a small panel of argumentative personae and has each of them make
one move per round against your thesis — concede, undercut, distinguish,
demand evidence, offer a counterexample — drawn from the ontology's
interaction_moves branch and from the critical questions attached to
argumentation_schemes. The output is a *transcript-agenda*: an ordered list
of challenges to answer, in the draft, in your own words.

This script never edits prose and never argues on your behalf. It produces
the questions; the answers are the writing.

  panel     argumentative roles and audience personae found in the
            character_and_persona branch (skeptic, hostile cross-examiner,
            resistant reader…), one per flavour where possible; falls back
            to a built-in skeptic / domain expert / general reader panel
  moves     argumentative and dialogue-game entries from interaction_moves,
            matched to a challenge template by what the move is called;
            falls back to a built-in ten-move repertoire
  questions critical questions from argumentation_schemes, instantiated
            against the thesis

Everything is seeded: the same --seed gives the same agenda, so a round of
sparring is reproducible and can be diffed between drafts.

--llm has the personae phrase sharper, more specific challenges (same plan,
better wording) using ANTHROPIC_API_KEY or OPENAI_API_KEY — slop_audit.py's
provider pattern, --model to force one. Without a key it prints a note and
generates the agenda from templates.

Usage:
    uv run scripts/sparring_partner.py --thesis "Remote work hollows out apprenticeship."
    uv run scripts/sparring_partner.py --thesis "…" -r 4 --panel 3 --seed 7
    uv run scripts/sparring_partner.py --thesis "…" --text latex/chapters/ch02.tex
    uv run scripts/sparring_partner.py --thesis "…" --json
    uv run scripts/sparring_partner.py --thesis "…" --llm

Advisory: always exits 0.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import writing_ontology as wo
except ImportError:  # standalone copy of the script
    wo = None

PERSONA_BRANCH = "character_and_persona"
MOVE_BRANCH = "interaction_moves"
SCHEME_BRANCH = "argumentation_schemes"

DROP_ENVS = (
    "tikzpicture", "figure", "table", "tabular", "tabularx", "lstlisting",
    "verbatim", "Verbatim", "equation", "align", "alignat", "gather",
    "definitionbox", "tryitbox", "examplebox", "codelisting", "promptcode",
    "outputcode",
)
WORD_RE = re.compile(r"[a-z][a-z'-]*[a-z]")
STOP = {
    "the", "and", "that", "this", "with", "from", "have", "has", "had", "for",
    "but", "not", "are", "was", "were", "you", "your", "our", "its", "they",
    "them", "their", "what", "when", "where", "which", "who", "will", "would",
    "can", "could", "should", "there", "here", "then", "than", "into", "over",
    "under", "about", "after", "before", "because", "been", "being", "does",
    "did", "just", "only", "also", "more", "most", "some", "such", "same",
    "each", "every", "any", "all", "one", "two", "how", "why", "very", "much",
    "many", "still", "even", "own", "way", "ways", "thing", "things", "make",
    "makes", "made", "take", "get", "like", "use", "used", "uses",
}


def light_detex(text: str) -> str:
    text = re.sub(r"(?<!\\)%.*", "", text)
    text = text.replace("---", "\u2014").replace("--", "\u2013")
    for env in DROP_ENVS:
        text = re.sub(rf"\\begin\{{{env}\*?\}}.*?\\end\{{{env}\*?\}}", " ",
                      text, flags=re.DOTALL)
    text = re.sub(r"\$[^$]*\$", " ", text)
    text = re.sub(r"\\(?:label|ref|cref|Cref|[A-Za-z]*cite[A-Za-z]*|input|"
                  r"include)\*?(?:\[[^\]]*\])?\{[^}]*\}", " ", text)
    text = re.sub(r"\\(?:begin|end)\{[^}]*\}(?:\[[^\]]*\])?", " ", text)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", text)
    text = re.sub(r"[{}~]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def shorten(text: str, n: int = 90) -> str:
    text = re.sub(r"\s+", " ", text).strip().rstrip(".")
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0] + "\u2026"


# ------------------------------------------------------------------- panel

FLAVOURS = ("challenger", "expert", "reader")
FLAVOUR_KEYWORDS: dict[str, tuple[str, ...]] = {
    "challenger": ("skeptic", "sceptic", "opponent", "adversar", "devil",
                   "cross-exam", "contrarian", "gadfly", "hostile", "critic",
                   "debunk", "red team", "objector", "prosecut", "polemic",
                   "provocateur", "curmudgeon", "resistant", "inquisit"),
    "expert": ("expert", "specialist", "domain", "scholar", "witness",
               "adjudicator", "referee", "moderator", "insider",
               "investigator", "analyst", "practitioner", "peer",
               "reporter of record", "steelman", "dialectical"),
    "reader": ("reader", "audience", "listener", "browser", "novice",
               "student", "lay ", "generalist", "naive", "newcomer",
               "curious", "busy", "beginner", "apprentice"),
}
BUILTIN_PANEL = [
    ("skeptic", "challenger",
     "refuses to grant anything the draft has not earned"),
    ("domain expert", "expert",
     "knows the field and hears every imprecision"),
    ("general reader", "reader",
     "has no background and will not fake understanding"),
]
# what each flavour reaches for first
FLAVOUR_MOVE_BIAS: dict[str, tuple[str, ...]] = {
    "challenger": ("undercut", "rebut", "counterexample", "deny", "attack",
                   "challenge", "burden", "reductio", "demand"),
    "expert": ("distinguish", "definition", "qualify", "narrow", "relevance",
               "sufficiency", "premise", "evidence", "ground", "precedent"),
    "reader": ("clarification", "question", "why", "explain", "relevance",
               "example", "analog", "broaden", "stipulate"),
}


@dataclass
class Persona:
    name: str
    flavour: str
    note: str = ""
    origin: str = "builtin"

    @property
    def label(self) -> str:
        return self.name[:1].upper() + self.name[1:]


def flavour_of(name: str) -> str | None:
    low = f" {name.lower()} "
    for flavour, kws in FLAVOUR_KEYWORDS.items():
        if any(kw in low for kw in kws):
            return flavour
    return None


def load_personae(n: int, rng: random.Random, verbose: bool) -> list[Persona]:
    pool: dict[str, list[Persona]] = {f: [] for f in FLAVOURS}
    if wo is not None:
        try:
            branch = wo.load_branch(PERSONA_BRANCH)
        except (OSError, ValueError) as e:
            branch = None
            if verbose:
                print(f"sparring_partner: no {PERSONA_BRANCH} branch ({e}); "
                      "using the built-in panel", file=sys.stderr)
        if branch:
            for entries in (branch.get("categories") or {}).values():
                for e in entries:
                    name = wo.entry_name(e)
                    flavour = flavour_of(name)
                    if flavour is None:
                        continue
                    note = e.get("definition", "") if isinstance(e, dict) else ""
                    pool[flavour].append(
                        Persona(name, flavour, note, PERSONA_BRANCH))
    picked: list[Persona] = []
    for flavour in FLAVOURS:
        if len(picked) >= n:
            break
        if pool[flavour]:
            picked.append(rng.choice(sorted(pool[flavour], key=lambda p: p.name)))
        else:
            match = next((b for b in BUILTIN_PANEL if b[1] == flavour), None)
            if match:
                picked.append(Persona(match[0], match[1], match[2]))
    # more seats than flavours: keep drawing from the widest pool
    rest = [p for f in FLAVOURS for p in sorted(pool[f], key=lambda q: q.name)
            if p.name not in {q.name for q in picked}]
    while len(picked) < n and rest:
        picked.append(rest.pop(rng.randrange(len(rest))))
    return picked[:n]


# ------------------------------------------------------------------- moves

MOVE_KEYWORDS = (
    "concede", "rebut", "undercut", "distinguish", "analog", "disanalog",
    "qualify", "retract", "reframe", "deny", "demand", "burden", "steelman",
    "strawman", "counterexample", "reductio", "narrow", "broaden", "stipulate",
    "dispute", "challenge", "question", "attack", "defend", "ground",
    "justify", "explain", "defeater", "premise", "conclusion", "relevance",
    "sufficiency", "clarification", "commit", "resolve", "grant", "bullet",
    "claim", "assert", "propose", "counterpropose", "accept", "reject",
    "license", "why", "evidence", "definition",
)

# Challenge templates. Each one states the family it can actually voice and
# the move names it will answer to, and a move is only allowed to label a
# challenge that executes it: a template asking the writer to restate the
# thesis must not go out labelled "retract", which is a different move
# entirely. Keywords match whole words in the move's name; a move matching
# nothing falls through to GENERIC_TEMPLATE and is labelled GENERIC_FAMILY,
# never with a name the wording does not perform.
TEMPLATES: list[tuple[str, tuple[str, ...], str]] = [
    ("undercut the inference",
     ("undercut", "defeater", "relevance", "sufficiency", "license",
      "warrant", "backing", "non sequitur"),
     "Granting your evidence, what licenses the step from it to \u201c{t}\u201d "
     "rather than to a weaker conclusion?"),
    ("demand evidence",
     ("evidence", "ground", "grounds", "justify", "justification", "defend",
      "support", "proof"),
     "What is the single strongest piece of evidence for \u201c{t}\u201d, and "
     "what finding would overturn it?"),
    ("counterexample",
     ("counterexample", "counter-example", "rebut", "rebuttal", "refute",
      "deny", "reject", "falsify"),
     "Name the clearest case where \u201c{t}\u201d is false. Why does that case "
     "not sink the claim?"),
    ("contest the definition",
     ("definition", "define", "stipulate", "stipulation", "clarification",
      "clarify", "equivocation"),
     "Which words in \u201c{t}\u201d are carrying hidden weight, and does the "
     "claim survive a stricter definition of them?"),
    ("state the boundary",
     ("distinguish", "distinction", "narrow", "qualify", "qualification",
      "broaden", "scope", "except", "exception"),
     "Under what conditions does \u201c{t}\u201d stop holding? State the boundary "
     "out loud instead of leaving it implied."),
    ("test the analogy",
     ("analogy", "analogize", "analogous", "disanalogy", "disanalogize",
      "precedent", "comparison"),
     "The comparison doing the work behind \u201c{t}\u201d \u2014 where does it "
     "break down, and does the argument survive the break?"),
    ("concede and see what is left",
     ("concede", "concession", "grant", "steelman", "bullet", "accept"),
     "State the opposing case at its strongest. After conceding that much, "
     "what is left of \u201c{t}\u201d?"),
    ("who carries the burden",
     ("burden", "presumption", "default"),
     "Who has to prove what here? If \u201c{t}\u201d is the default position, "
     "say why the default is earned rather than assumed."),
    ("push it to absurdity",
     ("reductio", "absurd", "absurdity"),
     "Push \u201c{t}\u201d to its limit: what conclusion follows that you would "
     "refuse, and where exactly do you get off?"),
    ("restate it unmisreadably",
     ("reframe", "restate", "rephrase", "reformulate"),
     "If you had to restate \u201c{t}\u201d so that a hostile reader could not "
     "misread it, what would you give up?"),
    ("withhold assent",
     ("challenge", "doubt", "dispute", "skepticism", "suspend"),
     "Why should a reader believe \u201c{t}\u201d rather than suspend judgment "
     "and wait for better evidence?"),
]
GENERIC_FAMILY = "open challenge"
GENERIC_TEMPLATE = ("Make the \u201c{m}\u201d move against \u201c{t}\u201d: what "
                    "does it expose that the draft has not answered?")

BUILTIN_MOVES: list[tuple[str, str]] = [
    ("demand evidence", "asks for the support behind an asserted claim"),
    ("undercut", "attacks the link between evidence and conclusion"),
    ("offer a counterexample", "produces a case the claim cannot cover"),
    ("distinguish", "separates cases the claim runs together"),
    ("dispute a definition", "contests the terms the claim depends on"),
    ("concede and pivot", "grants the strongest opposing point, then narrows"),
    ("shift the burden of proof", "asks who must prove what, and why"),
    ("reductio ad absurdum", "pushes the claim to an unacceptable conclusion"),
    ("analogize", "tests the comparison the claim rests on"),
    ("challenge relevance", "asks what the support has to do with the claim"),
]


@dataclass
class Move:
    name: str
    definition: str = ""
    origin: str = "builtin"

    def voiced_by(self) -> tuple[str, str]:
        """(family, template) for this move — the generic pair if none fits.

        Whole-word matching, longest keyword wins, so "dispute a definition"
        contests a definition rather than merely withholding assent, and a
        move nothing voices ("counterpropose") gets the generic challenge
        under the generic label instead of borrowing another move's wording.
        """
        words = set(re.findall(r"[a-z]+", self.name.lower()))
        best: tuple[int, str, str] = (0, GENERIC_FAMILY, GENERIC_TEMPLATE)
        for family, keys, tpl in TEMPLATES:
            for k in keys:
                hit = (set(k.split()) <= words if " " in k else k in words)
                if hit and len(k) > best[0]:
                    best = (len(k), family, tpl)
        return best[1], best[2]


def load_moves(verbose: bool) -> list[Move]:
    if wo is not None:
        try:
            branch = wo.load_branch(MOVE_BRANCH)
        except (OSError, ValueError) as e:
            branch = None
            if verbose:
                print(f"sparring_partner: no {MOVE_BRANCH} branch ({e}); "
                      "using the built-in move repertoire", file=sys.stderr)
        if branch:
            cats = {c: e for c, e in (branch.get("categories") or {}).items()
                    if isinstance(e, list)}
            # A sparring panel argues; it does not adjust a pillow. Prefer the
            # branch's argumentative categories, discovered by name, and only
            # fall back to keyword-filtering the whole branch when the
            # ontology offers no such category — otherwise "granting grace"
            # and "narrowed eyes" arrive as dialogue-game moves.
            argumentative = [c for c in cats if any(
                k in c.lower() for k in
                ("argument", "dialogue_game", "dialectic", "debate"))]
            chosen = argumentative or list(cats)
            out: list[Move] = []
            seen: set[str] = set()
            for cat in chosen:
                for e in cats[cat]:
                    name = wo.entry_name(e)
                    low = name.lower()
                    # short names are the moves themselves ("undercut",
                    # "shift the burden of proof"); long ones are descriptions
                    # of behaviour ("answering a question with a question")
                    if low in seen or len(low.split()) > 5:
                        continue
                    if not argumentative and not any(
                            k in low for k in MOVE_KEYWORDS):
                        continue
                    seen.add(low)
                    out.append(Move(
                        name,
                        e.get("definition", "") if isinstance(e, dict) else "",
                        MOVE_BRANCH))
            if out:
                if verbose:
                    print(f"sparring_partner: {len(out)} argumentative move(s) "
                          f"from {MOVE_BRANCH}", file=sys.stderr)
                return sorted(out, key=lambda m: m.name)
    return [Move(n, d) for n, d in BUILTIN_MOVES]


# what shape of thesis draws which schemes — matched against each scheme's
# own name and definition, never against the branch's category names
THESIS_FEATURES: dict[str, tuple[re.Pattern, tuple[str, ...]]] = {
    "causal": (re.compile(
        r"\b(?:causes?|caused|leads? to|results? in|drives?|produces?|"
        r"explains?|because|therefore|hollows?|undermines?|creates?)\b", re.I),
        ("cause", "causal", "effect", "consequence", "correlation", "sign",
         "explanation")),
    "source": (re.compile(
        r"\b(?:according to|studies|research|data|experts?|survey|evidence|"
        r"reports?)\b", re.I),
        ("expert", "testimony", "witness", "source", "authority", "evidence")),
    "analogy": (re.compile(
        r"\b(?:like|just as|similar|analogous|compared|equivalent)\b", re.I),
        ("analog", "similar", "precedent", "classification", "example")),
    "generalization": (re.compile(
        r"\b(?:all|every|always|never|most|none|no one|any)\b", re.I),
        ("generaliz", "sample", "population", "statistic", "instance")),
    "normative": (re.compile(
        r"\b(?:must|should|ought|better|worse|best|worst|essential|"
        r"necessary|wrong|right)\b", re.I),
        ("practical", "value", "action", "goal", "policy", "consequence")),
}


def load_scheme_questions(thesis: str,
                          verbose: bool) -> list[tuple[str, str, str]]:
    """(scheme, definition, critical question) triples, if the branch is
    present — narrowed to the schemes the thesis's own shape invites."""
    if wo is None:
        return []
    try:
        branch = wo.load_branch(SCHEME_BRANCH)
    except (OSError, ValueError):
        if verbose:
            print(f"sparring_partner: no {SCHEME_BRANCH} branch; moves only",
                  file=sys.stderr)
        return []
    out: list[tuple[str, str, str]] = []
    for entries in (branch.get("categories") or {}).values():
        for e in entries:
            if not isinstance(e, dict):
                continue
            name = str(e.get("name", "")).strip()
            definition = str(e.get("definition", "")).strip()
            for q in e.get("critical_questions") or []:
                if isinstance(q, str) and q.strip():
                    out.append((name, definition, q.strip()))
    out.sort()
    keywords: set[str] = set()
    for _feat, (rx, kws) in THESIS_FEATURES.items():
        if rx.search(thesis):
            keywords |= set(kws)
    if keywords:
        narrowed = [t for t in out
                    if any(k in f"{t[0]} {t[1]}".lower() for k in keywords)]
        if narrowed:
            out = narrowed
    if verbose:
        print(f"sparring_partner: {len(out)} critical question(s) from "
              f"{SCHEME_BRANCH} matching the thesis", file=sys.stderr)
    return out


VAR_RE = re.compile(r"(?<![A-Za-z0-9])([A-Z])(?![A-Za-z0-9])")


def instantiate_question(question: str, thesis: str) -> str:
    t = shorten(thesis, 60)
    fillers = {"A": t, "B": "the effect you claim", "C": "the effect you claim",
               "D": "your subject", "E": "the source you lean on",
               "P": t, "Q": "what you conclude from it", "W": "your witness",
               "X": t, "Y": "the effect you claim",
               "G": "the goal you invoke", "V": "the value you appeal to",
               "R": "the rule you invoke"}
    return VAR_RE.sub(lambda m: f"[{fillers[m.group(1)]}]"
                      if m.group(1) in fillers else m.group(1), question)


# ------------------------------------------------------------------ agenda

@dataclass
class Turn:
    round: int
    persona: Persona
    kind: str            # move | critical-question
    move: str            # the label shown: move name, scheme, or family
    definition: str
    challenge: str
    sharpened_by: str = ""
    family: str = ""     # challenge template the wording came from


def pick_move(persona: Persona, moves: list[Move], used: set[str],
              rng: random.Random) -> Move:
    bias = FLAVOUR_MOVE_BIAS.get(persona.flavour, ())
    fresh = [m for m in moves if m.name not in used] or moves
    weights = [3.0 if any(k in m.name.lower() for k in bias) else 1.0
               for m in fresh]
    return rng.choices(fresh, weights=weights, k=1)[0]


def build_agenda(thesis: str, personae: list[Persona], moves: list[Move],
                 questions: list[tuple[str, str, str]], rounds: int,
                 rng: random.Random, context_terms: list[str]) -> list[Turn]:
    turns: list[Turn] = []
    used_moves: set[str] = set()
    used_questions: set[str] = set()
    t = shorten(thesis, 90)
    for r in range(1, rounds + 1):
        for persona in personae:
            # later rounds lean on the schemes' critical questions, once the
            # obvious moves have been spent
            use_q = bool(questions) and rng.random() < (0.20 + 0.10 * r)
            if use_q:
                pool = [q for q in questions if q[2] not in used_questions] \
                    or questions
                scheme, definition, question = rng.choice(pool)
                used_questions.add(question)
                challenge = (f"Read \u201c{t}\u201d as {scheme} \u2014 "
                             + instantiate_question(question, thesis))
                turns.append(Turn(r, persona, "critical-question", scheme,
                                  definition, challenge,
                                  family="critical question"))
                continue
            move = pick_move(persona, moves, used_moves, rng)
            used_moves.add(move.name)
            family, template = move.voiced_by()
            challenge = template.format(t=t, m=move.name)
            if context_terms and rng.random() < 0.3:
                challenge += (" (the draft leans on: "
                              + ", ".join(context_terms[:3]) + ")")
            # only a move the template actually performs gets to name the
            # challenge; anything else is labelled for what the wording does
            label = move.name if family != GENERIC_FAMILY else GENERIC_FAMILY
            turns.append(Turn(r, persona, "move", label,
                              move.definition, challenge, family=family))
    return turns


# ----------------------------------------------------------------- LLM pass

def resolve_model(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic:claude-sonnet-5"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai:gpt-5.6-terra"
    return None


SPARRING_INSTRUCTIONS = """\
You voice one member of a sparring panel red-teaming a book's thesis. You
are given the persona you speak as, the dialogue move you must make, the
thesis, and (sometimes) an excerpt of the draft.

Write ONE challenge: a single question or demand, in that persona's voice,
executing exactly that move against that thesis. Be concrete — name the
mechanism, case, or distinction at issue rather than gesturing at "the
evidence". Never invent facts about the draft, never soften into advice,
never answer your own challenge, and attack the argument, not the author."""


def llm_sharpen(turns: list[Turn], thesis: str, context: str,
                model: str) -> None:
    from pydantic import BaseModel
    from pydantic_ai import Agent

    class Challenge(BaseModel):
        challenge: str

    agent = Agent(model, output_type=Challenge,
                  instructions=SPARRING_INSTRUCTIONS)
    print(f"sparring_partner: sharpening {len(turns)} turn(s) with {model}…",
          file=sys.stderr)
    for i, t in enumerate(turns, 1):
        prompt = (f"PERSONA: {t.persona.label} ({t.persona.flavour})"
                  + (f" — {t.persona.note}" if t.persona.note else "")
                  + f"\nMOVE: {t.move}"
                  + (f" — {t.definition}" if t.definition else "")
                  + f"\nTHESIS: {thesis}\n"
                  + (f"\nDRAFT EXCERPT:\n{context[:3000]}\n" if context else "")
                  + f"\nTemplate version (improve on it): {t.challenge}")
        try:
            out = agent.run_sync(prompt).output
        except Exception as e:  # auth, rate limit, refusal — keep going
            print(f"  [{i}/{len(turns)}] {t.persona.label} ERROR {e}",
                  file=sys.stderr)
            continue
        if out.challenge.strip():
            t.challenge = out.challenge.strip()
            t.sharpened_by = model


# ------------------------------------------------------------------ report

def context_from(path: Path, top: int = 6) -> tuple[str, list[str]]:
    raw = path.read_text(encoding="utf-8")
    text = light_detex(raw) if path.suffix == ".tex" else re.sub(r"\s+", " ", raw)
    freq: dict[str, int] = {}
    for w in WORD_RE.findall(text.lower()):
        if len(w) < 5 or w in STOP:
            continue
        freq[w] = freq.get(w, 0) + 1
    terms = [w for w, _ in sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))]
    return text, terms[:top]


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--thesis", required=True,
                    help="the claim the panel attacks (required)")
    ap.add_argument("--text", help="draft file for context (plain text or .tex)")
    ap.add_argument("-r", "--rounds", type=int, default=3,
                    help="rounds of sparring (default 3)")
    ap.add_argument("--panel", type=int, default=3,
                    help="personae on the panel, 2-3 recommended (default 3)")
    ap.add_argument("--seed", type=int, default=None,
                    help="reproducible agenda")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--llm", action="store_true",
                    help="personae phrase sharper challenges via a model")
    ap.add_argument("--model", default=None,
                    help="pydantic-ai model (default: from ANTHROPIC_API_KEY / "
                         "OPENAI_API_KEY)")
    args = ap.parse_args()

    thesis = args.thesis.strip()
    if not thesis:
        raise SystemExit("sparring_partner: --thesis must not be empty")
    if args.panel < 1 or args.rounds < 1:
        raise SystemExit("sparring_partner: --panel and --rounds must be >= 1")

    rng = random.Random(args.seed)
    verbose = not args.json
    personae = load_personae(args.panel, rng, verbose)
    moves = load_moves(verbose)
    questions = load_scheme_questions(thesis, verbose)

    context, terms = ("", [])
    if args.text:
        context, terms = context_from(Path(args.text))

    turns = build_agenda(thesis, personae, moves, questions, args.rounds,
                         rng, terms)

    if args.llm:
        model = resolve_model(args.model)
        if model is None:
            print("sparring_partner: no ANTHROPIC_API_KEY or OPENAI_API_KEY — "
                  "using template challenges (the agenda below is complete "
                  "without it)", file=sys.stderr)
        else:
            try:
                llm_sharpen(turns, thesis, context, model)
            except ImportError as e:
                print(f"sparring_partner: pydantic-ai unavailable ({e}); "
                      "using template challenges", file=sys.stderr)

    if args.json:
        print(json.dumps({
            "thesis": thesis,
            "seed": args.seed,
            "rounds": args.rounds,
            "panel": [{"name": p.name, "flavour": p.flavour, "note": p.note,
                       "origin": p.origin} for p in personae],
            "sources": {
                "moves": moves[0].origin if moves else "none",
                "move_count": len(moves),
                "critical_questions": len(questions),
            },
            "context_terms": terms,
            "turns": [{"round": t.round, "persona": t.persona.name,
                       "flavour": t.persona.flavour, "kind": t.kind,
                       "move": t.move, "family": t.family,
                       "definition": t.definition,
                       "challenge": t.challenge,
                       "sharpened_by": t.sharpened_by} for t in turns],
        }, indent=2))
        return

    seed_note = f"seed {args.seed}" if args.seed is not None else "unseeded"
    print(f"SPARRING AGENDA \u2014 {args.rounds} round(s), {len(personae)} "
          f"persona(e), {seed_note}")
    print(f"thesis: \u201c{thesis}\u201d")
    print("panel:  " + " \u00b7 ".join(
        f"{p.label} ({p.flavour})" for p in personae))
    print(f"moves:  {len(moves)} from "
          + (moves[0].origin if moves else "none")
          + (f"; {len(questions)} critical questions from {SCHEME_BRANCH}"
             if questions else ""))
    if terms:
        print("draft terms: " + ", ".join(terms))
    for r in range(1, args.rounds + 1):
        print(f"\nRound {r}")
        for t in [t for t in turns if t.round == r]:
            if t.kind != "move":
                tag = f"CQ / {t.move}"
            elif t.family and t.family != t.move:
                tag = f"{t.move} → {t.family}"   # move, and what it voices
            else:
                tag = t.move
            mark = " *" if t.sharpened_by else ""
            print(f"  {t.persona.label} ({tag}){mark}: {t.challenge}")
    print("\nAnswer each line in the draft, not in the margin. A challenge you "
          "cannot answer is either a revision or a claim to drop.")


if __name__ == "__main__":
    main()
