# /// script
# requires-python = ">=3.11"
# ///
"""Print-PDF preflight gates (`make preflight`).

The two POD rejection causes nothing else in the pipeline checked:

  fonts   every font fully embedded (`pdffonts` emb=yes) and no
          Type 3 bitmap fonts — the classic LuaLaTeX failure mode via
          TikZ pattern fills, listings bitmap fallbacks, or text inside
          included figure PDFs (which must be preflighted too, hence
          whole-document scan)
  images  every raster image at or above --min-dpi (default 300 —
          KDP, Lulu, and IngramSpark all specify 300 DPI)

Usage:
    uv run scripts/preflight_pdf.py build/latex/book-print.pdf \
        build/cover/cover-kdp.pdf
    ... --min-dpi 300 --allow 12:0     # exempt image num 0 on page 12

Needs poppler-utils (pdffonts, pdfimages) — audited by `make doctor`.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True,
                              check=True).stdout
    except FileNotFoundError:
        sys.exit(f"preflight_pdf: {cmd[0]} not found — install poppler-utils")
    except subprocess.CalledProcessError as e:
        sys.exit(f"preflight_pdf: {' '.join(cmd)} failed: {e.stderr.strip()}")


def parse_columns(header: str, ruler: str) -> list[tuple[str, int, int]]:
    """Column names and extents from a poppler header + dashed ruler
    line (`name type ... / ---- ------ ...`). Layout-proof against
    poppler adding or reordering columns."""
    cols = []
    for m in re.finditer(r"-+", ruler):
        cols.append((header[m.start():m.end()].strip(), m.start(), m.end()))
    return cols


def check_fonts(pdf: Path) -> list[str]:
    out = run(["pdffonts", str(pdf)]).splitlines()
    if len(out) < 2:
        return []
    cols = parse_columns(out[0], out[1])
    problems = []
    for line in out[2:]:
        if not line.strip():
            continue
        row = {name: line[a:b].strip() if len(line) > a else ""
               for name, a, b in cols}
        # Last column can overflow its ruler width; name never matters.
        if row.get("type") == "Type 3":
            problems.append(f"{pdf.name}: Type 3 (bitmap) font "
                            f"{row.get('name') or '[unnamed]'}")
        if row.get("emb") and row["emb"] != "yes":
            problems.append(f"{pdf.name}: font not embedded: "
                            f"{row.get('name') or '[unnamed]'} "
                            f"({row.get('type', '?')})")
    return problems


def check_images(pdf: Path, min_dpi: int, allow: set[str]) -> list[str]:
    out = run(["pdfimages", "-list", str(pdf)]).splitlines()
    if len(out) < 2:
        return []
    header = out[0].split()
    problems = []
    for line in out[2:]:
        parts = line.split()
        if len(parts) < len(header):
            continue
        row = dict(zip(header, parts))
        if row.get("type") != "image":
            continue  # masks/stencils scale with their parent image
        key = f"{row['page']}:{row['num']}"
        try:
            xppi, yppi = int(row["x-ppi"]), int(row["y-ppi"])
        except (KeyError, ValueError):
            continue
        if xppi <= 0 or yppi <= 0:
            continue  # poppler reports -1 when it cannot compute
        if (xppi < min_dpi or yppi < min_dpi) and key not in allow:
            problems.append(
                f"{pdf.name}: image page {row['page']} #{row['num']} is "
                f"{xppi}x{yppi} ppi (need {min_dpi}; pass --allow {key} "
                "if intentional)")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("pdfs", nargs="+", type=Path)
    ap.add_argument("--min-dpi", type=int, default=300,
                    help="minimum image resolution (default 300, per POD specs)")
    ap.add_argument("--allow", action="append", default=[],
                    metavar="PAGE:NUM",
                    help="exempt an image (repeatable; applies to all PDFs)")
    args = ap.parse_args()

    problems: list[str] = []
    for pdf in args.pdfs:
        if not pdf.exists():
            sys.exit(f"preflight_pdf: {pdf} not found — build it first")
        problems += check_fonts(pdf)
        problems += check_images(pdf, args.min_dpi, set(args.allow))

    for p in problems:
        print(f"preflight_pdf: FAIL {p}", file=sys.stderr)
    if problems:
        print(f"preflight_pdf: {len(problems)} problem(s) across "
              f"{len(args.pdfs)} PDF(s)", file=sys.stderr)
        return 1
    print(f"preflight_pdf: OK — {len(args.pdfs)} PDF(s): all fonts "
          f"embedded, no Type 3, images >= {args.min_dpi} ppi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
