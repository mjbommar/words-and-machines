# Research Report: complexity-book

Source: `/home/mjbommar/projects/personal/complexity-book`

## 1. Purpose & Status

Two books in one repo:

1. **Active: "The Math Inside the Machine: How Intelligence Emerges from Eleven Simple Operations"** (`pop-sci-book/`) — a ~335-page pop-science trade book explaining transformer AI through K-12 math (counting → tokenization, addition → residual connections, ... derivatives → backpropagation). Status per CLAUDE.md: Planning/Research/Drafting complete (14/14 chapters), revision phase next. It has been built end-to-end: dated release artifacts exist in `pop-sci-book/latex/` — `Math in the Machine - Draft 20260104 EBOOK.pdf / EPUB.epub / AZW3.azw3 / MOBI.mobi`, plus `kdp-cover.pdf` and `main-interior.pdf`. KDP metadata (ISBNs for print + ebook) is in `pop-sci-book/docs/KDP.md`.
2. **On hold: complexity-science textbook** — ~860-page undergraduate textbook (Peano axioms → NP-completeness), exists only as extensive planning material in `notes/`.

**Formats (the most multi-format of the three projects):** 6x9 print PDF, print-bleed PDF, KDP interior PDF + full-wrap cover PDF, large-font e-reader PDF (separate `main-ebook.tex` on `extbook` 14pt), EPUB (custom TexSoup-based converter), AZW3/MOBI via calibre.

## 2. Directory Layout

```
complexity-book/
├── CLAUDE.md                  # Master instructions: structure, agents, style, build commands
├── README.md                  # Textbook-era overview ("two projections" concept)
├── pyproject.toml / main.py   # uv project (main.py = hello-world stub); deps for figures/EPUB
├── .claude/agents/            # 14 writing sub-agent definitions (see §6)
│
├── pop-sci-book/              # ACTIVE BOOK
│   ├── README.md              # Book premise, K-12 arc, chapter table, specs, back-jacket blurb
│   ├── TODO.md, KDP.md, WRITING-PROCESS.md, FIGURES.md
│   ├── latex/
│   │   ├── main.tex           # Print master (6x9)
│   │   ├── main-ebook.tex     # E-reader variant (extbook, 14pt, oneside)
│   │   ├── main-interior.tex  # KDP interior (\NoCovers defined)
│   │   ├── kdp-cover.tex      # Full-wrap KDP cover (TikZ, computed spine)
│   │   ├── Makefile           # 580-line multi-format build system
│   │   ├── epub.cfg
│   │   ├── preamble/          # 11 modular files: packages, colors, tikz, boxes, code,
│   │   │                      #   styling, headers, commands (+ -ebook variants)
│   │   ├── chapters/          # prologue, 01-counting..12-life-of-a-token, epilogue,
│   │   │                      #   chapter-template.tex  ← annotated A-B-A' skeleton
│   │   ├── front-matter/      # half-title, title-page, copyright(+ebook), dedication, cover/
│   │   ├── back-matter/       # about-author, back-cover(+art, standalone), isbn-barcode.png
│   │   ├── bib/refs.bib
│   │   └── scripts/           # book_stats, ngram_analysis, adjacent_sentence_repetition,
│   │                          #   generate_isbn_barcode, update_kdp_cover_vars
│   ├── figures/
│   │   ├── tikz/              # ~61 TikZ figure sources (one file per figure)
│   │   ├── data/              # .dat/.csv/.json data for PGFPlots (generated)
│   │   ├── scripts/           # Python generators (lorenz, bifurcation, attention extraction,
│   │   │                      #   tokenizer comparisons) + period-authentic COBOL/Fortran demos
│   │   └── images/
│   ├── epub/                  # Custom LaTeX→EPUB converter (Python package `converter`:
│   │   │                      #   cli, parser (TexSoup), renderer, handlers/) + XHTML templates,
│   │   └── templates/         #   fonts, CSS, content.opf, nav.xhtml
│   ├── build/                 # Gitignored outputs (pdf/, epub/)
│   ├── docs/                  # STYLE.md, STYLE-REFERENCE.md, FIGURE-STYLE.md,
│   │                          #   FIGURE-REQUIREMENTS.md, EPUB-PUBLISHING.md, KDP.md
│   ├── research/              # detailed-outline.md, fact-check-consolidated.md,
│   │                          #   fact-check-report.md, vignettes/, per-chapter research
│   └── archive/               # markdown-drafts/ (pre-LaTeX chapter drafts), reviews/,
│                              #   style-exploration PNGs
│
└── notes/                     # Textbook planning + shared background
    ├── structure/             # 00-overview, 01-chapter-outline, 02-narrative-strategy,
    │                          #   03-audience-tracks (4 reader personas), 04-reviewer-synthesis,
    │                          #   06-marketing-blurbs, 07a-g narrative-frame options (!),
    │                          #   08a-b promoted frames
    ├── vignettes/             # Historical narratives per part + bibliography.bib
    ├── figures-equations/     # Visual/math inventory per part
    ├── pop-sci-projections/   # 3 competing book concepts + blurb evaluations
    ├── background/            # sources-01/02.md
    ├── samples/writing/       # Style reference samples (own blog posts, book excerpts)
    └── references/            # PDFs (von Neumann, SCOTUS prediction papers)
```

