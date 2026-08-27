# paper.yaml schema

`generate_metadata.py` validates every field and fails on unknown values or
leftover placeholders (`TODO`/`FIXME`/`XXX`/`[bracketed]`). It emits
`latex/generated/metadata.tex` (macros + `\ifPaper…` flags) and
`build/arxiv-readme.json`.

## Blocks

### `paper`
`title` (req), `subtitle`, `short_title` (running heads; defaults to title),
`date` (empty → `\today` at build; pin for stable rebuilds).

### `authors` (list, req)
Each: `name` (req), `affiliation`, `email`, `orcid`, `corresponding` (bool).
Affiliations are de-duplicated and numbered; the corresponding author (first
with `corresponding: true`, else the first) carries the email + AI-disclosure
`\thanks`. Rendered by the generated `\PaperAuthorBlock`.

### `abstract` (req)
Free text; feeds the title page, PDF metadata, arXiv form, and SSRN dossier.

### `classification`
`keywords` (list), `jel` (list of JEL codes like `C88`; rendered when non-empty
or for SSRN), `msc` (list), `arxiv_primary`/`arxiv_cross` (for the SUBMISSION
doc, not printed).

### `venue`
`target`: `preprint` | `arxiv` | `ssrn`. `series` (optional working-paper
line). `license` (arXiv): `cc-by-4.0` | `cc-by-sa-4.0` | `cc-by-nc-sa-4.0` |
`cc-by-nc-nd-4.0` | `arxiv-nonexclusive` | `cc0`. `ssrn` (all optional, echoed
into `SSRN-METADATA.md`): `prior_subtitle` (reversible-subtitle note),
`related` (list of `{title, abstract_id, note}`), `networks` (list of strings).

### `typography`
`engine`: `pdflatex` | `xelatex` | `lualatex`. `font_profile`: `libertinus` |
`newtx` | `lmodern` | `plex` (`plex` requires a Unicode engine — validated).
`base_size`: 10 | 11 | 12. `paper_size`: `letter` | `a4`. `linespacing`:
`single` | `onehalf` | `double`. `twocolumn`: bool. `title_background`:
optional figure name (under `latex/figures/`, no extension) placed behind the
title on page 1 via eso-pic; empty = none.

### `citations`
`system`: `natbib` | `biblatex`. `style`: `numeric` | `authoryear`.
`bibliography_title`, `sort` (bool).

### `modules`
`boxes`, `code`, `algorithms`, `siunitx` (bools) — gate optional preamble
modules via `\ifPaperModule…`.

### `disclosure`
`ai_used` (bool), `ai_statement`, `funding`, `competing_interests`,
`data_availability`. Feed the first-page footnote, the Disclosures section, and
the SSRN dossier. SSRN requires the AI statement when `ai_used` is true.

## Generated macros (selected)

`\PaperTitle`, `\PaperSubtitle`, `\PaperShortTitle`, `\PaperDate`,
`\PaperAbstract`, `\PaperKeywords`, `\PaperJEL`, `\PaperAuthorBlock`,
`\PaperAuthorPlain`, `\PaperLicense`, `\PaperAIStatement`, `\PaperFunding`,
`\PaperCompeting`, `\PaperDataAvail`, `\PaperBaseSize`, `\PaperFontProfile`,
`\PaperBibSystem`, `\PaperBibStyle`, `\PaperBibTitle`.

Flags: `\ifPaperHasSubtitle`, `\ifPaperHasJEL`, `\ifPaperVenueArxiv`,
`\ifPaperVenueSSRN`, `\ifPaperEnginePDF`, `\ifPaperBibNatbib`,
`\ifPaperBibBiblatex`, `\ifPaperBibNumeric`, `\ifPaperTwoColumn`,
`\ifPaperModuleBoxes/Code/Algo/SI`, `\ifPaperAIUsed`, `\ifPaperSortCites`.

## Makefile-facing flags

`--print-engine` (engine → latexmk flag) and `--print-venue` (Makefile status
line) are read by the Makefile. `--print-bibengine` (bibtex|biber) is available
for scripts but the Makefile relies on latexmk's auto-detection instead.
`--strict` is the release gate (corresponding email set; SSRN AI statement
present); `--allow-placeholders` bypasses the placeholder scan.
