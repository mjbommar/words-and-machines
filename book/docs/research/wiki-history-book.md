# Research Report: wiki-history-book ("The Commons Captured")

Source project: `/home/mjbommar/projects/personal/wiki-history-book`
Reviewed: 2026-07-06. All quotes below are verbatim from the files cited.

---

## 1. Purpose & status

- **Title:** *The Commons Captured* — subtitle *A Critical History of Wikipedia*. Author: Michael J Bommarito II. First Edition 2026.
- **Thesis** (`docs/VISION.md`): the "commercialization paradox" — a copyleft encyclopedia became AI training infrastructure; WMF chose Enterprise revenue over license enforcement ("The license did not fail. The institution did."), with a "political monoculture" capture thesis backed by replicated FEC-donation data (`scripts/fec_monoculture.py`).
- **Status:** effectively publication-ready as of July 2026. `KDP.md` says "Status: July 2026. ISBNs assigned. Covers and interior build-ready." All 22 chapters + prologue/epilogue drafted (~75,000 words per `latex/STATUS.md`, ~52,415 words at the June 2026 repetition baseline), fully fact-checked chapter-by-chapter (`review/finalization-tracker-2026-06.md` shows every unit **DONE** with per-chapter fix notes), multiple editorial passes complete.
- **Formats produced:**
  - Paperback interior: `latex/main.pdf`, US Trade **6×9 in**, no bleed, 259 pp, LuaLaTeX, fonts embedded.
  - Paperback cover: `latex/kdp-cover.pdf`, full wrap 12.893×9.25 in (spine 0.6433 in at 259 pp).
  - EPUB 3: `epub/the-commons-captured.epub`, epubcheck 0 fatals/0 errors/0 warnings, 1800×2700 cover embedded.
  - Public draft PDF (`make draft`): watermarked banner + disclaimer page for the author's website.
- **License:** the book itself is CC BY-SA 4.0 (deliberate symmetry with its subject; see KDP.md item 34 rationale). ISBNs: 979-8-951640-00-0 (paperback), 979-8-951640-01-7 (ebook). Book site: commonscaptured.com.

## 2. Directory layout

```
wiki-history-book/
├── CLAUDE.md                  # AI navigation: thesis arc, frameworks, style quick-ref, script table (210 lines)
├── AGENTS.md                  # Codex/generic-agent mirror of CLAUDE.md (plainer formatting)
├── GEMINI.md                  # Gemini mirror pointing at .gemini/agents/
├── KDP.md                     # Full KDP publication playbook (metadata, pricing, checklists)
├── README.md                  # Human quick-start + build-output table
├── pyproject.toml             # uv/hatchling project; scripts/ packaged
├── main.py                    # stub ("Hello from wiki-history-book!") — uv init artifact
├── .gitignore                 # LaTeX artifacts ignored; !latex/main.pdf etc. whitelisted
├── .claude/agents/            # 13 subagent definitions (Claude frontmatter: tools, model)
├── .gemini/agents/            # Same 13 agents with Gemini tool names (read_file, google_web_search…)
├── docs/                      # Style guides + process docs + editing-pass archives
│   ├── VISION.md              # Thesis, paradox structure, monoculture argument
│   ├── STYLE.md               # Core style guide (Coffee Test, banned words/phrases, A-B-A')
│   ├── STYLE-AI-TELLS.md      # AI-detection avoidance catalog
│   ├── STYLE-CRAFT.md         # Rhythm, transitions, historical-writing craft
│   ├── WRITING-PROCESS.md     # 7-phase workflow (research→verify), agent mapping
│   ├── CHAPTER-REVISION-CHECKLIST.md  # "Nine defects" per-chapter revision rubric
│   ├── REPETITION-AND-FATIGUE-GUIDE.md # Repetition taxonomy + remediation
│   ├── EPUB-TYPOGRAPHY-DIARY.md       # 4-iteration EPUB QA log
│   ├── cite-check.md          # Bibliography verification process (2-level)
│   ├── scripts.md             # Full script documentation (908 lines)
│   ├── sources.md, THEORETICAL-FRAMEWORKS.md, LITERARY-CRAFT-IDEATION.md
│   ├── revise-02/             # Rewrite pass 2: per-chapter plans, agent briefs, REVISION-DIARY.md, iteration-1..3
│   ├── edit-03/               # Full editorial pass 3: per-chapter findings, transitions audit
│   └── epub-qa/               # 3-agent EPUB sweep + consolidated fix list
├── latex/                     # Book production
│   ├── main.tex               # Master doc (front/main/back matter, 5 parts, 22 chapters)
│   ├── Makefile               # pdf/quick/full/bleed/draft/epub/kdp/validate/... (402 lines)
│   ├── preamble/              # packages.tex, colors.tex, styling.tex, commands.tex
│   ├── chapters/              # ch-01..ch-22 + prologue (.tex — LaTeX is the manuscript source of truth)
│   ├── front-matter/          # half-title, title, copyright (PCIP), dedication, epigraph, toc, preface, cover/ (kdp-cover-vars.tex)
│   ├── back-matter/           # epilogue, personal-note, methodology, bibliography
│   ├── bib/refs.bib           # biblatex database (+ refs-generated.bib)
│   ├── kdp-cover.tex          # Full-wrap KDP cover (TikZ)
│   ├── cover-proof.tex / back-cover-proof.tex / cover-fence-studies.tex  # Cover design studies
│   ├── scripts/update_kdp_cover_vars.py  # Spine-width regeneration from page count
│   ├── assets/                # cover art PNG/XCF, ISBN barcode PNG
│   └── STATUS.md              # Production phase tracker + chapter mapping
├── epub/                      # Custom LaTeX→EPUB pipeline
│   ├── converter/             # ~7,000-line Python package (parser, renderer, handler registry)
│   ├── templates/             # stylesheet.css, fonts/ (EB Garamond OTFs), images/cover.jpg
│   ├── scripts/package_epub.py
│   ├── build/                 # generated XHTML (gitignored)
│   └── the-commons-captured.epub
├── outline/                   # TEMPLATE.md, book-arc.md, per-part outline dirs, working/
├── research/                  # _shared/ (people/events/themes/controversies/data), ch-XX-*/, _web/, _history/, _talk/, synthesis/
├── review/                    # Audits: hook, naive-reader, style-coverage, flow, citation-json/-action, rubric-json/-action, finalization tracker
├── scripts/                   # 24 Python utilities (fetch/check/analyze/audit)
├── notes/, todos/             # Planning scraps
└── uv.lock, .python-version, .venv/
```

