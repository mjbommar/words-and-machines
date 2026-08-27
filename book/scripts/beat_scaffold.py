#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Instantiate an ontology arc or arrangement as an outline scaffold.

Takes a named template — any ontology record that carries `beats`
(argument arrangements, narrative structures) or a `curve` (arc shapes) —
and writes it out as a markdown outline: one section per beat, with its
position as a percentage and as a word budget against your target
length, its purpose, and two or three craft moves sampled from the meso
branches (discourse moves, interaction moves, scene patterns) to reach
for inside that beat.

Templates are discovered at runtime by scanning every branch file for
records with `beats` or `curve` — nothing about the taxonomy is
hardcoded here, so re-cutting the ontology cannot stale this script.
A named record with neither extra still scaffolds: it gets a generated
five-beat spread, marked as such.

Missing branch files are named and skipped (the scaffold still emits,
with fewer or no suggested moves). Advisory: exits 0 unless you name a
template that does not exist.

Usage:
    uv run scripts/beat_scaffold.py --list
    uv run scripts/beat_scaffold.py --template "classical oration" --words 5000
    uv run scripts/beat_scaffold.py --template "man in hole" --words 90000 --seed 3
    uv run scripts/beat_scaffold.py --template SCQA --json > scaffold.json
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import writing_ontology as wo  # noqa: E402

# meso branches that supply per-beat move suggestions; filenames are the
# stable contract (docs/architecture/writing-ontology.md), categories are not
MOVE_BRANCHES = ("discourse_moves", "interaction_moves", "scene_patterns")

# Default move pool tracks the template's home branch: an IRAC issue
# statement should be offered discourse moves, not escape scenes.
MOVE_BRANCHES_BY_SOURCE = {
    "argument_arrangements": ("discourse_moves", "paragraph_shapes",
                              "evidence_types"),
    "narrative_structures": ("scene_patterns", "interaction_moves",
                             "openings_and_closings"),
    "arc_shapes": ("scene_patterns", "discourse_moves",
                   "interaction_moves"),
}

# branches the design doc says carry beats/curves — used only to explain a
# lookup miss while the ontology is still being authored
TEMPLATE_BRANCHES = (
    "argument_arrangements", "narrative_structures", "arc_shapes",
)

DEFAULT_BEATS = [
    ("opening", "Establish the terms and the reason to keep reading."),
    ("development", "Build the case or the situation; raise the cost."),
    ("turn", "Complicate, reverse, or admit what cuts against you."),
    ("consequence", "Play out what the turn forces."),
    ("close", "Land the change; pay what the opening promised."),
]


# --------------------------------------------------------------------------
# fault-tolerant ontology access
# --------------------------------------------------------------------------
class Ontology:
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

    def records(self, name: str):
        """Yield (category, entry) for every record entry in a branch."""
        b = self.branch(name)
        if not b:
            return
        for cat, entries in (b.get("categories") or {}).items():
            if not isinstance(entries, list):
                continue
            for e in entries:
                yield cat, e


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")


# --------------------------------------------------------------------------
# template discovery
# --------------------------------------------------------------------------
def discover(onto: Ontology) -> list[dict]:
    """Every record in every branch, tagged with the scaffold source."""
    found: list[dict] = []
    for branch in wo.available_branches():
        for cat, entry in onto.records(branch):
            if not isinstance(entry, dict) or not entry.get("name"):
                continue
            beats = entry.get("beats")
            curve = entry.get("curve")
            if isinstance(beats, list) and beats:
                source, size = "beats", len(beats)
            elif isinstance(curve, list) and len(curve) >= 2:
                source, size = "curve", len(curve)
            else:
                source, size = "default", 0
            found.append({
                "name": str(entry["name"]),
                "branch": branch,
                "category": cat,
                "source": source,
                "size": size,
                "definition": str(entry.get("definition", "")),
                "entry": entry,
            })
    return found


def find_template(templates: list[dict], wanted: str) -> tuple[list[dict], str]:
    """Exact name, then slug, then substring. Returns (matches, how)."""
    want = wanted.strip().lower()
    exact = [t for t in templates if t["name"].lower() == want]
    if exact:
        return exact, "name"
    by_slug = [t for t in templates if slug(t["name"]) == slug(wanted)]
    if by_slug:
        return by_slug, "slug"
    partial = [t for t in templates if want in t["name"].lower()]
    return partial, "substring"


