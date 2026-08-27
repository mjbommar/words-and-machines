# Research Report: ai-law-finance-book

Source: `/home/mjbommar/projects/personal/ai-law-finance-book`
Reviewed: 2026-07-06. Purpose: extract reusable pieces for the master book template.

---

## 1. Purpose & Status

**What it is**: *Artificial Intelligence for Law and Finance* — an open-source, vendor-neutral LaTeX **textbook** for legal/financial practitioners, regulators, and researchers. 10 chapters across 3 parts (Foundations/LLMs, Agents, Knowledge Graphs). README declares "Status: Working Draft" (last updated December 2025); the title block in `main.tex` says "Version 0.1 --- In Active Development".

**Publication status**: The *main textbook* is an unpublished working draft. However, the repo contains two **minibooks** that are the actual published/publishable products:

- `minibooks/agents-in-law-finance/` — *Agentic AI in Law and Finance* (Bommarito, Katz, Bommarito), **fully publication-ready**: real ISBNs (print 979-8-9943457-0-2, Kindle 979-8-9943457-1-9), KDP + Lulu paperback + Lulu hardcover + Kindle Print Replica + 14pt ebook PDF. KDP.md last reviewed 2026-01-16.
- `minibooks/llm-foundations-law-finance/` — second minibook, same architecture, still has `TODO.md`.

**Formats produced** (minibook level): print interior PDF (6×9), bleed interior PDF (6.25×9.25), Lulu paperback wrap cover, Lulu hardcover case-wrap cover, KDP wrap cover, Kindle Print Replica PDF, 14pt e-reader PDF, timestamped release bundles.

## 2. Directory Layout

```
ai-law-finance-book/
├── CLAUDE.md              # AI-assistant entry point (workflow, quality gates, tool usage)
├── AGENTS.md              # Evidence hierarchy, file conventions, PR checklist (for Codex/Gemini too)
├── README.md              # Public-facing roadmap with per-chapter status (✅/🔄/📋)
├── main.tex               # Root book document (\documentclass{book} + subfiles)
├── preamble.tex           # SHARED single-file preamble (744 lines: fonts, 4-layer colors, boxes)
├── Makefile               # Root build: book / chapters / all-pdfs / validate / png / zip
├── bib/refs.bib           # CONSOLIDATED bibliography (154 entries, 1549 lines)
├── chapters/              # 10 chapters, each: main.tex, sections/*.tex, bib/refs.bib, figures/, Makefile, README.md
│   ├── 01-foundations-llm-primer-mechanics/ … 05-…
│   ├── 06-agents-part-1/ … 08-agents-part-3/
│   └── 09-kg-foundations/, 10-kg-operations-llm/
├── minibooks/             # Standalone extracted books (the real publishing pipeline)
│   ├── agents-in-law-finance/
│   │   ├── main.tex / main-ebook.tex / lulu-cover.tex
│   │   ├── preamble/ {main,packages,colors,tikz,boxes,styling,commands,headers,main-ebook}.tex
│   │   ├── front-matter/ {half-title,title-page,copyright,copyright-ebook,preface,how-to-read,glossary-entries,cover/}
│   │   ├── back-matter/ {about-authors,back-cover,back-cover-art}
│   │   ├── chapters/ 01-what-is-agent/ 02-how-to-design/ 03-how-to-govern/
│   │   ├── covers/ (cover-front.tex, cover-back.tex, archive/, option-06/ design experiments)
│   │   ├── scripts/ {update_cover_vars,update_kdp_cover_vars,check_pdf_dimensions,check_margins,generate_isbn_barcode}.py
│   │   ├── notes/ (validation reports, reorg plans, quality-review results)
│   │   ├── KDP.md          # Complete Amazon KDP publishing playbook
│   │   └── Makefile        # ~745 lines; lulu/kdp/kindle/ebook/release targets
│   └── llm-foundations-law-finance/   # same shape
├── trailers/              # Cross-promotion: ai-professional-services-prologue.pdf (the OTHER book's prologue as a teaser)
├── docs/                  # 9 guides: build-guide, style-guide, color-guide, box-guide, glossary-guide,
│                          #   chapter-setup, content-planning, prose-editing-checklist, README
└── scripts/               # Repo-wide validation + prose-analysis tools (see §5)
```

