#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Writing-ontology loader: lint, stats, browse, and seeded sampling.

The ontology (docs/architecture/writing-ontology.md) is a set of JSON
branch files under scripts/data/ontology/, each a controlled vocabulary
of writing craft at one level (macro | meso | micro). Two entry types:

  term    plain lowercase strings           "in medias res"
  record  objects: name + definition required; example / effect /
          register / caution / aka / tags recommended; structured
          extras allowed (beats, curve, critical_questions, pattern,
          renderings, cues, ...)

Library API (import writing_ontology after sys.path.append("scripts")):

    load_branch("rhetorical_figures")   -> dict (whole file)
    load_all()                          -> {name: dict}
    flatten("rhetorical_figures")       -> sorted list of entry names
    sample_entries(branch, category=None, n=1, seed=None) -> list
    entry_name(entry)                   -> str for term or record

CLI:

    uv run scripts/writing_ontology.py stats            # counts table
    uv run scripts/writing_ontology.py lint [--strict]  # schema audit
                                                        # + INFO: undeclared
                                                        #   cross-branch homonyms
    uv run scripts/writing_ontology.py show BRANCH [CATEGORY]
    uv run scripts/writing_ontology.py sample BRANCH[.CATEGORY] \
        [-n N] [--seed S] [--level macro|meso|micro]

Advisory: lint exits 0 unless --strict.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path

ONTOLOGY_DIR = Path(
    os.environ.get(
        "WRITING_ONTOLOGY_DIR",
        Path(__file__).resolve().parent / "data" / "ontology",
    )
)
LEVELS = ("macro", "meso", "micro")
ENTRY_TYPES = ("term", "record")
RECORD_REQUIRED = ("name", "definition")
RECORD_RECOMMENDED = ("example", "effect", "register")
POLARITIES = ("virtue", "fault", "neutral")


def branch_path(name: str) -> Path:
    return ONTOLOGY_DIR / f"{name}.json"


def available_branches() -> list[str]:
    if not ONTOLOGY_DIR.is_dir():
        return []
    return sorted(p.stem for p in ONTOLOGY_DIR.glob("*.json"))


def load_branch(name: str) -> dict:
    path = branch_path(name)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_all() -> dict[str, dict]:
    return {name: load_branch(name) for name in available_branches()}


def entry_name(entry) -> str:
    return entry["name"] if isinstance(entry, dict) else str(entry)


def flatten(name: str) -> list[str]:
    branch = load_branch(name)
    names = {
        entry_name(e)
        for entries in branch.get("categories", {}).values()
        for e in entries
    }
    return sorted(names)


FAULT_CATEGORY_HINTS = ("fault", "vice", "fallac", "dark_pattern")


def is_fault(entry, category: str = "") -> bool:
    """True when an entry names a failure mode rather than a technique.

    Generative samplers must not emit faults as positive directives
    (ONTOLOGY.md rule 3). Explicit ``polarity: fault`` wins; otherwise
    the category name decides (fault/vices/fallacies/dark patterns).
    """
    if isinstance(entry, dict):
        pol = entry.get("polarity")
        if pol:
            return pol == "fault"
    return any(h in category for h in FAULT_CATEGORY_HINTS)


def find_entries(query: str) -> list[tuple[str, str, str, object]]:
    """Case-insensitive search of name/aka/definition across all
    branches -> [(branch, category, matched_name, entry), ...]."""
    q = query.lower()
    out = []
    for name in available_branches():
        try:
            branch = load_branch(name)
        except (json.JSONDecodeError, OSError):
            continue
        for cat, entries in branch.get("categories", {}).items():
            for e in entries:
                label = entry_name(e)
                hay = label.lower()
                if isinstance(e, dict):
                    aka = e.get("aka", "")
                    if isinstance(aka, list):
                        aka = " ".join(str(a) for a in aka)
                    hay += " " + str(aka).lower() + " " \
                           + str(e.get("definition", "")).lower()
                if q in hay:
                    out.append((name, cat, label, e))
    return out


def sample_entries(branch, category=None, n=1, seed=None) -> list:
    """Seeded sample of entries from a branch dict (or branch name)."""
    if isinstance(branch, str):
        branch = load_branch(branch)
    cats = branch.get("categories", {})
    if category is not None:
        if category not in cats:
            raise KeyError(
                f"no category {category!r} in {branch.get('name')!r}; "
                f"have: {', '.join(sorted(cats))}"
            )
        pool = list(cats[category])
    else:
        pool = [e for entries in cats.values() for e in entries]
    rng = random.Random(seed)
    n = min(n, len(pool))
    return rng.sample(pool, n)


