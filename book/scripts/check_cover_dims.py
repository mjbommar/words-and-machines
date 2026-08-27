# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Gate: verify a rendered wrap cover matches generated/cover-vars.tex.

Catches the classic failure of uploading a cover rendered before the final
page count changed the spine width (make doctor also warns on staleness).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VARS = ROOT / "latex" / "generated" / "cover-vars.tex"
TOLERANCE_IN = 0.01


def pdf_size_inches(pdf: Path) -> tuple[float, float]:
    out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True,
                         text=True, check=True).stdout
    m = re.search(r"Page size:\s+([\d.]+) x ([\d.]+) pts", out)
    if not m:
        sys.exit(f"check_cover_dims: no page size in pdfinfo output for {pdf}")
    return float(m.group(1)) / 72.0, float(m.group(2)) / 72.0


def expected_size() -> tuple[float, float]:
    if not VARS.exists():
        sys.exit("check_cover_dims: latex/generated/cover-vars.tex missing — "
                 "run `make cover-vars` first")
    text = VARS.read_text()
    w = re.search(r"\\setlength\{\\CoverWidth\}\{([\d.]+)in\}", text)
    h = re.search(r"\\setlength\{\\CoverHeight\}\{([\d.]+)in\}", text)
    if not (w and h):
        sys.exit("check_cover_dims: could not parse CoverWidth/CoverHeight")
    return float(w.group(1)), float(h.group(1))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pdf", type=Path, required=True)
    args = ap.parse_args()

    got_w, got_h = pdf_size_inches(args.pdf)
    exp_w, exp_h = expected_size()
    if abs(got_w - exp_w) > TOLERANCE_IN or abs(got_h - exp_h) > TOLERANCE_IN:
        sys.exit(f"check_cover_dims: FAIL {args.pdf.name} is "
                 f"{got_w:.4f}x{got_h:.4f}in, expected {exp_w:.4f}x{exp_h:.4f}in "
                 "— rerun `make cover-vars` and rebuild the cover")
    print(f"check_cover_dims: OK {got_w:.4f}x{got_h:.4f}in")


if __name__ == "__main__":
    main()
