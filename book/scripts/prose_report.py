#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""One-command prose-quality report: every advisory tool, one markdown file.

Orchestrates the advisory suite as subprocesses and merges their machine
output into a single dated report with round-over-round deltas:

  prose_metrics.py   burstiness/diversity/specificity vs the house baseline
  slop_audit.py      quant slop signals + worst paragraphs (no LLM calls)
  vocab_variety.py   top overused style words + ban candidates

Optional (flags, cost/setup gated):
  --pangram          Pangram detector fractions per chapter (PANGRAM_API_KEY)
  --deslop N         voice-model fix brief for the N worst paragraphs
                     (needs the local voice server; see deslop.py)

Summary numbers are stored in build/prose-report-state.json; each run
reports the delta since the previous run, the same accountability
convention as book_stats.py. Report lands in build/prose-report.md by
default -- point --out at docs/review-NN/ to file it with a round.

Usage:
    uv run scripts/prose_report.py                    # free, offline tools
    uv run scripts/prose_report.py --pangram --deslop 5
    uv run scripts/prose_report.py --root ../other-book --out review.md

Advisory only -- never a CI gate.
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def run_jsonl(script: str, *extra: str, root: Path) -> list[dict]:
    """Run a suite script with --format jsonl and parse its stdout rows."""
    cmd = ["uv", "run", str(SCRIPTS / script), "--root", str(root),
           "--format", "jsonl", *extra]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True,
                             timeout=1800, check=False)
    except subprocess.TimeoutExpired:
        print(f"prose_report: WARN {script} timed out", file=sys.stderr)
        return []
    if out.returncode != 0:
        print(f"prose_report: WARN {script} failed: "
              f"{out.stderr.strip().splitlines()[-1] if out.stderr else '?'}",
              file=sys.stderr)
        return []
    rows = []
    for line in out.stdout.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def run_text(script: str, *extra: str, root: Path) -> str:
    cmd = ["uv", "run", str(SCRIPTS / script), "--root", str(root), *extra]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True,
                             timeout=1800, check=False)
        return out.stdout
    except subprocess.TimeoutExpired:
        return ""