# --------------------------------------------------------------------------
# beats
# --------------------------------------------------------------------------
def parse_position(raw) -> tuple[float | None, float | None]:
    """Return (start, end) as 0..1 fractions. Accepts 0.25, 25, '8-25%'."""
    if raw is None or isinstance(raw, bool):
        return None, None
    if isinstance(raw, (int, float)):
        return _norm(float(raw), percent=float(raw) > 1.0), None
    text = str(raw)
    # no leading minus: positions are 0..1 and "8-25%" is a range, not a minus
    nums = re.findall(r"\d+(?:\.\d+)?", text)
    if not nums:
        return None, None
    percent = "%" in text or any(float(n) > 1.0 for n in nums)
    start = _norm(float(nums[0]), percent)
    end = _norm(float(nums[1]), percent) if len(nums) > 1 else None
    return start, end


def _norm(value: float, percent: bool) -> float:
    frac = value / 100.0 if percent else value
    return min(max(frac, 0.0), 1.0)


def interpolate(starts: list[float | None]) -> list[float]:
    """Fill unknown positions by even spread between known neighbours."""
    n = len(starts)
    if n == 1:
        return [starts[0] if starts[0] is not None else 0.0]
    out: list[float | None] = list(starts)
    if out[0] is None:
        out[0] = 0.0
    known = [i for i, v in enumerate(out) if v is not None]
    if len(known) == 1 and known[0] == 0:
        return [i / n for i in range(n)]
    last = known[-1]
    if last != n - 1:
        # extrapolate the tail evenly over the remaining span
        span = max(1.0 - out[last], 0.0)  # type: ignore[operator]
        for j in range(last + 1, n):
            out[j] = out[last] + span * (j - last) / (n - last)  # type: ignore[operator]
    known = [i for i, v in enumerate(out) if v is not None]
    for a, b in zip(known, known[1:], strict=False):
        for j in range(a + 1, b):
            out[j] = out[a] + (out[b] - out[a]) * (j - a) / (b - a)  # type: ignore[operator]
    vals = [float(v) for v in out]  # type: ignore[arg-type]
    # keep monotone
    for i in range(1, n):
        vals[i] = max(vals[i], vals[i - 1])
    return vals


def beats_from_template(tpl: dict) -> tuple[list[dict], str]:
    """(beats, note) — beats are {name, purpose, start, end|None}."""
    entry = tpl["entry"]
    if tpl["source"] == "beats":
        raw = [b for b in entry["beats"] if isinstance(b, dict)]
        starts, ends = [], []
        for b in raw:
            s, e = parse_position(b.get("position"))
            starts.append(s)
            ends.append(e)
        filled = interpolate(starts)
        beats = [
            {
                "name": str(b.get("name", f"beat {i + 1}")),
                "purpose": str(b.get("purpose", "")),
                "start": filled[i],
                "end": ends[i],
                "raw_position": b.get("position"),
            }
            for i, b in enumerate(raw)
        ]
        note = ""
        if all(s is None for s in starts):
            note = ("template declares no beat positions — spread evenly")
        return beats, note

    if tpl["source"] == "curve":
        points = []
        for p in entry["curve"]:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                try:
                    points.append((float(p[0]), float(p[1])))
                except (TypeError, ValueError):
                    continue
        points.sort(key=lambda p: p[0])
        beats = []
        for i in range(len(points) - 1):
            (p0, v0), (p1, v1) = points[i], points[i + 1]
            delta = v1 - v0
            shape = ("rise" if delta > 0.05 else
                     "fall" if delta < -0.05 else "hold")
            beats.append({
                "name": f"movement {i + 1}: {shape}",
                "purpose": (f"Carry valence {v0:+.2f} → {v1:+.2f} ({shape}). "
                            "Earn the change with events, not assertion."),
                # the purpose above is boilerplate this script wrote, so it
                # is not evidence about the beat: match moves on the shape
                "fit_text": shape,
                "start": _norm(p0, percent=p0 > 1.0),
                "end": _norm(p1, percent=p1 > 1.0),
                "raw_position": p0,
            })
        return beats, "beats derived from the arc's valence curve"

    beats = [
        {"name": name, "purpose": purpose,
         "start": i / len(DEFAULT_BEATS), "end": None, "raw_position": None}
        for i, (name, purpose) in enumerate(DEFAULT_BEATS)
    ]
    return beats, ("template carries no beats and no curve — generated "
                   "five-beat default spread")