**Organizational analysis**: This repo pioneered the pattern the second book later cleaned up. Key ideas:

1. **Dual compilation** — root `main.tex` + shared `preamble.tex` + `subfiles`, so each chapter compiles standalone *and* into the book. `main.tex` sets `\def\input@path{{./}{../}{../../}}` so `preamble.tex` resolves from either level.
2. **Consolidated root `bib/refs.bib`** plus per-chapter `bib/refs.bib` (chapter-standalone builds cite locally; the book cites the merged root file). AGENTS.md records "Consolidate citations into root bib/refs.bib (Completed: November 2025)".
3. **Minibooks as extraction products**: the minibook README states the minibook is the *canonical* version of the agents content ("Changes should be made here first, then synced to the main book") — i.e., content forked from the textbook and diverged. That divergence is a real maintenance cost (see §10 pitfalls).
4. **`trailers/`** holds a PDF prologue of the *sibling* book (`ai-professional-services`) to bundle as promotional back-matter — cheap cross-marketing between books in the same family.

## 3. LaTeX Pipeline

There are **two distinct pipelines**: the textbook (pdfLaTeX, letter-ish geometry, monolithic preamble) and the minibooks (XeLaTeX, US Trade 6×9, modular preamble). The minibook pipeline is the mature one.

### 3.1 Textbook root (`main.tex`, `preamble.tex`)

- `\documentclass[11pt,oneside]{book}`; `\usepackage{import}` then `\usepackage{subfiles}`.
- Chapters as `\subfile{chapters/06-agents-part-1/main}` under `\part{...}` headings; `\frontmatter`/`\mainmatter`/`\backmatter`; single `\printbibliography`.

Fonts and page setup, `preamble.tex:14-31` (verbatim):

```latex
\usepackage[margin=1.2in, top=1.3in, bottom=1.3in]{geometry}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}

% Modern font: Libertinus (elegant, readable serif)
\usepackage{libertinus}
\usepackage{libertinust1math} % Math support for Libertinus

% Typography enhancements
\usepackage{microtype}  % Improved typography and spacing
\DisableLigatures{encoding = T1}  % Disable ligatures for better print compatibility
\usepackage{setspace}   % Line spacing control
\setstretch{1.15}       % Slightly increased line spacing for readability

% Paragraph formatting
\usepackage{parskip}    % Space between paragraphs instead of indentation
\setlength{\parskip}{0.5em}
\setlength{\parindent}{0pt}
```

Note the trade-offs: parskip style (report-like, not book-like), ligatures disabled, generic paper size. The minibooks fix all three.

**4-layer semantic color system** (`preamble.tex:50-273`) — the most reusable design asset:

- Layer 1 *primitives*: Tailwind-style scales (`slate-900`, `green-600`, `amber-100`, `gray-100..900`, `cream-100`) — "Change these to rebrand the entire document."
- Layer 2 *semantics*: seven educational content types, each with `-dark/-base/-light` variants: `definition` (blue), `example` (green), `key` (amber), `caution` (red), `note` (neutral/cream), `theorem` (indigo), `practice` (teal).
- Layer 3 *component aliases*: `bg-definition`, `border-key`, `text-caution`, `text-primary/secondary/muted`, `primary`, `accent` — self-documenting usage.
- Layer 4 *legacy aliases* (`agentblue`, `primary-slate`, …) kept for gradual migration.

**Box environments** (`preamble.tex:294-584`): tcolorbox with `\tcbuselibrary{breakable,skins,theorems,listings}`. Environments: `definitionbox`, `examplebox`, `highlightbox`, `keybox`, `questionbox`, `theorembox`, `cautionbox`, `technicalbox`, `practicebox`, plus `listingbox` (`\newtcblisting`) for code. All share the pattern: `enhanced`, semantic `colback/colframe`, attached boxed title, `breakable`, subtle drop shadow, west borderline for some types. There is also a **book-wide importance scale** (verbatim, `preamble.tex:311-330`):

