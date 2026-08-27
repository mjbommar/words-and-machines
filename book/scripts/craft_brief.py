#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""craft_brief.py -- one markdown craft brief per chapter: the whole
craft diagnosis, what the chapter owes its reader, and what to reach for.

`make craft` runs seven diagnostics and prints seven reports. Reading
them means holding seven tables in your head and doing the join yourself:
the arc is flat *here*, the cadence run is *there*, and the ontology
entry that answers both is somewhere in a 5,000-entry taxonomy. This
script does that join. It shells out to the seven diagnostics, slices
their output per chapter, and writes ONE brief per chapter that a human
(or a revision agent) can act on top to bottom:

  1. What this chapter does now   arc sparkline + range, discourse-move
                                  sequence and distribution, register
                                  numbers against the profile bands,
                                  cadence distribution, figure inventory,
                                  construction profile
  2. Where it is monotone         every WARN the tools raised, verbatim,
                                  plus the signals that sit below the
                                  warning line: opener share and runs,
                                  uniform-length paragraphs, cadence
                                  runs, discourse-move monotony
  3. What is owed                 unpaid / uncertain promises made in
                                  this chapter (questions raised, terms
                                  introduced, entities named once)
  4. What to reach for            5-7 seeded ontology entries chosen to
                                  answer the findings in section 2 --
                                  each with name, definition, example,
                                  and the finding it answers
  5. Paste-ready                  (a) a drafting palette in
                                  palette_sampler --for-prompt shape;
                                  (b) a fix brief in the anchor shape
                                  deslop.py --batch emits, with real
                                  file:line references

Nothing here measures anything itself and nothing here edits prose. It is
a composer: every number is carried through from a sibling script, every
suggestion comes from scripts/data/ontology/. Advisory, exit 0 always --
a tool that fails is reported as a missing section, not a crash.

Suggestions never include faults (writing_ontology.is_fault) and never
draw on the descriptor banks (settings_and_environments, tones_and_moods),
which are ideation fuel rather than craft technique.

Scope note: setup_payoff is deliberately run WITHOUT --chapter even when
you ask for one chapter. A promise made in ch03 is often paid in ch07,
and a chapter-scoped payoff audit would report those as unpaid. Every
other tool gets --chapter passed through.

Usage:
    uv run scripts/craft_brief.py                       # every chapter
    uv run scripts/craft_brief.py --chapter ch03        # one chapter
    uv run scripts/craft_brief.py --text draft.txt      # arbitrary prose
    uv run scripts/craft_brief.py --out docs/review-01/ # one file each
    uv run scripts/craft_brief.py --root ../other-book
    uv run scripts/craft_brief.py --seed 7              # reproducible picks
    uv run scripts/craft_brief.py --skip move_annotator --skip arc_profiler
    uv run scripts/craft_brief.py --chapter ch02 --json

    make brief                        # every chapter, to stdout
    make brief CHAPTER=ch02 OUT=docs/review-01

LIMITS
  - Composition only: every measurement inherits its source tool's
    limits (POS-lite openers, lexicon-based valence, cue-based move
    labels). Read those docstrings before trusting a number.
  - Register "bands" are shown as pass/over-band, not as numeric
    targets: the thresholds live in register_report's style profile and
    reach this script only through its warning text.
  - figure_detector does not carry warnings in its JSON, so the
    heavy-figuration flag is recomputed here from density and word count
    with that tool's documented defaults.
  - Fault exclusion is writing_ontology.is_fault plus a narrow cue list
    (UNMARKED_FAULT_CUES) for entries that describe a failure mode
    without carrying `polarity: fault`. The cue list is a stopgap, not a
    classifier; the fix belongs in the branch files.
  - The fix-brief block proposes directives, never rewrites. Feed the
    same anchors to `deslop.py --batch` if you want model rewrites.
  - One brief per chapter file; multi-file chapters are not merged.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"

# tool -> (json shape, pass --chapter through, accepts --seed)
#   "doc"   one JSON document on stdout
#   "lines" JSON Lines, one object per chapter
TOOLS: dict[str, dict] = {
    "construction_variety": {"shape": "doc", "chapter": True, "seed": True},
    "figure_detector": {"shape": "doc", "chapter": True, "seed": True},
    "rhythm_audit": {"shape": "lines", "chapter": True, "seed": True},
    "register_report": {"shape": "lines", "chapter": True, "seed": True},
    "arc_profiler": {"shape": "lines", "chapter": True, "seed": True},
    # corpus-wide on purpose: payoff can land in any later chapter
    "setup_payoff": {"shape": "doc", "chapter": False, "seed": False},
    "move_annotator": {"shape": "doc", "chapter": True, "seed": False},
}

# ideation fuel, not craft technique (writing-ontology.md, "Descriptor banks")
EXCLUDED_BRANCHES = ("settings_and_environments", "tones_and_moods")

# writing_ontology.is_fault is the rule; these cues are a stopgap for the
# handful of entries that name a failure mode in prose ("stress lapse",
# "dangling absolute") without carrying polarity: fault in the data. A
# positive directive must never be a defect. Deliberately narrow: this
# excludes ~7 entries out of the ~750 these pools draw on.
UNMARKED_FAULT_CUES = (
    "the cure is", "failure mode", "almost always a fault", "unintended",
    "unintentionally", "rhythmic vacuum", "no identifiable cause",
    "none intended", "and is not;",
)

