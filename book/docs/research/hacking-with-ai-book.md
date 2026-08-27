# Research Report: `hacking-with-ai-book`

Source: `/home/mjbommar/projects/personal/hacking-with-ai-book`

A technical/security book, *Hacking with AI* by Michael J Bommarito II — a spiritual
successor to Erickson's *Hacking: The Art of Exploitation* updated for the 2026 attack
surface. This report captures everything reusable for a master book template, with
emphasis on how it handles code listings, companion labs, and AI-authoring workflow.

---

## 1. Purpose & Status

- **What it is:** ~100,000-word, 7x10 hacking book. Twelve hex-numbered chapters
  (`0x100`–`0xC00`) organized by MITRE ATT&CK attack lifecycle. Teaches by building
  raw code first, then tools.
- **Status:** In production/drafting. LaTeX system, lab, and scripts are complete;
  chapters are being drafted per a documented research → draft → review pipeline.
  `latex/main.pdf` builds.
- **Formats produced:** Print PDF (7x10), print-bleed PDF, large-font e-reader PDF
  (`main-ebook.tex`), EPUB (two paths: `make epub` via pandoc, and a custom Python
  LaTeX→EPUB converter under `epub/`), and Amazon KDP interior + wrap cover.
- **Code-heavy handling:** This is the defining feature. Code is treated as first-class
  pedagogy ("The Code Hierarchy": raw code → open-source tools → commercial tools last,
  never required). Companion runnable code lives in `code/chapters/0xNNN/`, and a full
  Docker lab (`lab/`) ships the "Live CD" equivalent — `docker compose up` gives
  intentionally-vulnerable targets plus local LLMs (Ollama `qwen3:8b`).

---

## 2. Directory Layout (annotated)

```
hacking-with-ai-book/
├── CLAUDE.md              # Master brief: thesis, chapter architecture, style, non-negotiables
├── pyproject.toml         # uv/Python env (TexSoup, typer, rich, playwright, httpx)
├── uv.lock
├── reference/             # Original Hacking2E PDF + 100+ original C source files
│   ├── book/  └── source/
├── docs/                  # Style guides + process docs (see §8)
│   ├── VISION.md, STYLE.md, STYLE-CRAFT.md, STYLE-AI-TELLS.md
│   ├── RESEARCH-PROCESS.md, WRITING-PROCESS.md, sources.md
│   ├── curricula/, taxonomy/, scope-review-01/, REORGANIZATION-MAP.md
├── notes/                 # structure.md, outline/planning
├── outline/
├── research/              # Per-chapter research (R1-R6 pipeline)
│   ├── _shared/  ├── _templates/chapter-research.md  └── chapters/
├── code/                  # Runnable examples
│   ├── chapters/0x100..0x800/   ├── lib/  └── tests/
├── lab/                   # Docker vulnerable-target lab (the "Live CD")
│   ├── docker-compose.yml  ├── .env
│   ├── scripts/           # setup.sh, verify.sh, reset.sh, seed_data.py
│   └── targets/           # acmecorp-web/api/chatbot/rag, vuln-c-binaries, network-targets
├── courses/               # 3 university course adaptations (see §6)
│   ├── msu-broad-ai-audit, msu-broad-ai-audit-v2, msu-broad-it-audit
├── latex/                 # Book production (7x10)
│   ├── main.tex           # Master document
│   ├── Makefile
│   ├── preamble/          # packages.tex, colors.tex, styling.tex, commands.tex
│   ├── front-matter/      # title, copyright, dedication, toc, preface
│   ├── chapters/0xNNN-*/main.tex
│   ├── back-matter/       # appendix-tools, appendix-lab-setup, bibliography
│   ├── bib/refs.bib  └── figures/
├── scripts/               # book_stats.py, check_style.py, check_repetition.py,
│                          #   check_code.py, fetch_url.py
├── epub/                  # Custom LaTeX→EPUB converter (Python)
│   ├── converter/         # cli, parser, renderer, context, handlers/*
│   ├── templates/stylesheet.css  ├── META-INF/container.xml
│   └── scripts/package_epub.py
└── .claude/agents/        # 8 writing/research subagents (see §8)
```

---

## 3. LaTeX Pipeline

**Engine:** LuaLaTeX (`lualatex`) for fontspec. Document class:

