# Research Report: htsd-book ("How to Fight a Data Center")

Source project: `/home/mjbommar/projects/personal/htsd-book`
Reviewed: 2026-07-06. All paths below are absolute into the source project unless noted.

---

## 1. Purpose & status

**What it is.** *How to Fight a Data Center: A Citizen's Guide to Data Center Deals* by Michael J Bommarito II — a ~38,600-word (182-page, 6x9 US Trade) practical citizen's guide for residents and local officials facing proposed data center projects. Companion "what to do" volume to the narrative book *This Is Server Country*. Organized by "mechanism of action": government hierarchy (local/state/federal, all three branches plus elections/recall) crossed with a public-to-private spectrum (statutes -> agency action -> torts -> contracts -> market pressure). Ten chapters plus glossary, sample-documents, and resources appendices.

**Publication status.** Published. First Edition, February 2026; **Second printing (revised June 2026)** shipped as an in-place KDP content update (page count moved 176 -> 182, under KDP's 10% new-edition threshold, so same ISBNs). From `/home/mjbommar/projects/personal/htsd-book/releases/second-printing-2026-06/README.md`:

> This printing is a revised reprint of the First Edition (February 2026): an em-dash copyedit plus the review-03 fact-check/persona pass. Same edition, same ISBNs — it stays within KDP's content-update threshold (no new edition).

**Formats and channels.**
- KDP paperback (ISBN 979-8-9947460-8-0) — interior PDF + full-wrap cover PDF
- Kindle eBook via custom-built EPUB (ISBN 979-8-9947460-7-3)
- Lulu/IngramSpark paperback provisioned (ISBN 979-8-9947460-9-7, Lulu cover-vars file present; hardcover supported by tooling)
- **Free PDF** on GitHub Pages (`github/` dir: `index.html`, `how-to-fight-a-data-center.pdf`, cover.png, `.nojekyll`), Amazon listing at `https://www.amazon.com/dp/B0GQ1LTX1S`

**Licensing.** The free-distribution text is **CC BY-NC-SA 4.0** (`/home/mjbommar/projects/personal/htsd-book/github/LICENSE`), while the print copyright page (`latex/front-matter/copyright.tex`) is standard "All rights reserved" — dual-track: commercial editions reserved, GitHub PDF share-alike noncommercial.

---

## 2. Directory layout

```
htsd-book/
├── CLAUDE.md                  # Full agent instructions (213 lines): premise, principles, style quick ref, banned words
├── AGENTS.md                  # Condensed repo guide (73 lines) — same content, different framing
├── GEMINI.md                  # Gemini CLI variant (53 lines) — same rules, condensed again
├── README.md                  # EMPTY (0 lines) — public README lives in github/
├── pyproject.toml             # uv-managed Python env (requests, bs4, playwright, rich...)
├── docs/
│   ├── METADATA.md            # 502-line publishing dossier: ISBNs, BISAC, keywords, pricing, descriptions
│   ├── FRAMEWORK.md           # Organizing matrix (gov hierarchy x public-private spectrum) + coverage map
│   ├── STYLE.md               # Voice/grammar/banned words/reading level (528 lines)
│   ├── STYLE-CRAFT.md         # Guide-writing craft: burstiness, hooks, uncertainty framing (501 lines)
│   ├── STYLE-AI-TELLS.md      # AI-pattern detection signatures + bans (380 lines)
│   ├── CALLOUT-BOXES.md       # Governing rules for every callout box (193 lines)
│   ├── WRITING-PROCESS.md     # 7-phase workflow with exit criteria (602 lines)
│   ├── sources.md             # Source hierarchy + verification protocol
│   ├── cite-check.md          # Bibliography verification process ("Playwright or it didn't happen")
│   ├── fact-check.md          # Claim-extraction/batch-verification process
│   ├── review-01/             # Multi-model review pass: gemini.md, gemini-5.1.md, gpt-5.2.md, gpt-5.3.md,
│   │                          #   grok-4.1.md, cite-check-chN.md, claim-verification.md, date-claims-audit.md,
│   │                          #   numeric-claims-catalog.md, style-violations{,-gpt53}.tsv, triggers.md
│   ├── review-02/             # Citation audit: citation_audit_report.md, citation_fix_todo.md,
│   │                          #   cite_audit_static.json, date_claim_flags.json, sibling_project_citations.json
│   ├── review-03/             # Per-chapter persona-panel syntheses: intro + ch01..ch10-synthesis.md
│   └── reviews-02/            # Persona reviews: 00-synthesis, 01-wsj, 02-new-yorker, 03-kirkus,
│                              #   04-township-supervisor, 05-community-organizer, 06-energy-reporter
├── notes/
│   ├── structure.md           # Chapter outline, target specs, per-chapter word budgets
│   └── audience.md            # Reader personas (reluctant activist, confused official, ...)
├── research/
│   ├── chapters/              # Per-chapter research notes
│   └── fact-check-2026-06/    # June 2026 fact pass: AGENT-INSTRUCTIONS.md, COPYEDIT-INSTRUCTIONS.md,
│                              #   00-canonical-figures.md, per-chapter provenance logs (ch01..ch10, front/back)
├── latex/
│   ├── main.tex               # Master doc: book class, front/main/back matter includes
│   ├── Makefile               # 453-line build system (pdf/quick/full/bleed/kdp/lulu/epub/validate...)
│   ├── .latexmkrc             # LuaLaTeX + biber config
│   ├── preamble/              # packages.tex, colors.tex, styling.tex, commands.tex
│   ├── front-matter/          # title, copyright, dedication, toc, introduction
│   │   └── cover/             # kdp-cover-vars.tex, lulu-paperback-cover-vars.tex (auto-generated)
│   ├── chapters/              # 01-you-just-found-out.tex ... 10-fight-on-every-front.tex (NN-slug.tex)
│   ├── back-matter/           # appendix-glossary/-resources/-sample-documents/-state-reference,
│   │                          #   bibliography.tex, isbn-barcode.{pdf,png}
│   ├── bib/refs.bib           # ~104 biblatex entries
│   ├── figures/               # front-cover.jpg, sullivan-cover.png
│   ├── kdp-cover.tex          # Full-wrap cover (back+spine+front) — shared by KDP and Lulu via \def switches
│   └── cover-standalone.tex   # Front-cover-only 6x9 page -> JPEG for EPUB/Kindle thumbnail
├── epub/
│   ├── converter/             # Custom LaTeX->EPUB converter (TexSoup + lxml + typer): cli, parser,
│   │   │                      #   document, renderer, context, types
│   │   └── handlers/          # macros, environments, math, references, figures + htsd_macros, htsd_environments
│   ├── scripts/package_epub.py
│   ├── templates/             # content.opf, nav.xhtml, stylesheet.css, per-page XHTML, fonts/ (EB Garamond
│   │                          #   OTFs), images/icons/*.png (7 callout icons), images/cover.jpg
│   ├── build/                 # Converter output XHTML
│   ├── META-INF/container.xml
│   └── how-to-fight-a-data-center.epub
├── scripts/                   # check_style, check_repetition, check_adjacent_repetition, book_stats,
│                              #   fetch_url, generate_isbn_barcode, update_cover_vars
├── github/                    # GitHub Pages free-PDF site: index.html, README.md, LICENSE (CC BY-NC-SA),
│                              #   cover.png, how-to-fight-a-data-center.pdf, .nojekyll
└── releases/second-printing-2026-06/   # interior.pdf, cover.pdf, .epub, README.md, SHA256SUMS
```

Notable: the root `README.md` is empty — the public-facing README is `github/README.md`. Chapters carry inline `%CITE:` provenance comments (source, URL, access date) next to the claims they support; these are machine-audited (review-02) and kept current by fact-check agents.

---

## 3. LaTeX pipeline

### Document class and structure

`/home/mjbommar/projects/personal/htsd-book/latex/main.tex`:

```latex
\documentclass[11pt,twoside,openright]{book}

% Load preamble files
\input{preamble/packages}
\input{preamble/colors}
\input{preamble/styling}
\input{preamble/commands}
```

Front matter suppresses blank verso pages by temporarily aliasing `\cleardoublepage` to `\clearpage`, then restores `openright` for main matter — a neat trick worth keeping:

```latex
\frontmatter
% Prevent blank pages in front matter
\let\origcleardoublepage\cleardoublepage
\let\cleardoublepage\clearpage
...
% Restore openright behavior for main matter
\let\cleardoublepage\origcleardoublepage
\mainmatter
```

### Geometry (US Trade 6x9)

`/home/mjbommar/projects/personal/htsd-book/latex/preamble/packages.tex`:

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

### Fonts (engine-detected fontspec, EB Garamond body + Libertinus math)

```latex
\ifluatex
    \usepackage{fontspec}
    \setmainfont{EB Garamond}[
        Path           = /usr/share/texlive/texmf-dist/fonts/opentype/public/ebgaramond/,
        UprightFont    = EBGaramond-Regular.otf,
        ItalicFont     = EBGaramond-Italic.otf,
        BoldFont       = EBGaramond-Bold.otf,
        BoldItalicFont = EBGaramond-BoldItalic.otf,
    ]
    \usepackage{libertinust1math}
    \setmonofont{Latin Modern Mono}[Scale=MatchLowercase]
\else\ifxetex
    ... (identical fontspec block) ...
\else
    \usepackage[utf8]{inputenc}
    \usepackage[T1]{fontenc}
    \usepackage{ebgaramond}
    \usepackage{libertinust1math}
\fi\fi

% Improved micro-typography
\usepackage[nopatch=footnote]{microtype}
```

Pitfall for a template: the hard-coded TeX Live font path (`/usr/share/texlive/...`) makes the build machine-specific.

Body leading is customized to 11pt/13.5pt (123%) by redefining `\normalsize`, with `\parindent=1.5em`, `\parskip=3pt plus 1pt minus 0.5pt`, `\raggedbottom`, `\widowpenalty=10000`, `\clubpenalty=10000`, `\emergencystretch=2em`, `tolerance=1000`.

### Hyperref (print-black links) and PDF metadata

```latex
\usepackage{hyperref}
\hypersetup{
    colorlinks=true,
    linkcolor=black,
    citecolor=black,
    urlcolor=black,
    pdftitle={How to Fight a Data Center},
    pdfauthor={Michael J Bommarito II},
    pdfsubject={Data Center Citizen's Guide},
    pdfkeywords={data center, zoning, moratorium, community engagement, infrastructure, energy, water}
}
```

Also loaded: babel/csquotes, graphicx/float/wrapfig/subcaption, TikZ (calc, positioning, shapes.geometric, arrows.meta), booktabs/longtable/tabularx, enumitem, `\usepackage[most]{tcolorbox}`, **fontawesome5** (grayscale-friendly callout icons), url, cleveref, fancyhdr, titlesec, epigraph, lettrine (drop caps), setspace, quoting, ifdraft + draftwatermark.

### Headers/footers

```latex
\fancypagestyle{plain}{%
    \fancyhf{}
    \fancyfoot[C]{\thepage}
    \renewcommand{\headrulewidth}{0pt}
    \renewcommand{\footrulewidth}{0pt}
}

\fancypagestyle{body}{%
    \fancyhf{}
    \fancyhead[LE]{\small\textit{\leftmark}}
    \fancyhead[RO]{\small\textit{\rightmark}}
    \fancyfoot[LE,RO]{\thepage}
    \renewcommand{\headrulewidth}{0.4pt}
    \renewcommand{\footrulewidth}{0pt}
}
```

### Chapter styling (spelled-out chapter numbers)

`packages.tex` defines a word-number command:

```latex
\makeatletter
\newcommand{\chapterword}{%
    \ifcase\value{chapter}\or ONE\or TWO\or THREE\or FOUR\or FIVE\or SIX%
    \or SEVEN\or EIGHT\or NINE\or TEN\or ELEVEN\or TWELVE\or THIRTEEN%
    \or FOURTEEN\or FIFTEEN\or SIXTEEN\or SEVENTEEN\or EIGHTEEN\fi
}
\makeatother
```

`/home/mjbommar/projects/personal/htsd-book/latex/preamble/styling.tex`:

```latex
% Right-aligned, two-line chapter format:
%   CHAPTER ONE
%   What Is a Data Center?

\titleformat{\chapter}[display]
    {\raggedleft\normalfont}
    {\scshape\large CHAPTER \chapterword}
    {0.5em}
    {\huge\bfseries}

\titlespacing*{\chapter}{0pt}{30pt}{25pt}

\titleformat{\section}
    {\normalfont\large\bfseries\scshape}
    {\thesection}{1em}{}

\titleformat{\subsection}
    {\normalfont\normalsize\bfseries\itshape}
    {\thesubsection}{1em}{}
```

TOC uses titletoc with `\setcounter{tocdepth}{0}` (chapters only) and dotted-leader chapter entries. Quote environment is redefined to small italic with 1.5em margins; epigraphs flush right, `\epigraphrule=0pt`, width 0.75\textwidth. Lettrine defaults to 2-line drop caps. `\cleardoublepage` is patched so blank versos get `\thispagestyle{empty}`.

### Colors — deliberately grayscale for cheap B&W print

`/home/mjbommar/projects/personal/htsd-book/latex/preamble/colors.tex` (entire file is grayscale):

```latex
% Standard box style — light gray fill, dark border
\definecolor{boxbg}{RGB}{245, 245, 245}
\definecolor{boxborder}{RGB}{60, 60, 60}

% Caution box — slightly darker to stand out as a warning
\definecolor{cautionbg}{RGB}{230, 230, 230}
\definecolor{cautionborder}{RGB}{0, 0, 0}

% Plain English definition boxes
\definecolor{definitionbg}{RGB}{245, 245, 245}
\definecolor{definitionborder}{RGB}{0, 0, 0}
```

### Callout box environments (the signature feature)

`/home/mjbommar/projects/personal/htsd-book/latex/preamble/commands.tex` — all seven boxes are tcolorbox with FontAwesome icons for grayscale differentiation. Representative definitions verbatim:

```latex
% Key Fact box
\newtcolorbox{keyfact}[1][]{%
    colback=boxbg,
    colframe=boxborder,
    fonttitle=\bfseries,
    title={\faIcon{info-circle}\hspace{6pt}Key Fact},
    boxsep=3pt, top=3pt, bottom=3pt, left=5pt, right=5pt,
    before skip=8pt, after skip=8pt,
    #1
}

% Takeaway box (end-of-chapter action items)
\newtcolorbox{takeaway}[1][]{%
    ... title={\faIcon{clipboard-check}\hspace{6pt}What You Can Do}, ...
}

% Checklist box
\newtcolorbox{checklist}[1][]{%
    ... title={\faIcon{clipboard-list}\hspace{6pt}Checklist}, ...
}

% Tip/Advice box
\newtcolorbox{tip}[1][]{%
    ... title={\faIcon{lightbulb}\hspace{6pt}Tip}, ...
}

% Warning/Caution box
\newtcolorbox{caution}[1][]{%
    colback=cautionbg,
    colframe=cautionborder,
    boxrule=1.2pt,
    fonttitle=\bfseries,
    title={\faIcon{exclamation-triangle}\hspace{6pt}Caution},
    boxsep=3pt, top=3pt, bottom=3pt, left=5pt, right=5pt,
    before skip=8pt, after skip=8pt,
    #1
}

% "What This Means for You" box
\newtcolorbox{whatthismeans}[1][]{%
    ... fonttitle=\bfseries\itshape,
    title={\faIcon{hand-point-right}\hspace{6pt}What This Means for You}, ...
}

% Example/Case Study box
\newtcolorbox{casestudy}[1][]{%
    ... title={\faIcon{book-open}\hspace{6pt}Case Study}, ...
}
```

Plus a distinctive two-column inline glossary box that does NOT count against the 3-box budget:

```latex
% Plain English definition box — vocabulary aid in a full box
\newtcolorbox{plainenglish}[2][]{%
    colback=definitionbg,
    colframe=definitionborder,
    boxrule=0.75pt,
    left=6pt, right=5pt, top=3pt, bottom=3pt,
    boxsep=2pt,
    before skip=6pt, after skip=6pt,
    fontupper=\small,
    before upper={%
        \begin{minipage}[t]{0.22\linewidth}%
            \raggedright\textbf{#2}%
        \end{minipage}%
        \hspace{0.03\linewidth}%
        \begin{minipage}[t]{0.73\linewidth}%
    },
    after upper={\end{minipage}},
    #1
}
```

### Custom commands

Also in `commands.tex`: `\emdash`/`\ndash`/`\ellip`; `blockquote` env + `\attributed{quote}{who}` (quoting-based); `\scenebreak` (short centered rule); `\chapterquote{q}{who}` (epigraph wrapper); `\chapref`/`\figref`/`\tabref`/`\secref`/`\seeref`/`\seepage`; domain units `\MW`/`\GW`/`\TWh`/`\kW` (thin nbsp + xspace); `\dollars{}`; `\state{}` and `\keyterm{}` (bold/smallcaps + `\index`, index currently disabled); `\stat{n}{unit}`; draft-gated `\TODO`/`\NOTE`/`\VERIFY`/`\editnote`/`\citeneeded` (expand to nothing in final builds); `\placeholder{}`; and an `\unnumberedchapter{label}{title}` command reproducing the chapter look for Introduction/Conclusion with TOC + running-head registration.

### Chapter conventions

Files named `NN-slug.tex` (e.g. `latex/chapters/03-fight-at-city-hall.tex`). Each opens with a comment header stating coverage and reading-level target, then `\chapter{...}` + `\label{ch:...}`, a cold-open anecdote written one-sentence-per-line, inline `%CITE:` provenance comments after claims, `plainenglish` boxes for jargon on first use, and a closing `takeaway` environment with 3-5 bold-led enumerated action items.

### Front/back matter

Front: title page (`titlepage` env, centered), copyright (ISBNs, no-legal-advice disclaimer, cover-art credit to an 1883 Library of Congress boxing lithograph), dedication, TOC, and an introduction rendered via `\unnumberedchapter`. Back: three appendices (glossary in multicol, sample documents, resources), a fourth appendix (state reference) that exists but is not in `main.tex`, and `bibliography.tex`:

```latex
\chapter*{Bibliography}
\addcontentsline{toc}{chapter}{Bibliography}
\markboth{Bibliography}{Bibliography}
\printbibliography[heading=none]
```

(Note: biblatex/biber via `.latexmkrc`; `bibliography.tex` currently not `\input` in main.tex — references ship in the EPUB and via `%CITE` comments.)

### ISBN barcode

`scripts/generate_isbn_barcode.py` (python-barcode + Pillow, 300 DPI, custom text rendering) writes `latex/back-matter/isbn-barcode.{pdf,png}`; the wrap cover includes it:

```latex
% --- ISBN Barcode (bottom right) ---
\node[anchor=south east, inner sep=0pt]
    at ($ (back-sw) + (5.6in, 0.2in) $) {%
    \includegraphics[height=0.75in]{back-matter/isbn-barcode.pdf}%
};
```

### KDP + Lulu print covers

One cover source, `latex/kdp-cover.tex`, serves three products via `\def` switches set by the Makefile:

```latex
\ifdefined\LuluHardcover
    \input{front-matter/cover/lulu-hardcover-cover-vars}
\else\ifdefined\LuluCover
    \input{front-matter/cover/lulu-paperback-cover-vars}
\else
    \input{front-matter/cover/kdp-cover-vars}
\fi\fi

\usepackage[
    paperwidth=\CoverWidth,
    paperheight=\CoverHeight,
    margin=0pt
]{geometry}
```

The cover is one `tikzpicture[remember picture, overlay]` with three `scope`s (back cover, spine, front cover) positioned by computed lengths:

```latex
\setlength{\BackCoverStart}{\CoverBleed}
\setlength{\SpineStart}{\dimexpr\CoverBleed + \CoverTrimWidth\relax}
\setlength{\FrontCoverStart}{\dimexpr\CoverBleed + \CoverTrimWidth + \CoverSpineWidth\relax}
```

It must be compiled 3x (`remember picture`), then flattened to PDF 1.4 with Ghostscript (lossless FlateEncode, no downsampling) for KDP compatibility. Typography niceties: `\nohyphens` macro for back-jacket text, `pgfornament{82}` dividers, `\addfontfeature{LetterSpace=...}` display type, rotated spine text.

**Auto-generated cover vars.** `/home/mjbommar/projects/personal/htsd-book/latex/front-matter/cover/kdp-cover-vars.tex` (verbatim):

```latex
% ============================================================================
% COVER VARIABLES - Auto-generated for Amazon KDP Paperback
% ============================================================================
% Generated: 2026-06-14 07:40:26
% Platform: Amazon KDP | Binding: Paperback
% Paper: white | Pages: 182
%
% Amazon KDP Paperback Specifications:
%   - Trim size: 6.000" x 9.000"
%   - Bleed: 0.125"
%   - Spine width: 0.469864" (pages * 0.002252 + 0.06)
%   - Total cover: 12.719864" x 9.2500"
%
% Layout: [Bleed] [Back Cover] [Spine] [Front Cover] [Bleed]
%         0.125"    6.000"     spine     6.000"      0.125"
% ============================================================================

\newlength{\CoverTrimWidth}
\newlength{\CoverTrimHeight}
\setlength{\CoverTrimWidth}{6.000in}
\setlength{\CoverTrimHeight}{9.000in}

\newlength{\CoverBleed}
\setlength{\CoverBleed}{0.125in}

\newlength{\CoverSpineWidth}
\setlength{\CoverSpineWidth}{0.469864in}

\newlength{\CoverWidth}
\newlength{\CoverHeight}
\setlength{\CoverWidth}{12.719864in}
\setlength{\CoverHeight}{9.2500in}

\newcommand{\CoverPageCount}{182}
\newcommand{\CoverPaper}{white}
\newcommand{\CoverPlatform}{kdp}
\newcommand{\CoverBinding}{paperback}
```

`lulu-paperback-cover-vars.tex` is identical in shape with the Lulu formula (verbatim header excerpt):

```latex
% Platform: Lulu | Binding: Paperback
% Paper: white | Pages: 168
%   - Spine width: 0.438378" ((pages / 444) + 0.06)
%   - Total cover: 12.688378" x 9.2500"
...
\setlength{\CoverSpineWidth}{0.438378in}
\setlength{\CoverWidth}{12.688378in}
```

`latex/cover-standalone.tex` renders just the front cover as a single 6x9 page; `make cover-image` converts it with `pdftoppm -jpeg -r 300` into `epub/cover.jpg` for the ebook.

---

## 4. EPUB pipeline (custom LaTeX-to-EPUB converter)

Located at `/home/mjbommar/projects/personal/htsd-book/epub/converter/` — a from-scratch, dependency-light Python package run via `uv run --with TexSoup,lxml,typer,rich python -m converter`. No Pandoc.

### Architecture

- **`parser.py`** — wraps TexSoup with a preprocessing pass (strips comments outside verbatim/tikz, escapes shell-prompt `$` lines that TexSoup would read as math) and node-inspection helpers (`is_macro`, `get_env_content`, `get_macro_args`, ...).
- **`document.py`** — book model: `Chapter` and `Book` dataclasses; **first pass** over all chapters collects `\label` cross-references and parses `refs.bib` (own minimal BibTeX parser, supports a directory of .bib files, assigns citation numbers).
- **`context.py`** — `RenderContext` dataclass threaded through all handlers: chapter/section counters, figure/equation/footnote counters, label and citation indices, element stack, math/verbatim flags, duplicate-id tracking, collected warnings.
- **`renderer.py`** — walks the TexSoup AST, dispatches to registered handlers, and builds an lxml XHTML DOM directly (XHTML + `epub:` namespaces). Paragraph management is solved with **typed handler results** (`types.py`): handlers return `BlockElement` (closes open `<p>`, appended to parent), `InlineElement`/bare element (goes inside current `<p>`), `str`, or `None`. `is_block_result()` also recognizes inherently block tags.
- **`handlers/__init__.py`** — decorator registry: `@macro_handler("name")` / `@env_handler("name")` into global dicts; importing the handler modules triggers registration. Generic modules (`macros.py`, `environments.py`, `math.py`, `references.py`, `figures.py`) plus **book-specific** `htsd_macros.py` and `htsd_environments.py` — the extension point a template should keep as `<project>_macros/<project>_environments`.
- **`cli.py`** (typer) — `convert` (single file), `book` (whole book: chapters dir + `-b` bib + `-f` front-matter + `-k` back-matter; maps front-matter filenames to canonical XHTML names and `epub:type` values, e.g. `copyright.tex -> copyright.xhtml` with `epub:type="copyright-page"`), and `epub` (packaging: builds mimetype-first ZIP, writes container.xml inline, copies template fonts/images/stylesheet, and **generates content.opf and nav.xhtml dynamically** via `generate_content_opf`/`generate_nav_xhtml`).

### Callout mapping (LaTeX tcolorbox -> HTML aside)

`handlers/htsd_environments.py` maps all seven callouts plus `plainenglish` through one builder:

```python
def _make_callout_box(node, ctx, css_class, title):
    """
    <aside class="callout {css_class}">
      <h4 class="callout-title"><img class="callout-icon"
           src="images/icons/{css_class}.png" alt=""/>{title}</h4>
      <div class="callout-content">...rendered content...</div>
    </aside>
    """
```

It honors tcolorbox-style `[title={...}]` optional args (custom titles like "Case Study: White County, Indiana") and works around TexSoup echoing bracket args into content. Icons are **embedded PNGs** (`epub/templates/images/icons/{tip,caution,keyfact,checklist,casestudy,takeaway,whatthismeans}.png`) because Kindle doesn't render FontAwesome — the print icons are baked into raster equivalents. `htsd_macros.py` mirrors every custom LaTeX macro (units, `\keyterm` -> `<dfn>`-style, `\chapref`/`\cref` -> internal links, `\autocite` -> superscript citation links, `\scenebreak`, `\chapterquote`, `\attributed`, accents, `\unnumberedchapter`, and no-op handlers for layout-only commands like `\pagestyle`, `\centering`).

### Packaging, fonts, cover, Kindle specifics

- `epub/scripts/package_epub.py` — standalone fallback packer: assembles OEBPS from `templates/`, writes `mimetype` first with `ZIP_STORED`, everything else deflated.
- Fonts: four **EB Garamond OTFs embedded** (`epub/templates/fonts/`), declared in the manifest as `application/vnd.ms-opentype` — print/ebook font parity.
- Cover: `cover.xhtml` + `images/cover.jpg` (from `make cover-image`), manifest `properties="cover-image"` plus legacy `<meta name="cover" content="cover-image"/>` and a `<guide>` block for older Kindle readers.
- Kindle: KDP ingests the EPUB directly ("Prefer EPUB upload" per METADATA.md); icons-as-images and embedded fonts are the two Kindle-compatibility concessions. The stylesheet includes an `@media (prefers-color-scheme: dark)` block restyling everything including callouts.
- Validation: comments reference epubcheck conventions ("landmarks self-reference is valid per epubcheck"); accessibility metadata targets EPUB Accessibility 1.1.

### content.opf metadata (verbatim excerpt, `epub/templates/content.opf`)

```xml
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
  <dc:identifier id="bookid">urn:isbn:9798994746073</dc:identifier>
  <dc:title>How to Fight a Data Center</dc:title>
  <dc:creator>Michael J Bommarito II</dc:creator>
  <dc:language>en-US</dc:language>
  <dc:publisher>Michael J Bommarito II</dc:publisher>
  <dc:date>2026</dc:date>
  <dc:rights>Copyright 2026 Michael J Bommarito II. All rights reserved.</dc:rights>
  <dc:subject>Data Centers</dc:subject>
  ...
  <meta property="dcterms:modified">2026-02-24T08:35:27Z</meta>
  <meta name="cover" content="cover-image"/>
  <!-- EPUB Accessibility 1.1 metadata -->
  <meta property="schema:accessMode">textual</meta>
  <meta property="schema:accessModeSufficient">textual</meta>
  <meta property="schema:accessibilityFeature">structuralNavigation</meta>
  <meta property="schema:accessibilityHazard">none</meta>
</metadata>
```

`nav.xhtml` has both `epub:type="toc"` and a hidden `epub:type="landmarks"` nav (cover / titlepage / bodymatter start).

### Stylesheet key rules (`epub/templates/stylesheet.css`)

```css
@font-face {
  font-family: "EB Garamond";
  font-style: normal;
  font-weight: 400;
  src: url("fonts/EBGaramond-Regular.otf");
}
/* ...Italic 400, Bold 700, BoldItalic 700 variants... */

body {
  font-family: "EB Garamond", Georgia, "Times New Roman", serif;
  font-size: 1em;
  line-height: 1.6;
  color: #1f2937;
}

p { margin: 0.5em 0; text-indent: 1.5em; }
p:first-child, h1 + p, ... aside + p, blockquote + p,
.scene-break + p, .epigraph + p { text-indent: 0; }   /* book-style indentation */

h1.chapter-title {
  font-size: 1.8em;
  text-align: right;                 /* mirrors the print chapter style */
  border-bottom: 2px solid #000000;
}
.chapter-label {
  font-size: 0.55em;
  font-variant: small-caps;
  letter-spacing: 0.15em;
}

.callout {
  margin: 1.5em 0;
  border: 1px solid #3c3c3c;
  background-color: #f5f5f5;
  page-break-inside: avoid;
}
.callout-title {
  font-weight: 700;
  padding: 0.4em 0.7em;
  background-color: #e8e8e8;
  border-bottom: 1px solid #3c3c3c;
}
.callout-icon { width: 1em; height: 1em; vertical-align: -0.1em; margin-right: 0.3em; }

.callout.caution { border-width: 1.5px; border-color: #000000; background-color: #e6e6e6; }
.callout.whatthismeans .callout-title { font-style: italic; }
.callout.plainenglish .definition-term { font-weight: 700; display: inline; margin-right: 0.6em; }
.callout.plainenglish .definition-content { font-size: 0.9em; display: inline; }
```

Grayscale palette deliberately matches print ("Grayscale palette for B&W print parity"), plus full dark-mode overrides.

---

## 5. Build automation

### Makefile (`/home/mjbommar/projects/personal/htsd-book/latex/Makefile`, 453 lines)

Target inventory (from the header comment, all verified present):

```make
#   make          - Build the complete book PDF
#   make pdf      - Same as above
#   make quick    - Single-pass build (for minor edits)
#   make bleed    - Build print-ready PDF with bleed margins
#   make release  - Build all formats with timestamps to ../build/
#   make ebook    - Build e-reader PDF (large font)
#   make epub     - Build EPUB format
#   make kdp      - Build all KDP files (interior + cover)
#   make watch    - Continuous compilation on file changes
#   make validate - Check for undefined references
#   make clean    - Remove auxiliary files
#   make cleanall - Remove all generated files including PDF
```

Plus `full` (3-pass + biber), `kdp-interior`, `kdp-cover`, `kdp-cover-vars`, `lulu-paperback-vars`, `lulu-hardcover-vars`, `lulu-paperback-cover`, `lulu-hardcover-cover`, `lulu-paperback`, `lulu-hardcover`, `lulu-all`, `isbn-barcode`, `cover-standalone`, `cover-image`, `wordcount`, `pagecount`, `help`. Key mechanics worth copying verbatim:

```make
CACHE_DIR = $(CURDIR)/.texlive-cache
export TEXMFCACHE := $(CACHE_DIR)
export TEXMFVAR := $(CACHE_DIR)

LATEXMK_OPTS = -lualatex -interaction=nonstopmode -file-line-error -halt-on-error -recorder

TEX_DEPS = $(TEXFILE) \
	$(wildcard preamble/*.tex) \
	$(wildcard front-matter/*.tex) \
	$(wildcard chapters/*.tex) \
	$(wildcard back-matter/*.tex) \
	$(wildcard figures/*) \
	$(wildcard tables/*.tex) \
	$(wildcard bib/*.bib)
```

Cover builds run LaTeX 3x with a `-jobname`, then Ghostscript-flatten:

```make
$(KDP_COVER_PDF): $(KDP_COVER_TEX) front-matter/cover/kdp-cover-vars.tex
	$(LATEX) $(LATEX_OPTS) -jobname=kdp-cover-raw $(KDP_COVER_TEX)
	$(LATEX) $(LATEX_OPTS) -jobname=kdp-cover-raw $(KDP_COVER_TEX)
	$(LATEX) $(LATEX_OPTS) -jobname=kdp-cover-raw $(KDP_COVER_TEX)
	gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 \
		-dDownsampleColorImages=false -dDownsampleGrayImages=false -dDownsampleMonoImages=false \
		-dAutoFilterColorImages=false -dColorImageFilter=/FlateEncode \
		-dAutoFilterGrayImages=false -dGrayImageFilter=/FlateEncode \
		-sOutputFile=$(KDP_COVER_PDF) kdp-cover-raw.pdf >/dev/null 2>&1
```

Lulu covers reuse the same .tex with a symbol define: `-jobname=lulu-pb-cover-raw "\def\LuluCover{1}\input{$(KDP_COVER_TEX)}"`. Bleed builds similarly: `\def\BleedMode{1}\input{main.tex}`. EPUB target:

```make
epub: cover-image
	cd ../epub && uv run --with TexSoup,lxml,typer,rich python -m converter book \
		../latex/chapters/ -o build/ -b ../latex/bib/refs.bib \
		-f ../latex/front-matter -k ../latex/back-matter -v
	cd ../epub && uv run --with TexSoup,lxml,typer,rich python -m converter epub \
		build/ -o how-to-fight-a-data-center.epub -t templates/
```

`validate` checks page size against "432 x 648 pts (6\" x 9\")" and greps `main.log` for undefined references/citations.

### .latexmkrc (verbatim, `/home/mjbommar/projects/personal/htsd-book/latex/.latexmkrc`)

```perl
# .latexmkrc - Configuration for latexmk
# Use LuaLaTeX with Biber backend

$pdf_mode = 4;  # Use lualatex
$lualatex = 'lualatex -interaction=nonstopmode -file-line-error -halt-on-error %O %S';
$biber = 'biber %O %S';
$bibtex_use = 2;  # Use biber

# Clean up auxiliary files
$clean_ext = 'aux bbl bcf blg fdb_latexmk fls log out run.xml synctex.gz toc lof lot idx ilg ind';
```

### scripts/*.py (all self-contained uv PEP-723 scripts)

| Script | Purpose |
|---|---|
| `scripts/check_style.py` | Style-guide linter for .tex files (rich tables): banned words/phrases from STYLE.md + STYLE-AI-TELLS.md (including adverb tells like "essentially/ultimately/notably"), sentence length (avg 12-18, max 30), paragraph length (max 5 sentences), AI-tell patterns ("This" disease, gerund openers, filler transitions), Flesch-Kincaid reading-level estimate. Exit criterion: zero violations per chapter. |
| `scripts/check_repetition.py` | Repeated 3-6-word n-grams, common sentence starts, duplicate sentences across chapters/research notes. Uses pydetex to strip LaTeX + nupunkt for sentence segmentation. |
| `scripts/check_adjacent_repetition.py` | Phrasing echoes: shared n-grams between adjacent sentence spans (`--span 2/3`) to catch unintended parallelism. |
| `scripts/book_stats.py` | Word count per chapter (LaTeX-stripped regex), totals, status table (rich). |
| `scripts/fetch_url.py` | Citation verification fetcher: Playwright Firefox headless with desktop UA/locale/timezone, extracts title/content as markdown, `--screenshot`, `--bibtex` (emits a BibTeX entry). The enforcement tool behind "NEVER claim a citation is verified without fetching it." |
| `scripts/generate_isbn_barcode.py` | EAN-13 ISBN barcode via python-barcode + Pillow at 300 DPI with custom ISBN text; writes `back-matter/isbn-barcode.{png,pdf}`. |
| `scripts/update_cover_vars.py` | Cover-dimension generator (see below). |

### update_cover_vars.py — spine math

Reads the page count from the interior PDF (`pdfinfo`, fallback `mutool info`), then:

```python
# KDP paperback
if paper == "white":
    spine = pages * 0.002252 + 0.06
else:  # cream
    spine = pages * 0.0025 + 0.06

# Lulu paperback — official formula from Lulu Developer Portal
if paper in ("white", "standard"):
    spine = (pages / 444) + 0.06
else:  # magazine/economy (460 PPI paper)
    spine = (pages / 460) + 0.06

# Lulu hardcover: 26-row lookup table by page range, e.g. (169, 194, 0.688)

PAPERBACK_BLEED = 0.125  # Standard bleed
HARDCOVER_BLEED = 0.875  # 0.75" wrap around boards + 0.125" bleed

total_width = 2 * trim_width + spine_width + 2 * bleed
total_height = trim_height + 2 * bleed
```

It emits a fully-commented `.tex` vars file (see section 3) so the cover source never hard-codes dimensions. Guard: KDP + hardcover is rejected; Lulu hardcover requires 24-799 pages.

### pyproject.toml (verbatim core)

```toml
[project]
name = "htsd-book"
version = "0.1.0"
description = "How to Fight a Data Center - A citizen's guide to data center engagement"
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
dev = ["pytest>=7.4.0", "ruff>=0.1.0"]

[tool.ruff]
line-length = 100
target-version = "py311"
```

Note the split strategy: repo-level deps for research tooling, but every script also carries its own PEP-723 header (e.g. `dependencies = ["pydetex>=1.1.1", "nupunkt>=0.6.0"]`), and the EPUB converter injects deps at invocation (`uv run --with TexSoup,lxml,typer,rich`). Nothing needs an installed package.

---

## 6. Metadata & publishing

### docs/METADATA.md — a complete retailer-form dossier

502 lines covering every field for KDP, Bowker, Lulu, IngramSpark. Key facts:

```
ISBN (eBook/Kindle):     979-8-9947460-7-3
ISBN (Paperback/KDP):    979-8-9947460-8-0
ISBN (Paperback/Ingram): 979-8-9947460-9-7
```

BISAC recommendations: `POL044000` (Public Policy / Science & Technology Policy), `LAW034000` (Environmental), `POL028000` (Political Advocacy). Seven KDP keyword slots filled with character counts, e.g. `` `data center opposition community resistance` (43 chars) ``. Pricing: paperback $17.99, Kindle $9.99, hardcover $29.99. AI disclosure guidance: "This book was written with AI assistance (Claude Code/Opus for research, drafting, and revision, as disclosed in the Introduction)." Description ladder from 4,000-char HTML (KDP-supported tags only) down to a one-liner:

> "The developer has done this before. Now so have you."

Print specifics: "Trim size 6x9, B&W on white, no bleed, matte cover"; spine-width dependency warning: "Don't finalize the full-wrap cover until the print PDF is locked." KDP Select warning (don't enroll if distributing via Lulu/Ingram), DRM off, plus a pre-publication checklist (assign ISBNs -> update copyright.tex -> update barcode script -> make isbn-barcode -> make kdp-interior -> make kdp-cover-vars -> make kdp-cover -> upload) and a "Quick Reference: Form Completion" table for filling every retailer field.

### releases/ practice

`releases/second-printing-2026-06/` contains exactly the three upload artifacts plus a README (quoted in section 1) and `SHA256SUMS`:

```
d5f19190...  how-to-fight-a-data-center-cover.pdf
7ed9a747...  how-to-fight-a-data-center-interior.pdf
3687da1f...  how-to-fight-a-data-center.epub
```

README documents specs (182 pp, spine 0.4699" = 182 x 0.002252 + 0.06, built 2026-06-14), and the KDP in-place-update procedure ("run the Print Previewer (the spine moved)"), ending with `sha256sum -c SHA256SUMS`.

### github/ — free-distribution GitHub Pages site

Static single-page site (`index.html`, self-contained CSS matching the cover palette — `--accent: #a44b43`, cream background, OpenGraph book metadata), `.nojekyll`, `cover.png`, the full PDF, `LICENSE` (CC BY-NC-SA 4.0 summary), and `README.md` marketing page with free-download link, chapter table, "Buy on Amazon" support link, and related-project links. Model: give the PDF away noncommercially, sell the paperback/Kindle.

### Cover process (both retailers)

1. `make pdf` / `make kdp-interior` — lock interior page count.
2. `make kdp-cover-vars` or `make lulu-paperback-vars` — regenerate dimension file from actual PDF page count.
3. `make kdp-cover` / `make lulu-paperback-cover` — 3 LaTeX passes + gs flatten; Lulu variant is the same .tex with `\def\LuluCover{1}`.
4. `make cover-standalone && make cover-image` — 6x9 front-only JPEG for EPUB/Kindle.

---

## 7. Style / craft / AI-tone guides

### CLAUDE.md vs AGENTS.md vs GEMINI.md — NOT identical

Three per-agent instruction files with the same substance at decreasing length: `CLAUDE.md` (213 lines: premise, reader persona, differentiation table vs the sibling book, core principles, comparable-books style models, essential-reading priority table, sibling-project data access commands, style quick reference, prohibited content); `AGENTS.md` (73 lines: generic repo guide with required reading and quality gates); `GEMINI.md` (53 lines: further condensed for Gemini CLI). All three carry the banned-word list and the fetch_url verification mandate. CLAUDE.md opens with a date-awareness line worth stealing: `**Today's date: June 2026** | **Knowledge cutoff: May 2025** — verify recent events.`

### The banned lists (from CLAUDE.md, enforced by check_style.py)

```
BANNED WORDS: delve, landscape (metaphorical), tapestry, leverage, utilize, paradigm,
ecosystem, pivotal, crucial, robust, unlock, harness, foster, embark, illuminate, unveil,
myriad, multifaceted, plethora, streamline, realm, intricate, holistic, synergy, optimize,
stakeholders, empower, navigate, toolkit, framework, actionable, roadmap, bustling, nuanced,
ever-evolving, comprehensive, seamless, cutting-edge, innovative, proactive, paramount

BANNED PHRASES: "It's important to note", "It should be noted", "Let's dive in", "dive deep",
"game-changer", "groundbreaking", "Indeed/Furthermore/Moreover/Additionally" as openers,
"That said", "With that in mind", "Moving forward", "Now you're ready to", "Knowledge is
power", "Make your voice heard", "Empower yourself", "The good news is", "While every
situation is different"
```

### STYLE.md — most distinctive rules

- **The Neighbor Test** (core principle): "Read it aloud. Does it sound like something a knowledgeable friend would say...? If it sounds like: A corporate press release -> Rewrite. An academic paper -> Rewrite. A TED talk -> Rewrite. An activist pamphlet -> Rewrite. A government brochure -> Rewrite."
- Voice ladder: "you" default; "we" for shared walkthroughs; imperatives for actions; third person for examples; never "One must consider...", "It is recommended that...", "Citizens should be aware that...", "Folks".
- Sentences: 12-18 words average, hard max 30 ("If you hit 30, split it"). One idea per sentence. Front-load the point.
- Paragraphs: 2-5 sentences; structure **Point -> Evidence -> Implication**.
- Tense discipline: "Never drift within a paragraph."
- Em dashes: "Maximum one per paragraph... a well-known AI tell." (The second printing was partly "an em-dash copyedit.")
- Reading level: 7th-9th grade Ch 1-5, 8th-10th Ch 6-10 (measured by FK in check_style.py).

### STYLE-AI-TELLS.md — detection-signature catalog

Framed around perplexity and burstiness ("A reader who suspects the text is AI-generated will trust it less—and a guide lives or dies on trust"). Numbered, rule-per-tell:

- 1.1 The "This" Disease — "Maximum one 'This' opener per paragraph. Never consecutive."
- 1.2 The Gerund Opener — "Maximum one gerund opener per page."
- 1.3 The "As X, Y" Construction — max one per page.
- 1.4 The Triple Structure — "AI loves threes... Avoid numbered lists (First/Second/Third) in prose. Vary grouping sizes."
- 1.5 The Filler Transition — banned list ("That said," "With that in mind," "Against this backdrop," ...): "Delete them. The sentence works without them."
- 1.6 The Hedging Cluster — "might potentially -> might"; "One hedge per paragraph maximum. When genuinely uncertain, name the uncertainty."
- 1.7 The False Balance — "Don't split the difference. Help readers think, don't think for them, and don't refuse to think."
- Parts 2-5: guide-specific tells (motivational closers, disclaimer sludge, hypothetical examples), word-level tells, a self-edit checklist, detection heuristics.

### STYLE-CRAFT.md

Eight parts: sentence craft (burstiness principle with annotated word counts, front-loading, active voice), paragraph craft (inverted pyramid, the "So what?" test — "Action items must name who to contact, what to ask for, and where to find it"), chapter craft (hooks, 60/40 explain/equip ratio), callout craft, handling complexity (the "Uncertainty Problem": don't cherry-pick or false-balance; ask who bears the downside risk), emotional calibration, before/after examples, manuscript-level craft.

### CALLOUT-BOXES.md — the governing spec

A box does exactly one of three jobs — **Warn**, **Clear up a common confusion**, **Tell the reader what to do right now** — "If a box does not do one of these three things, it does not belong in a box." Explicit not-for list (background, unused statistics, case studies as decorated paragraphs, summaries, motivation: "The reader's motivation is the data center being built next to their house. They don't need a pep talk."). Format rules: 3-5 sentences, max 80 words; never split across pages (tcolorbox non-breakable default); **max 3 boxes per chapter** plus the end-of-chapter `takeaway`; never consecutive; a title-customization table per environment ("casestudy: Always—name the place"). Ends with "The Box Test" (three questions; all no -> delete) and the LaTeX implementation pointer. Takeaway boxes: 3-5 one-sentence bullets, specific, named resources, standalone.

### FRAMEWORK.md

The two-dimensional coverage matrix: government hierarchy (local/state/federal x legislative/executive/judicial x in-office vs elections/recall) crossed with a public-to-private spectrum. Includes per-cell tool tables (e.g. "PUC elections — ~11 states (AL, AZ, GA, KS, LA, MN, MT, NE, ND, OK, SD)") and a chapter-to-cell coverage map so "No cell is left uncovered." This is the book's content-completeness QA artifact.

### WRITING-PROCESS.md

Seven phases — Research -> Outline -> Draft -> Review -> Revise (loop) -> Polish -> Verify — with explicit exit criteria:

```
A chapter exits the loop when:
- [ ] uv run scripts/check_style.py latex/chapters/XX-*.tex returns zero violations
- [ ] Every section passes the "Can the reader act on this?" test
- [ ] All examples are real communities with real outcomes
- [ ] Reading level is within target (7th-9th for Ch 1-5, 8th-10th for Ch 6-10)
- [ ] Takeaway box has 3-5 specific, timed, standalone action items
```

Includes an outline template (Framework Coverage / Reader's Question / Hook / Explain 60% / Equip 40% / Callout Boxes / Sources / Jargon Budget) and a review-report template (Usefulness Score 1-5, AI Tells Found, Legal Risk).

### notes/audience.md

Persona document: the **Reluctant Activist** and the **Confused Official** as primary readers (plus organizer, ratepayer), each with emotional state, knowledge level, needs, expected **reading pattern** ("Chapter 1 first. Then the chapter about whatever scared them..."), and a "What NOT to do with this reader" list. Personas later become the review panel.

---

## 8. QA / review workflow

Four distinct review generations plus continuous automated checks — the most reusable process asset in the project.

### review-01 (Feb 2026): multi-model whole-book review

Independent full-manuscript reviews from **four different frontier models**, each writing its own markdown report against the repo's own style docs: `gemini.md` + `gemini-5.1.md`, `gpt-5.2.md`, `gpt-5.3.md`, `grok-4.1.md`. Each combines holistic issues with file:line-level notes (e.g. GPT-5.2 flags "time-sensitive / potentially incorrect real-world claims (highest risk)" and unsourced Appendix B; Grok runs the quality gates itself and reports "10 violations"). Alongside: machine-extracted `style-violations.tsv` / `style-violations-gpt53.tsv` (TSV of `file, line, type, message` from check_style.py), citation checks split by chapter range (`cite-check-ch1-3.md` etc.), `claim-verification.md`, `date-claims-audit.md`, `numeric-claims-catalog.md`, and the unusual `triggers.md` — an audit of passages that could read as politically coded to the book's conservative rural audience segment (audience-risk review, not censorship: it recommends keeping facts, flagging perception).

### review-02: static citation audit (tooling-driven)

`citation_audit_report.md` + JSON outputs (`cite_audit_static.json`, `date_claim_flags.json`, `sibling_project_citations.json`) from a static pass over 104 bib entries and 349 citation mentions: flags sibling-project self-citation (49 uses of `dc-project-database`, against the sources.md rule "Never cite the sibling projects themselves"), missing required fields (98 entries missing publisher), unused entries, and a heuristic matching claim numbers against citation notes (34 mismatch flags). Paired `citation_fix_todo.md`.

### reviews-02 (Feb 2026): persona review panel

Six simulated expert reviews, each a full-length written review in the voice and standards of its outlet/persona, then a synthesis (`00-synthesis.md`):

> 1. **WSJ book reviewer** — Business-literate general audience
> 2. **New Yorker literary critic** — Craft, narrative, prose quality
> 3. **Kirkus Reviews** — Standard trade review (starred)
> 4. **Township supervisor** (Karen Mitchell) — Rural Michigan local official
> 5. **Community organizer** (Marcus Washington) — 15-year Midwest Academy veteran
> 6. **Energy reporter** (Utility Dive) — Grid planning and utility regulation specialist

The synthesis triages findings into tiers ("Tier 1: Fix Before Publication" = factual errors "that would undermine credibility if caught by an opposing attorney, regulator, or journalist" — e.g. a 15-vs-19-year contract-term inconsistency caught by two independent personas). Personas deliberately mirror the audience doc: professional critics for craft, the actual target readers for usefulness, a domain specialist for technical accuracy.

### review-03: per-chapter persona syntheses

Eleven files (`intro-synthesis.md`, `ch01..ch10-synthesis.md`), each synthesizing **five personas per chapter** ("resident (Maria), township official, land-use attorney, fact-checker, line editor") into a prioritized edit list with exact find/replace strings and `%CITE` updates — directly executable edits, e.g.:

> **E1. Fix zoning-amendment attribution (opening).**
> - Find: `The Area Plan Commission had already changed the zoning ordinance...`
> - Replace: `The county had already amended its zoning ordinance...`
> - Rationale: In Indiana (IC 36-7-4) plan commissions recommend; only the county commissioners can amend the ordinance.

This pass fed the second printing.

### fact-check-2026-06: parallel agent fact-pass (the standout pattern)

`research/fact-check-2026-06/AGENT-INSTRUCTIONS.md` is a reusable prompt for per-file fact-check agents: assign one chapter per agent; set the "today" date explicitly; extract EVERY time-sensitive claim; verify anything that could have changed since the last pass; edit the .tex in place; keep `%CITE:` comments accurate; hard constraints (match voice, banned words, never invent facts/URLs, mark `[UNRESOLVED]`, don't touch other files); and a **required provenance log** per agent (claim / line / verdict Accurate-Updated-Unresolved / old->new / full source citation with access date, plus a closing bibtex block of proposed refs.bib changes).

`00-canonical-figures.md` is the coherence mechanism: a single table of cross-chapter headline figures (609 projects / $1.18T / 140.5 GW; 222 moratoria / 30 states / 100 in force; hyperscaler CapEx) with old->new values, sources, and usage rules ("Exact figures above are canonical; rounding for readability is fine... but must not contradict them"). This prevents the classic multi-agent failure where each chapter updates the same statistic differently — exactly the inconsistency class the persona reviews had caught (8,000 vs 9,000 generators).

`COPYEDIT-INSTRUCTIONS.md` is the follow-up pass: a house-style copy edit over the fact-pass seams with hard constraints ("Do not change any facts, figures, dates, names, or quotes", "Word count of the file should stay within +/-3%", zero check_style violations to finish). Fact pass and copyedit pass are deliberately separated so neither agent has license to do the other's job.

### Continuous automated checks

`check_style.py` (banned words, lengths, AI tells, FK level), `check_repetition.py` (cross-book n-grams), `check_adjacent_repetition.py` (local echoes), `book_stats.py` (word budget tracking), `make validate` (undefined refs, trim size), `fetch_url.py` (mandatory citation fetching). AGENTS.md frames these as "Quality Gates (Run Before You Say 'Done')".

---

## 9. Verdict — what to harvest for the master template

### Best reusable pieces

1. **The modular preamble** (`packages/colors/styling/commands` split) — engine-detected fontspec, 6x9 geometry, fancyhdr styles, titlesec chapter-word format, and the front-matter `\cleardoublepage` toggle are all drop-in generic. Parameterize title/author/ISBN.
2. **The tcolorbox callout system + CALLOUT-BOXES.md governance doc** as a unit. The design (grayscale + FontAwesome icons for B&W print, `plainenglish` two-column glossary box exempt from the box budget) and the editorial rules (3 jobs, 80-word cap, 3-per-chapter budget, The Box Test) are inseparable and both fully genre-portable.
3. **The cover toolchain**: `update_cover_vars.py` (KDP/Lulu paperback formulas + Lulu hardcover lookup table + hardcover 0.875" wrap bleed) -> generated `*-cover-vars.tex` -> single `kdp-cover.tex` with `\ifdefined` platform switches -> 3-pass build -> gs PDF-1.4 flatten. Fully generic; only the TikZ art layer is book-specific.
4. **The Makefile** — nearly book-agnostic already (title and filenames are variables at the top). Targets for quick/full/bleed/kdp/lulu/epub/watch/validate/wordcount cover the whole lifecycle.
5. **The custom EPUB converter** — handler-registry architecture with typed block/inline results is solid and the `htsd_*` handler modules are the designed extension seam; a template would rename them and regenerate the callout icon PNGs. Alternative: keep it as an optional module, since it is ~4,700 lines of maintenance surface (see pitfalls).
6. **The style-guide stack + check_style.py as enforcement pair.** STYLE-AI-TELLS.md (perplexity/burstiness framing, numbered tells with quantitative rules) and the banned lists are genre-independent; only reading-level targets and the "neighbor test" persona need retuning per book.
7. **The QA pipeline as process templates**: multi-model review (review-01) -> static citation audit (review-02) -> persona panel + tiered synthesis (reviews-02) -> per-chapter executable edit lists (review-03) -> dated parallel fact-check with canonical-figures file and provenance logs (fact-check-2026-06). AGENT-INSTRUCTIONS.md and COPYEDIT-INSTRUCTIONS.md are copy-paste-ready prompt templates.
8. **METADATA.md as a form-filling dossier pattern** (ISBN table, BISAC, 7 keywords with char counts, description ladder, pricing rationale, pre-publication checklist, quick-reference form table) and the **releases/<printing>/README + SHA256SUMS** artifact convention, including the KDP in-place-update recipe.
9. **The github/ free-PDF pattern** (single self-contained index.html + .nojekyll + CC BY-NC-SA license + buy links) as a distribution template.
10. **`%CITE:` inline provenance comments** in chapter .tex, machine-auditable and agent-maintainable — cheaper than full biblatex discipline during drafting, and it survived three review generations.

### Pitfalls to fix in the template

- **Hard-coded font path** `/usr/share/texlive/texmf-dist/fonts/opentype/public/ebgaramond/` in three files (packages.tex, kdp-cover.tex, cover-standalone.tex) — vendor the OTFs into the repo (they already exist under `epub/templates/fonts/`) and point `Path` there.
- **Empty root README.md**; public docs live only in `github/`.
- **Stale generated files drift**: lulu-paperback-cover-vars.tex still says 168 pages (Feb) while KDP says 182 (June); the vars files are generated artifacts checked into git — template should mark them clearly or regenerate in CI.
- `bibliography.tex` / `appendix-state-reference.tex` exist but aren't wired into `main.tex`; the biblatex setup is half-engaged (`\autocite` used, `\printbibliography` not included in the print build). Decide one citation strategy up front.
- Book-specific strings leak into "generic" tooling (`generate_isbn_barcode.py` has the ISBN hard-coded; `book_stats.py` has the title; converter package hard-codes htsd module names) — template needs a single config source.
- EPUB `content.opf` in templates/ is static while cli.py also generates one dynamically — two sources of truth.
- `epub/build/` and compiled PDFs are committed; define ignore rules.

### Unique to this project (likely absent from wiki-history-book)

- The **custom LaTeX->EPUB converter** (no Pandoc), with per-book handler modules and Kindle-safe raster callout icons.
- The **seven-environment callout system** with a standalone governance document and a print/EPUB parity contract.
- **Multi-retailer cover-vars generation** (KDP + Lulu paperback + Lulu hardcover from one TikZ cover source).
- The **persona review panel** (professional critics + actual target-reader personas + domain specialist) with tiered synthesis, and per-chapter five-persona edit lists.
- The **canonical-figures file** pattern for cross-chapter numeric coherence in parallel agent fact-checks, with per-agent provenance logs and a separate constrained copyedit pass.
- **Reading-level targets enforced by linter** (FK ceiling per chapter band) and guide-specific style rules (60/40 explain/equip, takeaway-box spec).
- **Second-printing in-place update discipline** (KDP content-update threshold, spine recheck, SHA256SUMS).
- The **triggers.md audience-risk audit** — reviewing content for political-coding perception in the target readership.
