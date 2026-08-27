# Research Report: history-book

Source: `/home/mjbommar/projects/personal/history-book`

## 1. Purpose & Status

**"History of the World: A Book for Curious Kids"** — a world history book for ages 10-14, organized as a 3D matrix: 14 chapters (time periods) x 9 dimensions of human experience x 6+ world regions. Gombrich-style warm narrative voice, polycentric (no default protagonist region), inquiry-driven pedagogy with explicit historical-thinking skills.

**Status (per `docs/PRODUCTION-TRACKER.md`, dated 2026-03-13):** far along — all 14 chapters through Research/Outline/BibTeX/Draft/Style Check/Review/Revise (DONE); Polish IN_PROGRESS; Verify TODO. Current metrics: **469 pages, 164,677 words, 192 feature boxes (0 errors), 0 style violations, 0 undefined citations**.

**Format:** single 7x10in illustrated-nonfiction PDF via LuaLaTeX (`latex/book.pdf`). No EPUB pipeline. A structured assessment corpus (Anki/web-compatible YAML) is a second output format in prototype stage.

## 2. Directory Layout

```
history-book/
  CLAUDE.md                 # Master project instructions (very rich — see §6)
  AGENTS.md                 # Agent guidance: priority docs, non-negotiables, conflict resolution
  README.md                 # Overview + the matrix table
  pyproject.toml / main.py  # uv project; main.py is a hello-world stub
  scripts/                  # 13 utility scripts (QA checks, research runners, stats)
  docs/
    PRODUCTION-TRACKER.md   # Single source of truth for pipeline state (self-verifying)
    WRITING-PROCESS.md      # 7-phase pipeline definition
    style-guide.md, STYLE-AI-TELLS.md, STYLE-CRAFT.md
    pedagogy.md, sources.md, feature-box-guidance.md, card-guidance.md
    assessment-anki-interoperability.md, bloom-structured-representation.md
    curriculum/             # AP World, IB History, Michigan standards summaries
    scope-review-01/        # Standards-alignment audit (master-matrix, gaps)
    copyedit-01/            # Per-chapter copyedit review reports (ch01–ch14)
    media-01/               # Per-chapter media/illustration specs
    reviews-02/             # Persona reviews (Chomsky, Rand, Sanders, Palin, Musk...) + SYNTHESIS
    reviews-03/             # Demographic-persona reviews (13 personas) + SYNTHESIS + EXPANSION-PLAN
  notes/
    structure.md            # Master plan: periods, dimensions, chapter architecture
    matrix.md               # Coverage rotation, dimension grids, compelling questions
    audience.md             # Audience/cognitive-development analysis
    14-chapter-design.md    # Split rationale, AP/IB alignment
    research-watchlist.md   # Volatile claims to re-verify before drafting
    writing-plan.md
    outlines/               # ch-01..ch-14 section-by-section outlines
  research/                 # Per-chapter research knowledge base (see §5)
    RUNNER.md               # How the Codex batch research runner works
    config/research-matrix.yaml  # Axes: periods/regions/dimensions/report kinds
    _templates/             # matrix-brief.md, chronology-report.md
    _shared/                # Cross-chapter research
    ch-01-first-humans/ ... ch-14-world-we-are-making/  (8–16 files each)
    _old-ch-*/              # Retired chapters kept for reference
  assessments/
    README.md               # Canonical assessment corpus rules
    chapters/ch01-first-humans.yaml  # Prototype structured assessment bank
  latex/
    book.tex                # Master file
    Makefile                # lualatex + biber + 2x lualatex
    preamble/colors.tex     # Semantic color system
    preamble/boxes.tex      # 13 tcolorbox feature environments
    bib/ch01..ch14 .bib     # One BibTeX file per chapter
    chapters/chNN-slug/     # 4 files each: main.tex, opening-*.tex, *-meanwhile.tex, sources-conclusion.tex
```

## 3. LaTeX Pipeline

### Class, geometry, fonts (`latex/book.tex`)

```latex
\documentclass[11pt,openany]{book}

% Page geometry - 7x10 illustrated nonfiction
\usepackage[paperwidth=7in, paperheight=10in,
  top=0.75in, bottom=0.75in, inner=0.875in, outer=0.75in]{geometry}

% Fonts (LuaLaTeX)
\usepackage{fontspec}
\setmainfont{Latin Modern Roman}
\setsansfont{Latin Modern Sans}
\setmonofont{Latin Modern Mono}
```

Notable global settings:

```latex
% Prevent LaTeX from stretching vertical space to fill pages
\raggedbottom
% Only number down to section level (not subsection/subsubsection)
\setcounter{secnumdepth}{1}
...
\setcounter{tocdepth}{1}   % TOC shows chapters and sections only
% Use \input + \clearpage instead of \include to avoid forced blank pages
\input{chapters/ch01-first-humans/main}\clearpage
```

