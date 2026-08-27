# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Export the front panel of the wrap cover for digital use.

Crops the front panel (right of the spine, inside the bleed) from the wrap
PDF via pdftoppm + ImageMagick. Two outputs:

  --out PATH          EPUB cover PNG at the book's true trim ratio (e.g.
                      1707x2560 for 6x9). This is what goes inside the EPUB.
  --kindle-out PATH   KDP marketing cover JPEG at exactly 1600x2560 (the
                      1.6:1 ideal from KDP spec G200645690), letterboxed
                      with the cover's own corner color when the trim ratio
                      differs. Upload THIS to KDP, not the EPUB PNG.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VARS = ROOT / "latex" / "generated" / "cover-vars.tex"
DPI = 300


def var_inches(name: str, text: str) -> float:
    m = re.search(rf"\\setlength\{{\\{name}\}}\{{([\d.]+)in\}}", text)
    if not m:
        sys.exit(f"export_cover_image: {name} not found in cover-vars.tex")
    return float(m.group(1))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pdf", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--kindle-out", type=Path, default=None,
                    help="also write a 1600x2560 JPEG for the KDP ebook listing")
    args = ap.parse_args()

    text = VARS.read_text()
    bleed = var_inches("CoverBleed", text)
    trim_w = var_inches("CoverTrimWidth", text)
    trim_h = var_inches("CoverTrimHeight", text)
    spine = var_inches("CoverSpineWidth", text)

    # Front panel offset from the left edge of the wrap sheet.
    left_px = round((bleed + trim_w + spine) * DPI)
    top_px = round(bleed * DPI)
    w_px = round(trim_w * DPI)
    h_px = round(trim_h * DPI)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        full = Path(td) / "wrap"
        subprocess.run(["pdftoppm", "-png", "-r", str(DPI), "-singlefile",
                        str(args.pdf), str(full)], check=True)
        # EPUB cover: front panel at true trim ratio, height 2560 px.
        subprocess.run(["magick", f"{full}.png",
                        "-crop", f"{w_px}x{h_px}+{left_px}+{top_px}", "+repage",
                        "-resize", "x2560", str(args.out)], check=True)
        print(f"export_cover_image: wrote {args.out} (EPUB, trim ratio)")
        if args.kindle_out:
            # KDP listing cover: exactly 1600x2560 (spec G200645690),
            # letterboxed with the front panel's top-left pixel color.
            args.kindle_out.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["magick", str(args.out),
                            "-resize", "1600x2560",
                            "-set", "option:bg", "%[pixel:p{2,2}]",
                            "-background", "%[bg]",
                            "-gravity", "center", "-extent", "1600x2560",
                            "-quality", "95", str(args.kindle_out)], check=True)
            print(f"export_cover_image: wrote {args.kindle_out} "
                  "(KDP listing, 1600x2560 JPEG)")


if __name__ == "__main__":
    main()
