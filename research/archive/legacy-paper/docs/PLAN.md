# paper-template — build plan

A configurable LaTeX **paper** production template, sibling to `book-template`,
targeting **arXiv** and **SSRN** preprints/working papers. One `paper.yaml`
drives metadata, engine, fonts, bibliography, and venue; a modular preamble and
a self-documenting Makefile produce the PDF, a hardened arXiv source bundle, and
an SSRN submission dossier.

## Why this exists (evidence from the portfolio)

A survey of 11 `paper/` repos and 5 `latex/`-dir papers found the *same*
boilerplate copy-pasted with drift across eight-plus papers: the ~15-line
package stack, the hyperref color+metadata block, the LLM-assistance `\thanks`,
URL-break hygiene, and the latexmk `clean` recipe. arXiv packaging was
re-implemented per repo (tar vs zip, different path lists). Section-file naming,
`bibtex/` vs `bib/`, `plain` vs `plainnat`, and abstract-as-input vs inline all
diverged for no reason. This template centralizes that shared DNA — exactly as
`book-template` did for the book projects.

## The two worlds this must serve (and why parameterization, not a pick)

| | arXiv house style | SSRN cluster |
|---|---|---|
| Exemplars | ioctl-census, needles-at-scale, binary-* | datacenter-paper-2026, moratorium-paper, us-data-center-opposition |
| Class | `article` 11pt | `article` 11pt letterpaper oneside |
| Engine | **pdflatex** (arXiv-safest) | lualatex + biber |
| Bib | natbib + bibtex (`plain`/`plainnat`) | biblatex authoryear + biber |
| Fonts | CM / Libertine | Libertinus (fontspec) |
| Venue extras | `make arxiv` bundle, alt-text | JEL codes, Disclosures section, `SSRN-METADATA.md` |

arXiv research (July 2026) is decisive on the safe path: arXiv runs **TeX Live
2025** (and 2023); **pdflatex and xelatex are the named-safe engines, lualatex is
not listed** in the FAQ; you must **ship the `.bbl`**, and a biblatex/biber
`.bbl` must match arXiv's format (3.3 on TL2025) while a natbib `.bbl` is
version-agnostic. SSRN (guidelines updated 2026-06-15) takes **PDF only**, wants
title+authors+affiliations on the page, keywords, optional JEL codes, and now
**requires an AI-disclosure statement** when AI was used.

Conclusion: parameterize `engine`, `bib.system`, and `venue`. Default the
shipped sample to the **maximally portable** configuration
(`pdflatex + libertinus + natbib/bibtex + venue: preprint`) so a fresh clone
builds anywhere and uploads to arXiv without a font or `.bbl`-format surprise —
then document the one-line switches to the SSRN look.

## Architecture (mirrors book-template ADRs 0002/0005/0006/0010)

- **`paper.yaml`** — single source of truth (ADR 0002 analogue). Placeholder
  scan fails the build on `TODO`/`[...]`.
- **`scripts/generate_metadata.py`** → `latex/generated/metadata.tex`
  (`\PaperTitle`, `\PaperAuthorBlock`, `\PaperKeywords`, `\PaperJEL`,
  `\PaperDate`, `\ifPaper*` flags, engine/font/bib selectors) +
  `build/arxiv-readme.json` + drives `SSRN-METADATA.md`.
- **`latex/main.tex`** — single entry; reads generated metadata *before*
  `\documentclass`. All variants from one file (ADR 0006 analogue).
- **`latex/preamble/main.tex`** — modular loader, fixed dependency order
  (ADR 0005 analogue):
  `packages → fonts → colors → styling → boxes → code → commands → hyperref-last`.
- **Build-mode flags** via `latexmk -usepretex` (ADR 0006):
  - `\DraftMode` — `lineno` line numbers + "DRAFT · date" banner
  - `\AnonMode` — strip author identity (page + PDF metadata) for double-blind
  - `\GrayscaleMode` — accent ramp collapses to gray for B&W-safe output
- **Engine-aware font profiles** (the key differentiator): `libertinus`,
  `newtx`, `lmodern` build on pdflatex/xelatex/lualatex; `plex` is OpenType-only
  (lua/xe) and errors clearly on pdflatex. Fonts by family/package name, never
  file path.
- **Dual bibliography** via `bib.system`: `natbib` (arXiv-robust, default) or
  `biblatex` (biber/bibtex backend; SSRN authoryear house block). One
  `\PrintBibliography` macro renders either.
- **4-layer color system** (primitives → semantic → component) with a
  `\GrayscaleMode` collapse, distilled from the SSRN cluster's "simplified"
  palette and book-template's ADR 0005.

## Deliverables

1. Config + generator: `paper.yaml`, `scripts/generate_metadata.py`.
2. Modular preamble (8 modules) exercising fonts/colors/styling/boxes/code/commands.
3. A sample paper (`sections/*.tex`) exercising **every** feature: abstract,
   keywords, JEL, figures (matplotlib + TikZ), wide/landscape table,
   `threeparttable`, `booktabs`, `siunitx`, `cleveref`, code listing, callout
   boxes, algorithm, footnotes, appendix, back-matter disclosures.
4. Figure pipelines: `scripts/build_figures.py` (matplotlib print-safe, per
   needles) **and** `scripts/build_tikz.py` (standalone TikZ, per book-template).
5. Hardened arXiv packager `scripts/make_arxiv.py` (per ioctl: fresh build, ship
   `.bbl`, verify standalone compile in a temp dir, assert 0 undefined refs,
   `.bbl`-format check for biber, `00README.json`, report page count).
6. SSRN dossier `scripts/export_ssrn_metadata.py` → paste-ready `SSRN-METADATA.md`.
7. QA scripts: `check_style.py` (STYLE-PAPER lint), `check_refs.py` (undefined
   refs/cites, figure alt-text, wired tables), `wordcount.py`, `doctor.py`.
8. Makefile: `pdf draft arxiv ssrn figures tables check wordcount doctor
   validate watch clean release`.
9. Docs: ADRs, architecture notes, `STYLE-PAPER.md`, `FIGURES.md`,
   `CITATIONS.md`, `SUBMISSION.md`. `.claude/agents/`. CI on TL2025.

## Then: 2–3 review iterations with sub-agents

Compare against `book-template` and the real papers; fix drift, verify every
Make target, verify the arXiv bundle compiles standalone, verify SSRN metadata
matches the built PDF.
