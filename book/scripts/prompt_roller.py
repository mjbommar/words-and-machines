#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///
"""Constrained ideation prompts rolled from the writing ontology.

Samples one coherent set of craft choices per prompt — an arc, an
arrangement, a persona, a hook, a couple of moves — and assembles them
into a drafting brief you (or a drafting LLM) can work from. It is the
generative sibling of the detection tooling: `make metrics` says a
chapter is flat, this says what to reach for instead.

Four kinds, each wiring different ontology branches into its slots:

  fiction   arc shape + narrative structure + theme + persona +
            interaction moves + POV + opening + setting + tone
  essay     argument arrangement + stasis/claim type + evidence types +
            argumentation scheme + audience + venue + stance + closer
  chapter   rhetorical situation + arrangement + arc + evidence +
            paragraph shape + hook + closer + venue + stance   (default)
  scene     scene pattern + interaction moves + persona + POV +
            scene opening + setting + tone + a micro texture directive

This is the one tool that draws on the ontology's *descriptor banks* —
settings_and_environments and tones_and_moods (writing-ontology.md):
concrete places and atmosphere labels, ideation fuel rather than craft
technique. The fiction and scene kinds take a setting and a tone from
them; chapter and essay take a nonfiction stance.

Two slot-fit rules keep the roll sane:

  situation vs venue  a rhetorical situation is an audience, an exigence,
                      or an occasion — not a publication form. Venue-like
                      categories are excluded from the situation slot and
                      carried on their own "Venue" line instead.
  written kinds       chapter and essay reject venues and occasions whose
                      name or definition marks them as spoken or performed
                      (toast, eulogy, lecture, podcast) or as fiction
                      (novel, screenplay). A heuristic, deliberately: the
                      ontology does not tag delivery mode.

Faults — entries naming a failure mode — are never rolled into a slot.

Branch files that do not exist yet are named and skipped — the roll
still emits, minus those slots. Advisory: always exits 0.

The book's genre profile (book.yaml `style.profile`, resolved against
docs/guides/styles/) is carried into every prompt so the roll never
fights the house voice.

Category names are discovered at runtime by keyword match against
whatever categories a branch actually declares, so this script never
goes stale when the ontology is re-cut.

Usage:
    uv run scripts/prompt_roller.py                          # one chapter prompt
    uv run scripts/prompt_roller.py --kind essay -n 3 --seed 7
    uv run scripts/prompt_roller.py --kind fiction --json
    uv run scripts/prompt_roller.py --kind scene \
        --branches texture=rhetorical_figures --branches pov=pov_and_narration
"""

from __future__ import annotations

import argparse
import contextlib
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import writing_ontology as wo  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent


# --------------------------------------------------------------------------
# faults (writing-ontology.md rule 3: never roll a failure mode into a slot)
#
# wo.is_fault decides on `polarity`, else on the category name; three local
# adjustments: the branch name is prepended, because not every category of a
# fault branch says so in its own title (fallacies_eristic.eristic_stratagems);
# the token "device" is dropped first — "sound_devices", "framing_devices" and
# "comparison_devices" all contain "vice"; and records whose own copy marks
# them as failures count too ("Faulty: …", "named as a diagnostic",
# "unintentional/inadvertent"), because the ontology carries no `polarity`
# stamps yet. A name that is a fault anywhere is a fault everywhere, so aspect
# homonyms (pleonasm-the-figure vs pleonasm-the-fault) cannot leak through the
# other home. An explicit `polarity: virtue` opts back out.
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


# Delivery-mode heuristic for the written kinds (chapter, essay). The
# ontology holds every publication form in one category, so a chapter roll
# would otherwise be "pitched at toast" or "written as a novel". Names are
# matched on their own words; definitions only on the strong cues, so that
# "open letter" (whose definition says *addressed to*) survives.
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


WRITTEN_KINDS = ("chapter", "essay")


# --------------------------------------------------------------------------
# fault-tolerant ontology access (branch files may not exist yet)
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
        return {
            k: v for k, v in cats.items() if isinstance(v, list) and v
        }

    def pool(
        self, name: str, keywords: tuple[str, ...] = (),
        category: str | None = None, avoid: tuple[str, ...] = (),
    ) -> list[tuple[object, str]]:
        """Entries as (entry, category) pairs, faults filtered out.

        `category` pins one category if it exists; otherwise categories
        whose *name* matches any `avoid` keyword are dropped, categories
        matching any `keywords` are preferred, and failing that the whole
        remainder is the pool. Category names are never hardcoded.
        """
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