SPARK = "▁▂▃▄▅▆▇█"
ARROW = " → "
DASH = "—"

# figure_detector defaults (its JSON carries no warnings; recompute)
FIG_MAX_DENSITY = 15.0
FIG_DENSITY_FLOOR = 200

# thresholds for the soft signals -- deliberately looser than each tool's
# own --strict gates, because this is a "look here" list, not a gate
TOP_OPENER_SHARE = 0.65
LOW_ODI = 0.25
TOP_CADENCE_SHARE = 0.30
THIN_FIGURE_DENSITY = 3.0
FLAT_RANGE = 0.30

# ---------------------------------------------------------------- pools
# Each finding kind names the ontology it should be answered from, as
# (branch, [categories]) pairs. Categories that do not exist are skipped,
# so the pools survive ontology reshuffles.
POOLS: dict[str, list[tuple[str, list[str]]]] = {
    "opener": [
        ("syntactic_constructions", [
            "focus_constructions", "modifier_placement",
            "participial_and_appositive", "absolute_constructions",
            "sentence_architectures"]),
    ],
    "length": [
        ("sound_and_rhythm", ["sentence_length_contours", "paragraph_rhythm"]),
        ("syntactic_constructions", ["sentence_length_moves"]),
    ],
    "cadence": [
        ("sound_and_rhythm", [
            "prose_cadence", "rhythm_moves", "pause_and_punctuation_rhythm"]),
    ],
    "moves": [
        ("discourse_moves", [
            "coherence_relations", "transition_families",
            "signposting_moves"]),
        ("paragraph_shapes", [
            "expository_shapes", "argumentative_shapes",
            "transitional_shapes"]),
    ],
    "move_gaps": [
        ("discourse_moves", [
            "reader_management_moves", "framing_moves",
            "metadiscourse_moves"]),
        ("interaction_moves", ["argumentative_exchange_moves"]),
    ],
    "figures": [
        ("rhetorical_figures", [
            "repetition_figures", "balance_and_antithesis_figures",
            "word_order_figures", "omission_and_brevity_figures",
            "amplification_and_addition_figures"]),
    ],
    "restraint": [
        ("syntactic_constructions", [
            "sentence_length_moves", "ellipsis_and_compression"]),
        ("sound_and_rhythm", ["rhythm_moves"]),
    ],
    "arc": [
        ("arc_shapes", [
            "tension_curves", "epistemic_arcs", "rise_and_fall_families"]),
        ("scene_patterns", ["pacing_moves"]),
    ],
    "register": [
        # register_levels and naming_strategies are descriptive labels
        # (journalese, style sheet entry), not repairs for a register
        # warning -- these three are the moves that fix one
        ("diction_and_register", [
            "verb_strength_moves", "precision_moves", "etymological_layers"]),
    ],
    "owed": [
        ("openings_and_closings", [
            "chapter_closings", "essay_closers", "false_endings_and_codas"]),
        ("discourse_moves", ["signposting_moves"]),
    ],
    "default": [
        ("syntactic_constructions", ["focus_constructions"]),
        ("sound_and_rhythm", ["rhythm_moves"]),
        ("discourse_moves", ["coherence_relations"]),
        ("rhetorical_figures", ["repetition_figures"]),
        ("paragraph_shapes", ["expository_shapes"]),
    ],
}

# WARN text -> finding kind, in priority order (first substring wins)
WARN_KINDS: list[tuple[tuple[str, ...], str]] = [
    (("opener", "subject-first", "opener-diversity"), "opener"),
    (("cadence", "cursus", "sentence-final"), "cadence"),
    (("uniform", "length", "plateau", "monotone rhythm"), "length"),
    (("hedge", "booster", "attitude", "nominal", "latinate", "contraction"),
     "register"),
    (("figure density",), "restraint"),
    (("valence", "tension", "arc", "flat", "slope"), "arc"),
    (("move", "transition"), "moves"),
]


# ------------------------------------------------------------- plumbing


def squash(text: str, limit: int = 240) -> str:
    """One line, collapsed whitespace, truncated for a markdown quote."""
    out = re.sub(r"\s+", " ", str(text)).strip()
    return out if len(out) <= limit else out[: limit - 1].rstrip() + "…"


