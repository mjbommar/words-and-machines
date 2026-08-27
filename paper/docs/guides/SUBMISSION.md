# Submitting to arXiv and SSRN

Current as of July 2026. Set `venue.target` in `paper.yaml`; this guide is the
why behind what each venue turns on.

## arXiv

**Toolchain.** arXiv runs **TeX Live 2025** (default) and 2023; it keeps only
the two most recent releases, so 2023 retires when 2026 lands. The CI container
(`texlive/texlive:TL2025-historic`) matches arXiv, so a CI-green paper compiles
on arXiv. TL2025 ships biblatex 3.20 / biber 2.20 / **bbl format 3.3**.

**Engine.** arXiv's FAQ names `tex`, `pdftex`, `latex`, `pdflatex`, and
`xelatex`. **`lualatex` is not named** — prefer `pdflatex` (the template
default) or `xelatex` for arXiv source upload. `make doctor` flags `lualatex` +
`venue.target: arxiv` as a problem, and `make arxiv` refuses to package it.

**hyperref.** As of late 2025 arXiv **no longer injects hyperref** — your
document must load it. The template does (`preamble/hyperref-last.tex`), so this
is handled; just don't remove it.

**Bibliography — ship the `.bbl`.** arXiv recompiles your source. Since Nov 2025
you *may* instead upload the `.bib` and let arXiv run BibTeX/biber, but shipping
the pre-generated `.bbl` (matching the main `.tex` name) is still the safest,
most reproducible path. `make arxiv` ships the `.bbl`. Two systems:

- **natbib + bibtex** (template default): the `.bbl` is version-agnostic and
  ships trivially. Lowest friction.
- **biblatex + biber**: the `.bbl` must match arXiv's biblatex/biber version
  (bbl format 3.3 on TL2025). If your local biber differs you get
  *"File '.bbl' is wrong format version"*. Fixes: compile locally against a
  matching TeX Live, select the matching TeX Live in the `00README.json`, or
  switch to natbib. `make arxiv` prints the detected `.bbl` format as a check.

**No shell-escape.** arXiv does not run `--shell-escape`. Anything needing it
(`minted`, on-the-fly TikZ externalization, `gnuplot`) fails. The `code` module
is pure `listings`; figures are pre-built PDFs. `make check` fails on `minted`.

**Figures.** pdfLaTeX path accepts `.pdf`/`.png`/`.jpg`. Convert beforehand
(the figure pipelines already emit PDF). A new (Feb 2026) warning fires for
images over 34 megapixels. Total submission cap: 50 MB; per-file warning at
10 MB.

**Accessibility / HTML.** arXiv generates HTML via LaTeXML ("View PDF HTML
(experimental)"; ~75% of the corpus converts error-free and rising). Write for
it: semantic markup (`\emph`, `\section`, real `\title`/`\author`/`abstract`),
**`alt=` on every `\includegraphics`** (the template requires it; `make check`
enforces it), and define macros with `\newcommand` in the preamble (not raw
`\def`/`\catcode`). LaTeXML has bindings for ~400+ packages.

Known conversion caveats for this template's stack (all convert *well* except
where noted):

- **tcolorbox callouts** are the one construct LaTeXML supports only partially —
  complex skins/breakable/TikZ-backed boxes may degrade to a plain block or emit
  a conversion warning. The template's callouts keep their internals to plain
  text/lists, which converts acceptably; keep it that way, and don't put
  essential-only content in a box's *decoration*.
- **The eso-pic title background does NOT appear in the HTML** — there is no page
  background in the HTML model. It's decorative only; the title/authors live in
  real front matter, so no meaning is lost.
- booktabs, longtable, threeparttable, subcaption, cleveref, siunitx, natbib,
  biblatex, orcidlink, listings, and algorithm/algpseudocodex all convert well.

After uploading, check arXiv's per-paper HTML error report and fix flagged items.

**`00README.json`.** `generate_metadata.py` writes `build/arxiv-readme.json`
(spec 1: compiler + `texlive_version` + `stamp`); `make arxiv` ships it as
`00README.json` so arXiv uses the intended compiler and TeX Live version.

**Metadata, DOI, license.** Title/author come from the arXiv form, not
`\hypersetup`. Every arXiv paper gets an automatic DataCite DOI
(`10.48550/arXiv.<id>`); enable ORCID auto-update to push it to your ORCID
record. Pick a license (`venue.license`): CC BY 4.0 (default), CC BY-SA,
CC BY-NC-SA, CC BY-NC-ND, the arXiv non-exclusive license, or CC0 — the choice
is irrevocable per version.

