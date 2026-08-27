# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Word counts per chapter with deltas vs. the previous run.

Writes build/stats.json; each run prints the change since last run so
review rounds can be quantified (before/after convention from the RFC
book). Never hand-type word counts anywhere — cite this script's output.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Every prose file, not just chNN-*.tex — see the same note in check_style.py.
# A word count that silently omits the interchapters is a wrong word count.
CHAPTERS = sorted(
    p for p in (ROOT / "latex" / "chapters").glob("*.tex") if not p.name.startswith("_")
)
STATS = ROOT / "build" / "stats.json"


def detex(text: str) -> str:
    text = re.sub(r"(?<!\\)%.*", "", text)
    for env in ("codelisting", "promptcode", "outputcode", "verbatim",
                "lstlisting", "tabular"):
        text = re.sub(rf"\\begin\{{{env}\}}.*?\\end\{{{env}\}}", " ",
                      text, flags=re.DOTALL)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", text)
    return re.sub(r"[{}~%]", " ", text)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true",
                    help="print the stats JSON to stdout instead of the table "
                         "(build/stats.json is written either way)")
    args = ap.parse_args()

    previous = {}
    if STATS.exists():
        previous = json.loads(STATS.read_text()).get("chapters", {})

    chapters = {}
    total = 0
    rows = []
    for chapter in CHAPTERS:
        words = len(detex(chapter.read_text()).split())
        total += words
        chapters[chapter.name] = words
        delta = words - previous.get(chapter.name, 0)
        sign = f"{delta:+d}" if chapter.name in previous else "new"
        rows.append(f"{chapter.name:<40}{words:>8}{sign:>8}")

    payload = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total": total,
        "chapters": chapters,
    }
    STATS.parent.mkdir(parents=True, exist_ok=True)
    STATS.write_text(json.dumps(payload, indent=2) + "\n")

    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(f"{'chapter':<40}{'words':>8}{'delta':>8}")
    for row in rows:
        print(row)
    prev_total = sum(previous.values())
    delta_total = f"{total - prev_total:+d}" if previous else "—"
    print(f"{'TOTAL':<40}{total:>8}{delta_total:>8}")


if __name__ == "__main__":
    main()
