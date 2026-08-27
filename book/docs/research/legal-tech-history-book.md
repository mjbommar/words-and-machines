# Research Report: legal-tech-history-book

Source: `/home/mjbommar/projects/personal/legal-tech-history-book`
Reviewed: 2026-07-06

---

## 1. Purpose & Status

**Book:** *From Clay to Code: How Legal Technology Shaped the Modern World* — Michael Bommarito. A trade-nonfiction history of legal technology as "the material infrastructure of authority," from the Egyptian Nilometer to autonomous AI agents (2026). 20 chapters in 5 Parts, target ~85,500 words / ~340 pages.

**Status (as of June 2026 commits):** Mid-production draft. All 20 chapters exist as expanded Markdown drafts (originally ~850-word skeletons, target 4,000 words each). Recent git history shows serious QA passes:

```
d301fdb Audit all references: remove 9 hallucinated citations, fix ~35 metadata errors
4c05963 Resolve flagged claims from June 2026 review; rebuild PDF + EPUB
33b810f June 2026 currency review: update dated claims, log provenance, copy edit
c9e5ec0 Editorial pass: fact-check, copy-edit, and flow across all chapters
62cc120 Add public-draft LaTeX build mode
```

**Formats produced:** print-oriented PDF (`latex/build/main.pdf`), a public draft PDF build with disclaimer banners (`make draft`), and an EPUB (`epub/book.epub`) built with a custom Python LaTeX→EPUB converter. No KDP/print-release artifacts yet (contrast with the RFC book).

---

## 2. Directory Layout (annotated)

```
legal-tech-history-book/
├── CLAUDE.md                 # 22 KB master AI-authoring instruction file (see §7)
├── AGENTS.md                 # Codex/agent instructions: knowledge-graph workflow (RDF/SKOS/OWL)
├── GEMINI.md                 # Gemini CLI variant of project context (earlier phase snapshot)
├── TODO.md                   # Short active task list
├── README.md                 # One-paragraph public premise
├── pyproject.toml            # uv project: playwright, TexSoup, lxml, typer, rich; epubcheck dev-dep
├── uv.lock
├── .claude/agents/           # 27 writing/research subagent definitions (*.md with frontmatter)
├── docs/                     # PLAN.md, style_guide.md, prose_craft_guide.md,
│                             #   chapter_expansion_process.md, cite-check.md
├── drafts/                   # 20 chapter drafts + part-title-pages.md (Markdown, canonical prose source)
├── outline/                  # book-structure.md, structure_forms.md (musical forms per chapter)
├── notes/                    # initial-notes/ (gemini/gpt/grok brainstorms),
│   ├── reviews-01/           #   simulated reviewer reports (acquisitions editor, general reader…)
│   └── review-02/            #   simulated FT/NYT/NYRB/WSJ reviews + 11 remediation plans + synthesis
├── research/                 # per-chapter dirs ch-01..ch-20, plus chronology/, countries/,
│                             #   sources/, technology/, structure/ (KG), _shared/, _templates/
├── scripts/                  # convert_drafts_to_latex.py, pandoc-fixes.lua, scaffold_chapters.py,
│                             #   verify_citation.py, build_kg.py, research_*.py
├── latex/                    # book production (see §3)
│   ├── main.tex, Makefile
│   ├── preamble/             # main, packages, colors, boxes, styling, headers, commands, preamble
│   ├── chapters/             # generated .tex from drafts/ via pandoc
│   ├── bib/refs.bib
│   ├── build/                # latexmk output (main.pdf)
│   └── figures/, front-matter/, back-matter/ (mostly .gitkeep — front matter is inline in main.tex)
└── epub/
    ├── converter/            # custom Python LaTeX→XHTML→EPUB package (cli, parser, renderer,
    │                         #   handlers/{macros,environments,figures,math,references})
    ├── template/             # content.opf, nav.xhtml, toc.ncx, cover/title/copyright.xhtml,
    │                         #   stylesheet.css, fonts/ (EB Garamond + Noto Sans Mono woff2)
    ├── output/               # generated per-chapter XHTML
    ├── META-INF/container.xml, mimetype
    └── book.epub
```