## 3. LaTeX pipeline

**Engine:** LuaLaTeX via latexmk (Makefile: `LATEX = lualatex`, `LATEXMK_OPTS = -lualatex -interaction=nonstopmode -file-line-error -halt-on-error -recorder`). Document class (`latex/main.tex:18`):

```latex
\documentclass[11pt,twoside,openright]{book}
```

Preamble is split into four files loaded from `main.tex`: `preamble/packages` (geometry, fonts, biblatex, fancyhdr), `preamble/colors` (grayscale palette for print), `preamble/styling` (titlesec/titletoc/caption), `preamble/commands` (semantic macros).

### Geometry (`latex/preamble/packages.tex:14-23`)

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

### Fonts (`latex/preamble/packages.tex:40-66`) — engine-conditional Libertinus

```latex
\ifxetex
    % XeLaTeX: use fontspec directly
    \usepackage{fontspec}
    \usepackage{libertinus}
    \usepackage{libertinust1math}
    % Monospace: Latin Modern Mono (Libertinus Mono not available as system font)
    \setmonofont{Latin Modern Mono}[Scale=MatchLowercase]
\else\ifluatex
    % LuaLaTeX: use fontspec
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

Also: `setspace` with `\setstretch{1.1}`, `\setlength{\parindent}{1.5em}` / `\parskip{0pt}`, `\widowpenalty=10000` / `\clubpenalty=10000`, `\emergencystretch=2em` / `\tolerance=1000`, `csquotes` with `\MakeOuterQuote{"}` (straight quotes auto-curl book-wide — a nice authoring convenience), `lettrine` drop caps, `epigraph`, `quoting`.

### Chapter/section styling (`latex/preamble/styling.tex:14-23`) — titlesec

```latex
\titleformat{\chapter}[display]
    {\raggedleft\normalfont}                          % Right-align the block
    {\scshape\large CHAPTER \chapterword}             % CHAPTER ONE
    {0.5em}                                           % Vertical space between lines
    {\huge\bfseries}                                  % Title formatting

\titlespacing*{\chapter}
    {0pt}    % Left margin
    {50pt}   % Space before (drop from top)
    {40pt}   % Space after (before body text)
```

`\chapterword` spells out chapter numbers as words (packages.tex:222-229, manual `\ifcase` ONE…TWENTY-FOUR because "fmtcount conflicts with titlesec"). Sections are `\large\bfseries\scshape`; subsections `\bfseries\itshape`; parts centered `\Huge\bfseries`. Unnumbered chapters (Prologue/Epilogue) use a hand-rolled `\unnumberedchapter{label}{title}` macro (`commands.tex:115-127`) that mirrors the titlesec look and adds TOC/`\markboth` entries.

**TOC** (`styling.tex:79-106`): `titletoc`, `\setcounter{tocdepth}{0}` (chapters only, fits one page), part entries bold small-caps with no page number, chapter entries with `\titlerule*[0.5pc]{.}\contentspage` dot leaders.

### Headers/footers (`latex/preamble/packages.tex:196-212`) — fancyhdr

```latex
\fancypagestyle{body}{%
    \fancyhf{}
    \fancyhead[LE]{\small\textit{\leftmark}}      % Chapter name on left pages
    \fancyhead[RO]{\small\textit{\rightmark}}     % Section name on right pages
    \fancyfoot[LE,RO]{\thepage}                   % Page numbers on outer edges
    \ifdefined\DraftMode\fancyfoot[C]{\draftbanner}\fi
    \renewcommand{\headrulewidth}{0.4pt}
    \renewcommand{\footrulewidth}{0pt}
}
```

### Hyperref — black links for print (`packages.tex:103-113`)

```latex
\hypersetup{
    colorlinks=true,
    linkcolor=black,
    citecolor=black,
    urlcolor=black,
    pdftitle={The Commons Captured: A Critical History of Wikipedia\ifdefined\DraftMode\space(DRAFT --- \DraftDate)\fi},
    pdfauthor={Michael J Bommarito II},
    ...
}
```

### Bibliography — biblatex/biber, superscript numeric (`packages.tex:135-163`)

```latex
\usepackage[
    backend=biber,
    style=numeric,              % Numeric citations, comma-separated (e.g. 3,4,5)
    autocite=superscript,       % \autocite -> superscript numbers, no brackets
    sorting=none,               % Citations appear in order of first use
    maxbibnames=3,
    minbibnames=1,
    doi=false, isbn=false,
    url=false,                  % URLs clutter print; sources verifiable by title
    eprint=false
]{biblatex}

\DeclareCiteCommand{\cite}[\mkbibsuperscript]
  {\usebibmacro{cite:init}%
   \let\multicitedelim=\supercitedelim
   ...}
```

Plus an `\AtEveryBibitem` block clearing `note/url/urldate/organization/pagetotal/howpublished` — the .bib carries research metadata (URLs, wayback links, notes) but the print bibliography stays clean. Index: `imakeidx` with `\makeindex[columns=2, intoc]`, populated via `\person{Name}` macros.

### Draft/bleed/front-matter machinery

- `\DraftMode` (set by `make draft` via `\def\DraftMode{1}\def\DraftDate{...}\input{main.tex}`) adds: red "DRAFT --- <date> --- Not for Distribution" banner on every page, a full disclaimer page after copyright (main.tex:50-88), and DRAFT markers in PDF metadata. Separate `-jobname=main-draft` keeps artifacts apart.
- `\BleedMode` similarly drives `make bleed` (jobname `main-bleed`).
- Front matter suppresses `openright` blank pages by locally rebinding `\let\cleardoublepage\clearpage` and restoring it before `\mainmatter` (main.tex:41-43, 97). Blank verso pages get `\thispagestyle{empty}` via a patched `\cleardoublepage` (styling.tex:184-190).
- Semantic author-facing macros (`commands.tex`): `\scenebreak` (centered short rule), `\chapterquote{quote}{attribution}` epigraphs, `\person{X}` (small caps + index entry), `\wikirev{oldid}{text}`, `\archive{wayback-path}{text}`, and draft-only `\TODO/\VERIFY/\citeneeded/\controversial/\livingperson` that compile to nothing in final builds.
- KDP print: interior is 6×9 **no bleed**; PDF/X is not used — instead the cover PDF is flattened for prepress via Ghostscript (see §6). `make validate` checks the page box is "432 x 648 pts (6\" x 9\")" and greps the log for undefined references/citations.

**Copyright page** (`latex/front-matter/copyright.tex`) is unusually complete: CC BY-SA 4.0 grant with `\ccbysa` icon (package `ccicons`), trademark disclaimer for the Wikipedia puzzle-globe, AI-assistance disclosure sentence, both ISBNs, and a full self-prepared **PCIP block** (LCSH subjects, LCC `ZA4482 .B66 2026`, DDC 030).

## 4. EPUB pipeline

**Not pandoc.** A custom ~7,000-line Python package at `epub/converter/` (TexSoup + lxml + typer + rich, pulled on demand by uv) parses the *same LaTeX chapter sources* and emits EPUB 3 XHTML, then packages. Two-step flow per `latex/Makefile:200-215`:

```make
EPUB_DIR  = ../epub
EPUB_FILE = the-commons-captured.epub
EPUB_RUN  = uv run --with TexSoup,lxml,typer,rich python -m converter

.PHONY: epub
epub:
	@echo "$(BOLD)$(BLUE)$(ARROW) Converting LaTeX to XHTML (custom converter)...$(RESET)"
	cd $(EPUB_DIR) && $(EPUB_RUN) book \
		../latex/chapters/ -o build/ -b ../latex/bib/refs.bib \
		-f ../latex/front-matter -k ../latex/back-matter -v
	@echo "$(BOLD)$(BLUE)$(ARROW) Packaging EPUB...$(RESET)"
	cd $(EPUB_DIR) && $(EPUB_RUN) epub build/ -o $(EPUB_FILE) -t templates/
```

Reading chapter `.tex` files directly (not `main.tex`) "avoids main.tex's print-only draft-notice block" (Makefile comment).

**Converter structure** (`epub/converter/`): `parser.py` (TexSoup preprocessing, strips print-only commands like `\titlespacing`), `renderer.py` (XHTML emission, footnote finalization), `document.py` (bib parsing — citations resolved from `refs.bib` into a references.xhtml), `context.py`, `types.py`, and a handler registry under `handlers/`: `macros.py`, `environments.py`, `figures.py`, `math.py`, `references.py`, plus book-specific `wiki_macros.py` / `wiki_environments.py` (mapping `\person`, `\chapterquote`, `\scenebreak`, etc. — the project-specific layer cleanly separated from the generic one). `cli.py` (1,263 lines) sorts the spine (`prologue` → `ch-NN`), converts front/back matter, and **generates `content.opf` and `nav.xhtml` dynamically**.

OPF metadata generated in `cli.py` (~line 691):

```xml
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">{identifier}</dc:identifier>
    ...
    <dc:rights>Copyright 2026 {author}. Licensed under Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0).</dc:rights>
    <meta property="dcterms:modified">{modified}</meta>
    <meta name="cover" content="cover-image"/>
    <!-- EPUB Accessibility 1.1 metadata -->
    <meta property="schema:accessMode">textual</meta>
    <meta property="schema:accessModeSufficient">textual</meta>
    <meta property="schema:accessibilityFeature">structuralNavigation</meta>
    ...
```

**CSS** (`epub/templates/stylesheet.css`, 793 lines): embedded EB Garamond (4 OTF faces via `@font-face`) — note the header comment still says "How to Fight a Data Center - EPUB Stylesheet," i.e. the stylesheet was inherited from a sibling book and the ebook uses EB Garamond while print uses Libertinus. Representative rules:

```css
body {
  font-family: "EB Garamond", Georgia, "Times New Roman", serif;
  font-size: 1em;
  line-height: 1.6;
  color: #1f2937;
}
p { margin: 0.5em 0; text-indent: 1.5em; }
p:first-child, h1 + p, h2 + p, ... .scene-break + p, .epigraph + p { text-indent: 0; }
h1.chapter-title { font-size: 1.8em; text-align: right; ... border-bottom: 2px solid #000000; }
.chapter-label { font-size: 0.55em; font-variant: small-caps; letter-spacing: 0.15em; color: #646464; }
```

(Print-indent conventions — first paragraph flush, others indented — reproduced in CSS.)

**Packaging:** `epub/scripts/package_epub.py` and the `epub` CLI command write the zip with `mimetype` first and STORED (uncompressed), then META-INF, then OEBPS — the classic EPUB zip requirement, done in plain `zipfile`.

**Cover:** `make cover-image` renders `cover-proof.pdf` (the standalone 6×9 TikZ front-cover) to a 1800×2700 JPEG via `pdftoppm -r 300 -jpeg -jpegopt quality=95` into `epub/templates/images/cover.jpg`; the same JPEG is uploaded to KDP as the ebook cover.

**Validation & QA:** `epubcheck` after every rebuild, target 0/0/0/0. Two QA artifacts are template-worthy:
- `docs/EPUB-TYPOGRAPHY-DIARY.md` — four iterations of scan→fix-converter→rebuild→revalidate. Classes of defects found: LaTeX command leaks (`\titlespacing` args rendering as text `0pt0pt20pt`), footnote bodies silently dropped (rebuilt as EPUB 3 `epub:type="noteref"`/`aside epub:type="footnote"` popup notes), straight quotes/`--`/`---` unconverted in table cells and captions, chapter-word map ending at 15, epigraph `\medskip` loss.
- `docs/epub-qa/00-FIXLIST.md` — three Sonnet reviewers swept the whole EPUB against LaTeX sources; found e.g. `$\times$` silently dropped ("3.2× more" → "3.2 more", meaning-changing), `<td>` instead of `<th scope="col">` in header rows, a dedication fallback silently substituting stale hardcoded text (fix note: "replace the fallback with a build error, not silent stale text").

## 5. Build automation

### Makefile (`latex/Makefile`, 402 lines)

Targets: `pdf` (latexmk, default), `quick` (single pass), `full` (3 passes + biber), `bleed`, `draft` (public draft with banner via `\def\DraftMode{1}`), `ebook` (large-font PDF from `main-ebook.tex` if present), `epub` (custom converter, see §4), `release` (timestamped copy to `../build/pdf/`), `kdp-interior`, `kdp-cover`, `kdp-cover-vars`, `cover-image`, `kdp`, `watch` (latexmk `-pvc`), `validate`, `wordcount`, `pagecount`, `clean`, `cleanall`, `help`. Niceties: ANSI-colored output with ✓/➜ symbols, a pinned local texlive cache (`export TEXMFCACHE := $(CURDIR)/.texlive-cache`), and post-build `pdfinfo` page-count/size reporting. Key non-obvious target — KDP cover with prepress flatten (`Makefile:253-266`):

```make
$(KDP_COVER_PDF): $(KDP_COVER_TEX) front-matter/cover/kdp-cover-vars.tex
	@echo "$(BOLD)$(BLUE)$(ARROW) Building KDP cover (3 passes + prepress flatten)...$(RESET)"
	@if [ -f $(KDP_COVER_TEX) ]; then \
		$(LATEX) $(LATEX_OPTS) $(KDP_COVER_TEX); \
		$(LATEX) $(LATEX_OPTS) $(KDP_COVER_TEX); \
		$(LATEX) $(LATEX_OPTS) $(KDP_COVER_TEX); \
		gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress \
		   -dCompatibilityLevel=1.3 -dAutoRotatePages=/None \
		   -sOutputFile=kdp-cover-flat.pdf $(KDP_COVER_PDF) && \
		mv kdp-cover-flat.pdf $(KDP_COVER_PDF); \
		pdfinfo $(KDP_COVER_PDF) | grep "Page size"; \
	fi
```

(3 LaTeX passes because TikZ `remember picture` needs them; Ghostscript `/prepress` at PDF 1.3 flattens transparency for KDP.)

### scripts/*.py (one line each, from docstrings)

| Script | Purpose |
|---|---|
| `fetch_url.py` | Fetch a URL with Playwright + stealth, return clean markdown (trafilatura); `--screenshot`, `--bibtex` modes |
| `extract_pdf.py` | Extract text/metadata from PDFs via pypdfium2 |
| `fetch_wiki_history.py` | Wikipedia edit history / user contributions / diffs via MediaWiki API |
| `fetch_wiki_talk.py` | Fetch and parse Wikipedia talk pages (threads, archives) |
| `archive_urls.py` | Submit research URLs to the Wayback Machine |
| `bibtex_from_research.py` | Generate BibTeX entries from YAML frontmatter in research files |
| `bibtex_utils.py` | Shared BibTeX-generation helpers for the fetch scripts |
| `book_stats.py` | Project statistics (per-chapter word counts, JSON output) |
| `check_style.py` | Deterministic style linter against STYLE.md/CLAUDE.md rules (see §8) |
| `check_repetition.py` | Repeated 3–6-word n-grams, common sentence starts, duplicate sentences across chapters |
| `check_citations.py` | Sample .bib entries, show where cited, check formatting, verification links |
| `check_quotes.py` | Extract blockquotes/inline quotes with sources for attribution review |
| `check_urls.py` | Verify research URLs are live (200/redirect/timeout report) |
| `check_research.py` | Sample research files, flag missing sections and gaps |
| `citation_audit.py` | LLM audit (pydantic-ai + OpenAI gpt-5.5, reasoning xhigh, flex tier): per-section structured list of citation-worthy claims, whether `\autocite` is nearby, suggested bib key |
| `citation_triage.py` | Deterministic triage of audit JSON into READY (in refs.bib) / IMPORT (in research BibTeX) / GAP-FACTCHECK buckets |
| `cite_lib.py` | Shared bib-parsing helpers for the citation pipeline |
| `crossref.py` | Cross-reference people/events/themes across research notes |
| `timeline.py` | Extract dates + context from research notes into a chronology |
| `random_research.py` | Sample a random research file stratified by category |
| `research_chronology.py` | Run codex in parallel to research each year 1993–2026 |
| `rubric_review.py` | LLM application of the revision rubric to each LaTeX section → JSON per file in `review/rubric-json/` |
| `rubric_triage.py` | Deterministic split of rubric JSON into per-chapter fix briefs vs cross-chapter worklists (`review/rubric-action/`) |
| `fec_monoculture.py` | Replicate the WMF-employee FEC donation analysis via the OpenFEC API (primary-data reproducibility for a book claim) |

Scripts use PEP 723 inline metadata (`# /// script` blocks) and are run via `uv run`. Full docs in `docs/scripts.md` (908 lines).

### pyproject.toml (verbatim, trimmed)

```toml
[project]
name = "wiki-history-book"
version = "0.1.0"
description = "A critical, objective history of Wikipedia and the Wikimedia Foundation"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.31.0",
    "beautifulsoup4>=4.12.0",
    "lxml>=5.0.0",
    "pyyaml>=6.0",
    "rich>=13.0.0",
    "playwright>=1.57.0",
    "httpx>=0.28.1",
]

[project.optional-dependencies]
dev = ["pytest>=7.4.0", "black>=24.0.0", "ruff>=0.1.0"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["scripts"]
```

Heavier deps (TexSoup, typer, pydantic-ai, pypdfium2) are pulled ad hoc with `uv run --with ...` rather than declared — keeps the base env light.

## 6. Metadata & publishing (KDP.md)

`KDP.md` is a complete, form-ordered upload playbook ("Everything KDP's forms ask for, in order," explicitly "Modeled on datacenter-2026-book/KDP.md" — there is a family of sibling book projects sharing house precedent). Contents:

- **Files-to-upload table** with rebuild commands per asset and the rule: "If the interior page count changes: `make pdf && make kdp-cover-vars && make kdp-cover` (spine width is derived from the page count)."
- **Metadata:** title/subtitle/author/publisher-of-record (self via Bowker), both ISBNs, language, edition, website, and a five-point analysis of publishing a book under CC BY-SA on KDP.
- **Descriptions:** long HTML description (mirrors the back cover verbatim) + ~350-char short description.
- **Keywords (7 slots):** wikipedia history; AI training data copyright; copyleft creative commons; institutional capture; knowledge commons enclosure; wikimedia foundation; open source encyclopedia.
- **BISAC categories:** COM079000 Computers/Social Aspects, SOC052000 Media Studies, HIS054000 Social History (+2 alternates).
- **AI content disclosure section** quoting KDP's AI-generated vs AI-assisted definitions, the facts of this book's workflow, and the decision logic (with the sibling-book contrast: "history-through-rfc-book answered 'No' because its prose was human-authored").
- **Pricing table with royalty math:** paperback $24.99 (60% − ~$3.96 print cost ≈ $11.03 net); Kindle $9.99 at 70% ≈ $6.90 — explicitly noting $9.99 out-earns $14.99 because the 70% band caps at $9.99. KDP Select not enrolled; DRM off; worldwide.
- **Pre-upload checklist** including expected cover page box ("928.32 x 666 pts"), physical proof order, USCO copyright registration process (with the AI-disclosure requirement mirroring the KDP checkbox), LCCN decision.

### Cover process and spine math

`latex/scripts/update_kdp_cover_vars.py` regenerates `front-matter/cover/kdp-cover-vars.tex` from `pdfinfo` of the built interior:

```python
TRIM_W, TRIM_H, BLEED = 6.0, 9.0, 0.125
PAPER = "white"  # white paper: 0.002252 in/page

spine = pages * 0.002252 + 0.06
width = 2 * BLEED + 2 * TRIM_W + spine
height = TRIM_H + 2 * BLEED
```

("KDP white paper formula + hinge allowance"; at 259 pp → spine 0.643268 in, cover 12.893268 × 9.250 in.) The generated vars file defines `\CoverTrimWidth/\CoverBleed/\CoverSpineWidth/\CoverWidth/\CoverHeight` lengths. `kdp-cover.tex` then lays out panels by cumulative offsets:

```latex
\newlength{\BackStart}\setlength{\BackStart}{\CoverBleed}
\newlength{\SpineStart}\setlength{\SpineStart}{\dimexpr\CoverBleed+\CoverTrimWidth\relax}
\newlength{\FrontStart}\setlength{\FrontStart}{\dimexpr\CoverBleed+\CoverTrimWidth+\CoverSpineWidth\relax}
```

The whole wrap is one TikZ picture (`remember picture,overlay,x=1in,y=1in`) with three shifted scopes (back / spine / front). The spine text rotates −90°; the back panel contains hook, divider, description, kicker, an "about the author" box, site URL, and a **self-embedded EAN-13 barcode** in the KDP 2.0×1.2 in zone ("At upload, KDP detects it — do not have KDP overprint its own"). Palette: bone `#F4F1E9`, ink `#20201E`, accent `#7C2D2D`. `cover-fence-studies.tex` is a clever design-iteration tool: ten one-page 6×9 studies with an identical type stack (`\newcommand{\typestack}{...}`) and a varying TikZ motif per page, so cover concepts can be compared side by side in one PDF. Standalone `cover-proof.tex` / `back-cover-proof.tex` render individual panels for proofing and feed the EPUB cover JPEG.

## 7. Style / craft / AI-tone guides

**CLAUDE.md vs AGENTS.md vs GEMINI.md:** not identical — three purpose-built variants of the same core. `CLAUDE.md` (210 lines) is the richest: thesis arc, analytical frameworks, the monoculture thesis with replication status per dataset, style quick-reference, script table, and operational rules ("Do NOT use WebFetch. Always use `fetch_url.py` via Bash," and guidance that specialized research agents lack Bash so URL-fetching subagents must be `general-purpose`). `AGENTS.md` (113 lines) is a plain-ASCII mirror for generic agents with an added "Anti-Hallucination / Verification Practices" section and non-negotiable citation rules (`[CITE]`/`[VERIFY]` markers, wayback+urldate in BibTeX, Wikipedia revision IDs). `GEMINI.md` (102 lines) mirrors CLAUDE.md but points at `.gemini/agents/`. The 13 agent files are duplicated across `.claude/agents/` and `.gemini/agents/` with only frontmatter translated (`tools: Read, Grep, Glob, WebFetch, WebSearch` / `model: sonnet` → `tools: read_file, search_file_content, glob, web_fetch, google_web_search` / `model: gemini`).

**STYLE.md** — the load-bearing rules:

- The Coffee Test: "Write as if explaining to a curious friend over coffee… If it sounds like: A corporate press release → Rewrite; An academic paper → Rewrite; A TED talk → Rewrite; A Wikipedia article → Rewrite (ironic, but true)."
- Voice: "we" for shared discovery, third person for historical narration; never "You must understand… / One might note… / I believe…".
- Sentences: average 15–20 words, max 35; paragraphs 3–7 sentences.
- The absolute banned-word list (STYLE.md:105-113, verbatim):

```
delve, landscape, realm, tapestry, crucial, unlock, leverage, utilize,
harness, foster, elevate, streamline, robust, embark, illuminate, unveil,
pivotal, intricate, myriad, plethora, multifaceted, paradigm, ecosystem,
navigate (metaphorical), cornerstone, bedrock, hallmark, catalyst,
stakeholder, synergy, optimize, facilitate, methodology, comprehensive,
imperative, paramount, seamless, cutting-edge, state-of-the-art, innovative,
transformative, holistic, proactive
```

- Banned phrase categories: setup phrases ("It's important to note that…"), filler transitions ("That said," "Moving forward,"), hype ("game-changer"), weak intensifiers ("Indeed," "Furthermore," "Moreover," "Notably,"), false casual ("Let's dive in"), and — added later — "Overused Rhetorical Templates (Use Sparingly — Not Banned)": the both-and/neither balancing construction, budgeted "at most once per few chapters."
- Em dashes: "Maximum one per paragraph… they're a tell for AI-generated text."
- Data rule: never a number without comparison/context (the 6.7M-articles vs Britannica example).
- The A-B-A' chapter architecture (hook scene → analysis → return/bridge) with tense assignments per section.

**STYLE-AI-TELLS.md** — a catalog of named, detectable patterns, each with pattern/fix/rule: the "This" disease (max one "This" opener per paragraph), gerund openers (max one per page), "As X, Y" constructions, the Triple Structure ("AI loves threes… Use two sometimes. Use four occasionally."), filler transitions (banned list), hedging clusters ("might potentially → might"), false balance ("Don't default to 'both sides.' Make claims."), nominalizations ("made a decision → decided"), rhetorical-question setups (max one per chapter, never as transition), summary openers ("Never announce what you're about to write"), the predictable paragraph template, symmetrical sections, exhaustive lists (max ~3 examples), plus extra banned adverbs/adjectives (Additionally, Essentially, Notably; Bustling, Intricate, Nuanced, Ever-evolving…). Framed explicitly in terms of perplexity/burstiness.

**STYLE-CRAFT.md** — burstiness worked examples, short-sentence deployment, echo/temporal/contrast transitions, banned paragraph-opener transitions (Furthermore/Moreover/Indeed/Nevertheless/Consequently/Subsequently), show-don't-summarize with the Seigenthaler scene example, and attribution grammar for documented vs reconstructed vs uncertain vs disputed claims.

**WRITING-PROCESS.md** — a 7-phase pipeline (Research → Planning → Drafting → Review → Revision → Polish → Verification), each phase with steps, a quality checklist, and named agents. Includes the standard research-folder schema (README/sources/timeline/people/vignettes/data-notes/controversies + downloads/), the A-B-A' page/word budget table, a 7-perspective review scheme (general/technical/historian/skeptic readers + copy/developmental/fact-check editors), and a unified review-report template.

**outline/TEMPLATE.md** (288 lines) — richest chapter-outline template seen in these projects: a "Beat Position" table (Save the Cat beat, position-in-book %, expected tension 0–1, pacing), a **Kishotenketsu** layer (Ki conventional understanding → Sho evidence → Ten reframing twist → Ketsu synthesis) mapped onto nonfiction, then the A/B1/B2/B3/A' section outline with per-section word counts, opening technique, scene fields (date/place/person/action/stakes), sensory details, and source-for-scene citation.

**Subagent roster** (`.claude/agents/*.md`, 13 files, name + purpose from frontmatter):

| Agent | Purpose | Model |
|---|---|---|
| `wikipedia-research` | Extract/synthesize Wikipedia primary sources (policies, talk pages, arbitration, edit histories) | sonnet |
| `controversy-research` | Multi-perspective research on disputed topics | sonnet |
| `outline-iteration` | Refine outlines pre-drafting (structure, hook strength, gaps) | sonnet |
| `draft-from-outline` | Outline → first-draft prose per style guide | **opus** |
| `critical-review` | Review from a specified perspective; feedback only, no edits | sonnet |
| `accessibility-check` | Readability, jargon control, Coffee Test compliance | sonnet |
| `revision-from-feedback` | Apply review feedback systematically (Edit access) | sonnet |
| `citation-management` | Verify/complete citations, BibTeX, archive links | **opus** |
| `style-guide-conformance` | Enforce STYLE.md/AI-TELLS; report or fix mode | sonnet |
| `compression-tightening` | Cut redundancy; target 5–10% word reduction | sonnet |
| `flow-improvement` | Transitions, pacing, momentum (Edit access) | sonnet |
| `fact-check` | Verify claims/dates/names/stats/quotes against sources | sonnet |
| `cross-reference-verification` | Internal consistency across chapters | sonnet |

Note the deliberate model economics: only drafting and citation work get opus; review/polish agents that don't edit get read-only tool sets.

## 8. QA / review workflow

This project's QA machinery is its most distinctive asset — a stack of **deterministic linters + LLM auditors + named human-style audits**, each writing durable reports into `review/` or `docs/`.

### Deterministic checks

`scripts/check_style.py` implements 13 checks: `check_banned_words`, `check_banned_phrases`, `check_sentence_length` (max 35 words), `check_weasel_words`, `check_passive_voice`, `check_filler_phrases`, `check_em_dashes` (max 1/paragraph), `check_paragraph_length` (max 7 sentences), `check_double_hyphens`, `check_semicolons` (rate per 500 words), `check_paragraph_openers` (banned openers), `check_spelled_numbers` (STYLE.md numeral rules, with allowlists for "Chapter 5"-type usage and months), `check_sentence_start_numbers`. Representative in-code lists (check_style.py:45-62):

```python
BANNED_WORDS = [
    "delve", "landscape", "tapestry", "leverage", "utilize", "paradigm",
    "ecosystem", "pivotal", "crucial", "robust", "unlock", "harness",
    "foster", "embark", "illuminate", "unveil", "myriad", "multifaceted",
]

BANNED_PHRASES = [
    "it's important to note", "it is important to note",
    "let's dive in", "let us dive in",
    "game-changer", "game changer", "groundbreaking",
    "indeed", "furthermore", "moreover",
]
```

Crucially, `review/style-coverage-audit.md` audits **the checker against the style guide**: a coverage table mapping every concrete STYLE.md rule to deterministic check / LLM rubric / neither, noting e.g. "`BANNED_WORDS` has 18 of ~43 listed words… Partial," and recording which gaps were closed. `check_repetition.py` finds repeated 3–6-word n-grams, common sentence starts, and duplicate sentences (8-word threshold); its output feeds a book-wide "Repetition Ledger" in `review/finalization-tracker-2026-06.md` with per-tic budgets ("'at industrial scale' 11x — keep prologue origin + 1-2 echoes; vary the rest").

### LLM audit pipelines (audit → triage → action)

Two parallel pipelines, both with the same shape — LLM produces structured JSON, deterministic triage turns it into per-chapter fix briefs:

1. **Citations:** `citation_audit.py` (gpt-5.5, xhigh reasoning, flex tier) extracts citation-worthy claims per section into `review/citation-json/`; `citation_triage.py` matches each claim against refs.bib (READY), BibTeX embedded in research notes (IMPORT → `_to-import.bib`), or nothing (GAP/FACTCHECK) into `review/citation-action/<chapter>.md` plus `_FLAGS.md`/`_gaps.md`/`_summary.md`.
2. **Rubric:** `rubric_review.py` applies the nine-defect revision rubric per section into `review/rubric-json/` (26 files); `rubric_triage.py` splits findings into per-chapter LOCAL briefs (`review/rubric-action/`) and a `_cross-chapter.md` holistic list.

### Citation verification (`docs/cite-check.md`)

Two mandatory levels: **metadata verification** (title/author/date/URL/entry type correct) and **claim verification** ("Retrieve actual source content… find the specific passage supporting the claim. Confirm figures, dates, and context match"). Tooling: `check_citations.py` sampling plus Playwright-with-Firefox fetch recipes for bot-protected sites. Results are visible in the finalization tracker: per-chapter fixes like "Joi Ito stitched quote unstitched (first clause wasn't in the post) → paraphrase" and "epigraph (Corbet 'flier' quote) unverifiable in any primary source → replaced."

### Named audits in `review/`

- `hook-audit.md` — every chapter's opening tested against one defect ("decapitated hook"), severity table with "minimal fix" column.
- `hook-presupposition-audit.md` — a second lens on the same openings.
- `ch01-naive-reader.md` — simulated first-time-reader comprehension audit that first enumerates *exactly what the reader knows entering the chapter* from front matter alone.
- `flow-audit/_FLOW-BRIEF.md`, `style-coverage-audit.md`, `chapter-research-review-2026-01-28.md`, `finalization-tracker-2026-06.md` (the master per-unit fact-check ledger), `self-review-brief.md`, `sanger-june-2026-incorporation-plan.md` (integrating late-breaking real-world events).

### Multi-pass editing archives

- **`docs/revise-02/`** — the big rewrite pass: per-chapter revision *plans* (23 files), `_AGENT-BRIEF.md`/`_CRITIQUE-BRIEF.md` (reusable prompts for reviser/critic agents), and `REVISION-DIARY.md` logging iterations of "launch 5 Opus reviewers → synthesize → launch revisers with non-overlapping file ownership → rebuild + verify." The diary's iteration-1 findings are a masterclass in multi-agent failure modes: "The problems are second-order artifacts of independent parallel rewrites: the same idea lands too many times because adjacent chapters each restate it, plus a few number drifts" (e.g., WMF revenue stated as $180M/$185M/$200M in different chapters). The action plan assigns "one owner per beat; one agent per file-set, no file overlap."
- **`docs/edit-03/`** — a full copy+content editorial pass, chapter by chapter, by the lead model itself ("Read the whole chapter (the editor, not an agent)"), with per-chapter findings files, transition-seam audits (`transitions-chapter-seams.md`, `transitions-section-seams.md`, a transitions rubric), a currency check (`currency-2026-07-01.md`), and a status table tracking read/logged/edited/committed per file. Rule: "Edit what is clearly right; log everything. Judgment calls and anything touching sourced facts/quotes → flagged for the author, not edited."
- **`docs/CHAPTER-REVISION-CHECKLIST.md`** — diagnoses the root cause of first-draft weakness as "one template, stamped on every chapter" (labeled Synthesis/Bridge Forward/Return-to-X scaffolding) and defines **nine detectable defects** with detect/why/fix recipes, designed so "a subagent should be able to take one chapter, run this checklist top to bottom, and produce a revised .tex file plus a short report."
- **`docs/REPETITION-AND-FATIGUE-GUIDE.md`** — taxonomy of repetition (verbatim in-chapter duplicates, cross-chapter quote reuse — "the April 2024 'many may not be compliant' quote appeared verbatim in 7+ chapters," repeated statistics, sentence-template tics) with remediation strategy per type.

## 9. Verdict — what to lift into the master template

**Take wholesale (near copy-paste):**

1. **The four-file LaTeX preamble split** (`packages`/`colors`/`styling`/`commands`) with the 6×9 geometry, engine-conditional Libertinus setup, superscript-numeric biblatex config with `\AtEveryBibitem` field clearing, fancyhdr styles, and titlesec chapter format. It is a complete, KDP-proven 6×9 trade-book skin.
2. **The Makefile** — especially `draft` mode (`\def\DraftMode{1}` + jobname isolation + banner/disclaimer machinery in main.tex), the KDP cover target with 3-pass TikZ + Ghostscript `/prepress` flatten, `validate`, and the local `.texlive-cache`.
3. **`update_kdp_cover_vars.py` + `kdp-cover-vars.tex` + the cover panel-offset pattern.** The spine formula (`pages * 0.002252 + 0.06` for white paper), the vars-file indirection, and the `\BackStart/\SpineStart/\FrontStart` scoped-TikZ layout generalize to any KDP book. Also take `cover-fence-studies.tex`'s pattern of N design studies sharing one `\typestack` macro.
4. **KDP.md as a playbook template** — the file-upload table with rebuild commands, AI-disclosure decision framework (with the KDP-vs-USCO consistency note), royalty-band pricing math, and pre-upload checklist. It explicitly inherits from sibling books ("house precedent"), i.e. it is already a template in practice.
5. **The style-guide trio** (STYLE.md / STYLE-AI-TELLS.md / STYLE-CRAFT.md) and `check_style.py`. Almost none of it is Wikipedia-specific. The pairing of each guide rule with a deterministic check — and the **style-coverage audit that verifies the checker implements the guide** — is the standout practice.
6. **The audit→triage→action pattern** (`rubric_review.py`/`rubric_triage.py`, `citation_audit.py`/`citation_triage.py`): LLM produces structured JSON per chapter, deterministic code buckets it into per-chapter fix briefs with no file overlap between fixer agents. This plus the revise-02 diary's "one owner per beat" rule is the proven recipe for multi-agent book revision.
7. **Semantic LaTeX macro layer** (`commands.tex`): `\person` (small caps + index), `\chapterquote`, `\scenebreak`, `\archive`, draft-only `\TODO/\VERIFY/\controversial/\livingperson`. Keeping chapters in semantic macros is also what makes the custom EPUB converter viable — handlers map macros to HTML classes.
8. **The custom EPUB converter architecture** — generic core (`parser/renderer/handlers/macros|environments|math|references`) + per-book handler modules (`wiki_macros.py`), dynamic OPF/nav generation with accessibility metadata, correct mimetype-first zip packaging, epubcheck-0/0/0/0 gate, and `make cover-image` (pdftoppm from the front-cover proof). Pair it with the EPUB-TYPOGRAPHY-DIARY + 3-agent epub-qa sweep as the QA method.
9. **Process docs as reusable prompts:** WRITING-PROCESS.md's 7 phases, outline/TEMPLATE.md (Save-the-Cat beat position + Kishotenketsu + A-B-A' with scene/source fields), CHAPTER-REVISION-CHECKLIST.md's nine defects, REPETITION-AND-FATIGUE-GUIDE.md, and the 13-agent roster with its model-tiering (opus only where it drafts or verifies citations).

