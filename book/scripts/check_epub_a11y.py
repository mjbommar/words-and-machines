# /// script
# requires-python = ">=3.11"
# ///
"""Ace by DAISY accessibility gate (`make epub-a11y`).

Runs Ace (https://daisy.github.io/ace/) on the built EPUB and fails on
any violation of impact `serious` or `critical`, or every violation with
``--strict``. Ace's exit code is 0
even when violations exist, so the JSON report — not the exit code —
is the gate. The generated OPF claims `EPUB Accessibility 1.1 -
WCAG 2.2 Level AA`; this gate is what keeps that claim honest.

Ace resolution order: `ace` on PATH, else the Puppeteer runner from
`npx --yes --package @daisy/ace ace-puppeteer` (the first npx run downloads
Ace plus a headless Chromium — needs network). The explicit runner avoids
Electron's setuid-sandbox requirement in an unprivileged build workspace.
Override with --ace-cmd or the ACE_CMD environment variable.

    uv run scripts/check_epub_a11y.py --epub build/epub/book.epub
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAIL_IMPACTS = {"serious", "critical"}
IMPACT_ORDER = ["critical", "serious", "moderate", "minor"]


def ace_command() -> list[str]:
    override = os.environ.get("ACE_CMD")
    if override:
        return shlex.split(override)
    if shutil.which("ace"):
        return ["ace"]
    if shutil.which("npx"):
        return ["npx", "--yes", "--package", "@daisy/ace", "ace-puppeteer"]
    sys.exit("check_epub_a11y: neither `ace` nor `npx` found — install "
             "Node.js (or `npm install -g @daisy/ace`) for `make epub-a11y`")


def collect_failures(node, out: list[dict]) -> None:
    """Walk Ace's nested EARL assertion tree, collecting failed tests."""
    if isinstance(node, list):
        for item in node:
            collect_failures(item, out)
        return
    if not isinstance(node, dict):
        return
    result = node.get("earl:result") or {}
    test = node.get("earl:test") or {}
    if result.get("earl:outcome") == "fail" and test:
        out.append({
            "rule": test.get("dct:title", "?"),
            "impact": test.get("earl:impact", "?"),
            "file": (node.get("earl:testSubject") or {}).get("url", ""),
            "desc": (result.get("dct:description") or "").strip(),
        })
    collect_failures(node.get("assertions"), out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--epub", type=Path,
                    default=ROOT / "build" / "epub" / "book.epub")
    ap.add_argument("--outdir", type=Path,
                    default=ROOT / "build" / "a11y-report",
                    help="Ace report directory (report.json + report.html)")
    ap.add_argument("--ace-cmd", default=None,
                    help="Ace invocation override (also: ACE_CMD env var)")
    ap.add_argument("--strict", action="store_true",
                    help="fail on moderate and minor violations too")
    args = ap.parse_args()

    if not args.epub.exists():
        sys.exit(f"check_epub_a11y: {args.epub} not found — run `make epub`")

    cmd = shlex.split(args.ace_cmd) if args.ace_cmd else ace_command()
    cmd += ["--force", "--outdir", str(args.outdir), str(args.epub)]
    proc = subprocess.run(cmd)

    report_path = args.outdir / "report.json"
    if not report_path.exists():
        sys.exit(f"check_epub_a11y: ace produced no {report_path} "
                 f"(exit {proc.returncode}) — see output above")

    report = json.loads(report_path.read_text())
    failures: list[dict] = []
    collect_failures(report.get("assertions"), failures)

    counts = {i: sum(1 for f in failures if f["impact"] == i)
              for i in IMPACT_ORDER}
    gate = failures if args.strict else [
        f for f in failures if f["impact"] in FAIL_IMPACTS]
    for f in sorted(failures, key=lambda f: IMPACT_ORDER.index(f["impact"])
                    if f["impact"] in IMPACT_ORDER else 9):
        marker = "FAIL" if args.strict or f["impact"] in FAIL_IMPACTS else "warn"
        print(f"check_epub_a11y: {marker} [{f['impact']}] {f['rule']} "
              f"{f['file']}  {f['desc'][:100]}")

    summary = ", ".join(f"{counts[i]} {i}" for i in IMPACT_ORDER if counts[i])
    print(f"check_epub_a11y: {len(failures)} violation(s)"
          f"{' — ' + summary if summary else ''}; "
          f"report: {args.outdir.relative_to(ROOT)}/report.html")
    if gate:
        scope = "accessibility" if args.strict else "serious/critical"
        print(f"check_epub_a11y: FAIL — {len(gate)} {scope} "
              "violation(s) contradict the release contract",
              file=sys.stderr)
        return 1
    message = "no violations" if args.strict else "no serious/critical violations"
    print(f"check_epub_a11y: OK ({message})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