**Content pipeline:** `drafts/*.md` (canonical) → pandoc → `latex/chapters/*.tex` → (a) lualatex PDF, (b) custom converter → XHTML → EPUB. Markdown is the source of truth; LaTeX chapters are generated.

---

## 3. LaTeX Pipeline

### Document class & build

`latex/main.tex`:

```latex
\documentclass[11pt,twoside,openright]{book}
\input{preamble/main}
\addbibresource{bib/refs.bib}
```

Built with `latexmk -lualatex` (fontspec required). Biber bibliography. Two compile modes via pre-TeX `\def`s:
- `\BleedMode` — print-ready expanded canvas
- `\DraftMode` + `\DraftDate` — public draft: banner on every page, red "DRAFT MANUSCRIPT" on the title page, and an auto-inserted disclaimer page ("Do not cite this draft… redistribution not permitted"), plus DRAFT markers injected into PDF metadata:

```latex
pdftitle={From Clay to Code: ...\ifdefined\DraftMode\space(DRAFT --- \DraftDate)\fi},
```

`latex/Makefile` (complete, small):

```make
DRAFT_DATE := $(shell date +'%B %Y')
pdf:
	mkdir -p build
	latexmk -lualatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
draft:
	mkdir -p build-draft
	latexmk -lualatex -interaction=nonstopmode -halt-on-error \
	  -output-directory=build-draft \
	  -usepretex='\def\DraftMode{1}\def\DraftDate{$(DRAFT_DATE)}' \
	  main.tex
```

The `-usepretex` trick for injecting mode flags without editing source is clean and template-worthy.

### Modular preamble

`latex/preamble/main.tex` loads components in dependency order:

```latex
\input{preamble/packages}   % geometry, fonts, microtype, biblatex...
\input{preamble/colors}     % layered Tailwind-based color system
\input{preamble/boxes}      % tcolorbox environments
\input{preamble/styling}    % titlesec chapter/part/section + titletoc
\input{preamble/headers}    % fancyhdr page styles
\input{preamble/commands}   % \keyterm, \scenebreak, \pullquote, hypersetup
```

(There is also a stray minimal `preamble/preamble.tex` — a pandoc-standalone shared preamble; only `preamble/main.tex` is used by the book.)

### Trim size / geometry (packages.tex)

```latex
% US Trade size: 6in x 9in (standard for professional/technical books)
\usepackage[
  papersize={6in,9in},
  inner=0.65in,        % Gutter margin (KDP min is 0.5")
  outer=0.525in,       % Outside margin (KDP min is 0.25")
  top=0.75in,          % Top margin (0.75" for headers per KDP)
  bottom=0.75in,
  includehead,
  includefoot,
]{geometry}

\ifdefined\BleedMode
  \geometry{
    paperwidth=6.25in, paperheight=9.25in,
    inner=1in, outer=0.75in,
    top=0.875in, bottom=0.875in, footskip=0.35in
  }
\fi
```

Margins are annotated against KDP minimums — clearly written with Amazon POD in mind.

### Fonts (packages.tex) — quote exact setup

```latex
\ifPDFTeX
  \usepackage[T1]{fontenc}
  \usepackage[utf8]{inputenc}
  \usepackage{lmodern}
\else
  \usepackage{fontspec}
  % CJK fallback for occasional Chinese characters (must be defined before fonts)
  \directlua{
    luaotfload.add_fallback("cjkfallback", {
      "NotoSansCJKsc:mode=node;script=hani;language=dflt;"
    })
  }
  % EB Garamond: Elegant, readable serif for body text
  \setmainfont{EB Garamond}[
    Scale = 1.05,
    Ligatures = TeX,
    Numbers = OldStyle,
    RawFeature = {fallback=cjkfallback},
  ]
  \setsansfont{Source Sans Pro}[ Scale = MatchLowercase, ]
  \setmonofont{Noto Sans Mono}[ Scale = MatchLowercase, ]
\fi
```

Notable: pdfTeX fallback path retained; a **luaotfload CJK fallback chain** so stray Chinese characters (Smart Court chapter) render without wrapping macros.

