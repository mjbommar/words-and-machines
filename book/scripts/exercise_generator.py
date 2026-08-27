#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Progymnasmata drills: one topic through the classical exercise ladder.

The progymnasmata are the graded composition exercises of the Greek and
Roman schools (Aelius Theon, Hermogenes, Aphthonius, Nicolaus) — the
sequence that carried a student from retelling a fable to arguing a law.
Each rung reuses the previous rung's skills on harder material, which is
exactly the shape a writer needs when drilling one subject deliberately
rather than "practising writing" in general.

This generator takes your topic, walks the ladder, and pins one or two
micro-level constraints to each rung — a syntactic construction, a
rhetorical figure, a rhythm move — sampled from the ontology's micro
branches so the drill trains sentence machinery, not just invention.
Constraints get harder as the ladder climbs: one on the early rungs,
two once you are arguing rather than retelling.

Micro branches that do not exist yet are named and skipped; the ladder
still emits, with fewer constraints. Advisory: always exits 0.

Usage:
    uv run scripts/exercise_generator.py --topic "the cost of certainty"
    uv run scripts/exercise_generator.py --topic "AI in courts" -n 5 --seed 3
    uv run scripts/exercise_generator.py --topic "expert testimony" --json
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import writing_ontology as wo  # noqa: E402

# micro branches supplying sentence-level constraints; filenames are the
# stable contract (docs/architecture/writing-ontology.md)
MICRO_BRANCHES = (
    "syntactic_constructions", "rhetorical_figures", "sound_and_rhythm",
)

# The classical sequence. `task` is filled with the topic.
LADDER: list[dict] = [
    {
        "name": "fable",
        "aka": "mythos / fabula",
        "words": (150, 250),
        "task": "Invent a short beast fable whose moral bears on {topic}. "
                "Tell it once plainly, then retell it in half the words. "
                "State the moral last, in one sentence, without the word "
                "'lesson'.",
    },
    {
        "name": "narrative",
        "aka": "diegema / narratio",
        "words": (250, 400),
        "task": "Narrate one true or plausible episode of {topic}: who, "
                "what, when, where, why, how. Keep strict chronology, then "
                "write a second version that opens at the crisis.",
    },
    {
        "name": "chreia",
        "aka": "chreia / usus",
        "words": (300, 450),
        "task": "Take a saying or deed by a named person concerning "
                "{topic}. Work the eight heads: praise the speaker, "
                "paraphrase the saying, give the cause, state the "
                "contrary, offer an analogy, an example, a testimony of "
                "the ancients, and a brief exhortation.",
    },
    {
        "name": "maxim",
        "aka": "gnome / sententia",
        "words": (250, 400),
        "task": "Write a general maxim about {topic} in under fifteen "
                "words, then expand it exactly as a chreia — cause, "
                "contrary, analogy, example, testimony, exhortation. The "
                "maxim must survive the expansion unchanged.",
    },
    {
        "name": "refutation",
        "aka": "anaskeue / refutatio",
        "words": (350, 550),
        "task": "Take the most common claim made about {topic} and attack "
                "it on the classical heads: obscure, implausible, "
                "impossible, inconsistent, unfitting, inexpedient. Do not "
                "assert your own view.",
    },
    {
        "name": "confirmation",
        "aka": "kataskeue / confirmatio",
        "words": (350, 550),
        "task": "Now defend the same claim about {topic} on the same "
                "heads: clear, plausible, possible, consistent, fitting, "
                "expedient. Give it the strongest version it has.",
    },
    {
        "name": "commonplace",
        "aka": "koinos topos / locus communis",
        "words": (350, 500),
        "task": "Amplify the general vice or virtue that {topic} exposes "
                "— not one offender, the type. Assume guilt is settled; "
                "the work is intensity, contrast, and consequence.",
    },
    {
        "name": "encomium",
        "aka": "enkomion / laus (with its inverse, psogos)",
        "words": (400, 600),
        "task": "Praise a person, practice, or institution bound up with "
                "{topic}: origin, upbringing, deeds, comparison, epilogue. "
                "Then write the opening paragraph of its invective twin.",
    },
    {
        "name": "comparison",
        "aka": "synkrisis / comparatio",
        "words": (400, 600),
        "task": "Set two cases of {topic} side by side and judge them "
                "point for point on the same heads, in the same order. "
                "Do not let one case get more heads than the other.",
    },
    {
        "name": "speech-in-character",
        "aka": "ethopoeia / prosopopoeia",
        "words": (300, 500),
        "task": "Write what one specific person would say at the worst "
                "moment of {topic} — their diction, their evasions, their "
                "sense of what is obvious. No narration, no gloss.",
    },
    {
        "name": "description",
        "aka": "ekphrasis / descriptio",
        "words": (300, 450),
        "task": "Bring one place, object, or process from {topic} before "
                "the reader's eyes in order — spatial or procedural, "
                "chosen deliberately. No abstraction until the last "
                "sentence.",
    },
    {
        "name": "thesis",
        "aka": "thesis / quaestio infinita",
        "words": (500, 800),
        "task": "Argue the general question behind {topic} — no named "
                "parties, no dates. State the question, divide it, prove "
                "your side, answer the two strongest objections, close.",
    },
    {
        "name": "law-proposal",
        "aka": "nomou eisphora / legis latio",
        "words": (500, 800),
        "task": "Propose or oppose a specific rule governing {topic}. "
                "Argue it as legal, just, expedient, and practicable; "
                "name who bears the cost and what you would accept as "
                "evidence that it failed.",
    },
]