def fmt_delta(cur: float, prev: float | None, decimals: int = 2,
              lower_is_better: bool = False) -> str:
    if prev is None:
        return f"{cur:.{decimals}f}"
    d = cur - prev
    arrow = "" if abs(d) < 10 ** -decimals else (
        "↓" if d < 0 else "↑")
    good = (d < 0) == lower_is_better if arrow else True
    mark = "" if not arrow else (" ✓" if good else "")
    return f"{cur:.{decimals}f} ({arrow}{abs(d):.{decimals}f}{mark})" \
        if arrow else f"{cur:.{decimals}f} (=)"


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path,
                    default=SCRIPTS.parent)
    ap.add_argument("--out", type=Path, default=None,
                    help="report path (default build/prose-report.md)")
    ap.add_argument("--pangram", action="store_true",
                    help="include Pangram detector fractions (paid)")
    ap.add_argument("--deslop", type=int, default=0, metavar="N",
                    help="append a voice-model fix brief for the N worst "
                         "paragraphs (needs the local voice server)")
    args = ap.parse_args()
    root = args.root.resolve()
    out_path = args.out or (root / "build" / "prose-report.md")
    state_path = root / "build" / "prose-report-state.json"

    print(f"prose_report: {root.name}", file=sys.stderr)

    # ---- gather -----------------------------------------------------------
    metrics = run_jsonl("prose_metrics.py", root=root)
    slop_paras = run_jsonl("slop_audit.py", "--level", "paragraph",
                           "--top", "8", root=root)
    slop_files = run_jsonl("slop_audit.py", "--level", "file", root=root)
    vocab = run_jsonl("vocab_variety.py", "--sort", "ratio", "--band", "mid",
                      "--top", "8", root=root)
    bans = run_text("vocab_variety.py", "--suggest-bans", "--top", "8",
                    root=root)
    pangram = run_jsonl("pangram_check.py", root=root) if args.pangram else []

    # ---- summary + deltas -------------------------------------------------
    words = sum(m.get("words", 0) for m in metrics)
    cvs = [m["cv"] for m in metrics if m.get("cv")]
    mtlds = [m["mtld"] for m in metrics if m.get("mtld")]
    house_notes = sum(len(m.get("house_notes", [])) for m in metrics)
    warns = sum(len(m.get("warnings", [])) for m in metrics)
    slop_hits = sum(f.get("slop_per_1k", 0) * f.get("words", 0) / 1000
                    for f in slop_files)
    summary = {
        "date": datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
        "words": words,
        "chapters": len(metrics),
        "cv_median": round(statistics.median(cvs), 3) if cvs else 0,
        "mtld_median": round(statistics.median(mtlds), 1) if mtlds else 0,
        "metric_warnings": warns,
        "house_notes": house_notes,
        "slop_hits": round(slop_hits, 1),
        "flagged_paras": len([p for p in slop_paras
                              if p.get("score", 0) >= 3]),
    }
    if pangram:
        tw = sum(r["words"] for r in pangram) or 1
        summary["pangram_ai"] = round(
            sum((r.get("fraction_ai") or 0) * r["words"]
                for r in pangram) / tw, 3)

    prev = {}
    if state_path.exists():
        try:
            prev = json.loads(state_path.read_text())
        except json.JSONDecodeError:
            prev = {}

    # ---- render -----------------------------------------------------------
    L: list[str] = [
        f"# Prose-quality report — {root.name}",
        "",
        f"Generated {summary['date']} by scripts/prose_report.py. "
        "Advisory; craft wins over any number here.",
        "",
        "## Summary" + (f" (delta vs {prev.get('date', 'previous run')})"
                        if prev else ""),
        "",
        "| metric | value | note |",
        "|---|---|---|",
        f"| words | {summary['words']:,} | {summary['chapters']} chapters |",
        f"| sentence-length cv (median) | "
        f"{fmt_delta(summary['cv_median'], prev.get('cv_median'), 3)} "
        f"| house band 0.52–0.68; low = machine metronome |",
        f"| MTLD (median) | "
        f"{fmt_delta(summary['mtld_median'], prev.get('mtld_median'), 1)} "
        f"| house band 90–161; HIGH is also a draft signal |",
        f"| metric warnings | "
        f"{fmt_delta(summary['metric_warnings'], prev.get('metric_warnings'), 0, True)} | prose_metrics thresholds |",
        f"| house-baseline notes | "
        f"{fmt_delta(summary['house_notes'], prev.get('house_notes'), 0, True)} | 3+ on one chapter = under-edited |",
        f"| slop-vocabulary hits | "
        f"{fmt_delta(summary['slop_hits'], prev.get('slop_hits'), 1, True)} | slop_audit lists |",
        f"| flagged paragraphs (score ≥ 3) | "
        f"{fmt_delta(summary['flagged_paras'], prev.get('flagged_paras'), 0, True)} | quant composite |",
    ]
    if "pangram_ai" in summary:
        L.append(f"| pangram fraction AI (book) | "
                 f"{fmt_delta(summary['pangram_ai'], prev.get('pangram_ai'), 3, True)} | detectability, not craft |")
    L.append("")

    if metrics:
        hot = [m for m in metrics
               if len(m.get("house_notes", [])) + len(m.get("warnings", [])) >= 2]
        if hot:
            L += ["## Chapters needing attention", ""]
            for m in sorted(hot, key=lambda x: -(len(x.get("house_notes", []))
                                                 + len(x.get("warnings", [])))):
                issues = m.get("warnings", []) + m.get("house_notes", [])
                L.append(f"- **{m['file']}** — " + "; ".join(issues[:4]))
            L.append("")

    if slop_paras:
        L += ["## Worst paragraphs (quant slop)", ""]
        for p in slop_paras[:8]:
            sig = ", ".join(p.get("constructions", [])[:2]
                            + p.get("slop_words", [])[:3]) or "comp outlier"
            L.append(f"- `{p['file']}:{p['line']}` score {p['score']} — {sig}")
        L += ["", "Drill down: `uv run scripts/slop_audit.py --level "
              "paragraph`; judge: `--llm`; rewrite ideas: "
              "`scripts/deslop.py --batch`.", ""]

    if vocab:
        L += ["## Overused style words (mid-band, by ratio)", ""]
        for v in vocab[:8]:
            over = (f"{2 ** v['overuse_log2']:.0f}x"
                    if v.get("overuse_log2") else "—")
            fresh = ", ".join(v.get("fresh_picks", [])[:4])
            L.append(f"- **{v['word']}** {v['book_count']}x ({over} expected)"
                     + (f" — fresh: {fresh}" if fresh else ""))
        L.append("")

    ban_lines = [ln for ln in bans.splitlines()
                 if ln.strip() and not ln.startswith("#")]
    if ban_lines:
        L += ["## Ban candidates (`--suggest-bans`, review before adopting)",
              "", "```"] + ban_lines + ["```", ""]

    if pangram:
        worst_pg = sorted(pangram, key=lambda r: -(r.get("fraction_ai") or 0))
        L += ["## Pangram per chapter (top)", ""]
        for r in worst_pg[:8]:
            L.append(f"- `{r['file']}` ai={r.get('fraction_ai', 0):.2f} "
                     f"assisted={r.get('fraction_ai_assisted', 0):.2f}")
        L.append("")

    if args.deslop:
        print(f"prose_report: deslop brief for {args.deslop} worst "
              "paragraphs…", file=sys.stderr)
        brief = run_text("deslop.py", "--batch", "--limit", str(args.deslop),
                         root=root)
        if brief.strip():
            L += ["## Voice-model fix brief", ""]
            L += brief.splitlines()[6:]  # skip its own header
            L.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(L) + "\n")
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(summary, indent=2))
    print(f"prose_report: -> {out_path}", file=sys.stderr)
    for line in L[6:18]:
        print(line)


if __name__ == "__main__":
    main()
