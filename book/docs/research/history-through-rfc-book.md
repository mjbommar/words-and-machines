# Research Report: history-through-rfc-book

Source: `/home/mjbommar/projects/personal/history-through-rfc-book`
Reviewed: 2026-07-06

---

## 1. Purpose & Status

**Book:** *Rough Consensus: How Engineers, Hackers, and Spies Built the Internet* — Michael J Bommarito II. Pop-science history/security of internet protocols told through RFCs: 23 protocol chapters + prologue, interlude ("Right Now"), epilogue ("Lo and Behold"), in four Parts (The Network / The Internet / The Web / The Reckoning). Thesis: *"The same thing that made the internet vulnerable is what made it possible. And that thing is still running."*

**Status:** Effectively **production-complete and publication-ready**. ~91,000 words, 371 citations, 91 visual elements; 434-page KDP interior verified; own ISBNs assigned (paperback 979-8-9947460-0-4, ebook 979-8-9947460-1-1); PCIP data on the copyright page; CMYK PDF/X-1a wrap cover built; KDP listing copy, categories, and keywords drafted (`docs/KDP-PREP.md`, June 2026). Three full edit rounds logged (`docs/review-02/`, `review-03/`, `edit-03/`). Recent commits:

```
6ece117 ISBN reassignment, Author's Note, back-cover justification, production review
e57a7b6 Back jacket redesign: fix collision, justify, dedash, retune bio
ed370a5 Edit round 03, iteration 3: hierarchical transitions audit
6fa1191 Edit round 03: two-pass copy + content edit across full manuscript
```

**Formats produced** (timestamped in `build/`): PRINT (6×9), PRINT-BLEED, EBOOK (large-font PDF), EPUB, AZW3/MOBI (via Calibre), KDP interior + KDP wrap cover (RGB and CMYK/X-1a), grayscale and true-B&W variants, prerelease preview PDF. A root-level `Rough Consensus - Draft 20260330.pdf` is the public draft.

---

## 2. Directory Layout (annotated)

```
history-through-rfc-book/
├── CLAUDE.md                  # Master AI instructions (thesis, A-B-A'-C structure, agents, scripts)
├── GEMINI.md                  # Gemini variant (same thesis/structure content)
├── TODO.md                    # 771-line metrics-driven review plan (word counts, quality scores/chapter)
├── Rough Consensus - Draft 20260330.pdf   # public draft artifact
├── .claude/agents/            # 22 writing/research agents (fork of legal-tech book's 27)
├── docs/                      # 20+ guides: SPIRIT, STYLE*, WRITING-PROCESS, LATEX, KDP-PREP,
│   ├── review-02/, review-03/ #   per-chapter review reports, round syntheses, revision coordination
│   └── edit-03/               #   edit-round working docs
├── notes/                     # structure.md, emotional-core.md, revision plans, citation review reports
├── outline/                   # per-chapter outlines + master-outline.md
├── research/                  # ch-XX dirs w/ per-section templates, _shared/ (people, orgs, themes,
│                              #   knowledge_graph), _templates/, cve-integration/, primary-source-verification/
├── src/                       # DATA TOOLING (not book text): IETF mailing-list archivers
│   │                          #   (archive_mailing_lists.py, imap_mirror_all.py, mail_to_jsonl.py...)
│   └── knowledge_graph/       #   entity/edge extraction + graph analysis over research corpus
├── scripts/                   # book_stats.py, check_prose.py, sample_text.py, fix_proto.py,
│                              #   render_cover.py, regenerate_cover_background.py, book QA + cover tools
├── latex/                     # ALL LaTeX sources AND build workdir (aux files live here)
│   ├── main.tex               # full book (includes cover pages)
│   ├── main-interior.tex      # KDP interior (no covers)
│   ├── main-ebook.tex         # 14pt extbook one-side e-reader PDF
│   ├── kdp-cover.tex          # full-wrap cover (back + spine + front), TikZ
│   ├── Makefile               # 810-line build system (see §5)
│   ├── preamble/              # main, packages, colors, tikz, boxes, elements, code, styling,
│   │                          #   headers, commands
│   ├── chapters/              # 01-arpanet.tex ... 23-robots-txt.tex + prologue/interlude/epilogue
│   ├── front-matter/          # half-title, title-page, copyright (ISBN/PCIP), dedication, cover/
│   ├── back-matter/           # author-note (AI disclosure), timeline, acknowledgments, back-cover
│   ├── bib/refs.bib
│   ├── data/rfc_per_year.csv  # data-driven figure input
│   ├── figures/, figures-png/ # TikZ figures + rendered PNGs
│   ├── scripts/               # update_kdp_cover_vars.py, generate_isbn_barcode.py, ngram/repetition QA
│   ├── src/                   # cover_network.py, protocol_networks.py (cover art generators)
│   └── cover-python-*.{svg,png,pdf,jpg}  # generated cover art variants
├── epub/
│   ├── converter/             # LaTeX→EPUB converter (evolved fork: + generators.py for nav/opf/front matter)
│   ├── templates/             # content.opf, stylesheet.css, per-chapter XHTML, fonts (IBM Plex otf)
│   ├── scripts/               # package_epub.py, render_figures.py
│   └── META-INF/
└── build/                     # RELEASE OUTPUT (timestamped)
    ├── pdf/                   # "Rough Consensus - YYYYMMDD-HHMM - {PRINT,PRINT-BLEED,EBOOK}.pdf"
    └── epub/                  # "... - EPUB.epub", Rough Consensus.azw3/.mobi
```