## 3. LaTeX Pipeline

### Class & variants

```latex
% main.tex (print)
\documentclass[11pt,twoside,openright]{book}
\input{preamble/main}
```

```latex
% main-ebook.tex (e-reader PDF)
\documentclass[14pt,oneside]{extbook}
\input{preamble/main-ebook}
```

`main-interior.tex` defines `\NoCovers` and reuses main; bleed mode is a compile-time flag: `\def\BleedMode{1}\input{main.tex}` (via `make bleed -jobname=main-bleed`).

### Modular preamble (`latex/preamble/main.tex`)

```latex
% Load order matters - packages first, then colors (needs xcolor),
% then TikZ (needs colors), then boxes (needs tcolorbox + colors),
% then styling (needs colors), then headers, then commands
\input{preamble/packages}
\input{preamble/colors}
\input{preamble/tikz}
\input{preamble/boxes}
\input{preamble/code}
\input{preamble/styling}
\input{preamble/headers}
\input{preamble/commands}
```

### Geometry (`preamble/packages.tex`) — KDP-aware, with bleed switch

```latex
% US Trade size: 6in x 9in (standard for professional/technical books)
\usepackage[
  papersize={6in,9in},
  inner=0.65in,        % Gutter margin (KDP min is 0.5")
  outer=0.525in,       % Outside margin (KDP min is 0.25")
  top=0.75in,          % Top margin (0.75" for headers per KDP)
  bottom=0.75in,       % Bottom margin (0.75" for footers per KDP)
  includehead,
  includefoot,
]{geometry}

% Bleed build: expand canvas to 6.125 x 9.25 while preserving trim margins.
\ifdefined\BleedMode
  \geometry{ paperwidth=6.25in, paperheight=9.25in, inner=1in, outer=0.75in,
    top=0.875in, bottom=0.875in, footskip=0.35in }
\fi
```

### Fonts — exact setup (`preamble/packages.tex`)

```latex
\usepackage{fontspec}
...
% EB Garamond: Elegant, readable serif for body text
% Runs slightly small, so scale up to 1.05 for comfortable reading at 11pt
\setmainfont{EB Garamond}[
  Scale = 1.05,
  Ligatures = TeX,
  Numbers = OldStyle,
]

% Sans-serif for occasional use (figures, captions, headers)
\setsansfont{Source Sans Pro}[ Scale = MatchLowercase, ]

% Monospace for any code snippets
\setmonofont{Noto Sans Mono}[ Scale = MatchLowercase, ]

% --- Fallback fonts for CJK and Emoji ---
\newfontfamily\cjkfont{Noto Serif CJK SC}[Scale=0.95]
\newfontfamily\emojifont{Noto Color Emoji}[Renderer=HarfBuzz]
\newcommand{\cjk}[1]{{\cjkfont #1}}
\newcommand{\emoji}[1]{{\emojifont #1}}
```

