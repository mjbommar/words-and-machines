# Figures — authoring diagrams for print and EPUB

Math, logic, and technical books are diagram-heavy, and the authoring
contract forbids raw TikZ in chapters (it does not convert to EPUB). So
diagrams live as **standalone TikZ sources** that build into the figure
PDFs a chapter includes. One source, both editions.

## The workflow

1. Write a bare `tikzpicture` (or pgfplots `axis`) body — no `\documentclass`,
   no `\begin{document}` — in `latex/figures/src/<name>.tikz`.
2. `make figures` compiles each source, via `latex/figures/figure-preamble.tex`
   (which supplies the book's fonts and palette), into
   `latex/figures/<name>.pdf`.
3. Include it in a chapter per the contract:

   ```latex
   \begin{figure}
     \centering
     \includegraphics[width=0.85\textwidth]{figures/<name>}
     \caption{What it shows, and why it matters.}
     \figalt{One-sentence description for screen readers, <= 140 chars.}
     \label{fig:<name>}
   \end{figure}
   ```

The print build uses the vector PDF directly. The EPUB build rasterizes it
to PNG on its own (no extra step).

## Colour and grayscale — one source, two editions

Use the book palette (`accent-*`, `gray-*`, and the math/logic hues
`ml-blue/teal/amber-*`). Common Tailwind step names (`slate-500`,
`blue-700`, `amber-600`, …) are aliased to it in the preamble, so a
figure written with those renders in-house.

- **Colour edition / EPUB:** `make figures` → colour PDFs.
- **Grayscale POD interior:** `make figures GRAYSCALE=1` → `<name>-gray.pdf`,
  with `\GrayscaleMode` collapsing every hue onto grays (ADR 0006).

Because a B&W press flattens all hue, **do not encode meaning in colour
alone**. Distinguish series by line weight, dash pattern, marker, and
label as well — then the grayscale variant stays readable.

## EPUB resolution and format

The converter rasterizes figure PDFs to PNG at 200 dpi by default. For
crisp diagrams under reader zoom, raise it: `FIGURE_DPI=300 make epub`.

Keep figures as **PNG (auto) for EPUB** — it is the only image format
every reader, Kindle included, renders reliably. SVG is supported in the
manifest but is opt-in per figure: supply a hand-checked `.svg` only for
simple, text-light diagrams in a non-Kindle EPUB. TikZ→SVG (`dvisvgm`)
outlines label text and converts shadings unevenly, and KDP often
rasterizes SVG anyway — so it rarely pays.

## Accessibility

Every figure needs `\figalt{…}` (≤ 140 chars; the OPF conformance claim
depends on it). `\figalt{}` marks a purely decorative figure. For a dense
diagram (a map, a reduction graph), also give a longer description in the
surrounding prose — neither raster nor vector conveys a diagram's meaning
to a screen reader; the words do.

## Options

`make figures` — build all colour PDFs.
`make figures GRAYSCALE=1` — also build B&W variants.
`make figures PNG=1` — also emit 300-dpi preview PNGs.
`uv run scripts/build_figures.py --only <name>` — build one figure.
