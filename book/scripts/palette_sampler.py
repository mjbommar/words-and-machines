#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Sample a construction palette — a small, coherent set of craft moves.

A *palette* is what a painter squeezes out before starting: a deliberately
short list of tools chosen in advance, so the session reaches for named
constructions instead of the same three habitual ones. This draws that
palette from the writing ontology (docs/architecture/writing-ontology.md),
seeded and reproducible.

Default recipe (level "all"):

    3 syntactic_constructions   3 rhetorical_figures
    2 sound_and_rhythm          2 diction_and_register
    1 discourse_moves           1 scene_patterns        (the meso pair)

Reshape it with --counts; 0 drops a branch, and any branch file in the
ontology may be added (`pov_and_narration=2`). Branch FILENAMES are the
stable contract — categories are discovered at runtime, never assumed.

Two things never enter a palette by default:

  faults            entries that name a failure mode (diction faults,
                    rhythm faults, figure vices, fallacies) are filtered
                    out — a palette is a list of things to reach for, and
                    "use a slop lexicon" is not a drafting directive.
                    --include-faults adds them back in AUDIT phrasing only
                    ("Audit the passage for X and repair it"), never as
                    "use X".
  descriptor banks  settings_and_environments and tones_and_moods are
                    ideation nouns and atmosphere labels, not craft
                    techniques (writing-ontology.md). prompt_roller draws
                    on them; a construction palette does not. Naming one
                    in --counts is obeyed, with a warning.

