#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml>=6.0",
#     "tomli-w>=1.0",
# ]
# ///
"""Stateful outline composer: build one book's outline, breadth then depth.

The five generative ontology CLIs (prompt_roller, beat_scaffold,
palette_sampler, variation_engine, exercise_generator) are single-shot
rollers. Each is stateless: roll, read, paste, throw away. That is the
right shape for ideation and the wrong shape for an outline, because an
outline is one artifact that has to stay internally consistent while it
grows. This script is the generative counterpart of craft_brief.py —
craft_brief composes the seven diagnostics into one brief; this composes
the ontology into one outline, and keeps it.

Three things the rollers structurally cannot do, and this does:

  state          One YAML document (outline/composition.yaml) holds the
                 book's registry (POV, tense, register, tone, setting,
                 themes, entities), the spine template it was built on,
                 the node tree, and the promise ledger. It is canonical,
                 hand-editable, and diffable — commit it.
  conditioning   Children are not rolled freely. A child inherits its
                 parent's span and word budget, takes its valence from
                 the spine curve at its own midpoint, and draws its craft
                 moves from a pool filtered by that valence's sign and
                 local slope plus the parent's purpose. A falling span is
                 offered setbacks and reversals; a rising span is offered
                 recoveries and payoffs.
  idempotence    All randomness for a node's expansion comes from
                 Random(f"{seed}:{node_id}"). Deepening ch07 cannot move
                 ch01. Re-running the same deepen is refused rather than
                 silently re-rolled (--reroll opts in, and refuses in turn
                 if any child has itself been deepened or locked).

One schema serves fiction and nonfiction; `kind` decides which registry
slots are rolled, which branches supply spine templates, and which
branches supply moves. Crossovers are warned about, never blocked — a
nonfiction book arranged on a narrative arc is a choice, not an error.

Rules inherited from the ontology (docs/architecture/writing-ontology.md):
branch FILENAMES are the contract and categories are discovered at
runtime; missing or broken branch files are named on stderr and skipped;
faults are never emitted as directives; the descriptor banks
(settings_and_environments, tones_and_moods) fill the registry's setting
and tone slots only, never a move list.

Advisory. Nothing here writes prose or touches latex/. It exits nonzero
only for hard user errors — no state file, unknown node, unknown
template, an overwrite refused — and for `lint --strict` with findings.

Usage:
    uv run scripts/outline_composer.py init --kind fiction --words 80000 \
        --premise "a small-town lawyer finds the town archive is faked" --seed 7
    uv run scripts/outline_composer.py init --kind nonfiction --words 60000 \
        --template "classical oration" --chapters 9 --seed 3
    uv run scripts/outline_composer.py --list-templates --kind fiction
    uv run scripts/outline_composer.py deepen ch01
    uv run scripts/outline_composer.py deepen ch01 --children 4 --reroll
    uv run scripts/outline_composer.py deepen --all-stubs
    uv run scripts/outline_composer.py lint
    uv run scripts/outline_composer.py render --out outline/outline.md
    uv run scripts/outline_composer.py render --format html --out outline/outline.html
    uv run scripts/outline_composer.py render --format json | jq '.nodes[0]'
    uv run scripts/outline_composer.py render --format toml --out outline/outline.toml
    uv run scripts/outline_composer.py show ch03
    uv run scripts/outline_composer.py set registry.tense=present
"""

from __future__ import annotations

import argparse
import datetime as _dt
import html as _html
import json
import math
import random
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import writing_ontology as wo  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STATE = Path("outline") / "composition.yaml"
SCHEMA_VERSION = 1
SPARK = "▁▂▃▄▅▆▇█"

# Ideation nouns and atmosphere labels, not craft technique
# (writing-ontology.md). Legal in the registry's setting/tone slots and
# nowhere else in this file.
DESCRIPTOR_BANKS = ("settings_and_environments", "tones_and_moods")


# --------------------------------------------------------------------------
# faults — copied from prompt_roller.py, which carries the stricter logic:
# wo.is_fault decides on `polarity` else the category name; the branch name
# is prepended because not every fault category says so in its own title;
# "device" is dropped first (sound_devices contains "vice"); a record whose
# own copy marks it as a failure counts; and a name that is a fault anywhere
# is a fault everywhere, so aspect homonyms cannot leak through the other
# home. Each ontology script carries its own copy — the house convention.
# --------------------------------------------------------------------------
def fault_label(branch: str, category: str) -> str:
    return f"{branch}.{category}".replace("device", "")


def fault_copy(entry) -> bool:
    if not isinstance(entry, dict):
        return False
    if str(entry.get("example", "")).strip().lower().startswith("faulty"):
        return True
    hay = f"{entry.get('definition', '')} {entry.get('effect', '')}".lower()
    return ("as a diagnostic" in hay or "unintentional" in hay
            or "inadvertent" in hay)


_FAULT_NAMES: set[str] | None = None


def fault_names() -> set[str]:
    """Every entry name that is a fault somewhere in the ontology."""
    global _FAULT_NAMES
    if _FAULT_NAMES is None:
        names: set[str] = set()
        for branch in wo.available_branches():
            try:
                data = wo.load_branch(branch)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            for category, entries in (data.get("categories") or {}).items():
                if not isinstance(entries, list):
                    continue
                for entry in entries:
                    if (wo.is_fault(entry, fault_label(branch, category))
                            or fault_copy(entry)):
                        names.add(wo.entry_name(entry).strip().lower())
        _FAULT_NAMES = names
    return _FAULT_NAMES


def is_fault(entry, branch: str = "", category: str = "") -> bool:
    if wo.is_fault(entry, fault_label(branch, category)) or fault_copy(entry):
        return True
    if isinstance(entry, dict) and entry.get("polarity") == "virtue":
        return False
    return wo.entry_name(entry).strip().lower() in fault_names()


_BANK_NAMES: set[str] | None = None


def descriptor_bank_names() -> set[str]:
    """Every entry name owned by a descriptor bank (lint uses this)."""
    global _BANK_NAMES
    if _BANK_NAMES is None:
        names: set[str] = set()
        for branch in DESCRIPTOR_BANKS:
            try:
                data = wo.load_branch(branch)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            for entries in (data.get("categories") or {}).values():
                if isinstance(entries, list):
                    names.update(
                        wo.entry_name(e).strip().lower() for e in entries)
        _BANK_NAMES = names
    return _BANK_NAMES


# Delivery-mode heuristic for nonfiction venues and occasions — copied from
# prompt_roller.py. The ontology holds every publication form in one
# category, so a nonfiction book would otherwise be "pitched at toast".
SPOKEN_NAME_CUES = (
    "toast", "eulogy", "sermon", "speech", "oration", "address", "talk",
    "lecture", "podcast", "narration", "deck", "screenplay", "stage play",
    "novel", "short story", "interview",
)
SPOKEN_DEF_CUES = ("spoken", "voiceover", "aloud", "live performance",
                   "recited")


def spoken_form(entry) -> bool:
    name = wo.entry_name(entry).lower()
    if any(cue in name for cue in SPOKEN_NAME_CUES):
        return True
    definition = (str(entry.get("definition", "")).lower()
                  if isinstance(entry, dict) else "")
    return any(cue in definition for cue in SPOKEN_DEF_CUES)


# --------------------------------------------------------------------------
# fault-tolerant ontology access (each script carries its own copy)
# --------------------------------------------------------------------------
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

    def categories(self, name: str) -> dict[str, list]:
        b = self.branch(name)
        if not b:
            return {}
        cats = b.get("categories") or {}
        return {k: v for k, v in cats.items() if isinstance(v, list) and v}

    def records(self, name: str):
        for cat, entries in self.categories(name).items():
            for e in entries:
                yield cat, e

    def pool(self, name, keywords=(), category=None, avoid=()):
        """Entries as (entry, category) pairs, faults filtered out."""
        cats = self.categories(name)
        if not cats:
            return []
        if category:
            if category in cats:
                return [(e, category) for e in cats[category]
                        if not is_fault(e, name, category)]
            self.missing.setdefault(
                f"{name}.{category}",
                "no such category; have: " + ", ".join(sorted(cats)),
            )
        allowed = [c for c in cats if not _matches(c, avoid)] or list(cats)
        chosen = [c for c in allowed if _matches(c, keywords)] \
            if keywords else []
        if not chosen:
            chosen = allowed
        return [(e, c) for c in chosen for e in cats[c]
                if not is_fault(e, name, c)]


def _matches(category: str, keywords) -> bool:
    label = category.lower().replace("_", " ").replace("-", " ")
    return any(k in label for k in keywords)


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")


# --------------------------------------------------------------------------
# template discovery + position maths (adapted from beat_scaffold.py)
# --------------------------------------------------------------------------
# Which branches supply a spine, by kind. Discovery is still runtime: a
# branch listed here that carries no beats and no curve simply yields no
# templates (narrative_structures is a `term` branch today, so it does not).
TEMPLATE_BRANCHES_BY_KIND = {
    "fiction": ("story_beat_templates", "narrative_structures", "arc_shapes"),
    "nonfiction": ("argument_arrangements", "arc_shapes"),
}
# arc_shapes holds both story curves and epistemic (certainty) curves; the
# category, not the branch, decides which kind they belong to.
EPISTEMIC_HINT = "epistemic"

MOVE_BRANCHES_BY_KIND = {
    "fiction": ("scene_patterns", "interaction_moves", "dialogue_mechanics",
                "information_release"),
    "nonfiction": ("discourse_moves", "evidence_types", "paragraph_shapes",
                   "argumentation_schemes"),
}

DEFAULT_BEATS = [
    ("opening", "Establish the terms and the reason to keep reading."),
    ("development", "Build the case or the situation; raise the cost."),
    ("turn", "Complicate, reverse, or admit what cuts against you."),
    ("consequence", "Play out what the turn forces."),
    ("close", "Land the change; pay what the opening promised."),
]


def discover(onto: Ontology) -> list[dict]:
    """Every ontology record that could serve as a spine."""
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
                continue
            found.append({
                "name": str(entry["name"]),
                "branch": branch,
                "category": cat,
                "source": source,
                "size": size,
                "definition": str(entry.get("definition", "")),
                "entry": entry,
            })
    found.sort(key=lambda t: (t["branch"], t["category"], t["name"]))
    return found


def eligible(templates: list[dict], kind: str) -> list[dict]:
    branches = TEMPLATE_BRANCHES_BY_KIND.get(kind, ())
    out = []
    for t in templates:
        if t["branch"] not in branches:
            continue
        if t["branch"] == "arc_shapes":
            epistemic = EPISTEMIC_HINT in t["category"].lower()
            if epistemic != (kind == "nonfiction"):
                continue
        out.append(t)
    return out


def find_template(templates: list[dict], wanted: str) -> tuple[list[dict], str]:
    """Exact name, then slug, then substring. Returns (matches, how)."""
    want = wanted.strip().lower()
    exact = [t for t in templates if t["name"].lower() == want]
    if exact:
        return exact, "name"
    by_slug = [t for t in templates if slug(t["name"]) == slug(wanted)]
    if by_slug:
        return by_slug, "slug"
    return [t for t in templates if want in t["name"].lower()], "substring"


def parse_position(raw) -> tuple[float | None, float | None]:
    """Return (start, end) as 0..1 fractions. Accepts 0.25, 25, '8-25%'."""
    if raw is None or isinstance(raw, bool):
        return None, None
    if isinstance(raw, (int, float)):
        return _norm(float(raw), percent=float(raw) > 1.0), None
    nums = re.findall(r"\d+(?:\.\d+)?", str(raw))
    if not nums:
        return None, None
    percent = "%" in str(raw) or any(float(n) > 1.0 for n in nums)
    start = _norm(float(nums[0]), percent)
    end = _norm(float(nums[1]), percent) if len(nums) > 1 else None
    return start, end


def _norm(value: float, percent: bool) -> float:
    frac = value / 100.0 if percent else value
    return min(max(frac, 0.0), 1.0)


