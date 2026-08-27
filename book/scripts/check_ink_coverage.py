# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10"]
# ///
"""Cover ink-coverage (TAC) gate (`make cover-ink`).

POD presses cap total area coverage — the sum of C+M+Y+K ink in any one
spot. KDP's cover guidance and US Web Coated (SWOP) both sit at ~240%;
exceeding it risks muddy rich blacks, set-off, and rejected files.

Ghostscript's `inkcov` device only reports page-*average* coverage,
which hides per-pixel spikes, so this rasterizes the cover through
`tiffsep` (one grayscale TIFF per plate, GS handles any RGB->CMYK
conversion the press would redo) and computes the true per-pixel
maximum: TAC(x,y) = sum over plates of ink%(x,y).

    uv run scripts/check_ink_coverage.py --pdf build/cover/cover-kdp.pdf
    ... --max-tac 240 --dpi 75
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

# Vendor TAC cap (percent). KDP covers and SWOP: 240. Override per
# platform with --max-tac if a press proof says otherwise.
MAX_TAC_PERCENT = 240


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--pdf", type=Path, required=True)
    ap.add_argument("--max-tac", type=float, default=MAX_TAC_PERCENT)
    ap.add_argument("--dpi", type=int, default=75,
                    help="separation raster resolution (75 catches "
                         "area fills; raise for hairline audits)")
    args = ap.parse_args()

    if not args.pdf.exists():
        sys.exit(f"check_ink_coverage: {args.pdf} not found — build it first")

    with tempfile.TemporaryDirectory() as tmp:
        proc = subprocess.run(
            ["gs", "-dBATCH", "-dNOPAUSE", "-q", "-sDEVICE=tiffsep",
             f"-r{args.dpi}", f"-sOutputFile={tmp}/sep-%d.tif",
             str(args.pdf)],
            capture_output=True, text=True)
        if proc.returncode:
            sys.exit(f"check_ink_coverage: ghostscript failed: "
                     f"{proc.stderr.strip()[-200:]}")

        worst = 0.0
        pages = 0
        # tiffsep writes sep-N.tif (CMYK composite) + sep-N(Plate).tif.
        for composite in sorted(Path(tmp).glob("sep-*.tif")):
            if "(" in composite.name:
                continue
            pages += 1
            plates = sorted(Path(tmp).glob(
                composite.stem + "(*).tif"))
            if not plates:
                continue
            total = None
            for plate in plates:
                with Image.open(plate) as im:
                    data = list(im.convert("L").tobytes())
                # tiffsep plates: 255 = no ink; ink% = (255-v)/255*100
                vals = [(255 - v) for v in data]
                total = vals if total is None else [
                    a + b for a, b in zip(total, vals)]
            page_max = max(total) / 255 * 100
            worst = max(worst, page_max)

        if pages == 0:
            sys.exit("check_ink_coverage: no separations produced — "
                     "is the PDF valid?")

    print(f"check_ink_coverage: max TAC {worst:.0f}% across {pages} "
          f"page(s) at {args.dpi} dpi (limit {args.max_tac:.0f}%)")
    if worst > args.max_tac:
        print(f"check_ink_coverage: FAIL — reduce rich-black/dark fills "
              f"(cap C+M+Y+K at {args.max_tac:.0f}%)", file=sys.stderr)
        return 1
    print("check_ink_coverage: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
