# ADR 0014 — Standalone TikZ figure workflow (module: figures)

## Decision
Diagrams are authored as **standalone TikZ/pgfplots sources** in
`latex/figures/src/*.tikz` and compiled by `scripts/build_figures.py`
(`make figures`) into the `latex/figures/*.pdf` assets that chapters
`\includegraphics` per the authoring contract. Each source is wrapped in
a `standalone` document that inputs `latex/figures/figure-preamble.tex`,
which supplies the book's fonts and the shared palette (`colors.tex`), so
every figure matches the interior and responds to `\GrayscaleMode` (ADR
0006). One source produces the colour asset; `--grayscale` produces a B&W
variant; the EPUB build rasterizes the PDF to PNG at `FIGURE_DPI` (default
200).

## Alternatives considered
- **Raw TikZ in chapters:** rejected by the authoring contract — it does
  not convert to EPUB and would fail the coverage audit (ADR 0007). Keeping
  diagrams out of the prose stream also keeps chapters parseable.
- **Hand-built figure PDFs (status quo):** works, but gives no reproducible
  source, no palette/font consistency, and no grayscale variant — every
  diagram-heavy book re-invented a private build step.
- **TikZ → SVG for EPUB:** vector and crisp, but `dvisvgm` outlines label
  text and converts shadings unevenly, and KDP frequently rasterizes SVG on
  ingest — so PNG (auto-derived) is the reliable default; SVG stays an
  opt-in per figure (the manifest already supports the mimetype).

## Rationale
Diagram-heavy genres (math, logic, CS) were the template's largest gap: it
loaded no TikZ at all. A standalone-compile step is the portable habit
across the sibling books; centralizing it as one script + one shared
preamble means figures inherit the palette (including the ADR 0013
math/logic hues) and the grayscale collapse for free, and the colour vs.
B&W editions come from a single source.

## Consequences
- New: `scripts/build_figures.py` (stdlib only; lualatex + pdftoppm),
  `latex/figures/figure-preamble.tex` (fonts + tikz/pgfplots libraries +
  palette + a Tailwind-name compatibility layer), `latex/figures/src/`
  (a sample source), the `figures` Makefile target, `docs/guides/FIGURES.md`.
- `epub/converter/core.py`: figure rasterization DPI reads `FIGURE_DPI`
  (default 200, non-breaking).
- Authors: put a bare `tikzpicture` in `src/`, run `make figures`, include
  the PDF with `\caption` + `\figalt`; design grayscale-safe (weight/dash/
  label, not hue alone).
- Provenance: the foundations-book project, whose 30 TikZ diagrams drove
  the design.