def _matches(category: str, keywords: tuple[str, ...]) -> bool:
    label = category.lower().replace("_", " ").replace("-", " ")
    return any(k in label for k in keywords)


def entry_line(entry) -> str:
    if not isinstance(entry, dict):
        return str(entry)
    line = str(entry.get("name", "")).strip()
    definition = str(entry.get("definition", "")).strip()
    return f"{line} — {definition}" if definition else line


def entry_extras(entry) -> list[str]:
    """The bits of a record worth carrying into a drafting brief."""
    if not isinstance(entry, dict):
        return []
    out: list[str] = []
    if entry.get("beats"):
        names = [str(b.get("name", "?")) for b in entry["beats"]
                 if isinstance(b, dict)]
        if names:
            out.append("beats: " + " → ".join(names))
    if entry.get("curve"):
        pts = entry["curve"]
        if isinstance(pts, list) and pts:
            out.append(f"curve: {len(pts)} points, "
                       f"valence {_curve_summary(pts)}")
    if entry.get("critical_questions"):
        qs = entry["critical_questions"]
        if isinstance(qs, list) and qs:
            out.append(f"critical question: {qs[0]}")
    for key in ("example", "effect", "cues", "caution"):
        val = entry.get(key)
        if isinstance(val, list):
            val = ", ".join(str(v) for v in val[:4])
        if val:
            out.append(f"{key}: {val}")
    return out


def _curve_summary(points) -> str:
    vals = []
    for p in points:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            with contextlib.suppress(TypeError, ValueError):
                vals.append(float(p[1]))
    if not vals:
        return "?"
    return " → ".join(f"{v:+.1f}" for v in vals[:6]) + (
        " …" if len(vals) > 6 else "")


# --------------------------------------------------------------------------
# slot wiring — branch FILENAMES are stable, category names are not
# --------------------------------------------------------------------------
def slot(sid, label, branch, keys=(), n=1, avoid=(), written_only=False):
    """One slot. `keys` prefer categories, `avoid` excludes them.

    `written_only` applies the spoken/performed/fiction-form filter to the
    entries themselves — see SPOKEN_NAME_CUES.
    """
    return {"id": sid, "label": label, "branch": branch, "keys": keys,
            "n": n, "avoid": avoid, "written_only": written_only}


# categories that hold whole publication forms rather than situations; kept
# out of the situation slot and given their own line
VENUE_CATEGORY_KEYS = ("venue", "genre", "publication", "form")
# what a rhetorical situation actually is
SITUATION_KEYS = ("exigence", "occasion", "audience", "reader", "constraint")