def run_tool(tool: str, root: Path, chapter: str | None,
             text: Path | None, seed: int) -> tuple[object, str]:
    """Invoke a sibling diagnostic. Returns (parsed, error-note).

    uv scripts are not importable and sys.executable is not their
    interpreter, so every tool is a subprocess: `uv run scripts/X.py`
    from the template repo root, with --root pointing at the book.
    """
    spec = TOOLS[tool]
    cmd = ["uv", "run", f"scripts/{tool}.py", "--json"]
    if text is not None:
        cmd += ["--text", str(text)]
    else:
        cmd += ["--root", str(root)]
        if chapter and spec["chapter"]:
            cmd += ["--chapter", chapter]
    if spec["seed"]:
        cmd += ["--seed", str(seed)]
    try:
        proc = subprocess.run(cmd, cwd=REPO, capture_output=True,
                              text=True, timeout=600, check=False)
    except FileNotFoundError:
        return None, "`uv` not on PATH"
    except OSError as exc:
        return None, f"could not run: {exc}"
    except subprocess.TimeoutExpired:
        return None, "timed out after 600s"
    if proc.returncode != 0:
        why = (proc.stderr or proc.stdout or "").strip().splitlines()
        return None, (why[-1] if why else f"exit {proc.returncode}")
    body = proc.stdout.strip()
    if not body:
        return None, "produced no output"
    # the tools mix plain "note:" lines into stdout alongside their JSON,
    # so parse tolerantly and report the prose back as the reason when
    # there is no JSON at all ("nothing long enough to analyze")
    lines = [ln for ln in body.splitlines() if ln.strip()]
    if spec["shape"] == "lines":
        rows = []
        for line in lines:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return (rows, "") if rows else (None, squash(lines[-1], 120))
    start = next((i for i, ln in enumerate(lines)
                  if ln.lstrip().startswith(("{", "["))), None)
    if start is None:
        return None, squash(lines[-1], 120)
    try:
        return json.loads("\n".join(lines[start:])), ""
    except json.JSONDecodeError as exc:
        return None, f"unreadable JSON ({exc})"


def collect(root: Path, chapter: str | None, text: Path | None,
            seed: int, skip: set[str]) -> tuple[dict, dict]:
    """Run every non-skipped tool once. Returns (data, errors)."""
    data: dict[str, object] = {}
    errors: dict[str, str] = {}
    for tool in TOOLS:
        if tool in skip:
            continue
        parsed, err = run_tool(tool, root, chapter, text, seed)
        if err:
            errors[tool] = err
        else:
            data[tool] = parsed
    return data, errors


def by_file(records, key: str = "file") -> dict[str, list]:
    out: dict[str, list] = {}
    for rec in records or []:
        out.setdefault(rec.get(key, "?"), []).append(rec)
    return out


def slice_chapters(data: dict, chapter: str | None,
                   prose_only: bool = True) -> dict[str, dict]:
    """Regroup every tool's output by chapter file name.

    ``prose_only`` drops files that no prose-scale tool could measure —
    the front and back matter (copyright, dedication, colophon) that
    lives under latex/ and has nothing a craft brief can say about it.
    """
    cv = {u["file"]: u for u in (data.get("construction_variety") or {}).get(
        "units", [])}
    fd = {u["file"]: u for u in (data.get("figure_detector") or {}).get(
        "units", [])}
    ra = {m["file"]: m for m in (data.get("rhythm_audit") or [])}
    rr = {m["file"]: m for m in (data.get("register_report") or [])}
    ap = {m["file"]: m for m in (data.get("arc_profiler") or [])}
    sp = data.get("setup_payoff") or {}
    promises = by_file(sp.get("promises"))
    ma = data.get("move_annotator") or {}
    paras = by_file(ma.get("paragraphs"))
    monotony = by_file(ma.get("monotony"))
    dist = (ma.get("distribution") or {}).get("by_file", {})
    builtin = sorted(name for name, meta in (ma.get("inventory") or {}).items()
                     if meta.get("origin") == "builtin")

    names: set[str] = set()
    for src in (cv, fd, ra, rr, ap, promises, paras, monotony, dist):
        names |= set(src)
    substantial = set(cv) | set(ra) | set(rr) | set(ap)
    if prose_only and substantial:
        names &= substantial
    if chapter:
        names = {n for n in names if n.startswith(chapter)}
    return {
        name: {
            "file": name,
            "cv": cv.get(name),
            "fd": fd.get(name),
            "ra": ra.get(name),
            "rr": rr.get(name),
            "ap": ap.get(name),
            "promises": promises.get(name, []),
            "paras": paras.get(name, []),
            "monotony": monotony.get(name, []),
            "moves": dist.get(name, {}),
            "builtin_moves": builtin,
        }
        for name in sorted(names)
    }


# -------------------------------------------------------------- ontology


def load_ontology():
    """Import the ontology library, or None when it is not built."""
    sys.path.insert(0, str(SCRIPTS))
    try:
        import writing_ontology
    except ImportError:
        return None
    if not writing_ontology.available_branches():
        return None
    return writing_ontology


def unmarked_fault(entry: dict) -> bool:
    """Fault the data forgot to mark; see UNMARKED_FAULT_CUES."""
    blob = " ".join(str(entry.get(k, "")) for k in
                    ("name", "definition", "effect", "caution")).lower()
    return any(cue in blob for cue in UNMARKED_FAULT_CUES)


def pool_entries(onto, pairs: list[tuple[str, list[str]]]) -> list[dict]:
    """Every usable record in a pool: no faults, no descriptor banks."""
    out: list[dict] = []
    for branch_name, cats in pairs:
        if branch_name in EXCLUDED_BRANCHES:
            continue
        try:
            branch = onto.load_branch(branch_name)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        categories = branch.get("categories", {})
        for cat in cats:
            for entry in categories.get(cat, []):
                if onto.is_fault(entry, cat) or not isinstance(entry, dict):
                    # bare `term` entries carry no definition, and a
                    # suggestion without one is not actionable
                    continue
                if not entry.get("definition") or unmarked_fault(entry):
                    continue
                out.append({**entry, "_branch": branch_name, "_category": cat})
    return out