Typography discipline follows: `microtype`, `\setstretch{1.18}`, `\parindent 1.5em` / `\parskip 0pt` (traditional book style), `\raggedbottom`, `\emergencystretch=2em`, tuned hyphenation penalties, and hard widow/orphan control (`\widowpenalty=10000 \clubpenalty=10000 \brokenpenalty=5000`).

### Chapter styling (`preamble/styling.tex`) — the most book-like of the three projects

```latex
% Numbered chapters: CHAPTER I / Title
\titleformat{\chapter}[display]
  {\normalfont\raggedleft}
  {%
    \vspace{10pt}%
    {\color{text-muted}\scshape\large CHAPTER \MakeUppercase{\romannumeral\thechapter}}%
  }
  {8pt}
  {\LARGE\itshape}
  [\vspace{8pt}\hfill{\color{lightcolor}\rule{0.5\textwidth}{0.4pt}}]

% Unnumbered chapters (Prologue, Epilogue, etc.): just the title
\titleformat{name=\chapter,numberless}[display]
  {\normalfont\raggedleft} {} {0pt}
  {\vspace{10pt}\LARGE\itshape}
  [\vspace{8pt}\hfill{\color{lightcolor}\rule{0.5\textwidth}{0.4pt}}]
```

Plus: an ornament command (`\chapterornament` — rule ◇ rule) used in part pages; titletoc-styled TOC (parts/chapters/sections with dot leaders and color); heading-orphan protection by wrapping sectioning commands:

```latex
\let\originalsection\section
\renewcommand{\section}{\Needspace{5\baselineskip}\originalsection}
```

Custom small `quote` renewal (italic, `text-secondary`), custom `\epigraph` (right-aligned 0.75\textwidth minipage), caption setup (bold colored labels, muted text).

### Running heads (`preamble/headers.tex`) — proper trade-book conventions

Three fancyhdr page styles with switch commands used in the master file (`\usefrontmatterstyle`, `\usemainmatterstyle`, `\usebackmatterstyle`), plus `\disablecleardoublepage`/`\enablecleardoublepage` toggles so front matter packs tightly while main-matter chapters open recto:

```latex
% Main matter: Book title (even/verso), Chapter title (odd/recto)
\fancypagestyle{mainmatterstyle}{%
  \fancyhf{}%
  \fancyhead[LE]{\small\thepage\quad\itshape\color{text-muted}\booktitle}
  \fancyhead[RO]{\small\itshape\color{text-muted}\leftmark\quad\thepage}
  \renewcommand{\headrulewidth}{0pt}%
  \renewcommand{\footrulewidth}{0pt}%
}
```

`main.tex` documents the traditional US Trade front-matter page order (half title p.i, title p.iii, copyright p.iv verso, dedication p.v, TOC p.vii) in comments — a checklist worth keeping.

### Layered color system (`preamble/colors.tex`)

Explicit 5-layer architecture — the cleanest color design of the three projects:

```latex
% ARCHITECTURE:
%   Layer 1: PRIMITIVES - Raw RGB values (slate-900, amber-600, etc.)
%   Layer 2: SEMANTICS - Content types (definition, example, history, key)
%   Layer 3: COMPONENTS - Usage contexts (bg-*, border-*, text-*)
%   Layer 4: COVER - Cover-specific colors
%   Layer 5: LEGACY - Backward compatibility aliases
```

Layer 1 is Tailwind palette hex values (`slate-50..900`, blue/green/amber/red/teal/indigo families). Layer 2 maps content types (`definition-dark/base/light`, `example-*`, `history-*`, `key-*`, `caution-*`, `note-*`, `tryit-*`, `technical-*`). Layer 3: `primary`, `text-primary/secondary/muted`, `bg-*`, `border-*`. Layer 5 uses `\colorlet` aliases so old names keep working.

### Boxes (`preamble/boxes.tex`)

