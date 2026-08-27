# Research Report: ai-professional-services-book

Source: `/home/mjbommar/projects/personal/ai-professional-services-book`
Reviewed: 2026-07-06. Purpose: extract reusable pieces for the master book template.

---

## 1. Purpose & Status

**What it is**: *Building AI-Native Professional Services Firms — Strategy, Economics, and Execution* (Katz, Bommarito, Bommarito). A trade/business book for partners, founders, and practice leaders on transforming or building AI-native professional-services firms. Unlike the textbook sibling, this is a **narrative-driven business book**: frameworks are carried by a continuing fictional storyline (Sarah Okonkwo's AI-native firm "Candor" vs. Marcus Chen's traditional firm "Stratton Hewitt") — evidenced by the paired chapter files (`01-ai-native-psf.tex` + `01-ai-native-psf-sarah.tex`, the narrative rewrites that `main.tex` actually includes) and `notes/character-bible.md`, `notes/narrative-timeline.md`.

**Status** (CLAUDE.md, April 2026): "First draft complete → Review and revision phase." STATUS.md records three full review/revision iterations completed 2025-12-30 with all 14 chapters + 7 appendices marked COMPLETE across Review/Assess/Revise/Polish/Integrate; final build 340 pages. Four further review rounds live in `docs/review*`. Not yet published; cover art in concept/production (`docs/COVER_ART.md`, Blender renders in `artifacts/cover/`).

**Formats**: full book PDF (`latex/main.pdf`, LuaLaTeX, US Trade 6×9 with in-document cover); **serialized chapter PDFs** for weekly release (`latex/serial/build-chNN.pdf`); numerous standalone previews (`prologue-standalone.tex`, `part1-standalone.tex`, `main-sampler.tex`, `preview-ch1-6.tex`, per-chapter Sarah standalones); presentation deck (`book-slides.tex`).

## 2. Directory Layout

```
ai-professional-services-book/
├── CLAUDE.md                  # AI-assistant guide: status, workflow, cardinal prose rules, tools, build commands
├── STATUS.md                  # Iteration-by-iteration review/revision tracker with per-chapter gates
├── README.md                  # Overview + project structure
├── pyproject.toml / uv.lock / .venv/   # uv-managed Python project (deps mostly via PEP 723 script headers)
├── chapter-data.csv           # NARRATIVE CANON DATABASE (see §4b): per-chapter in-story dates, revenue,
│                              #   headcount, margins, engagements, characters — continuity source of truth
├── download_references.py     # Fetches industry-report PDFs into references/ (see §4)
├── references/                # Downloaded source PDFs; gitignored (*.pdf excluded, .gitkeep kept)
├── artifacts/
│   ├── cover/                 # pyramid_cover_art.{png,jpg} — Blender-rendered cover art
│   └── mockups/               # HTML mockups (os-1-vs-os-2-stacks.html)
├── notes/                     # Working corpus: outlines/, drafts/ (markdown chapter drafts), research/,
│   │                          #   reviews/, interviews/, character-bible.md, timeline*.md,
│   │                          #   chapter-summaries.md, frameworks-reference.md, expansion plans
├── docs/                      # Documentation hub + review rounds
│   ├── README.md, workflow-guide.md, style-guide.md, STYLE-AI-TELLS.md, STYLE-CRAFT.md,
│   │   prose-editing-checklist.md, latex-guide.md, chapter-architecture-guide.md, COVER_ART.md,
│   │   AI-TELLS-AUDIT.md, CHANGES-SIGNOFF.md, CHANGES-SIGNOFF-2.md
│   ├── review/                # HTML sign-off tool: build_review.py, apply_changes.py, index.html, changes.js
│   ├── review-02/             # critical reads, story-arc analysis, style-violations JSON, change diary
│   ├── review-03/             # fact-check findings (legal/regulatory, market data)
│   └── review-04/             # continuity-ledger.md, rule-audit.md, serial-read.md
├── scripts/                   # check_style.py, check_prose.py, book_stats.py, sample_text.py,
│                              #   generate_pyramid_cover.py (+ v1/v2 backups) — Blender cover generator
├── .claude/agents/            # 8 subagent definitions for the writing pipeline (see §8)
└── latex/
    ├── main.tex               # Root book (lualatex), main-original.tex (pre-narrative version)
    ├── Makefile               # pdf/quick/validate/clean … (lualatex + biber)
    ├── preamble/              # {main,packages,colors,tikz,boxes,styling,commands,headers,
    │                          #  dividers-modern,part-dividers-modern}.tex
    ├── chapters/              # prologue + 14 chapters ×2 variants (-sarah = canonical) + appendices a–g
    ├── front-matter/          # half-title, title-page, copyright, dedication, ai-disclosure, preface,
    │                          #   how-to-read, cover/ (cover-standalone.pdf — Blender render, via \includepdf)
    ├── back-matter/           # about-author, back-cover
    ├── serial/                # Weekly-release system: build-chNN.tex wrappers, serial-preamble.tex,
    │                          #   serial-cover.tex, serial-roadmap.tex, serial-teaser.tex, serial-backmatter.tex, Makefile
    ├── bib/refs.bib           # Bibliography (35 entries)
    └── figures/, many ch*-fig-*.tex/pdf, candor-* brand/diagram experiments, book-slides.tex
```