### Source-to-output flow (build/ and src/ clarified)

- **Book text source:** `latex/chapters/*.tex` is authored directly in LaTeX (no Markdown intermediary, unlike the legal-tech book). Outlines/research feed drafting agents, which write .tex.
- **`latex/` is also the compile workdir**: aux/bbl/log files sit beside sources; `.texlive-cache/` pins TEXMFCACHE locally.
- **`build/` is the release directory**: `make release` and `make epub` copy timestamped, human-named artifacts (`Rough Consensus - 20260330-1312 - EPUB.epub`) into `../build/{pdf,epub}` — a clean separation of working PDFs from distributable releases.
- **Top-level `src/` is research-data tooling, not book code**: scripts that archived IETF mailing lists (mailarchive.ietf.org + legacy FTP + IMAP) into `/data0/reference/rfc/mailing-lists/`, normalized mail to JSONL, plus a `knowledge_graph/` package (entities/edges/schema/graph_builder/analyze) run over the research corpus for narrative-connection mining.
- **`latex/src/` is cover-art generation**: `cover_network.py` / `protocol_networks.py` (PEP 723 inline-dep scripts using networkx/matplotlib) generate the layered network visualization used on the cover; `scripts/render_cover.py` renders final cover styles (default/radiant/atmospheric/particles) to SVG/PNG/PDF/JPG.

---

## 3. LaTeX Pipeline

### Entry points

Three top-level documents sharing one preamble and chapter set:

- `main.tex` — `\documentclass[11pt,twoside,openright]{book}`; includes front-cover image page and back-cover page (full self-contained PDF). Mode flags: `\BleedMode`, `\PreReleaseMode`+`\PreReleaseDate`, `\GrayscaleMode` (set via Makefile `-jobname` + inline `\def...\input{main.tex}`).
- `main-interior.tex` — identical content minus cover pages, for KDP upload.
- `main-ebook.tex` — `\documentclass[14pt,oneside]{extbook}` with `\def\EbookMode{1}` before preamble (triggers narrow-margin geometry) and a re-declared main font at `Scale=1.15` — a large-print PDF for e-readers.

main.tex is heavily annotated with the book's narrative architecture — each `\part` block carries trust-model, tempo, and thesis comments:

```latex
% ACT I: THE NETWORK (1969-1982)
% "We're all friends here"
% Trust model: Implicit. Everyone knows everyone.
% Tempo: Allegro - intimate, detailed, scene-setting
```

and every chapter include documents its breach pairing:

```latex
% Chapter 7: DNS — The Internet's Phonebook (1983-1987)
% A' Breach: Kaminsky Attack (2008)
\input{chapters/07-dns}
```

### Preamble (`latex/preamble/main.tex`)

Ten components, load-order documented:

```latex
\input{preamble/packages}   % geometry, fonts, microtype, biblatex, glossaries
\input{preamble/colors}     % layered color system (cover-matched)
\input{preamble/tikz}       % network-diagram styles
\input{preamble/boxes}      % tcolorbox (definition/protocol/history/breach, rfcbox, vt100box, impbox)
\input{preamble/elements}   % transcript, timeline, terminal, rfccard
\input{preamble/code}       % ccode, terminalbox, packetbox
\input{preamble/styling}    % TTY chapter/section styles, ls-style ToC
\input{preamble/headers}    % fancyhdr page styles
\input{preamble/commands}   % \proto, \keyterm, \rfclink, \vuln, \person ...
```

### Trim size / geometry (packages.tex)

```latex
\usepackage[
  papersize={6in,9in},
  inner=0.875in,       % Gutter margin (for binding)
  outer=0.625in,
  top=0.75in, bottom=0.75in,
  includehead, includefoot, footskip=0.35in
]{geometry}

\ifdefined\BleedMode
  \geometry{ paperwidth=6.25in, paperheight=9.25in,
    inner=1in, outer=0.75in, top=0.875in, bottom=0.875in, footskip=0.35in }
\fi

\ifdefined\EbookMode
  \geometry{ paperwidth=6in, paperheight=9in,
    inner=0.5in, outer=0.4in, top=0.5in, bottom=0.6in, footskip=0.3in }
\fi
```

Note the wider gutter (0.875") than the legal-tech book — sized for the verified 434-page count (KDP requires ≥0.625" at 301–500pp).