### Typography & line-breaking

```latex
\usepackage{microtype}
\usepackage{setspace}
\setstretch{1.18}
\setlength{\parindent}{1.5em}
\setlength{\parskip}{0pt}
...
\raggedbottom
\setlength{\emergencystretch}{2em}
\tolerance=1000  \pretolerance=100
\hyphenpenalty=300 \exhyphenpenalty=200
\widowpenalty=10000 \clubpenalty=10000 \brokenpenalty=5000
```

Plus `csquotes` with `\MakeOuterQuote{"}` (ASCII quotes become smart quotes — very handy for pandoc-generated chapters), `needspace`, `emptypage`, `enumitem` global list tuning, `cleveref` with capitalized names.

### Bibliography (packages.tex)

```latex
\usepackage[
  backend=biber, style=numeric-comp,
  maxbibnames=3, minbibnames=1,
  sorting=none, doi=false, isbn=false, url=true, eprint=false
]{biblatex}

% Make citations superscript without brackets
\DeclareCiteCommand{\cite}[\mkbibsuperscript]
  {\usebibmacro{cite:init}%
   \let\multicitedelim=\supercitedelim ...}
```

Superscript endnote-style numeric citations, `\renewbibmacro{in:}{}` to drop "In:", `\small` bibfont — a fully worked pop-science biblatex profile.

### Chapter/part/section styling (styling.tex)

Elegant literary style — right-aligned italic chapter titles with small-caps Roman chapter numbers and a hairline rule:

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
```

Parts use a centered `\chapterornament` (rule–diamond–rule). Sections are colored bold (`\color{primary}`); `\paragraph` is run-in with a period. Headings are wrapped with `\Needspace{5\baselineskip}` etc. to prevent orphaned headings. `titletoc` custom TOC entries with dotted leaders; `tocdepth=1`. Custom `quote` env renders italic in `text-secondary`; custom `\epigraph` is a right-aligned 0.75\textwidth minipage.

### Layered color system (colors.tex)

A 4-layer architecture worth copying wholesale:

```
Layer 1: PRIMITIVES  - Tailwind palette (slate-900..50, blue, green, amber, red, teal)
Layer 2: SEMANTICS   - definition-*, example-*, history-*, key-*, caution-*, note-*
Layer 3: COMPONENTS  - primary, accent, text-primary/secondary/muted, bg-*, border-*
Layer 4: LEGACY      - \colorlet aliases for backward compatibility
```

e.g. `\definecolor{primary}{HTML}{334155} % Slate 700`, `\definecolor{text-muted}{HTML}{64748B}`.

### Boxes (boxes.tex)

tcolorbox environments with smart breaking defaults:

```latex
\tcbset{
  lines before break=3,
  short/.style={unbreakable},
  long/.style={breakable, lines before break=4}
}
```

Environments: `keyfact` (amber left-border, flat), `historybox`, `definitionbox`, `notebox`, `cautionbox` (all titled, `attach boxed title to top left`), `sidebar` (title centered in the top border via `attach boxed title to top center={yshift=-\tcboxedtitleheight/2}`), plus legacy `definition`/`note`.

### Headers/footers (headers.tex)

Documented US-trade conventions in the comments:

```latex
% US Trade Paperback Professional Book Conventions:
%   - Front matter: Roman numerals, folios only (no running heads)
%   - Main matter: Book title (even/verso), Chapter title (odd/recto)
%   - Chapter openers: Plain style (folio bottom center, no running head)
%   - Folios: Top outer corner in running heads
```

Three fancyhdr styles (`frontmatterstyle`, `mainmatterstyle`, `backmatterstyle`) plus a redefined `plain`; `\chaptermark` set, `\sectionmark` disabled. Two very reusable helpers:

```latex
\let\cleardoublepagestd\cleardoublepage
\newcommand{\disablecleardoublepage}{\let\cleardoublepage\clearpage}
\newcommand{\enablecleardoublepage}{\let\cleardoublepage\cleardoublepagestd}
```

used so front matter packs tightly while main-matter chapters open recto.

### Commands (commands.tex)

`\keyterm{}` (bold+primary), `\term{}`, `\acr{}` (fake small caps via `\textsc{\MakeLowercase{...}}`), `\scenebreak` (rule–diamond–rule), `\pullquote{}`, `\historicaldate{}`, `\marginnote{}`, pandoc `\tightlist` compat, and `hypersetup` (colorlinks with palette colors, `bookmarksnumbered`, `pdfpagelabels`).

### Front/back matter

Title page, draft disclaimer, TOC, five `\part` pages (each with a dated epigraph) are **inline in main.tex**; `front-matter/` and `back-matter/` dirs are empty placeholders. Back matter = `\printbibliography[title={References}]` only. No index, no glossary.

### Markdown → LaTeX conversion

`scripts/convert_drafts_to_latex.py` runs pandoc per chapter:

```
pandoc --from gfm --to latex --top-level-division=chapter \
  --lua-filter scripts/pandoc-fixes.lua --no-highlight --wrap=none
