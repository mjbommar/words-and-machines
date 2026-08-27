# Build system

## One entry, all variants

`latex/main.tex` is the single entry point. Build variants come from
**build-mode flags** injected at compile time via `latexmk -usepretex`, with a
distinct `-jobname` per variant, building **out-of-tree** into `build/latex/`:

| Mode | Flag | Effect | Read in |
|---|---|---|---|
| default | — | the paper | — |
| draft | `\DraftMode` | `lineno` line numbers + "DRAFT" banner | `styling.tex` |
| anon | `\AnonMode` | author identity stripped (double-blind) | `frontmatter/titleblock.tex` |

`main.tex` reads `generated/metadata.tex` **before** `\documentclass` because
`\PaperBaseSize` and `\ifPaperTwoColumn` feed the class options.

## Engine and bibliography are data

The Makefile asks `generate_metadata.py` for the engine and venue:

```make
ENGINE := $(shell $(GEN) --print-engine)   # pdflatex | xelatex | lualatex
VENUE  := $(shell $(GEN) --print-venue)     # preprint | arxiv | ssrn
```

and maps the engine to latexmk's flag (`-pdf` / `-pdfxe` / `-pdflua`).
latexmk auto-detects the bibliography backend (bibtex for natbib, biber for
biblatex) from the `.aux`/`.bcf`, so one rule handles both.

## Targets

```
pdf quick draft anon           # interiors
figures figures-mpl figures-tikz  # figures
arxiv ssrn                     # submission
check wordcount doctor validate   # QA
release watch clean            # lifecycle
```

`make help` lists them (it greps the `##` comments). See CLAUDE.md for the full
table.

## Reproducible builds

`SOURCE_DATE_EPOCH` is pinned to the last commit's timestamp (falling back to
now pre-commit), so `\today` and PDF timestamps are stable; CI runs a frozen
`texlive/texlive:TL2025-historic` container that matches arXiv's toolchain. Two
builds of the same tree are byte-identical.

## The arXiv packager

`make arxiv` (`scripts/make_arxiv.py`) is the one non-trivial target:

1. `make pdf` — refresh `main.bbl` and `main.pdf`.
2. Stage sources + final figure PDFs into a temp dir; **inline**
   `generated/metadata.tex` into `main.tex` so the bundle needs no generation
   step; copy `main.bbl` and `00README.json`.
3. **Verify**: compile the stage standalone (twice) with the configured engine;
   assert a PDF is produced with **zero undefined references**.
4. Drop compile byproducts and tar the verified stage.

This catches the classic failure — a bundle that builds for you (with your
`generated/` dir and bib backend) but not for arXiv.

## Out-of-tree note

`bibtex`/`biber` refuse to write outside the tree under `openout_any=p`;
latexmk sidesteps this by running the backend in the output directory with the
source dir on `BIBINPUTS`. Always build via `make`/latexmk, not a bare
`pdflatex; bibtex` from `build/`.