def interpolate(starts: list[float | None]) -> list[float]:
    """Fill unknown positions by even spread between known neighbours."""
    n = len(starts)
    if n == 0:
        return []
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
        span = max(1.0 - out[last], 0.0)  # type: ignore[operator]
        for j in range(last + 1, n):
            out[j] = out[last] + span * (j - last) / (n - last)  # type: ignore[operator]
    known = [i for i, v in enumerate(out) if v is not None]
    for a, b in zip(known, known[1:], strict=False):
        for j in range(a + 1, b):
            out[j] = out[a] + (out[b] - out[a]) * (j - a) / (b - a)  # type: ignore[operator]
    vals = [float(v) for v in out]  # type: ignore[arg-type]
    for i in range(1, n):
        vals[i] = max(vals[i], vals[i - 1])
    return vals


def beats_from_template(tpl: dict) -> tuple[list[dict], str]:
    """(beats, note) — beats are {name, purpose, start, end}."""
    entry = tpl["entry"]
    if tpl["source"] == "beats":
        raw = [b for b in entry["beats"] if isinstance(b, (dict, str))]
        starts: list[float | None] = []
        ends: list[float | None] = []
        norm = []
        for b in raw:
            if isinstance(b, str):
                norm.append({"name": b, "purpose": ""})
                starts.append(None)
                ends.append(None)
                continue
            norm.append(b)
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
            }
            for i, b in enumerate(norm)
        ]
        note = ("template declares no beat positions — spread evenly"
                if all(s is None for s in starts) else "")
        return beats, note

    if tpl["source"] == "curve":
        points = clean_curve(entry.get("curve"))
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
                "start": p0,
                "end": p1,
            })
        return beats, "beats derived from the arc's valence curve"

    beats = [
        {"name": name, "purpose": purpose,
         "start": i / len(DEFAULT_BEATS), "end": None}
        for i, (name, purpose) in enumerate(DEFAULT_BEATS)
    ]
    return beats, "template carries no beats and no curve — default spread"


def resolve_spans(beats: list[dict]) -> None:
    """Give every beat an end: its own, else the next beat's start."""
    for i, b in enumerate(beats):
        end = b.get("end")
        if end is None:
            end = beats[i + 1]["start"] if i + 1 < len(beats) else 1.0
        b["end"] = max(float(end), float(b["start"]))
    if beats:
        beats[-1]["end"] = 1.0


# --------------------------------------------------------------------------
# curve maths
# --------------------------------------------------------------------------
def clean_curve(curve) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    for p in curve or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                pts.append((_norm(float(p[0]), float(p[0]) > 1.0),
                            float(p[1])))
            except (TypeError, ValueError):
                continue
    pts.sort(key=lambda p: p[0])
    return pts


def curve_at(curve, pos: float) -> float | None:
    """Linear interpolation of the spine curve at `pos` (0..1)."""
    pts = clean_curve(curve)
    if len(pts) < 2:
        return None
    if pos <= pts[0][0]:
        return round(pts[0][1], 3)
    if pos >= pts[-1][0]:
        return round(pts[-1][1], 3)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:], strict=False):
        if x0 <= pos <= x1:
            if x1 - x0 < 1e-12:
                return round(y1, 3)
            return round(y0 + (y1 - y0) * (pos - x0) / (x1 - x0), 3)
    return round(pts[-1][1], 3)


def sparkline(values, lo: float | None = None, hi: float | None = None) -> str:
    """Block-char sparkline. Pass lo/hi to plot against a fixed scale, so a
    flat node reads as flat instead of being renormalized into a slope."""
    vals = [v for v in values if isinstance(v, (int, float))]
    if not vals:
        return ""
    lo = min(vals) if lo is None else lo
    hi = max(vals) if hi is None else hi
    if hi - lo < 1e-9:
        return SPARK[len(SPARK) // 2] * len(vals)
    span = len(SPARK) - 1
    return "".join(
        SPARK[max(0, min(span, round((v - lo) / (hi - lo) * span)))]
        for v in vals)


def curve_bounds(curve) -> tuple[float | None, float | None]:
    pts = clean_curve(curve)
    if not pts:
        return None, None
    vals = [v for _p, v in pts]
    return min(vals), max(vals)


def partition_words(total: int, weights: list[float]) -> list[int]:
    """Largest-remainder split that sums to `total` exactly, deterministic."""
    n = len(weights)
    if n == 0:
        return []
    total = max(int(total), 0)
    tw = sum(weights)
    if tw <= 0:
        weights = [1.0] * n
        tw = float(n)
    exact = [total * w / tw for w in weights]
    base = [int(math.floor(e)) for e in exact]
    remainder = total - sum(base)
    order = sorted(range(n), key=lambda i: (-(exact[i] - base[i]), i))
    for i in order[:max(remainder, 0)]:
        base[i] += 1
    return base


# --------------------------------------------------------------------------
# conditioning
# --------------------------------------------------------------------------
# The keyword sets that turn a valence sign and a local slope into a move
# filter. Substrings, matched case-insensitively against an entry's name,
# definition, effect, cues and tags. Concession is a falling move: it is
# what it costs you to be fair, not a payoff.
MODE_CUES = {
    "falling": ("setback", "loss", "confront", "reversal", "complicat",
                "escalat", "objection", "doubt", "conflict", "refus",
                "conced", "concession", "withhold", "cost"),
    "rising": ("resolution", "recovery", "reconcil", "insight", "answer",
               "payoff", "synthesis", "triumph", "reveal", "resolve"),
    "flat": ("establish", "exposition", "setup", "introduc", "context",
             "orient", "background", "definition"),
}

PURPOSE_STOP = {
    "the", "and", "that", "this", "with", "from", "for", "into", "onto",
    "their", "there", "which", "while", "where", "what", "when", "them",
    "they", "then", "than", "your", "yours", "have", "having", "been",
    "being", "does", "doing", "will", "would", "could", "should", "about",
    "after", "before", "because", "reader", "readers", "writer", "story",
    "scene", "chapter", "beat", "beats", "book", "books", "text", "prose",
    "make", "makes", "made", "take", "takes", "give", "gives", "show",
    "shows", "thing", "things", "something", "someone", "enough", "still",
    "every", "other", "another", "first", "second", "third", "final",
    "without", "within", "against", "through", "order", "point", "points",
}

MODE_CLAUSES = {
    "falling": (
        "cost something that cannot be bought back",
        "let the opposition win this exchange on the merits",
        "raise the price of the position already taken",
        "close off the easy way out",
        "make the doubt specific rather than atmospheric",
    ),
    "rising": (
        "pay something the earlier span promised",
        "let the pieces already on the table do the work",
        "convert an accumulated cost into a result",
        "restore something, changed",
        "let the reader see the answer arrive before it is named",
    ),
    "flat": (
        "establish the terms the next movement will disturb",
        "put the concrete particulars on the table",
        "orient the reader without narrating the orientation",
        "seed one detail that will be needed later",
        "hold the level and vary the texture instead",
    ),
}


def purpose_tokens(text: str, limit: int = 6) -> tuple[str, ...]:
    """Content words from a parent purpose, used as extra move keywords."""
    seen: list[str] = []
    for word in re.findall(r"[a-z]{5,}", str(text).lower()):
        if word in PURPOSE_STOP or word in seen:
            continue
        seen.append(word)
        if len(seen) >= limit:
            break
    return tuple(seen)


def span_mode(valence: float | None, slope: float | None) -> str:
    """falling | rising | flat, from the spine curve over this span."""
    if slope is not None:
        if slope < -0.05:
            return "falling"
        if slope > 0.05:
            return "rising"
    if valence is not None:
        if valence < -0.2:
            return "falling"
        if valence > 0.2:
            return "rising"
    return "flat"


def build_move_pool(onto: Ontology, branches) -> list[dict]:
    """Every non-fault move entry in `branches`, with a match haystack."""
    pool: list[dict] = []
    for branch in branches:
        if branch in DESCRIPTOR_BANKS:
            print(f"outline_composer: {branch} is a descriptor bank — "
                  "not a source of craft moves; skipped", file=sys.stderr)
            continue
        for cat, entry in onto.records(branch):
            if is_fault(entry, branch, cat):
                continue
            name = wo.entry_name(entry).strip()
            if not name:
                continue
            record = entry if isinstance(entry, dict) else {}
            bits = [name, str(record.get("definition", "")),
                    str(record.get("effect", ""))]
            for key in ("tags", "cues"):
                val = record.get(key)
                if isinstance(val, list):
                    bits.append(" ".join(str(v) for v in val))
                elif val:
                    bits.append(str(val))
            pool.append({
                "name": name,
                "branch": branch,
                "category": cat,
                "definition": str(record.get("definition", "")),
                "haystack": " ".join(bits).lower(),
            })
    pool.sort(key=lambda m: (m["branch"], m["category"], m["name"]))
    return pool


def conditioned_moves(pool, rng, mode, valence, slope, parent_purpose, k=None):
    """k moves whose text answers this span's shape and its parent's job."""
    if not pool:
        return []
    cues = MODE_CUES.get(mode, ())
    tokens = purpose_tokens(parent_purpose)
    keywords = tuple(cues) + tokens
    hits: list[tuple[dict, str]] = []
    for m in pool:
        for kw in keywords:
            if kw in m["haystack"]:
                hits.append((m, kw))
                break
    k = k if k is not None else rng.choice((2, 3))
    shape = f"{mode} span"
    if valence is not None:
        shape += f" (valence {valence:+.2f}"
        if slope is not None:
            shape += f", slope {slope:+.2f}"
        shape += ")"
    if not hits:
        picks = rng.sample(pool, min(k, len(pool)))
        why = (f"{shape}: no move in the pool matched the conditioning "
               "keywords — sampled unfiltered")
        return [move_record(m, why) for m in picks]
    chosen = rng.sample(hits, min(k, len(hits)))
    return [
        move_record(m, f"{shape}; matched '{kw}' via "
                       + ("the arc" if kw in cues else "the parent purpose"))
        for m, kw in chosen
    ]


def move_record(m: dict, why: str) -> dict:
    return {
        "name": m["name"],
        "branch": m["branch"],
        "category": m["category"],
        "definition": m["definition"],
        "why": why,
    }


# --------------------------------------------------------------------------
# registry slots
# --------------------------------------------------------------------------
def slot(sid, label, branch, keys=(), n=1, avoid=(), written_only=False):
    return {"id": sid, "label": label, "branch": branch, "keys": keys,
            "n": n, "avoid": avoid, "written_only": written_only}


VENUE_CATEGORY_KEYS = ("venue", "genre", "publication", "form")
SITUATION_KEYS = ("exigence", "occasion", "audience", "reader", "constraint")

REGISTRY_SLOTS = {
    "fiction": [
        slot("pov", "POV", "pov_and_narration",
             ("pov", "point of view", "person", "distance", "narrat")),
        slot("tense_strategy", "Tense strategy", "pov_and_narration",
             ("tense",)),
        slot("register", "Register", "diction_and_register",
             ("register level", "register", "style")),
        slot("tone", "Tone", "tones_and_moods", avoid=("stance",)),
        slot("setting", "Setting", "settings_and_environments"),
        slot("protagonist", "Protagonist", "character_and_persona",
             ("archetype", "stock", "function", "protagonist")),
        slot("themes", "Themes", "themes_and_questions",
             ("theme", "dilemma", "question", "motif"), n=2),
    ],
    "nonfiction": [
        slot("stance", "Stance", "tones_and_moods", ("stance",)),
        slot("narration", "Narration mode", "pov_and_narration",
             ("nonfiction", "narration")),
        slot("tense_strategy", "Tense strategy", "pov_and_narration",
             ("tense",)),
        slot("register", "Register", "diction_and_register",
             ("register level", "register", "style")),
        slot("tone", "Tone", "tones_and_moods", avoid=("stance",)),
        slot("persona", "Authorial persona", "character_and_persona",
             ("authorial", "persona", "argumentative", "role")),
        slot("audience", "Audience", "rhetorical_situations",
             SITUATION_KEYS, avoid=VENUE_CATEGORY_KEYS, written_only=True),
        slot("venue", "Venue", "rhetorical_situations",
             VENUE_CATEGORY_KEYS, written_only=True),
        slot("themes", "Themes / questions", "themes_and_questions",
             ("research question", "philosophical", "question", "theme"),
             n=2),
    ],
}

# Registry slots a node may legitimately override (with `override: true`).
OVERRIDABLE = ("pov", "tense", "register", "tone", "setting", "stance",
               "narration")


def entry_value(entry, branch: str, category: str) -> dict:
    out = {"name": wo.entry_name(entry).strip(),
           "source": f"{branch}.{category}"}
    if isinstance(entry, dict) and str(entry.get("definition", "")).strip():
        out["definition"] = str(entry["definition"]).strip()
    return out


def roll_registry(kind: str, onto: Ontology, rng: random.Random) -> dict:
    registry: dict = {}
    for spec in REGISTRY_SLOTS.get(kind, []):
        pool = onto.pool(spec["branch"], spec["keys"], None, spec["avoid"])
        if spec["written_only"]:
            # a book is not delivered as a toast, and is not a screenplay
            pool = [(e, c) for e, c in pool if not spoken_form(e)] or pool
        if not pool:
            continue
        picks = rng.sample(pool, min(spec["n"], len(pool)))
        values = [entry_value(e, spec["branch"], c) for e, c in picks]
        registry[spec["id"]] = values if spec["n"] > 1 else values[0]
    strategy = registry.get("tense_strategy") or {}
    name = str(strategy.get("name", "")).lower()
    registry["tense"] = "present" if "present" in name else "past"
    registry["entities"] = []
    # canonical key order: tense next to its strategy, entities last
    order = ["pov", "narration", "stance", "tense", "tense_strategy",
             "register", "tone", "setting", "protagonist", "persona",
             "audience", "venue", "themes", "entities"]
    return {k: registry[k] for k in order if k in registry}


# --------------------------------------------------------------------------
# state file
# --------------------------------------------------------------------------
def state_path(arg: str | None) -> Path:
    if arg:
        return Path(arg).expanduser()
    return Path.cwd() / DEFAULT_STATE


def load_state(path: Path) -> dict | None:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"outline_composer: no state file at {path} — "
              "run `init` first (or pass --file).", file=sys.stderr)
        return None
    except (OSError, yaml.YAMLError) as exc:
        print(f"outline_composer: cannot read {path}: {exc}", file=sys.stderr)
        return None
    if not isinstance(raw, dict):
        print(f"outline_composer: {path} is not a YAML mapping.",
              file=sys.stderr)
        return None
    return raw