8 semantic tcolorbox environments (definition/example/history/key/caution/note/tryit/technical) with two clever global mechanisms:

```latex
\tcbset{
  % Require at least 3 lines before breaking to next page
  lines before break=3,
  short/.style={unbreakable},
  long/.style={breakable, lines before break=4}
}

\tcbset{
  importance/.is choice,
  importance/high/.style={ boxrule=2pt, top=10pt,bottom=10pt,left=12pt,right=12pt },
  importance/medium/.style={},
  importance/low/.style={ boxrule=0.8pt, opacityback=0.92, opacityframe=0.6, ... },
  importance/.default=medium
}
```

So authors write `\begin{examplebox}[long]` or `[importance=low]` without touching styling.

### Bibliography (`preamble/packages.tex`)

biblatex/biber `numeric-comp, sorting=none`, superscript unbracketed citations (¹²³), aggressively cleaned for pop-sci reading: `doi=false, isbn=false, eprint=false, maxbibnames=3`, `\renewbibmacro{in:}{}` (drops "In:"), issue numbers hidden, `\small` bibfont.

### Custom commands (`preamble/commands.tex`)

`\keyterm{}` (bold primary color for first-introduction), `\term{}`, color-coded attention terms `\Q{}/\K{}/\V{}` (blue/green/amber so readers track Query/Key/Value visually), `\acr{}` small-caps acronyms, `\spacetoken` (visible ␣ via Noto Sans Symbols2 for tokenization examples), `\scenbreak` (used in chapter template for scene breaks).

### Chapter template (`latex/chapters/chapter-template.tex`)

An annotated skeleton encoding the A-B-A' structure with per-section style/tense/length guidance in comments, e.g.:

```latex
% SECTION A: OPENING HOOK
% Style: Novelistic, scene-setting, character-driven
% Tense: Past tense for events; present tense for "camera-present" immediacy
% Length: ~6 pages
```

Directly reusable pattern: ship a `chapter-template.tex` whose comments teach the book's structure.

## 4. Build Automation

- **`latex/Makefile`** (580 lines) is the centerpiece: targets `pdf` (latexmk -lualatex with auto-retry after clearing `.fdb_latexmk`), `quick`, `full`, `ebook`, `bleed` (jobname trick), `release` (timestamped copies to `../build/pdf/` named `"$(BOOK_TITLE) - $(TIMESTAMP) - PRINT.pdf"` etc.), `epub`, `kindle` (calibre `ebook-convert` with tuned flags), `kindle-validate` (epubcheck), `all-formats`, `watch` (latexmk -pvc), `validate` (checks page size vs. expected 432x648pt, greps log for undefined references and overfull boxes), `wordcount`/`pagecount` (pdftotext/pdfinfo), `data` (regenerates PGFPlots `.dat` files from Python scripts with proper Make dependencies), and the KDP chain:
  - `kdp-interior` → `kdp-cover-vars` (Python computes spine width from page count: `pages*0.002252 + 0.06` for white paper, writes `kdp-cover-vars.tex`) → `kdp-cover` (3 passes for TikZ `remember picture`, then Ghostscript transparency flattening to PDF/X-ish 1.3) → `kdp`.
  - Sandbox-friendly details: `TEXMFCACHE`/`TEXMFVAR` pinned to a repo-local `.texlive-cache`, `UV_CACHE_DIR` pinned inside `build/`.
  - Colored terminal output with ✓/✗/➜ symbols and a `help` target documenting everything.