### Chapter styling

Minimal — the craft investment went into feature boxes, not chapter openers:

```latex
\usepackage{titlesec}
\titleformat{\chapter}[display]
  {\normalfont\huge\bfseries}
  {\chaptertitlename\ \thechapter}{20pt}{\Huge}
```

### Bibliography

biblatex/biber, superscript bracketed numeric citations, one `.bib` per chapter loaded via 14 `\addbibresource` lines:

```latex
\usepackage[backend=biber,style=numeric-comp,sorting=none,maxbibnames=99]{biblatex}
\renewcommand{\mkbibsuperscript}[1]{\textsuperscript{\mkbibbrackets{#1}}}
\DeclareCiteCommand{\cite}[\mkbibsuperscript]
  {\usebibmacro{cite:init}\usebibmacro{prenote}}
  {\usebibmacro{citeindex}\usebibmacro{cite:comp}}
  {}
  {\usebibmacro{cite:dump}\usebibmacro{postnote}}
...
\printbibliography[heading=bibintoc,title={Sources and Further Reading}]
```

### Feature environments (`latex/preamble/boxes.tex` + `colors.tex`)

The signature LaTeX asset. 13 semantic tcolorbox environments (`compellingquestion`, `sourcecheck`, `intheirworld`, `twoviews`, `walkintheirshoes`, `whatif`, `connecttoday`, `meanwhile`, `zoomout`, `youdecide`, `historiansdebate`, `thinkdeeper`, `dimensionsnapshot`), each mapping a pedagogical move to a color family + FontAwesome icon. Header comment: "Adapted from ai-professional-services-book design system." Shared base style:

```latex
\tcbset{
  history base/.style={
    enhanced,
    boxrule=0pt,
    arc=3pt,
    left=10pt, right=10pt, top=10pt, bottom=10pt,
    fonttitle=\fontsize{10pt}{12pt}\selectfont\bfseries\scshape,
    coltitle=title-text,
    colframe=white,
    attach boxed title to top left={yshift=-6pt, xshift=4pt},
    fuzzy shadow={1pt}{-1pt}{0pt}{0.4pt}{black!15},
    before skip=\baselineskip,
    after skip=\baselineskip,
  },
  history title/.style n args={1}{
    boxed title style={ enhanced, colback=#1, colframe=#1, arc=2pt, boxrule=0pt,
      left=8pt, right=8pt, top=4pt, bottom=4pt,
      fuzzy shadow={0.8pt}{-0.8pt}{0pt}{0.3pt}{black!15}, },
    borderline west={4pt}{0pt}{#1},
    borderline north={1.5pt}{0pt}{#1},
  },
}
```

Nice touches worth stealing:
- `\iconShadow{...}` — TikZ drop shadow behind white FontAwesome icons in box titles.
- `\histsubtitle{#1}` — appends "`: Subtitle`" only if the optional argument is non-empty.
- Short boxes are `unbreakable`; long-form ones (`meanwhile`, `youdecide`, `dimensionsnapshot`) are `breakable`.

Colors are a semantic dark/light pair per pedagogical family (`latex/preamble/colors.tex`):

```latex
% SOURCE BLUE — detective work, primary source analysis
\definecolor{source-dark}{RGB}{30,64,120}
\definecolor{source-light}{RGB}{232,241,255}
% WORLD GREEN ... QUESTION AMBER ... CONNECT TEAL ... PATTERN INDIGO ...
% DEBATE ROSE ... DECIDE GOLD ... SLATE (data) ... plus title-text/icon-shadow utility
```

### Build (`latex/Makefile`)

Deliberately simple:

```make
$(MAIN).pdf: $(MAIN).tex $(wildcard chapters/*/*.tex) $(wildcard bib/*.bib)
	lualatex -interaction=nonstopmode $(MAIN).tex
	biber $(MAIN)
	lualatex -interaction=nonstopmode $(MAIN).tex
	lualatex -interaction=nonstopmode $(MAIN).tex
```

### Chapter file convention

Each chapter dir has exactly 4 files; `main.tex` is a thin wrapper (`\chapter`, `\label`, `compellingquestion` box, TODO comments for timeline/map art, then 3 `\input` calls). Keeps individual files small enough for AI editing.

## 4. Build Automation & Scripts