def save_state(state: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(state, sort_keys=False, allow_unicode=True,
                          default_flow_style=False, width=100)
    path.write_text(text, encoding="utf-8")


def nodes_of(state: dict) -> list[dict]:
    nodes = state.get("nodes")
    return nodes if isinstance(nodes, list) else []


def walk(nodes, depth: int = 1, parent: dict | None = None):
    """Yield (node, depth, parent) depth-first in declared order."""
    for node in nodes or []:
        if not isinstance(node, dict):
            continue
        yield node, depth, parent
        yield from walk(node.get("children") or [], depth + 1, node)


def find_node(state: dict, node_id: str):
    for node, depth, parent in walk(nodes_of(state)):
        if str(node.get("id")) == node_id:
            return node, depth, parent
    return None, 0, None


def node_span(node) -> tuple[float, float]:
    pos = node.get("position") if isinstance(node, dict) else None
    if isinstance(pos, (list, tuple)) and len(pos) >= 2:
        try:
            return float(pos[0]), float(pos[1])
        except (TypeError, ValueError):
            return 0.0, 0.0
    return 0.0, 0.0


def make_node(node_id, title, purpose, start, end, words, valence) -> dict:
    """One node, keys in canonical order so rewrites diff minimally."""
    return {
        "id": node_id,
        "title": title,
        "purpose": purpose,
        "position": [round(float(start), 6), round(float(end), 6)],
        "words": int(words),
        "valence": valence,
        "status": "stub",
        "moves": [],
        "opens": [],
        "pays": [],
        "children": [],
    }


def next_promise_id(state: dict) -> str:
    used = set()
    for p in state.get("promises") or []:
        if isinstance(p, dict):
            m = re.fullmatch(r"p(\d+)", str(p.get("id", "")))
            if m:
                used.add(int(m.group(1)))
    n = 1
    while n in used:
        n += 1
    return f"p{n}"


def add_promise(state, node, kind, text, paid_by=None) -> dict:
    pid = next_promise_id(state)
    promise = {
        "id": pid,
        "kind": kind,
        "text": text,
        "opened_by": node["id"],
        "paid_by": paid_by,
        "intentional_open": paid_by is None,
    }
    state.setdefault("promises", []).append(promise)
    node.setdefault("opens", []).append(pid)
    return promise


# --------------------------------------------------------------------------
# init
# --------------------------------------------------------------------------
def level1_from_beats(beats, words, chapters) -> list[dict]:
    """Beats (or an even chapter grid mapped onto them) as level-1 spans."""
    if chapters and chapters > 0:
        spans = []
        for i in range(chapters):
            start, end = i / chapters, (i + 1) / chapters
            overlap = [b for b in beats
                       if b["end"] > start + 1e-9 and b["start"] < end - 1e-9]
            if not overlap and beats:
                mid = (start + end) / 2
                overlap = [min(beats, key=lambda b: abs(
                    (b["start"] + b["end"]) / 2 - mid))]
            names = [b["name"] for b in overlap][:2]
            purposes = [b["purpose"] for b in overlap if b["purpose"]][:2]
            spans.append({
                "name": " / ".join(names) or f"chapter {i + 1}",
                "purpose": " ".join(purposes),
                "start": start,
                "end": end,
            })
        beats = spans
    weights = [max(b["end"] - b["start"], 1e-6) for b in beats]
    budgets = partition_words(words, weights)
    return [dict(b, words=budgets[i]) for i, b in enumerate(beats)]


def reproduce_line(args, words, seed, tpl, arc) -> str:
    """The exact command that rebuilds this composition from scratch."""
    parts = ["uv run scripts/outline_composer.py init",
             f"--kind {args.kind}", f"--words {words}", f"--seed {seed}",
             f'--template "{tpl["name"]}"']
    if arc is not None:
        parts.append(f'--arc "{arc["name"]}"')
    if args.chapters:
        parts.append(f"--chapters {args.chapters}")
    if args.title:
        parts.append(f'--title "{args.title}"')
    if args.premise:
        parts.append(f'--premise "{args.premise}"')
    return " ".join(parts)


def cmd_init(args) -> int:
    path = state_path(args.file)
    if path.exists() and not args.force:
        print(f"outline_composer: {path} already exists — pass --force to "
              "overwrite (it is canonical state; prefer a new --file).",
              file=sys.stderr)
        return 1

    seed = args.seed if args.seed is not None else random.randrange(1, 10**6)
    onto = Ontology()
    templates = discover(onto)
    if not templates:
        print(f"outline_composer: no spine templates in {wo.ONTOLOGY_DIR} — "
              "the ontology has no records carrying beats or a curve.",
              file=sys.stderr)
        return 1

    kind_pool = eligible(templates, args.kind)
    rng = random.Random(f"{seed}:init:{args.kind}")

    if args.template:
        matches, how = find_template(templates, args.template)
        if not matches:
            print(f"outline_composer: no template matching "
                  f"{args.template!r} in {len(templates)} records. "
                  "Run --list-templates.", file=sys.stderr)
            return 1
        if len(matches) > 1:
            print(f"outline_composer: {args.template!r} is ambiguous "
                  f"({how} match):", file=sys.stderr)
            for m in matches[:15]:
                print(f"  {m['name']}  [{m['branch']}.{m['category']}]",
                      file=sys.stderr)
            return 1
        tpl = matches[0]
        if tpl not in kind_pool:
            print(f"outline_composer: note — {tpl['name']!r} lives in "
                  f"{tpl['branch']}.{tpl['category']}, which is not the "
                  f"usual spine source for {args.kind}. Using it anyway.",
                  file=sys.stderr)
    else:
        if not kind_pool:
            print(f"outline_composer: no {args.kind} spine template "
                  "available; name one with --template.", file=sys.stderr)
            return 1
        tpl = rng.choice(kind_pool)

    beats, note = beats_from_template(tpl)
    resolve_spans(beats)
    if not beats:
        print(f"outline_composer: template {tpl['name']!r} yielded no beats.",
              file=sys.stderr)
        return 1

    # A beat sheet says what happens where; an arc shape says how it should
    # feel there. Conditioning needs the second, so a spine that carries no
    # curve of its own is paired with one (--arc pins it).
    arc = None
    points = clean_curve(tpl["entry"].get("curve"))
    if args.arc:
        matches, how = find_template(templates, args.arc)
        matches = [m for m in matches if m["source"] == "curve"]
        if len(matches) != 1:
            print(f"outline_composer: --arc {args.arc!r} matched "
                  f"{len(matches)} curve-bearing record(s) ({how}); name one "
                  "exactly (--list-templates).", file=sys.stderr)
            return 1
        arc = matches[0]
    elif not points:
        curved = [t for t in eligible(templates, args.kind)
                  if t["source"] == "curve"]
        if curved:
            arc = rng.choice(curved)
    if arc is not None:
        points = clean_curve(arc["entry"].get("curve"))

    registry = roll_registry(args.kind, onto, rng)
    curve = [[round(p, 4), round(v, 4)] for p, v in points]
    words = max(int(args.words), 1)
    spans = level1_from_beats(beats, words, args.chapters)

    state: dict = {
        "composer": {
            "version": SCHEMA_VERSION,
            "tool": "outline_composer.py",
            "seed": seed,
            "created": _dt.date.today().isoformat(),
            "reproduce": reproduce_line(args, words, seed, tpl, arc),
        },
        "meta": {
            "kind": args.kind,
            "title": args.title or "",
            "premise": args.premise or "",
            "words": words,
        },
        "registry": registry,
        "spine": {
            "template": {
                "name": tpl["name"],
                "branch": tpl["branch"],
                "category": tpl["category"],
                "source": tpl["source"],
            },
            "definition": tpl["definition"],
            "note": note,
            "arc": ({"name": arc["name"], "branch": arc["branch"],
                     "category": arc["category"],
                     "definition": arc["definition"]}
                    if arc is not None else None),
            "curve": curve,
            "beats": [
                {"name": b["name"], "purpose": b["purpose"],
                 "position": [round(b["start"], 4), round(b["end"], 4)]}
                for b in beats
            ],
        },
        "nodes": [],
        "promises": [],
    }

    pool = build_move_pool(onto, MOVE_BRANCHES_BY_KIND.get(args.kind, ()))
    nodes: list[dict] = []
    for i, span in enumerate(spans):
        node_id = f"ch{i + 1:02d}"
        start, end = span["start"], span["end"]
        mid = (start + end) / 2
        valence = curve_at(curve, mid)
        v0, v1 = curve_at(curve, start), curve_at(curve, end)
        slope = None if v0 is None or v1 is None else round(v1 - v0, 3)
        node = make_node(node_id, span["name"], span["purpose"],
                         start, end, span["words"], valence)
        nrng = random.Random(f"{seed}:{node_id}:level1")
        mode = span_mode(valence, slope)
        node["moves"] = conditioned_moves(
            pool, nrng, mode, valence, slope, span["purpose"] or span["name"])
        nodes.append(node)
    state["nodes"] = nodes

    # The spine's central promise: opened by the first node, paid by the last.
    if nodes:
        theme = ""
        themes = registry.get("themes") or []
        if isinstance(themes, list) and themes:
            theme = str(themes[0].get("name", ""))
        subject = args.premise or args.title or "the book's governing claim"
        text = f"Central question — {subject}"
        if theme:
            text += f" (theme: {theme})"
        add_promise(state, nodes[0], "question", text,
                    paid_by=nodes[-1]["id"])
        nodes[-1].setdefault("pays", []).append(state["promises"][-1]["id"])

    save_state(state, path)
    print(f"outline_composer: wrote {path}")
    print(f"  kind      {args.kind}")
    print(f"  spine     {tpl['name']}  [{tpl['branch']}.{tpl['category']}, "
          f"{tpl['source']}]")
    if arc is not None:
        print(f"  arc       {arc['name']}  [{arc['branch']}.{arc['category']}]"
              f"  {sparkline([v for _p, v in points])}")
    if note:
        print(f"  note      {note}")
    print(f"  nodes     {len(nodes)} level-1, {words:,} words")
    print(f"  seed      {seed}  (reproduce: {state['composer']['reproduce']})")
    if onto.missing:
        for name, why in sorted(onto.missing.items()):
            print(f"  skipped   {name}: {why}", file=sys.stderr)
    print("  next      deepen ch01  ·  deepen --all-stubs  ·  lint  ·  render")
    return 0


# --------------------------------------------------------------------------
# deepen
# --------------------------------------------------------------------------
CHILD_PREFIX = {2: "s", 3: "b", 4: "u"}


def child_prefix(depth: int) -> str:
    return CHILD_PREFIX.get(depth, "n")


def short_title(text: str, limit: int = 28) -> str:
    text = str(text).strip()
    return text if len(text) <= limit else text[:limit - 1].rstrip() + "…"


def cast_slot(noun: str) -> str:
    """A generated cast slot: an indefinite label, never a proper name."""
    noun = str(noun).strip()
    if re.match(r"^(the|a|an)\s", noun, re.I):
        return noun
    return ("an " if noun[:1].lower() in "aeiou" else "a ") + noun


ROLE_PREFIX_RE = re.compile(
    r"^(open|develop|turn|close|carry) this span\s+[—-]\s+", re.I)


def first_clause(text: str, limit: int = 90) -> str:
    text = ROLE_PREFIX_RE.sub("", " ".join(str(text).split()))
    if not text:
        return ""
    head = re.split(r"(?<=[.;])\s", text)[0].rstrip(" .;")
    return head if len(head) <= limit else head[:limit - 1].rstrip() + "…"


def child_roles(n: int, modes: list[str]) -> list[str]:
    if n <= 0:
        return []
    if n == 1:
        return ["Carry"]
    roles = ["Open"] + ["Develop"] * (n - 2) + ["Close"]
    middles = list(range(1, n - 1))
    if middles:
        turn = min(middles, key=lambda i: (modes[i] != "falling", i))
        roles[turn] = "Turn"
    return roles


def cmd_deepen(args) -> int:
    path = state_path(args.file)
    state = load_state(path)
    if state is None:
        return 1

    targets: list[str] = []
    if args.all_stubs:
        by_depth: dict[int, list[str]] = {}
        for node, depth, _parent in walk(nodes_of(state)):
            if (str(node.get("status", "stub")) == "stub"
                    and not (node.get("children") or [])
                    and depth < args.max_depth):
                by_depth.setdefault(depth, []).append(str(node.get("id")))
        if not by_depth:
            print("outline_composer: no stub nodes left to deepen "
                  f"(--max-depth {args.max_depth}).")
            return 0
        targets = by_depth[min(by_depth)]
    elif args.node_id:
        targets = [args.node_id]
    else:
        print("outline_composer: name a NODE_ID or pass --all-stubs.",
              file=sys.stderr)
        return 1

    onto = Ontology()
    pool = build_move_pool(
        onto, MOVE_BRANCHES_BY_KIND.get(
            str((state.get("meta") or {}).get("kind", "")), ()))
    changed = 0
    for node_id in targets:
        rc = deepen_one(state, node_id, pool, args)
        if rc == 1:
            return 1
        changed += 1 if rc == 0 else 0

    if changed:
        save_state(state, path)
        print(f"outline_composer: {changed} node(s) deepened; wrote {path}")
    if onto.missing:
        for name, why in sorted(onto.missing.items()):
            print(f"  skipped   {name}: {why}", file=sys.stderr)
    return 0


def deepen_one(state: dict, node_id: str, pool: list[dict], args) -> int:
    """0 = deepened, 1 = hard error, 2 = skipped."""
    node, depth, _parent = find_node(state, node_id)
    if node is None:
        print(f"outline_composer: no node {node_id!r} in the state file.",
              file=sys.stderr)
        return 1
    if depth >= args.max_depth:
        print(f"outline_composer: {node_id} is at depth {depth}; raise "
              f"--max-depth (currently {args.max_depth}) to go deeper.",
              file=sys.stderr)
        return 1
    if str(node.get("status")) == "locked" and not args.force:
        print(f"outline_composer: {node_id} is locked — pass --force.",
              file=sys.stderr)
        return 1

    existing = node.get("children") or []
    if existing:
        if not args.reroll:
            print(f"outline_composer: {node_id} already has "
                  f"{len(existing)} children — nothing to do "
                  "(pass --reroll to replace them).")
            return 2
        blocked = [str(c.get("id")) for c in existing
                   if isinstance(c, dict)
                   and (c.get("children") or c.get("status") in
                        ("deepened", "locked"))]
        if blocked and not args.force:
            print(f"outline_composer: refusing to reroll {node_id} — "
                  f"{', '.join(blocked)} already deepened or locked "
                  "(pass --force to discard that work).", file=sys.stderr)
            return 1
        # drop promises the discarded subtree owned
        drop = {str(c.get("id")) for c, _d, _p in walk(existing, depth + 1)}
        prune_promises(state, drop)

    seed = (state.get("composer") or {}).get("seed", 0)
    if args.seed_override is not None:
        seed = args.seed_override
    rng = random.Random(f"{seed}:{node_id}")

    n = args.children or (rng.choice((3, 4, 5)) if depth == 1
                          else rng.choice((2, 3)))
    n = max(1, min(int(n), 12))

    start, end = node_span(node)
    span = max(end - start, 0.0)
    curve = (state.get("spine") or {}).get("curve") or []
    weights = [rng.choice((0.8, 0.9, 1.0, 1.0, 1.15, 1.3)) for _ in range(n)]
    total = sum(weights)
    budgets = partition_words(int(node.get("words") or 0), weights)

    # positions tile the parent's span in the same proportions as the words,
    # so a node's share of the book and its share of the page agree
    bounds = [start]
    acc = 0.0
    for w in weights[:-1]:
        acc += w
        bounds.append(round(start + span * acc / total, 6))
    bounds.append(end)

    prefix = child_prefix(depth + 1)
    kind = str((state.get("meta") or {}).get("kind", ""))
    parent_purpose = str(node.get("purpose") or node.get("title") or "")

    kids: list[dict] = []
    modes: list[str] = []
    for i in range(n):
        c0, c1 = bounds[i], bounds[i + 1]
        mid = (c0 + c1) / 2
        valence = curve_at(curve, mid)
        v0, v1 = curve_at(curve, c0), curve_at(curve, c1)
        slope = None if v0 is None or v1 is None else round(v1 - v0, 3)
        modes.append(span_mode(valence, slope))
        kids.append({"start": c0, "end": c1, "valence": valence,
                     "slope": slope, "words": budgets[i]})

    roles = child_roles(n, modes)
    children: list[dict] = []
    for i, k in enumerate(kids):
        cid = f"{node_id}.{prefix}{i + 1:02d}"
        role, mode = roles[i], modes[i]
        crng = random.Random(f"{seed}:{cid}")
        clause = crng.choice(MODE_CLAUSES[mode])
        title = f"{short_title(node.get('title', node_id))} — {role.lower()}"
        if role == "Develop" and n > 3:
            title += f" {i + 1}"
        purpose = f"{role} this span — {clause}."
        served = first_clause(parent_purpose)
        if served:
            purpose += f" Serves the parent beat: {served}"
        child = make_node(cid, title, purpose, k["start"], k["end"],
                          k["words"], k["valence"])
        child["moves"] = conditioned_moves(
            pool, crng, mode, k["valence"], k["slope"], parent_purpose)
        children.append(child)

    node["children"] = children
    node["status"] = "deepened"

    cascade(state, node, children, kids, modes, kind, seed, args)

    spark = sparkline([k["valence"] for k in kids
                       if k["valence"] is not None], *curve_bounds(curve))
    print(f"outline_composer: {node_id} → {n} children "
          f"({', '.join(c['id'].rsplit('.', 1)[-1] for c in children)}) "
          f"· {sum(budgets):,} words" + (f" · {spark}" if spark else ""))
    return 0


def prune_promises(state: dict, dropped: set[str]) -> None:
    """Remove promises owned by deleted nodes; unhook payoffs pointing at them."""
    kept = []
    removed = set()
    for p in state.get("promises") or []:
        if isinstance(p, dict) and str(p.get("opened_by")) in dropped:
            removed.add(str(p.get("id")))
            continue
        kept.append(p)
    for p in kept:
        if isinstance(p, dict) and str(p.get("paid_by")) in dropped:
            p["paid_by"] = None
            p["intentional_open"] = True
    state["promises"] = kept
    for node, _d, _p in walk(nodes_of(state)):
        for key in ("opens", "pays"):
            vals = node.get(key)
            if isinstance(vals, list):
                node[key] = [v for v in vals if str(v) not in removed]


def later_nodes(state: dict, after: float) -> list[dict]:
    return [n for n, _d, _p in walk(nodes_of(state))
            if node_span(n)[0] > after + 1e-9]


PROMISE_TEXT = {
    "question": "What does it cost {who} to {clause}?",
    "forward-ref": "Deferred here, owed later: {clause}.",
    "term": "Term introduced here and owed a working use later: {clause}.",
    "entity": "Planted here and owed a return: {who}.",
}


def cascade(state, parent, children, kids, modes, kind, seed, args) -> None:
    """Entities and promises a deepen introduces, planned forward.

    Every promise opened here is assigned a payer at open time — a later
    sibling, or a later node elsewhere in the tree. The ledger is planned,
    not discovered; setup_payoff.py audits the mirror image in the prose.
    """
    registry = state.setdefault("registry", {})
    entities = registry.setdefault("entities", [])
    onto = Ontology()
    for i, child in enumerate(children):
        crng = random.Random(f"{seed}:{child['id']}:cascade")
        mode = modes[i]
        introduced: list[str] = []

        # a deepen may introduce unnamed cast slots — never proper names,
        # which are the author's to invent
        if kind == "fiction" and crng.random() < 0.25:
            how_many = crng.choice((1, 1, 2))
            roles = onto.pool("character_and_persona",
                              ("function", "role", "stock"))
            picks = crng.sample(roles, min(how_many, len(roles)))
            for e, cat in picks:
                label = cast_slot(wo.entry_name(e))
                if any(str(x.get("name")) == label for x in entities
                       if isinstance(x, dict)):
                    continue
                entities.append({
                    "name": label,
                    "kind": "character",
                    "introduced_at": child["id"],
                    "note": (f"unnamed slot from character_and_persona.{cat}"
                             " — name it when you draft"),
                })
                introduced.append(label)

        candidates = later_nodes(state, node_span(child)[0])
        payer = candidates[0]["id"] if candidates else None
        if len(candidates) > 2:
            payer = crng.choice(candidates[1:]).get("id")

        if introduced:
            for label in introduced:
                p = add_promise(state, child, "entity",
                                PROMISE_TEXT["entity"].format(who=label),
                                paid_by=payer)
                register_payer(state, p, payer)
        elif mode == "falling" and crng.random() < 0.5:
            who = "the argument" if kind == "nonfiction" else "the protagonist"
            clause = first_clause(child.get("purpose", ""), 70)
            p = add_promise(state, child, "question",
                            PROMISE_TEXT["question"].format(
                                who=who, clause=clause[:1].lower() + clause[1:]),
                            paid_by=payer)
            register_payer(state, p, payer)
        elif kind == "nonfiction" and crng.random() < 0.3:
            clause = first_clause(child.get("purpose", ""), 70)
            p = add_promise(state, child, "term",
                            PROMISE_TEXT["term"].format(clause=clause),
                            paid_by=payer)
            register_payer(state, p, payer)
        elif crng.random() < 0.15:
            clause = first_clause(child.get("purpose", ""), 70)
            p = add_promise(state, child, "forward-ref",
                            PROMISE_TEXT["forward-ref"].format(clause=clause),
                            paid_by=payer)
            register_payer(state, p, payer)


def register_payer(state: dict, promise: dict, payer_id) -> None:
    if not payer_id:
        return
    node, _d, _p = find_node(state, str(payer_id))
    if node is None:
        promise["paid_by"] = None
        promise["intentional_open"] = True
        return
    node.setdefault("pays", []).append(promise["id"])


# --------------------------------------------------------------------------
# lint
# --------------------------------------------------------------------------
class Findings:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str]] = []

    def warn(self, where: str, message: str) -> None:
        self.rows.append(("WARN", where, message))

    def info(self, where: str, message: str) -> None:
        self.rows.append(("INFO", where, message))

    @property
    def warnings(self) -> int:
        return sum(1 for tag, _w, _m in self.rows if tag == "WARN")