def pick_suggestions(onto, findings: list[dict], chapter: str,
                     seed: int, want: int) -> list[dict]:
    """One entry per finding, best findings first, then filler.

    Findings are re-ordered so the first occurrence of each *kind* comes
    first: a chapter with six opener findings and one cadence finding
    should still be told something about cadence.
    """
    if onto is None:
        return []
    picked: list[dict] = []
    seen: set[str] = set()
    first, rest, kinds = [], [], set()
    for finding in findings:
        if finding["kind"] in kinds:
            rest.append(finding)
        else:
            kinds.add(finding["kind"])
            first.append(finding)
    queue = first + rest + [
        {"kind": "default", "text": "general variety (no finding to answer)"}
        for _ in range(want)
    ]
    for i, finding in enumerate(queue):
        if len(picked) >= want:
            break
        pairs = POOLS.get(finding["kind"], POOLS["default"])
        pool = [e for e in pool_entries(onto, pairs)
                if e["name"].lower() not in seen]
        if not pool:
            continue
        rng = random.Random(f"{seed}|{chapter}|{finding['kind']}|{i}")
        entry = rng.choice(pool)
        seen.add(entry["name"].lower())
        picked.append({**entry, "_answers": finding["text"],
                       "_kind": finding["kind"]})
    return picked


# -------------------------------------------------------------- findings


def warn_kind(text: str) -> str:
    low = text.lower()
    for needles, kind in WARN_KINDS:
        if any(n in low for n in needles):
            return kind
    return "default"


def gather_warnings(ch: dict) -> list[tuple[str, str]]:
    """(tool, warning) for every WARN the tools raised on this chapter."""
    warns: list[tuple[str, str]] = []
    for tool, key in (("construction_variety", "cv"), ("rhythm_audit", "ra"),
                      ("register_report", "rr"), ("arc_profiler", "ap")):
        unit = ch.get(key) or {}
        warns += [(tool, w) for w in unit.get("warnings", [])]
    fd = ch.get("fd") or {}
    if fd.get("density", 0) > FIG_MAX_DENSITY and \
            fd.get("words", 0) >= FIG_DENSITY_FLOOR:
        warns.append(("figure_detector",
                      f"figure density {fd['density']}/1k > "
                      f"{FIG_MAX_DENSITY}/1k — heavily figured prose"))
    return warns


def gather_findings(ch: dict, warns: list[tuple[str, str]]) -> list[dict]:
    """Everything section 2 lists, ranked; section 4 answers these."""
    out: list[dict] = []
    for tool, text in warns:
        out.append({"kind": warn_kind(text), "severity": 2, "tool": tool,
                    "text": text, "anchor": None, "quote": ""})

    cv = ch.get("cv") or {}
    if cv and cv.get("top_share", 0) >= TOP_OPENER_SHARE:
        out.append({
            "kind": "opener", "severity": 1, "tool": "construction_variety",
            "text": f"{cv['top_class']} opens {cv['top_share']:.0%} of "
                    f"{cv['sents']} sentences",
            "anchor": None, "quote": ""})
    if cv and cv.get("odi", 1.0) < LOW_ODI:
        out.append({
            "kind": "opener", "severity": 1, "tool": "construction_variety",
            "text": f"opener diversity odi {cv['odi']} (below {LOW_ODI})",
            "anchor": None, "quote": ""})
    for run in (cv.get("runs") or [])[:3]:
        if run.get("kind") != "class" or run.get("length", 0) < 3:
            continue
        sents = run.get("sentences") or []
        out.append({
            "kind": "opener", "severity": 1, "tool": "construction_variety",
            "text": f"{run['length']} consecutive {run['key']} openers "
                    f"at line {run['line']}",
            "anchor": run.get("line"),
            "quote": squash(sents[0]["text"]) if sents else ""})

    ra = ch.get("ra") or {}
    if ra and ra.get("top_share", 0) >= TOP_CADENCE_SHARE:
        out.append({
            "kind": "cadence", "severity": 1, "tool": "rhythm_audit",
            "text": f"{ra['top_cadence']} endings on "
                    f"{ra['top_share']:.0%} of sentences",
            "anchor": None, "quote": ""})
    for run in (ra.get("runs") or [])[:3]:
        if run.get("length", 0) < 3:
            continue
        out.append({
            "kind": "cadence", "severity": 1, "tool": "rhythm_audit",
            "text": f"{run['length']} consecutive {run['cadence']} endings "
                    f"from sentence {run['at_sentence']}",
            "anchor": None,
            "quote": squash(run.get("sample", ""))})
    for para in (ra.get("uniform_band_paras") or [])[:3]:
        out.append({
            "kind": "length", "severity": 1, "tool": "rhythm_audit",
            "text": f"paragraph {para['paragraph']} sits entirely in the "
                    f"{para['band']}-word band "
                    f"({', '.join(str(n) for n in para['lengths'])})",
            "anchor": None,
            "quote": squash(para.get("opening", ""))})

    for run in (ch.get("monotony") or [])[:3]:
        out.append({
            "kind": "moves", "severity": 1, "tool": "move_annotator",
            "text": f"{run['length']} consecutive '{run['move']}' paragraphs "
                    f"({run['start_para']}–{run['end_para']})",
            "anchor": run.get("line"), "quote": ""})
    moves, builtin = ch.get("moves") or {}, ch.get("builtin_moves") or []
    missing = [m for m in ("concession", "contrast", "question", "evidence",
                           "comparison", "narrative") if m in builtin
               and m not in moves]
    if moves and missing:
        out.append({
            "kind": "move_gaps", "severity": 1, "tool": "move_annotator",
            "text": "no paragraph labelled " +
                    ", ".join(missing[:4]) + " in this chapter",
            "anchor": None, "quote": ""})

    fd = ch.get("fd") or {}
    if fd and fd.get("words", 0) >= FIG_DENSITY_FLOOR and \
            fd.get("density", 0) < THIN_FIGURE_DENSITY:
        out.append({
            "kind": "figures", "severity": 1, "tool": "figure_detector",
            "text": f"figure density {fd['density']}/1k — the sentences "
                    "are doing the work unaided",
            "anchor": None, "quote": ""})

    ap = ch.get("ap") or {}
    if ap and ap.get("valence_range", 1.0) < FLAT_RANGE:
        out.append({
            "kind": "arc", "severity": 1, "tool": "arc_profiler",
            "text": f"valence range {ap['valence_range']} across "
                    f"{ap.get('windows')} windows — flat line of feeling",
            "anchor": None, "quote": squash(ap.get("peak", {}).get(
                "opening", ""), 120)})
    if ap and ap.get("tension_range", 1.0) < FLAT_RANGE:
        out.append({
            "kind": "arc", "severity": 1, "tool": "arc_profiler",
            "text": f"tension range {ap['tension_range']} — nothing is "
                    "at stake anywhere in particular",
            "anchor": None, "quote": ""})

    unpaid = [p for p in ch.get("promises", [])
              if p.get("status") in ("unpaid", "uncertain")]
    if unpaid:
        first = unpaid[0]
        out.append({
            "kind": "owed", "severity": 1, "tool": "setup_payoff",
            "text": f"{len(unpaid)} promise(s) made here are unpaid or "
                    f"uncertain (first: “{first['promise']}”, "
                    f"line {first['line']})",
            "anchor": first.get("line"), "quote": ""})

    out.sort(key=lambda f: -f["severity"])
    return out


