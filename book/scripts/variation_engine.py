#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Axes of variation for a passage: N distinct sets of recast directives.

Give it a paragraph or a page; it measures the passage's shape (sentence
count, mean length, longest and shortest sentence) and emits N directive
SETS drawn from the writing ontology
(docs/architecture/writing-ontology.md). Each set pushes the passage in a
DIFFERENT coherent direction — one global axis (register, branching,
rhythm contour, distance) plus 3-5 ontology moves anchored to real
positions in the text ("sentence 9 (41 words) — recast as a periodic
sentence"). The sets are alternatives, not a checklist: pick one, apply
it whole, and compare against the original.

It never rewrites prose. The ontology emits directives; a human — or a
revision pass such as deslop.py — applies them. A set pastes cleanly into
a de-slop fix brief or into an LLM revision prompt.

Input is plain prose from --text FILE or stdin; LaTeX is stripped with the
same cheap regex detex prose_metrics.py uses for paragraph counting, so
chapter excerpts work as-is.

Two exclusions, both from docs/architecture/writing-ontology.md:

  faults            failure modes (diction faults, rhythm faults, figure
                    vices, fallacies, dangling participles) are never
                    emitted as recast directives. --include-faults adds
                    them back in AUDIT phrasing only ("audit sentence 4 for
                    X and repair what it finds"), never as "recast it as X".
  descriptor banks  settings_and_environments and tones_and_moods are
                    ideation nouns and atmosphere labels rather than craft
                    techniques; prompt_roller draws on them, a recast
                    directive does not.

Advisory, always exits 0 once it has a passage. Branch files that do not
exist yet (the ontology is authored incrementally) are named on stderr and
skipped; with no branches at all, each set still carries its global axis.

Usage:
    uv run scripts/variation_engine.py --text draft.txt
    sed -n '40,60p' latex/chapters/ch03.tex | uv run scripts/variation_engine.py
    uv run scripts/variation_engine.py --text draft.txt --seed 7 -n 5
    uv run scripts/variation_engine.py --text draft.txt --include-faults
    uv run scripts/variation_engine.py --text draft.txt --json | jq '.sets[0]'
"""

from __future__ import annotations

import argparse
import json
import random
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import writing_ontology as wo  # noqa: E402

DROP_ENVS = (
    "tikzpicture", "figure", "table", "tabular", "tabularx", "lstlisting",
    "verbatim", "Verbatim", "equation", "align", "alignat", "gather",
)
ABBREV = {
    "mr", "mrs", "ms", "dr", "prof", "sr", "jr", "st", "vs", "etc", "eg",
    "ie", "e.g", "i.e", "cf", "fig", "figs", "no", "nos", "vol", "p", "pp",
    "ch", "sec", "para", "ed", "eds", "al", "inc", "ltd", "u.s", "u.k",
    "ca", "approx",
}

# Global axes: whole-passage directions. Each names a branch whose entries
# make it concrete — if that branch file exists, the set is built around it.
# Branch FILENAMES are the stable contract; categories are never assumed.
AXES = [
    {"tag": "anglo-saxon",
     "directive": "Shift register toward Anglo-Saxon monosyllables — replace "
                  "Latinate abstractions with short native words wherever the "
                  "meaning survives the trade.",
     "branch": "diction_and_register"},
    {"tag": "periodic",
     "directive": "Convert loose sentences to periodic ones in the final "
                  "position of each paragraph — hold the main clause until "
                  "the end so the paragraph lands rather than trails.",
     "branch": "syntactic_constructions"},
    {"tag": "parataxis",
     "directive": "Break the hypotaxis into parataxis — coordinate instead of "
                  "subordinate, and let the order of the clauses carry the "
                  "logic the conjunctions were carrying.",
     "branch": "syntactic_constructions"},
    {"tag": "contour",
     "directive": "Re-cut the length contour — no two adjacent sentences "
                  "within five words of each other, and one sentence under "
                  "eight words in every paragraph.",
     "branch": "sound_and_rhythm"},
    {"tag": "end-stress",
     "directive": "Move the most important word of each sentence into final "
                  "position; nothing trails after the point.",
     "branch": "sound_and_rhythm"},
    {"tag": "concretion",
     "directive": "Push every abstraction one rung down the ladder — name the "
                  "object, the number, the place, the person.",
     "branch": "diction_and_register"},
    {"tag": "figured repetition",
     "directive": "Let one word or one structure recur deliberately across the "
                  "passage until the repetition reads as design rather than "
                  "as accident.",
     "branch": "rhetorical_figures"},
    {"tag": "stripped signposting",
     "directive": "Strip the metadiscourse — delete the signposting and the "
                  "hedges, and make the sentences themselves do the pointing.",
     "branch": "discourse_moves"},
    {"tag": "close focus",
     "directive": "Tighten the distance — move from report and summary toward "
                  "the near view, holding the same tense throughout.",
     "branch": "pov_and_narration"},
    {"tag": "fronted",
     "directive": "Front something other than the subject in a third of the "
                  "sentences — an adverbial, an object, a participial phrase.",
     "branch": "syntactic_constructions"},
    {"tag": "compression",
     "directive": "Cut the passage by a quarter without losing a fact; spend "
                  "the words you save on one concrete detail that is not "
                  "there yet.",
     "branch": "diction_and_register"},
]

# Directive phrasing per branch; unknown branches use GENERIC. Entry names
# are dropped in verbatim, so no template takes an article — ontology names
# range from noun phrases ("nominative absolute") to verb phrases
# ("introduce a deadline") and only article-free frames fit both.
TEMPLATES = {
    "syntactic_constructions": "{anchor} — recast on the {name} construction",
    "rhetorical_figures": "{anchor} — work the figure {name} into it",
    "sound_and_rhythm": "{anchor} — retune for {name}",
    "diction_and_register": "{anchor} — shift the diction with {name}",
    "pov_and_narration": "{anchor} — narrate it through {name}",
    "discourse_moves": "{anchor} — carry the join with {name}",
    "paragraph_shapes": "{anchor} — rebuild the paragraph on the {name} shape",
    "scene_patterns": "{anchor} — restage it on the {name} pattern",
    "openings_and_closings": "{anchor} — rebuild it on the {name} pattern",
    "argumentation_schemes": "{anchor} — carry the claim with {name}",
    "evidence_types": "{anchor} — ground the claim with {name}",
    "interaction_moves": "{anchor} — play the move {name}",
    "character_and_persona": "{anchor} — angle it through {name}",
}
GENERIC = "{anchor} — apply {name}"
# One frame for every fault, whatever branch it came from: a failure mode is
# something to find and remove, never something to recast a sentence into.
AUDIT = "{anchor} — audit it for {name} and repair what it finds"

# Descriptor banks, not craft branches (writing-ontology.md): ideation fuel
# for prompt_roller, never a recast directive. Both are meso files, so they
# would otherwise land in the pool below.
DESCRIPTOR_BANKS = ("settings_and_environments", "tones_and_moods")


# ------------------------------------------------------------ text handling


def light_detex(text: str) -> str:
    """Cheap regex detex (same recipe as prose_metrics.light_detex)."""
    text = re.sub(r"(?<!\\)%.*", "", text)
    for env in DROP_ENVS:
        text = re.sub(rf"\\begin\{{{env}\*?\}}.*?\\end\{{{env}\*?\}}", " ",
                      text, flags=re.DOTALL)
    text = re.sub(r"\$[^$]*\$", " ", text)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", text)
    return re.sub(r"[{}~]", " ", text)


def split_paragraphs(text: str) -> list[str]:
    latex = "\\" in text or "%" in text
    paras = []
    for block in re.split(r"\n\s*\n", text):
        block = block.strip()
        if not block:
            continue
        # runs of lone commands (\chapter{...}\label{...}, \input) aren't
        # paragraphs — the rule prose_metrics.paragraphs_of uses, widened to
        # multi-line command blocks
        if latex and all(ln.lstrip().startswith("\\")
                         for ln in block.splitlines() if ln.strip()):
            continue
        if latex:
            block = light_detex(block)
        block = " ".join(block.split())
        if block:
            paras.append(block)
    return paras


def split_sentences(paragraph: str) -> list[str]:
    """Stdlib sentence split: terminator + space + capital, minus abbreviations."""
    out, start = [], 0
    for m in re.finditer(r"[.!?]['\")\]]*\s+", paragraph):
        head = paragraph[start:m.end()].strip()
        last = re.split(r"[\s(]", head.rstrip("'\")]").rstrip(".!?"))[-1]
        if last.lower().strip(".") in ABBREV or re.fullmatch(r"[A-Z]", last):
            continue
        nxt = paragraph[m.end():m.end() + 1]
        if nxt and not (nxt.isupper() or nxt.isdigit() or nxt in "\"'“‘("):
            continue
        if head:
            out.append(head)
        start = m.end()
    tail = paragraph[start:].strip()
    if tail:
        out.append(tail)
    return out


def measure(text: str) -> dict:
    paras = split_paragraphs(text)
    sents: list[dict] = []
    for pi, para in enumerate(paras, 1):
        for s in split_sentences(para):
            words = len(s.split())
            if words < 2:
                continue
            sents.append({"index": len(sents) + 1, "paragraph": pi,
                          "words": words, "text": s})
    lens = [s["words"] for s in sents]
    total = sum(lens)
    mean = statistics.mean(lens) if lens else 0.0
    sd = statistics.stdev(lens) if len(lens) > 1 else 0.0
    return {
        "paragraphs": len(paras),
        "sentences": len(sents),
        "words": total,
        "mean_len": round(mean, 1),
        "sd_len": round(sd, 1),
        "cv": round(sd / mean, 2) if mean else 0.0,
        "longest": max(sents, key=lambda s: s["words"]) if sents else None,
        "shortest": min(sents, key=lambda s: s["words"]) if sents else None,
        "sents": sents,
    }


def clip(text: str, n: int = 64) -> str:
    text = " ".join(text.split())
    return text if len(text) <= n else text[: n - 1] + "…"


# --------------------------------------------------------------- ontology IO


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


def micro_meso_pools(include_faults: bool = False,
                     ) -> tuple[dict[str, list], dict[str, str], list[str]]:
    """{branch: [(entry, category, fault)]} for every craft micro/meso branch.

    Descriptor banks are skipped outright; faults are skipped unless
    `include_faults`, in which case they are carried with their flag set and
    rendered as audit directives.
    """
    pools: dict[str, list] = {}
    levels: dict[str, str] = {}
    bad: list[str] = []
    for name in wo.available_branches():
        if name in DESCRIPTOR_BANKS:
            continue
        try:
            branch = wo.load_branch(name)
        except (OSError, json.JSONDecodeError) as exc:
            bad.append(f"{name} ({exc})")
            continue
        level = str(branch.get("level", "") or "")
        if level not in ("micro", "meso"):
            continue
        items = [
            (entry, category, is_fault(entry, name, category))
            for category, entries in (branch.get("categories") or {}).items()
            if isinstance(entries, list)
            for entry in entries
        ]
        if not include_faults:
            items = [it for it in items if not it[2]]
        if items:
            pools[name] = items
            levels[name] = level
    return pools, levels, bad


def field(entry, key: str) -> str:
    if isinstance(entry, dict):
        return str(entry.get(key, "") or "").strip()
    return str(entry).strip() if key == "name" else ""


# ------------------------------------------------------------------- anchors


def anchor_pools(shape: dict, rng: random.Random) -> tuple[list[str], list[str]]:
    """Concrete positions in THIS passage: sentence-level, structural.

    Micro moves get aimed at sentences, meso moves at paragraphs and seams.
    """
    sents = shape["sents"]
    sentence_anchors: list[str] = []
    used: set[int] = set()

    def add(s: dict, label: str) -> None:
        if s["index"] in used:
            return
        used.add(s["index"])
        sentence_anchors.append(label)

    if sents:
        lg, sh = shape["longest"], shape["shortest"]
        add(lg, f"your longest sentence (sentence {lg['index']}, "
                f"{lg['words']} words)")
        add(sents[0], f"the opening sentence ({sents[0]['words']} words)")
        if len(sents) > 2:
            add(sents[-1], f"the closing sentence (sentence "
                           f"{sents[-1]['index']}, {sents[-1]['words']} words)")
        add(sh, f"your shortest sentence (sentence {sh['index']}, "
                f"{sh['words']} words)")
        for s in rng.sample(sents, min(5, len(sents))):
            add(s, f"sentence {s['index']} ({s['words']} words)")

    structural = [f"the final position of paragraph {p}"
                  for p in range(1, shape["paragraphs"] + 1)]
    if shape["paragraphs"] > 1:
        structural.append("the seam between the first two paragraphs")
    structural.append("the passage as a whole")
    rng.shuffle(structural)
    return sentence_anchors, structural


NOTE_TEMPLATES = [
    "your longest sentence is {longest_words} words (sentence {longest_idx}) — "
    "split it against directive {d}",
    "mean sentence length is {mean} words with sd {sd}; this set should widen "
    "the spread, not move the average — directive {d} is where it moves",
    "your shortest sentence is {short_words} words (sentence {short_idx}); "
    "leave it short and let directive {d} carry the weight elsewhere",
    "{paragraphs} paragraph(s), {sentences} sentences — apply directive {d} "
    "once in the passage, not once per paragraph",
]


# ------------------------------------------------------------ set generation


def build_set(index: int, axis: dict, pools: dict[str, list],
              levels: dict[str, str], shape: dict,
              rng: random.Random) -> dict:
    branches = sorted(pools)
    if axis["branch"] in pools:  # keep the set coherent with its axis
        branches.remove(axis["branch"])
        rng.shuffle(branches)
        branches.insert(0, axis["branch"])
    else:
        rng.shuffle(branches)
    k = min(rng.randint(3, 5), len(branches))
    sentence_anchors, structural = anchor_pools(shape, rng)

    def take_anchor(level: str) -> str:
        first, second = ((structural, sentence_anchors) if level == "meso"
                         else (sentence_anchors, structural))
        for src in (first, second):
            if src:
                return src.pop(0)
        return "the passage as a whole"

    directives = []
    for i, branch in enumerate(branches[:k]):
        entry, category, fault = rng.choice(pools[branch])
        name = field(entry, "name")
        anchor = take_anchor(levels.get(branch, "micro"))
        template = AUDIT if fault else TEMPLATES.get(branch, GENERIC)
        head = template.format(anchor=anchor, name=name)
        definition = field(entry, "definition")
        directives.append({
            "n": i + 1,
            "branch": branch,
            "level": levels.get(branch, ""),
            "category": category,
            "fault": fault,
            "name": name,
            "definition": definition,
            "example": field(entry, "example"),
            "caution": field(entry, "caution"),
            "anchor": anchor,
            "text": f"{head}: {definition}" if definition else head,
        })

    # the set is named for what it asks you to write, never for a fault it
    # only asks you to audit
    positive = [d for d in directives if not d["fault"]]
    dominant = positive[0]["name"].lower() if positive else "axis only"
    lg, sh = shape["longest"], shape["shortest"]
    note = rng.choice(NOTE_TEMPLATES).format(
        d=rng.randint(1, len(directives)) if directives else 1,
        longest_words=lg["words"] if lg else 0,
        longest_idx=lg["index"] if lg else 0,
        short_words=sh["words"] if sh else 0,
        short_idx=sh["index"] if sh else 0,
        mean=shape["mean_len"], sd=shape["sd_len"],
        paragraphs=shape["paragraphs"], sentences=shape["sentences"],
    )
    return {
        "index": index,
        "title": f"Set {index} — {axis['tag']} + {dominant}",
        "axis": {"tag": axis["tag"], "directive": axis["directive"]},
        "directives": directives,
        "note": note,
    }


# -------------------------------------------------------------------- output


def print_header(shape: dict, seed: int) -> None:
    print(f"Passage shape (seed {seed})")
    print("-" * 66)
    print(f"  {shape['words']} words · {shape['paragraphs']} paragraph(s) · "
          f"{shape['sentences']} sentences · mean {shape['mean_len']} words "
          f"(sd {shape['sd_len']}, cv {shape['cv']})")
    if shape["longest"]:
        lg = shape["longest"]
        print(f"  longest   sentence {lg['index']} — {lg['words']} words: "
              f"\u201c{clip(lg['text'])}\u201d")
    if shape["shortest"]:
        sh = shape["shortest"]
        print(f"  shortest  sentence {sh['index']} — {sh['words']} words: "
              f"\u201c{clip(sh['text'])}\u201d")
    print("  Directives only — this tool never rewrites prose. Each set is a "
          "different direction;\n  apply one whole, then compare against the "
          "original.")
    print()


def print_sets(sets: list[dict]) -> None:
    for s in sets:
        print(s["title"])
        print(f"  axis: {s['axis']['directive']}")
        for d in s["directives"]:
            print(f"  {d['n']}. {d['text']}")
            if d["example"]:
                print(f"       e.g. {clip(d['example'], 96)}")
            if d["caution"]:
                print(f"       caution: {clip(d['caution'], 96)}")
        print(f"  note: {s['note']}")
        print()


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        epilog="\n".join(__doc__.splitlines()[1:]),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--text", type=Path, default=None,
                    help="plain prose (or LaTeX) file; default: stdin")
    ap.add_argument("-n", type=int, default=3, metavar="N",
                    help="number of directive sets (default 3)")
    ap.add_argument("--seed", type=int, default=None,
                    help="reproducibility seed (default: random, reported)")
    ap.add_argument("--include-faults", action="store_true",
                    help="also draw failure modes (diction faults, rhythm "
                         "faults, figure vices, fallacies); they are emitted "
                         "as audit directives — 'audit it for X and repair "
                         "what it finds' — never as recasts")
    ap.add_argument("--json", action="store_true", help="machine-readable")
    args = ap.parse_args()

    if args.n < 1:
        ap.error("-n must be >= 1")
    if args.text is not None:
        try:
            raw = args.text.read_text(encoding="utf-8")
        except OSError as exc:
            raise SystemExit(
                f"variation_engine: cannot read {args.text}: {exc}") from None
    elif not sys.stdin.isatty():
        raw = sys.stdin.read()
    else:
        raise SystemExit("variation_engine: no passage — give --text FILE or "
                         "pipe prose on stdin")

    shape = measure(raw)
    if not shape["sents"]:
        raise SystemExit("variation_engine: empty passage after stripping "
                         "markup — nothing to vary")

    seed = args.seed if args.seed is not None else random.randrange(1, 10**6)
    rng = random.Random(seed)

    pools, levels, bad = micro_meso_pools(args.include_faults)
    for b in bad:
        print(f"variation_engine: WARN unreadable branch {b}", file=sys.stderr)
    if not pools:
        print(f"variation_engine: no micro/meso branch files with entries in "
              f"{wo.ONTOLOGY_DIR} — emitting global axes only (the ontology is "
              f"authored incrementally)", file=sys.stderr)

    axes = list(AXES)
    rng.shuffle(axes)
    while len(axes) < args.n:  # more sets than axes: reuse, still seeded
        extra = list(AXES)
        rng.shuffle(extra)
        axes += extra
    sets = [build_set(i, axes[i - 1], pools, levels, shape, rng)
            for i in range(1, args.n + 1)]

    if args.json:
        header = {k: v for k, v in shape.items() if k != "sents"}
        for key in ("longest", "shortest"):
            if header.get(key):
                header[key] = {kk: vv for kk, vv in header[key].items()
                               if kk != "text"} | {"text": clip(
                                   shape[key]["text"], 120)}
        print(json.dumps({
            "seed": seed,
            "shape": header,
            "branches_used": sorted(pools),
            "sets": sets,
        }, indent=2))
    else:
        print_header(shape, seed)
        print_sets(sets)
    return 0


if __name__ == "__main__":
    sys.exit(main())