KINDS: dict[str, dict] = {
    "fiction": {
        "blurb": "a story premise",
        "slots": [
            slot("arc", "Arc shape", "arc_shapes",
                 ("story", "narrative", "emotion", "shape", "rise", "fall")),
            slot("structure", "Structure", "narrative_structures",
                 ("act", "structure", "journey", "quest", "form")),
            slot("theme", "Theme", "themes_and_questions",
                 ("theme", "dilemma", "question", "motif")),
            slot("persona", "Protagonist", "character_and_persona",
                 ("character", "archetype", "stock", "protagonist")),
            slot("moves", "Interaction moves", "interaction_moves",
                 ("emotional", "social", "conflict", "character"), n=2),
            slot("pov", "POV", "pov_and_narration",
                 ("pov", "point of view", "person", "distance", "narrat")),
            slot("open", "Opening", "openings_and_closings",
                 ("hook", "opening", "lede", "cold", "frame")),
            slot("setting", "Setting", "settings_and_environments"),
            slot("tone", "Tone", "tones_and_moods", avoid=("stance",)),
        ],
        "fragments": [
            "Draft {kindword} whose protagonist is defined by {persona}.",
            "Run the {arc} arc.",
            "Build it on {structure}.",
            "Let {theme} be what the book is actually about.",
            "Set it in {setting}, and hold the atmosphere at {tone}.",
            "Narrate in {pov}.",
            "Open with the '{open}' move.",
            "Make the relationships turn on {moves}.",
        ],
    },
    "essay": {
        "blurb": "an argumentative essay",
        "slots": [
            slot("arrangement", "Arrangement", "argument_arrangements",
                 ("oration", "arrangement", "essay", "structure", "proof")),
            slot("stasis", "Stasis / claim type", "stakes_and_stasis",
                 ("stasis", "claim", "burden", "question")),
            slot("evidence", "Evidence", "evidence_types",
                 ("evidence", "example", "authority", "statistic", "case"),
                 n=2),
            slot("scheme", "Argumentation scheme", "argumentation_schemes",
                 ("scheme", "cause", "analogy", "sign", "expert")),
            slot("audience", "Audience / occasion", "rhetorical_situations",
                 SITUATION_KEYS, avoid=VENUE_CATEGORY_KEYS,
                 written_only=True),
            slot("venue", "Venue", "rhetorical_situations",
                 VENUE_CATEGORY_KEYS, written_only=True),
            slot("tone", "Stance", "tones_and_moods", ("stance",)),
            slot("close", "Closer", "openings_and_closings",
                 ("closing", "closer", "coda", "callback", "ending")),
        ],
        "fragments": [
            "Write {kindword} for {audience}.",
            "Pitch it at the length and manners of {venue}.",
            "Arrange it as {arrangement}.",
            "Fight the argument at {stasis}.",
            "Carry the inference with {scheme}.",
            "Ground it in {evidence}.",
            "Hold the stance at {tone}.",
            "Land it with {close}.",
        ],
    },
    "chapter": {
        "blurb": "a chapter",
        "slots": [
            slot("situation", "Rhetorical situation", "rhetorical_situations",
                 SITUATION_KEYS, avoid=VENUE_CATEGORY_KEYS,
                 written_only=True),
            slot("venue", "Venue", "rhetorical_situations",
                 VENUE_CATEGORY_KEYS, written_only=True),
            slot("arrangement", "Arrangement", "argument_arrangements",
                 ("oration", "arrangement", "essay", "structure", "proof")),
            slot("arc", "Certainty / tension arc", "arc_shapes",
                 ("epistemic", "certainty", "proof", "shape", "arc")),
            slot("evidence", "Evidence", "evidence_types",
                 ("evidence", "example", "case", "statistic", "authority"),
                 n=2),
            slot("para", "Paragraph architecture", "paragraph_shapes",
                 ("paragraph", "shape", "architecture")),
            slot("open", "Hook", "openings_and_closings",
                 ("hook", "opening", "lede", "cold", "frame")),
            slot("tone", "Stance", "tones_and_moods", ("stance",)),
            slot("close", "Closer", "openings_and_closings",
                 ("closing", "closer", "coda", "callback", "ending")),
        ],
        "fragments": [
            "Draft {kindword} pitched at {situation}.",
            "Write it to the conventions of {venue}.",
            "Arrange it as {arrangement}.",
            "Shape the reader's certainty along {arc}.",
            "Argue from {evidence}.",
            "Default the body paragraphs to {para} — vary off it deliberately.",
            "Hold the stance at {tone}.",
            "Open on {open}; close on {close}.",
        ],
    },
    "scene": {
        "blurb": "a scene",
        "slots": [
            slot("pattern", "Scene pattern", "scene_patterns",
                 ("pattern", "sequel", "try", "yes-but", "type", "function")),
            slot("persona", "Who is in it", "character_and_persona",
                 ("character", "archetype", "stock", "role")),
            slot("moves", "Moves in play", "interaction_moves",
                 ("emotional", "social", "conflict", "dialogue"), n=2),
            slot("pov", "POV / distance", "pov_and_narration",
                 ("pov", "point of view", "distance", "person", "narrat")),
            slot("open", "Scene opening", "openings_and_closings",
                 ("scene", "hook", "opening", "cold", "entry")),
            slot("texture", "Micro texture", "syntactic_constructions",
                 ("period", "cumulative", "absolute", "clause", "sentence")),
            slot("setting", "Setting", "settings_and_environments"),
            slot("tone", "Mood", "tones_and_moods", avoid=("stance",)),
        ],
        "fragments": [
            "Write {kindword} built as {pattern}.",
            "Stage it in {setting}; play the mood as {tone}.",
            "Put {persona} under pressure in it.",
            "Let the exchange run on {moves}.",
            "Hold {pov}.",
            "Enter the scene through {open}.",
            "Give at least two sentences the shape of {texture}.",
        ],
    },
}

