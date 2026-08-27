# Figures — two pipelines, one look

Papers in this portfolio use both matplotlib and TikZ, so the template ships
both. Both write vector PDFs into `latex/figures/`; sections include them with a
bare `\includegraphics{name}` (the `figures/` path is on `\graphicspath`).

## Matplotlib pipeline (data plots)

For anything data-driven. `scripts/build_figures.py` reads aggregate CSVs under
`scripts/data/` and emits PDF+PNG+SVG with one shared **print-safe** style:
serif type matching the paper, grayscale fills with hatching (meaning never
depends on color), Type-42 embedded fonts.

```bash
make figures-mpl                              # all matplotlib figures
uv run --with matplotlib scripts/build_figures.py --only scaling
```

Add a figure: write a `fig_<name>()` function that calls `_save(fig,
"<name>")`, and register it in the `FIGURES` dict. Keep the raw data in
`scripts/data/` so the figure is reproducible from the repo.

## TikZ pipeline (diagrams)

For schematics and flow diagrams. Put a bare `tikzpicture` (or pgfplots `axis`)
body in `latex/figures/src/<name>.tikz` — no `\documentclass`. `build_tikz.py`
wraps it in a `standalone` document that inputs
`latex/figures/figure-preamble.tex`, so every diagram inherits the paper's
palette and serif.

```bash
make figures-tikz                             # all TikZ figures
uv run scripts/build_tikz.py --only pipeline --png   # + preview PNG
uv run scripts/build_tikz.py --grayscale             # B&W variants
```

Use the palette tokens (`fig-accent`, `fig-ink`, `fig-muted`, …) so colors
match the callouts and collapse under `\GrayscaleMode`. **Do not name a TikZ
style `out`, `in`, `left`, …** — they collide with TikZ keys (use `stage`,
`result`, etc.).

## Colour and grayscale

Because a B&W press flattens hue, **do not encode meaning in colour alone** —
distinguish series by fill, hatch, line weight, dash, marker, and label. The
matplotlib style already does this; TikZ figures should too.

## Including a figure (the contract)

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=0.82\linewidth,
    alt={One-sentence description for screen readers, <= 140 chars}]{scaling}
  \caption{What it shows, and why it matters.}
  \label{fig:scaling}
\end{figure}
```

`alt=` is **required** (arXiv HTML / `make check`). Wide figures rotate onto a
landscape page with `sidewaysfigure` (from `rotating`); a table that outruns a
page uses `longtable`; two panels side by side use `subcaption` (see
`latex/sections/A_appendix.tex`).

## Title-page background (hero image)

For a magazine-style cover, set `typography.title_background` in `paper.yaml` to
a figure name (under `latex/figures/`, no extension). It is placed behind the
title on **page 1 only** via `eso-pic`, and collapses to gray under
`\GrayscaleMode` with the palette. A demo asset ships as
`latex/figures/src/title-banner.tikz` (build it with `make figures`):

```yaml
typography:
  title_background: "title-banner"   # -> latex/figures/title-banner.pdf
```

Keep the asset **light** so the title stays legible — a soft accent wash or a
top banner, not a full-bleed dark photo. For a photographic hero, drop a
pre-built PDF/PNG into `latex/figures/` and name it here.
