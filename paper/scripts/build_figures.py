# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib>=3.8"]
# ///
"""build_figures.py — reproducible matplotlib figures for the paper.

Run with an ephemeral matplotlib (no project install required):

    uv run scripts/build_figures.py

Every figure shares one print-safe style: serif type matching the paper,
grayscale fills with hatching (so meaning never depends on color), and
Type-42 embedded fonts. Reads aggregate CSVs under ``scripts/data/`` and
writes PDF + PNG + SVG for each figure into ``latex/figures/``. The print
build uses the vector PDF; ``alt=`` text lives in the section, not here.

Add a figure: write a ``fig_<name>()`` function that calls ``_save(fig,
"<name>")`` and append it to ``FIGURES`` at the bottom.
"""
from __future__ import annotations

import argparse
import csv
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "data"
FIGS = HERE.parent / "latex" / "figures"
FIGS.mkdir(parents=True, exist_ok=True)

# --- one shared style: serif, grayscale, hatch-friendly -------------------
plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["Libertinus Serif", "CMU Serif", "DejaVu Serif",
                       "Times New Roman"],
        "mathtext.fontset": "cm",
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "legend.fontsize": 8,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": "#333333",
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": "#000000",
        "grid.alpha": 0.12,
        "grid.linewidth": 0.5,
        "hatch.linewidth": 0.6,
    }
)

# Grayscale fills + a hatch vocabulary so grouped series stay distinct in B&W.
FILLS = ["#dcdcdc", "#9a9a9a", "#5a5a5a"]
HATCHES = ["", "///", "..."]
INK = "#1a1a1a"


def read_csv(path: pathlib.Path) -> list[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def _save(fig, name: str) -> None:
    for ext in ("pdf", "png", "svg"):
        fig.savefig(FIGS / f"{name}.{ext}", bbox_inches="tight", dpi=220)
    plt.close(fig)
    print(f"  wrote latex/figures/{name}.{{pdf,png,svg}}")


def fig_scaling() -> None:
    """Grouped bars: per-step build time across the three engines."""
    rows = read_csv(DATA / "scaling.csv")
    steps = [r["step"].replace("_", " ") for r in rows]
    engines = ["pdflatex", "xelatex", "lualatex"]
    x = range(len(steps))
    width = 0.26

    fig, ax = plt.subplots(figsize=(5.4, 3.0))
    for i, eng in enumerate(engines):
        vals = [float(r[eng]) for r in rows]
        offs = [xi + (i - 1) * width for xi in x]
        ax.bar(offs, vals, width, label=eng, color=FILLS[i], hatch=HATCHES[i],
               edgecolor=INK, linewidth=0.6)
    ax.set_xticks(list(x))
    ax.set_xticklabels(steps, rotation=15, ha="right")
    ax.set_ylabel("time (s, illustrative)")
    ax.set_title("Per-step build time by engine")
    ax.legend(frameon=False, ncol=3, loc="upper center",
              bbox_to_anchor=(0.5, 1.28))
    _save(fig, "scaling")


FIGURES = {
    "scaling": fig_scaling,
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", action="append", default=[], metavar="NAME",
                    help="build only this figure (repeatable)")
    args = ap.parse_args()
    names = args.only or list(FIGURES)
    for name in names:
        if name not in FIGURES:
            print(f"build_figures: unknown figure {name!r}")
            return 1
        FIGURES[name]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
