# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Compute wrap-cover dimensions from the interior page count.

Reads trim size and paper stock from book.yaml, takes the page count from
the built print PDF (pdfinfo), and writes latex/generated/cover-vars.tex
for latex/cover/cover.tex.

Spine formulas:
  KDP paperback     white/standard-color: pages * 0.002252
                    cream: pages * 0.0025     groundwood: pages * 0.00235
                    premium-color: pages * 0.002347
  Lulu paperback    pages / 444 + 0.06
  Lulu hardcover    lookup table (case wrap), bleed 0.875" (0.75" board wrap + 0.125")
Sources: KDP paperback cover spec (kdp.amazon.com G201953020, verified
2026-07-07) — no additive term; Lulu Book Creation Guide. NOTE: some prior
book projects' scripts carried Lulu's +0.06 into the KDP branch; KDP's own
calculator does not.

Also emits \\ifCoverSpineText: KDP allows spine text only at >= 79 pages
(Lulu: ~80); cover.tex additionally keeps its own legibility threshold.

Usage:
    uv run scripts/update_cover_vars.py --platform kdp [--pdf build/latex/book-print.pdf]
    uv run scripts/update_cover_vars.py --platform lulu --binding hardcover --page-count 320
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml
from trim_catalog import TRIM_PRESETS

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "latex" / "generated" / "cover-vars.tex"
DEFAULT_PDF = ROOT / "build" / "latex" / "book-print.pdf"

# (min_pages, max_pages, spine_inches) — Lulu hardcover case wrap
LULU_HARDCOVER_SPINE = [
    (24, 84, 0.25), (85, 140, 0.50), (141, 168, 0.625), (169, 194, 0.688),
    (195, 222, 0.75), (223, 250, 0.813), (251, 278, 0.875), (279, 306, 0.938),
    (307, 334, 1.0), (335, 360, 1.063), (361, 388, 1.125), (389, 416, 1.188),
    (417, 444, 1.25), (445, 472, 1.313), (473, 500, 1.375), (501, 528, 1.438),
    (529, 556, 1.5), (557, 582, 1.563), (583, 610, 1.625), (611, 638, 1.688),
    (639, 666, 1.75), (667, 694, 1.813), (695, 722, 1.875), (723, 750, 1.938),
    (751, 778, 2.0), (779, 799, 2.063),
]

PAPERBACK_BLEED = 0.125
HARDCOVER_BLEED = 0.875  # 0.75" board wrap + 0.125" bleed

# KDP per-page spine thickness by paper stock (G201953020).
KDP_SPINE_PER_PAGE = {
    "white": 0.002252,
    "cream": 0.0025,
    "groundwood": 0.00235,
    "standard-color": 0.002252,  # printed on the white stock
    "premium-color": 0.002347,
}

# Minimum page count before the platform allows text on the spine.
SPINE_TEXT_MIN_PAGES = {"kdp": 79, "lulu": 80}


def page_count_from_pdf(pdf: Path) -> int:
    out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True,
                         text=True, check=True).stdout
    for line in out.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":")[1])
    raise RuntimeError(f"pdfinfo gave no page count for {pdf}")


def spine_width(pages: int, platform: str, binding: str, paper: str) -> tuple[float, str]:
    if platform == "lulu" and binding == "hardcover":
        if not 24 <= pages <= 799:
            sys.exit(f"Lulu hardcover supports 24-799 pages (got {pages})")
        for lo, hi, spine in LULU_HARDCOVER_SPINE:
            if lo <= pages <= hi:
                return spine, f"Lulu hardcover lookup ({pages}p)"
    if platform == "lulu":
        return pages / 444 + 0.06, "pages/444 + 0.06"
    per_page = KDP_SPINE_PER_PAGE[paper]
    return pages * per_page, f"pages*{per_page} ({paper})"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--platform", choices=["kdp", "lulu"], required=True)
    ap.add_argument("--binding", choices=["paperback", "hardcover"],
                    default="paperback")
    ap.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    ap.add_argument("--page-count", type=int)
    args = ap.parse_args()

    if args.platform == "kdp" and args.binding == "hardcover":
        sys.exit("KDP hardcover is not supported here; use --platform lulu")

    cfg = yaml.safe_load((ROOT / "book.yaml").read_text())
    trim_w, trim_h = TRIM_PRESETS[cfg["trim"]["preset"]]
    paper = cfg["trim"].get("paper", "white")
    if paper not in KDP_SPINE_PER_PAGE:
        sys.exit(f"trim.paper must be one of {sorted(KDP_SPINE_PER_PAGE)}, "
                 f"got {paper!r}")

    if args.page_count:
        pages = args.page_count
    else:
        if not args.pdf.exists():
            sys.exit(f"{args.pdf} not found — run `make pdf` first "
                     "(or pass --page-count)")
        pages = page_count_from_pdf(args.pdf)

    spine, formula = spine_width(pages, args.platform, args.binding, paper)
    bleed = HARDCOVER_BLEED if args.binding == "hardcover" else PAPERBACK_BLEED
    total_w = 2 * trim_w + spine + 2 * bleed
    total_h = trim_h + 2 * bleed
    spine_text_ok = pages >= SPINE_TEXT_MIN_PAGES[args.platform]
    if not spine_text_ok:
        print(f"cover-vars: NOTE {pages} pages is under the "
              f"{SPINE_TEXT_MIN_PAGES[args.platform]}-page {args.platform} "
              "minimum for spine text — the cover renders a blank spine")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(f"""\
% GENERATED by scripts/update_cover_vars.py — do not edit, do not commit.
% {args.platform} {args.binding} | {paper} paper | {pages} pages
% spine = {spine:.4f}in ({formula}); wrap = {total_w:.4f}in x {total_h:.4f}in
\\newlength{{\\CoverTrimWidth}}\\setlength{{\\CoverTrimWidth}}{{{trim_w:.3f}in}}
\\newlength{{\\CoverTrimHeight}}\\setlength{{\\CoverTrimHeight}}{{{trim_h:.3f}in}}
\\newlength{{\\CoverBleed}}\\setlength{{\\CoverBleed}}{{{bleed:.3f}in}}
\\newlength{{\\CoverSpineWidth}}\\setlength{{\\CoverSpineWidth}}{{{spine:.6f}in}}
\\newlength{{\\CoverWidth}}\\setlength{{\\CoverWidth}}{{{total_w:.6f}in}}
\\newlength{{\\CoverHeight}}\\setlength{{\\CoverHeight}}{{{total_h:.4f}in}}
\\newcommand{{\\CoverPageCount}}{{{pages}}}
\\newcommand{{\\CoverPlatform}}{{{args.platform}}}
\\newcommand{{\\CoverBinding}}{{{args.binding}}}
\\newif\\ifCoverSpineText\\CoverSpineText{'true' if spine_text_ok else 'false'}
""")
    print(f"cover-vars: {args.platform}/{args.binding} {pages}p "
          f"spine={spine:.4f}in wrap={total_w:.4f}x{total_h:.4f}in")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