```

`scripts/pandoc-fixes.lua` (a) strips leading "Chapter N:" from H1s so chapters aren't double-numbered, and (b) converts paragraphs starting with emphasized `Draft notes:` into LaTeX comments — a neat pattern for keeping editorial notes in drafts without them leaking into output.

---

## 4. EPUB Pipeline

### Tooling

A **custom Python LaTeX→EPUB converter** package at `epub/converter/` (~2,100 LOC): `cli.py` (typer + rich), `parser.py` (TexSoup-based), `document.py` (book/bib loading), `renderer.py` (XHTML emission), `context.py`, `types.py`, and pluggable `handlers/` for `macros`, `environments`, `figures`, `math`, `references`. Registered as a console script in pyproject:

```toml
[project.scripts]
epub-converter = "epub.converter.cli:main"

[tool.uv]
dev-dependencies = ["epubcheck>=0.5.0"]
```

CLI subcommands: `convert` (single chapter → XHTML), `book` (whole book, generates `references.xhtml` from parsed BibTeX with numbered superscript citations), `validate` (runs epubcheck binary or jar, plus accessibility checks; degrades gracefully if epubcheck missing).

### Structure

Hand-maintained EPUB 3 skeleton in `epub/template/`: `content.opf`, `nav.xhtml`, `toc.ncx` (legacy NCX kept for old readers), `cover.xhtml`, `title-page.xhtml`, `copyright.xhtml`, `stylesheet.css`, `fonts/` (EB Garamond woff2 ×6 weights/styles + Noto Sans Mono ×3). Converter output goes to `epub/output/*.xhtml`.

### OPF metadata highlights (`epub/template/content.opf`)

EPUB 3.0 package with `dc:` metadata, MARC relator role refinement, and a full **schema.org accessibility block**:

```xml
<meta property="schema:accessMode">textual</meta>
<meta property="schema:accessModeSufficient">textual</meta>
<meta property="schema:accessibilityFeature">structuralNavigation</meta>
<meta property="schema:accessibilityFeature">tableOfContents</meta>
<meta property="schema:accessibilityFeature">alternativeText</meta>
<meta property="schema:accessibilityHazard">none</meta>
<meta property="schema:accessibilitySummary">This publication conforms to WCAG 2.0 Level AA...</meta>
```

Cover image declared with `properties="cover-image"`; spine includes `linear="no"` for cover and nav; legacy `<guide>` block retained. Placeholders (`[Author Name]`, uuid identifier) remain — less production-final than the RFC book's OPF.

### CSS (`epub/template/stylesheet.css`) — key rules

Deliberately mirrors the LaTeX design ("Beautiful typography for e-readers, matching LaTeX print quality"):

```css
body {
  font-family: 'EB Garamond', Georgia, 'Palatino Linotype', Palatino, 'Times New Roman', serif;
  line-height: 1.5;
  text-align: justify;
  hyphens: auto; -epub-hyphens: auto;
  hyphenate-limit-chars: 6 3 3;
  font-kerning: normal;
  font-variant-numeric: oldstyle-nums proportional-nums;
  font-feature-settings: "kern" 1, "liga" 1, "clig" 1, "onum" 1, "pnum" 1;
  orphans: 2; widows: 2;
}
```

Classic book paragraphing (`p { margin: 0; text-indent: 1.5em; }` with no-indent-after-heading rules), `.chapter-title` right-aligned small-caps matching the print chapter style, `.scene-break::before { content: "\2042"; }` (asterism), epigraph classes with em-dash `::before` on the source.

Two hard-won e-reader lessons encoded in comments:

```css
/* Acronyms ... Using "fake small-caps" approach for Kindle compatibility:
   True small-caps (font-variant-caps) don't work reliably on Kindle
   because the font-size compensation gets stripped by ebook-convert. */