Output modes (pick one):

    (default)      human-readable: name — definition, plus example,
                   effect and caution when the entry carries them
    --for-deslop   terse directive lines to paste into a deslop.py fix
                   brief ("Recast one sentence as a nominative absolute:
                   ..."). deslop.py never reads these itself — the human
                   or revision agent applies them; see REVIEW-QA §7.
    --for-prompt   a block to paste into an LLM drafting prompt, with the
                   use-sparingly rules attached
    --json         machine-readable

Advisory, always exits 0. Missing branch files (the ontology is authored
incrementally) are named on stderr and skipped — whatever exists is still
sampled.

Usage:
    uv run scripts/palette_sampler.py                          # one palette
    uv run scripts/palette_sampler.py --seed 7 -n 3            # three, reproducible
    uv run scripts/palette_sampler.py --level micro
    uv run scripts/palette_sampler.py --counts syntactic_constructions=5,rhetorical_figures=2
    uv run scripts/palette_sampler.py --counts scene_patterns=0,pov_and_narration=2
    uv run scripts/palette_sampler.py --seed 7 --for-deslop >> brief.md
    uv run scripts/palette_sampler.py --for-prompt --level micro
    uv run scripts/palette_sampler.py --include-faults --level micro
    uv run scripts/palette_sampler.py --json | jq '.palettes[0].items[].name'
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import writing_ontology as wo  # noqa: E402

# Branch FILENAMES only — the stable half of the contract. Categories are
# read from whatever the branch file happens to define.
MICRO_RECIPE = {
    "syntactic_constructions": 3,
    "rhetorical_figures": 3,
    "sound_and_rhythm": 2,
    "diction_and_register": 2,
}
MESO_RECIPE = {"discourse_moves": 1, "scene_patterns": 1}
MESO_ONLY_RECIPE = {"discourse_moves": 3, "scene_patterns": 2}

# Descriptor banks, not craft branches (writing-ontology.md): ideation fuel
# for prompt_roller, never a construction palette. Excluded from every
# recipe; nameable in --counts, which warns and obeys.
DESCRIPTOR_BANKS = ("settings_and_environments", "tones_and_moods")

# Directive verb per branch for --for-deslop. Unknown branches fall back to
# GENERIC_DIRECTIVE, so a branch added to the ontology later still works.
DIRECTIVES = {
    "syntactic_constructions": "Recast one sentence as {a} {name}",
    "rhetorical_figures": "Work in one {name} where the emphasis should land",
    "sound_and_rhythm": "Tune one sentence for {name}",
    "diction_and_register": "Use {name} in the diction of one passage",
    "pov_and_narration": "Adjust the narration using {name}",
    "discourse_moves": "Make one transition do the work of {name}",
    "paragraph_shapes": "Rebuild one paragraph on the {name} shape",
    "scene_patterns": "Shape one scene on the {name} pattern",
    "openings_and_closings": "Rebuild an opening or close on the {name} pattern",
    "argumentation_schemes": "Carry one claim with {name}",
    "evidence_types": "Ground one claim with {name}",
    "interaction_moves": "Give one exchange the move {name}",
    "character_and_persona": "Angle the passage through {name}",
    "stakes_and_stasis": "Re-pitch the stakes using {name}",
    "themes_and_questions": "Thread {name} through the passage",
}
# Only syntactic_constructions takes an article ({a}): its entries are noun
# phrases. Elsewhere names may be verb phrases ("introduce a deadline"), so
# the frames stay article-free.
GENERIC_DIRECTIVE = "Bring {name} into the passage"
# The single frame every fault gets, whatever branch it came from: a failure
# mode is a thing to look for and remove, never a thing to write.
AUDIT_DIRECTIVE = "Audit the passage for {name} and repair it"

MAX_DEF = 170  # --for-deslop lines stay one screen line where possible


# ------------------------------------------------------------------- faults


# Rule 3 of docs/architecture/writing-ontology.md: a fault names a failure
# mode and is never a positive drafting directive. wo.is_fault decides on
# `polarity`, else on the category name; three local adjustments:
#   * the branch name is prepended, because not every category of a fault
#     branch says so in its own title (fallacies_eristic.eristic_stratagems);
#   * the token "device" is dropped first — "sound_devices",
#     "framing_devices" and "comparison_devices" all contain "vice";
#   * records whose own copy marks them as failures count too ("Faulty: …",
#     "named as a diagnostic", "unintentional/inadvertent"), because the
#     ontology carries no `polarity` stamps yet.
# Finally a name that is a fault anywhere is treated as a fault everywhere,
# so aspect homonyms (pleonasm-the-figure vs pleonasm-the-fault) cannot leak
# through the other home. An explicit `polarity: virtue` opts back out.


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
            except (OSError, json.JSONDecodeError):
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


# ------------------------------------------------------------------ helpers


def field(entry, key: str) -> str:
    """Value of an entry field; term entries have only a name."""
    if isinstance(entry, dict):
        return str(entry.get(key, "") or "").strip()
    return str(entry).strip() if key == "name" else ""


def shorten(text: str, limit: int = MAX_DEF) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip(" ,;:") + "…"


def article(name: str) -> str:
    return "an" if name[:1].lower() in "aeiou" else "a"


def parse_counts(spec: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        branch, sep, num = chunk.partition("=")
        branch = branch.strip()
        if not sep or not branch:
            raise ValueError(f"bad --counts item {chunk!r}; want BRANCH=N")
        try:
            n = int(num)
        except ValueError:
            raise ValueError(f"bad count in {chunk!r}; want BRANCH=N") from None
        if n < 0:
            raise ValueError(f"negative count in {chunk!r}")
        counts[branch] = n
    if not counts:
        raise ValueError("--counts is empty; want BRANCH=N[,BRANCH=N]")
    return counts


def recipe_for(level: str) -> dict[str, int]:
    if level == "micro":
        return dict(MICRO_RECIPE)
    if level == "meso":
        return dict(MESO_ONLY_RECIPE)
    return {**MICRO_RECIPE, **MESO_RECIPE}


# ------------------------------------------------------------------ sampling


LEVELS: dict[str, str] = {}  # branch -> declared level, filled by load_pools


def load_pools(recipe: dict[str, int], include_faults: bool = False,
               requested: frozenset[str] = frozenset(),
               ) -> tuple[dict[str, list], list[str]]:
    """{branch: [(entry, category, fault)]} for branches that exist.

    Faults are dropped unless `include_faults`; descriptor banks are dropped
    unless the caller named them in --counts (`requested`), and warn even
    then. Second return value: branches with nothing left to sample.
    """
    have = set(wo.available_branches())
    pools: dict[str, list] = {}
    missing: list[str] = []
    for name, n in recipe.items():
        if n <= 0:
            continue
        if name not in have:
            missing.append(name)
            continue
        if name in DESCRIPTOR_BANKS:
            if name not in requested:
                continue
            print(f"palette_sampler: WARN {name} is a descriptor bank, not a "
                  f"craft branch — sampling it because --counts asked "
                  f"(writing-ontology.md)", file=sys.stderr)
        try:
            branch = wo.load_branch(name)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"palette_sampler: WARN unreadable branch {name}: {exc}",
                  file=sys.stderr)
            missing.append(name)
            continue
        items = [
            (entry, category, is_fault(entry, name, category))
            for category, entries in (branch.get("categories") or {}).items()
            if isinstance(entries, list)
            for entry in entries
        ]
        if not include_faults:
            items = [it for it in items if not it[2]]
        if not items:
            missing.append(name)
            continue
        LEVELS[name] = str(branch.get("level", "") or "")
        pools[name] = items
    return pools, missing


def sample_palette(recipe: dict[str, int], pools: dict[str, list],
                   rng: random.Random) -> tuple[list[dict], list[str]]:
    """One palette: items in recipe order, plus shortfall notes."""
    items: list[dict] = []
    notes: list[str] = []
    for name, n in recipe.items():
        pool = pools.get(name)
        if n <= 0 or not pool:
            continue
        take = min(n, len(pool))
        if take < n:
            notes.append(f"{name}: asked {n}, branch holds {len(pool)}")
        for entry, category, fault in rng.sample(pool, take):
            items.append({
                "branch": name,
                "level": LEVELS.get(name, ""),
                "category": category,
                "fault": fault,
                "name": field(entry, "name"),
                "definition": field(entry, "definition"),
                "example": field(entry, "example"),
                "effect": field(entry, "effect"),
                "register": field(entry, "register"),
                "caution": field(entry, "caution"),
            })
    return items, notes


# ------------------------------------------------------------------- output


def directive_line(item: dict) -> str:
    name = item["name"]
    template = (AUDIT_DIRECTIVE if item.get("fault")
                else DIRECTIVES.get(item["branch"], GENERIC_DIRECTIVE))
    head = template.format(name=name, a=article(name))
    definition = shorten(item["definition"])
    line = f"- {head}: {definition}" if definition else f"- {head}."
    if item["example"]:
        line += f" [e.g. {shorten(item['example'], 110)}]"
    if item["caution"]:
        line += f" (caution: {shorten(item['caution'], 90)})"
    return line


def print_human(palettes: list[dict], seed: int, level: str) -> None:
    for p in palettes:
        label = f"Palette {p['index']}" if len(palettes) > 1 else "Palette"
        print(f"{label} — level {level}, seed {seed}")
        print("-" * 66)
        current = None
        for it in p["items"]:
            if it["branch"] != current:
                current = it["branch"]
                lvl = f" [{it['level']}]" if it["level"] else ""
                print(f"\n{current.replace('_', ' ')}{lvl}")
            mark = "  [FAULT — audit target, do not write it]" if it["fault"] \
                else ""
            print(f"  {it['name']} — {it['definition']}{mark}"
                  if it["definition"] else f"  {it['name']}{mark}")
            if it["example"]:
                print(f"      e.g. {it['example']}")
            if it["effect"]:
                print(f"      effect: {it['effect']}")
            if it["register"]:
                print(f"      register: {it['register']}")
            if it["caution"]:
                print(f"      caution: {it['caution']}")
        for note in p["notes"]:
            print(f"\n  note: {note}")
        print()
    print("Use what earns its place; an unused palette item costs nothing, a "
          "forced one costs a sentence.")


def print_for_deslop(palettes: list[dict], seed: int) -> None:
    multi = len(palettes) > 1
    print(f"## Construction palette — seed {seed} (writing ontology)")
    print()
    print("Directives, not edits. Apply at most one per paragraph; skipping "
          "one is a valid outcome.")
    for p in palettes:
        if multi:
            print(f"\n### Palette {p['index']}")
        print()
        for it in p["items"]:
            print(directive_line(it))


def print_for_prompt(palettes: list[dict], seed: int) -> None:
    for p in palettes:
        suffix = f" {p['index']}" if len(palettes) > 1 else ""
        print(f"CONSTRUCTION PALETTE{suffix} (seed {seed})")
        print("Write with these tools available. Rules:")
        print("  - at most one palette move per paragraph;")
        print("  - do not use every item — unused items are free, forced "
              "items are not;")
        print("  - never name the technique in the prose.")
        print()
        current = None
        use = [it for it in p["items"] if not it["fault"]]
        faults = [it for it in p["items"] if it["fault"]]
        for it in use:
            if it["branch"] != current:
                current = it["branch"]
                print(f"{current.replace('_', ' ').upper()}")
            line = f"  - {it['name']}"
            if it["definition"]:
                line += f": {shorten(it['definition'], 140)}"
            print(line)
            if it["example"]:
                print(f"      e.g. {shorten(it['example'], 110)}")
        if faults:
            print("\nAUDIT TARGETS (failure modes — check the draft for these "
                  "and repair them; never write them)")
            for it in faults:
                line = f"  - {it['name']}"
                if it["definition"]:
                    line += f": {shorten(it['definition'], 140)}"
                print(line)
        cautions = [it for it in use if it["caution"]]
        if cautions:
            print("\nOVERUSE WARNINGS")
            for it in cautions:
                print(f"  - {it['name']}: {shorten(it['caution'], 120)}")
        print()


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        epilog="\n".join(__doc__.splitlines()[1:]),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("-n", type=int, default=1, metavar="N",
                    help="number of independent palettes (default 1)")
    ap.add_argument("--level", choices=("micro", "meso", "all"), default="all",
                    help="which recipe to start from (default: all)")
    ap.add_argument("--counts", default=None, metavar="SPEC",
                    help="reshape the recipe: BRANCH=N[,BRANCH=N]; 0 drops a "
                         "branch, unlisted branches keep their default")
    ap.add_argument("--seed", type=int, default=None,
                    help="reproducibility seed (default: random, reported)")
    ap.add_argument("--include-faults", action="store_true",
                    help="also draw failure modes (diction faults, rhythm "
                         "faults, figure vices, fallacies); they are emitted "
                         "as audit targets — 'audit the passage for X and "
                         "repair it' — never as directives to use them")
    out = ap.add_mutually_exclusive_group()
    out.add_argument("--for-deslop", action="store_true",
                     help="terse directive lines for a deslop.py fix brief")
    out.add_argument("--for-prompt", action="store_true",
                     help="block for an LLM drafting prompt")
    out.add_argument("--json", action="store_true", help="machine-readable")
    args = ap.parse_args()

    if args.n < 1:
        ap.error("-n must be >= 1")
    recipe = recipe_for(args.level)
    requested: frozenset[str] = frozenset()
    if args.counts:
        try:
            asked = parse_counts(args.counts)
        except ValueError as exc:
            ap.error(str(exc))
        recipe.update(asked)
        requested = frozenset(asked)

    seed = args.seed if args.seed is not None else random.randrange(1, 10**6)
    rng = random.Random(seed)

    pools, missing = load_pools(recipe, args.include_faults, requested)
    if missing:
        print(f"palette_sampler: no entries for {', '.join(sorted(missing))} "
              f"in {wo.ONTOLOGY_DIR} — skipped (ontology is authored "
              f"incrementally)", file=sys.stderr)
    if not pools:
        print("palette_sampler: nothing to sample; the requested branches are "
              "all missing or empty. Nothing written.", file=sys.stderr)
        if args.json:
            print(json.dumps({"seed": seed, "level": args.level,
                              "recipe": recipe, "missing_branches":
                              sorted(missing), "palettes": []}, indent=2))
        return 0

    palettes = []
    for i in range(1, args.n + 1):
        items, notes = sample_palette(recipe, pools, rng)
        palettes.append({"index": i, "items": items, "notes": notes})

    if args.json:
        print(json.dumps({
            "seed": seed,
            "level": args.level,
            "recipe": {k: v for k, v in recipe.items() if v > 0},
            "missing_branches": sorted(missing),
            "palettes": palettes,
        }, indent=2))
    elif args.for_deslop:
        print_for_deslop(palettes, seed)
    elif args.for_prompt:
        print_for_prompt(palettes, seed)
    else:
        print_human(palettes, seed, args.level)
    return 0


if __name__ == "__main__":
    sys.exit(main())
