# Research Report: `datacenter-2026-book` ("This Is Server Country")

**Reviewed:** 2026-07-06
**Project path:** `/home/mjbommar/projects/personal/datacenter-2026-book`
**Purpose of this report:** Primary source for building a master book template. All paths below are absolute into the reviewed project unless noted. Configuration is quoted verbatim so the setup can be rebuilt without opening the original project.

---

## 1. Purpose & Status

**Book:** *This Is Server Country: AI, Power, and the Remaking of Rural America* (subtitle in KDP.md/copyright; earlier subtitle "AI, Power, and Politics" persists in some files) by Michael J Bommarito II. Narrative nonfiction about the US AI data-center buildout, anchored on Saline Township, Michigan, structured as "the life of a token" traced backward through the infrastructure stack (Prologue + 13 chapters + Epilogue, ~98,000 words full edition).

**Status:** Published/publication-ready. Evidence:
- `published/` contains final PDFs: `This is Server Country - Complete Edition.pdf` and `This is Server Country - Essential Edition.pdf`.
- `release/v1.0/` contains uploaded artifacts: `KDP-Interior-400pp.pdf`, `KDP-Cover-Paperback.pdf`, `Lulu-Interior-400pp.pdf`, `Lulu-Cover-Paperback.pdf`, `Lulu-Cover-Hardcover-Casewrap.pdf`, `This-Is-Server-Country-v1.0.epub`, `This-Is-Server-Country-v1.0.pdf`, plus a snapshot `KDP.md`.
- Real ISBNs assigned: **979-8-9943457-3-3** (paperback), **979-8-9943457-2-6** (ebook), **979-8-9943457-4-0** (Essential Edition ebook, from `epub-abridged/templates/content.opf`).

