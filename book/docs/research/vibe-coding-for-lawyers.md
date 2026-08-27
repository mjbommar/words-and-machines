# Research Report: `vibe-coding-for-lawyers`

Source: `/home/mjbommar/projects/personal/vibe-coding-for-lawyers`

*Vibe Coding for Lawyers: A Practical Guide to AI-Assisted Programming for Legal
Professionals* by Michael J Bommarito II. A code-heavy professional book teaching lawyers
to build tools with Claude Code without becoming engineers. This report captures
everything reusable for a master template, emphasizing code-in-books handling, the
companion GitHub repo model, and the more elaborate LaTeX system (vs. the hacking book).

---

## 1. Purpose & Status

- **What it is:** ~6x9 US-Trade professional book. Four parts (Foundations → Five
  Capabilities → Building Tools → Professional Practice) + prologue, epilogue, 6
  appendices. Writes for three audiences at once — Partners, Associates, Technical
  Beginners.
- **Status (CLAUDE.md):** "Research complete, ready for drafting." Directory structure,
  LaTeX system, and build system complete; 17 research areas (~980KB) done; outline v5.
  `latex/main.pdf`, `.bbl`, `.gls` all present (builds with glossary + bib).
- **Formats produced:** Print PDF (6x9), bleed PDF, grayscale PDF (B&W POD), large-font
  e-reader PDF (`main-ebook.tex`), EPUB (custom Python converter), Kindle AZW3 + MOBI (via
  Calibre `ebook-convert`), KDP interior + wrap cover. `main-epub.tex` and
  `main-interior.tex` are separate driver files.
- **Code-heavy handling:** The signature constraint is a **72-character line limit** for
  all code (print-fit at IBM Plex Mono 0.85 scale), enforced by a dedicated
  `docs/CODE-STYLE-GUIDE.md`. Companion code uses a **pattern.py vs full-implementation**
  split hosted in `github-companion/`.

---

## 2. Directory Layout (annotated)

```
vibe-coding-for-lawyers/
├── CLAUDE.md              # Master brief: three-audience principle, boxes, ethics, style
├── README.md, SETUP.md, TODO.md
├── pyproject.toml         # uv env (hatchling; scripts package)
├── requirements.txt + requirements-{core,dev,gui,optional}.txt   # tiered deps
├── uv.lock
├── docs/                  # 18 docs (see §8) — STYLE, CODE-STYLE-GUIDE, CHAPTER-WORKFLOW…
├── latex/                 # Book production (6x9)
│   ├── main.tex           # Master; main-ebook.tex, main-epub.tex, main-interior.tex
│   ├── cover-standalone.tex, cover.jpg
│   ├── Makefile
│   ├── preamble/          # 10 modular files (main loader + packages/colors/tikz/boxes/
│   │                      #   code/styling/headers/commands/elements)
│   ├── front-matter/      # half-title, title-page, copyright, dedication, how-to-use, preface
│   ├── chapters/00-prologue.tex, chapter-template.tex, NN-*/main.tex
│   ├── back-matter/       # epilogue, acknowledgments, about-author, appendix-a..f, back-cover
│   └── bib/refs.bib
├── code/                  # Runnable examples by chapter (ch00-first-tool, intro-examples,
│                          #   ch02-setup, ch13-sharing, reference/, archived/)
├── github-companion/      # The public companion repo (see §6)
│   ├── code-examples/chNN-*/ (pattern.py + full impl + README + samples/)
│   ├── templates/         # firm-ai-policy, it-approval-request, verification-report…
│   └── checklists/        # vendor-vetting, tool-sharing, pre-filing, data-classification
├── research/              # 17 research areas (case-studies, ethics, security, prompting…)
│   ├── _shared/, _web/, _templates/research-note.md, templates/
├── notes/                 # outlines/ (book-outline-v5.md), drafts/, reviews/
├── scripts/               # 9 Python utilities (see §5)
├── epub/                  # Custom LaTeX→EPUB converter (INHERITED from RFC book — see §4)
└── .claude/agents/        # 8 writing/review agents (see §8)
```

---

## 3. LaTeX Pipeline