def resolve_spans(beats: list[dict]) -> None:
    """Give every beat an end: its own, else the next beat's start."""
    for i, b in enumerate(beats):
        end = b.get("end")
        if end is None:
            end = beats[i + 1]["start"] if i + 1 < len(beats) else 1.0
        b["end"] = max(float(end), float(b["start"]))


# --------------------------------------------------------------------------
# move suggestions
# --------------------------------------------------------------------------
def move_pool(onto: Ontology, branches: tuple[str, ...]) -> list[dict]:
    pool: list[dict] = []
    for branch in branches:
        for cat, entry in onto.records(branch):
            name = wo.entry_name(entry)
            if not name:
                continue
            record = entry if isinstance(entry, dict) else {}
            cues = record.get("cues") or []
            pool.append({
                "branch": branch,
                "category": cat,
                "name": name,
                "definition": str(record.get("definition", "")),
                "cues": [str(c) for c in cues if isinstance(c, str)][:8],
            })
    return pool


# Moves are matched to the beat they are offered for, not drawn at random:
# an IRAC 'issue' beat should be offered issue-framing moves, not "escape
# scene". The match is deliberately cheap — token overlap between the beat's
# own name/purpose and the move's name, definition and cue phrases, plus a
# position boost for categories that name openings or closings.
FIT_STOP = {
    "the", "and", "that", "this", "with", "from", "for", "but", "not", "are",
    "was", "were", "you", "your", "its", "their", "what", "when", "which",
    "who", "will", "would", "can", "could", "should", "there", "here", "then",
    "than", "into", "over", "under", "about", "after", "before", "because",
    "been", "being", "does", "did", "just", "only", "also", "more", "most",
    "some", "such", "same", "each", "every", "any", "all", "one", "two",
    "how", "why", "very", "much", "many", "still", "even", "own", "way",
    "ways", "thing", "things", "make", "makes", "made", "take", "takes",
    "get", "gets", "like", "use", "used", "uses", "let", "lets", "give",
    "gives", "put", "puts", "out", "off", "has", "have", "had",
    "onto", "upon", "while", "where", "beat", "reader", "readers", "writer",
}
OPENING_CUES = ("open", "hook", "lede", "cold", "entry", "introduc", "frame",
                "first")
CLOSING_CUES = ("clos", "end", "coda", "resolution", "conclu", "callback",
                "final", "last")
# structural words too common to carry a x3 name match on their own
GENERIC_TOKENS = {"opening", "closing", "open", "close", "opens", "closes",
                  "image", "scene", "story", "moment", "world", "beat",
                  "first", "final", "new"}


def fit_tokens(text) -> set[str]:
    return {w for w in re.findall(r"[a-z]{3,}", str(text).lower())
            if w not in FIT_STOP}


def cue_hit(tokens: set[str], cues: tuple[str, ...]) -> bool:
    """Prefix match on whole tokens: 'ending' hits 'end', 'recommend' does not."""
    return any(t.startswith(c) for t in tokens for c in cues)


def move_fit(move: dict, beat_tokens: set[str], position: float) -> float:
    """How well one move answers one beat. 0 means nothing in common."""
    if not beat_tokens:
        return 0.0
    name_tokens = fit_tokens(move["name"])
    category_tokens = fit_tokens(move["category"].replace("_", " "))
    # a bare structural word shared with the beat name is weak evidence:
    # "opening someone's mail" is not an opener for the Opening Image beat
    name_hits = beat_tokens & name_tokens
    score = 3.0 * len(name_hits - GENERIC_TOKENS)
    score += 0.5 * len(name_hits & GENERIC_TOKENS)
    score += 1.0 * len(beat_tokens & fit_tokens(move["definition"]))
    score += 1.0 * len(beat_tokens & fit_tokens(" ".join(move["cues"])))
    score += 1.5 * len(beat_tokens & category_tokens)
    # first and last beats want openers and closers — and actively do not
    # want the other one. The category carries the reliable signal
    # (scene_openings, hooks_and_ledes); a name cue alone is weak.
    opens = cue_hit(name_tokens, OPENING_CUES)
    closes = cue_hit(name_tokens, CLOSING_CUES)
    if position < 0.15:
        score += (1.0 * opens + 2.0 * cue_hit(category_tokens, OPENING_CUES)
                  - 2.0 * closes)
    elif position > 0.85:
        score += (1.0 * closes + 2.0 * cue_hit(category_tokens, CLOSING_CUES)
                  - 2.0 * opens)
    return score