```latex
% latex/main.tex
\documentclass[11pt,twoside,openright]{book}
\input{preamble/packages}
\input{preamble/colors}
\input{preamble/styling}
\input{preamble/commands}
\addbibresource{bib/refs.bib}
```

Preamble is only 4 files (leaner than vibe-coding's 10). `main.tex` manually builds the
half-title, front matter with `\frontmatter`, `\mainmatter`, then `\backmatter` +
`\appendix`. Notably it temporarily aliases `\cleardoublepage` to `\clearpage` during
front matter to avoid blank pages, then restores it.

### Trim size / geometry (`latex/preamble/packages.tex`)

```latex
% 7x10 format with proper margins for print
\usepackage[
    paperwidth=7in,
    paperheight=10in,
    inner=0.875in,      % Gutter margin (binding side)
    outer=0.75in,       % Outside margin
    top=0.75in,
    bottom=0.75in,
    includehead,
    includefoot
]{geometry}
```

### Fonts — IBM Plex via fontspec, with pdfLaTeX fallback

```latex
\ifluatex
    \usepackage{fontspec}
    \setmainfont{IBM Plex Serif}
    \setsansfont{IBM Plex Sans}
    \setmonofont{IBM Plex Mono}[Scale=MatchLowercase]
\else\ifxetex
    ... same ...
\else
    \usepackage[utf8]{inputenc}
    \usepackage[T1]{fontenc}
    \usepackage{plex-serif}\usepackage{plex-sans}\usepackage{plex-mono}
\fi\fi
\usepackage[nopatch=footnote]{microtype}
```

Body: 11pt with 13.5pt leading, set via a `\renewcommand\normalsize` override.
`\parindent=1.5em`, `\parskip=3pt`, `\raggedbottom`, widow/clubpenalty=10000,
`\emergencystretch=2em`, `\tolerance=1000`.

### Code listing setup — `listings` (NOT minted)

```latex
\usepackage{listings}
\lstset{
    basicstyle=\small\ttfamily,
    breaklines=true,            % line-wrapping in print
    breakatwhitespace=false,
    tabsize=4,
    showstringspaces=false,
    numbers=left,
    numberstyle=\tiny\ttfamily\color{codegray},
    numbersep=8pt,
    frame=none,
    xleftmargin=1.5em,
    aboveskip=0.5em, belowskip=0.5em,
    escapeinside={(*@}{@*)},
}
```

`tcolorbox` is loaded with `[most]` + libraries `skins, breakable, listings`. There is
**no separate `code.tex`** here — listings is configured inline in packages.tex and the
colored boxes live in `commands.tex`.

### Callout box environments (`latex/preamble/commands.tex`)

Five `tcolorbox` environments, all `breakable`, all with FontAwesome5 icon titles:
- `exploitbox` (skull-crossbones, orange) — exploit walkthrough
- `defensebox` (shield-alt, blue) — countermeasure
- `notebox` (info-circle, green)
- `warningbox` (exclamation-triangle, red, thick `boxrule=1.2pt`)
- `terminalbox` (terminal icon, dark `#1A1A2E` bg, green mono text) — shell sessions

### Custom semantic macros (`commands.tex`)

Hex chapter/section machinery is fully custom (bypasses `\chapter` numbering):

```latex
\newcommand{\hackchapter}[2]{%   % \hackchapter{0x200}{Reconnaissance}
    \clearpage\thispagestyle{plain}\vspace*{30pt}%
    {\raggedleft
        {\fontsize{36}{40}\selectfont\bfseries\ttfamily\color{chaptercolor} #1}\par
        \vspace{0.5em}{\huge\bfseries\sffamily #2}\par}%
    \vspace{25pt}\addcontentsline{toc}{chapter}{#1\quad #2}%
    \markboth{#1\quad #2}{#2}}
```

Plus inline semantics: `\code`, `\cmd`, `\file`, `\cve`, `\tool`, `\attack`, `\malware`,
`\model`, `\prompt`, `\api`, `\agent`, `\person`, `\keyterm` (indexes), and draft-only
`\TODO/\NOTE/\VERIFY/\editnote/\citeneeded` (toggle via `ifdraft`).

### Colors (`latex/preamble/colors.tex`)

Hacker palette: terminal green `#00FF41`, hacker orange `#FF6600`, cyber blue `#00B4D8`;
code bg near-black `#1A1A2E`, fg `#E0E0E0`; per-box tint colors. Explicit note that
these are screen colors and tcolorbox uses grayscale-safe border weights for B&W print.

### Chapter/section styling (`latex/preamble/styling.tex`)

`titlesec` display chapter format (right-aligned, huge bold); sans-serif section
headings; `titletoc` custom TOC (chapter bold + dotted leaders, tocdepth=1); `caption`
(bold label, period sep); custom footnote rule (2in); italic small `quote`; `lettrine`
drop caps (2 lines); tight `enumitem` lists; custom twoside `\cleardoublepage`.

### Headers/footers (`packages.tex`)

`fancyhdr`: `body` style puts `\leftmark`/`\rightmark` in `\texttt` running heads
(LE/RO), page numbers outer, 0.4pt headrule.

### Hyperref / bib / refs

- `hyperref` all-black links for print + full PDF metadata (title/author/subject/keywords).
- `biblatex` backend=biber, `style=numeric-comp`, `sorting=nyt`, `maxbibnames=99`.
- `cleveref` with custom `\crefname` for listing/appendix.
- `epigraph`, `setspace`, `quoting`, `ifdraft`+`draftwatermark` (DRAFT watermark),
  `imakeidx` scaffolded but commented until `\keyterm` entries populate.

---

## 4. EPUB Pipeline

Two parallel approaches:

1. **Quick pandoc path** (`make epub`): `pandoc main.tex --from=latex --to=epub3
   --toc --toc-depth=2` with title/author metadata. Falls back with a helpful message
   if pandoc is missing.

2. **Custom Python LaTeX→EPUB converter** (`epub/converter/`) — the interesting,
   reusable piece. A `typer` CLI (`python -m converter`) with `parser.py` (TexSoup-based
   load), `renderer.py`, `context.py` (loads bibliography), and pluggable `handlers/`
   split into generic (`macros.py`, `environments.py`) and book-specific
   (`hacking_macros.py`, `hacking_environments.py`) — so the semantic LaTeX macros map to
   semantic HTML/CSS classes. `epub/scripts/package_epub.py` zips a valid EPUB 3:

```python
with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
    # mimetype must be first and stored without compression
    zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
    for file_path in sorted(staging.rglob("*")):
        ...
```

Structure produced: `mimetype`, `META-INF/container.xml`, `OEBPS/{content.opf,
styles/stylesheet.css, text/*.xhtml, images/, fonts/}`.

### EPUB CSS (`epub/templates/stylesheet.css`) — code handling

- Body Georgia serif, justified, 1.5em text-indent (removed after headings).
- `pre` = dark `#1e1e1e` bg, `#d4d4d4` text, `border-radius:4px`, **`overflow-x:auto`**
  (horizontal scroll instead of print's line-wrap), 0.85em.
- `h1.hack-chapter` monospace with bottom border (mirrors print hex style).
- Callout `aside.callout` + modifier classes `.exploit/.defense/.warning/.note` with
  colored left borders — direct analogues of the print tcolorboxes.
- `div.terminal pre` = black bg, green `#33ff33` text (matches print terminalbox).
- Inline semantic spans (`.tool/.model/.prompt/.attack/.malware/.agent/.cve`) mirror the
  LaTeX macros.

**Validation:** No epubcheck wired here (vibe-coding has it — see that report).

---

## 5. Build Automation

**`latex/Makefile`** (ANSI-colored output, targets):
- `pdf`/`all` (latexmk `-lualatex`, reports pages/size/dims via pdfinfo)
- `quick` (single pass), `full` (3-pass + biber), `draft` (DRAFT watermark via
  `\PassOptionsToPackage{draft}{ifdraft}`)
- `bleed` (`-jobname=main-bleed` with `\def\BleedMode{1}`)
- `ebook` (`main-ebook.tex`, large font)
- `epub` (pandoc)
- `release` (timestamped copy to `../build/pdf/`)
- `kdp`, `kdp-interior`, `kdp-cover` — cover build does 3 LaTeX passes then Ghostscript
  flatten to PDF/1.4 lossless FlateEncode
- `watch` (latexmk `-pvc`), `validate` (page-size check, undefined refs, overfull boxes),
  `wordcount`/`pagecount`/`texcount`, `clean`/`cleanall`, `help`
- Local TeX cache via `TEXMFCACHE`/`TEXMFVAR` → `$(CURDIR)/.texlive-cache`
- **Pitfall:** references `../scripts/update_cover_vars.py` and
  `generate_isbn_barcode.py` which are **not present** in `scripts/`.

**`scripts/`** (Python, run via `uv run`):
- `book_stats.py` — word counts + quality metrics (`--json`)
- `check_style.py` — banned-word/phrase, sentence length, AI-tell, reading-level checker
  (typer + rich; `BANNED_WORDS` list embedded; operates on `latex/chapters/`)
- `check_repetition.py` — repetitive-language detection
- `check_code.py` — code-example verification
- `fetch_url.py` — source/citation verification

**Python env** (`pyproject.toml`): requires-python >=3.11; deps requests, bs4, lxml,
pyyaml, rich, playwright, httpx, TexSoup, typer; dev pytest+ruff; ruff line-length 100.

---

## 6. Companion Material

Three tiers, tightly cross-referenced from the book:

1. **`code/chapters/0xNNN/`** — runnable examples per chapter, plus `code/lib/` and
   `code/tests/`. Philosophy from CLAUDE.md: "Raw code first… Open source tools second…
   Commercial tools last, and only as references."

2. **`lab/`** — the Docker "Live CD". `docker-compose.yml` with profiles
   (`web/ai/network/cloud/binary`). Targets: `acmecorp-web` (Flask: SQLi/XSS/SSTI/XXE/
   CSRF/IDOR…), `acmecorp-api` (FastAPI: mass assignment/JWT/GraphQL/gRPC),
   `acmecorp-chatbot` (prompt injection/tool abuse), `acmecorp-rag` (poisoning),
   `vuln-c-binaries` (GDB/pwndbg), `network-targets` (FTP/SSH/HTTP/HTTPS misconfigs),
   Ollama (`qwen3:8b` + `nomic-embed-text`), Postgres, Redis, LocalStack. `lab/README.md`
   is exemplary: a **vulnerability map table mapping every endpoint to the book section**
   (e.g. `/login → SQL Injection → 0x330`), test-credential table, per-profile RAM/disk
   budget, `DEFENSE_LEVEL=none|basic|proper` env toggles, reset/troubleshooting. Scripts:
   `setup.sh`, `verify.sh`, `reset.sh`, `seed_data.py`.

3. **`courses/`** — three university course adaptations (MSU Broad College: ACC 892
   Applied AI for Audit). Each has `syllabus.md`, `assignments/`, `instructor-guide.md`,
   its own `latex/`, `reference/`, `reviews/`. Shows the book content repurposed as a
   graduate course (skill stack "Prompt, Read, Evaluate, Fix, Reflect").

Companion code is referenced from prose by chapter number; the lab is referenced by the
appendix `back-matter/appendix-lab-setup.tex`.

---

## 7. Metadata & Publishing

- PDF metadata set in `hypersetup` (title, author, subject, keywords).
- KDP: `make kdp` builds interior + wrap cover; cover flattened with Ghostscript to
  PDF/1.4. Bleed build for print-on-demand. Cover-var/ISBN-barcode scripts referenced but
  missing (scaffolded).
- `back-matter/` holds `appendix-tools`, `appendix-lab-setup`, `bibliography`.
- Currency doctrine (CLAUDE.md): everything must be current to March 2026 — tool
  versions, CVEs (2024–2026), OWASP LLM 2025, MITRE ATT&CK/ATLAS; verify with WebSearch.

---

## 8. Style / Craft / AI-Tone Guides

This project's writing-governance is its richest reusable asset.

- **`CLAUDE.md`** (424 lines) — thesis, 12-chapter ATT&CK architecture table, "AI-Assisted
  Teaching Pattern" (AI writes it → you read it → you understand why → AI's version breaks
  → you fix it), "The Code Hierarchy" (non-negotiable), Whiteboard Test, huge **BANNED
  words** and **BANNED phrases** lists, **AI Tells** rules (max 1 "This" opener/paragraph,
  no First/Second/Third prose enumeration, show dead ends before the solution), 10
  Non-Negotiables, custom LaTeX command/environment reference, key scripts, workflow.

- **`docs/STYLE.md`** — voice/grammar/banned words. **`docs/STYLE-AI-TELLS.md`** — AI
  pattern detection & elimination. **`docs/STYLE-CRAFT.md`** — the lineage (Erickson +
  2600 + Mitnick + IRC/Usenet) and, notably, **Part 6: "Ethics Without the Corporate
  Voice"** — the security-content authorization framing. Its rule set:

  > Corporate voice (avoid): "It is essential to only use these techniques in authorized
  > testing environments. Unauthorized access… is illegal under the Computer Fraud and
  > Abuse Act…"
  > Community voice (use): "…We demonstrate it against local models you control. If you
  > find this in the wild, report it — the developer probably doesn't know it's there."

  Every attack section must include: (1) why it works, (2) attacker impact, (3) how to
  detect/prevent, (4) when to disclose. All exploits demonstrated only against
  reader-controlled targets (local models, provided containers). "Accuracy over hype" —
  cite exact model versions an exploit works against.

- **`docs/RESEARCH-PROCESS.md`** — R1–R6 pre-writing research pipeline; **WRITING-PROCESS.md**
  — 8-phase workflow (research → outline → draft → code → tech review → style → compression
  → fact-check).

- **`.claude/agents/`** (8): `citation-management`, `code-development`,
  `compression-tightening`, `critical-review`, `draft-from-outline`, `fact-check`,
  `security-research`, `style-guide-conformance`.

---

## 9. QA / Review Workflow

- Automated: `check_style.py` (banned words/phrases, sentence length, AI tells, reading
  level), `check_repetition.py`, `check_code.py` (verify examples run), `fetch_url.py`
  (source verification), `book_stats.py` (metrics, `--json` for before/after deltas).
- `make validate` — page-size assertion (504×720pt), undefined refs, overfull boxes.
- Lab `verify.sh` confirms all services healthy before a reader starts.
- Non-negotiable "working code or no code" — every example must run with pinned versions;
  every chapter must contain one AI-generates-then-fails-then-reader-fixes cycle.
- Subagents (`fact-check`, `critical-review`, `code-development`, `security-research`)
  handle multi-perspective review.

---

## 10. Verdict — Best Reusable Pieces

**Take for the master template:**
- The **LuaLaTeX + IBM Plex + `listings` + `tcolorbox`** print stack, with `breaklines=true`
  for print wrapping and `escapeinside` for annotation.
- The **semantic-macro layer** (`\code/\tool/\cmd/\file/\cve/\model/\keyterm`) + matching
  **EPUB CSS classes** — one authoring vocabulary, two renderers. This is the cleanest
  single-source model here.
- The **custom Python LaTeX→EPUB converter** with generic vs. book-specific handler split
  (`handlers/macros.py` + `handlers/<book>_macros.py`) — genuinely template-worthy for
  code-heavy books where pandoc mangles listings.
- **`package_epub.py`** (correct mimetype-first zip) as a drop-in EPUB packager.
- The **Makefile** (bleed/ebook/kdp/draft-watermark/validate/local-tex-cache) — nearly
  identical to vibe-coding's; converge them.
- The **lab README pattern**: a vulnerability/endpoint → book-section mapping table, test
  creds, resource budgets, difficulty/defense toggles. Model for any book with a companion
  sandbox.
- The **draft toggle system** (`ifdraft` → `\TODO/\VERIFY` + watermark).
- The **AI-authoring governance** (`CLAUDE.md` banned lists, STYLE-AI-TELLS, STYLE-CRAFT
  ethics framing) and **8 subagents** — reusable verbatim as writing infrastructure.
- **check_style.py / check_code.py / book_stats.py** scripts.

**Pitfalls / gaps:**
- Makefile references cover/ISBN scripts (`update_cover_vars.py`,
  `generate_isbn_barcode.py`) that don't exist — dead targets.
- EPUB validation (epubcheck) not wired; two divergent EPUB paths (pandoc vs custom).
- Preamble is split across only 4 files with listings config crammed into `packages.tex`
  — vibe-coding's 10-file modular preamble is cleaner; prefer that structure.
- Index (`imakeidx`) scaffolded but disabled.

**Unique to this project:** the hex-numbered chapter machinery (`\hackchapter`); the
Docker vulnerable-target lab as the companion "artifact"; the security-specific
authorization/ethics voice guidance; three university course spin-offs; the
AI-writes-then-fails teaching pattern baked into non-negotiables.