def lint_branch(name: str) -> list[str]:
    """Return a list of problem strings for one branch file."""
    problems: list[str] = []
    try:
        branch = load_branch(name)
    except (json.JSONDecodeError, OSError) as exc:
        return [f"{name}: unreadable JSON ({exc})"]

    for key in ("name", "level", "entry_type", "description", "categories"):
        if key not in branch:
            problems.append(f"{name}: missing top-level key {key!r}")
    if branch.get("name") != name:
        problems.append(
            f"{name}: name field {branch.get('name')!r} != filename stem"
        )
    if branch.get("level") not in LEVELS:
        problems.append(f"{name}: level must be one of {LEVELS}")
    etype = branch.get("entry_type")
    if etype not in ENTRY_TYPES:
        problems.append(f"{name}: entry_type must be one of {ENTRY_TYPES}")

    cats = branch.get("categories", {})
    if not isinstance(cats, dict) or not cats:
        problems.append(f"{name}: categories must be a non-empty object")
        return problems

    seen: dict[str, str] = {}
    for cat, entries in cats.items():
        if not isinstance(entries, list) or not entries:
            problems.append(f"{name}.{cat}: must be a non-empty list")
            continue
        for i, e in enumerate(entries):
            where = f"{name}.{cat}[{i}]"
            if etype == "term":
                if not isinstance(e, str) or not e.strip():
                    problems.append(f"{where}: term must be non-empty string")
                    continue
                label = e.strip().lower()
            else:
                if not isinstance(e, dict):
                    problems.append(f"{where}: record must be an object")
                    continue
                for req in RECORD_REQUIRED:
                    if not str(e.get(req, "")).strip():
                        problems.append(f"{where}: missing {req!r}")
                pol = e.get("polarity")
                if pol is not None and pol not in POLARITIES:
                    problems.append(
                        f"{where}: polarity must be one of {POLARITIES}")
                label = str(e.get("name", "")).strip().lower()
            if label and label in seen:
                problems.append(
                    f"{where}: duplicate of {seen[label]} ({label!r})"
                )
            elif label:
                seen[label] = f"{name}.{cat}"
    return problems


def _cross_refs(entry) -> set[str]:
    """Branch (and branch/category) tokens an entry points at.

    Reads ``see_also`` (string or list of ``"branch/category"``) and any
    ``aka`` text, which is where an aspect-split entry names its sibling.
    """
    if not isinstance(entry, dict):
        return set()
    out: set[str] = set()
    sa = entry.get("see_also", [])
    for ref in [sa] if isinstance(sa, str) else list(sa):
        ref = str(ref).strip()
        if ref:
            out.add(ref)
            out.add(ref.split("/", 1)[0])
    aka = entry.get("aka", "")
    if isinstance(aka, list):
        aka = " ".join(str(a) for a in aka)
    aka = str(aka).lower()
    for token in aka.replace("/", " ").replace(",", " ").split():
        out.add(token)
    return out


def cross_branch_collisions() -> list[tuple[str, list[tuple[str, str, bool]]]]:
    """Names living in 2+ branches with no ``see_also``/``aka`` linking them.

    Aspect ownership (writing-ontology.md) allows one concept to live in
    several branches when each owns a different aspect, but a legitimate
    split has to be declared. Term entries cannot carry metadata, so
    term-vs-term collisions are exempt; record-vs-record and record-vs-term
    are reported.

    Returns ``[(name, [(branch, category, is_record), ...]), ...]`` sorted
    by number of homes (descending), then name.
    """
    homes: dict[str, list[tuple[str, str, object]]] = {}
    for branch_name in available_branches():
        try:
            branch = load_branch(branch_name)
        except (json.JSONDecodeError, OSError):
            continue
        for cat, entries in branch.get("categories", {}).items():
            if not isinstance(entries, list):
                continue
            for e in entries:
                label = entry_name(e).strip().lower()
                if label:
                    homes.setdefault(label, []).append((branch_name, cat, e))

    out = []
    for label, places in homes.items():
        branches = {b for b, _, _ in places}
        if len(branches) < 2:
            continue
        if not any(isinstance(e, dict) for _, _, e in places):
            continue  # term-vs-term: nowhere to record the split
        linked = False
        for branch_name, _cat, e in places:
            refs = _cross_refs(e)
            others = {
                f"{b}/{c}" for b, c, _ in places if b != branch_name
            } | {b for b, _, _ in places if b != branch_name}
            if refs & others:
                linked = True
                break
        if not linked:
            out.append(
                (label, [(b, c, isinstance(e, dict)) for b, c, e in places])
            )
    out.sort(key=lambda kv: (-len(kv[1]), kv[0]))
    return out