**Pitfalls to avoid (observed in this project):**

- **Structure drift between docs and source:** `latex/STATUS.md` documents an 18-chapter LaTeX layout as "outdated" vs the 22-chapter outline; README.md's Part names don't match main.tex's. A template should have one canonical structure file that build and docs both derive from.
- **Copied assets carrying stale identity:** `epub/templates/stylesheet.css` still says "How to Fight a Data Center" and describes box colors this book doesn't use; the EPUB uses EB Garamond while print uses Libertinus (possibly intentional, but undocumented). Templates need a "rename sweep" checklist.
- **Silent fallbacks in converters:** the dedication bug (converter fell back to a stale hardcoded string when extraction failed) — epub-qa's own fix note is the rule to encode: fail the build, never emit placeholder text silently.
- **Parallel-agent rewrites create cross-chapter repetition and number drift** — plan a dedicated continuity/dedup pass after any parallel revision, and keep a canonical-figures list (the "Truth = ch-11 table, FY2024 $185M" problem).
- **Checker/guide divergence:** check_style.py bans 18 of STYLE.md's ~43 words until audited. Generate the checker's lists from the guide (or vice versa).
- **Duplicated agent definitions** (`.claude/agents` vs `.gemini/agents` differ only in frontmatter) — generate one from the other rather than maintaining both by hand.
- Leftover scaffolding: `main.py` stub, `ebook` target referencing a `main-ebook.tex` that doesn't exist.

**Unique things this project does that others likely don't:**

- Reproducible primary-data analysis shipped with the book (`fec_monoculture.py` re-derives a central empirical claim from the OpenFEC API), with replication status per dataset tracked in CLAUDE.md including a negative result ("DOES NOT REPLICATE; do not use").
- Straight-quote normalization at the LaTeX level (`\MakeOuterQuote{"}`) so AI-drafted chapters with ASCII quotes typeset correctly.
- Word-spelled chapter numbers (`\chapterword`) consistently mirrored in the EPUB converter.
- A self-prepared PCIP block, self-embedded EAN-13 barcode in the cover TikZ, and publishing the book itself under CC BY-SA as a thesis statement.
- Honest AI-authorship disclosure plumbing from copyright page → KDP checkbox → USCO registration, reasoned through in writing.