**Reference-management workflow analysis** (references/ + download_references.py + chapter-data.csv):
- `download_references.py` is a zero-dependency stdlib fetcher: a curated `DOWNLOADS` list of `(url, filename, description)` tuples (McKinsey, Altman Weil, CLOC, Georgetown/TR reports), browser-mimicking headers, `%PDF` magic-byte validation to reject HTML error pages, 1s politeness delay, success/failure summary, and — importantly — a commented **"MANUAL DOWNLOAD REQUIRED"** section listing registration-gated reports with URLs and instructions. Downloaded PDFs land in `references/` which is **gitignored** (`.gitignore:69-70`: `references/*.pdf` / `!references/.gitkeep`) so heavyweight sources are reproducible-by-script rather than committed.
- The script's docstring encodes a source-of-truth hierarchy: "These PDFs are HISTORICAL REFERENCES (2020-2024)... PRIMARY SOURCES for Q3/Q4 2025 market developments are in the wiki" (the author's personal wiki at `michaelbommarito.com/src/content/wiki/legal/alternative-structures/`, ~150+ primary references). So: wiki = live research base, references/ = frozen background PDFs, `latex/bib/refs.bib` = only what is actually cited.
- `chapter-data.csv` is **not** citation data — it is a 15-row narrative continuity ledger with columns `Chapter, Title, In-Story Date, Candor Revenue, Candor Headcount, Candor EBITDA Margin, Stratton Hewitt Revenue, …, Marcus / SHC Narrative Notes, Other Firms & Engagements, Characters`. Every number a character states in-story (run rates, margins, valuations, headcounts, deal sizes) is tracked per chapter so later chapters stay consistent. Paired with `docs/review-04/continuity-ledger.md`. This is a genuinely novel artifact worth templating for any narrative-driven book.

## 3. LaTeX Pipeline

- `latex/main.tex`: `\documentclass[11pt,twoside,openright]{book}`; header comment: "US Trade format: 6" x 9" / Build: lualatex main.tex (or xelatex main.tex)". Modular preamble via `\input{preamble/main}`; `\addbibresource{bib/refs.bib}`; same matter choreography as the law-finance minibook (Alph-numbered in-document cover, half-title/title/copyright/dedication, **`ai-disclosure.tex`** front-matter page, unnumbered Prologue with manual `\addcontentsline`+`\markboth`, 4 `\part`s, `\appendix` kept in mainmatter "for proper numbering", `\printbibliography[title={References}]`, about-author, back cover). Uses the same `\usefrontmatterstyle`/`\enablecleardoublepage` machinery.

**Geometry** (`latex/preamble/packages.tex:12-21`, verbatim):

```latex
\usepackage[
  papersize={6in,9in},
  inner=0.875in,      % Gutter margin (for binding)
  outer=0.625in,      % Outside margin
  top=0.75in,
  bottom=0.75in,
  includehead,
  includefoot,
  footskip=0.35in
]{geometry}
```

