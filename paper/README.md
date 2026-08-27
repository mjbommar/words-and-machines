# paper-template

A configurable LaTeX **paper**-production template for **arXiv** and **SSRN**,
sibling to [`book-template`](../book-template). One `paper.yaml` drives
everything: the LaTeX metadata, the engine and fonts, the bibliography system,
the submission venue, a hardened arXiv source bundle, and a paste-ready SSRN
dossier — with QA gates and reproducible builds.

## Quickstart

```bash
# 1. Instantiate ("Use this template" on GitHub, or clone)
git clone <your-new-repo> mypaper && cd mypaper

# 2. Personalize paper.yaml (title, authors, abstract, venue)
uv run scripts/init_paper.py --title "My Paper" \
  --author "A. Name <a@x.org> @ My Lab" --venue arxiv --fresh

# 3. Build
make pdf          # the paper PDF (engine/bib/venue from paper.yaml)
make figures      # matplotlib + TikZ figures
make check        # style + reference/alt-text gates
make arxiv        # verified arXiv source bundle (ships .bbl)
make ssrn         # SSRN PDF + paste-ready SSRN-METADATA.md
make doctor       # audit the toolchain for THIS config
```

Requires TeX Live 2025 (LuaLaTeX/XeLaTeX/pdfLaTeX + `latexmk` + `biber`),
`uv`, and poppler-utils. `make doctor` audits your toolchain and fonts for the
configuration in `paper.yaml`.

## The one idea

The **submission target**, not the author, decides the mechanical details. The
portfolio it distills splits two ways, and a template that serves both must
parameterize rather than pick:

| | arXiv house style | SSRN cluster |
|---|---|---|
| Engine | **pdflatex** (arXiv-safest) | lualatex + biber |
| Bib | natbib + bibtex | biblatex authoryear + biber |
| Fonts | Computer Modern / Libertine | Libertinus |
| Extras | `make arxiv` bundle, alt-text | JEL codes, disclosures, dossier |

`paper.yaml` exposes `engine`, `citations.system`, `typography.font_profile`,
and `venue.target` as first-class knobs; the shipped default
(`pdflatex + libertinus + natbib + preprint`) is the maximally portable
configuration, so a fresh clone builds anywhere and uploads to arXiv without a
font or `.bbl`-format surprise. See [`docs/guides/SUBMISSION.md`](docs/guides/SUBMISSION.md).

Also configurable: US-letter or **A4**, 1/1.5/2 line spacing, one or two
columns, a **title-page hero image** (`typography.title_background`, via
eso-pic), and B&W-safe output (`make grayscale`). Common paper furniture is
demonstrated in the sample: figures (matplotlib + TikZ), `booktabs` +
`siunitx` + `threeparttable` tables, landscape `sidewaystable`, multi-page
`longtable`, `subcaption` panels, algorithms, code listings, theorems, and
callout boxes.

## What's inside

| Where | What |
|-------|------|
| `paper.yaml` | Single source of truth: title, authors, abstract, keywords, JEL, engine, fonts, bib system, venue, disclosures |
| `latex/` | Single `main.tex`; modular preamble (engine-aware font profiles, layered color, build modes); sample paper exercising every feature |
| `scripts/` | `generate_metadata` (yaml→macros + `00README.json`), `build_figures` (matplotlib) + `build_tikz` (standalone TikZ), `make_arxiv` (verified bundle), `export_arxiv_metadata` + `export_ssrn_metadata` (dossiers), `check_style`/`check_refs`/`wordcount`/`doctor` — all `uv run`, zero install |
| `docs/` | ADRs, architecture (build system, config schema, layout), guides (STYLE-PAPER, FIGURES, CITATIONS, **SUBMISSION**) |
| `.claude/agents/` | Curated agent library for the AI-assisted paper workflow |

## Engine-aware font profiles

The same profile renders on all three engines, so switching engines never means
rewriting the font setup:

| Profile | pdflatex | xelatex / lualatex | Use |
|---|---|---|---|
| `libertinus` | `libertinus` pkg | fontspec Libertinus + Math | house serif (default) |
| `newtx` | `newtxtext`/`newtxmath` | TeX Gyre Termes | Times-like (law/econ) |
| `lmodern` | `lmodern` | Latin Modern | CM look (max arXiv-safe) |
| `plex` | — (errors) | IBM Plex + STIX Two Math | technical (OpenType only) |

## The gates (`make validate`)

| Gate | Catches |
|------|---------|
| `make check` (`check_refs`) | undefined refs/citations, missing figure `alt=` (dead-section is advisory) |
| `make check` (`check_style`) | raw color/spacing/macros in sections, `minted` usage (filler words advisory) |
| `make doctor` | missing tools/packages/fonts for THIS config; CLAUDE.md ↔ Makefile drift |
| `make arxiv` | a source bundle that fails to compile standalone (nonzero exit, TeX errors, or undefined refs) |

Builds pin `SOURCE_DATE_EPOCH` to the last commit and CI runs a frozen
`TL2025` container, so a release rebuilds byte-for-byte.

## License

MIT. See [`LICENSE`](LICENSE).