KIND_WORDS = {
    "fiction": "a story",
    "essay": "an essay",
    "chapter": "a chapter",
    "scene": "a scene",
}


# --------------------------------------------------------------------------
# style profile
# --------------------------------------------------------------------------
def load_profile(root: Path) -> dict:
    """book.yaml style.profile, resolved against docs/guides/styles/."""
    info = {"name": "", "path": "", "exists": False}
    book_yaml = root / "book.yaml"
    if not book_yaml.exists():
        return info
    try:
        import yaml
        cfg = yaml.safe_load(book_yaml.read_text(encoding="utf-8")) or {}
    except Exception:  # noqa: BLE001 - advisory tool, never fail on config
        return info
    name = ((cfg.get("style") or {}).get("profile") or "").strip()
    if not name:
        return info
    md = root / "docs" / "guides" / "styles" / f"{name}.md"
    info.update(name=name, path=str(md.relative_to(root)), exists=md.exists())
    return info


def profile_line(profile: dict) -> str:
    if not profile["name"]:
        return ("Style: docs/guides/STYLE.md + STYLE-AI-TELLS.md "
                "(no genre profile set in book.yaml).")
    where = profile["path"] + ("" if profile["exists"] else " [MISSING]")
    return (f"Style: genre profile '{profile['name']}' ({where}) layered "
            f"over docs/guides/STYLE.md + STYLE-AI-TELLS.md.")


# --------------------------------------------------------------------------
# rolling
# --------------------------------------------------------------------------
def parse_overrides(pairs: list[str]) -> dict[str, tuple[str, str | None]]:
    """--branches slot=branch[.category] → {slot: (branch, category)}."""
    out: dict[str, tuple[str, str | None]] = {}
    for raw in pairs:
        sid, sep, spec = raw.partition("=")
        if not sep or not spec.strip():
            raise SystemExit(
                f"prompt_roller: bad --branches {raw!r}; "
                "expected slot=branch or slot=branch.category")
        branch, _, category = spec.strip().partition(".")
        out[sid.strip()] = (branch, category or None)
    return out


def roll(kind: str, onto: Ontology, rng: random.Random,
         overrides: dict[str, tuple[str, str | None]]) -> dict:
    filled: dict[str, dict] = {}
    for spec in KINDS[kind]["slots"]:
        branch, category = overrides.get(
            spec["id"], (spec["branch"], None))
        own = branch == spec["branch"]
        keys = spec["keys"] if own else ()
        avoid = spec["avoid"] if own else ()
        pool = onto.pool(branch, keys, category, avoid)
        if spec["written_only"] and kind in WRITTEN_KINDS:
            # a chapter is not delivered as a toast, and is not a novel
            pool = [(e, c) for e, c in pool if not spoken_form(e)] or pool
        if not pool:
            continue
        picks = rng.sample(pool, min(spec["n"], len(pool)))
        filled[spec["id"]] = {
            "label": spec["label"],
            "branch": branch,
            "picks": [
                {
                    "category": cat,
                    "name": wo.entry_name(e),
                    "entry": e if isinstance(e, dict) else {"name": e},
                }
                for e, cat in picks
            ],
        }
    return filled


def phrase(slot_data: dict) -> str:
    names = [p["name"] for p in slot_data["picks"]]
    if len(names) == 1:
        return names[0]
    return " and ".join([", ".join(names[:-1]), names[-1]])


def render_instruction(kind: str, filled: dict) -> str:
    out: list[str] = []
    values = {sid: phrase(d) for sid, d in filled.items()}
    values["kindword"] = KIND_WORDS[kind]
    for frag in KINDS[kind]["fragments"]:
        needed = [
            part.split("}")[0]
            for part in frag.split("{")[1:]
        ]
        if all(n in values for n in needed):
            # collapse echoes like "the detective arc arc" when an entry
            # name already ends with the fragment's noun
            out.append(re.sub(r"\b(\w+)( \1)+\b", r"\1",
                              frag.format(**values)))
    return " ".join(out)