- **Figure pipeline:** Python generators in `figures/scripts/` (run via `uv run python`) produce data files consumed by TikZ/PGFPlots sources in `figures/tikz/`; Make tracks script→data dependencies. Includes real model-derived data (GPT-2/KL3M attention extraction) and even compiled COBOL/Fortran Y2K/Patriot bug demos for authenticity.
- **EPUB converter** (`epub/converter/`): a custom Python package (TexSoup parser → document model → XHTML renderer with handler registry), CLI via typer: `python -m converter book ../latex/chapters/ -o templates/ -b ../latex/bib/refs.bib` then `python -m converter epub ...`. Run with `uv run --with TexSoup,lxml,typer,rich`. `docs/EPUB-PUBLISHING.md` documents KDP/Apple Books requirements (cover 2560x1600, 300 DPI images, no MathML on KDP) and the TikZ→PNG externalization strategy.
- **Prose QA scripts** (`latex/scripts/`): `book_stats.py`, `ngram_analysis.py`, `adjacent_sentence_repetition.py` — repetition detection at the n-gram and adjacent-sentence level.
- Root `pyproject.toml` deps: lxml, numpy, nupunkt, pandas, pillow, pydetex, rich, scipy, texsoup, tiktoken, tokenizers, typer, yfinance (yfinance for the Intel FDIV stock-price figure). `main.py` is a stub.

## 5. Research Workflow

Lighter-weight than history-book but with a distinctive **exploratory front end**:

- **Concept exploration before commitment** (`notes/`): the repo's most template-worthy early-stage asset. `notes/structure/07-narrative-frame-options.md` plus `07a`–`07g` each develop a competing narrative frame (post-collapse, generation ship, family chronicle, discovered archive, contemporary thriller, historical vignettes, hybrid), then `08a/08b` "promote" the winners. Similarly `notes/pop-sci-projections/` contains **three complete competing book concepts** (version-1/2/3 with chapter lists), `blurb-variations-*.md`, and `blurb-evaluation-synthesis.md` — marketing copy written and evaluated *before* the book, used to pick the concept. `00-overview.md` carries a dated NOTE redirecting to the authoritative outline once the decision was made.
- **Audience personas** (`notes/structure/03-audience-tracks.md`): four named readers (Alex the curious teen programmer, Jordan the social-science PhD, Sam the senior engineer, Dr. Chen the professor) that later become **review-agent perspectives**.
- **Research → drafting inputs**: `pop-sci-book/research/outline/detailed-outline.md` (master outline, single source of truth), `research/vignettes/` (per-chapter narrative research), `research/fact-check-consolidated.md` (verified corrections that drafting agents must cross-reference), plus targeted memos (`chapter-08-trigonometry-research.md`). `notes/vignettes/` holds historical-narrative research per part with its own `bibliography.bib`.
- **Draft lineage preserved**: `archive/markdown-drafts/` keeps the pre-LaTeX markdown chapter drafts; `archive/reviews/` keeps past review output.

## 6. Style / Craft / AI-Tone Guides

- **`pop-sci-book/docs/STYLE.md`** — the voice bible. Core principle: "Write as if explaining to a curious friend over coffee." The **Coffee Test**: "After writing a paragraph, ask yourself whether you could say it aloud without feeling ridiculous. If it sounds like a textbook, a press release, or a TED talk, rewrite it." Rules: "we" for shared discovery (never "one might", never second-person commands); present tense for explanations, past for history, no tense drift; sentence targets (avg 15-20 words, max 35, occasional 3-8); one-idea-per-sentence; front-load the point; banned paragraph openers ("It is important to note that...", "There are several reasons why..."); paragraphs 3-5 sentences, never more than 7. Banned words: `delve, landscape, realm, tapestry, crucial, unlock, leverage, utilize, harness, foster, elevate, streamline, robust, embark, illuminate, unveil, pivotal, intricate, myriad, plethora, multifaceted, paradigm`. Banned phrases include "Let's dive in", "Here's the thing", "Indeed/Furthermore/Moreover".
- **`docs/STYLE-REFERENCE.md`** — extended DOs/DON'Ts; **`docs/FIGURE-STYLE.md`** — a *visual* style guide: "Elegant restraint — figures should feel like something from Quanta Magazine", high data-to-ink ratio, Tailwind-based figure palette with semantic mappings (definitions=blue, examples=green, history=amber...), typography table for axis labels/annotations. Having a figure style guide parallel to the prose style guide is a strong pattern.
- **`CLAUDE.md`** — includes a date/model-freshness warning block (forces web-search verification of AI model claims — an anti-staleness pattern), the repo map, the ordered "Key Files to Read" list, quick-reference style rules, the A-B-A' table, build commands ("ALWAYS use the Makefile... Never run lualatex directly"), and the agent workflow.
- **`.claude/agents/` — 14 writing sub-agents**, the repo's signature AI-workflow asset, organized as a 7-phase pipeline in CLAUDE.md: Planning (`outline-iteration`), Drafting (`draft-from-outline`, model: opus), Review (`critical-review` with persona parameter — the four audience personas plus copy-editor/developmental-editor/fact-checker; `citation-verification` — uncited claims, bibtex key existence, claim-source alignment, WebSearch for missing sources), Revision (`revision-from-feedback`, `accessibility-check`, `example-analogy-refinement`), Polish (`flow-improvement`, `style-guide-conformance`, `compression-tightening`), Integration (`cross-reference-verification`, `opening-closing-hooks`, `visual-figure-specification`), Final (`post-revision-fact-check`). Agent files carry frontmatter (`tools`, `model: opus`) and embed the style rules + mandatory-reading lists so each agent is self-sufficient.
- **`pop-sci-book/WRITING-PROCESS.md`** — maps the agents to a step-by-step chapter workflow with a "When to Skip" column per polish agent.

