# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""build_tikz.py — compile standalone TikZ/pgfplots sources into figure PDFs.

Each ``latex/figures/src/<name>.tikz`` (a bare ``tikzpicture`` / ``axis``
body) is wrapped in a ``standalone`` document that inputs
``latex/figures/figure-preamble.tex`` — so every diagram gets the paper's
palette and serif — and compiled to ``latex/figures/<name>.pdf``. Sections
then ``\\includegraphics{<name>}``.

Compiles with pdflatex (Type 1 fonts; portable and arXiv-safe). Options:

  --grayscale   define \\GrayscaleMode -> a B&W variant (<name>-gray.pdf).
  --png[=DPI]   also emit a preview PNG (default 300 dpi) via pdftoppm.
  --only NAME   build a single figure stem (repeatable).

Zero third-party deps: pdflatex + (for --png) pdftoppm.
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

WRAPPER = r"""\documentclass[border=4pt]{standalone}
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
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
             "-output-directory", td, "fig.tex"],
            cwd=td, capture_output=True, text=True,
        )
        pdf = tmp / "fig.pdf"
        if proc.returncode != 0 or not pdf.exists():
            sys.stderr.write(f"build_tikz: FAILED {src.name}\n")
            sys.stderr.write("\n".join(proc.stdout.splitlines()[-18:]) + "\n")
            return False
        dest = OUT / f"{name}.pdf"
        shutil.copyfile(pdf, dest)
        msg = f"build_tikz: latex/figures/{name}.pdf"
        if png_dpi:
            subprocess.run(
                ["pdftoppm", "-png", "-r", str(png_dpi), "-singlefile",
                 pdf.as_posix(), (OUT / name).as_posix()], check=False)
            msg += f"  (+ {name}.png @ {png_dpi}dpi)"
        print(msg)
        return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--grayscale", action="store_true")
    ap.add_argument("--png", nargs="?", const=300, type=int, default=None,
                    metavar="DPI")
    ap.add_argument("--only", action="append", default=[], metavar="NAME")
    args = ap.parse_args()

    if not SRC.is_dir():
        print(f"build_tikz: no sources at {SRC}")
        return 0
    if shutil.which("pdflatex") is None:
        sys.stderr.write("build_tikz: pdflatex not found\n")
        return 1

    sources = sorted(SRC.glob("*.tikz"))
    if args.only:
        wanted = set(args.only)
        sources = [s for s in sources if s.stem in wanted]
    if not sources:
        print("build_tikz: nothing to build")
        return 0

    ok = True
    for src in sources:
        ok &= build_one(src, grayscale=False, png_dpi=args.png)
        if args.grayscale:
            ok &= build_one(src, grayscale=True, png_dpi=args.png)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
