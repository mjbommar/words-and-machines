# ADR 0007 — Book-agnostic LaTeX→EPUB converter with handler registry

## Decision
Ship `epub/converter/` as a clean, parameterized Python package (TexSoup + lxml):

- **Generic core**: tokenizes the constrained dialect (ADR 0003), walks chapters, emits XHTML
- **Handler registry**: decorator-registered handlers per command/environment; books add local handlers without touching core
- **`generators.py`**: `container.xml`, `content.opf`, `nav.xhtml`, cover page, title/copyright front matter — all generated from `book.yaml` + discovered chapter structure (never from static templates with baked-in strings)
- **CSS**: house stylesheet with box classes mirroring LaTeX environments, Kindle-safe subset (no flexbox/rgba), dark-mode via `currentColor`/media query, `pre { overflow-x: auto }` for code
- **Gates**: `epubcheck` 0 errors; handler-coverage audit (`epub-check` target) fails the build on unhandled commands; accessibility metadata (schema:accessMode etc.) included

## Evidence
Four books built and shipped with variants of this converter (datacenter ~5,800 lines, htsd, wiki, RFC — RFC's `generators.py` is the best OPF/nav approach). Every copy embedded book-specific strings and handlers in "generic" files, which is the drift this rewrite eliminates. pandoc was tried and abandoned in the early books (code listings, semantic boxes, footnote→endnote all inadequate).

## Consequences
- The converter is written fresh for the template (~1,500 lines target), covering exactly the template's authoring contract; the 5,800-line ancestors remain reference material in `docs/research/`.
- Fonts embedded to match the print profile (ADR 0004).
- Footnotes become chapter endnotes with backlinks; citations resolve through the same .bib.