- `main.py` is a stub ("Hello from history-book!"); all real logic lives in `scripts/`, run via `uv run python scripts/<name>.py`.
- `pyproject.toml`: Python >= 3.13, deps: `requests, beautifulsoup4, lxml, pyyaml, rich, playwright, httpx`; ruff configured (line-length 120).
- QA scripts, each enforcing a documented rule set:
  - `check_style.py` — banned words, sentence length (exit criteria for the Draft→Review loop is zero violations)
  - `check_boxes.py` — feature box word counts (per-type targets/hard maxes defined in CLAUDE.md), nesting, title tab length
  - `check_headings.py` — heading length/word-count limits per level (warn/error thresholds tabulated in CLAUDE.md)
  - `check_repetition.py` — repetition detection
  - `book_stats.py` — word/page metrics feeding PRODUCTION-TRACKER
  - `build_assessments.py` — YAML assessment bank → machine JSON + Anki import
  - `gen_copyedit_templates.py`, `outline.py`, `ch01_analysis.py`
  - `fetch_url.py` — Playwright-based source verification (CLAUDE.md explicitly: "Do NOT use WebFetch for source verification")
- Research automation: `research_matrix.py` and `research_chronology.py` (see §5).

## 5. Research Workflow (the standout system)

### Per-chapter research folders

Standard file schema per `docs/WRITING-PROCESS.md`:

```
research/ch-XX-[period-name]/
├── README.md              ← Period overview, key questions, gaps
├── sources.md             ← Curated sources with full citations
├── close-up-1.md          ← Deep research for close-up region 1
├── close-up-2.md          ← Deep research for close-up region 2
├── panoramic.md           ← Key facts for panoramic regions
├── primary-sources.md     ← Excerpts for Source Check features
├── daily-life.md          ← Material for "what was it like?" moments
├── timeline.md            ← Event chronology
└── downloads/             ← PDFs, images, source materials
```

Plus ad-hoc fact-check files per chapter (e.g. `inca-roman-roads-check.md`, `floresiensis-dating-check.md`, `henry-viii-reformation-check.md`) — targeted verification memos for specific risky claims.

The chapter `README.md` is the keystone: it defines the compelling question, close-up vs. panoramic regions, a **dimension-depth table** (Deep/Medium/Light per dimension with key content), supporting questions, "Questions We Can't Fully Answer", and a volatility-watchlist check. This is written during Research phase, before any prose.

### Config-driven batch research runner

`scripts/research_matrix.py` is a **Codex batch runner** (spawns `codex` CLI jobs with ThreadPoolExecutor, default timeout 45min, max 36 tasks). All axes live in `research/config/research-matrix.yaml`, not code: `report_kinds` (matrix-brief, chronology), 14 `periods`, ~25 `regions`, 9 `dimensions` — each with `slug`, `title`, `summary`, `file_stems` (mapping axis slugs to actual chapter filenames) and `aliases`; plus `alias_groups` for batch selection (e.g. `socioeconomic` expands to 3 dimensions).

For each period x region x dimension cell, the runner resolves local context files (CLAUDE.md, docs/sources.md, chapter README/sources/primary-sources/debates, plus axis-matched close-up/dimension files) and feeds them to Codex with an output template. Templates (`research/_templates/matrix-brief.md`, `chronology-report.md`) enforce required section headers, validated by the script:

```python
MATRIX_REQUIRED_HEADERS = [
    "## Why This Cell Matters", "## Core Answer", "## Key Facts",
    "## Timeline Anchors", "## Evidence and Primary Sources",
    "## Debates and Cautions", "## Research Gaps", "## Sources Used",
]
```

Key Facts tables carry structured epistemic metadata: `| Claim | Confidence (secure/probable/debated) | Evidence Type (textual/archaeological/material/environmental/statistical) | Source |`. Usage supports `--dry-run --show-context` to preview exactly which files a cell will receive, and `--workers N` for parallelism.

### Assessment layer (`assessments/`)

Structured YAML per chapter (`assessments/chapters/ch01-first-humans.yaml`): `content_nodes` anchored to LaTeX file + line ranges, each tagged with chapter phase, feature type, dimensions, historical skills, and **two-dimensional Bloom alignment split into `teaches` / `elicits` / `assesses` roles**. AGENTS.md non-negotiable: "The LaTeX manuscript in `latex/` is the content source of truth"; structured layers point back to source files + hashes. Target density: 1-2 items per rendered page (~25-50/chapter).

### Multi-persona review system (docs/reviews-02, reviews-03)

Two review rounds simulate readers: round 2 uses ideologically opposed personas (objective historian, Chomsky, Rand, Sanders, Palin, Musk) to stress-test neutrality; round 3 uses 13 demographic personas (Lakota teacher, evangelical homeschooler, Muslim doctor in Dearborn, union steelworker...). Each round ends in a `SYNTHESIS.md` and an expansion/revision plan. `docs/copyedit-01/` holds per-chapter copyedit reports; `docs/scope-review-01/` audits against AP/IB/Michigan standards captured in `docs/curriculum/`.

## 6. Style / Craft / AI-Tone Guides