def cmd_lint(args) -> int:
    path = state_path(args.file)
    state = load_state(path)
    if state is None:
        return 1
    f = lint_state(state)
    width = max((len(w) for _t, w, _m in f.rows), default=0)
    for tag, where, message in f.rows:
        print(f"{tag} {where:<{width}}  {message}")
    total = len(list(walk(nodes_of(state))))
    print(f"outline_composer: {total} node(s), "
          f"{len(state.get('promises') or [])} promise(s), "
          f"{f.warnings} warning(s), "
          f"{len(f.rows) - f.warnings} note(s) — {path}")
    return 1 if (args.strict and f.warnings) else 0


def lint_state(state: dict) -> Findings:  # noqa: C901 - one pass, many rules
    f = Findings()
    meta = state.get("meta") or {}
    registry = state.get("registry") or {}
    curve = (state.get("spine") or {}).get("curve") or []
    kind = str(meta.get("kind", ""))
    if kind not in ("fiction", "nonfiction"):
        f.warn("meta.kind", f"expected fiction|nonfiction, found {kind!r}")
    tense = str(registry.get("tense", ""))
    if tense and tense not in ("past", "present"):
        f.info("registry.tense", f"unusual tense {tense!r}")

    banks = descriptor_bank_names()
    faults = fault_names()
    seen_ids: dict[str, int] = {}
    nodes = nodes_of(state)
    if not nodes:
        f.warn("nodes", "no nodes — run init")

    # --- node tree -------------------------------------------------------
    for node, depth, parent in walk(nodes):
        nid = str(node.get("id", "?"))
        where = f"nodes.{nid}"
        seen_ids[nid] = seen_ids.get(nid, 0) + 1
        if seen_ids[nid] == 2:
            f.warn(where, "duplicate node id")
        if not str(node.get("title", "")).strip():
            f.info(where, "no title")
        status = str(node.get("status", ""))
        if status not in ("stub", "deepened", "locked"):
            f.warn(where, f"unknown status {status!r}")
        kids = node.get("children") or []
        if status == "deepened" and not kids:
            f.warn(where, "status 'deepened' but no children")
        words = node.get("words")
        if not isinstance(words, int) or words <= 0:
            f.warn(where, f"word budget must be a positive integer, "
                          f"found {words!r}")
        s, e = node_span(node)
        if not (0.0 <= s < e <= 1.0 + 1e-9):
            f.warn(where, f"position {node.get('position')!r} is not an "
                          "ordered 0..1 span")
        if parent is not None:
            ps, pe = node_span(parent)
            if s < ps - 1e-6 or e > pe + 1e-6:
                f.warn(where, f"span [{s:.4f}, {e:.4f}] escapes its parent "
                              f"{parent.get('id')} [{ps:.4f}, {pe:.4f}]")
        for key in OVERRIDABLE:
            if key in node and not node.get("override"):
                f.warn(where, f"declares registry slot {key!r} without "
                              "`override: true`")

        # valence against the recorded spine curve
        expected = curve_at(curve, (s + e) / 2)
        val = node.get("valence")
        if expected is not None and isinstance(val, (int, float)):
            if abs(float(val) - expected) > 0.15:
                f.warn(where, f"valence {float(val):+.2f} disagrees with the "
                              f"spine curve at {(s + e) / 2:.2f} "
                              f"({expected:+.2f})")
        elif expected is not None and val is None:
            f.info(where, "no valence recorded although the spine has a curve")

        # children budgets, order, tiling
        real_kids = [k for k in kids if isinstance(k, dict)]
        if real_kids:
            ksum = sum(int(k.get("words") or 0) for k in real_kids)
            parent_words = int(words) if isinstance(words, int) else 0
            if parent_words:
                drift = abs(ksum - parent_words) / parent_words
                if drift > 0.01:
                    f.warn(where, f"children budget {ksum:,} words vs parent "
                                  f"{parent_words:,} ({drift * 100:.1f}% off)")
            cursor = s
            for k in real_kids:
                ks, ke = node_span(k)
                if ks < cursor - 0.005:
                    f.warn(f"nodes.{k.get('id')}", "children overlap or are "
                                                   "out of order")
                elif ks > cursor + 0.005:
                    f.warn(f"nodes.{k.get('id')}", f"gap of "
                           f"{(ks - cursor) * 100:.1f}% before this child")
                cursor = max(cursor, ke)
            if abs(cursor - e) > 0.005:
                f.warn(where, f"children tile to {cursor:.4f}, parent ends "
                              f"at {e:.4f}")

        # moves
        for m in node.get("moves") or []:
            if not isinstance(m, dict):
                f.warn(where, f"move entry is not a mapping: {m!r}")
                continue
            name = str(m.get("name", "")).strip()
            branch = str(m.get("branch", ""))
            if name.lower() in faults:
                f.warn(where, f"move {name!r} names a fault — faults are "
                              "audit targets, never directives")
            if branch in DESCRIPTOR_BANKS or name.lower() in banks:
                f.warn(where, f"move {name!r} comes from a descriptor bank "
                              "— those belong in the setting/tone slots")

    # --- promises --------------------------------------------------------
    pos_of = {str(n.get("id")): node_span(n)
              for n, _d, _p in walk(nodes)}
    for p in state.get("promises") or []:
        if not isinstance(p, dict):
            f.warn("promises", f"entry is not a mapping: {p!r}")
            continue
        pid = str(p.get("id", "?"))
        where = f"promises.{pid}"
        opened = str(p.get("opened_by", ""))
        paid = p.get("paid_by")
        if opened not in pos_of:
            f.warn(where, f"opened_by {opened!r} is not a node")
            continue
        if paid in (None, "", False):
            if not p.get("intentional_open"):
                f.warn(where, "no paid_by and not marked "
                              "`intentional_open: true`")
            continue
        paid = str(paid)
        if paid not in pos_of:
            f.warn(where, f"paid_by {paid!r} is not a node")
            continue
        if pos_of[paid][0] <= pos_of[opened][0] + 1e-9:
            f.warn(where, f"paid_by {paid} sits at or before opened_by "
                          f"{opened} — a promise cannot be paid before "
                          "it is made")

    # --- entities --------------------------------------------------------
    for ent in (state.get("registry") or {}).get("entities") or []:
        if not isinstance(ent, dict):
            continue
        label = str(ent.get("name", "")).strip()
        at = str(ent.get("introduced_at", ""))
        if not label:
            continue
        if at and at not in pos_of:
            f.warn(f"registry.entities.{label}",
                   f"introduced_at {at!r} is not a node")
            continue
        intro = pos_of[at][0] if at in pos_of else 0.0
        needle = label.lower()
        for node, _d, _p in walk(nodes):
            s, _e = node_span(node)
            if s >= intro - 1e-9:
                continue
            hay = " ".join([
                str(node.get("title", "")), str(node.get("purpose", "")),
                " ".join(str(m.get("name", "")) for m in node.get("moves")
                         or [] if isinstance(m, dict)),
            ]).lower()
            if needle in hay:
                f.warn(f"nodes.{node.get('id')}",
                       f"mentions {label!r} before it is introduced at {at}")
    return f