def sample_moves(pool: list[dict], rng: random.Random,
                 beat: dict | None = None) -> list[dict]:
    """Best-fitting moves for this beat, seeded ties; uniform if nothing fits."""
    if not pool:
        return []
    k = min(rng.choice((2, 3)), len(pool))
    if beat is None:
        return rng.sample(pool, k)
    beat_tokens = fit_tokens(
        beat.get("fit_text") or f"{beat['name']} {beat['purpose']}")
    position = (float(beat["start"]) + float(beat["end"])) / 2.0
    # rng.random() is the tie-break, so equal-scoring moves still vary with
    # the seed and the order of the pool never decides anything
    ranked = sorted(((move_fit(m, beat_tokens, position), rng.random(), m)
                     for m in pool), key=lambda t: (-t[0], t[1]))
    if ranked[0][0] <= 0.0:
        return rng.sample(pool, k)
    return [dict(m, fit=round(score, 1)) for score, _, m in ranked[:k]]


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------
def build(tpl: dict, words: int, seed: int, onto: Ontology,
          branches: tuple[str, ...]) -> dict:
    beats, note = beats_from_template(tpl)
    resolve_spans(beats)
    pool = move_pool(onto, branches)
    out_beats = []
    cursor = 1
    for i, b in enumerate(beats):
        rng = random.Random(f"{seed}:{tpl['name']}:{i}")
        span = max(b["end"] - b["start"], 0.0)
        wcount = int(round(span * words))
        start_word = cursor
        cursor += wcount
        out_beats.append({
            "index": i + 1,
            "name": b["name"],
            "purpose": b["purpose"],
            "start_pct": round(b["start"] * 100, 1),
            "end_pct": round(b["end"] * 100, 1),
            "words": wcount,
            "word_range": [start_word, max(start_word, cursor - 1)],
            "raw_position": b.get("raw_position"),
            "moves": sample_moves(pool, rng, b),
        })
    return {
        "template": {k: tpl[k] for k in
                     ("name", "branch", "category", "source", "definition")},
        "words": words,
        "seed": seed,
        "note": note,
        "beats": out_beats,
        "move_branches": list(branches),
        "moves_available": len(pool),
        "unavailable": onto.missing,
    }


def render_markdown(data: dict) -> str:
    t = data["template"]
    lines = [f"# Beat scaffold — {t['name']}", ""]
    src = f"{t['branch']}.{t['category']}"
    if t["definition"]:
        lines.append(f"*{t['definition']}*")
        lines.append("")
    lines.append(
        f"Source: `{src}` ({t['source']}) · target {data['words']:,} words · "
        f"{len(data['beats'])} beats · seed {data['seed']}"
    )
    if data["note"]:
        lines.append(f"Note: {data['note']}.")
    if not data["moves_available"]:
        lines.append(
            "Note: no move branches available yet ("
            + ", ".join(data["move_branches"]) + ") — beats emitted bare.")
    lines.append("")
    for b in data["beats"]:
        lines.append(f"## {b['index']}. {b['name']}")
        lines.append("")
        lines.append(
            f"**Position** {b['start_pct']:g}–{b['end_pct']:g}% · "
            f"~{b['words']:,} words (words {b['word_range'][0]:,}–"
            f"{b['word_range'][1]:,})"
        )
        if b["purpose"]:
            lines.append(f"**Purpose** {b['purpose']}")
        if b["moves"]:
            lines.append("")
            lines.append("**Moves to reach for**")
            for m in b["moves"]:
                defn = f" — {m['definition']}" if m["definition"] else ""
                lines.append(
                    f"- {m['name']}{defn}  `[{m['branch']}.{m['category']}]`")
        lines.append("")
        lines.append("<!-- draft here -->")
        lines.append("")
    if data["unavailable"]:
        lines.append("---")
        lines.append("")
        lines.append("Branches not available yet (skipped, not an error):")
        for name, why in sorted(data["unavailable"].items()):
            lines.append(f"- `{name}`: {why}")
        lines.append("")
    return "\n".join(lines)