```latex
% Importance scaling for tcolorbox environments (book-wide)
% Usage in any box: [importance=low|medium|high]
\tcbset{
  importance/.is choice,
  importance/high/.style={
    boxrule=2pt,
    drop shadow={shadow xshift=1pt, shadow yshift=-1pt, opacity=0.14},
    top=10pt,bottom=10pt,left=12pt,right=12pt
  },
  importance/medium/.style={},
  importance/low/.style={
    boxrule=0.8pt,
    drop shadow={opacity=0},
    opacityback=0.92,
    opacityframe=0.6,
    boxed title style={opacityback=0.85},
    top=6pt,bottom=6pt,left=8pt,right=8pt
  },
  importance/.default=medium
}
```

The book even ships a front-matter chapter "How to Read This Book" explaining the box colors and importance levels to readers — a nice template idea.

**Sectioning** via `titlesec`/`titletoc` (colored `\Large\bfseries\color{primary}` sections with `\titlerule`), custom ToC entries, `caption` with `labelfont={bf,color=primary}`, `cleveref` with capitalized `\crefname`s, `hyperref` with `colorlinks=true, linkcolor=primary, citecolor=accent`.

**Bibliography** (verbatim, `preamble.tex:714-731`; identical block reappears in both projects — this is the house standard):

```latex
\usepackage[
  backend=biber,
  style=authoryear,
  maxcitenames=2,
  maxbibnames=99,
  uniquename=false,
  uniquelist=false,
  sorting=nyt,
  dashed=false
]{biblatex}

% Citation formatting
\DeclareFieldFormat{citetitle}{\mkbibquote{#1}}
\DeclareFieldFormat[article]{citetitle}{#1}
\DeclareFieldFormat[inproceedings]{citetitle}{#1}
\DeclareFieldFormat[book]{citetitle}{\mkbibemph{#1}}
```

### 3.2 Minibook pipeline (`minibooks/agents-in-law-finance/`) — the template-grade version

- `\documentclass[10pt,twoside,openright]{book}`, compiled with **XeLaTeX** (`latexmk -xelatex ... -recorder`).
- **Modular preamble** loaded via `\input{preamble/main}` which chains, in dependency order: `packages → colors → tikz → boxes → styling → commands → headers`. Each file documents its load-order constraints.

**Trim/geometry with bleed switch** (verbatim, `preamble/packages.tex:10-32`):

```latex
% US Trade size: 6in x 9in (standard for professional/technical books)
\usepackage[
  papersize={6in,9in},
  inner=0.80in,       % Gutter margin (for binding) - increased for KDP
  outer=0.55in,       % Outside margin - increased for KDP
  top=0.7in,
  bottom=0.8in,
  footskip=0.35in
]{geometry}

% Bleed build: expand canvas to 6.25 x 9.25 while preserving trim margins.
\ifdefined\BleedMode
  \geometry{
    paperwidth=6.25in,
    paperheight=9.25in,
    inner=0.875in,
    outer=0.625in,
    top=0.825in,
    bottom=0.925in,
    footskip=0.35in
  }
\fi
```

The Makefile triggers bleed mode without touching sources: `BLEED_INPUT = \\def\\BleedMode{1}\\input{$(TEXFILE)}` compiled under `-jobname=interior-bleed`.

**Engine-adaptive fonts** (`preamble/packages.tex:34-74`): `iftex` detection; Libertinus everywhere ("libertinus package auto-detects engine: XeLaTeX/LuaLaTeX loads libertinus-otf … pdfLaTeX loads libertinus-type1"); mono font matched with a graceful fallback chain:

```latex
\ifxetex
  \IfFontExistsTF{Libertinus Mono}
    {\setmonofont{Libertinus Mono}[Scale=MatchLowercase]}
    {\IfFontExistsTF{LibertinusMono}
      {\setmonofont{LibertinusMono}[Scale=MatchLowercase]}
      {\IfFileExists{LibertinusMono-Regular.otf}
        {\setmonofont{LibertinusMono-Regular.otf}[Scale=MatchLowercase]}
        {\setmonofont{Latin Modern Mono}[Scale=MatchLowercase]}}}
```