def print_cross_branch_info(limit: int = 30) -> int:
    """Print the advisory INFO block; returns the number of names found."""
    hits = cross_branch_collisions()
    if not hits:
        return 0
    print(
        f"INFO {len(hits)} names live in 2+ branches with no see_also/aka "
        f"linking them (term-vs-term collisions exempt)"
    )
    for label, places in hits[:limit]:
        where = ", ".join(f"{b}.{c}" for b, c, _ in places)
        print(f"INFO   {label}: {where}")
    extra = len(hits) - limit
    if extra > 0:
        print(f"INFO   ... and {extra} more")
    return len(hits)


def stats_rows() -> list[tuple[str, str, str, int, int]]:
    rows = []
    for name in available_branches():
        try:
            b = load_branch(name)
        except (json.JSONDecodeError, OSError):
            rows.append((name, "?", "?", 0, 0))
            continue
        cats = b.get("categories", {})
        n = sum(len(v) for v in cats.values() if isinstance(v, list))
        rows.append(
            (name, b.get("level", "?"), b.get("entry_type", "?"), len(cats), n)
        )
    return rows


def cmd_stats(_args) -> int:
    rows = stats_rows()
    if not rows:
        print(f"no branch files in {ONTOLOGY_DIR}")
        return 0
    width = max(len(r[0]) for r in rows)
    print(f"{'branch':<{width}}  level  type    cats  entries")
    total = 0
    for name, level, etype, ncat, n in rows:
        total += n
        print(f"{name:<{width}}  {level:<5}  {etype:<6}  {ncat:>4}  {n:>7}")
    print(f"{'TOTAL':<{width}}  {'':5}  {'':6}  {'':4}  {total:>7}")
    return 0


def cmd_lint(args) -> int:
    branches = available_branches()
    if not branches:
        print(f"no branch files in {ONTOLOGY_DIR}")
        return 1 if args.strict else 0
    problems: list[str] = []
    for name in branches:
        problems.extend(lint_branch(name))
    for p in problems:
        print(f"WARN {p}")
    print(f"{len(branches)} branches, {len(problems)} problems")
    print_cross_branch_info()  # advisory: never fails --strict
    return 1 if (problems and args.strict) else 0


def cmd_show(args) -> int:
    branch = load_branch(args.branch)
    cats = branch.get("categories", {})
    if args.category:
        entries = cats.get(args.category)
        if entries is None:
            print(f"no category {args.category!r}; have: "
                  + ", ".join(sorted(cats)))
            return 1
        for e in entries:
            if isinstance(e, dict):
                print(f"- {e['name']}: {e.get('definition', '')}")
            else:
                print(f"- {e}")
    else:
        print(f"{branch['name']} ({branch.get('level')}): "
              f"{branch.get('description', '')}")
        for cat, entries in cats.items():
            print(f"  {cat}  [{len(entries)}]")
    return 0


def cmd_find(args) -> int:
    hits = find_entries(args.query)
    if not hits:
        print(f"no entry matching {args.query!r} in "
              f"{len(available_branches())} branches")
        return 1
    for branch, cat, label, e in hits[:args.limit]:
        line = f"{branch}.{cat}: {label}"
        if isinstance(e, dict):
            if e.get("polarity") == "fault":
                line += "  [fault]"
            if e.get("definition"):
                line += f" — {e['definition']}"
        print(line)
    extra = len(hits) - args.limit
    if extra > 0:
        print(f"… and {extra} more (raise --limit)")
    return 0


def cmd_sample(args) -> int:
    spec = args.spec
    branch_name, _, category = spec.partition(".")
    picked = sample_entries(
        branch_name, category or None, n=args.n, seed=args.seed
    )
    for e in picked:
        if isinstance(e, dict):
            line = f"{e['name']} — {e.get('definition', '')}"
            if e.get("example"):
                line += f"  e.g. {e['example']}"
            print(line)
        else:
            print(e)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("stats")
    lint = sub.add_parser("lint")
    lint.add_argument("--strict", action="store_true")
    show = sub.add_parser("show")
    show.add_argument("branch")
    show.add_argument("category", nargs="?")
    samp = sub.add_parser("sample")
    samp.add_argument("spec", help="BRANCH or BRANCH.CATEGORY")
    samp.add_argument("-n", type=int, default=1)
    samp.add_argument("--seed", type=int, default=None)
    fnd = sub.add_parser("find")
    fnd.add_argument("query", help="substring of name/aka/definition")
    fnd.add_argument("--limit", type=int, default=25)
    args = ap.parse_args()
    return {
        "stats": cmd_stats,
        "lint": cmd_lint,
        "show": cmd_show,
        "sample": cmd_sample,
        "find": cmd_find,
    }[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