- **`CLAUDE.md`** (335 lines) is the master doc: matrix concept, chapter architecture (8-step inquiry model), section heading standards with enforced char/word limits per level, feature-box word budgets per environment type, "THE PRIME DIRECTIVE: Neutral, Objective, True History" (Full Picture Rule, Framing Symmetry Rule, what "neutral" does NOT mean), voice rules, readability targets (FK 6th-8th grade, 12-18 word average sentence, 30-word max), the "Kitchen Table Test", and a banned-word list (delve, tapestry, landscape (metaphorical), cornerstone, pivotal, groundbreaking, foster, leverage...).
- **`docs/STYLE-AI-TELLS.md`** — a catalog of AI-detection signatures with fix rules: "This" disease (max one "This" opener per paragraph), gerund openers (max one per page), "As X, Y" constructions, triple structures ("AI loves threes... Break the pattern. Use two sometimes. Four occasionally."), banned filler transitions ("That said," "Against this backdrop,"...), hedging clusters ("might potentially → might"), textbook voice, motivational closers, definition dumps. Framed via perplexity + burstiness.
- **`docs/STYLE-CRAFT.md`** — positive craft: the Burstiness Principle with worked before/after rhythm examples, short-sentences-for-emphasis, front-loading for young readers, active voice, and "The Concrete-First Principle" ("the single most important craft rule": every abstraction arrives through a specific person/object/place/moment).
- **`docs/WRITING-PROCESS.md`** — 7-phase pipeline `Research → Outline → Draft → Review → Revise (loop) → Polish → Verify` with explicit exit criteria, a full chapter-outline markdown template (word budgets per section, Feature Inventory checklist, Vocabulary Budget, Coverage Audit), reader-perspective review table, AI-tell audit checklist, and per-phase deliverable checklists.
- **`docs/PRODUCTION-TRACKER.md`** — "single source of truth for the writing pipeline... knows how to verify its own state": a chapter x phase status table plus current book metrics and the commands to re-verify each column. CLAUDE.md instructs "Always read `docs/PRODUCTION-TRACKER.md` first."
- **`AGENTS.md`** — priority reading order, non-negotiables, and a conflict-resolution order: (1) direct user request, (2) AGENTS.md + CLAUDE.md, (3) detailed docs.

## 7. Verdict

**Reusable pieces (high value):**
1. `latex/preamble/boxes.tex` + `colors.tex` — a complete, generic-izable semantic feature-box design system (base style + per-feature environments with icons, dark/light color pairs, breakable/unbreakable discipline).
2. The **research folder schema** (README + sources + close-ups + panoramic + primary-sources + timeline + debates + fact-check memos) with the chapter README as pre-writing contract.
3. **Config-driven research runner** pattern: axes in YAML, output templates with required headers, confidence/evidence-type tables, `--dry-run --show-context` preview. Generalizes to any book with a coverage matrix.
4. **PRODUCTION-TRACKER.md** pattern: self-verifying status table + phase exit criteria + "read this first" rule.
5. The style-guide triad: banned words + AI-tells (negative) + craft (positive) + machine enforcement (`check_style.py`, `check_boxes.py`, `check_headings.py`). The check-script-per-rule-doc pairing is the key idea.
6. The chapter file convention (4 small `.tex` files + thin `main.tex` wrapper) and per-chapter `.bib` files — both AI-editing-friendly.
7. Multi-persona review rounds with SYNTHESIS docs.

**Early-stage / outlining workflow (important for a template supporting new books):** the sequence here was `notes/structure.md` (master plan) → `notes/matrix.md` (coverage plan) → `notes/audience.md` → `notes/research-watchlist.md` → per-chapter research README → `notes/outlines/ch-XX.md` (using the WRITING-PROCESS outline template with word budgets and coverage audit) → draft. A template should scaffold `notes/` and `research/_templates/` before it scaffolds `latex/`.

**Pitfalls:**
- Build artifacts (`book.pdf`, `.log`, `.bbl`, etc.) are committed in `latex/` — no output dir separation (contrast with complexity-book's `build/`).
- Fonts are plain Latin Modern — the typographic identity is entirely in the boxes; a template should upgrade the font stack (see complexity-book/beamer-template).
- `main.py` is dead weight; the hatch `packages = ["scripts"]` wheel config is an odd workaround.
- Single monolithic `book.tex` with 14 hardcoded `\addbibresource` + `\input` lines — fine at 14 chapters, but a template could generate these.
- Duplication risk: CLAUDE.md restates rules that also live in docs/ (word budgets, heading limits) — two places to update.
- Retired research kept as `_old-ch-*` dirs — works, but the convention should be documented.

**Unique:** the pedagogical metadata layer (Bloom teaches/elicits/assesses anchored to LaTeX line ranges) and the assessment-bank-as-second-output-format idea; the neutrality "Prime Directive" with Framing Symmetry Rule as an example of a book-specific editorial constitution living in CLAUDE.md.