`libertinust1math` only under `\ifpdftex` (OTF math comes via unicode-math otherwise).

**Print-craft settings** (`packages.tex:108-126`): `\raggedbottom` (with rationale comment), `\emergencystretch=2em`, and widow/orphan control:

```latex
\widowpenalty=10000
\clubpenalty=10000
\brokenpenalty=10000  % Discourage hyphenation across page breaks
\tolerance=1500
\hyphenpenalty=1200
\exhyphenpenalty=1200
```

**Headers/footers** (`preamble/headers.tex`): fancyhdr with US Trade conventions, encoded as three named page styles plus a redefined `plain`:

- `frontmatterstyle`: folios only, no running heads, no rules.
- `mainmatterstyle`: verso `\thepage\quad\textsc{\booktitle}`, recto `\textsc{\leftmark}\quad\thepage`, 0.4pt headrule.
- `backmatterstyle`: same as main matter.
- `plain` (chapter openers): folio at outer top corner only.
- `\chaptermark` redefined to chapter title only; `\sectionmark` disabled ("prevents long section titles in headers").
- Switching commands `\usefrontmatterstyle` / `\usemainmatterstyle` / `\usebackmatterstyle` called at matter boundaries in `main.tex`.
- **Selective `\cleardoublepage` toggle** — saves the original and swaps in `\clearpage` so blank versos are inserted only where wanted:

```latex
\let\cleardoublepagestd\cleardoublepage
\newcommand{\disablecleardoublepage}{\let\cleardoublepage\clearpage}
\newcommand{\enablecleardoublepage}{\let\cleardoublepage\cleardoublepagestd}
```

**Section heading orphan protection** (`preamble/styling.tex`) — wraps sectioning commands in `needspace`:

```latex
\let\originalsection\section
\renewcommand{\section}{\Needspace{5\baselineskip}\originalsection}
\let\originalsubsection\subsection
\renewcommand{\subsection}{\Needspace{4\baselineskip}\originalsubsection}
```

**Glossary**: `glossaries` package with `[toc, section=chapter, nopostdot, automake=immediate]` + `glossary-longbooktabs`; entries centralized in `front-matter/glossary-entries.tex`; `\printglossary[title={Glossary of Key Terms}]` in back matter. `docs/glossary-guide.md` documents the workflow.

**Front/back matter**: proper US Trade page order is encoded and commented in `main.tex` (half-title recto → blank verso → title recto → copyright verso → ToC recto → preface → how-to-read). The **cover is compiled into the same document** with `\pagenumbering{Alph}` "to avoid hyperref anchor conflicts with frontmatter roman numerals", then stripped by `mutool` for the print interior. There is a separate `copyright-ebook.tex` for the ebook variant.

**Ebook variant**: `main-ebook.tex` + `preamble/main-ebook.tex` loads the full base preamble, then overrides: larger base font (extbook/14pt), symmetric narrow margins, one-sided layout, no headers, no blank versos. Same content sources — single source of truth across print/ebook.

## 4. Bibliography / Citations Workflow

- **Style**: BibLaTeX + biber, `authoryear`, `sorting=nyt`, `maxcitenames=2`, `maxbibnames=99` (full block quoted in §3.1). Citations via `\parencite` / `\textcite` / `\parencite[p.~42]{key}`.
- **Layout**: consolidated `bib/refs.bib` (154 entries) at root; each chapter also has its own `bib/refs.bib` for standalone builds. Minibooks carry their own `bib/refs.bib`.
- **Metadata rules** (AGENTS.md/CLAUDE.md, mandatory): every entry includes title, authors, venue, date, stable URL/DOI, `urldate`, **and a 1–2 line relevance note in the `note` field** ("note = {Relevance: Establishes key framework for...}"). Evidence hierarchy is spelled out per domain (statutes/reporters for law; SEC/FRB/BIS/FSB for finance; peer review/arXiv/vendor docs for research), with an explicit rule: facts after June 2024 must be re-verified via web search before inclusion, and effective dates stated.
- **Legal citation plan**: Bluebook elements mapped into BibLaTeX fields (`shorttitle`, `note`, `institution`, `jurisdiction`, `howpublished`); a Bluebook-mapping appendix is an open task.
- **Tooling**:
  - `scripts/check_bib.sh` — lints all `.bib` files (part of `run_all.sh`).
  - `scripts/find_unused_citations.py` — "Compares citation keys defined in .bib files against actual usage in .tex files."
  - `scripts/bib_to_checklist.py` — "Convert a BibTeX file to a markdown checklist for review" (human/AI source-verification pass).
  - `make validate` — greps the `.log` for undefined references/citations and multiply-defined labels.