### Fonts — "The Terminal and the Page" (quote exact setup)

The design concept is documented in the preamble itself:

```latex
% TYPOGRAPHY CONCEPT: "The Terminal and the Page"
% This book lives between two worlds: the humanist tradition of printed books
% and the monospace world of early computing. IBM Plex bridges these...
```

```latex
\setmainfont{IBM Plex Serif}[
  Scale = 0.92,
  Ligatures = TeX,
  Numbers = OldStyle,
  BoldFont = IBMPlexSerif-SemiBold.otf,  % SemiBold reads better than Bold at text sizes
  ItalicFont = IBMPlexSerif-Italic.otf,
  BoldItalicFont = IBMPlexSerif-SemiBoldItalic.otf,
  UprightFeatures = {
    SizeFeatures = {
      {Size = -8.5, Font = IBMPlexSerif-Text.otf},      % Optical size for small text
      {Size = 8.5-, Font = IBMPlexSerif-Regular.otf},
    },
  },
]
\setsansfont{IBM Plex Sans}[ Scale = MatchLowercase, Numbers = Lining,
  BoldFont = IBMPlexSans-SemiBold.otf, ... ]
\setmonofont{IBM Plex Mono}[ Scale = 0.85, ... ]   % Mono runs large; scale down
\IfFontExistsTF{IBMPlexMath-Regular.otf}{
  \setmathfont{IBMPlexMath-Regular.otf}[Scale = 0.92]
}{ \setmathfont{Latin Modern Math}[Scale = 0.92] }
```

Extras: `\newfontfamily` light/medium/thin weights, `\cjkfont` (Noto Serif CJK SC) and `\emojifont` (Noto Color Emoji with `Renderer=HarfBuzz`) with `\cjk{}`/`\emoji{}` wrappers, Font Awesome 5, Noto Sans Symbols2, and `pmboxdraw` for Unicode box-drawing (terminal ASCII art).

### Microtype — tuned, not default

```latex
\usepackage[
  activate={true,nocompatibility}, final,
  tracking=true, protrusion=true, expansion=true,
  factor=1100, stretch=20, shrink=20,
]{microtype}
\SetTracking{encoding=*, shape=sc}{50}
\SetProtrusion{ encoding = *, family = *, }{
  . = {0, 700}, {,} = {0, 700}, ... — = {0, 300}, ( = {400, 0}, / = {200, 300},
}
```

Hand-written protrusion table for hanging punctuation including en/em dashes. Line-breaking is deliberately loosened for technical terms: `\tolerance=2000`, `\hyphenpenalty=25`, `\emergencystretch=3em`, `\hfuzz=3pt`. Widows/orphans hard-banned (10000). `\setstretch{1.15}`, `parindent 1.5em`, `indentfirst` package (first paragraph after heading indented, traditional style).

### Chapter/section styling — TTY aesthetic (styling.tex)

```latex
% CHAPTER STYLE: Authentic TTY / Early Terminal
%   - Regular weight mono (terminals didn't have bold)
%   - UPPERCASE titles (early systems often lacked lowercase)
%   - ASCII decoration lines (======) like RFC section breaks

\newcommand{\ttylineshort}{%
  {\color{slate-400}\ttfamily\small ================================}}

\titleformat{\chapter}[display]
  {\normalfont\centering\ttfamily}
  {\chapterornament\vspace{6pt}{\color{slate-500}\small CHAPTER \thechapter}}
  {8pt}
  {\Large\MakeUppercase}
  [\vspace{8pt}\ttylineshort]
```

Sections are RFC-style: `\titleformat{\section}{\large\ttfamily\color{slate-700}}{\thesection.}{0.75em}{\MakeUppercase}` (period after number, uppercase mono). The **table of contents is styled as a Unix directory listing** (`% TOC — Terminal Directory Listing Style ... ls -la`), chapters only (`tocdepth=0`), and main.tex locally re-formats the chapter title for the TOC page. Section-heading `\Needspace` protection identical to the legal-tech book.

### Colors (colors.tex)

Same 4-layer Tailwind architecture as the legal-tech book but **cover-matched**: the entire palette is remapped to charcoal/gold ("THEME: Internet History & Security (Cover-Matched)"), with an instructive hack — semantic family names were kept while values were re-pointed at the cover palette:

```latex
% --- GOLD FAMILY (Networking, connectivity, protocols) ---
\definecolor{cyan-900}{HTML}{92400E}   % NodeDeep (cover)
\definecolor{cyan-600}{HTML}{F59E0B}   % NodePrimary
```