**Engine:** LuaLaTeX. Document class `\documentclass[11pt,twoside,openright]{book}`.
The preamble is **modular via a master loader** (cleaner than the hacking book):

```latex
% latex/preamble/main.tex — load order matters
\input{preamble/packages}   % core, fonts, geometry, bib
\input{preamble/colors}     % Tailwind-derived 4-layer palette
\input{preamble/tikz}
\input{preamble/boxes}      % tcolorbox environments
\input{preamble/code}       % listings styles + code environments
\input{preamble/styling}    % chapter/section/ToC
\input{preamble/headers}    % fancyhdr
\input{preamble/commands}
\input{preamble/elements}
```

`main.tex` uses `\part{}` divisions, a glossary (`\makeglossaries`), `\printbibliography
[heading=bibintoc]`, and `\input{chapters/NN-*/main}` per chapter.

### Trim size / geometry (mode-switchable) — `preamble/packages.tex`

```latex
% US Trade 6x9, default screen/proof (no bleed)
\usepackage[
  papersize={6in,9in},
  inner=0.875in, outer=0.625in, top=0.75in, bottom=0.75in,
  includehead, includefoot, footskip=0.35in
]{geometry}
\ifdefined\BleedMode  \geometry{paperwidth=6.25in,paperheight=9.25in, inner=1in,...}\fi
\ifdefined\EbookMode  \geometry{paperwidth=6in,paperheight=9in, inner=0.5in,outer=0.4in,...}\fi
```

Three build modes selected by `\def\BleedMode{1}` / `\def\EbookMode{true}` /
`\def\GrayscaleMode{1}` before the class — a clean single-source multi-format pattern.

### Fonts — IBM Plex, fully specified (best font block of the two projects)

```latex
% preamble/packages.tex
\setmainfont{IBM Plex Serif}[
  Scale = 0.92, Ligatures = TeX,
  Numbers = OldStyle,                       % old-style figures in body
  BoldFont = IBMPlexSerif-SemiBold.otf,
  ItalicFont = IBMPlexSerif-Italic.otf,
  BoldItalicFont = IBMPlexSerif-SemiBoldItalic.otf,
  UprightFeatures = { SizeFeatures = {
      {Size = -8.5, Font = IBMPlexSerif-Text.otf},   % optical sizing
      {Size = 8.5-, Font = IBMPlexSerif-Regular.otf}, }, },
]
\setsansfont{IBM Plex Sans}[Scale=MatchLowercase, Numbers=Lining, BoldFont=…SemiBold…]
\setmonofont{IBM Plex Mono}[Scale=0.85, BoldFont=…SemiBold…]   % 0.85 => ~65-72 chars/line
\IfFontExistsTF{IBMPlexMath-Regular.otf}{\setmathfont{IBMPlexMath-Regular.otf}[Scale=0.92]}
                                        {\setmathfont{Latin Modern Math}[Scale=0.92]}
```

Plus extra weights (`\lightfont`, `\mediumfont`, `\thinfont`) via `\newfontfamily`.
**Microtype is heavily tuned** (protrusion table for punctuation, tracking for small caps,
`factor=1100`, expansion). `\setstretch{1.15}`, `\parindent=1.5em`, `\parskip=0pt`,
`indentfirst`, aggressive hyphenation penalties, widow/club/broken penalties.

### Code listing setup — `listings` + `tcolorbox` (`preamble/code.tex`)

Per-language `\lstdefinestyle` on a shared `bookcode` base, then **code environments built
with `lstnewenvironment` (not `\newtcblisting`)** to correctly handle `#`:

```latex
\lstdefinestyle{bookcode}{
  basicstyle=\ttfamily\small,
  keywordstyle=\color{code-keyword}\bfseries,
  stringstyle=\color{code-string},
  commentstyle=\color{code-comment}\itshape,
  numberstyle=\scriptsize\ttfamily\color{code-linenumber},
  showstringspaces=false, breaklines=true, breakatwhitespace=false,
  tabsize=4, keepspaces=true, columns=fullflexible, basewidth=0.5em,
  escapeinside={(*@}{@*)},
}
% Fix for # in tcolorbox listings — change catcode during listings processing
\makeatletter \lst@AddToHook{Init}{\catcode`\#=12\relax} \makeatother