## 5. Build Automation

### Root `Makefile`
Targets: `pdf` (latexmk if available, else manual 4-pass `pdflatex → biber → pdflatex → pdflatex` with per-pass logs), `quick`, `watch` (`latexmk -pvc`), `book`, `chapters` (iterates `chapters/*/Makefile`), `all-pdfs`, `validate`, `view`, `png` (pdftoppm 300dpi), `zip`, `wordcount` (detex), `clean/cleanall/distclean`, `show-summary` (pdfinfo page/size report), `help`. Heavy use of ANSI colors and ✓/✗/➜/★ icons for readable output. Each chapter dir carries a copy of a similar Makefile (pdflatex-based).

### Minibook `Makefile` (~745 lines) — the crown jewel
Beyond `pdf/quick/watch/validate/clean`: 

- `ebook` — 14pt e-reader build from `main-ebook.tex`.
- `interior` / `interior-bleed` — strip cover pages with `mutool merge -o out.pdf main.pdf 3-$last` (pages 1–2 are the in-document cover + blank verso); bleed variant recompiles under `\def\BleedMode{1}` jobname.
- `cover-vars` → `scripts/update_cover_vars.py --pdf lulu-interior.pdf --output front-matter/cover/cover-vars.tex` — **computes spine width from actual page count** (paperback formula `(pages/444)+0.06 in`; hardcover via a discrete Lulu lookup table with 0.75" wrap area) and writes LaTeX `\def`s consumed by `lulu-cover.tex`.
- `cover`, `cover-hardcover`, `kdp-cover` — one shared `lulu-cover.tex` wrap-cover template parameterized only by the vars file (temporarily swapped in for HC/KDP jobs); Ghostscript flattening to PDF 1.3 `-dPDFSETTINGS=/prepress` for printer compatibility (with a comment warning that flattening the *interior* rasterizes and 100x-inflates files, so it's disabled there).
- `cover-check` / `kdp-cover-check` — `scripts/check_pdf_dimensions.py` verifies produced cover size matches the computed vars.
- `kdp`, `kindle`, `lulu-paperback`, `lulu-hardcover` — per-channel bundles with printed upload instructions.
- `release` — timestamped copies to `build/pdf/"$(BOOK_TITLE) - YYYYmmdd-HHMM - {PRINT,EBOOK,PRINT-BLEED}.pdf"`.

### Repo-wide `scripts/`
Shell (all source `lib.sh` for colored logging; graceful "tool not installed" skips):
- `check_markdown.sh` (markdownlint), `check_latex.sh` (lacheck/chktex, `STRICT=1` to fail on warnings), `check_bib.sh`, `check_spelling.sh` (codespell), `check_links.sh` (lychee), `check_yaml.sh` (yamllint), `run_all.sh` (runs all), `test_chapter.sh` (build+validate one chapter), `lib.sh`.

Python (run via `uv run --with rich,typer …` — deps declared in the invocation, no venv):
- `tex_paragraphs.py` — find short (<30 words) / long (>150) paragraphs; outputs clickable `file:line`; formats table/json/jsonl/csv.
- `tex_frequency.py` — over-used word/phrase frequencies, per-file breakdown.
- `tex_chunks.py` — sliding-window paragraph chunks (3-para window, 1 overlap) exported as JSONL **specifically for LLM review passes**.
- `tex_utils.py` — shared LaTeX-stripping helpers.
- `find_unused_citations.py`, `bib_to_checklist.py`, `generate_toc_csv.py` (chapter/section index CSV from main.tex order).
- Minibook-local: `check_margins.py` (renders pages via pypdfium2/numpy/pillow, flags non-white pixels in margin zones with LOW/MEDIUM/HIGH severity, twoside-aware inner/outer swap, `--debug-pages` annotated PNGs; default profile is US Trade 6×9 with 0.75/0.625/0.7/0.8 margins), `check_pdf_dimensions.py`, `update_cover_vars.py`, `update_kdp_cover_vars.py` (KDP spine formula `pages × 0.002252 + 0.06`), `generate_isbn_barcode.py`.

Python deps overall: `rich`, `typer`, `pillow`, `pypdfium2`, `numpy` — invoked ad hoc through `uv run --with`, never a project venv.

## 6. Sub-products

- **`minibooks/`** — standalone spin-off books extracted from parts of the textbook (Agents part → *Agentic AI in Law and Finance*; Foundations part → *LLM Foundations*). Each is a complete self-sufficient book repo-within-a-repo (own preamble, bib, covers, Makefile, KDP metadata). Generated by copying and reworking chapter content — after which the minibook became canonical and the main book secondary (explicitly documented in the minibook README). Cover design experiments preserved under `covers/archive/` and `covers/option-06/` (TikZ covers with generated network graphs via `generate_network.py`).
- **`trailers/`** — contains `ai-professional-services-prologue.pdf`: the prologue of the sibling book rendered as a standalone teaser PDF, presumably bound into this book's back matter / distributed as cross-promotion. (Generation lives in the sibling repo's `latex/serial/` system.)

## 7. Metadata & Publishing

No STATUS.md; status lives in README.md (roadmap table with ✅/🔄/📋 per chapter) and AGENTS.md "Open Tasks". The publishing metadata is concentrated in **`minibooks/agents-in-law-finance/KDP.md`**, a complete, reusable publishing playbook containing: ISBNs, build commands, KDP form values (trim 6×9, B&W/white, no bleed, matte), **HTML sales description + plain-text Bowker description + 350-char short description + one-liner + taglines**, three author bios, category strategy (3 Amazon categories + alternatives), **7 keyword slots with character counts and rotation alternatives**, BISAC codes table, comparable-titles market research with pricing tiers, recommended prices (paper $29.99 / Kindle $19.99 / HC $44.99) with rationale, pre-publication checklist, and a 90-day post-publication marketing plan (Author Central, A+ content, category requests, keyword rotation, professional channels). License: CC BY-SA (DRM off, no KDP Select).

Cover process: fully in-repo — TikZ front/back covers compiled to PDFs, composed into a wrap by `lulu-cover.tex` using script-computed dimensions; ISBN barcode generated by script; dimension check gate before upload.

## 8. Style / Craft / AI-tone Guides

- **CLAUDE.md** (large): AI-assistant entry point. Notable sections: a "⚠️ CRITICAL: Current Date and Technology Verification" block mandating web-search verification of any model/API claims and listing the current model landscape with "any model reference > 6 months old → VERIFY"; voice rules ("we" for analysis, "you" for guidance, never "I", avoid "one"); box-title length limit (≤4-5 words, "long titles overflow into margins"); table-width tactics (tabularx, `@{}` specifiers, split/convert-to-prose); LaTeX snippets for sections/boxes/citations; troubleshooting; a documented file hierarchy diagram; and a changelog table.
- **AGENTS.md**: evidence/source hierarchy by domain, writing musts, file/naming conventions (`sec:<slug>-<topic>`, `fig-<slug>-<name>.pdf`), quality gates PR checklist, commit hygiene (`area: summary (refs #issue)`), prohibited content (client-confidential, MNPI, PII).
- **docs/style-guide.md** (692 lines): tone/voice/tense, chapter-vs-book framing language, cross-referencing rules (`\Cref{}`, never "see above"), keyterm highlighting, sentence/paragraph length, active voice, pitfalls (double negatives, apologetic framing, vague intensifiers, hedging), boxes/emphasis/tables/quotes, grammar mechanics, revision checklist.
- **docs/prose-editing-checklist.md** (334 lines): em-dash overuse, fragments, semicolon lists → flow, colon lists → paragraphs, sentence-structure variety, preferred conjunctions/transitions, box design and conversion, table design, voice/tone. This is an early ancestor of the second project's AI-tells regime.
- **docs/color-guide.md** (1164 lines), **box-guide.md**, **glossary-guide.md**, **chapter-setup.md** (1224 lines), **content-planning.md**, **build-guide.md** (643 lines: dual-compilation architecture, adding a chapter, troubleshooting).

## 9. QA / Review Workflow

- Quality gates checklist (AGENTS.md + CLAUDE.md): compiles clean, `make validate` clean, style-guide conformance, citations dated, figures labeled/captioned/referenced with alt text, **no HIGH severity margin violations** (`scripts/check_margins.py check main.pdf --no-top`), no prohibited data.
- Layered automated checks: `run_all.sh` (markdown/spelling/yaml/links/latex/bib), `make validate`, margin checker, unused-citation finder, prose-analytics trio (paragraphs/frequency/chunks) designed to feed LLM review.
- Minibook `notes/` retains QA artifacts: `VALIDATION-REPORT.md`, `quality-review-results.md`, reorganization plans — evidence of review passes kept adjacent to the product.
- CI is an acknowledged gap: "Add CI to compile chapters and the book on PRs" is still an open task.

## 10. Verdict — Reusables & Pitfalls

**Take for the master template (highest value first):**
1. The **minibook preamble architecture**: `preamble/{main,packages,colors,tikz,boxes,styling,commands,headers}.tex` with documented load order — strictly better than the root's 744-line monolith.
2. The **publishing Makefile**: interior-strip via mutool, `\BleedMode` bleed builds, page-count-driven spine/cover-vars generation, one parameterized wrap-cover template serving Lulu paperback/hardcover/KDP, ghostscript flattening for covers only, dimension-check gates, timestamped `release` target.
3. **4-layer semantic color system** + tcolorbox family + `importance=` key + reader-facing "How to Read This Book" page.
4. **Headers/matter machinery**: named fancyhdr page styles per matter, `plain` redefinition, chapter-only `\leftmark`, `\enablecleardoublepage`/`\disablecleardoublepage` toggles, `\pagenumbering{Alph}` cover trick, needspace-wrapped section commands, widow/orphan penalties.
5. **Bibliography discipline**: the exact biblatex block, `urldate` + relevance-note convention, evidence hierarchy text, `find_unused_citations.py`, `bib_to_checklist.py`.
6. **KDP.md as a template document** — every future book should start with this skeleton (metadata, categories, keywords, pricing, checklists).
7. `scripts/lib.sh` + check_* suite and the uv-run prose tools; `check_margins.py` as a print-QA gate.
8. Dual-compilation (subfiles + shared preamble + per-chapter bib) *if* the template wants standalone chapter builds.

**Pitfalls observed:**
- **Preamble drift**: chapters 02/06/07/08 use `\documentclass[11pt]{article}` with a *pasted copy* of the preamble (even with divergent comments — ch. 06 re-enables ligatures that `preamble.tex` disables), while 01/03/04/05/09/10 correctly use `\documentclass[../../main.tex]{subfiles}`. The dual-compilation promise is broken for half the chapters; a template must make the subfiles pattern impossible to bypass.
- **Content forking**: minibook vs. main-book chapter divergence with a "canonical here, sync manually" note — a known trap; the sibling project solved it with single-source chapter files included by multiple wrappers.
- Two engines (pdfLaTeX root, XeLaTeX minibooks) and two geometries in one repo; the CLAUDE.md margin-checker section describes 6×9 defaults that don't match the root book's 1.2in-margin geometry, and root `scripts/` doesn't actually contain `check_margins.py` (it lives in the minibook) — docs drifted from reality.
- Root Makefile dependency line references `sections/*.tex figures/*.tex` that don't exist at root (copied from a chapter Makefile).
- Legacy color aliases (Layer 4) linger; migration never finished.

**Unique to this repo**: the importance-scaled box system, the trailer/cross-promo concept, the KDP/Lulu dual-channel cover math with hardcover lookup table, and the "AI assistant guide as first-class repo artifact" pattern (CLAUDE.md + AGENTS.md division of labor).