(i.e., "cyan-*" now holds gold values so downstream styles didn't need edits). A `\GrayscaleMode` build converts LaTeX colors to grays; `make bw` then flattens embedded images via Ghostscript.

### Visual elements (elements.tex, boxes.tex, code.tex)

Signature period-styled environments (tcolorbox):

```latex
% Transcript with attribution header
\newtcolorbox{transcriptsrc}[1]{
  enhanced, colback=white, colframe=white, boxrule=0pt,
  borderline west={2.5pt}{0pt}{amber-600},
  borderline north={0.4pt}{0pt}{slate-300},
  fontupper=\ttfamily\small, unbreakable,
  before upper={{\fontspec{IBM Plex Mono}\fontsize{8}{10}\selectfont\color{slate-500}#1}\par\vspace{6pt}},
}
```

Usage: `\begin{transcript}[RFC 1 --- April 7, 1969 --- Steve Crocker] ... \end{transcript}`. Also `email`, `timeline` (TikZ), `terminal`, `rfccard` (RFC metadata cards); boxes.tex adds `definitionbox`, `protocolbox`, `historybox`, `breachbox`, `rfcbox`, `vt100box`/`vt100titled` (dark terminal), `impbox` (amber teletype); code.tex adds `ccode`, `terminalbox`, `packetbox`. The elements file even contains ASCII-art banner comments and box-drawing usage diagrams — the docs live in the code.

### Domain commands (commands.tex)

```latex
\newcommand{\proto}[1]{\texttt{\color{cyan-700}#1}}     % protocol/program names
\newcommand{\port}[1]{\texttt{\color{cyan-600}#1}}
\newcommand{\ip}[1]{\texttt{\color{code-identifier}#1}}
\newcommand{\rfclink}[1]{\href{https://www.rfc-editor.org/rfc/rfc#1}{\rfcnum{#1}}}
\newcommand{\vuln}[1]{\texttt{\color{red-700}#1}}       % CVE ids
\newcommand{\attack}[1]{\textbf{\color{red-600}#1}}
\newcommand{\malware}[1]{\textit{\color{red-700}#1}}
\newcommand{\person}[1]{\textbf{#1}}
\newcommand{\org}[1]{\textsc{#1}}
```

plus `\keyterm`, `\scenebreak` (pgfornament), `\networkdivider`, `\timestamp`, `\pullquote`. `docs/LATEX.md` has a decision table for `\proto{}` vs `\keyterm{}` vs `\texttt{}` (skip inside quotes/epigraphs/headings), **enforced mechanically** by `scripts/fix_proto.py --dry-run`.

### Headers/footers (headers.tex)

Same proven three-style fancyhdr system as the legal-tech book (frontmatter folios-only; main matter verso `page — Book Title`, recto `Chapter Title — page`; `plain` = folio bottom-center for chapter openers; `\sectionmark` disabled; `\disablecleardoublepage`/`\enablecleardoublepage` helpers), with the draft banner generalized to:

```latex
\newcommand{\prereleasebanner}{\small\bfseries\color{red!70!black}%
  PRE-PUBLICATION COPY --- \PreReleaseDate{} --- Not for Resale or Redistribution}
```

### Bibliography

biblatex/biber `numeric-comp`, `autocite=superscript`, `\AtBeginDocument{\let\cite\supercite}` (simpler than the legal-tech book's DeclareCiteCommand approach), `sorting=none`, `sortcites=true`, doi/isbn/eprint hidden, urls kept, `\small` bibfont, "In:" removed. Also loads `glossaries` (`\makeglossaries`, toc, per-chapter numbering).

### Front/back matter (real files, unlike legal-tech)

`front-matter/`: half-title, title-page, `copyright.tex` with real ISBNs and a **Publisher's Cataloging-in-Publication block**:

```latex
\noindent ISBN 979-8-9947460-0-4 (paperback)\\
\noindent ISBN 979-8-9947460-1-1 (ebook)
...
Classification: LCC TK5105.875.I57 B66 2026 | DDC 004.678---dc23
```

`back-matter/`: `author-note.tex` (**carries the AI-assistance disclosure**), `timeline.tex`, `acknowledgments.tex`, `back-cover.tex`, ISBN barcode assets. Pre-release notice page auto-inserted after copyright under `\PreReleaseMode`.

---

## 4. EPUB Pipeline

### Tooling

Evolved fork of the legal-tech converter at `epub/converter/` — same architecture (TexSoup parser, renderer, handlers) **plus `generators.py`**, which dynamically generates the EPUB infrastructure from book structure:

```python
"""
This module generates all required EPUB files dynamically from the book structure:
- nav.xhtml (EPUB 3 navigation document)
- content.opf (package manifest)
- Front matter pages (cover, half-title, title-page, copyright, dedication, toc-page)
- Part divider pages
- Interlude page
All files are generated to be epubcheck compliant.
"""
```

Driven entirely from the Makefile with ephemeral deps (no pyproject in this repo):

```make
epub: cover-image
	@cd ../epub && uv run --with TexSoup,lxml,typer,rich \
		python -m converter book ../latex/main.tex -o templates/ -b ../latex/bib/refs.bib
	@cd ../epub && uv run --with TexSoup,lxml,typer,rich \
		python -m converter epub templates/ -o "$(EPUB_FILE)" -t templates/
```

Note it parses **`main.tex` itself** to discover chapters/parts (no separate manifest). `epub/scripts/package_epub.py` assembles OEBPS/META-INF and zips (mimetype first); `render_figures.py` rasterizes TikZ figures for EPUB. Utility targets: `make epub-test-chapter` (single-chapter conversion to /tmp) and `make epub-check` (reports LaTeX macros/environments lacking converter handlers — a great coverage-check pattern).

### OPF metadata (`epub/templates/content.opf`)

```xml
<dc:identifier id="bookid">urn:isbn:9798994345764</dc:identifier>
<dc:title>Rough Consensus: How Engineers, Hackers, and Spies Built—And Broke—The Internet</dc:title>
<dc:creator>Michael J Bommarito II</dc:creator>
<dc:publisher>Michael J Bommarito II</dc:publisher>
<dc:subject>Internet History</dc:subject> ... 
<meta name="cover" content="cover-image"/>
```

Manifest embeds **IBM Plex OTFs** (`application/vnd.ms-opentype`) — serif ×4, sans ×3, mono ×3 — cover.jpg with `properties="cover-image"`, an SVG timeline figure, nav.xhtml, part-divider pages, and per-chapter XHTML. (Note: identifier ISBN `9798994345764` and subtitle "Built—And Broke—" predate the final ISBN/subtitle in copyright.tex — stale-metadata drift to guard against; `generators.py` regenerating the OPF is the fix.)

### CSS (`epub/templates/stylesheet.css`)

IBM Plex @font-face set, then print-matching typography:

```css
body { font-family: "IBM Plex Serif", Georgia, "Times New Roman", serif; line-height: 1.6; }
/* terminal / rfc content */
... { font-family: "IBM Plex Mono", "Courier New", Courier, monospace; line-height: 1.2; }
```

with classes mirroring the LaTeX environments (transcript, terminal, rfcbox equivalents) so the TTY aesthetic survives conversion.

### Cover handling

Canonical generator is `scripts/render_cover.py` (matplotlib/numpy/Pillow, PEP 723 inline deps; styles: default/radiant/atmospheric/particles). `make cover-image` renders the *atmospheric* style to JPG and copies it into both `latex/cover.jpg` and `epub/templates/OEBPS/images/cover.jpg` — one source of truth for print and EPUB covers.

### Kindle & validation

```make
kindle: epub    # ebook-convert → AZW3 (kindle_pw3 profile) + MOBI (kindle_pw)
	ebook-convert "$(EPUB_LATEST)" ... --embed-all-fonts --subset-embedded-fonts \
	  --smarten-punctuation --keep-ligatures --minimum-line-height 120 --no-inline-toc
kindle-validate:   # epubcheck on latest EPUB
```

---

## 5. Build Automation

### The Makefile (latex/Makefile, 810 lines) — the crown jewel

Colored, self-documenting (`make help`), reports page count/size/dimensions after every build via pdfinfo. Targets:

| Target | Output |
|---|---|
| `pdf` / `quick` / `full` / `watch` | latexmk lualatex builds (deps wildcard all preamble/chapters/front/back/bib) |
| `bleed` | 6.25×9.25 print PDF via `-jobname=main-bleed "$(BLEED_INPUT)"` where `BLEED_INPUT = \\def\\BleedMode{1}\\input{main.tex}` |
| `prerelease` | public preview w/ banner + notice page, date auto-injected |
| `grayscale`, `grayscale-bleed` | `\GrayscaleMode` builds |
| `bw`, `bw-bleed` | Ghostscript `-sColorConversionStrategy=Gray` true-B&W conversion |
| `ebook` | main-ebook.tex (14pt, needs `-shell-escape`) |
| `release` | copies PRINT/EBOOK/PRINT-BLEED to `../build/pdf/` as `"$(BOOK_TITLE) - $(TIMESTAMP) - X.pdf"` |
| `cover-image` | render_cover.py → cover.jpg → EPUB templates |
| `epub`, `epub-test-chapter`, `epub-check` | custom converter pipeline |
| `kindle`, `kindle-validate` | Calibre AZW3/MOBI, epubcheck |
| `kdp-interior` | main-interior.pdf (no covers) |
| `kdp-cover-vars` | **computes spine width from actual page count**: `spine = pages * 0.002252 + 0.06` (KDP white-paper formula) → writes `front-matter/cover/kdp-cover-vars.tex` |
| `kdp-cover` | 3-pass TikZ wrap cover + Ghostscript transparency flatten |
| `kdp-cover-cmyk` | Ghostscript `-dPDFX` conversion to **CMYK PDF/X-1a:2001** with SWOP output intent (`kdp-pdfx-def.ps`); runs in mktemp dir because "Ghostscript's pdfwrite cannot create its temp files on NFS mounts" |
| `kdp` | interior + cover convenience |
| `figures`, `figures-png`, `figures-gray` | figures-only PDF, 300-dpi PNGs (pdftoppm), grayscale (ImageMagick) |
| `validate` | page-size check vs 432×648pt, undefined refs/citations grep, overfull-box count from log |
| `wordcount`, `pagecount` | pdftotext / pdfinfo |
| `all-formats` | release + kindle |

Also pins a local TeX cache: `export TEXMFCACHE := $(CURDIR)/.texlive-cache`.

### Python scripts (all PEP 723 inline-dep, `uv run` friendly)

| Script | Purpose |
|---|---|
| `scripts/book_stats.py` | Words/sentences/paragraphs, structure counts, environments by category, citations/labels/footnotes; `--json/--markdown/--detailed` (quality + readability scores). Documented before/after-delta workflow |
| `scripts/check_prose.py` | Repetition QA: n-gram repetition (3–6 words), monotonous sentence starts, duplicate sentences (8+ words, cross-file = error), adjacent-sentence repetition; nupunkt tokenization + pydetex LaTeX stripping; `--format console/jsonl/json/grep`, `--severity`, CI-friendly non-zero exit |
| `scripts/sample_text.py` | Random prose sampling for stratified line-editing review (prose filtering, `--seed`, context lines) |
| `scripts/fix_proto.py` | Auto-enforce `\proto{}` markup; skips quotes/epigraphs/transcriptsrc/headings; `--dry-run` audit mode |
| `scripts/render_cover.py`, `regenerate_cover_background.py` | Cover art + 300-DPI background regeneration |
| `scripts/extract_tikz_figures.py`, `scripts/search_emails_*.py` | Figure extraction; mailing-list mining for chapters |
| `latex/scripts/update_kdp_cover_vars.py` | Reads interior PDF page count → spine width vars |
| `latex/scripts/generate_isbn_barcode.py` | ISBN barcode |
| `latex/scripts/ngram_analysis.py`, `find_duplicate_sentences.py`, `adjacent_sentence_repetition.py` | Earlier-generation prose QA (superseded by check_prose.py) |
| `src/archive_mailing_lists.py`, `imap_mirror_all.py`, `mail_to_jsonl.py`, `eml_to_jsonl.py`, `mailarchive_fetch.py` | Primary-source corpus building (IETF mail archives → JSONL) |
| `src/knowledge_graph/*` | Entity/edge KG over research corpus |

No pyproject/uv.lock — everything uses `uv run --with ...` or PEP 723 headers. `docs/SCRIPTS.md` documents book_stats/sample_text/check_prose in depth.

---

## 6. Metadata & Publishing

`docs/KDP-PREP.md` is a complete, verified publishing runbook (June 2026):

- **Files:** `main-interior.pdf` (6×9, 434pp, no bleed, all fonts embedded CID Type 0C, no Type 3 — verify with `pdffonts`) + `kdp-cover-cmyk.pdf` (13.287"×9.25" = 2×6" + 1.0374" spine + 2×0.125" bleed; PDF/X-1a:2001 CMYK).
- **Spine math documented:** `434 × 0.002252 + 0.06`; regenerate cover vars + background whenever page count changes.
- **Barcode:** white quiet-zone box reserved lower-right of back cover for KDP's auto barcode.
- **AI-content disclosure reasoning** (quotable policy): "This book is **AI-assisted**: the author directed research, drafting, and revision with Claude Code… Select AI-assisted in the KDP AI-content question." Plus an in-book disclosure in the Author's Note, and the determination that Python-rendered cover/diagrams are "algorithmic, author-created, not AI image generation."
- **Listing metadata drafted:** full sales description, BISAC categories (`COM018000` Computers›History, `COM043050` Security›Networking, `TEC052000` Tech&Eng›History), 7 keyword slots (`internet history nonfiction`, `tcp ip dns bgp protocols`, …), pricing guidance (~$5–6 print cost at 434pp → $16.99–22.99 list).
- **Pre-upload checklist** ending with "Order a physical proof before going live."
- ISBNs: 979-8-9947460-0-4 (paperback) / -1-1 (ebook), own-ISBN route; PCIP data with LCC/DDC classification on copyright page.
- Release naming convention: `Rough Consensus - YYYYMMDD-HHMM - {PRINT|PRINT-BLEED|EBOOK|EPUB}.{pdf,epub}` in `build/`.

---

## 7. Style / Craft / AI-Tone Guides

The most developed style system of the two projects — ~20 docs:

### docs/SPIRIT.md — "the soul of the book"
Unique doc type: defines the *feeling* before the rules. Title's promise, unified thesis, **two emotional threads** (The Contrast/grief: "Four nodes became five billion users"; The Miracle/awe: "It still works, every day, despite everything") with the instruction "**Every paragraph you write should touch at least one.**" Maps the reader's journey (curiosity+anxiety → unease → "awe and fragile hope") and the second-person implication device: "The reader isn't observing the internet. They're in it… 'Right now, as you read this…'". Defines the "And Yet" chapter coda.

### docs/STYLE.md
Voice ("we" for shared discovery; third-person present-tense for vignettes; never second-person commands), tense discipline (present = mechanism, past = events, no drift), sentence-length table (avg 15–20, max 35, occasional 3–8 for punch), one-idea rule with a nuanced "combined related facts" counter-example, front-loading, banned openers. Coffee test: "If it sounds like a textbook, a corporate security briefing, or a TED talk, rewrite it."

### docs/STYLE-AI-TELLS.md (720 lines) — the anti-AI-detection manual
Grounded in perplexity/burstiness research with citations, including the note that Claude's tells differ from ChatGPT's. Cataloged syntactic tells, each with pattern, fix, and a hard **rule**:

- "This" disease — "Maximum one 'This' opener per paragraph. Zero in consecutive sentences."
- Gerund openers — "Maximum one per page. Never consecutive."
- "As X, Y" constructions — max one per page.
- **The Triple Structure** — "AI loves threes… Use two sometimes. Use four occasionally."
- Filler transitions (banned list: "That said, / With that in mind, / Against this backdrop, …")
- Hedging clusters ("might potentially → might"), false balance ("Don't default to 'both sides.' Make claims."), nominalizations ("made a decision → decided"), rhetorical-question setups.

### The rest of the STYLE family
`STYLE-CRAFT.md` (rhythm, transitions, historical writing), `STYLE-RHYTHM.md` (fixing staccato prose — sentence-combining), `STYLE-VELOCITY.md` (keeping momentum in technical explainer sections), `STYLE-REFERENCE.md` (extended examples), `PROSE-EDITING-RULES.md`, `REPETITION-AND-FATIGUE-GUIDE.md` + `REPETITION-AUDIT.md`, `READABILITY.md` (research-backed benchmarks with sources: avg 15–18 words/sentence per Oxford Plain English; 75–150 words/paragraph; chapters 2,500–3,500 words — "nonfiction bestseller lengths have dropped 42% in the past decade"; 0.8–1.5 visuals per 1000 words).

### Process docs
`WRITING-PROCESS.md` — the 8-step per-chapter workflow bound to the **A-B-A′(-C) chapter architecture** (A: Creation Story ~6pp novelistic; B: Mechanism ~8–10pp explainer; A′: Breach ~6pp narrative; C: "And Yet" coda), with agent assignments per step and "When to Skip" columns (`fact-check`: "Never skip"). `FIGURE-STYLE.md` + `DIAGRAMS.md` (visual language for TikZ figures), `CITATION-METHODOLOGY.md` (see §8), `EPUB-CONVERTER-PLAN.md` (1,032-line design doc for the converter), `sources.md` (816-line research source inventory).

### CLAUDE.md
Compact orchestrator (243 lines vs legal-tech's sprawl): date-awareness header ("Trust `/data0/reference/` data over memory"), thesis + emotional threads + A-B-A'-C table, prioritized doc-reading table (CRITICAL/High/Reference), script usage blocks, 22-agent phase table, style quick-reference (banned words include domain-specific `cyber`, "Bad actors", "In the world of cybersecurity"), **local source-material map** (`/data0/reference/rfc/` 9,398+ RFCs, rfc.jsonl metadata, CVE archive, CISA KEV), LaTeX quick reference with the `\proto{}` convention, current status metrics, and the 10-step workflow.

### research/
Per-chapter dirs with **section-aligned templates** in `research/_templates/`: `section-a-research.md`, `section-a-sources.md`, `section-a-vignettes.md`, `section-a-prime-incident-timeline.md`, `section-b-diagrams.md`, etc. — research scaffolding shaped by the chapter architecture. `_shared/` has people/, organizations/, themes/, knowledge_graph/, narrative_connections.md; special dirs `cve-integration/`, `primary-source-verification/`, `institutional-health-2025/`. `RESEARCH-GUIDE.md` + `PROMPT.md` define methodology.

---

## 8. QA / Review Workflow

Quantified and multi-round — the most mature part of the project:

1. **Metrics-driven TODO.md**: a full audit table per chapter (words, citations, visuals, quality score /100) with severity-ranked issues (length outliers, chapters missing visuals, 21/25 chapters missing citations at the time) — a machine-generated review plan.
2. **Automated prose QA**: `check_prose.py` (n-grams, sentence starts, duplicates, adjacent repetition; severities; grep/jsonl outputs; CI exit codes) + `book_stats.py` before/after deltas + `sample_text.py` stratified sampling + `fix_proto.py` markup enforcement.
3. **Citation verification** (`docs/CITATION-METHODOLOGY.md`): classify every claim (OBVIOUS / RFC-VERIFIABLE / HISTORICAL / STATISTICAL / BIOGRAPHICAL), verify against local primary corpora first (RFC archive jsonl, mailing lists, oral histories) before web; claims-inventory format with line numbers. Results tracked in `notes/citation-review-*.md`.
4. **Review rounds as artifacts**: `docs/review-02/`, `docs/review-03/` contain per-chapter review files (01-arpanet.md … 23-robots-txt.md), batched agent-review rollups (`AGENT-REVIEWS-ch03-06.md`…), `00-HOLISTIC-REVIEW.md`, `01-PRIORITIES.md`, `02-ROUND4-SYNTHESIS.md`, `03-EXTERNAL-REVIEW-DELTA.md`, `05-REVISION-COORDINATION.md`, plus a round-scoped TODO. `docs/manuscript-review-2026-03-16.md` is a dated full-manuscript review.
5. **Build validation**: `make validate` (trim size, undefined refs/citations, overfull boxes), `make kindle-validate` (epubcheck), `make epub-check` (unhandled macro coverage), `pdffonts` embedding check per KDP-PREP.
6. **Pre-publication checklist** in KDP-PREP.md, ending in a physical proof order.

---

## 9. Verdict

### Best reusable pieces for a master template
1. **The 810-line Makefile** — the single most valuable artifact: one command surface covering print/bleed/prerelease/grayscale/BW/ebook/EPUB/Kindle/KDP-interior/KDP-cover/CMYK, with timestamped releases to `build/`, pdfinfo reporting, and `validate`. Lift nearly verbatim; parameterize `BOOK_TITLE`, trim size, paper formula.
2. **KDP-PREP.md as a runbook genre** — verified specs, spine-width formula wired to actual page count (`update_kdp_cover_vars.py`), CMYK/PDF-X conversion recipe, AI-disclosure policy, listing metadata, checklist.
3. **Multi-target document set**: main.tex / main-interior.tex / main-ebook.tex sharing one preamble + mode flags (`\BleedMode`/`\EbookMode`/`\PreReleaseMode`/`\GrayscaleMode`) injected via `-jobname` + `\def...\input`.
4. **The prose-QA toolchain**: check_prose.py + book_stats.py (+ before/after-delta convention) + sample_text.py + a domain-markup enforcer (fix_proto.py pattern generalizes to any `\keyterm`-style convention). All PEP 723/uv, zero-install.
5. **SPIRIT.md as a doc type** (emotional threads before style rules) + **STYLE-AI-TELLS.md** (rule-per-tell anti-AI-pattern manual) — the strongest AI-tone guidance in either repo.
6. **Section-aligned research templates** (`section-a-*.md`, `section-b-*.md`, `section-a-prime-*.md`) — research scaffolding derived from the chapter architecture.
7. **Cover-as-code**: matplotlib/networkx cover generators with style variants, single `make cover-image` feeding both print and EPUB.
8. **EPUB converter's `generators.py`** (nav/OPF/front-matter generated from book structure → epubcheck-compliant) and `make epub-check` handler-coverage audit.
9. **Fonts**: the full IBM Plex fontspec block (optical sizes, SemiBold-as-bold, per-family figure styles) and the tuned microtype protrusion table.
10. **Narrative architecture in main.tex comments** (per-part trust model/tempo, per-chapter breach pairing) — main.tex doubles as the book's structural outline.
11. **Metrics-driven TODO/review-round file conventions** (`docs/review-NN/` with per-chapter files + synthesis + coordination docs).

### Pitfalls
- **Stale-metadata drift**: EPUB OPF has an old ISBN (`9798994345764`) and old subtitle ("Built—And Broke—") vs copyright.tex (979-8-9947460-0-4, "Built the Internet"); outline/ and epub template chapter numbering diverge from final chapter order. A template needs one metadata source (YAML/`book-meta.tex`) feeding LaTeX, OPF, and KDP copy.
- `latex/` doubles as build workdir — aux/log/pdf clutter beside sources (committed even). Template should build out-of-tree (the legal-tech book's `-output-directory=build` does this better).
- Legacy duplicate QA scripts in `latex/scripts/` superseded by `scripts/check_prose.py`; two knowledge_graph implementations (src/ and research/_shared/).
- The color system's family-name/value mismatch (`cyan-*` holding gold) is clever but a trap for future maintainers — a template should rename semantically.
- Hard dependencies on machine-local corpora (`/data0/reference/rfc/...`) baked into CLAUDE.md/docs — fine for one machine, breaks portability.
- No pyproject/lockfile — `uv run --with` strings duplicated across Makefile targets.
- extbook (14pt) + `-shell-escape` needed only for the ebook target; note the tolerance of failure (`-$(LATEX) ...` third pass).

### Unique to this project
- Primary-source corpus tooling (IETF mailing-list archiver → JSONL → knowledge graph) feeding narrative research.
- TTY/RFC visual identity implemented consistently across LaTeX (styling/elements), EPUB CSS, and cover art.
- The A-B-A′-C chapter form with per-section research templates and agents.
- Full self-publishing terminal state: ISBNs, PCIP, CMYK cover, KDP listing copy, AI-disclosure policy.