# --------------------------------------------------------------------------
# render / show
# --------------------------------------------------------------------------
# The one canonical serialization. `render --format json` and
# `--format toml` dump THIS dict and nothing else, so the two files always
# describe the same document.
#
# Convention, so a loader never has to distinguish null from missing: a key
# whose value is None, "", [] or {} is omitted entirely. `False` and `0` are
# real values and are kept. TOML has no null, so this is also what makes the
# two formats interchangeable.
def prune(value):
    """Drop None / empty-string / empty-collection keys, recursively."""
    if isinstance(value, dict):
        out = {}
        for key, val in value.items():
            val = prune(val)
            if val is None or val == "" or val == [] or val == {}:
                continue
            out[str(key)] = val
        return out
    if isinstance(value, (list, tuple)):
        return [prune(v) for v in value
                if not (v is None or v == "" or v == [] or v == {})]
    if isinstance(value, float):
        return round(value, 6)
    if isinstance(value, (str, int, bool)):
        return value
    return None if value is None else str(value)


def document(state: dict) -> dict:
    """The resolved, format-independent document: positions and budgets
    normalized, spine valence filled in, empties dropped."""
    spine = state.get("spine") or {}
    curve = spine.get("curve") or []
    total = int((state.get("meta") or {}).get("words") or 0)

    def visit(nodes, depth):
        out = []
        for n in nodes or []:
            if not isinstance(n, dict):
                continue
            s0, e0 = node_span(n)
            words = int(n.get("words") or 0)
            valence = n.get("valence")
            out.append({
                "id": str(n.get("id", "")),
                "depth": depth,
                "title": str(n.get("title", "")),
                "purpose": str(n.get("purpose", "")),
                "position": [round(s0, 6), round(e0, 6)],
                "position_pct": [round(s0 * 100, 3), round(e0 * 100, 3)],
                "words": words,
                "share": round(words / total, 6) if total else None,
                "valence": (round(float(valence), 4)
                            if isinstance(valence, (int, float)) else None),
                "spine_valence": curve_at(curve, (s0 + e0) / 2),
                "status": str(n.get("status", "stub")),
                "moves": [
                    {
                        "name": str(m.get("name", "")),
                        "branch": str(m.get("branch", "")),
                        "category": str(m.get("category", "")),
                        "definition": str(m.get("definition", "")),
                        "why": str(m.get("why", "")),
                    }
                    for m in (n.get("moves") or []) if isinstance(m, dict)
                ],
                "opens": [str(p) for p in (n.get("opens") or [])],
                "pays": [str(p) for p in (n.get("pays") or [])],
                "children": visit(n.get("children") or [], depth + 1),
            })
        return out

    promises = []
    for pr in state.get("promises") or []:
        if not isinstance(pr, dict):
            continue
        promises.append({
            "id": str(pr.get("id", "")),
            "kind": str(pr.get("kind", "")),
            "text": str(pr.get("text", "")),
            "opened_by": str(pr.get("opened_by", "")),
            "paid_by": (str(pr["paid_by"]) if pr.get("paid_by") else None),
            "intentional_open": bool(pr.get("intentional_open")),
        })

    doc = {
        "composer": dict(state.get("composer") or {}),
        "meta": dict(state.get("meta") or {}),
        "registry": dict(state.get("registry") or {}),
        "spine": {
            "template": dict(spine.get("template") or {}),
            "arc": dict(spine.get("arc") or {}) if spine.get("arc") else None,
            "definition": spine.get("definition") or "",
            "note": spine.get("note") or "",
            "curve": [[round(float(pt[0]), 6), round(float(pt[1]), 6)]
                      for pt in clean_curve(curve)],
            "beats": [dict(b) for b in (spine.get("beats") or [])
                      if isinstance(b, dict)],
        },
        "nodes": visit(nodes_of(state), 1),
        "promises": promises,
    }
    return prune(doc)


def render_json(state: dict) -> str:
    return json.dumps(document(state), indent=2, ensure_ascii=False,
                      sort_keys=False)


