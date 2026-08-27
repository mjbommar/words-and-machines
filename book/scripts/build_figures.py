#!/usr/bin/env python3
"""build_figures.py — compile standalone TikZ/pgfplots sources into the
figure PDFs the authoring contract includes (module: figures, ADR 0014).

Each ``latex/figures/src/<name>.tikz`` (a bare ``tikzpicture`` /
``axis`` body) is wrapped in a ``standalone`` document that inputs
``latex/figures/figure-preamble.tex`` — so every diagram gets the book's
fonts and palette — and compiled to ``latex/figures/<name>.pdf``.
Chapters then ``\\includegraphics{figures/<name>}`` per the contract; the
EPUB build rasterizes the PDF to PNG on its own.

Print wants vector PDF; that is the one asset this produces. Options:

  --grayscale   define \\GrayscaleMode before the palette -> a B&W-POD
                variant (writes <name>-gray.pdf), so the same source
                serves the colour edition and the grayscale interior.
  --png[=DPI]   also emit a preview PNG (default 300 dpi) next to the
                PDF, for quick review or a non-Kindle EPUB that prefers
                supplied rasters over the converter's 200-dpi default.
  --only NAME   build a single figure (repeatable).

Zero third-party deps: lualatex + (for --png) pdftoppm.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LATEX = ROOT / "latex"
SRC = LATEX / "figures" / "src"
OUT = LATEX / "figures"
PREAMBLE = OUT / "figure-preamble.tex"

WRAPPER = r"""\documentclass[border=4pt,varwidth=false]{standalone}
\def\FigurePreambleDir{%(latexdir)s/}
%(grayscale)s\input{%(preamble)s}
\begin{document}
\input{%(source)s}
\end{document}
"""


def build_one(src: Path, grayscale: bool, png_dpi: int | None) -> bool:
    name = src.stem + ("-gray" if grayscale else "")
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        (tmp / "fig.tex").write_text(WRAPPER % {
            "latexdir": LATEX.as_posix(),
            "preamble": PREAMBLE.as_posix(),
            "source": src.as_posix(),
            "grayscale": (r"\def\GrayscaleMode{}" + "\n") if grayscale else "",
        })
        proc = subprocess.run(
            ["lualatex", "-interaction=nonstopmode", "-halt-on-error",
             "-output-directory", td, "fig.tex"],
            cwd=td, capture_output=True, text=True,
        )
        pdf = tmp / "fig.pdf"
        if proc.returncode != 0 or not pdf.exists():
            sys.stderr.write(f"build_figures: FAILED {src.name}\n")
            tail = "\n".join(proc.stdout.splitlines()[-15:])
            sys.stderr.write(tail + "\n")
            return False
        dest = OUT / f"{name}.pdf"
        shutil.copyfile(pdf, dest)
        msg = f"build_figures: {dest.relative_to(ROOT)}"
        if png_dpi:
            subprocess.run(
                ["pdftoppm", "-png", "-r", str(png_dpi), "-singlefile",
                 pdf.as_posix(), (OUT / name).as_posix()],
                check=False,
            )
            msg += f"  (+ {name}.png @ {png_dpi}dpi)"
        print(msg)
        return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--grayscale", action="store_true",
                    help="also build a \\GrayscaleMode B&W variant")
    ap.add_argument("--png", nargs="?", const=300, type=int, default=None,
                    metavar="DPI", help="also emit a preview PNG (default 300)")
    ap.add_argument("--only", action="append", default=[], metavar="NAME",
                    help="build only this figure stem (repeatable)")
    args = ap.parse_args()

    if not SRC.is_dir():
        print(f"build_figures: no sources at {SRC.relative_to(ROOT)}")
        return 0
    if shutil.which("lualatex") is None:
        sys.stderr.write("build_figures: lualatex not found\n")
        return 1

    sources = sorted(SRC.glob("*.tikz"))
    if args.only:
        wanted = set(args.only)
        sources = [s for s in sources if s.stem in wanted]
    if not sources:
        print("build_figures: nothing to build")
        return 0

    ok = True
    for src in sources:
        ok &= build_one(src, grayscale=False, png_dpi=args.png)
        if args.grayscale:
            ok &= build_one(src, grayscale=True, png_dpi=args.png)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