**Formats produced (four editions across two trims/channels):**
1. **Full print edition** (`latex/`) — 6×9 US Trade, XeLaTeX; KDP paperback interior+wrap cover; Lulu paperback and Lulu hardcover (case wrap) covers from the same interior.
2. **Full EPUB** (`epub/`) — custom Python LaTeX→XHTML converter, EPUB 3, Kindle via Calibre `ebook-convert` (AZW3/MOBI targets in Makefile).
3. **Essential Edition** (`latex-abridged/` + `epub-abridged/`) — ~41k-word abridged print + EPUB, derived from the audiobook scripts.
4. **Abridged audiobook** (`abridged-audio-book/`) — 17 narrator-ready Markdown scripts, 4–5 hr runtime target (~42k words). Human-narrator oriented, not TTS (a `tts-test/` dir is gitignored, suggesting TTS experiments happened but weren't kept).

The pipeline chain: **Full book → abridged audiobook scripts → Essential print/ebook edition.**

---

## 2. Directory Layout (annotated)

```
datacenter-2026-book/
├── CLAUDE.md                    # Master AI instructions (27 KB): date awareness, citation-verification
│                                #   rules ("YOU HAVE FAILED AT THIS BEFORE"), style summary, structure,
│                                #   edition matrix, workflow, prohibited content
├── AGENTS.md                    # Condensed agent-agnostic version of CLAUDE.md (~3.5 KB)
├── GEMINI.md                    # Same instructions adapted to Gemini CLI conventions
├── README.md                    # Human-facing project overview (premise, structure, timeline)
├── START.md                     # Session start/target end timestamps (time-boxing a work session)
├── TIME.md                      # Append-only run log (research_runner.py start/end times)
├── COUNTER.txt                  # "5" — count of self-review iterations completed
├── PUBLICATION_REVIEW_COUNTER.txt # "5" — count of publication-review rounds completed
├── KDP.md                       # Complete KDP publishing metadata playbook (see §7)
├── pyproject.toml               # uv project; deps for epub converter, playwright, cairosvg
├── .python-version              # 3.13
├── .claude/agents/              # 27 subagent definitions (write/review/research roles, see §8)
├── docs/                        # Style guides, writing process, citation standards
│   ├── STYLE.md                 # Primary style guide (banned words, coffee test, checklists)
│   ├── STYLE-AI-TELLS.md        # AI-pattern avoidance (burstiness, "As X, Y", repetitive openers)
│   ├── STYLE-CRAFT.md           # Narrative technique (Tracy Kidder model, sensory detail)
│   ├── STYLE-REFERENCE.md       # DO/DON'T before-after examples
│   ├── WRITING-PROCESS.md       # 7-phase workflow with agent assignments (828 lines)
│   ├── sources.md               # 4-tier source hierarchy + citation standards
│   ├── cite-check.md            # Bibliography verification protocol (Playwright-only)
│   ├── GLOSSARY.md / glossary-tools.md / REPETITION-AUDIT.md
│   ├── editorial-review-recommendations.md / fix-abridged-copy.md
│   ├── support/                 # Per-chapter citation worksheets (ch-00..ch-14-citations.md)
│   └── edition-2/               # Backlog of topics for a second edition
├── notes/                       # Planning: book-plan, structure, title decision, heading analysis,
│                                #   fictional/composite-character registry, glossary-terms.csv,
│                                #   summary/ (per-chapter must-keep beats used by the abridgement)
├── outline/                     # One markdown outline per chapter (00-prologue..14-epilogue)
├── research/                    # Per-chapter research folders (ch-00..ch-13) + _shared/, _web/,
│                                #   _wiki-content/, _data-analysis/, saline-township-dossier/,
│                                #   deep_dives/, random_fact_checks/, state-policy/, state-power/
├── latex/                       # FULL EDITION print production (see §3)
│   ├── main.tex, Makefile, .latexmkrc
│   ├── preamble/ {packages,colors,styling,commands}.tex
│   ├── front-matter/ {half-title,title,copyright,dedication,author-note,toc}.tex + cover/
│   ├── chapters/ 00-prologue..14-epilogue.tex
│   ├── back-matter/ {bibliography,glossary-entries,notes}.tex + isbn-barcode.{pdf,png}
│   ├── bib/ refs-{datacenter,entities,examples,geography,policy,power-grid}.bib
│   ├── figures/ TikZ figure sources + rendered PDFs/PNGs + cover-network SVG
│   ├── scripts/ update_cover_vars.py, generate_isbn_barcode.py, cover/
│   ├── kdp-cover.tex, cover-standalone.tex, back-cover-standalone.tex
│   └── (built artifacts: main-interior.pdf, kdp-cover.pdf, lulu-*.pdf, preview PDFs)
├── epub/                        # FULL EPUB pipeline (see §4)
│   ├── converter/               # Custom Python LaTeX→XHTML→EPUB package (~5,800 lines)
│   ├── templates/               # content.opf (metadata template), stylesheet.css, cover.xhtml,
│   │                            #   fonts/ (Libertinus OTF), fonts-backup/ (IBM Plex), images/
│   ├── scripts/                 # package_epub.py + 4 QA shell scripts
│   ├── META-INF/container.xml
│   └── qa-reports/              # epubcheck/ACE/metadata/link reports from `make epub-qa`
├── epub-abridged/               # Essential Edition EPUB: hand-maintained XHTML templates,
│                                #   own content.opf (own ISBN), make_kindle_cover.py (1.6:1 pad)
├── latex-abridged/              # Essential Edition print: own main.tex/Makefile/preamble copies,
│                                #   chapters converted from audiobook markdown, KDP.md, README.md,
│                                #   ACCESSIBILITY-TODO.md, figures -> ../latex/figures (symlink)
├── abridged-audio-book/         # 17 narrator scripts 00-title..16-epilogue + README.md (runtime
│                                #   math, formatting conventions) + PLAN.md (per-section targets)
├── scripts/                     # Project-wide utilities (see §6)
├── review/                      # Round-1 consolidated self-review reports (fact/style/accessibility…)
├── reviews/02/                  # Round-2 persona reviews (NYT/NYRB/WSJ/New Yorker + synthesis)
├── review-diary/                # Per-iteration edit logs (iteration-01..05, span-sampling diaries)
├── publication-reviews/         # 5-round scored persona review loop + FINAL_SUMMARY.md
├── release/v1.0/                # Frozen upload artifacts
├── published/                   # Final "as published" PDFs
└── Saline...ConsentJudgment.pdf/.txt  # Primary-source court document kept at repo root
```

---

## 3. LaTeX Pipeline (full edition, `latex/`)

### 3.1 Document class and structure

`latex/main.tex`:

```latex
\documentclass[11pt,twoside,openright]{book}

% Load preamble files
\input{preamble/packages}
\input{preamble/colors}
\input{preamble/styling}
\input{preamble/commands}

% Bibliography setup (modular topic-based files)
\addbibresource{bib/refs-datacenter.bib}
\addbibresource{bib/refs-entities.bib}
\addbibresource{bib/refs-examples.bib}
\addbibresource{bib/refs-geography.bib}
\addbibresource{bib/refs-policy.bib}
\addbibresource{bib/refs-power-grid.bib}
```

Front matter: `\frontmatter` → half-title → title → copyright → dedication → author-note → TOC. Main matter: `\mainmatter` → chapters input in DAG order with Part comments (no `\part` pages used). Back matter: `\backmatter` → bibliography only (acknowledgments/glossary/notes present but commented out).

### 3.2 Page geometry / trim size

`latex/preamble/packages.tex` — 6×9 US Trade, no interior bleed:

```latex
\usepackage[
    paperwidth=6in,
    paperheight=9in,
    inner=0.9in,        % Gutter margin (binding side)
    outer=0.625in,      % Outside margin
    top=0.75in,         % Top margin
    bottom=0.875in,     % Bottom margin (larger for visual balance)
    includehead,
    includefoot
]{geometry}
```

### 3.3 Fonts (exact setup)

XeLaTeX with Libertinus, engine-conditional fallback:

```latex
\usepackage{iftex}
...
\ifxetex
    % XeLaTeX: use fontspec directly
    \usepackage{fontspec}
    \usepackage{libertinus}
    \usepackage{libertinust1math}

    % Monospace: Latin Modern Mono (Libertinus Mono not available as system font)
    \setmonofont{Latin Modern Mono}[Scale=MatchLowercase]
\else\ifluatex
    \usepackage{fontspec}
    \usepackage{libertinus}
    \usepackage{libertinust1math}
    \setmonofont{Latin Modern Mono}[Scale=MatchLowercase]
\else
    % pdfLaTeX fallback: use traditional encoding
    \usepackage[utf8]{inputenc}
    \usepackage[T1]{fontenc}
    \usepackage{libertinus}
    \usepackage{libertinust1math}
\fi\fi

% Improved micro-typography
% nopatch=footnote avoids "Unable to apply patch `footnote'" warning
\usepackage[nopatch=footnote]{microtype}
```

Cover documents use a different face — `\setmainfont{Linux Libertine O}` (system font) in `kdp-cover.tex` and `cover-standalone.tex`.

### 3.4 Body typography

```latex
\usepackage{setspace}
\setstretch{1.1}  % Slight increase for readability

\setlength{\parindent}{1.5em}
\setlength{\parskip}{0pt}

\widowpenalty=10000
\clubpenalty=10000

\setlength{\emergencystretch}{2em}
\tolerance=1000
```

Plus: `babel` (english), `csquotes`, `graphicx`/`float`/`wrapfig`/`subcaption`, TikZ (`calc`, `positioning`), `booktabs`/`longtable`/`tabularx`, `enumitem`, `xcolor`, `epigraph` (width `0.75\textwidth`, no rule), `lettrine` for drop caps, `multicol` (two-column bibliography), `glossaries` loaded before hyperref with `automake=immediate` and `nohypertypes={main}`.

### 3.5 Chapter/section title styling

`latex/preamble/styling.tex` — right-aligned two-line chapter heads with spelled-out numbers:

```latex
\titleformat{\chapter}[display]
    {\raggedleft\normalfont}                          % Right-align the block
    {\scshape\large CHAPTER \chapterword}             % CHAPTER ONE
    {0.5em}                                           % Vertical space between lines
    {\huge\bfseries\color{chaptercolor}}              % Title formatting

\titlespacing*{\chapter}{0pt}{50pt}{40pt}

\titleformat{\section}
    {\normalfont\large\bfseries\scshape\color{bookblue}}
    {\thesection}{1em}{}

\titleformat{\subsection}
    {\normalfont\normalsize\bfseries\itshape}
    {\thesubsection}{1em}{}
```

The word-number counter (`packages.tex`, defined manually because `fmtcount` conflicts with `titlesec`):

```latex
\makeatletter
\newcommand{\chapterword}{%
    \ifcase\value{chapter}\or ONE\or TWO\or THREE\or FOUR\or FIVE\or SIX%
    \or SEVEN\or EIGHT\or NINE\or TEN\or ELEVEN\or TWELVE\or THIRTEEN\fi
}
\makeatother
```

Matching unnumbered variant for Prologue/Epilogue (`commands.tex`):

```latex
% Usage: \unnumberedchapter{PROLOGUE}{The Token}
\newcommand{\unnumberedchapter}[2]{%
    \clearpage
    \thispagestyle{plain}
    \vspace*{50pt}%
    {\raggedleft
        {\scshape\large\MakeUppercase{#1}}\par
        \vspace{0.5em}%
        {\huge\bfseries\color{chaptercolor}#2}\par
    }%
    \vspace{40pt}%
    \addcontentsline{toc}{chapter}{#1: #2}%
    \markboth{#1}{#2}%
}
```

TOC: `titletoc` with `\setcounter{tocdepth}{0}` (chapters only) and dot leaders:

```latex
\titlecontents{chapter}
    [1.5em]
    {\addvspace{0.25em}}
    {\contentslabel{1.5em}}
    {\hspace*{-1.5em}}
    {\titlerule*[0.5pc]{.}\contentspage}
    []
```

Drop caps (lettrine) tuned to 2 lines, colored:

```latex
\renewcommand{\LettrineFontHook}{\color{chaptercolor}}
\setcounter{DefaultLines}{2}
```

Blank verso pages made truly blank via redefined `\cleardoublepage` with `\thispagestyle{empty}`.

### 3.6 Headers/footers

`fancyhdr`, two named page styles:

```latex
\fancypagestyle{plain}{%
    \fancyhf{}
    \fancyfoot[C]{\thepage}
    \renewcommand{\headrulewidth}{0pt}
    \renewcommand{\footrulewidth}{0pt}
}

\fancypagestyle{body}{%
    \fancyhf{}
    \fancyhead[LE]{\small\textit{\leftmark}}      % Chapter name on left pages
    \fancyhead[RO]{\small\textit{\rightmark}}     % Section name on right pages
    \fancyfoot[LE,RO]{\thepage}                   % Page numbers on outer edges
    \renewcommand{\headrulewidth}{0.4pt}
    \renewcommand{\footrulewidth}{0pt}
}
```

### 3.7 hyperref + bibliography

```latex
\usepackage{hyperref}
\hypersetup{
    colorlinks=true,
    linkcolor=bookblue,
    citecolor=bookblue,
    urlcolor=bookblue,
    pdfauthor={Michael Bommarito},
    pdftitle={This Is Server Country},
    pdfsubject={AI Data Center Infrastructure},
    pdfkeywords={data centers, AI, infrastructure, power grid, rural America}
}
```

Note `bookblue` is RGB(28,36,42) — near-black, so "colored" links are print-safe. There is **no separate print vs digital PDF variant for link color**; the same interior serves both (the `kdp-interior` target passes `\def\NoCovers{1}`, a hook for suppressing embedded covers, though current `main.tex` contains no cover pages anyway).

Biblatex with superscript numeric citations (a signature choice — reads like endnote markers):

```latex
\usepackage[
    backend=biber,
    style=numeric-comp,         % Numeric citations, compressed ranges [1-3]
    sorting=none,               % Citations appear in order of first use
    maxbibnames=3,
    minbibnames=1,
    doi=false,
    isbn=false,
    url=false,                  % URLs clutter print; sources verifiable by title
    eprint=false
]{biblatex}

% Make citations superscript without brackets (like ¹²³)
\DeclareCiteCommand{\cite}[\mkbibsuperscript]
  {\usebibmacro{cite:init}%
   \let\multicitedelim=\supercitedelim
   \iffieldundef{prenote}
     {}
     {\BibliographyWarning{}%
      \usebibmacro{prenote}}}
  {\usebibmacro{citeindex}%
   \usebibmacro{cite:comp}}
  {}
  {\usebibmacro{cite:dump}}

\newcommand{\scite}[1]{\cite{#1}}

% Suppress fields that clutter print bibliography
\AtEveryBibitem{%
    \clearfield{note}\clearfield{url}\clearfield{urldate}%
    \clearfield{urlyear}\clearfield{urlmonth}\clearfield{urlday}%
    \clearfield{organization}\clearfield{pagetotal}\clearfield{howpublished}%
}
```

Bibliography rendered compact two-column (`latex/back-matter/bibliography.tex`):

```latex
\begingroup
\footnotesize
\setlength{\bibitemsep}{0.15\baselineskip}
\setlength{\biblabelsep}{0.3em}
\setlength{\bibhang}{1em}
\setlength{\columnsep}{1.5em}
\renewcommand*{\bibfont}{\footnotesize}
\begin{multicols}{2}
\raggedright
\printbibliography[heading=none]
\end{multicols}
\endgroup
```

### 3.8 Custom commands & environments (`latex/preamble/commands.tex`)

- Unit macros with `xspace`: `\kW \MW \GW \kWh ... \TB \PB \GPU`.
- Entity small-caps macros: `\Microsoft`, `\OpenAI`, `\NVIDIA`, etc.
- `tcolorbox` callouts: `sidebar` (titled, breakable, bookblue frame), `keyfact` (amber left-rule), `definition`, plus `bythenumbers` environment wrapping `keyfact`.
- `\scenebreak` — centered thin 3em rule for in-section scene transitions.
- Draft markers `\TODO{}`, `\NOTE{}`, `\VERIFY{}` in semantic colors.
- Cross-ref sugar `\chapref \figref \tabref \secref`.

### 3.9 Colors (`latex/preamble/colors.tex`)

```latex
\definecolor{bookblue}{RGB}{28, 36, 42}     % very dark slate (primary accent)
\definecolor{bookamber}{RGB}{191, 144, 64}  % warm amber (secondary)
\definecolor{bookrust}{RGB}{166, 94, 72}    % rust (tertiary)
\definecolor{chaptercolor}{RGB}{28, 36, 42}
```

Plus neutral grays, sequential/categorical dataviz palettes, semantic colors, box colors.

### 3.10 Front matter files

- `half-title.tex`: `\vspace*{0.3\textheight}` + `{\Huge\itshape Title}` centered, empty pagestyle.
- `title.tex`: hand-kerned tracked small caps at `\fontsize{28}{34}`, italic subtitle at 14pt in `black!70`, TikZ decorative rule with center dot, small-caps author, "First Edition / 2026" footer. Copyright is deliberately placed on title verso (`% No \cleardoublepage here`).
- `copyright.tex`: bottom-anchored `\footnotesize` block (rights, disclaimer, websites, both ISBNs) **plus a `\tiny` Publisher's Cataloging-in-Publication (PCIP) data block** following LoC CIP format with LCSH subjects and LCC/DDC classification — a professional touch worth templating.
- `toc.tex`: wraps `\tableofcontents` in a group with tightened `\titlespacing*{\chapter}`.

### 3.11 latexmk configuration (`latex/.latexmkrc`)

```perl
$pdf_mode = 5;                          # XeLaTeX
$xelatex = 'xelatex -interaction=nonstopmode -shell-escape %O %S';
$biber = 'biber %O %S';
$bibtex_use = 2;
add_cus_dep('glo', 'gls', 0, 'makeglossaries');
add_cus_dep('acn', 'acr', 0, 'makeglossaries');
sub makeglossaries { ... system "makeglossaries" ... }
$clean_ext .= ' %R.glo %R.gls %R.glg %R.acn %R.acr %R.alg %R.ist';
$clean_ext .= ' %R.run.xml %R.bcf %R.bbl';
$clean_ext .= ' %R.xdv';
$max_repeat = 7;                        # allow glossaries + bib + refs reruns
```

### 3.12 KDP/Lulu print specifics (covers, bleed, spine)

**Interior:** no bleed; gutter handled via `inner=0.9in`. KDP interior built with a distinct jobname so covers never leak in:

```make
$(INTERIOR).pdf: ...
	$(LATEX) -interaction=nonstopmode -jobname=$(INTERIOR) "\def\NoCovers{1}\input{$(MAIN).tex}"
	$(BIBER) $(INTERIOR)
	$(LATEX) ... (x2 more passes)
```

**Wrap cover:** `latex/kdp-cover.tex` is a single `article` page sized to the full wrap `[Bleed][Back 6"][Spine][Front 6"][Bleed]`, all art drawn in one `tikzpicture[remember picture, overlay]` (hence 3 compile passes). One template serves three products via `\def` switches:

```latex
\ifdefined\LuluHardcover
    \input{front-matter/cover/lulu-hardcover-cover-vars}
\else\ifdefined\LuluCover
    \input{front-matter/cover/lulu-paperback-cover-vars}
\else
    \input{front-matter/cover/kdp-cover-vars}
\fi\fi

\usepackage[paperwidth=\CoverWidth, paperheight=\CoverHeight, margin=0pt]{geometry}
```

**Cover dimension generation:** `latex/scripts/update_cover_vars.py` (stdlib-only PEP 723 script) reads the interior page count via `pdfinfo`/`mutool` and emits a `.tex` vars file. Spine formulas encoded:
- KDP paperback: `spine = pages * 0.002252 + 0.06` (white paper) or `* 0.0025` (cream)
- Lulu paperback: `pages * 0.0025` (standard) or `* 0.002252` (economy)
- Lulu hardcover: 26-row lookup table from Lulu's Book Creation Guide (24–799 pages)
- Bleed: `PAPERBACK_BLEED = 0.125`, `HARDCOVER_BLEED = 0.875` (0.75" board wrap + 0.125" bleed)

Generated vars file (`latex/front-matter/cover/kdp-cover-vars.tex`, 409-page build):

```latex
\newlength{\CoverTrimWidth}   \setlength{\CoverTrimWidth}{6.000in}
\newlength{\CoverTrimHeight}  \setlength{\CoverTrimHeight}{9.000in}
\newlength{\CoverBleed}       \setlength{\CoverBleed}{0.125in}
\newlength{\CoverSpineWidth}  \setlength{\CoverSpineWidth}{0.981068in}
\newlength{\CoverWidth}       \setlength{\CoverWidth}{13.231068in}
\newlength{\CoverHeight}      \setlength{\CoverHeight}{9.2500in}
\newcommand{\CoverPageCount}{409}
```

**Post-processing:** every wrap cover is flattened to PDF/X-1a-ish output with Ghostscript (removes transparency KDP rejects):

```make
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.3 -dNOPAUSE -dBATCH -dSAFER \
    -dPDFSETTINGS=/prepress -sOutputFile=... "$(KDP_COVER).pdf"
```

**ISBN barcode:** `latex/scripts/generate_isbn_barcode.py` (python-barcode + Pillow, PEP 723) renders EAN-13 with custom text into `back-matter/isbn-barcode.pdf`, placed on the back cover by TikZ.

**Ebook cover:** `cover-standalone.tex` renders the front cover alone at 6×9; `make cover-image` converts to 300-dpi JPEG via `pdftoppm` for the EPUB. `epub-abridged/make_kindle_cover.py` pads the JPEG canvas to Amazon's 1.6:1 minimum aspect ratio using the cover background color `(252, 251, 248)`.

**Digital preview assemblies:** `make full` (front cover + interior via `pdfunite`) and `make preview` (front + interior + back).

### 3.13 Build targets summary (`latex/Makefile`, 769 lines)

| Target | Purpose |
|---|---|
| `all` / `quick` / `rebuild` / `watch` | latexmk full build / single pass / clean rebuild / `-pvc` |
| `validate` | pdfinfo page-size check (432×648 pt) + grep counts of undefined refs, over/underfull boxes, warnings |
| `wordcount` / `pagecount` | pdftotext wc / pdfinfo |
| `kdp`, `kdp-interior`, `kdp-cover`, `kdp-cover-vars`, `kdp-cover-check` | KDP print pipeline |
| `lulu-paperback`, `lulu-hardcover`, `lulu-all` (+ `-vars`, `-cover`, `-check` each) | Lulu pipeline |
| `epub`, `epub-quick`, `epub-bib` | EPUB via converter (`epub-bib` cats the 6 modular .bib files) |
| `epub-qa` = `epub-validate` + `epub-accessibility` + `epub-metadata` + `epub-images` + `epub-links` | full QA with reports in `epub/qa-reports/` |
| `epub-check`, `epub-ci`, `install-epub-tools` | quick check / CI-fail mode / installs epubcheck 5.3.0 + DAISY ACE |
| `kindle` | Calibre `ebook-convert` → AZW3 (`kindle_pw3` profile) + MOBI, with `--embed-all-fonts --subset-embedded-fonts --smarten-punctuation --keep-ligatures --minimum-line-height 120 --no-inline-toc` |
| `release`, `pdf-release`, `epub-release`, `kdp-release`, `lulu-release`, `all-formats` | timestamped copies into `../build/{pdf,epub,kdp,lulu}/` named "`$(BOOK_TITLE) - $(TIMESTAMP) - ROLE`" |
| `isbn-barcode`, `cover-standalone`, `back-cover-standalone`, `cover-image`, `full`, `preview` | cover tooling |
| `clean`, `cleanall`, `epub-clean`, `cover-clean` | cleanup |

---

## 4. EPUB Pipeline (`epub/`)

### 4.1 Architecture — custom converter, not pandoc

A bespoke Python package `epub/converter/` (~5,800 lines) converts the *same LaTeX chapter sources* to EPUB 3. Invocation (from `latex/Makefile`):

```make
UV_RUN = uv run --with TexSoup,lxml,typer,rich

epub: cover-image epub-bib
	cd $(EPUB_DIR) && $(UV_RUN) python -m converter book ../latex/chapters -o $(EPUB_BUILD_DIR) \
		--bib $(EPUB_BUILD_DIR)/combined-refs.bib \
		--front-matter ../latex/front-matter \
		--back-matter ../latex/back-matter
	cd $(EPUB_DIR) && $(UV_RUN) python -m converter epub $(EPUB_BUILD_DIR) -o $(EPUB_OUTPUT) -t templates
```

Modules:
- `parser.py` — TexSoup-based AST helpers (`is_macro`, `get_env_content`, …).
- `document.py` — `Book`/`Chapter` model; first pass collects `\label` cross-refs and parses .bib files (own minimal BibTeX parser; accepts a directory of .bib files).
- `renderer.py` — walks the AST, dispatches to handlers, builds lxml DOM directly; handlers return typed `BlockElement`/`InlineElement` results to manage paragraph wrapping; XHTML+epub namespaces.
- `handlers/` — `macros.py`, `environments.py`, `figures.py`, `math.py`, `references.py` (generic) plus **book-specific** `datacenter_macros.py`/`datacenter_environments.py` and **inherited** `rfc_macros.py`/`rfc_environments.py` (789/501 lines carried over from a previous book, "history-through-rfc-book").
- `cli.py` (1,115 lines, typer) — `convert` (single file), `book` (whole book: chapters + front/back matter), `epub` (package). Front matter converted via a filename map (`half-title→half-title.xhtml`, `title→title-page.xhtml`, …) with correct `epub:type` values (`halftitlepage`, `titlepage`, `copyright-page`, `dedication`, `preface`); LaTeX-only commands and TikZ are regex-stripped for simple pages. `toc.tex` is skipped — nav.xhtml is generated. **`generate_content_opf()` builds the OPF manifest/spine dynamically from actual output files**, pulling metadata from `templates/content.opf` and auto-adding font entries per file found in `fonts/`.

### 4.2 EPUB structure & metadata

- `META-INF/container.xml` → `OEBPS/content.opf`.
- Metadata template `epub/templates/content.opf` (EPUB 3.0, `unique-identifier="bookid"`):

```xml
<dc:identifier id="bookid">urn:isbn:PLACEHOLDER</dc:identifier>
<dc:title>This Is Server Country: AI, Power, and Politics</dc:title>
<dc:creator>Michael J Bommarito II</dc:creator>
<dc:language>en-US</dc:language>
<dc:publisher>Michael J Bommarito II</dc:publisher>
<dc:date>2026</dc:date>
<dc:subject>Data Centers</dc:subject> ... (5 subjects)
<dc:rights>Copyright 2026 Michael J Bommarito II. All rights reserved.</dc:rights>
<meta property="dcterms:modified">2026-01-17T00:00:00Z</meta>
...
<item id="cover-image" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>
...
<guide>
  <reference type="cover" .../><reference type="toc" .../>
  <reference type="text" title="Beginning" href="prologue.xhtml"/>
  <reference type="bibliography" href="references.xhtml"/>
</guide>
```

- Spine: cover (`linear="no"`) → half-title → title → copyright → dedication → toc-page → author-note → prologue → part/chapter files → epilogue → back matter.
- Packaging: `epub/scripts/package_epub.py` — zips with `mimetype` first and STORED (uncompressed), then META-INF, then OEBPS. (The `converter epub` subcommand does the same job in-pipeline.)

### 4.3 Fonts and CSS

Embedded fonts are **Libertinus OTFs to match print** (`epub/templates/fonts/`); IBM Plex was the earlier choice and survives in `fonts-backup/` and the stale template manifest. The shipped EPUB embeds Libertinus (verified in `this-is-server-country.epub`).

Key rules from `epub/templates/stylesheet.css` (1,644 lines — includes legacy RFC-book classes):

```css
@font-face {
  font-family: "Libertinus Serif";
  font-style: normal;  font-weight: 400;
  src: url("fonts/LibertinusSerif-Regular.otf");
}
/* + Italic/Bold/BoldItalic, Libertinus Sans x3, Libertinus Mono x1 */

body {
  font-family: "Libertinus Serif", Georgia, "Times New Roman", serif;
  font-size: 1em;  line-height: 1.6;  color: #1f2937;  padding: 1em;
}

/* Section headings: bold, small-caps, bookblue color (matches LaTeX) */
h2 { font-size: 1.3em; font-weight: bold; font-variant: small-caps;
     color: #1c242a; letter-spacing: 0.02em; }
h3 { font-size: 1.15em; font-weight: bold; font-style: italic; }

p { margin: 0 0 1em 0; text-align: justify; hyphens: auto; -webkit-hyphens: auto; }

/* Chapter headings: RIGHT-ALIGNED, two-line format (matches LaTeX \raggedleft) */
h1.chapter-title { text-align: right; color: #1c242a;
                   margin-top: 3em; page-break-before: always; }
.chapter-label { display: block; font-size: 0.9em; font-variant: small-caps;
                 letter-spacing: 0.1em; }
.chapter-title-text { display: block; font-size: 1.8em; font-weight: bold; }

/* Scene break: matches LaTeX \scenebreak */
.scene-break { border: none; border-top: 1px solid #646464;
               width: 3em; margin: 1.5em auto; }

/* Key Fact box - bookamber accent (matches LaTeX keyfact tcolorbox) */
.keyfact { border-left: 4px solid #bf9040; background-color: #f5f5f5; }

/* Drop cap: chaptercolor (matches LaTeX lettrine) */
.dropcap { float: left; font-size: 3.5em; line-height: 0.8;
           padding-right: 0.1em; font-weight: bold; color: #1c242a; }

.citation { font-size: 0.75em; vertical-align: super; }
.reference-entry { margin-bottom: 0.75em; padding-left: 2em;
                   text-indent: -2em; font-size: 0.9em; }
```

Deliberate **Kindle compatibility** engineering documented in comments: avoid flexbox on the title page ("Kindle-compatible: avoid flexbox, use text-align + inline-block"), avoid `rgba()` ("Kindle-safe"), plus `@media (prefers-color-scheme: dark)` night-mode overrides and a `@media (max-width: 600px)` block.

### 4.4 Validation (make epub-qa)

- **epubcheck** (v5.3.0, checks `/usr/share/java/epubcheck.jar` then `~/tools/`), JSON + log into `epub/qa-reports/`.
- **DAISY ACE** accessibility audit (runs under `xvfb-run` when headless; suggests https://ace.daisy.org/ otherwise).
- `epub/scripts/validate_metadata.sh` — OPF field checks; `check_images.sh` — alt-text presence; `validate_links.sh` — internal href targets; `generate_summary.sh` — roll-up.
- `epub-ci` variant exits nonzero on error for CI.

### 4.5 `epub-abridged/` differences

- **Not converter-generated**: hand-maintained XHTML per chapter in `epub-abridged/templates/` (14 chapter files with different slugs/count than the full book, e.g. `ch11-what-could-change.xhtml`, `ch12-our-future.xhtml`, single combined `references.xhtml`).
- Own `content.opf` with its **own ISBN** `urn:isbn:979-8-9943457-4-0`, title "This Is Server Country: Essential Edition", 8 subjects.
- Built via `latex-abridged/Makefile`, which points `EPUB_DIR = ../epub-abridged` but reuses `CONVERTER_DIR = ../epub/converter` for packaging.
- `make_kindle_cover.py` pads cover.jpg 1800×2700 → 1800×2880 for the 1.6:1 Kindle requirement.

---

## 5. Audiobook Pipeline (`abridged-audio-book/`)

**No TTS tooling** — this is a *human-narrator* script package (17 Markdown files, `00-title.md` … `16-epilogue-the-token-revisited.md`). A gitignored `tts-test/` suggests TTS experiments were tried and discarded. The reusable assets are the **process documents**:

- **`README.md`** — runtime math and formatting conventions:
  - Source total 98,714 words → targets: 4 h @150 wpm = 36k words (36.5%) … 5 h @165 wpm = 49.5k (50.1%); baseline **4.5 h @ 155 wpm = 41,850 words = 42.4% ratio**.
  - QA bands: total 36k–50k hard; per-section targets ±10–15%.
  - Narrator conventions: blank line = beat/breath; 1–4 sentence paragraphs; `### NOTE (Narrator):`, `PRONUNCIATION:`, `PAUSE:` blocks; spoken section headings `## [SECTION] Title` (3–5 per chapter, read aloud with 2-beat pause); `---` scene breaks = unannounced pause; decimals read "one point four"; expand symbols ("$7B" → "seven billion dollars").
  - Word-count/runtime one-liners using `wc`/`awk` (documented workaround for a `uv` cache-permission failure).
- **`PLAN.md`** — per-section source mapping (summary in `notes/summary/` first, then the LaTeX chapter), per-section word targets, and abridgement rules: keep hooks/scenes/anchor numbers/transitions; cut lists (→ 1 sentence + 2–3 examples), stat runs (→ 1–2 numbers + meaning), figure-like content. **"Numbers rule": >~3 numeric facts in a paragraph ⇒ rewrite.**

Essential Edition conversion back to LaTeX (per `latex-abridged/README.md`): strip narrator blocks/`PAUSE:`, `*x*`→`\textit{}`, `**x**`→`\textbf{}`, `---`→`\scenesep`, add `\chapter{}`.

---

## 6. Build Automation & Scripts

### 6.1 `pyproject.toml`

```toml
[project]
name = "datacenter-2026-book"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "cairocffi>=1.7.1", "cairosvg>=2.8.2", "cffi>=2.0.0",
    "cssselect2>=0.8.0", "defusedxml>=0.7.1", "lxml>=6.0.2",
    "pillow>=12.1.0", "playwright>=1.57.0", "pycparser>=2.23",
    "texsoup>=0.3.1", "tinycss2>=1.5.1", "typer>=0.21.1",
    "webencodings>=0.5.1",
]
```

Notable: most standalone scripts are **PEP 723 self-contained** (`# /// script` headers with their own deps: `pylatexenc`, `nltk`, `python-barcode`, `bibtexparser`, `trafilatura`), so `uv run scripts/foo.py` works regardless of project env. The Makefile uses `uv run --with TexSoup,lxml,typer,rich` for the converter.

### 6.2 `scripts/` (project root)

| Script | Purpose |
|---|---|
| `book_stats.py` (954) | LaTeX stats: word/sentence/paragraph counts, environments, citations, per-chapter breakdown, page estimate at 275 words/6×9 page. Regex fallback if deps absent. `--json/--markdown/--verbose`. (Docstring still says "Rough Consensus" — inherited.) |
| `verify_url.py` (206) | **Playwright Firefox fetch** of a URL with realistic viewport/UA/locale; prints TITLE/byline/date (+trafilatura extraction) for citation verification. The mandated tool in CLAUDE.md. |
| `verify_citation.py` (374) | Citation-vs-page comparison helper. |
| `cite_verify_tracker.py` (346) | Tracks verification via an inline `verified = {2026-01-22}` / `{TODO}` / `{... FIXME}` field in bib entries; `--progress`, `--mark-verified KEY`, `--list-unverified`. |
| `split_bibliography.py` (267) | Splits monolithic refs.bib into the 6 topic files by keyword patterns. |
| `term_tools.py` (435) | Term usage + glossary/index candidate reports from `notes/glossary-terms.csv` (+ stopword list). |
| `sample_latex_spans.py` (170) | Randomly samples 3–5-paragraph spans from chapters for spot QA (fuels the span-sampling review diaries). |
| `research_runner.py` (454) | Time-boxed autonomous research loop: samples wiki pages as seeds, generates queries, hits Bing/Google-News-RSS/OpenAlex, fetches results, prefers .gov, writes into `research/`, and logs start/end lines into `TIME.md`. Flags: `--duration 15m --samples-per-cycle --queries-per-seed --openalex ...` |
| `research_state_policy.py` / `research_state_power.py` | Topic-focused research collectors into `research/state-policy/`, `research/state-power/`. |
| `entity_extractor.py`, `data_exporter.py` | Entity extraction from chapters; data export from the external project database. |
| `wiki_to_research.py` (58) | Extracts relevant wiki sections into chapter research folders. |
| `latex/scripts/update_cover_vars.py`, `latex/scripts/generate_isbn_barcode.py` | See §3.12. |
| `epub/scripts/*` | See §4.4. |

### 6.3 Timekeeping oddities

`START.md` (session start + 2-hour target end) and `TIME.md` (appended timestamps, also written by `research_runner.py`) implement crude session time-boxing for autonomous runs.

---

## 7. Metadata & Publishing (`KDP.md`, `release/`, `published/`)

`KDP.md` (root, 521 lines; snapshot also frozen in `release/v1.0/KDP.md`; a separate `latex-abridged/KDP.md` covers the Essential Edition) is a complete fill-in playbook:

- **Identity:** Title/subtitle; author "Michael J / Bommarito II"; author bio paragraph ready to paste; ISBNs print 979-8-9943457-3-3 / ebook 979-8-9943457-2-6.
- **AI disclosure:** "This book was written with AI assistance (Claude Code/Opus 4.5 for research, drafting, and revision, as disclosed in the Author's Note). Answer per KDP's definitions at publish time." Don't credit AI as Contributor.
- **Descriptions:** HTML description (~1,850 chars, only KDP-supported tags `<b> <br> <em> <h4>-<h6> <ul> <ol> <li>`), plain-text version for Bowker/ISBN registration, a ~265-char short description, a 67-char one-liner, and four marketing taglines.
- **Categories:** Bowker primary POLITICAL SCIENCE / secondary TECHNOLOGY (deliberate differentiation from COMPUTERS); BISAC picks POL044000, BUS070060, COM004000 (+2 alternates); 3 Amazon browse categories with rationale.
- **Keywords:** 7 slots ≤50 chars each with strategy notes (avoid words already in title/subtitle; target reader search problems), e.g. `data center electricity grid energy`, `chip war semiconductors geopolitics`, `utility rates electricity bills ratepayers`.
- **Print options:** 6×9, B&W on **white** paper (better for charts than cream), **no bleed**, matte cover; spine formula `pages × 0.002252" + 0.06" ≈ 0.92"` at 383 pp; "KDP print manuscripts should not include the full-wrap cover."
- **Kindle:** upload EPUB; cover 1.6:1 (e.g. 2560×1600); **DRM off** recommendation; KDP Select = decide (exclusivity warning).
- **Pricing (2026 comps table: Chip War, The Grid, Evicted, etc.):** Paperback **$24.99**, Kindle **$14.99**, Hardcover **$34.99**; launch-week promo $9.99–12.99 suggested.
- **Comparable-titles market analysis** in 3 tiers + "market gap" statement.
- **Post-publish playbook:** A+ Content, Author Central, request extra categories via KDP support, keyword review at 30–60 days.
- Ends with a **Quick Reference form-completion table** (every KDP field → value) and sources (KDP docs, Kindlepreneur, Reedsy, BISG).

**Cover creation:** documented in `latex/front-matter/cover/README.md` — concept (US as wave-perturbed network mesh, radial blue→copper gradient centered on Michigan, datacenter-intensity node weighting), generated as SVG (`figures/cover-network-source.svg`) → PDF via cairosvg (Makefile rule), composed in TikZ wrap-cover template with transmission-tower line art drawn in raw TikZ coordinates.

---

## 8. Style / Craft / AI-Tone Guides

### 8.1 The four-file style system (`docs/`)

1. **`STYLE.md`** (486 lines) — the core. Highlights:
   - **The Coffee Test**: "Write as if explaining to a curious friend over coffee… If it sounds like a corporate press release, an academic paper, or a TED talk, rewrite it."
   - Voice: "we" for shared analysis; third person for narrative scenes; "you" sparingly; **never "one"**.
   - Tense: present = current state; past = events; future/conditional = projections.
   - Sentences: 15–20 words average, **35-word hard max**, one idea each, vary length.
   - Punctuation hierarchy: commas → colons → semicolons → new sentences → em dashes (**max one per paragraph**) → parentheses (rare; abbreviations only).
   - Paragraphs: 3–7 sentences, Point-Evidence-Analysis.
   - **Banned words** (with replacements): `delve, leverage(v), utilize, harness, foster, elevate, streamline, robust, unlock, crucial, pivotal, paramount, landscape(metaphor), realm, tapestry, myriad, plethora, multifaceted, intricate, embark, illuminate, unveil, paradigm, ecosystem, game-changer, disruptive, revolutionary`.
   - **Banned phrases**: "It's important to note…", "Let's dive in", "Here's the thing", "At the end of the day", "Indeed/Furthermore/Moreover", hype terms, vague qualifiers.
   - Data rules: every number gets context ("1.4 gigawatts—enough to power a city of 800,000"), round for readability, cite everything.
   - Book-specific: Saline anchor transitions must be shown not announced; balance narrative/analysis; multiple perspectives without judgment; forward-looking closes.
   - Ends with a **pre-submission checklist** (13 items).
2. **`STYLE-AI-TELLS.md`** (105) — AI-pattern hunting: low burstiness fix (follow a 30-word sentence with a 5-word one), repetitive sentence openers ("This/The/It"), the **"As X, Y" overuse tell**, passive-voice default, parenthetical overuse; 5-item checklist ("Could you say this to a friend over coffee without feeling like a robot?").
3. **`STYLE-CRAFT.md`** (45) — narrative technique: the **Tracy Kidder model** (*The Soul of a New Machine*): people first, micro→macro, prose-as-camera; sensory detail lists (70 dB fans, 500 kV buzz); explain-complexity pattern **Analogy → Direct explanation → Implication**; chapter hooks.
4. **`STYLE-REFERENCE.md`** (53) — 5 before/after pairs (corporate speak, academic abstraction, monotone rhythm, data dumping, throat clearing).

### 8.2 Process docs

- **`WRITING-PROCESS.md`** (828) — 7 phases (Research → Planning → Drafting → Review → Revision → Polish → Verification), each with process steps, deliverable checklists, and an agent table. Contains the canonical **chapter outline template** (Overview / Dependencies / Opening Hook 1,000–1,500 w / Context / two Deep Dives / Stakeholder Perspectives / Implications / Saline Return / Transition / Figures / Key Sources) and **figure spec template**.
- **`sources.md`** (522) — 4-tier source hierarchy (Government/Regulatory → Company → Industry press → Major news → Academic) with per-tier caveats; required citation metadata (title, author, date, stable URL/DOI, access date, archive URL); rule: cite the wiki's original sources, never the wiki.
- **`cite-check.md`** (768) — verification protocol born of failure: an initial audit found **57% of sampled citations had errors** (wrong bylines most common). Rules: verification = Playwright fetch + field-by-field comparison; never WebFetch (403/451), never trust search snippets; a failure-modes table (false confirmation, wrong tool, partial verification, rushing) and workflow `bib entry → Playwright fetch → extract → compare → document`.
- **CLAUDE.md extras**: "Today's date / training cutoff" awareness block; **"CRITICAL: No Interviews Were Conducted"** section (composite characters are fictional, dialogue invented from documented sources; never imply interviews/anonymity) pointing at `front-matter/author-note.tex` for the methodology disclosure; prohibited content list; edition matrix; quick-reference commands.
- **AGENTS.md / GEMINI.md** — same content compressed for other agent harnesses (Gemini version maps to `google_web_search` / `delegate_to_agent` tool names).

### 8.3 Subagents (`.claude/agents/`, 27 files)

Frontmatter pattern: `name`, `description`, `tools: Read, Grep, Glob[, Write, Edit, WebSearch, WebFetch]`, `model: sonnet|opus`. Model assignment is deliberate: **opus for generative/judgment-heavy** (draft-from-outline, line-editor, content-expansion, repetition-elimination, citation-management, acquisitions-editor, technical-expert-reviewer, example-analogy-refinement, opening-closing-hooks), **sonnet for mechanical/review** (critical-review, fact-check, flow-improvement, structural-balance, style-guide-conformance, etc.).

Roster by phase: research (datacenter-research, policy-research, rfc-research*, security-incident-research*), planning (outline-iteration, visual-element-planning, structural-balance), drafting (draft-from-outline, narrative-scene-building, data-storytelling), review (critical-review with 7 selectable personas, accessibility-check, technical-expert-reviewer, acquisitions-editor, cross-reference-verification), revision (revision-from-feedback, citation-management), polish (style-guide-conformance, compression-tightening, content-expansion, flow-improvement, opening-closing-hooks, line-editor, paragraph-restructuring, repetition-elimination, example-analogy-refinement), verification (fact-check).

*Several agents (rfc-research, security-incident-research, critical-review body text mentioning "Trusted by Default") were **copied from prior book projects and never retargeted** — they still reference other books.

Key agent conventions worth templating (from `draft-from-outline.md`): mandatory "read STYLE docs before drafting" preamble, a quality-metrics table (words/sentence, paragraph length, burstiness, voice, anchor integration), banned-word list inline, and review agents that **give feedback but never edit** (edits belong to revision agents).

---

## 9. QA / Review Workflow

Four distinct review systems, run in sequence, with counters tracking iterations:

### 9.1 Self-review iterations (`COUNTER.txt` = 5, `review-diary/`)
Each iteration = full read-through + **grep audit of every banned word/phrase** with a triage table (literal "landscape" OK; "leverage" as noun OK; verb uses fixed), an explicit list of edits made (file, line, before→after, reason), acceptable-use rationales, and next-iteration goals. `span-sampling-*.md` diaries document random 3–5-paragraph sampling via `scripts/sample_latex_spans.py` to catch weaknesses linear reading misses ("vague hinge sentences", uncited comparative claims).

### 9.2 Consolidated agent review (`review/`)
One round of 5 parallel reports — general-reader, technical-accuracy (92/100), fact-check, style-conformance (32–40 banned-word hits), accessibility (grade 11–12 reading level) — synthesized into `CONSOLIDATED-REVISION-PLAN.md` with a 3-tier priority matrix (Critical corrections / Important improvements / Polish) broken down per chapter.

### 9.3 Publication-persona reviews (`reviews/02/`, `publication-reviews/`, `PUBLICATION_REVIEW_COUNTER.txt` = 5)
The standout process. Full-length fake reviews written **in the voice of NYT Book Review, New Yorker, NYRB, WSJ** (each ~1,500–2,800 words with a headline), then:
- `summary-and-actionable-feedback.md` extracts consensus strengths/weaknesses;
- 5 scored rounds (`publication-reviews/round-1..5/` + per-iteration synthesis + response docs);
- `FINAL_SUMMARY.md` tracks a score matrix per publication per round (7.67 → 8.47 average over 5 rounds), documents what was changed each round (named characters added, theory callbacks rewritten), identifies regressions and turning points (e.g., "theory inserted rather than integrated" flagged by all three personas in round 4), and distills lessons ("Concrete first, concept second"; the removal test: "Remove the theory—does the argument change?").

### 9.4 Automated/format QA
- `make validate` (page geometry, undefined refs, overfull boxes), `make epub-qa` (epubcheck + ACE + metadata/images/links scripts), `make epub-ci` for fail-fast.
- Citation QA: `cite_verify_tracker.py` progress tracking over inline `verified = {date}` bib fields + `verify_url.py` Playwright fetches + per-chapter worksheets in `docs/support/ch-XX-citations.md`.
- `notes/` holds one-off audits: heading-analysis, repetition-resolution prompt, composite-character/fictional-character registries (ethics tracking), name-change guide, title-decision record.

---

## 10. Verdict

### Best reusable pieces for a master template

1. **The whole `latex/` preamble family** (`packages/colors/styling/commands.tex` split + `.latexmkrc` + `main.tex` skeleton): 6×9 geometry with gutter, Libertinus/engine-conditional fonts, right-aligned two-line chapter heads with `\chapterword`, `\unnumberedchapter`, superscript `\scite` biblatex config, two-column footnotesize bibliography, fancyhdr styles, blank-verso handling, `tcolorbox` callouts, `\scenebreak`, draft markers. Parameterize title/author/ISBN/colors and it's a drop-in.
2. **The cover system**: `update_cover_vars.py` (KDP + Lulu paperback + Lulu hardcover spine math and bleed constants), single `kdp-cover.tex` template with `\ifdefined` platform switches, Ghostscript flattening step, `generate_isbn_barcode.py`, `cover-standalone → pdftoppm JPEG → make_kindle_cover.py 1.6:1 pad` chain. This is the hardest-won, most reusable machinery in the repo.
3. **The Makefile** as a whole: target taxonomy (build/validate/kdp/lulu/epub/epub-qa/kindle/release), timestamped `release` outputs, `install-epub-tools`, `validate` grep-based lint. Genericize `BOOK_TITLE` and paths.
4. **The EPUB converter package** (`epub/converter/`): already designed for reuse (generic handlers + per-book handler modules + dynamic OPF generation from a metadata template). Extract as a standalone tool; make the book-specific handler module pluggable and drop the RFC legacy modules.
5. **EPUB QA harness**: epubcheck + DAISY ACE + the four shell validators + qa-reports convention + CI mode.
6. **The style-guide stack**: STYLE.md (banned words/phrases + coffee test + checklist), STYLE-AI-TELLS.md (burstiness, openers, "As X, Y"), STYLE-CRAFT.md (Kidder model, analogy→explanation→implication), STYLE-REFERENCE.md (before/after pairs). These are book-agnostic with minor edits and are the single biggest quality lever for AI-authored prose.
7. **WRITING-PROCESS.md 7-phase workflow** + chapter outline template + the `.claude/agents/` roster pattern (opus-for-generation / sonnet-for-review split, review-agents-don't-edit rule, mandatory style-doc reads).
8. **Citation-verification protocol**: cite-check.md rules, `verify_url.py` (Playwright Firefox), `cite_verify_tracker.py` inline `verified={date}` bib fields, per-chapter citation worksheets, and the modular topic-based .bib layout (+ `split_bibliography.py`).
9. **The review-loop design**: counters + review-diary edit logs + grep-based banned-word audits + random span sampling + **scored multi-persona publication reviews across rounds with synthesis docs**. This loop demonstrably improved the manuscript and is fully generic.
10. **Multi-edition architecture**: full → audiobook scripts (with runtime math, per-section ratio targets, narrator conventions) → Essential print/ebook, each edition with its own ISBN and KDP.md. The abridgement rules (numbers rule, list compression) are reusable verbatim.
11. **KDP.md playbook structure** (form-field walkthrough, HTML + plain descriptions, BISAC/Bowker/keywords with rationale, pricing comps, post-publish checklist) — keep as a template with placeholders.
12. **Small touches**: PCIP/CIP data block on the copyright page; multi-agent instruction files (CLAUDE.md + AGENTS.md + GEMINI.md) kept in sync at different verbosity; PEP 723 self-contained scripts; date/cutoff-awareness header in CLAUDE.md; `book_stats.py` for progress tracking.

### Pitfalls / things to avoid

- **Copy-paste drift from prior books**: agents referencing "Trusted by Default", `book_stats.py` docstring saying "Rough Consensus", `package_epub.py` default output `rough-consensus.epub`, ~1,300 lines of RFC-book handlers and dozens of unused RFC CSS classes shipped in this book's converter/stylesheet. A master template must have a single source of truth and a rename/parametrization checklist.
- **Stale template metadata**: `epub/templates/content.opf` still lists IBM Plex fonts and `urn:isbn:PLACEHOLDER` while the shipped EPUB embeds Libertinus with a real ISBN (converter regenerates the manifest, but the template misleads). Keep metadata in one parameterized place.
- **Subtitle/title inconsistency**: "AI, Power, and Politics" vs "AI, Power, and the Remaking of Rural America" coexist across README, OPF, copyright, and KDP.md. Template should have one metadata file (YAML/TeX vars) that everything reads.
- **Duplicated preambles**: `latex-abridged/` copies (not symlinks) the preamble despite README claiming symlinks; fixes must be made twice. Template should share preamble via a common include path with per-edition override files.
- **Makefile sprawl**: 769 lines with legacy aliases and repeated 3-pass cover recipes; several near-duplicate lulu/kdp blocks could be pattern rules. Also `kdp-interior` passes `\def\NoCovers{1}` that nothing consumes anymore.
- **Root-directory clutter**: a 10 MB court-document PDF, built PDFs/`main.xdv` committed alongside source. Define `build/` and `sources/` conventions and gitignore artifacts from the start (the .gitignore here even has `latex/main.pdf` as a one-off exception).
- **Citation risk is real**: the 57% error rate happened *with* a style guide in place; the protocol (Playwright fetch + field-by-field compare + tracker fields) was added reactively. Bake it in from day one, including the "never trust search snippets" rule.
- **Hand-maintained abridged EPUB XHTML**: `epub-abridged/templates/` bypasses the converter, so fixes to shared prose require parallel edits. Prefer converting `latex-abridged/` chapters through the same converter.
- **Env quirks encoded in docs**: uv cache-permission workaround in the audiobook README, hardcoded absolute paths to the wiki/support data in CLAUDE.md/scripts. Template should use env vars/config for external data roots.
- **Review-score inflation risk**: self-administered persona scores (7.67→8.47) are motivating but not calibrated; keep the *process* (round synthesis, removal tests, regression detection) and treat numbers as directional only.