def render_toml(state: dict) -> str:
    """Same document as --format json. Nested nodes become arrays of tables
    ([[nodes]], [[nodes.children]]); tomli-w orders scalars before tables.

    Imported lazily: stdlib `tomllib` reads TOML but cannot write it, and
    only this one output family needs the writer."""
    try:
        import tomli_w
    except ImportError as exc:  # pragma: no cover - environment problem
        raise SystemExit(
            "outline_composer: --format toml needs tomli-w. Run the script "
            "with `uv run scripts/outline_composer.py` (PEP 723 handles it) "
            "or install the project's `compose` dependency group."
        ) from exc
    return tomli_w.dumps(document(state), multiline_strings=False).rstrip("\n")


def render_markdown(state: dict) -> str:
    meta = state.get("meta") or {}
    comp = state.get("composer") or {}
    spine = state.get("spine") or {}
    tpl = spine.get("template") or {}
    curve = spine.get("curve") or []
    total = int(meta.get("words") or 0)
    title = str(meta.get("title") or "").strip() or "Untitled"

    lines = [f"# Outline — {title}", ""]
    if meta.get("premise"):
        lines += [f"*{meta['premise']}*", ""]
    src = f"{tpl.get('branch', '?')}.{tpl.get('category', '?')}"
    lines.append(
        f"{meta.get('kind', '?')} · spine **{tpl.get('name', '?')}** "
        f"(`{src}`, {tpl.get('source', '?')}) · target {total:,} words · "
        f"seed {comp.get('seed', '?')}")
    if spine.get("definition"):
        lines.append("")
        lines.append(f"> {spine['definition']}")
    arc = spine.get("arc")
    if isinstance(arc, dict) and arc.get("name"):
        lines.append("")
        lines.append(f"Arc: **{arc['name']}** "
                     f"(`{arc.get('branch')}.{arc.get('category')}`)")
    if curve:
        samples = [curve_at(curve, i / 23) for i in range(24)]
        vals = [v for v in samples if v is not None]
        if vals:
            lines += ["", f"Spine curve `{sparkline(samples)}` "
                          f"({min(vals):+.2f} … {max(vals):+.2f})"]
    if spine.get("note"):
        lines += ["", f"Note: {spine['note']}."]
    lines.append("")

    def visit(nodes, depth):
        nonlocal lines
        for n in nodes or []:
            if not isinstance(n, dict):
                continue
            s, e = node_span(n)
            hashes = "#" * min(depth + 1, 6)
            lines.append(f"{hashes} `{n.get('id')}` {n.get('title', '')}")
            lines.append("")
            bits = [f"{s * 100:.1f}–{e * 100:.1f}%",
                    f"~{int(n.get('words') or 0):,} words"]
            val = n.get("valence")
            if isinstance(val, (int, float)):
                spark = sparkline(
                    [curve_at(curve, s + (e - s) * i / 4) for i in range(5)],
                    *curve_bounds(curve))
                bits.append(f"valence {float(val):+.2f} `{spark}`")
            bits.append(str(n.get("status", "stub")))
            lines.append("**" + "** · **".join(bits) + "**")
            if n.get("purpose"):
                lines += ["", str(n["purpose"])]
            moves = [m for m in n.get("moves") or [] if isinstance(m, dict)]
            if moves:
                lines += ["", "*Moves to reach for*"]
                for m in moves:
                    defn = f" — {m['definition']}" if m.get("definition") \
                        else ""
                    lines.append(
                        f"- {m.get('name')}{defn}  "
                        f"`[{m.get('branch')}.{m.get('category')}]`")
            debts = []
            if n.get("opens"):
                debts.append("opens " + ", ".join(str(p) for p in n["opens"]))
            if n.get("pays"):
                debts.append("pays " + ", ".join(str(p) for p in n["pays"]))
            if debts:
                lines += ["", "*Ledger*: " + " · ".join(debts)]
            lines.append("")
            visit(n.get("children") or [], depth + 1)

    visit(nodes_of(state), 1)

    promises = [p for p in state.get("promises") or [] if isinstance(p, dict)]
    if promises:
        lines += ["## Promise ledger", "",
                  "| id | kind | opened by | paid by | promise |",
                  "|---|---|---|---|---|"]
        for p in promises:
            paid = p.get("paid_by") or (
                "*open by design*" if p.get("intentional_open") else "—")
            text = str(p.get("text", "")).replace("|", "\\|")
            lines.append(f"| {p.get('id')} | {p.get('kind')} | "
                         f"{p.get('opened_by')} | {paid} | {text} |")
        lines.append("")

    registry = state.get("registry") or {}
    if registry:
        lines += ["## Registry", ""]
        for key, val in registry.items():
            if key == "entities":
                continue
            lines.append(f"- **{key}** — {registry_line(val)}")
        entities = registry.get("entities") or []
        if entities:
            lines += ["", "### Entities", ""]
            for ent in entities:
                if not isinstance(ent, dict):
                    continue
                lines.append(
                    f"- **{ent.get('name')}** ({ent.get('kind')}) — "
                    f"introduced at `{ent.get('introduced_at')}`"
                    + (f"; {ent['note']}" if ent.get("note") else ""))
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"<!-- outline_composer: seed {comp.get('seed')}; "
                 f"state {DEFAULT_STATE.as_posix()}; "
                 "regenerate with `outline_composer.py render` -->")
    return "\n".join(lines)


def registry_line(val) -> str:
    if isinstance(val, dict):
        out = str(val.get("name", ""))
        if val.get("definition"):
            out += f" — {val['definition']}"
        if val.get("source"):
            out += f"  `[{val['source']}]`"
        return out
    if isinstance(val, list):
        return "; ".join(registry_line(v) for v in val)
    return str(val)


# --------------------------------------------------------------------------
# html — one self-contained static page: inline CSS tokens, inline SVG,
# no scripts, no network requests of any kind.
# --------------------------------------------------------------------------
HTML_CSS = """
:root{
  --bg:#ffffff; --surface:#ffffff; --surface-2:#f8fafc; --surface-3:#f1f5f9;
  --border:#e2e8f0; --border-strong:#cbd5e1;
  --text:#0f172a; --muted:#64748b; --faint:#94a3b8;
  --accent:#4f46e5; --accent-soft:#eef2ff; --accent-text:#4338ca;
  --pos:#059669; --pos-soft:#ecfdf5; --neg:#dc2626; --neg-soft:#fef2f2;
  --amber:#b45309; --amber-soft:#fffbeb;
  --shadow:0 1px 2px rgba(15,23,42,.06), 0 8px 24px -12px rgba(15,23,42,.18);
  --radius:14px;
  --sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;
}
@media (prefers-color-scheme: dark){
  :root{
    --bg:#0b1120; --surface:#111827; --surface-2:#0f172a; --surface-3:#1e293b;
    --border:#1e293b; --border-strong:#334155;
    --text:#e2e8f0; --muted:#94a3b8; --faint:#64748b;
    --accent:#818cf8; --accent-soft:#1e1b4b; --accent-text:#c7d2fe;
    --pos:#34d399; --pos-soft:#052e2b; --neg:#f87171; --neg-soft:#3f1d1d;
    --amber:#fbbf24; --amber-soft:#3a2a06;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -12px rgba(0,0,0,.6);
  }
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0; background:var(--bg); color:var(--text);
  font-family:var(--sans); font-size:16px; line-height:1.6;
  overflow-x:hidden;
}
.wrap{max-width:70rem;margin:0 auto;padding:2.5rem 1.25rem 5rem}
a{color:var(--accent-text);text-decoration:none}
a:hover{text-decoration:underline}
h1,h2,h3{line-height:1.25;margin:0}
h1{font-size:2rem;letter-spacing:-.02em;font-weight:700}
h2{font-size:1.15rem;letter-spacing:-.01em;font-weight:650;margin:2.75rem 0 1rem}
h2 .rule{display:block;height:1px;background:var(--border);margin-top:.6rem}
.premise{color:var(--muted);font-size:1.05rem;margin:.65rem 0 0;font-style:italic}
.chips{display:flex;flex-wrap:wrap;gap:.45rem;margin-top:1.1rem}
.chip{
  display:inline-flex;align-items:center;gap:.35rem;
  padding:.2rem .6rem;border-radius:999px;font-size:.78rem;font-weight:550;
  background:var(--surface-3);color:var(--muted);border:1px solid var(--border);
  white-space:nowrap;
}
.chip b{color:var(--text);font-weight:650}
.chip--accent{background:var(--accent-soft);color:var(--accent-text);border-color:transparent}
.card{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--radius);box-shadow:var(--shadow);padding:1.35rem 1.5rem;
}
.chart{padding:1.1rem 1.1rem .5rem;overflow-x:auto}
.chart svg{display:block;width:100%;height:auto;min-width:34rem;color:var(--muted)}
.chart figcaption{color:var(--faint);font-size:.78rem;margin:.35rem .25rem 0}
.tree{margin-top:.25rem}
.node{
  border-left:2px solid var(--border);padding:0 0 0 1.1rem;margin:1rem 0 0;
}
.node > .node-body{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--radius);padding:.95rem 1.15rem;box-shadow:var(--shadow);
}
.node--d1{border-left-color:var(--accent)}
.node--d1 > .node-body{background:var(--surface)}
.node--d2 > .node-body{background:var(--surface-2)}
.node--d3 > .node-body{background:var(--surface-2)}
.node-head{display:flex;flex-wrap:wrap;align-items:center;gap:.5rem}
.id{
  font-family:var(--mono);font-size:.76rem;font-weight:600;
  background:var(--surface-3);border:1px solid var(--border);
  padding:.1rem .42rem;border-radius:6px;color:var(--muted);
}
.node-title{font-weight:650;font-size:1rem;letter-spacing:-.01em}
.node--d1 .node-title{font-size:1.12rem}
.spacer{flex:1 1 auto}
.metric{font-size:.78rem;color:var(--muted);white-space:nowrap}
.metric b{color:var(--text);font-weight:600}
.pill{
  font-size:.7rem;font-weight:650;text-transform:uppercase;letter-spacing:.04em;
  padding:.14rem .5rem;border-radius:999px;border:1px solid transparent;
}
.pill--stub{background:var(--surface-3);color:var(--muted);border-color:var(--border)}
.pill--deepened{background:var(--accent-soft);color:var(--accent-text)}
.pill--locked{background:var(--amber-soft);color:var(--amber)}
.vbar{
  position:relative;display:inline-block;width:96px;height:9px;flex:0 0 auto;
  background:var(--surface-3);border-radius:999px;overflow:hidden;
  border:1px solid var(--border);
}
.vbar::after{content:"";position:absolute;left:50%;top:0;bottom:0;width:1px;background:var(--border-strong)}
.vfill{position:absolute;top:0;bottom:0;border-radius:999px}
.vfill--pos{background:var(--pos)}
.vfill--neg{background:var(--neg)}
.purpose{margin:.6rem 0 0;color:var(--text)}
.moves{list-style:none;margin:.7rem 0 0;padding:0;display:grid;gap:.4rem}
.moves li{
  font-size:.9rem;color:var(--muted);
  padding-left:.9rem;position:relative;
}
.moves li::before{content:"";position:absolute;left:0;top:.62em;width:5px;height:5px;border-radius:50%;background:var(--accent);opacity:.65}
.moves .mname{color:var(--text);font-weight:600}
.tag{
  font-family:var(--mono);font-size:.7rem;color:var(--faint);
  background:var(--surface-3);border-radius:5px;padding:.05rem .3rem;
  white-space:nowrap;
}
.ledger-chips{display:flex;flex-wrap:wrap;gap:.35rem;margin-top:.7rem}
.pchip{
  font-family:var(--mono);font-size:.72rem;font-weight:600;
  padding:.12rem .45rem;border-radius:6px;border:1px solid var(--border);
  background:var(--surface-3);color:var(--muted);
}
.pchip--opens{background:var(--amber-soft);color:var(--amber);border-color:transparent}
.pchip--pays{background:var(--pos-soft);color:var(--pos);border-color:transparent}
details.node-children{margin:0}
details.node-children > summary{
  cursor:pointer;list-style:none;font-size:.8rem;color:var(--muted);
  padding:.45rem 0 0 1.1rem;user-select:none;
}
details.node-children > summary::-webkit-details-marker{display:none}
details.node-children > summary::before{content:"▸ ";color:var(--faint)}
details.node-children[open] > summary::before{content:"▾ "}
.table-wrap{overflow-x:auto;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);box-shadow:var(--shadow)}
table{border-collapse:collapse;width:100%;min-width:44rem;font-size:.88rem}
th,td{text-align:left;padding:.6rem .85rem;border-bottom:1px solid var(--border);vertical-align:top}
thead th{
  font-size:.72rem;text-transform:uppercase;letter-spacing:.06em;
  color:var(--faint);font-weight:650;background:var(--surface-2);
}
tbody tr:last-child td{border-bottom:none}
tbody tr:target{background:var(--accent-soft)}
td.mono,th.mono{font-family:var(--mono);font-size:.8rem;white-space:nowrap}
.open-by-design{color:var(--faint);font-style:italic}
.reg{display:grid;gap:.55rem;margin:0;padding:0}
.reg div{display:grid;grid-template-columns:minmax(7rem,10rem) 1fr;gap:.75rem;align-items:baseline}
.reg dt{color:var(--muted);font-size:.82rem;text-transform:uppercase;letter-spacing:.05em;font-weight:650}
.reg dd{margin:0}
.reg .defn{color:var(--muted)}
@media (max-width:640px){
  .wrap{padding:1.75rem 1rem 4rem}
  h1{font-size:1.55rem}
  .reg div{grid-template-columns:1fr;gap:.15rem}
  .node{padding-left:.7rem}
}
footer{margin-top:3rem;color:var(--faint);font-size:.78rem;border-top:1px solid var(--border);padding-top:1rem}
"""