\lstnewenvironment{pythoncode}[1][]
  {\vspace{0.5\baselineskip}\lstset{style=pythonstyle,
    backgroundcolor=\color{code-bg}, frame=leftline, framerule=3pt,
    rulecolor=\color{code-rule}, framesep=6pt, xleftmargin=9pt, #1}}
  {\vspace{0.5\baselineskip}}
```

Environments: `pythoncode`, `jscode`, `bashcode`, `jsoncode` (with literate digit/brace
coloring), `promptcode` (cyan-tinted AI prompt input), `outputcode` (dark terminal),
`terminalbox`. Inline: `\inlinecode`, `\code` (colorbox), `\apiname`, `\filepath`.
A **`\ifdefined\GrayscaleMode`** block overrides all code colors to grays for B&W print.

### Content boxes — `preamble/boxes.tex` (audience/pedagogy-themed)

15+ `enhanced` tcolorboxes with boxed titles, left color rules, and an `importance` choice
key (`high/medium/low`): `definitionbox`, `examplebox`, `keybox`, `cautionbox`,
`practicebox`, `codebox`, `ethicsbox`, **`partnerbox`/`associatebox`** (the
three-audience mechanism), `notebox`, `sidebar`, `promptbox`, `responsebox`,
`legalcontextbox`, `tipbox`, plus legacy `definition`/`note` aliases. A global
`\tcbset{lines before break=3, short/long styles}` governs breaking.

### Colors — `preamble/colors.tex` (4-layer Tailwind system)

```
Layer 1 PRIMITIVES  slate-900..50, amber-*, green-*, red-*, teal-*, blue-*, cyan-* (full ramps)
Layer 2 SEMANTICS   definition/example/key/caution -base/-dark
Layer 3 COMPONENTS  bg-*, border-*, text-* (text-primary/secondary/muted, primary, primary-light)
Layer 4 LEGACY      back-compat aliases
```

Explicitly "Based on Tailwind CSS color palette." This layered indirection (primitive →
semantic → component) is the single most portable color architecture across both books.

### Chapter/section styling — `preamble/styling.tex`

`titlesec` display chapter: centered sans, `slate-300` ornament rule, `slate-500`
"CHAPTER N" kicker, `\LARGE\bfseries\color{primary}` title, closing rule. `\part` display
style. Section headings sans-bold-primary with a 1.5pt rule; `Needspace` guards keep
headings with content. `titletoc` custom Part/Chapter/Section/Subsection entries with
colored labels + dotted leaders (tocdepth=1). Custom `checklist` list (teal squares),
`\epigraph`, colored `quote`, glossary name font.

### Headers/footers — `preamble/headers.tex`

Professional US-Trade convention documented in comments: front matter = folios only
(`frontmatterstyle`); main matter = verso page# + italic muted book title, recto italic
chapter (`\leftmark`) + page# (`mainmatterstyle`); chapter openers = plain (bottom-center
folio). `\usefrontmatterstyle`/`\usemainmatterstyle`/`\usebackmatterstyle` switchers +
`\enablecleardoublepage`/`\disablecleardoublepage` for openright control.

### Bib/refs (`packages.tex`)

`biblatex` biber, `style=numeric-comp`, `autocite=superscript` (superscript citations),
`sorting=none`, extensive `\DeclareFieldFormat` cleanups, `\bibfont=\small`. `glossaries`
with `automake=immediate`. `cleveref`, `hyperref`, `pmboxdraw` (box-drawing chars for
terminal art).

---

## 4. EPUB Pipeline

`make epub` runs a **custom Python LaTeX→EPUB converter** (`epub/converter/`, a `typer`
app: `python -m converter book … / epub …`, deps TexSoup, lxml, typer, rich). It converts
`latex/main.tex` → XHTML chapters → packaged EPUB 3 in `../build/epub/`, then symlinks
`latest.epub`. `make cover-image` renders `cover-standalone.tex` → `cover.jpg` (pdftoppm
300dpi or ImageMagick).

**IMPORTANT — the `epub/` system is inherited from the "Rough Consensus" (RFC History)
book and only partially adapted:**
- `epub/templates/content.opf` still declares
  `<dc:title>Rough Consensus: How Engineers, Hackers, and Spies Built…</dc:title>` and
  ISBN `9798994345764`.
- `epub/templates/chNN-*.xhtml` are all RFC chapters (ch01-arpanet … ch23-robots-txt),
  and `epub/converter/handlers/` has `rfc_environments.py` / `rfc_macros.py` — no
  vibe-coding-specific handlers yet.
- The full IBM Plex OTF font set is embedded under `epub/templates/fonts/` and declared in
  the OPF manifest (`application/vnd.ms-opentype`), with `<meta name="cover">` + a
  `properties="cover-image"` item — a correct, reusable OPF metadata/cover pattern.

### EPUB CSS (`epub/templates/stylesheet.css`, ~1000 lines, also RFC-derived)

- `pre { overflow-x:auto; white-space:pre-wrap; }` — dual strategy (scroll + wrap) for
  code on small screens.
- Terminal aesthetic classes: `.terminal`, `.vt100-box`, `.transcript pre`, `.email pre`,
  `.code`, `.code-c`. Monospace uppercase section headings mirror the LaTeX look.

**Validation:** `make kindle-validate` runs **epubcheck** on the built EPUB (wired here,
unlike the hacking book). Kindle build passes rich `ebook-convert` flags (embed+subset
fonts, smarten punctuation, keep ligatures, min line-height 120).

---

## 5. Build Automation

**`latex/Makefile`** (785 lines — the more complete of the two). Targets: `pdf`/`all`
(latexmk with a **manual 4-pass fallback** `pdf-manual`), `quick`, `bleed`, `grayscale`
(`\def\GrayscaleMode`), `ebook`, `release` (timestamped PRINT/EBOOK/PRINT-BLEED copies +
`latest-*.pdf` symlinks), `cover-image`, `epub`, `kindle` (AZW3+MOBI), `kindle-validate`
(epubcheck), `all-formats`, `kdp`/`kdp-interior`/`kdp-cover`/`kdp-cover-vars` (spine-width
computed from page count via `scripts/update_kdp_cover_vars.py`, else `bc` fallback
`pages*0.002252+0.06`; Ghostscript PDF/X-1a `/prepress` flatten), `figures`/`figures-png`,
`watch` (latexmk `-pvc`), `validate` (page size 432×648pt, undefined refs, overfull),
`wordcount`/`pagecount`, `view`, and script shims `stats`/`style`/`repetition`. Local TeX
cache via `TEXMFCACHE`/`TEXMFVAR`.

**`scripts/`** (9): `book_stats.py`, `check_style.py` (banned words/AI tells; `make style`),
`check_repetition.py`, `check_citations.py`, `check_urls.py`, `archive_urls.py`,
`bibtex_utils.py`, `extract_pdf.py`, `fetch_url.py`.

**Python env:** `pyproject.toml` requires-python >=3.11, hatchling backend packaging the
`scripts` dir, deps (requests, bs4, lxml, pyyaml, rich, playwright, playwright-stealth,
trafilatura, httpx, pypdfium2, pydetex, nupunkt, typer), ruff+black line-length 100.
**Tiered runtime requirements** for the reader's own tooling:
- `requirements-core.txt` — minimal (pymupdf, python-docx, pandas, python-dateutil,
  anthropic, requests, python-dotenv)
- `requirements.txt` — full (adds pdfplumber, openpyxl, defusedxml, pytesseract,
  pdf2image, Pillow, Jinja2, httpx)
- `requirements-dev.txt`, `requirements-gui.txt`, `requirements-optional.txt`
Each is heavily commented with install notes (e.g. Tesseract OS packages).

---

## 6. Companion Material

**`github-companion/`** is a self-contained public companion repo with its own README,
philosophy, and license split (**templates/checklists CC-BY-4.0, code MIT**). Its model:

> "The book teaches capabilities and judgment. This repository provides implementations."
> Pattern code in the book shows the concept; full implementations here are
> production-ready; practice variations adapt to practice areas; updates track post-pub
> changes.

- **`code-examples/chNN-*/`** — each chapter dir has `pattern.py` (matches the book
  verbatim, minimal), a full implementation (e.g. `extractor.py` with error handling,
  batch, checkpointing), `README.md`, and `samples/` test docs. Chapters mapped in a table
  (ch06 contract-extractor, ch07 policy-summarizer, ch08 intake-processor, ch09
  citation-verifier).
- **`templates/`** — `firm-ai-policy.md`, `it-approval-request.md`,
  `verification-report.md`, `morning-triage-report.md`, `readme-template.md` (each tied to
  a chapter).
- **`checklists/`** — `vendor-vetting.md`, `tool-sharing.md`, `pre-filing.md`,
  `data-classification.md`.
- Referenced from prose via short URLs (`vibe.legal/ch7-code`) or `\filename{ch07/…}`.

Separately, **`code/`** in the book repo holds the in-book snippets (organizer.py etc.)
with an inventory table (file / language / lines / description). The
**pattern-vs-implementation split** is the reusable idea: keep book code minimal and
stable, offload robustness + churn to the companion repo.

---

## 7. Metadata & Publishing

- KDP wrap cover from computed spine width; interior via `main-interior.tex`; Ghostscript
  PDF/X-1a flatten. Grayscale build for cheaper B&W POD.
- EPUB OPF metadata + embedded fonts + cover-image pattern present (though currently the
  RFC book's metadata — needs re-titling/ISBN for this book).
- `front-matter/copyright.tex`, `back-cover.tex`, `about-author.tex`, `half-title.tex`
  provide the standard publishing furniture.
- Legal-citation conventions codified in CLAUDE.md (Bluebook, ABA Model Rule format, ABA
  Formal Opinion format).

---

## 8. Style / Craft / AI-Tone Guides

Documentation is unusually deep (18 files in `docs/`):

- **`CLAUDE.md`** — three-audience core principle; per-chapter required sections (partner
  box, working code, ethics consideration, practice exercises, real legal scenarios);
  code requirements (runnable, 72-char, cross-platform Mac/WSL/Linux); banned words/phrases;
  terminology consistency table (use "lawyer" not "attorney", "use" not "leverage/utilize",
  "workflow" not "pipeline"); typography table; box/command reference; a dedicated **Ethics
  & Professional Responsibility** section mapping content to ABA Model Rules 1.1/1.6/5.3/
  1.4/3.3; quality checklists; workflow.
- **`docs/STYLE.md`** — voice ("coffee test": sound like a senior colleague over coffee,
  not a law review), tone, audience tiers.
- **`docs/CODE-STYLE-GUIDE.md`** — the standout for code-in-books: hard 72-char limit
  (target 65), per-language line-breaking patterns (parens continuation, string concat,
  `pathlib` for long paths, bash backslash, vertical JSON), `~/legal-projects/` standard
  working dir, `pathlib.Path` for platform neutrality, WSL path translation, `\macmark/
  \winmark/\linuxmark` platform markers, error-traceback truncation rules, `$`-only
  terminal prompts, a LaTeX-environment selection table, URL/GitHub-reference conventions,
  and a pre-inclusion checklist.
- **`docs/STYLE-AI-TELLS.md`**, `WRITING-PROCESS.md` (7 phases), `CHAPTER-WORKFLOW.md`
  (step-by-step with agent invocations), `REPETITION-AUDIT.md`, `BUILD-GUIDE.md`,
  `SCRIPTS-GUIDE.md`, `FORMATTING-GUIDE.md`, `GLOSSARY.md`, `CHAPTER-TEMPLATE.md`,
  `EXERCISE-SPECIFICATIONS.md`, `PRACTICAL-EXAMPLE-CHECKLIST.md`, `BOOK-GITHUB-SPLIT.md`,
  `START.md` (new-session entrypoint).
- **`.claude/agents/`** (8): `outline-iteration`, `draft-from-outline`, `critical-review`,
  `code-review`, `ethics-review`, `style-conformance`, `compression`, `integration-review`
  — mapped to workflow phases in a CLAUDE.md table.

**Safety/authorization framing:** unlike the hacking book's CFAA framing, safety here is
professional-responsibility framing — every chapter touching AI/client data must address
competence, confidentiality, supervision, communication, and candor (ABA Model Rules),
delivered via `ethicsbox`/`cautionbox`.

---

## 9. QA / Review Workflow

- Automated: `check_style.py` (`make style`), `check_repetition.py`, `check_citations.py`,
  `check_urls.py`, `archive_urls.py` (link rot), `book_stats.py` (before/after JSON deltas
  in commit messages).
- `make validate` (page size, undefined refs/citations, overfull boxes);
  `make kindle-validate` (epubcheck).
- **Code testing workflow (CLAUDE.md):** write code in a test file → run it, verify output
  → add to LaTeX with actual output → test again in context → include in code-review
  checklist. Every example "runnable without modification," ≤72 chars, cross-platform.
- Quality gate checklist before submitting content (code tested, no banned words, serves
  three audiences, ethics addressed, citations, passes coffee test).
- Review agents: `code-review`, `ethics-review`, `critical-review`, `integration-review`.

---

## 10. Verdict — Best Reusable Pieces

**Take for the master template (prefer these over the hacking book's where they overlap):**
- The **10-file modular preamble** with a `preamble/main.tex` loader and documented
  load-order — the cleanest structure of the two books; adopt as the template skeleton.
- The **4-layer Tailwind color system** (primitive → semantic → component → legacy) — the
  most portable, theme-swappable color architecture found.
- The **fully-specified IBM Plex font block** (optical sizing, old-style vs lining figures,
  explicit weight files) and the tuned **microtype** protrusion/tracking table.
- **`preamble/code.tex`**: `lstnewenvironment` code environments + the
  `\lst@AddToHook{Init}{\catcode`\#=12}` fix for `#` inside listings — a real gotcha solved
  here. Per-language styles on a shared base; `promptcode`/`outputcode`/`responsebox` for
  AI prompt/response rendering.
- The **build-mode switch pattern** (`\BleedMode`/`\EbookMode`/`\GrayscaleMode` sensed with
  `\ifdefined`) for single-source multi-format output.
- The **grayscale build** for B&W POD (with in-preamble color overrides).
- The **Makefile** (kindle AZW3/MOBI, epubcheck validation, KDP spine-width computation,
  latexmk-with-4-pass-fallback, figures-png) — the more complete build system; merge with
  the hacking book's.
- The **`docs/CODE-STYLE-GUIDE.md`** — the single best artifact across both projects for
  "code in books": 72-char discipline, line-breaking recipes, platform handling, error
  truncation. Adopt nearly verbatim.
- The **pattern.py vs full-implementation companion split** + separate `github-companion/`
  with its own README and CC-BY/MIT license split.
- **Tiered `requirements-*.txt`** for the reader's own environment.
- The **three-audience box system** (`partnerbox`/`associatebox`) and the
  professional-responsibility ethics framing (ABA Model Rules mapping).
- The **8-agent writing pipeline** + `docs/CHAPTER-WORKFLOW.md`.

**Pitfalls / gaps:**
- **The `epub/` system is stale RFC-book leftovers** — `content.opf` still says "Rough
  Consensus" with the wrong ISBN, all `chNN-*.xhtml` templates and converter handlers are
  RFC-specific. The EPUB build will produce mis-titled output until the templates,
  handlers, and OPF metadata are rewritten for this book. This is the biggest cleanup item
  and a clear argument for a **parameterized, book-agnostic EPUB converter** in the master
  template (drive title/ISBN/handlers from config, not hard-coded templates).
- `bookauthor` is still `[Author Name]` placeholder in `main.tex`.
- `main-ebook.tex` references chapters (`01-introduction`) that differ from `main.tex`'s
  chapter set — the driver files have drifted.
- KDP cover-vars script may be absent (Makefile has a `bc` fallback).

**Unique to this project:** the 72-char code discipline enforced by tooling and font-scale
math; the three-simultaneous-audiences box model; ABA-Model-Rules ethics integration; the
Kindle (AZW3/MOBI) + epubcheck path; the separate public GitHub companion repo with a
pattern/implementation split and per-chapter templates/checklists.