.acr { text-transform: uppercase; letter-spacing: 0.05em; }
```

and night-mode safety: `color: currentColor` on ornaments/links, `code { background-color: transparent; }`, plus a `@media (prefers-color-scheme: dark)` block for code listings.

### Validation

`epub-converter validate book.epub` → epubcheck + accessibility checks; epubcheck also available as a uv dev-dependency.

---

## 5. Build Automation & Scripts

| Script | Purpose |
|---|---|
| `scripts/convert_drafts_to_latex.py` | Pandoc gfm→LaTeX per chapter, with lua filter; CLI accepts custom in/out dirs |
| `scripts/pandoc-fixes.lua` | Strip "Chapter N:" from H1; convert `*Draft notes:*` paras to LaTeX comments |
| `scripts/scaffold_chapters.py` | Create per-chapter drafts/research directory skeletons |
| `scripts/verify_citation.py` | Bibliography QA: random/specific entry checks, `--unused`, `--all`, `--count N` |
| `scripts/build_kg.py` (742 LOC) | Build RDF/SKOS/OWL knowledge graph in `research/structure/kg/` (`uv run --with rdflib`) |
| `scripts/research_chronology.py` / `research_countries.py` / `research_technologies.py` | Research automation that populated `research/chronology|countries|technology` |
| `latex/scripts/cleanup_chapters.py` | Post-conversion LaTeX cleanup |
| `epub/converter/*` | The LaTeX→EPUB converter (see §4) |

**Python env:** uv-managed (`pyproject.toml`, `.python-version` = 3.13, `uv.lock`). Deps: `playwright` (for citation verification against bot-protected sites), `TexSoup`, `lxml`, `typer`, `rich`; dev: `epubcheck`.

Makefile only covers `pdf`/`draft`/`clean`. **Pitfall:** CLAUDE.md references `make validate` and `make wordcount`, which do not exist in this Makefile (they exist in the RFC book's) — doc/Makefile drift.

---

## 6. Metadata & Publishing

- No ISBN yet; EPUB OPF has placeholder author/publisher and a UUID identifier.
- PDF metadata set in `main.tex` `\hypersetup` (title/author/subject/keywords with draft-mode variants).
- Cover: only a `cover.xhtml` + `images/cover.jpg` slot in the EPUB template; no cover generation pipeline (contrast RFC book).
- No release directory; PDFs land in `latex/build/` and `latex/build-draft/`.
- Positioning data lives in CLAUDE.md: audience (legal-tech buyers, investors, compliance professionals), comparable titles with word counts (*Soul of a New Machine* 85k/293pp, *The Code* 75k, *Sapiens* 135k), target 85.5k words ≈ 340pp at 250 wpp.

---

## 7. Style / Craft / AI-Tone Guides

This project's biggest asset. Layered doc system, all in `docs/`:

### CLAUDE.md (22 KB) — the orchestration layer
- Opens with **date/knowledge-cutoff awareness**: "You are operating nearly a year past your pretraining data… When in doubt, search."
- Full project map, "Key Files to Read (in order)" list, current-status table, word-count targets and comparables.
- Documents all **27 agents** with a phase pipeline `RESEARCH → PLANNING → DRAFTING → REVIEW → REVISION → POLISH → VERIFY`, a 14-step "typical full chapter workflow," invocation examples, and a troubleshooting section.
- Inline style quick-reference with BANNED word/phrase lists:

```
delve, landscape, realm, tapestry, crucial, unlock, leverage, utilize,
harness, foster, elevate, streamline, robust, embark, illuminate, unveil,
pivotal, intricate, myriad, plethora, multifaceted, paradigm, ecosystem,
synergy, holistic, best-of-breed, next-generation, cutting-edge
```

- **The Coffee Test:** "After writing a paragraph, ask yourself whether you could say it aloud to a smart colleague without sounding like a vendor pitch deck."

### docs/style_guide.md — "The Voice of the Machine"
Four voice pillars (the "Sapiens" zoom, "Soul of a New Machine" technical drama, "Power Broker" institutional weight, "Ancient Mystery" reveal structure), each with bad/good example pairs. Structural templates as **musical forms** (Sonata A-B-A′, Linear A-B-C, Counterpoint A-B-A-B), mapped per chapter in `outline/structure_forms.md`. Section 5 is a compact **anti-AI-tics catalog**: the "Tapestry" trap, "Crucial" adjectives, the "Delve" verb, the "In Conclusion" summary, the Balanced Hedge, "Not Only/But Also," "today's fast-paced digital world," robotic transitions ("Furthermore/Moreover" → "But/Yet/Meanwhile").

### docs/prose_craft_guide.md (326 lines)
The standout doc: five **mentor authors** (Harari, Caro, Kidder, Graeber, Fukuyama), each broken into The Move / The Pattern / Signature Moves / Emotional Effect / **Application to Legal Tech with before→after rewrites**. Then: combining techniques (opening = Harari zoom + Graeber inversion; middle = Kidder sprint + Caro weight; close = Fukuyama comparison + Harari defamiliarization), **emotional arcs by chapter type** (Origin: Wonder→Strangeness→Recognition; Disruption: Crisis→Struggle→Transformation; Power: Curiosity→Unease→Understanding; Conflict: Tension→Complexity→Open Question), sentence-level craft rules, and a 7-point expanded Coffee Test (Alien/Room/Clock/Myth/Comparison/Stakes/Vendor tests).

### docs/chapter_expansion_process.md (514 lines)
8-phase per-chapter workflow (PREPARE → RESEARCH → ORGANIZE → DRAFT → CITE → REVIEW → FINALIZE → CONTINUE) with exact file paths to read, WebSearch query patterns, and a review-agent run order. Time estimate: 45–90 min/chapter.

### docs/PLAN.md (973 lines)
Master production plan: 8 phases with ASCII progress bars, per-chapter checkbox checklists (each chapter enumerated PREPARE/RESEARCH/DRAFT/CITE/REVIEW/FINALIZE/COMMIT), and quality gates.

### docs/cite-check.md
Bibliography-verification methodology, motivated by a real finding: "Initial spot-check found **50% error rate** in a 4-entry sample." Includes ready-to-paste Playwright snippets (Firefox preferred, Chrome-with-stealth alternative) for verifying sources behind bot detection.

### .claude/agents/ (27 agents)
Markdown agent definitions with frontmatter (`name`, `description`, `tools`, `model:` — drafting/line-editing agents pinned to **opus**). Each agent re-reads CLAUDE.md + style guides before acting. Example (`draft-from-outline.md`): "Write as if explaining to a smart colleague at an industry conference… Think John Carreyrou, Michael Lewis, or Tracy Kidder."

### AGENTS.md
A separate, narrower charter for KG work: canonical **RDF Turtle**, SKOS taxonomy + OWL ontology, stable URIs under `https://legal-tech-history-book.invalid/kg/`, every node needs a label and link back to local evidence. Deterministic builds via `scripts/build_kg.py`.

### research/
20 per-chapter dirs plus cross-cutting `chronology/` (per-year/century files), `countries/`, `sources/` (1000+ source files per CLAUDE.md), `technology/`, `structure/` (KG), `_shared/` (e.g., `bibliography-audit-2026-06.md`), `_templates/`. Documented convention: each chapter dir may contain `bibliography.md`, `entities.md`, `people.md`, `primary-sources.md`, `notes.md`, `timeline.md`.

### notes/reviews — simulated editorial pressure
`notes/reviews-01/` contains AI-simulated reads from an acquisitions editor, developmental editor, general reader, investor reader, accessibility check. `notes/review-02/` goes further: **simulated reviews in the persona of FT, NYT, NYRB, WSJ**, then 11 targeted remediation plans (plan-causal-claims.md, plan-geographic-myopia.md, plan-private-equity.md, plan-middle-pacing.md…) and `synthesis-prioritized.md`. A genuinely novel revision technique.

---

## 8. QA / Review Workflow

- **Review agent sequence** (after drafting): `fact-check` → `style-guide-conformance` → `critical-review` (developmental-editor persona) → `technical-expert-reviewer`; polish with `compression-tightening`, `flow-improvement`, `line-editor`.
- `critical-review` agent supports 7 named perspectives (legal-ops-reader, investor-reader, lawyer-reader, general-reader, copy-editor, developmental-editor, fact-checker).
- **Citation QA:** `scripts/verify_citation.py` (random sampling, unused-entry detection) + `docs/cite-check.md` Playwright workflow. Git history proves it was used ("remove 9 hallucinated citations, fix ~35 metadata errors").
- **EPUB QA:** `epub-converter validate` → epubcheck + accessibility checks.
- Simulated-publication reviews (§7) used as book-level QA gates between drafting rounds.
- Quality gates enumerated in `docs/PLAN.md` phases 4–8.

---

## 9. Verdict

### Best reusable pieces for a master template
1. **The modular preamble architecture** (`preamble/main.tex` + packages/colors/boxes/styling/headers/commands) — clean separation, load-order documented, directly liftable.
2. **The 4-layer Tailwind color system** (primitives → semantics → components → legacy aliases) — makes theming a book a palette swap.
3. **Draft-mode plumbing**: `-usepretex='\def\DraftMode{1}...'` + banner page styles + disclaimer page + metadata suffixes. Perfect for public preview builds.
4. **`\disablecleardoublepage`/`\enablecleardoublepage`** and the documented US-trade header/folio conventions.
5. **The docs stack**: CLAUDE.md orchestrator + style_guide (banned words / AI tics) + prose_craft_guide (mentor authors, before/after) + chapter_expansion_process + PLAN.md checklists. This is the AI-authoring playbook.
6. **27-agent library** in `.claude/agents/` with phase mapping and model pinning (opus for prose) — near-verbatim reusable (the RFC book already forked it).
7. **Citation verification**: verify_citation.py + Playwright fetch recipes + the "assume 50% error rate until proven otherwise" posture.
8. **Markdown→LaTeX pandoc bridge** with the lua filter (chapter-prefix stripping, draft-notes→comments).
9. **EPUB accessibility metadata block** and the Kindle-compat CSS notes (fake small caps, night-mode currentColor).
10. **Simulated-reviewer QA** (FT/NYT/WSJ personas → remediation plans → prioritized synthesis).

### Pitfalls
- **Doc/build drift:** CLAUDE.md advertises `make validate`/`make wordcount` that this Makefile lacks; GEMINI.md and CLAUDE.md describe different project phases/titles (stale snapshots). A template should generate these from one source or keep one canonical AI-instructions file.
- Three overlapping AI-instruction files (CLAUDE.md / AGENTS.md / GEMINI.md) with divergent content; AGENTS.md covers only the KG side.
- Empty `front-matter/`/`back-matter/` dirs while the content lives inline in main.tex — inconsistent with the declared structure.
- Duplicate/vestigial `preamble/preamble.tex`; `epub/output/` and `__pycache__` committed.
- EPUB OPF still has `[Author Name]` placeholders — template should fail loudly on unfilled placeholders.
- Makefile lacks the KDP/cover/grayscale/kindle machinery — this book would need the RFC book's Makefile at publish time anyway.

### Unique to this project
- The RDF/SKOS/OWL research knowledge graph (AGENTS.md + build_kg.py).
- Musical-form chapter structures (Sonata/Linear/Counterpoint) mapped per chapter.
- Mentor-author craft guide with domain-specific before/after rewrites.
- CJK luaotfload fallback in the main font.