def esc(text) -> str:
    return _html.escape(str(text), quote=True)


def node_anchor(node_id: str) -> str:
    return "node-" + str(node_id)


def svg_arc(curve, boundaries, labels) -> str:
    """Inline SVG of the spine curve, with chapter-boundary ticks."""
    pts = clean_curve(curve)
    if len(pts) < 2:
        return ""
    w, h = 880.0, 250.0
    ml, mr, mt, mb = 46.0, 18.0, 20.0, 30.0
    iw, ih = w - ml - mr, h - mt - mb

    def px(pos: float) -> float:
        return round(ml + pos * iw, 2)

    def py(val: float) -> float:
        return round(mt + (1.0 - (max(-1.0, min(1.0, val)) + 1.0) / 2.0) * ih, 2)

    zero = py(0.0)
    line = " ".join(f"{px(p)},{py(v)}" for p, v in pts)
    area = (f"M {px(pts[0][0])},{zero} L "
            + " L ".join(f"{px(p)},{py(v)}" for p, v in pts)
            + f" L {px(pts[-1][0])},{zero} Z")

    out = [
        f'<svg viewBox="0 0 {w:g} {h:g}" role="img"',
        ' aria-label="Spine valence curve across the length of the book">',
        '<defs><linearGradient id="arcfill" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0%" style="stop-color:var(--accent)" stop-opacity=".30"/>',
        '<stop offset="100%" style="stop-color:var(--accent)" stop-opacity=".02"/>',
        "</linearGradient></defs>",
    ]
    # horizontal guides at +1 / 0 / -1
    for val, dash in ((1.0, "3 4"), (0.0, ""), (-1.0, "3 4")):
        y = py(val)
        stroke = "var(--border-strong)" if val == 0 else "var(--border)"
        out.append(
            f'<line x1="{ml:g}" y1="{y}" x2="{w - mr:g}" y2="{y}" '
            f'style="stroke:{stroke}" stroke-width="1"'
            + (f' stroke-dasharray="{dash}"' if dash else "") + "/>")
        out.append(
            f'<text x="{ml - 8:g}" y="{y + 4}" text-anchor="end" '
            f'font-size="11" style="fill:var(--faint)">{val:+.0f}</text>')
    # chapter boundaries
    for pos in boundaries:
        x = px(pos)
        out.append(f'<line x1="{x}" y1="{mt:g}" x2="{x}" y2="{mt + ih:g}" '
                   'style="stroke:var(--border)" stroke-width="1" '
                   'stroke-dasharray="2 5"/>')
    # the curve
    out.append(f'<path d="{area}" fill="url(#arcfill)"/>')
    out.append(f'<polyline points="{line}" '
               'style="fill:none;stroke:var(--accent)" stroke-width="2.5" '
               'stroke-linejoin="round" stroke-linecap="round"/>')
    for p, v in pts:
        out.append(f'<circle cx="{px(p)}" cy="{py(v)}" r="3.5" '
                   'style="fill:var(--surface);stroke:var(--accent)" '
                   'stroke-width="2"/>')
    # node midpoint markers
    for pos in labels:
        val = curve_at(curve, pos)
        if val is None:
            continue
        out.append(f'<circle cx="{px(pos)}" cy="{py(val)}" r="2" '
                   'style="fill:var(--muted)" opacity=".55"/>')
    for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
        anchor = ("start" if frac == 0 else
                  "end" if frac == 1 else "middle")
        out.append(
            f'<text x="{px(frac)}" y="{mt + ih + 18:g}" '
            f'text-anchor="{anchor}" font-size="11" '
            f'style="fill:var(--faint)">{frac * 100:.0f}%</text>')
    out.append("</svg>")
    return "".join(out)


def html_valence_bar(valence) -> str:
    if not isinstance(valence, (int, float)):
        return ""
    v = max(-1.0, min(1.0, float(valence)))
    width = abs(v) * 50.0
    left = 50.0 if v >= 0 else 50.0 - width
    cls = "vfill--pos" if v >= 0 else "vfill--neg"
    return (f'<span class="vbar" role="img" aria-label="valence {v:+.2f}">'
            f'<span class="vfill {cls}" style="left:{left:.2f}%;'
            f'width:{width:.2f}%"></span></span>')


def html_nodes(nodes, out: list, depth: int = 1) -> None:
    for n in nodes:
        nid = str(n.get("id", ""))
        klass = f"node node--d{min(depth, 3)}"
        out.append(f'<section class="{klass}" id="{esc(node_anchor(nid))}">')
        out.append('<div class="node-body">')
        out.append('<div class="node-head">')
        out.append(f'<span class="id">{esc(nid)}</span>')
        out.append(f'<span class="node-title">{esc(n.get("title", ""))}</span>')
        out.append('<span class="spacer"></span>')
        start, end = (n.get("position_pct") or [0, 0])[:2]
        out.append(f'<span class="metric">{start:g}–{end:g}%</span>')
        out.append(f'<span class="metric"><b>{int(n.get("words") or 0):,}</b>'
                   " words</span>")
        valence = n.get("valence")
        if isinstance(valence, (int, float)):
            out.append(html_valence_bar(valence))
            out.append(f'<span class="metric">{float(valence):+.2f}</span>')
        status = str(n.get("status", "stub"))
        out.append(f'<span class="pill pill--{esc(status)}">{esc(status)}'
                   "</span>")
        out.append("</div>")
        if n.get("purpose"):
            out.append(f'<p class="purpose">{esc(n["purpose"])}</p>')
        moves = n.get("moves") or []
        if moves:
            out.append('<ul class="moves">')
            for m in moves:
                defn = (" — " + esc(m["definition"])) if m.get("definition") \
                    else ""
                tag = ".".join(x for x in (m.get("branch"), m.get("category"))
                               if x)
                out.append(f'<li><span class="mname">{esc(m.get("name", ""))}'
                           f"</span>{defn} "
                           f'<span class="tag">{esc(tag)}</span></li>')
            out.append("</ul>")
        chips = []
        for pid in n.get("opens") or []:
            chips.append(f'<a class="pchip pchip--opens" href="#{esc(pid)}">'
                         f"opens {esc(pid)}</a>")
        for pid in n.get("pays") or []:
            chips.append(f'<a class="pchip pchip--pays" href="#{esc(pid)}">'
                         f"pays {esc(pid)}</a>")
        if chips:
            out.append('<div class="ledger-chips">' + "".join(chips) + "</div>")
        out.append("</div>")
        kids = n.get("children") or []
        if kids:
            if depth >= 2:
                out.append('<details class="node-children" open>')
                out.append(f"<summary>{len(kids)} child node(s)</summary>")
                html_nodes(kids, out, depth + 1)
                out.append("</details>")
            else:
                html_nodes(kids, out, depth + 1)
        out.append("</section>")


def html_registry(registry: dict, out: list) -> None:
    rows = []
    for key, val in registry.items():
        if key == "entities":
            continue
        rows.append((key, val))
    if rows:
        out.append('<dl class="reg">')
        for key, val in rows:
            out.append("<div>")
            out.append(f"<dt>{esc(key.replace('_', ' '))}</dt>")
            out.append(f"<dd>{html_registry_value(val)}</dd>")
            out.append("</div>")
        out.append("</dl>")
    entities = registry.get("entities") or []
    if entities:
        out.append('<h3 style="margin:1.75rem 0 .75rem;font-size:.95rem">'
                   "Entities</h3>")
        out.append('<div class="table-wrap"><table><thead><tr>'
                   "<th>Name</th><th>Kind</th><th>Introduced at</th>"
                   "<th>Note</th></tr></thead><tbody>")
        for ent in entities:
            if not isinstance(ent, dict):
                continue
            at = str(ent.get("introduced_at", ""))
            link = (f'<a href="#{esc(node_anchor(at))}">{esc(at)}</a>'
                    if at else "")
            out.append(f"<tr><td><b>{esc(ent.get('name', ''))}</b></td>"
                       f"<td>{esc(ent.get('kind', ''))}</td>"
                       f'<td class="mono">{link}</td>'
                       f"<td>{esc(ent.get('note', ''))}</td></tr>")
        out.append("</tbody></table></div>")


def html_registry_value(val) -> str:
    if isinstance(val, dict):
        parts = [f"<b>{esc(val.get('name', ''))}</b>"]
        if val.get("definition"):
            parts.append(f'<span class="defn"> — {esc(val["definition"])}'
                         "</span>")
        if val.get("source"):
            parts.append(f' <span class="tag">{esc(val["source"])}</span>')
        return "".join(parts)
    if isinstance(val, list):
        return " · ".join(html_registry_value(v) for v in val)
    return esc(val)