**Fonts** — the big departure from the sibling (Libertinus): classic trade-book pairing via fontspec (verbatim, `packages.tex:37-59`):

```latex
\ifxetex
  \usepackage{fontspec}
  \usepackage{unicode-math}
  \setmainfont{EB Garamond}[
    Scale=1.0,
    Ligatures=TeX,
    Numbers=OldStyle
  ]
  \setsansfont{Source Sans Pro}[Scale=MatchLowercase]
  \setmonofont{Noto Sans Mono}[Scale=MatchLowercase]
  \setmathfont{Latin Modern Math}
\else\ifluatex
  ... identical block ...
\fi\fi

\ifpdftex
  \usepackage{ebgaramond}
  \usepackage{ebgaramond-maths}
\fi
```

Plus **Unicode fallback families** — a solution the first book never had:

```latex
\newfontfamily\symbolfont{DejaVu Sans}[Scale=MatchLowercase]
\newfontfamily\cjkfont{Noto Serif CJK SC}[Scale=0.95]
\newfontfamily\emojifont{Noto Color Emoji}
\newcommand{\cjk}[1]{{\cjkfont #1}}
\newcommand{\yes}{{\symbolfont\char"2713}}
\newcommand{\no}{{\symbolfont\char"2717}}
\AtBeginDocument{\let\oldcheckmark\checkmark
  \renewcommand{\checkmark}{{\symbolfont\char"2713}}}
```

(The recurring "Font (box chars)" build warnings in STATUS.md are what motivated this.)

**Microtype, fully armed** (engine-conditional; LuaLaTeX branch verbatim):

```latex
\usepackage[
  activate={true,nocompatibility},
  final,
  tracking=true,
  expansion=true,
  protrusion=true,
  factor=1100,
  stretch=10,
  shrink=10
]{microtype}
% Letterspacing for small caps - elegant spacing for heading use
\SetTracking{encoding=*,shape=sc}{60}
```