## 7. Verdict

**Reusable pieces (high value):**
1. **The whole `latex/` production stack** — modular preamble with documented load order, layered Tailwind color system, importance/breaking-aware boxes, trade-book headers/front-matter ordering, EB Garamond + Source Sans + Noto Mono font stack with CJK/emoji fallbacks, widow/orphan discipline. This is the best starting point for the template's LaTeX core.
2. **The multi-format Makefile** — print/bleed/ebook/EPUB/Kindle/KDP-cover from one source, timestamped `release` target, `validate`, spine-width computation, repo-local TeX/uv caches. Directly liftable.
3. **`chapter-template.tex`** — annotated skeleton as executable documentation of chapter structure.
4. **The 14-agent writing pipeline** — persona-parameterized review, dedicated citation-verification, phase-organized polish agents with skip guidance.
5. **STYLE.md (Coffee Test) + FIGURE-STYLE.md pairing** — prose and visual style guides as siblings.
6. **Early-stage exploration workflow** (crucial for a template that must support books that are just starting): numbered `notes/structure/` planning docs; multiple competing narrative frames and book "projections" each developed in its own file; blurbs/marketing copy written and adversarially evaluated pre-drafting; audience personas defined early and reused as reviewers; a dated NOTE in superseded docs pointing to the new source of truth.
7. Figure pipeline pattern: Python generator → data file → TikZ/PGFPlots, wired into Make.

**Pitfalls:**
- Release artifacts (PDF/EPUB/AZW3/MOBI) committed inside `latex/` alongside sources despite `build/` existing — inconsistent output discipline.
- Documentation drift: title says "Eleven Operations" but there are 12 chapters; CLAUDE.md says "13 specialized agents" then lists 14; `notes/pop-sci-projections/00-overview.md` says 10 operations. Multiple stale duplicates (`KDP.md` at two levels, `FIGURES.md` at two levels, WRITING-PROCESS.md vs CLAUDE.md overlap). A template should minimize doc duplication and designate one source of truth per topic.
- Repo carries two books; the "on hold" textbook material makes the root README misleading relative to CLAUDE.md. The template should assume one book per repo.
- Custom EPUB converter is powerful but heavy (a whole Python package + 101 template files); for a template, offering it as an optional module (or documenting tex4ebook/pandoc alternatives, as `EPUB-PUBLISHING.md` partially does) is wiser than making it core.
- LuaTeX shutdown segfault workaround baked into Makefile (`-$(LATEX) ...` tolerated failure + `test -s` on output) — keep the pattern, document why.

**Unique:** the KDP publishing chain (computed spine, wrap cover, PDF flattening, ISBN barcode generation) — nothing in the other projects covers actually shipping to a printer; and the persona system that flows from planning doc → review agents.