**Packaging.** `make arxiv` is a hardened packager (after
`ioctl-census/make_arxiv.sh`): it rebuilds cleanly, ships the `.bbl` and
`00README.json`, inlines `generated/metadata.tex` into `main.tex`, and — before
tarring — **verifies the bundle compiles standalone with zero undefined
references**. The bundle is already minimal (source + final figure PDFs) and
comment-auditable.

For extra hygiene (comment stripping, image downscaling to hit the 50 MB cap),
run Google's `arxiv-latex-cleaner` (v1.0.11, 2026) on the extracted bundle
before re-zipping — no install needed:

```bash
mkdir /tmp/ax && tar xzf build/arxiv/*-arxiv.tar.gz -C /tmp/ax
uvx arxiv-latex-cleaner --keep_bib /tmp/ax     # -> /tmp/ax_arXiv/
# recompile /tmp/ax_arXiv/main.tex to confirm it still builds, then zip it.
```

Pass `--keep_bib` (we ship the `.bbl`, but keeping `.bib` is harmless and lets
arXiv fall back to running biber); add `--resize_images --im_size 500` only if a
raster figure pushes you near the cap. Always recompile the cleaned copy — the
cleaner strips *all* comments, including any `%!TeX` magic.

## SSRN

**Format.** SSRN (owned by Elsevier; guidelines updated 2026-06-15) takes a
**PDF only**, in English, that shows the **title and all authors with
affiliations** on the page. `make ssrn` builds that PDF and writes
`SSRN-METADATA.md`.

**Form fields.** Title, abstract (English), all authors + affiliations + valid
emails, **keywords** (for discoverability), and **optional JEL codes**
(standard for econ/law). Set them in `paper.yaml`; `export_ssrn_metadata.py`
emits them one-per-line for clean pasting.

**AI disclosure — required.** As of the 2026-06-15 guidelines, an
AI-disclosure statement **must accompany the abstract and appear on the PDF**
when AI was used (exempt only if AI was used solely for accessibility). The
template prints it as a first-page footnote and in the Disclosures section
(`disclosure.ai_used: true`), and the dossier flags it.

**Title page.** For `venue.target: ssrn` the template adds "Working paper —
draft; comments welcome", the JEL block, and a back-matter "Disclosures and
limitations" section (funding, competing interests, data availability, AI).
Optionally set `venue.series` for a working-paper-series line.

**Date.** If `paper.date` is empty the title page uses `\today` — rebuild
(`make ssrn`) the day you upload so the page date matches SSRN's "date written".

**Dossier + checklist.** `make ssrn` writes `SSRN-METADATA.md` (paste-ready
form fields, incl. `venue.ssrn.related`/`networks`/`prior_subtitle`). Copy
`docs/TODO-SSRN.md` to the repo root and work it before uploading.

## Tagged PDF (accessibility) — a future opt-in, not a default

Neither arXiv nor SSRN requires a tagged (PDF/UA) PDF in 2026 — arXiv's
accessibility deliverable is the LaTeXML **HTML**, not tagged PDF. LaTeX's
Tagging Project has matured (put `\DocumentMetadata{tagging=on}` before
`\documentclass` with a TeX Live ≥ 2025 kernel), but tagging still interacts
badly with heavy custom layout — exactly this template's `tcolorbox` callouts,
`eso-pic` background, and two-column mode — and turning it on would also perturb
the byte-reproducible output. So the template deliberately does **not** enable
it. If your institution needs tagged output (e.g. ADA Title II), add
`\DocumentMetadata{tagging=on}` yourself, drop the hero and simplify callouts,
and verify the result — treat it as an experiment, not a supported path.

## Out of scope: law-review submissions

This template targets arXiv and SSRN working papers. A true **law-review**
submission (double-spaced, `twoside`, Bluebook footnote citations via
`autocite=footnote`, *id./supra* signals) is a different genre — `paper.yaml`
offers `linespacing: double` but **not** the footnote-citation apparatus. For
that, see the portfolio's `gpt-law-school/latex` rather than forcing it here.

## Quick reference

| | arXiv | SSRN |
|---|---|---|
| Upload | LaTeX **source** + `.bbl` | **PDF** only |
| `paper.yaml` | `venue.target: arxiv` | `venue.target: ssrn` |
| Command | `make arxiv` | `make ssrn` |
| Dossier | `ARXIV-SUBMISSION.md` | `SSRN-METADATA.md` (+ `docs/TODO-SSRN.md`) |
| Safe engine | pdflatex / xelatex | any (PDF only) |
| Bib | natbib easiest; biblatex needs matched `.bbl` | either |
| Must include | alt-text, `.bbl`, `00README.json` | JEL, keywords, AI disclosure |