# ---------------------------------------------------------------- render


def sparkline(series: list[float]) -> str:
    vals = [v for v in (series or []) if isinstance(v, (int, float))]
    if not vals:
        return ""
    lo, hi = min(vals), max(vals)
    if hi - lo < 1e-9:
        return SPARK[len(SPARK) // 2] * len(vals)
    span = len(SPARK) - 1
    return "".join(SPARK[round((v - lo) / (hi - lo) * span)] for v in vals)


def pct_line(counts: dict, unit: str = "", top: int = 8) -> str:
    items = sorted(counts.items(), key=lambda kv: -kv[1])[:top]
    return " | ".join(f"{k} {v}{unit}" for k, v in items if v)


def section_now(ch: dict, missing: dict) -> list[str]:
    md = ["## 1. What this chapter does now", ""]

    ap = ch.get("ap")
    if ap:
        md += [
            f"- **Arc** (arc_profiler, {ap.get('windows')} windows over "
            f"{ap.get('words')} words)",
            f"    - valence `{sparkline(ap.get('valence'))}` "
            f"range {ap.get('valence_range')}, mean {ap.get('valence_mean')}, "
            f"slope {ap.get('slope')}",
            f"    - tension `{sparkline(ap.get('tension'))}` "
            f"range {ap.get('tension_range')}, mean {ap.get('tension_mean')}",
        ]
        peak, trough = ap.get("peak") or {}, ap.get("trough") or {}
        if peak:
            md.append(f"    - peak at {peak.get('position', 0):.0%}: "
                      f"“{squash(peak.get('opening', ''), 90)}”")
        if trough:
            md.append(f"    - trough at {trough.get('position', 0):.0%}: "
                      f"“{squash(trough.get('opening', ''), 90)}”")
    else:
        md.append(f"- **Arc** {DASH} {missing.get('arc_profiler', 'no data')}")

    paras, moves = ch.get("paras") or [], ch.get("moves") or {}
    if paras or moves:
        seq = [p.get("move", "?") for p in paras]
        shown = ARROW.join(seq[:14]) + (" …" if len(seq) > 14 else "")
        md += [
            f"- **Discourse moves** (move_annotator, {len(paras)} paragraphs)",
            f"    - sequence: {shown}" if shown else
            "    - sequence: (no labelled paragraphs)",
            f"    - distribution: {pct_line(moves, top=10)}",
        ]
        unused = [m for m in (ch.get("builtin_moves") or []) if m not in moves]
        if unused:
            md.append(f"    - core families unused here ({len(unused)}): "
                      + ", ".join(unused))
    else:
        md.append(f"- **Discourse moves** {DASH} "
                  f"{missing.get('move_annotator', 'no data')}")

    rr = ch.get("rr")
    if rr:
        over = {w.split()[0].lower() for w in rr.get("warnings", [])}
        band = ("all metrics inside the profile bands" if not over
                else "over band: " + ", ".join(sorted(over)))
        md += [
            f"- **Register** (register_report, {rr.get('words')} words)",
            f"    - hedges {rr.get('hedge_per_1000')}/1k | boosters "
            f"{rr.get('booster_per_1000')}/1k | attitude "
            f"{rr.get('attitude_per_1000')}/1k | nominalizations "
            f"{rr.get('nominalization_per_1000')}/1k",
            f"    - Latinate share {rr.get('latinate_ratio')} | contractions "
            f"{rr.get('contraction_per_1000')}/1k | 1st person "
            f"{rr.get('first_person_per_1000')}/1k | 2nd person "
            f"{rr.get('second_person_per_1000')}/1k",
            f"    - vs bands: {band}",
        ]
        for note in rr.get("notes", []):
            md.append(f"    - note: {note}")
    else:
        md.append(f"- **Register** {DASH} "
                  f"{missing.get('register_report', 'no data')}")

    ra = ch.get("ra")
    if ra:
        md += [
            f"- **Cadence** (rhythm_audit, {ra.get('sents')} sentences, mean "
            f"{ra.get('mean_len')} words, cursus {ra.get('cursus_pct')}%)",
            "    - endings: " + pct_line(ra.get("cadence_pct") or {}, "%"),
            "    - paragraph contours: " + pct_line(ra.get("contours") or {}),
        ]
    else:
        md.append(f"- **Cadence** {DASH} "
                  f"{missing.get('rhythm_audit', 'no data')}")

    fd = ch.get("fd")
    if fd:
        counts = fd.get("counts") or {}
        used = {k: v for k, v in counts.items() if v}
        absent = [k for k, v in counts.items() if not v]
        md += [
            f"- **Figures** (figure_detector, {fd.get('total')} in "
            f"{fd.get('words')} words = {fd.get('density')}/1k)",
            "    - present: " + (pct_line(used, top=12) or "none detected"),
        ]
        if absent:
            md.append(f"    - absent: {', '.join(absent)}")
    else:
        md.append(f"- **Figures** {DASH} "
                  f"{missing.get('figure_detector', 'no data')}")

    cv = ch.get("cv")
    if cv:
        openers = cv.get("openers") or {}
        total = max(1, cv.get("sents", 1))
        share = {k: f"{v / total:.0%}" for k, v in
                 sorted(openers.items(), key=lambda kv: -kv[1])}
        md += [
            f"- **Constructions** (construction_variety, {cv.get('sents')} "
            f"sentences, mean {cv.get('mean_len')} words, odi {cv.get('odi')})",
            "    - openers: " + " | ".join(f"{k} {v}" for k, v in
                                           list(share.items())[:8]),
            "    - length bands: " + pct_line(cv.get("bands") or {}),
            "    - architecture: " + pct_line(cv.get("architecture") or {}),
        ]
    else:
        md.append(f"- **Constructions** {DASH} "
                  f"{missing.get('construction_variety', 'no data')}")

    md.append("")
    return md


def section_monotone(warns, findings) -> list[str]:
    md = ["## 2. Where it is monotone", ""]
    if warns:
        md.append("**Warnings, verbatim:**")
        md.append("")
        md += [f"- `WARN` ({tool}) {text}" for tool, text in warns]
        md.append("")
    else:
        md += ["No tool raised a warning on this chapter.", ""]
    soft = [f for f in findings if f["severity"] < 2]
    if soft:
        md.append("**Below the warning line:**")
        md.append("")
        for f in soft:
            line = f"- ({f['tool']}) {f['text']}"
            if f.get("quote"):
                line += f"\n    > {f['quote']}"
            md.append(line)
        md.append("")
    elif warns:
        md += ["Nothing else crossed the softer thresholds.", ""]
    else:
        md += ["Nothing crossed the softer thresholds either — read the "
               "numbers in section 1 and trust your ear.", ""]
    return md


def section_owed(ch: dict, missing: dict, chapter_scope: bool) -> list[str]:
    md = ["## 3. What is owed", ""]
    if "setup_payoff" in missing:
        return md + [f"setup_payoff {DASH} {missing['setup_payoff']}", ""]
    promises = ch.get("promises", [])
    open_ones = [p for p in promises
                 if p.get("status") in ("unpaid", "uncertain")]
    scope = ("audited across the whole book, so a payoff in a later "
             "chapter counts" if chapter_scope else
             "audited over the given text only")
    if not promises:
        return md + [f"No promises detected in this chapter ({scope}).", ""]
    if not open_ones:
        return md + [f"All {len(promises)} promise(s) made here are paid "
                     f"({scope}).", ""]
    md += [f"{len(open_ones)} of {len(promises)} promise(s) made in this "
           f"chapter are still open ({scope}).", ""]
    for p in open_ones[:20]:
        md.append(
            f"- **{p.get('status')}** {p.get('kind')} "
            f"“{p.get('promise')}” {DASH} line {p.get('line')}"
            + (f", §{p['section']}" if p.get("section") else "")
            + (f" {DASH} {p['evidence']}" if p.get("evidence") else ""))
    if len(open_ones) > 20:
        md.append(f"- … and {len(open_ones) - 20} more "
                  "(`uv run scripts/setup_payoff.py --status unpaid`)")
    md.append("")
    return md


def section_reach(picks: list[dict], onto_ok: bool, seed: int) -> list[str]:
    md = ["## 4. What to reach for", ""]
    if not onto_ok:
        return md + ["The writing ontology is not available under "
                     "`scripts/data/ontology/`, so there is nothing to "
                     "sample.", ""]
    if not picks:
        return md + ["No usable ontology entries matched this chapter's "
                     "findings.", ""]
    md += [f"Seeded picks (seed {seed}), each chosen to answer a finding "
           "above. Faults and descriptor banks excluded; suggestions still "
           "have to pass `make check`.", ""]
    for i, e in enumerate(picks, 1):
        md.append(f"{i}. **{e['name']}** "
                  f"*({e['_branch']}/{e['_category']})*")
        md.append(f"    - answers: {e['_answers']}")
        if e.get("definition"):
            md.append(f"    - {e['definition']}")
        if e.get("example"):
            md.append(f"    - e.g. {squash(e['example'], 300)}")
        if e.get("effect"):
            md.append(f"    - effect: {squash(e['effect'], 200)}")
        if e.get("caution"):
            md.append(f"    - caution: {squash(e['caution'], 200)}")
    md.append("")
    return md


def palette_block(picks: list[dict], name: str, seed: int) -> list[str]:
    """A drafting palette in palette_sampler --for-prompt shape."""
    lines = [
        f"CONSTRUCTION PALETTE (craft_brief seed {seed} {DASH} {name})",
        "Write with these tools available. Rules:",
        "  - at most one palette move per paragraph;",
        "  - do not use every item — unused items are free, forced "
        "items are not;",
        "  - never name the technique in the prose.",
        "",
    ]
    grouped: dict[str, list[dict]] = {}
    for e in picks:
        grouped.setdefault(e["_branch"], []).append(e)
    for branch, entries in grouped.items():
        lines.append(branch.replace("_", " ").upper())
        for e in entries:
            lines.append(f"  - {e['name']}: {e.get('definition', '')}")
            if e.get("example"):
                lines.append(f"      e.g. {squash(e['example'], 300)}")
    cautions = [e for e in picks if e.get("caution")]
    if cautions:
        lines += ["", "OVERUSE WARNINGS"]
        lines += [f"  - {e['name']}: {squash(e['caution'], 200)}"
                  for e in cautions]
    return lines


def fixbrief_block(name: str, findings: list[dict], picks: list[dict],
                   promises: list[dict], seed: int) -> list[str]:
    """Terse per-issue directives in the anchor shape deslop --batch emits."""
    def directive(entry: dict) -> str:
        return (f"recast on **{entry['name']}** — "
                f"{squash(entry.get('definition', ''), 140)}")

    by_kind: dict[str, list[dict]] = {}
    for e in picks:
        by_kind.setdefault(e["_kind"], []).append(e)
    directives = [directive(e) for e in picks] or [
        "vary the shape; see section 1"]
    issues = [f for f in findings if f["kind"] != "owed"][:8]
    lines = [
        f"# Craft fix brief — {name}",
        "",
        f"Source: `craft_brief.py` (seed {seed}) — {len(issues)} issue(s)"
        f" + {min(3, len(promises))} open promise(s). Directives only, no "
        "rewrites: apply by hand, or feed the same anchors to "
        "`uv run scripts/deslop.py --batch`.",
        "",
    ]
    for i, f in enumerate(issues):
        anchor = f"{name}:{f['anchor']}" if f.get("anchor") else name
        lines += [f"## {anchor} — {squash(f['text'], 110)}", ""]
        lines.append(f"- diagnosis: {f['tool']} {DASH} {f['text']}")
        # answer each issue from the pool its own kind selected, so the
        # directive addresses the finding rather than the reading order
        same = by_kind.get(f["kind"])
        lines.append("- directive: " + (directive(same[i % len(same)]) if same
                                        else directives[i % len(directives)]))
        if f.get("quote"):
            lines += ["", "**Original:**", f"> {f['quote']}"]
        lines.append("")
    for p in promises[:3]:
        lines += [
            f"## {name}:{p.get('line')} — unpaid {p.get('kind')} "
            f"“{p.get('promise')}”",
            "",
            f"- diagnosis: setup_payoff {DASH} {p.get('evidence', '')}",
            "- directive: pay it, cut it, or move it — a term introduced "
            "and dropped reads as throat-clearing.",
            "",
        ]
    return lines


def section_paste(name: str, picks: list[dict], findings: list[dict],
                  promises: list[dict], seed: int, onto_ok: bool) -> list[str]:
    md = ["## 5. Paste-ready", "", "### 5a. Drafting palette", ""]
    if onto_ok and picks:
        md += ["Hand this to a drafting or revision model "
               "(`palette_sampler --for-prompt` shape):", "", "```text"]
        md += palette_block(picks, name, seed)
        md += ["```", ""]
    else:
        md += ["No ontology entries available for a palette.", ""]
    md += ["### 5b. Fix brief", "", "```markdown"]
    md += fixbrief_block(name, findings, picks, promises, seed)
    md += ["```", ""]
    return md


def build_brief(ch: dict, missing: dict, onto, seed: int, want: int,
                root: Path, chapter_scope: bool) -> tuple[str, dict]:
    name = ch["file"]
    warns = gather_warnings(ch)
    findings = gather_findings(ch, warns)
    picks = pick_suggestions(onto, findings, name, seed, want)
    open_promises = [p for p in ch.get("promises", [])
                     if p.get("status") in ("unpaid", "uncertain")]

    md = [f"# Craft brief — {name}", ""]
    md.append(f"`scripts/craft_brief.py` (advisory, seed {seed}) over "
              f"`{root}`. Every number below is carried through from a "
              "sibling diagnostic; nothing here is measured twice.")
    if missing:
        md += ["", "> Missing sections: " + "; ".join(
            f"**{tool}** ({why})" for tool, why in sorted(missing.items()))]
    md.append("")
    md += section_now(ch, missing)
    md += section_monotone(warns, findings)
    md += section_owed(ch, missing, chapter_scope)
    md += section_reach(picks, onto is not None, seed)
    md += section_paste(name, picks, findings, open_promises, seed,
                        onto is not None)
    md += [f"Reproduce: `uv run scripts/craft_brief.py --root {root} "
           f"--chapter {name.split('-')[0]} --seed {seed}`", ""]

    payload = {
        "chapter": name,
        "root": str(root),
        "missing": missing,
        "warnings": [{"tool": t, "text": w} for t, w in warns],
        "findings": [{k: v for k, v in f.items() if k != "quote"}
                     for f in findings],
        "open_promises": open_promises,
        "suggestions": [
            {"name": e["name"], "branch": e["_branch"],
             "category": e["_category"], "definition": e.get("definition", ""),
             "example": e.get("example", ""), "answers": e["_answers"]}
            for e in picks],
        "palette": "\n".join(palette_block(picks, name, seed)) if picks else "",
        "fix_brief": "\n".join(
            fixbrief_block(name, findings, picks, open_promises, seed)),
        "markdown": "\n".join(md),
    }
    return "\n".join(md), payload


# ------------------------------------------------------------------ main


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, action="append", default=None,
                    help="book root; repeatable (default: this repo)")
    ap.add_argument("--chapter", help="restrict to files starting with this")
    ap.add_argument("--text", type=Path,
                    help="brief one plain-text or .tex file instead")
    ap.add_argument("--out", type=Path,
                    help="write one markdown file per chapter into this dir")
    ap.add_argument("--seed", type=int, default=0,
                    help="seed for ontology sampling (default 0)")
    ap.add_argument("--suggest", type=int, default=6,
                    help="ontology suggestions per brief, 5-7 (default 6)")
    ap.add_argument("--skip", action="append", default=[], metavar="TOOL",
                    help=f"skip a diagnostic; repeatable ({', '.join(TOOLS)})")
    ap.add_argument("--json", action="store_true",
                    help="machine envelope instead of markdown")
    args = ap.parse_args()

    skip = {s.removesuffix(".py") for s in args.skip}
    unknown = skip - set(TOOLS)
    if unknown:
        print(f"craft_brief: unknown --skip {', '.join(sorted(unknown))}; "
              f"known: {', '.join(TOOLS)}", file=sys.stderr)
        skip &= set(TOOLS)
    want = max(5, min(7, args.suggest))
    roots = [REPO] if args.text else (args.root or [REPO])
    onto = load_ontology()
    if onto is None:
        print("craft_brief: no writing ontology found; section 4 will be "
              "empty", file=sys.stderr)

    chapters_out: list[dict] = []
    briefs: list[tuple[str, str]] = []
    for root in roots:
        root = root.resolve()
        data, errors = collect(root, args.chapter, args.text, args.seed, skip)
        missing = dict(errors)
        for tool in skip:
            missing[tool] = "skipped (--skip)"
        chapters = slice_chapters(
            data, args.chapter if not args.text else None,
            prose_only=args.text is None)
        if not chapters:
            print(f"craft_brief: nothing to report under {root}"
                  + (f" for --chapter {args.chapter}" if args.chapter else ""),
                  file=sys.stderr)
            for tool, why in sorted(missing.items()):
                print(f"craft_brief:   {tool}: {why}", file=sys.stderr)
            continue
        for name, ch in chapters.items():
            md, payload = build_brief(
                ch, missing, onto, args.seed, want, root,
                chapter_scope=args.text is None)
            briefs.append((name, md))
            chapters_out.append(payload)

    if args.json:
        print(json.dumps({"tool": "craft_brief", "seed": args.seed,
                          "chapters": chapters_out}, indent=2))
        return 0

    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        for name, md in briefs:
            path = args.out / f"craft-brief-{Path(name).stem}.md"
            path.write_text(md + "\n", encoding="utf-8")
            print(f"craft_brief: {path}")
        print(f"craft_brief: {len(briefs)} brief(s), seed {args.seed}")
        return 0

    for i, (_name, md) in enumerate(briefs):
        if i:
            print("\n---\n")
        print(md)
    print(f"craft_brief: {len(briefs)} brief(s), seed {args.seed}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