def format_block(index: int, total: int, kind: str, seed: int,
                 profile: dict, filled: dict, skipped: list[str]) -> str:
    lines = [
        f"── prompt {index}/{total} ── kind={kind} seed={seed} "
        + ("profile=" + (profile["name"] or "none")),
        "",
    ]
    width = max((len(d["label"]) for d in filled.values()), default=0)
    avail = max(40, 86 - width)

    def emit(label: str, text: str) -> None:
        chunks = _wrap(text, avail)
        lines.append(f"  {label:<{width}}  {chunks[0]}")
        for chunk in chunks[1:]:
            lines.append(f"  {'':<{width}}    {chunk}")

    for spec in KINDS[kind]["slots"]:
        data = filled.get(spec["id"])
        if not data:
            continue
        for i, pick in enumerate(data["picks"]):
            emit(data["label"] if i == 0 else "", entry_line(pick["entry"]))
            src = f"{data['branch']}"
            if pick["category"]:
                src += f".{pick['category']}"
            lines.append(f"  {'':<{width}}  [{src}]")
            for extra in entry_extras(pick["entry"]):
                emit("", extra)
    lines.append("")
    lines.append("  BRIEF")
    for line in _wrap(render_instruction(kind, filled), 72):
        lines.append(f"    {line}")
    lines.append(f"    {profile_line(profile)}")
    if skipped:
        lines.append("")
        lines.append("  slots skipped (branch unavailable): "
                     + ", ".join(skipped))
    return "\n".join(lines)


def _wrap(text: str, width: int) -> list[str]:
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


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Slots per kind: "
               + "; ".join(
                   f"{k}: " + ",".join(s["id"] for s in v["slots"])
                   for k, v in KINDS.items()),
    )
    ap.add_argument("--kind", choices=sorted(KINDS), default="chapter",
                    help="what to roll a prompt for (default: chapter)")
    ap.add_argument("-n", type=int, default=1, help="number of prompts")
    ap.add_argument("--seed", type=int, default=None,
                    help="reproducible roll (printed if omitted)")
    ap.add_argument("--branches", action="append", default=[], metavar="SLOT=BRANCH",
                    help="override a slot's branch, e.g. arc=narrative_structures "
                         "or texture=rhetorical_figures.tropes (repeatable)")
    ap.add_argument("--root", type=Path, default=REPO_ROOT,
                    help="book root holding book.yaml (default: repo root)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    seed = args.seed if args.seed is not None else random.randrange(1, 10**6)
    overrides = parse_overrides(args.branches)
    onto = Ontology()
    profile = load_profile(args.root)

    branches = wo.available_branches()
    rolls = []
    for i in range(max(1, args.n)):
        rng = random.Random(f"{seed}:{args.kind}:{i}")
        filled = roll(args.kind, onto, rng, overrides)
        skipped = [
            s["id"] for s in KINDS[args.kind]["slots"] if s["id"] not in filled
        ]
        rolls.append((filled, skipped))

    if args.json:
        print(json.dumps({
            "kind": args.kind,
            "seed": seed,
            "profile": profile,
            "ontology_dir": str(wo.ONTOLOGY_DIR),
            "branches_available": branches,
            "unavailable": onto.missing,
            "prompts": [
                {
                    "index": i + 1,
                    "slots": filled,
                    "skipped": skipped,
                    "brief": render_instruction(args.kind, filled),
                    "style": profile_line(profile),
                }
                for i, (filled, skipped) in enumerate(rolls)
            ],
        }, indent=2))
        return 0

    if not branches:
        print(f"prompt_roller: no ontology branch files in {wo.ONTOLOGY_DIR} "
              "— nothing to sample yet.")
    for i, (filled, skipped) in enumerate(rolls):
        if i:
            print()
        print(format_block(i + 1, len(rolls), args.kind, seed, profile,
                           filled, skipped))
    if onto.missing:
        print()
        print("branches not available yet (slots dropped, not an error):")
        for name, why in sorted(onto.missing.items()):
            print(f"  {name}: {why}")
    print()
    print(f"prompt_roller: {len(rolls)} prompt(s), seed {seed} "
          f"(rerun with --seed {seed}); advisory only.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