def render_list(templates: list[dict]) -> str:
    usable = [t for t in templates if t["source"] in ("beats", "curve")]
    if not usable:
        return ""
    width = max(len(t["name"]) for t in usable)
    lines = [f"{'template':<{width}}  kind    n  source"]
    lines.append("-" * (width + 22))
    for t in sorted(usable, key=lambda x: (x["branch"], x["name"])):
        lines.append(
            f"{t['name']:<{width}}  {t['source']:<6} {t['size']:>2}  "
            f"{t['branch']}.{t['category']}")
    other = len(templates) - len(usable)
    lines.append("")
    lines.append(f"{len(usable)} template(s) with beats/curve; {other} other "
                 "record(s) can still be scaffolded with the default spread.")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--template", metavar="NAME",
                    help="record name to scaffold (exact, slug, or substring)")
    ap.add_argument("--list", action="store_true",
                    help="list templates carrying beats or a curve")
    ap.add_argument("--words", type=int, default=4000,
                    help="total word target the beats are budgeted against")
    ap.add_argument("--seed", type=int, default=None,
                    help="reproducible move sampling (printed if omitted)")
    ap.add_argument("--moves", action="append", default=[], metavar="BRANCH",
                    help="branch to sample suggested moves from "
                         f"(repeatable; default: {', '.join(MOVE_BRANCHES)})")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    onto = Ontology()
    templates = discover(onto)
    branches = tuple(args.moves) if args.moves else MOVE_BRANCHES

    if args.list or not args.template:
        if args.json:
            print(json.dumps({
                "ontology_dir": str(wo.ONTOLOGY_DIR),
                "templates": [
                    {k: t[k] for k in
                     ("name", "branch", "category", "source", "size",
                      "definition")}
                    for t in templates
                ],
            }, indent=2))
            return 0
        if not templates:
            print(f"beat_scaffold: no ontology branch files in "
                  f"{wo.ONTOLOGY_DIR} — no templates to list yet.")
            print("Branches that carry beats/curves per the design doc: "
                  "argument_arrangements, narrative_structures, arc_shapes.")
            return 0
        listing = render_list(templates)
        print(listing or "beat_scaffold: no template carries beats or a curve "
                         "yet (branches present: "
                         + ", ".join(wo.available_branches()) + ").")
        if not args.list:
            print()
            print("Pick one with --template NAME.")
        return 0

    if not templates:
        print(f"beat_scaffold: no ontology branch files in {wo.ONTOLOGY_DIR} "
              f"— cannot resolve template {args.template!r} yet.")
        return 0

    matches, how = find_template(templates, args.template)
    if not matches:
        have = set(wo.available_branches())
        absent = [b for b in TEMPLATE_BRANCHES if b not in have]
        print(f"beat_scaffold: no template matching {args.template!r} in "
              f"{len(templates)} records across {len(have)} branches.")
        print("Run --list to see templates that carry beats or a curve.")
        if absent:
            # still-unauthored branches are not a user error
            print("Template-bearing branches not authored yet: "
                  + ", ".join(absent))
            return 0
        return 1
    if len(matches) > 1:
        print(f"beat_scaffold: {args.template!r} is ambiguous ({how} match):")
        for m in matches[:15]:
            print(f"  {m['name']}  [{m['branch']}.{m['category']}] "
                  f"({m['source']})")
        if len(matches) > 15:
            print(f"  … and {len(matches) - 15} more")
        return 1

    seed = args.seed if args.seed is not None else random.randrange(1, 10**6)
    if not args.moves:
        branches = MOVE_BRANCHES_BY_SOURCE.get(
            matches[0]["branch"], MOVE_BRANCHES)
    data = build(matches[0], max(args.words, 1), seed, onto, branches)
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(render_markdown(data))
        print(f"<!-- beat_scaffold: seed {seed}; rerun with --seed {seed} -->")
    return 0


if __name__ == "__main__":
    sys.exit(main())