**Traditional book paragraphing** (vs. the textbook's parskip):

```latex
\setstretch{1.05}
\setlength{\parindent}{1.5em}
\setlength{\parskip}{3.2pt plus 1pt minus 1pt}
```

Justification tuning: `\tolerance=2000 \pretolerance=150 \hyphenpenalty=50 \exhyphenpenalty=50 \emergencystretch=3em \hbadness=2000`; widows/orphans `\widowpenalty=10000 \clubpenalty=10000 \brokenpenalty=4991`; `\raggedbottom`.

**Chapter/part/section styling** (`preamble/styling.tex`) — a designed "Progressive Design Language," documented in a table in-source (Part: Huge/Bold/tracked small caps slate-800 → Chapter: LARGE italic slate-700 → Section: 13.5pt tracked small caps, *no bold* → Subsection: italic → Subsubsection: bold small). Chapter heads are right-aligned display style with hairline rules:

```latex
\titleformat{\chapter}[display]
  {\normalfont\raggedleft}
  {%
    {\color{slate-300}\rule{3cm}{0.5pt}}\\[12pt]%
    {\color{text-muted}\scshape\lsstyle\large Chapter \thechapter}%
  }
  {8pt}
  {\LARGE\itshape\color{slate-700}}
  [\vspace{8pt}{\color{slate-300}\rule{5cm}{0.5pt}}]
```

Parts get a centered TikZ `\partdivider` (line–dot–line). **Drop caps** via `lettrine` with house defaults (`DefaultLines=3`, `\renewcommand{\LettrineFontHook}{\color{primary}}`). **Scene breaks**: `preamble/dividers-modern.tex` defines ten alternatives (`\scenebreakminimal`, `dots`, `binary`, `geometric`, `asymmetric`, `code`, `rule`, `double`, `tech`, `asterisk`) and `styling.tex`/`commands.tex` alias the chosen one (`\let\scenebreak\scenebreakgeometric`) — swap one `\let` to restyle the whole book. Ornaments via `pgfornament` (`[object=vectorian]`), icons via `fontawesome5`.

**Headers** (`preamble/headers.tex`): same three-page-style architecture as the sibling minibook but restyled — no head rules, muted italics:

```latex
\fancypagestyle{mainmatterstyle}{%
  \fancyhf{}
  \fancyhead[LE]{\small\thepage\quad\itshape\color{text-muted}\booktitle}
  \fancyhead[RO]{\small\itshape\color{text-muted}\leftmark\quad\thepage}
  \renewcommand{\headrulewidth}{0pt}
  ...
}
```

**hyperref/cleveref/caption/enumitem/booktabs/tabularx** blocks are identical in spirit to the sibling (colorlinks with `linkcolor=primary, citecolor=accent`, `plainpages=false, pdfpagelabels=true`). `pdfpages` is loaded — used to `\includepdf` the Blender cover (`front-matter/cover/cover-standalone.pdf`); CLAUDE.md: "Always use this file via `\includepdf` for covers; never recreate it in TikZ."

**Bibliography setup** (verbatim, `packages.tex`, identical to the sibling — confirmed house standard):

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
...
\renewcommand*{\bibfont}{\small}
\setlength{\bibitemsep}{0.5em}
\setlength{\bibhang}{1.5em}
```

## 4. Bibliography / Citations Workflow

- `latex/bib/refs.bib` has **35 entries** — deliberately small. This is a trade book: citations (`\parencite`) back only load-bearing market facts (Am Law 100 data, Eve/Eudia funding rounds, UK ABS statistics, Axiom Ince collapse, Slater & Gordon writedown — per STATUS.md Iteration 2 log: "Added bibliography entries for key sources... Build now 338 pages with References section").
- The research mass lives *outside* the bib: the personal wiki (primary, current), `notes/research/*.md` (synthesized agent-research docs like `agent-synthesis-*.md`, `market-developments-q3q4-2025.md`, `chapter-2-economics-data.md`), and `references/` PDFs fetched by `download_references.py` (see §2 for full analysis of the script: curated URL list, PDF magic-byte validation, gitignored output, manual-download appendix).
- **Verification is a dedicated review round**: `docs/review-03/` contains `fact-check-findings-legal-regulatory.md`, `fact-check-findings-market-data.md`, `fact-check-issues.md`. STATUS.md logs concrete factual corrections (e.g., "Fixed California AB 931 characterization (fee-sharing restriction, not full freeze)", "Added Texas Opinion 706 nuance").
- **`chapter-data.csv`** covers the *fictional* numbers the same way the bib covers real ones — a per-chapter canon of every in-story financial figure, date, and character so the narrative stays internally consistent (backed by `docs/review-04/continuity-ledger.md` and `notes/character-bible.md`). Appendix G (`appendix-g-methodology.tex`, "Data Sources and Methodology") discloses sourcing to readers.

## 5. Build Automation

- **`latex/Makefile`**: adapted from the sibling's root Makefile but `LATEX = lualatex`, `LATEXMK_FLAGS = -lualatex -use-make`. Targets: `pdf` (latexmk or manual lualatex→biber→lualatex→lualatex), `quick`, `validate`, `clean`, etc. Comment: "use lualatex for fontspec/modular preamble".
- **`latex/serial/Makefile`**: per-installment targets `prologue ch01 … ch14`; each runs from the parent dir so paths resolve: `cd .. && lualatex --output-directory=serial serial/build-chNN.tex` (+ biber + second pass for chapters with citations).
- **`scripts/`** (Python; note the **PEP 723 inline dependency headers** — `# /// script … dependencies = [...] ///` — executed via `uv run`, some with `#!/usr/bin/env -S uv run --script` shebangs):
  - `check_style.py` (deps: rich) — "Check LaTeX files against style guides (STYLE-AI-TELLS.md, STYLE-CRAFT.md)": banned words/phrases, sentence & paragraph length, **em-dash density (max 1 per paragraph)**, AI-tell patterns ("This disease", gerund openers, filler transitions), Flesch-Kincaid estimate, opt-in contraction check.
  - `check_prose.py` (deps: pydetex, nupunkt) — n-gram repetition (3–6 word phrases across the book), monotonous sentence starts, exact/near-duplicate sentences across files, adjacent repetition; `--format grep` for pipeline use.
  - `book_stats.py` (deps: pylatexenc, nltk) — word/sentence/paragraph counts per chapter, environment counts (tables/figures/boxes/TikZ), citations/labels/cross-refs, estimated pages; `--json`/`--markdown` output (raw JSON snapshots are checked into `docs/review-02/book-stats-raw.json`).
  - `sample_text.py` (zero deps) — random 3–5-paragraph samples for spot-editing review, seedable for reproducibility.
  - `generate_pyramid_cover.py` (+ two versioned backups) — **Blender headless cover generator**: `/opt/blender/blender --background --python scripts/generate_pyramid_cover.py -- --test` (600×800/32 samples) vs. full render (2400×3200/256 samples), output to `artifacts/cover/`.
- `pyproject.toml` is nearly empty (`requires-python = ">=3.13"`, no deps) — dependencies are carried per-script via PEP 723, which is the cleaner pattern for a template.
- CLAUDE.md wires tools into workflow gates, e.g. "Before ANY revision work, run: `grep -c '\\begin{itemize}' latex/chapters/*.tex` ... It must DECREASE, not increase."

## 6. Sub-products (`artifacts/`, `latex/serial/`, standalones)

- **`artifacts/cover/`** — final rendered cover art (`pyramid_cover_art.png/jpg`) produced by the Blender script; concept documented in `docs/COVER_ART.md` ("The Cravath Pyramid": metallic/circuit base = automated leverage work, organic apex = human judgment; Blender Principled BSDF band-mixing pipeline described). The render is then wrapped as `latex/front-matter/cover/cover-standalone.pdf` and `\includepdf`-ed everywhere.
- **`artifacts/mockups/`** — HTML design mockups (e.g., `os-1-vs-os-2-stacks.html`) used to prototype figures before TikZ.
- **`latex/serial/`** — the **weekly serialization system**: for each installment, a ~10-line-metadata wrapper `build-chNN.tex` composes `serial-cover.tex` (cover art) → chapter card (TikZ) → `serial-roadmap.tex` (book roadmap with "you are here") → the *same* chapter `.tex` used by the main book (single source of truth, explicitly called out in CLAUDE.md) → `serial-teaser.tex` ("Coming Next Week") → `serial-backmatter.tex` (About the Authors). This is what produced the `trailers/ai-professional-services-prologue.pdf` found in the sibling repo.
- **Standalone previews/samplers** in `latex/`: `prologue-standalone.tex`, `part1-standalone.tex`, `preview-ch1-6.tex`, `main-sampler.tex`, per-chapter `chapterN-sarah-standalone.tex`, plus `book-slides.tex` (a slide deck) and many named-figure experiments (`candor-os-logos.tex`, `juris-dictum-logos.tex`, `ch11-fig-*.tex`) — figures developed as standalone docs then included.

## 7. Metadata & Publishing

- **STATUS.md** is a dedicated tracker: iteration summary table, per-chapter × per-phase (Review/Assess/Revise/Polish/Integrate) checkbox matrix for prologue + 14 chapters + 6 appendices, an accomplishments log per iteration, an **Issues Log** table (date/chapter/issue/resolution), and **Build Validation** tables (date/status/pages/warnings). This is the best "book project status" document in either repo.
- No KDP/ISBN metadata yet (pre-publication); cover process is documented (COVER_ART.md) and reproducible (Blender script). Front matter includes an **`ai-disclosure.tex`** page — an AI-authorship disclosure, worth carrying into a template.
- Author metadata in `main.tex` `\hypersetup{pdfauthor={Daniel Martin Katz, Michael J. Bommarito II, Jillian Bommarito}, ...}`.

## 8. Style / Craft / AI-tone Guides — the standout asset

The docs/ hub is a full editorial operating system:

- **`docs/STYLE-AI-TELLS.md`** — a taxonomy of synthetic-prose patterns in five parts: *Syntactic tells* (the "This" disease, gerund openers, "As X, Y" constructions, triple structures, filler transitions, hedging clusters, false balance, nominalization, rhetorical-question setups, summary openers), *Structural tells* (predictable paragraph, intro-body-conclusion trap, symmetrical sections, exhaustive lists), *Semantic tells* (superlative piles, value-neutral praise, weasel citations, temporal waffling), *Word-level tells* (extended banned words & phrases — 40+ including delve, landscape, leverage, navigate, unlock, robust, paradigm, streamline, synergy, holistic, ecosystem, stakeholder), and *Detection heuristics* ("If-Then-Delete" test, "Who Said This?" test, "10% adverb budget"). Directly machine-enforced by `check_style.py`.
- **`docs/STYLE-CRAFT.md`** — positive craft rules with a notable philosophy section: "Rules Are Flags, Not Orders" and the read-aloud test; sentence rhythm ("Earn your short sentences", no 3+ consecutive <12-word sentences), **em-dash discipline** ("does the construction do work?" — earned pairs allowed, 3+ per paragraph is the disease), contraction policy (Garner's test; in dialogue contractions are *characterization*: "Marcus and David do not contract... Sarah, Maya, Jennifer, and James do"), fragment permission.
- **CLAUDE.md cardinal rule**: "PROSE, NOT LISTS. This book is prose, not a slide deck. This is the #1 quality requirement" — with a measurable gate (itemize count must decrease; "All 14 main chapters have 0 itemize environments"). Banned transitions list ("However," "Furthermore," "Moreover," …). Voice: "we"/"you", never "I"/"one". Chapter contract: "Opening → Framework → Decision → Value Implications → Takeaways"; "Every chapter delivers: Named framework + Decision to make + Economics connection."
- **`docs/workflow-guide.md`** — the six-phase pipeline `OUTLINE → DRAFT → REVIEW → REVISE → POLISH → INTEGRATE`, each phase with a named agent and an explicit **quality gate**; includes guidance on running agents in parallel. "Critical Rule: Never skip REVIEW or POLISH."
- **`.claude/agents/`** — 8 subagent definitions with YAML frontmatter (`tools: Read, Grep, Glob`, `model: sonnet`): `outline-iteration`, `draft-from-outline`, `critical-review`, `revision-from-feedback`, `example-case-refinement`, `style-guide-conformance`, `compression-tightening`, `flow-improvement`. `critical-review.md` defines **persona-based review**: four reader personas (managing-partner 45–60 skeptical decision-maker; tech-lead implementer; skeptical-partner 50–65 resistant; junior-associate end user) plus editorial personas (copy-editor, developmental editor), each with age, concerns, and review focus. Reviewers "do NOT make edits—provide feedback for the revision agent."
- Also: `docs/chapter-architecture-guide.md` (per-chapter visual-element requirements: 1 TikZ framework diagram, 2–4 boxes, drop cap, 1–2 scene breaks), `docs/style-guide.md`, `docs/prose-editing-checklist.md` (evolved from the sibling's), `docs/latex-guide.md` (box environments, label conventions `ch:`/`app:`, table recipes), `notes/character-bible.md` + timeline docs for narrative consistency.

## 9. QA / Review Workflow

Multi-round, artifact-preserving review:

- **Round 1–3 (STATUS.md)**: banned-word purges (50+ "leverage" instances), factual corrections, bullet→prose conversion (57 lists in Ch10 alone), citation additions, all logged with page-count deltas and build validations.
- **`docs/review/` — an HTML sign-off tool**: `build_review.py` "Parse CHANGES-SIGNOFF.md into changes.js for the HTML review page. For each change we also pull the surrounding paragraphs from the real source .tex file so the reviewer can see the edit in context" (3 paragraphs of context each side); `index.html`+`changes.js` render an accept/reject UI; `apply_changes.py` then applies accepted edits — "Dry-run by default... Pass --write to apply. Auto-applies exact single-span replacements... Multi-part 'approx' edits are listed for manual handling", with explicit `REJECTED`/`SUPERSEDED`/`APPROX` ID sets and verbatim (file, old, new) tuples for manual edits. A human-in-the-loop batch-edit pipeline for AI-proposed changes — highly template-worthy.
- **review-02**: critical reads in thirds (prologue–ch3, ch4–8, ch9–14), story-arc analysis, futurist research, machine-readable `style-violations-per-chapter.json`, `book-stats-raw.json`, `check-prose-raw.json`, change diary.
- **review-03**: fact-checking (legal/regulatory + market data findings, issues list).
- **review-04**: `continuity-ledger.md` (narrative canon audit vs. chapter-data.csv), `rule-audit.md` (style-rule compliance), `serial-read.md` (reading the book as serialized installments).
- Automated gates: `check_style.py` / `check_prose.py` / `book_stats.py` before-and-after each revision pass; itemize-count grep gate; `make validate`.
- `docs/AI-TELLS-AUDIT.md` + `CHANGES-SIGNOFF{,-2}.md` — audit findings converted into numbered, individually sign-off-able edits.

## 10. Verdict — Reusables & Pitfalls

**Take for the master template:**
1. **The editorial OS**: STYLE-AI-TELLS.md + STYLE-CRAFT.md + `check_style.py`/`check_prose.py` enforcement + the six-phase workflow with named `.claude/agents/` subagents and persona-based `critical-review`. This is the most complete AI-authoring quality system in either repo and is book-agnostic with minor edits (character names, banned-word tuning).
2. **The review sign-off pipeline** (`docs/review/`): audit → CHANGES-SIGNOFF.md → HTML accept/reject UI with source context → dry-run `apply_changes.py --write`. Solves the "AI proposed 100 edits, human must approve each" problem.
3. **PEP 723 script headers + uv** for all tooling (no venv management), `book_stats.py --json` snapshots per review round.
4. **Typography**: EB Garamond/Source Sans Pro/Noto Sans Mono fontspec stack with OldStyle numerals, aggressive microtype (+`\SetTracking{...shape=sc}{60}`), Unicode fallback families (`\symbolfont`/`\cjk`/`\emoji`, `\checkmark` redefinition), lettrine drop caps, the pluggable `\scenebreak*` divider library, progressive heading hierarchy, ruleless italic running heads.
5. **Serialization system** (`latex/serial/`): tiny metadata wrappers around single-source chapter files → weekly installment PDFs with cover/roadmap/teaser — doubles as a trailer generator for cross-promo (see sibling's `trailers/`).
6. **STATUS.md format** (iteration tables, per-chapter phase matrix, issues log, build-validation log) and **chapter-data.csv continuity ledger** for any narrative or example-heavy book.
7. `download_references.py` pattern: scripted, validated, gitignored source-PDF acquisition with a documented manual-download appendix.
8. `ai-disclosure.tex` front-matter page; Blender-scripted cover generation with test/full render modes.

**Pitfalls:**
- **Bibliography is thin relative to claims** (35 entries for a data-heavy 340-page book); the compensating fact-check rounds are manual. A template should pair the trade-book "cite only what's load-bearing" stance with the sibling's `urldate`+relevance-note discipline.
- **Duplicate chapter variants** (`NN-*.tex` and `NN-*-sarah.tex` both kept; only `-sarah` is included) plus `main-original.tex` and `removed-fig-*.tex` — dead source accumulates in `latex/`; build artifacts (main.log/.bbl/.fls, many experiment PDFs) are committed alongside source. A template needs a `latex/attic/` convention and stricter gitignore.
- `docs/` accumulated four inconsistently named review dirs (`review`, `review2`, `review-02`, `review-03`, `review-04`) — standardize round naming up front.
- `pyproject.toml` is vestigial ("Add your description here") while real deps live in script headers — fine, but decide one way in the template.
- Makefile inherited from the textbook still references non-existent `sections/` in its dependency rule.

**Unique to this repo**: narrative continuity tooling (chapter-data.csv, character bible, continuity ledger), the anti-AI-tell style regime with automated enforcement, the persona-review agents, the HTML change sign-off tool, LuaLaTeX+EB Garamond trade design, and the serial/weekly-release build system.