class Ontology:
    """Lazy view over branch files that tolerates missing/broken branches."""

    def __init__(self) -> None:
        self._cache: dict[str, dict | None] = {}
        self.missing: dict[str, str] = {}

    def branch(self, name: str) -> dict | None:
        if name not in self._cache:
            try:
                self._cache[name] = wo.load_branch(name)
            except FileNotFoundError:
                self._cache[name] = None
                self.missing[name] = "no such branch file yet"
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                self._cache[name] = None
                self.missing[name] = f"unreadable ({exc})"
        return self._cache[name]

    def entries(self, name: str) -> list[dict]:
        """Flat (category-tagged) entries; categories discovered at runtime."""
        b = self.branch(name)
        if not b:
            return []
        out = []
        for cat, entries in (b.get("categories") or {}).items():
            if not isinstance(entries, list):
                continue
            for e in entries:
                label = wo.entry_name(e)
                if not label:
                    continue
                out.append({
                    "branch": name,
                    "category": cat,
                    "name": label,
                    "definition": (e.get("definition", "")
                                   if isinstance(e, dict) else ""),
                    "example": (e.get("example", "")
                                if isinstance(e, dict) else ""),
                })
        return out


def constraints_for(index: int, onto: Ontology, branches: tuple[str, ...],
                    rng: random.Random) -> list[dict]:
    """One constraint on the early rungs, two once the ladder turns to argument."""
    stocked = [b for b in branches if onto.entries(b)]
    if not stocked:
        return []
    wanted = 1 if index < 4 else 2
    picks: list[dict] = []
    # rotate the branch order by rung so a ladder drills construction,
    # figure, and rhythm rather than three rhythm moves in a row
    shift = index % len(stocked)
    order = stocked[shift:] + stocked[:shift]
    for branch in order:
        if len(picks) >= wanted:
            break
        pool = [e for e in onto.entries(branch)
                if e["name"] not in {p["name"] for p in picks}]
        if pool:
            picks.append(rng.choice(pool))
    return picks


def build(topic: str, stages: list[dict], onto: Ontology,
          branches: tuple[str, ...], seed: int) -> list[dict]:
    out = []
    for i, stage in enumerate(stages):
        rng = random.Random(f"{seed}:{stage['name']}:{i}")
        lo, hi = stage["words"]
        out.append({
            "step": i + 1,
            "name": stage["name"],
            "aka": stage["aka"],
            "words": [lo, hi],
            "task": stage["task"].format(topic=topic),
            "constraints": constraints_for(i, onto, branches, rng),
        })
    return out


def wrap(text: str, width: int) -> list[str]:
    words, line, out = text.split(), "", []
    for w in words:
        if line and len(line) + 1 + len(w) > width:
            out.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    if line:
        out.append(line)
    return out or [""]


def render(topic: str, exercises: list[dict], seed: int,
           onto: Ontology, total: int) -> str:
    lines = [f"Progymnasmata ladder — topic: {topic!r}",
             f"{len(exercises)} of {total} rungs · seed {seed}", ""]
    for ex in exercises:
        lines.append(f"{ex['step']}. {ex['name'].upper()}  ({ex['aka']})"
                     f"   target {ex['words'][0]}–{ex['words'][1]} words")
        for line in wrap(ex["task"], 70):
            lines.append(f"     {line}")
        if ex["constraints"]:
            lines.append("     constraints:")
            for c in ex["constraints"]:
                defn = f" — {c['definition']}" if c["definition"] else ""
                chunks = wrap(f"{c['name']}{defn}", 64)
                lines.append(f"       · {chunks[0]}")
                for chunk in chunks[1:]:
                    lines.append(f"         {chunk}")
                lines.append(f"         [{c['branch']}.{c['category']}]")
                if c["example"]:
                    for j, line in enumerate(wrap(f"e.g. {c['example']}", 60)):
                        lines.append(f"         {line}" if j == 0
                                     else f"              {line}")
        lines.append("")
    if onto.missing:
        lines.append("branches not available yet "
                     "(constraints thinned, not an error):")
        for name, why in sorted(onto.missing.items()):
            lines.append(f"  {name}: {why}")
        lines.append("")
    lines.append(f"exercise_generator: seed {seed} "
                 f"(rerun with --seed {seed}); advisory only.")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Ladder: " + " → ".join(s["name"] for s in LADDER),
    )
    ap.add_argument("--topic", required=True,
                    help="what every rung of the ladder is about")
    ap.add_argument("-n", type=int, default=len(LADDER),
                    help=f"how many rungs, from the bottom (max {len(LADDER)})")
    ap.add_argument("--seed", type=int, default=None,
                    help="reproducible constraint sampling (printed if omitted)")
    ap.add_argument("--branches", action="append", default=[], metavar="BRANCH",
                    help="branch to draw constraints from (repeatable; "
                         f"default: {', '.join(MICRO_BRANCHES)})")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    topic = args.topic.strip()
    if not topic:
        raise SystemExit("exercise_generator: --topic must not be empty")
    seed = args.seed if args.seed is not None else random.randrange(1, 10**6)
    branches = tuple(args.branches) if args.branches else MICRO_BRANCHES
    stages = LADDER[:max(1, min(args.n, len(LADDER)))]
    onto = Ontology()
    exercises = build(topic, stages, onto, branches, seed)

    if args.json:
        print(json.dumps({
            "topic": topic,
            "seed": seed,
            "ontology_dir": str(wo.ONTOLOGY_DIR),
            "constraint_branches": list(branches),
            "unavailable": onto.missing,
            "ladder": [s["name"] for s in LADDER],
            "exercises": exercises,
        }, indent=2))
        return 0

    if not wo.available_branches():
        print(f"exercise_generator: no ontology branch files in "
              f"{wo.ONTOLOGY_DIR} — emitting the ladder without "
              f"micro constraints.\n")
    print(render(topic, exercises, seed, onto, len(LADDER)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