def render_html(state: dict) -> str:
    doc = document(state)
    meta = doc.get("meta") or {}
    comp = doc.get("composer") or {}
    spine = doc.get("spine") or {}
    tpl = spine.get("template") or {}
    arc = spine.get("arc") or {}
    curve = spine.get("curve") or []
    nodes = doc.get("nodes") or []
    title = str(meta.get("title") or "").strip() or "Untitled outline"

    out: list[str] = [
        "<!doctype html>",
        '<html lang="en"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        '<meta name="color-scheme" content="light dark">',
        '<meta name="generator" content="outline_composer.py">',
        f"<title>Outline — {esc(title)}</title>",
        f"<style>{HTML_CSS}</style>",
        "</head><body><div class=\"wrap\">",
        "<header>",
        f"<h1>{esc(title)}</h1>",
    ]
    if meta.get("premise"):
        out.append(f'<p class="premise">{esc(meta["premise"])}</p>')
    chips = [
        f'<span class="chip chip--accent">{esc(meta.get("kind", "?"))}</span>',
        f'<span class="chip">spine <b>{esc(tpl.get("name", "?"))}</b></span>',
    ]
    if arc.get("name"):
        chips.append(f'<span class="chip">arc <b>{esc(arc["name"])}</b></span>')
    chips.append('<span class="chip">target '
                 f'<b>{int(meta.get("words") or 0):,}</b> words</span>')
    chips.append(f'<span class="chip">{len(nodes)} chapters</span>')
    chips.append(f'<span class="chip">seed <b>{esc(comp.get("seed", "?"))}'
                 "</b></span>")
    out.append('<div class="chips">' + "".join(chips) + "</div>")
    if spine.get("definition"):
        out.append(f'<p class="premise" style="font-style:normal">'
                   f'{esc(spine["definition"])}</p>')
    out.append("</header>")

    if curve:
        boundaries = [float(n["position"][0]) for n in nodes
                      if n.get("position")][1:]
        mids = [(float(n["position"][0]) + float(n["position"][1])) / 2
                for n in nodes if n.get("position")]
        svg = svg_arc(curve, boundaries, mids)
        if svg:
            out.append('<h2>Arc<span class="rule"></span></h2>')
            out.append('<figure class="card chart" style="margin:0">')
            out.append(svg)
            caption = "Spine valence over the length of the book"
            if arc.get("name"):
                caption += f" — {arc['name']}"
            caption += "; dashed verticals are chapter boundaries."
            out.append(f"<figcaption>{esc(caption)}</figcaption>")
            out.append("</figure>")

    out.append('<h2>Outline<span class="rule"></span></h2>')
    out.append('<div class="tree">')
    html_nodes(nodes, out, 1)
    out.append("</div>")

    promises = doc.get("promises") or []
    if promises:
        out.append('<h2 id="ledger">Promise ledger<span class="rule"></span>'
                   "</h2>")
        out.append('<div class="table-wrap"><table><thead><tr>'
                   '<th class="mono">id</th><th>Kind</th>'
                   '<th class="mono">Opened by</th>'
                   '<th class="mono">Paid by</th><th>Promise</th>'
                   "</tr></thead><tbody>")
        for pr in promises:
            pid = str(pr.get("id", ""))
            opened = str(pr.get("opened_by", ""))
            paid = pr.get("paid_by")
            paid_cell = (
                f'<a href="#{esc(node_anchor(str(paid)))}">{esc(paid)}</a>'
                if paid else
                '<span class="open-by-design">open by design</span>'
                if pr.get("intentional_open") else "—")
            out.append(
                f'<tr id="{esc(pid)}"><td class="mono">{esc(pid)}</td>'
                f"<td>{esc(pr.get('kind', ''))}</td>"
                f'<td class="mono">'
                f'<a href="#{esc(node_anchor(opened))}">{esc(opened)}</a></td>'
                f'<td class="mono">{paid_cell}</td>'
                f"<td>{esc(pr.get('text', ''))}</td></tr>")
        out.append("</tbody></table></div>")

    registry = doc.get("registry") or {}
    if registry:
        out.append('<h2>Registry<span class="rule"></span></h2>')
        html_registry(registry, out)

    out.append("<footer>")
    out.append(
        f"Generated by outline_composer.py from "
        f"<code>{esc(DEFAULT_STATE.as_posix())}</code> · seed "
        f"<b>{esc(comp.get('seed', '?'))}</b>")
    if comp.get("reproduce"):
        out.append(f"<br><code>{esc(comp['reproduce'])}</code>")
    out.append("</footer>")
    out.append("</div></body></html>")
    return "\n".join(out)


RENDERERS = {
    "md": render_markdown,
    "json": render_json,
    "toml": render_toml,
    "html": render_html,
}


def cmd_render(args) -> int:
    path = state_path(args.file)
    state = load_state(path)
    if state is None:
        return 1
    fmt = args.format
    if args.json:
        # kept for back-compat; --format json is the spelling now
        if fmt not in (None, "json"):
            print(f"outline_composer: --json contradicts --format {fmt}; "
                  "using json.", file=sys.stderr)
        fmt = "json"
    fmt = fmt or "md"
    text = RENDERERS[fmt](state)
    if args.out:
        out = Path(args.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
        print(f"outline_composer: wrote {out}")
    else:
        print(text)
    return 0


def cmd_show(args) -> int:
    path = state_path(args.file)
    state = load_state(path)
    if state is None:
        return 1
    curve = (state.get("spine") or {}).get("curve") or []
    if args.node_id:
        node, depth, parent = find_node(state, args.node_id)
        if node is None:
            print(f"outline_composer: no node {args.node_id!r}.",
                  file=sys.stderr)
            return 1
        s, e = node_span(node)
        print(f"{node.get('id')}  {node.get('title', '')}")
        print(f"  depth     {depth}"
              + (f"  (child of {parent.get('id')})" if parent else ""))
        print(f"  position  {s * 100:.1f}–{e * 100:.1f}%")
        print(f"  words     {int(node.get('words') or 0):,}")
        print(f"  valence   {node.get('valence')}  "
              f"(spine {curve_at(curve, (s + e) / 2)})")
        print(f"  status    {node.get('status')}")
        if node.get("purpose"):
            print(f"  purpose   {node['purpose']}")
        for m in node.get("moves") or []:
            if isinstance(m, dict):
                print(f"  move      {m.get('name')}  "
                      f"[{m.get('branch')}.{m.get('category')}] — "
                      f"{m.get('why', '')}")
        if node.get("opens"):
            print(f"  opens     {', '.join(str(p) for p in node['opens'])}")
        if node.get("pays"):
            print(f"  pays      {', '.join(str(p) for p in node['pays'])}")
        for child in node.get("children") or []:
            if isinstance(child, dict):
                print(f"  child     {child.get('id')}  "
                      f"{child.get('title', '')}")
        return 0

    meta = state.get("meta") or {}
    print(f"{meta.get('kind', '?')} · {int(meta.get('words') or 0):,} words · "
          f"spine {(state.get('spine') or {}).get('template', {}).get('name')}"
          f" · seed {(state.get('composer') or {}).get('seed')}")
    for node, depth, _parent in walk(nodes_of(state)):
        s, e = node_span(node)
        val = node.get("valence")
        vtxt = f"{float(val):+.2f}" if isinstance(val, (int, float)) else "   ·"
        label = f"{'  ' * (depth - 1)}{node.get('id')}"
        print(f"{label:<26}"
              f"{s * 100:5.1f}–{e * 100:5.1f}%  "
              f"{int(node.get('words') or 0):>7,}w  {vtxt}  "
              f"{node.get('status', ''):<9} {node.get('title', '')}")
    return 0


# --------------------------------------------------------------------------
# set — the small escape hatch; hand-editing the YAML is the primary path
# --------------------------------------------------------------------------
SETTABLE_ROOTS = ("registry", "meta")


def cmd_set(args) -> int:
    path = state_path(args.file)
    state = load_state(path)
    if state is None:
        return 1
    spec = args.assignment
    key, sep, value = spec.partition("=")
    key, value = key.strip(), value.strip()
    if not sep or not key:
        print(f"outline_composer: bad assignment {spec!r}; expected "
              "PATH=VALUE, e.g. registry.tense=present", file=sys.stderr)
        return 1
    parts = key.split(".")
    if parts[0] not in SETTABLE_ROOTS or len(parts) != 2:
        print(f"outline_composer: `set` handles {'/'.join(SETTABLE_ROOTS)} "
              "scalars only (e.g. registry.tense=present, meta.words=90000). "
              "Edit the YAML directly for anything else, then run `lint`.",
              file=sys.stderr)
        return 1
    root, leaf = parts
    section = state.setdefault(root, {})
    if not isinstance(section, dict):
        print(f"outline_composer: {root} is not a mapping.", file=sys.stderr)
        return 1

    if leaf == "words":
        if not value.isdigit() or int(value) <= 0:
            print("outline_composer: meta.words must be a positive integer.",
                  file=sys.stderr)
            return 1
        section[leaf] = int(value)
    elif leaf == "tense":
        if value not in ("past", "present"):
            print("outline_composer: registry.tense must be past or present.",
                  file=sys.stderr)
            return 1
        section[leaf] = value
    elif leaf == "kind":
        if value not in ("fiction", "nonfiction"):
            print("outline_composer: meta.kind must be fiction or nonfiction.",
                  file=sys.stderr)
            return 1
        section[leaf] = value
    else:
        old = section.get(leaf)
        section[leaf] = ({"name": value, "source": "manual"}
                         if isinstance(old, dict) else value)
    save_state(state, path)
    print(f"outline_composer: {key} = {registry_line(section[leaf])}")
    if leaf == "words":
        print("  note: node budgets are NOT rescaled — run `lint` to see the "
              "drift, then reroll or edit the tree.")
    return 0


# --------------------------------------------------------------------------
# templates listing
# --------------------------------------------------------------------------
def cmd_list_templates(kind: str | None) -> int:
    onto = Ontology()
    templates = discover(onto)
    if kind:
        templates = eligible(templates, kind)
    if not templates:
        print(f"outline_composer: no spine templates found in "
              f"{wo.ONTOLOGY_DIR}"
              + (f" for kind {kind}" if kind else "") + ".")
        return 0
    width = max(len(t["name"]) for t in templates)
    print(f"{'template':<{width}}  kind    n  source")
    print("-" * (width + 24))
    for t in templates:
        print(f"{t['name']:<{width}}  {t['source']:<6} {t['size']:>2}  "
              f"{t['branch']}.{t['category']}")
    print()
    print(f"{len(templates)} template(s)"
          + (f" eligible for {kind}" if kind else "")
          + "; name one with --template.")
    return 0


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def add_file_arg(p: argparse.ArgumentParser) -> None:
    p.add_argument("--file", metavar="PATH",
                   help=f"state file (default: {DEFAULT_STATE.as_posix()})")


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="outline_composer.py",
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--list-templates", action="store_true",
                    help="list ontology records usable as a spine and exit")
    ap.add_argument("--kind", choices=("fiction", "nonfiction"),
                    help="with --list-templates: restrict to one kind")
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("init", help="roll the registry, spine and level-1 nodes")
    p.add_argument("--kind", choices=("fiction", "nonfiction"), required=True)
    p.add_argument("--title", default="")
    p.add_argument("--premise", default="")
    p.add_argument("--words", type=int, required=True,
                   help="target length of the whole work")
    p.add_argument("--seed", type=int, default=None,
                   help="reproducible composition (printed if omitted)")
    p.add_argument("--template", metavar="NAME",
                   help="spine template (exact, slug, or substring)")
    p.add_argument("--arc", metavar="NAME",
                   help="valence curve to run under the spine "
                        "(default: seeded, when the spine carries no curve)")
    p.add_argument("--chapters", type=int, default=None,
                   help="redistribute the spine's beats into N chapters")
    p.add_argument("--force", action="store_true",
                   help="overwrite an existing state file")
    add_file_arg(p)

    p = sub.add_parser("deepen", help="expand one node (or every shallow stub)")
    p.add_argument("node_id", nargs="?", metavar="NODE_ID")
    p.add_argument("--all-stubs", action="store_true",
                   help="deepen every stub at the shallowest incomplete level")
    p.add_argument("--children", type=int, default=None,
                   help="how many children (default: seeded 3-5, then 2-3)")
    p.add_argument("--max-depth", type=int, default=3,
                   help="deepest level this command will create (default: 3)")
    p.add_argument("--reroll", action="store_true",
                   help="replace existing children")
    p.add_argument("--force", action="store_true",
                   help="with --reroll: discard deepened or locked children")
    p.add_argument("--seed-override", type=int, default=None,
                   help="reroll this node from a different seed")
    add_file_arg(p)

    p = sub.add_parser("lint", help="consistency pass over the state file")
    p.add_argument("--strict", action="store_true",
                   help="exit 1 when there are warnings")
    add_file_arg(p)

    p = sub.add_parser("render",
                       help="markdown, json, toml or html outline from state")
    p.add_argument("--format", choices=tuple(RENDERERS), default=None,
                   help="output family (default: md). json and toml carry "
                        "the same document; html is one self-contained page")
    p.add_argument("--out", metavar="FILE", help="write here instead of stdout")
    p.add_argument("--json", action="store_true",
                   help="deprecated alias for --format json")
    add_file_arg(p)

    p = sub.add_parser("show", help="one node, or the whole tree")
    p.add_argument("node_id", nargs="?", metavar="NODE_ID")
    add_file_arg(p)

    p = sub.add_parser("set", help="edit one registry/meta scalar")
    p.add_argument("assignment", metavar="PATH=VALUE")
    add_file_arg(p)

    args = ap.parse_args()
    if args.list_templates:
        return cmd_list_templates(args.kind)
    if not args.cmd:
        ap.print_help()
        return 0
    return {
        "init": cmd_init,
        "deepen": cmd_deepen,
        "lint": cmd_lint,
        "render": cmd_render,
        "show": cmd_show,
        "set": cmd_set,
    }[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
