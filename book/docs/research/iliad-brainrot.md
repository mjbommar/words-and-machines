# Research Report: iliad-brainrot

**Project path:** `/home/mjbommar/projects/personal/iliad-brainrot`
**Reviewed:** 2026-07-06, for extraction into the master book template.

---

## 1. Purpose & Status

**The Brainrot Iliad: A Terminally Online Translation** — a parallel Modern Greek / English edition of Homer's Iliad. The Greek is Alexandros Pallis' 1904/1917 demotic verse translation (Project Gutenberg eBook #36248, public domain); the English is a new AI-produced ("GPT-5.4") translation in internet-native "brainrot" register, matched **1:1 line-for-line** against the Greek. The book doubles as a **progressive Modern Greek reader**: ~117 grammar margin notes, ~87 vocabulary notes, and a 223-entry glossary teach Greek from alphabet (Book 1) to sentence parsing (Book 24).

- **Status:** Published / at final pre-publication stage. ISBN assigned (979-8-9947460-2-8), interior locked at **682 pages**, KDP wrap cover built; the pre-pub checklist in METADATA.md has all build items checked, with only upload/proof steps unchecked. Book 1 of the "Brainrot Classics" series (per the Ovid project's docs; the Odyssey and Aeneid followed as Books 2–3).
- **Formats:** 7"×10" paperback (Amazon KDP + Lulu paperback + Lulu hardcover case wrap) plus a home-grown EPUB 3.
- **The `album/` directory is music.** Yes — a full companion **concept album**: *THE WILL OF ZEUS (Του Διός η Γνώμη)*, 23 tracks of Blind-Guardian-style symphonic power metal, artist "Forged Gods", generated with **Suno** from per-track style prompts + lyrics written in Markdown. `album/audio/` holds the WAV takes (A/B/C/D variants per song), an MP3 build dir, cover.jpg, and M3U playlists. See §7.
- **Books:** 23 of 24 (Pallis never translated Book 13/Nu; the numbering deliberately skips it).

## 2. Directory Layout

```
iliad-brainrot/
  pyproject.toml               # uv-managed; pydantic, rich, lxml, typer
  CLAUDE.md                    # AI production guide (structure, safety rules, workflow)
  AGENTS.md                    # QA/spot-check conventions for agents
  METADATA.md                  # Complete KDP/Bowker publishing dossier (530 lines)
  data/                        # === SOURCE OF TRUTH (JSON) ===
    source.json                # Parsed Pallis Greek: books > stanzas > lines
    translations/book_*.json   # 23 books; per-stanza source+translation+notes (EDIT THESE)
    book_summaries.json        # 23 summaries: greek/english/brainrot titles, key scenes, arcs
    character_bible.json       # characters/factions/places/conventions (150+ entries)
    glossary.json              # 223 entries w/ frequency, first appearance, example line
  scripts/                     # Python build tooling (see §5)
  latex/
    main.tex                   # book class master
    Makefile                   # full build system (pdf/kdp/lulu/epub/covers/validate)
    .latexmkrc                 # xelatex config
    preamble/{packages,colors,styling,commands}.tex
    front-matter/{half-title,title,copyright,dedication,toc,introduction}.tex
    front-matter/cover/        # AUTO-GENERATED cover dimension vars per platform
    chapters/book_*.tex        # AUTO-GENERATED from JSON — never hand-edit
    back-matter/{glossary,translator-note,about-source}.tex + isbn-barcode.{pdf,png}
    figures/cover-art.png      # AI-generated cover art
    kdp-cover.tex              # one TikZ file drives KDP + Lulu pb + Lulu hc wrap covers
    cover-standalone.tex       # front-cover-only page → JPEG for EPUB/marketing
  epub/
    converter/                 # pure-Python EPUB 3 builder (typer CLI)
  docs/                        # Greek-teaching apparatus (see §8)
  album/                       # concept album (see §7)
  build/                       # timestamped release PDFs
```

**Data storage model:** everything renderable lives in JSON validated by Pydantic models (`scripts/models.py`). The core unit is the **stanza**: `StanzaResult { stanza_index, source: StanzaSource{lines[{line_index, global_line, content}]}, translation: StanzaTranslation{lines[{line_index, translation}], notes[MarginNote], mood, scene_break}, model, timestamp }`. `MarginNote { line_ref, note_type, text, marked_words[] }` with note types `character | cultural | reference | translation | wordplay | grammar | vocabulary`. The project mantra, stated in CLAUDE.md:

```
data/translations/book_*.json  ──(generate_chapters_tex.py)──>  latex/chapters/book_*.tex
       SOURCE OF TRUTH                                            AUTO-GENERATED
       (edit these)                                               (NEVER edit these)
```

## 3. LaTeX Pipeline

- **Class:** `\documentclass[10pt,twoside]{book}`, engine **XeLaTeX** (required for fontspec + polyglossia), driven by latexmk (`$pdf_mode = 5` in `.latexmkrc`).
- **Trim/geometry** (`latex/preamble/packages.tex`) — KDP-compliant 7×10:

```latex
\usepackage[
    paperwidth=7in,
    paperheight=10in,
    inner=0.9in,        % Gutter margin (binding side)
    outer=0.625in,      % Outside margin
    top=0.75in,         % Top margin
    bottom=0.875in,     % Bottom margin (larger for visual balance)
    includehead,
    includefoot
]{geometry}
```

- **Fonts** — Libertinus for its Greek coverage, with a decorative archaic-Greek display face and bilingual setup via polyglossia:

```latex
\usepackage{fontspec}
\usepackage{libertinus}
\usepackage{libertinust1math}
\setmonofont{Latin Modern Mono}[Scale=MatchLowercase]

% Decorative title font (GFS Complutum - archaic Greek feel)
\newfontfamily\titlefont{GFS Complutum}[LetterSpace=12]

\usepackage{polyglossia}
\setdefaultlanguage{english}
\setotherlanguage[variant=monotonic]{greek}
```

- **Parallel verse layout — the crown jewel.** Two-column **paracol** per chapter: ~70% verse pairs, ~30% margin notes, with *independent page breaking per column* (explicitly chosen over longtable/supertabular to eliminate wasted whitespace at page boundaries). From `packages.tex`:

```latex
\usepackage{paracol}
\usepackage{multicol}
\columnratio{0.70}                          % 70% verses, 30% notes
\setlength{\columnsep}{0.04\textwidth}      % gap between columns
```

- **Verse formatting** (emitted by the generator, one Greek+English pair per source line): hanging indents for wrapped lines, line numbers every 5 lines in gray, Greek in muted gray, English in italic black:

```latex
\hangindent=3.2em\noindent \makebox[1.6em][r]{\scriptsize\color{linenumcolor}1}\hspace{0.3em}{\small\color{greekcolor}\textgreek{...}}\par
\hangindent=3.2em\noindent\hspace{1.9em}{\small\itshape\color{englishcolor}...}\par
\vspace{0.5pt}
```

- **Column-sync commands** (`preamble/commands.tex`) — stanza boundaries sync both columns; scene breaks span both columns with a centered rule:

```latex
\newcommand{\scenebreak}{%
    \switchcolumn*[\vspace{2pt}{\centering\color{scenecolor}\rule{1.5cm}{0.3pt}\par}\vspace{1pt}]%
}
\newcommand{\stanzasync}{\switchcolumn*}
```

- **Margin-note symbols + grammar underlining** — each note type has a marginal symbol matching an HTML-reader convention; grammar-taught Greek words get a dashed underline via a leaders-based `\gmarkdot`:

```latex
\newcommand{\notesymchar}{\dag}        % character note
\newcommand{\notesymcultural}{$\circ$} % cultural note
\newcommand{\notesymref}{\S}           % reference note
\newcommand{\notesymtrans}{\P}         % translation note
\newcommand{\notesymwordplay}{\ddag}   % wordplay note
\newcommand{\notesymgrammar}{\textgreek{α}} % grammar note
\newcommand{\notesymvocab}{\textgreek{λ}}   % vocabulary note

\newcommand{\gmarkdot}[1]{%
  {\color{greekcolor}%
    \setbox0=\hbox{#1}%
    \leavevmode
    \vtop{\offinterlineskip
      \copy0\kern0.8pt
      \hbox to \wd0{\color{grammarmark}%
        \xleaders\hbox to 2.5pt{\hss\rule{1pt}{0.4pt}\hss}\hfill}}}}
```

- **Running headers with paracol workaround** — paracol swallows `\markboth`, so headers are set through global macros (`\setchapterheads{left}{right}`) emitted by the generator, consumed by fancyhdr page style `body` (chapter name LE / Greek rhapsody RO, page numbers on outer edges).
- **Chapter styling** (`preamble/styling.tex`): right-aligned two-line display — small-caps `BOOK \Roman{chapter}` over huge bold title via titlesec; chapters actually generated as `\chapter*` with manual `\addcontentsline` so the TOC entry combines English + Greek titles. Drop caps via lettrine (2 lines, colored), epigraph package configured flush-right.
- **Custom TOC** (`front-matter/toc.tex`): hand-built longtable — `Book I | \pageref{book:1} | English title \newline {\small\color{textmid}\textit{brainrot subtitle}}` — bypassing the .toc file entirely for the book list; `tocdepth=0`, no dot leaders.
- **Interior colors are grayscale only** (AGENTS.md rule): `colors.tex` defines a "classical palette" where all accents are literally black/gray (`bookblue = RGB 0,0,0`), Greek text at RGB 110/110/110 so it "recedes visually", English black. Cover files carry their own independent color palette (terracotta/wine/gold).
- **Front matter:** half-title, title page (ΙΛΙΑΣ in GFS Complutum, credits "Based on the 1904 Pallis · English by Michael J Bommarito II"), copyright page with full **PCIP (Publisher's Cataloging-in-Publication) block, LCC/DDC classification, AI-assistance disclosure**, dedication, custom TOC, introduction. `\cleardoublepage` is temporarily disabled during front matter to avoid blank pages, restored for main matter; blank pages patched to be truly empty.
- **Back matter:** generated glossary (1,010 lines of .tex), translator's note, about-the-source, ISBN barcode assets.
- **Misc craft settings:** `\setstretch{1.0}` ("tight spacing to control page count"), widow/club penalties 10000, `\emergencystretch=2em`, microtype with `nopatch=footnote`.

## 4. EPUB Pipeline

Home-grown, dependency-light EPUB 3 builder at `epub/converter/cli.py` (371 lines, typer CLI, invoked `python -m converter`). No pandoc, no LaTeX involvement: it renders **directly from the same translation JSON**.

- Chapter XHTML per book: line pairs as `<span class="line-num">` + `<p class="greek">` + `<p class="english">`, stanza notes in a bordered `<div class="stanza-notes">`, `<hr class="scene-break"/>`.
- `nav.xhtml` TOC, `content.opf` with dc: metadata (title, creator, language, subjects, description, `dcterms:modified`, `urn:uuid` identifier), cover `<item properties="cover-image">` + cover.xhtml.
- Embedded ~110-line CSS stylesheet (serif stack `"Libertinus Serif", "EB Garamond", Georgia, serif`; wine/gold accents `#781c2a`/`#b49032` — notably the EPUB keeps color that print dropped).
- Zip assembly done manually with `zipfile` — `mimetype` written first with `ZIP_STORED` (correct EPUB requirement), then META-INF/container.xml, OEBPS content.
- Cover: `make cover-image` renders `cover-standalone.tex` → `pdftoppm -jpeg -r 300` → `epub/cover.jpg`, copied into `epub/templates/images/` before packaging.
- **No epubcheck / validation step** — the one gap in an otherwise complete pipeline.

## 5. Build Automation (scripts/ + Makefile)

`latex/Makefile` (425 lines) is the orchestrator; colored/emoji output, `.texlive-cache` TEXMF isolation, wildcard TEX_DEPS so `make pdf` rebuilds when any preamble/chapter/figure changes. Key targets: `all` (chapters+pdf), `pdf`, `quick` (1 pass), `full` (3 passes), `release` (timestamped copy to `../build/pdf/`), `kdp` = pdf + kdp-cover-vars + kdp-cover, `lulu-paperback` / `lulu-hardcover` / `lulu-all`, `cover-standalone`, `cover-image`, `epub`, `isbn-barcode`, `watch` (`latexmk -pvc`), `validate`, `wordcount`, `pagecount`, `clean`/`cleanall`/`rebuild`, `help`.

Cover builds run xelatex **3 times** (TikZ `remember picture`) then flatten losslessly with Ghostscript:

```
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 \
   -dDownsampleColorImages=false ... -dColorImageFilter=/FlateEncode ...
```

Lulu variants reuse the *same* `kdp-cover.tex` by predefining a flag: `xelatex -jobname=lulu-pb-cover-raw "\def\LuluCover{1}\input{kdp-cover.tex}"`.

**Python scripts** (`uv run`, Python ≥3.12; deps pydantic/rich/lxml/typer; some use PEP-723 inline script metadata):

| Script | Purpose |
|---|---|
| `models.py` | Pydantic models for the whole pipeline — doubles as LLM structured-output schema and storage format ("format-agnostic data layer for LaTeX/HTML/EPUB rendering") |
| `generate_chapters_tex.py` | JSON → paracol chapter .tex; LaTeX escaping, line numbers, `\gmarkdot` marked-word underlines, note symbols, scene breaks, TOC entries, running-header macros; `--book N` |
| `generate_glossary_tex.py` | glossary.json → back-matter glossary.tex (function-word table + alphabetical entries with examples + thematic index) |
| `update_cover_vars.py` | pdfinfo page count → spine width → writes `\CoverWidth/\CoverHeight/\CoverSpineWidth/...` vars file per platform. Formulas: KDP `pages*0.002252+0.06` (white) / `*0.0025` (cream); Lulu pb `pages/444+0.06`; Lulu hardcover from a 26-row lookup table; bleeds 0.125" pb / 0.875" hardcover case wrap |
| `generate_isbn_barcode.py` | python-barcode + Pillow ISBN barcode (PDF+PNG) for the back cover |
| `sample_stanza.py` | Random stanza sampler for QA (`--book/--stanza/-n/--seed`), prints Greek+English side by side with mood/notes |
| `gen_album_art.py` | Album art via OpenAI gpt-image-1 or Gemini image model; shared painterly "style spine" prompt + 4 concepts; `--dry-run` |
| `title_cover.py` | Pillow compositing of title typography onto generated art ("text is NOT baked by the image model — we add it here for control and correct Greek glyphs"); EB Garamond system fonts |
| `build_album.py` | Suno WAVs → RIFF metadata remux, MP3 320k with embedded cover, M3U playlists; embeds **AI disclosure tags** (`AI_GENERATED=true`, `AI_TOOL=Suno`, `AI_DIGITAL_SOURCE_TYPE=compositeWithTrainedAlgorithmicMedia`) |
| `retag.py` / `embed_cover.py` | ffmpeg lossless retagging / cover replacement for the album |

Notably **absent** here (present in Ovid): the translation script itself. Translation was run in a separate `parallel-reader/` project; CLAUDE.md warns "NEVER re-run the translation pipeline… it would overwrite data/translations and destroy all QA fixes."

## 6. Data Pipeline

```
Pallis Greek (Gutenberg #36248) → [parallel-reader project] → data/source.json
source.json + character_bible + book_summaries → GPT-5.4 stanza translation → data/translations/book_*.json
book_*.json  ──generate_chapters_tex.py──►  latex/chapters/book_*.tex ──make pdf──► main.pdf
book_*.json  ──epub/converter─────────────► iliad-brainrot.epub
glossary.json ──generate_glossary_tex.py──► back-matter/glossary.tex
```

- **Chunking unit = stanza** (Pallis' own paragraphing), each with 1-based `line_index` plus book-wide `global_line`; the 1:1 line constraint is enforced structurally (every Greek line has exactly one English line in the JSON).
- Translation JSON preserves full provenance: `model: "openai:gpt-5.4"`, per-stanza timestamps.
- Post-translation enrichment happens **in the JSON**: grammar notes (`note_type: "grammar"` + `marked_words`) were added book-by-book by an AI/human workflow governed by the docs/ apparatus (§8), then chapters regenerated.
- CLAUDE.md encodes ordering hazards as hard rules, e.g. "NEVER run generate_chapters_tex.py until Task 3 (generator update) is complete" — the project treats generator/schema version skew as a first-class risk.

## 7. Metadata & Publishing (+ album production)

**METADATA.md is a complete self-publishing playbook** (530 lines) — arguably the most reusable single document in the project. Contents: build commands and output-file→upload-destination table; build stats (682 pp, spine ~1.596", margins vs KDP minimums); KDP form-field walkthrough (title/subtitle, contributors listing **Homer as Author and Pallis as Translator**, series, edition); **AI content disclosure recommendations** for text/images/translation; Amazon HTML description (with allowed-tag list) + plain-text Bowker variant + 250-char short + 60-char one-liner + marketing taglines; Bowker subject choices and full **BISAC code table** (FRE013000, POE005020, POE005050…); category strategy (3 picks + alternates + "request more via KDP support"); **7 keyword slots with per-keyword rationale**; pricing analysis against Loeb/Fagles/Wilson comparables landing at $29.99; a market-gap analysis ("no parallel Homer uses Modern Greek…"); pre-publication checklist; a one-table "Quick Reference: Form Completion"; full **PCIP/LCC block**; and sourced links to KDP/Bowker docs.

**Cover process:** AI art (gpt-image-1) → `figures/cover-art.png` → TikZ overlay composition in `kdp-cover.tex` (back-cover hook/description/author-box/ISBN barcode; rotated spine text with letter-spacing; front cover = full-bleed art + translucent banners for title/author). One tex file, three platforms via `\def` flags and swapped vars files.

**Album production (`album/`):** README.md is a full A&R document — concept ("where the book drags Homer terminally online, the album drags him up the mountain"), *Nightfall in Middle Earth* structural analysis, 4-act / 23-track architecture, **leitmotif system** (Wrath motif, Hector's theme, Olympus choir, the Armor fanfare, dogs-and-birds lyrical motif), production philosophy (voice casting, choir-as-the-dead, "Greek used sparingly and ritually"). Each `tracks/NN-slug.md` carries: source-line citation to Pallis, a **≤1000-char self-contained Suno style prompt** in a code fence, a prose composition description, leitmotifs introduced, and full lyrics. `album-art-prompt.md` has tool-agnostic + Midjourney + SD-negative prompt variants. Scripts then master/tag the Suno output (§5). This is a complete, reusable **book→companion-album pipeline**.

## 8. Style / Craft / AI-Tone Guides

- **CLAUDE.md**: project map, key commands, source provenance, the source-of-truth diagram, CRITICAL do/don't lists (never edit generated .tex; never re-run translation; generator-version hazard), grammar-notes workflow (read diary → read curriculum → add notes → update diary + status), publishing targets, dependency list.
- **AGENTS.md**: agent-facing QA guide — what to check when spot-checking: *"1:1 line matching… Register consistency: English should sound internet-native, not academic… Quiet moments: grief, tenderness, and death scenes should use simple language, not forced slang… Note accuracy."* Plus conventions: grayscale interior, XeLaTeX required, "Book 13 does not exist."
- **Register/voice** lives partly in `character_bible.json` (e.g., Achilles: *"Keep him slangy but never unserious in grief scenes; when he talks smack, let him sound brutally funny and lethal"*) and `conventions` entries — voice rules stored **as data**, shipped into every translation prompt.
- **docs/ — the pedagogy engine** (unique to this series):
  - `greek-pedagogy-taxonomy.md` (664 lines): design philosophy, inventory of the existing ~2,740 margin notes by type, Bloom's-taxonomy mapping for the curriculum.
  - `greek-curriculum-linear.md` (515 lines): text-anchored linear curriculum — "Every grammar note must point to a specific Greek word or phrase visible on that page. We never teach in the abstract." Includes corpus statistics (111,549 tokens; top-50 words = ~45% coverage) used to sequence teaching.
  - `grammar-notes-diary.md` (588 lines): **cumulative reader-knowledge-state diary** — "Rule: Never re-teach. Always build forward." Updated after every book; the mechanism that gives a stateless LLM long-range curricular memory.
  - `grammar-notes-status.md`: per-book progress dashboard table (book / status / note count / concepts / verified).
  - `grammar-notes-implementation.md` (412 lines): full technical spec of the `marked_words` feature across JSON → Python → LaTeX, with validation rules and parallelizable task breakdown.

## 9. QA / Review Workflow

- `scripts/sample_stanza.py` — seeded random stanza sampling for human/agent review (AGENTS.md defines the review rubric).
- `make validate` — PDF page-size check against 504×720pt, grep of the .log for undefined references and overfull-box count.
- Grammar-notes process requires updating diary + status docs after each book ("Verified: Yes" column).
- Structural QA is otherwise implicit in Pydantic validation. The heavier automated QA suite (qa_source/qa_translations/audit_notes/fix_marked_words) was developed later in the series — see the Ovid report.

## 10. Verdict — What to Extract for the Master Template

**Take wholesale (highest value):**
1. **The JSON-as-source-of-truth architecture** with Pydantic models shared between LLM structured output, storage, and renderers — plus the "generated files are never edited" doctrine and its CLAUDE.md phrasing.
2. **The paracol parallel-verse layout**: 70/30 column ratio, stanza-sync/scene-break commands, hanging-indent verse pairs, every-5-lines line numbers, `\gmarkdot` dashed underline, note-symbol system, and the `\setchapterheads` paracol-header workaround. This is a solved, print-proven design for bilingual verse.
3. **`update_cover_vars.py` + `kdp-cover.tex`**: fully platform-parameterized wrap covers (KDP/Lulu pb/Lulu hc from one TikZ file), spine formulas + Lulu hardcover lookup table, Ghostscript flattening, 3-pass TikZ builds. Directly reusable for any trim size.
4. **The Makefile** nearly verbatim (parameterize title/trim), including `release`, `watch`, `validate`, and the TEXMF cache isolation.
5. **METADATA.md as a template document** — the KDP/Bowker/BISAC/keywords/pricing/PCIP structure generalizes to any book.
6. **The docs/ pedagogy pattern** (curriculum + cumulative diary + status tracker + implementation spec) — the general pattern is "persistent state files that let serial LLM passes build on each other"; reusable far beyond language teaching.
7. **The zero-dependency EPUB builder** — small, correct (stored mimetype first), renders from the same JSON.
8. **Album kit** (optional module): track-file format with embedded Suno prompts, art-prompt document, ffmpeg tagging scripts with AI-disclosure metadata.

**Pitfalls to fix in the template:**
- Chapter list in `main.tex` is hard-coded (and the Book-13 skip is manual) — the template should generate the `\input` list.
- EPUB has **no epubcheck** step and its OPF metadata is hard-coded in Python rather than read from a config; the metadata should come from one shared source (the same place METADATA.md fields live).
- `make cover-image` writes through a fixed `/tmp/iliad-cover` path.
- Iliad's `escape_latex` is naive (no markdown bold/italic handling, no control-char stripping) — Ovid's version supersedes it.
- The translation pipeline lives outside the repo (`parallel-reader/`), so this project alone is not end-to-end reproducible; Ovid fixed that.
- Duplicated near-identical code between the two projects (generators, Makefile, cover tooling) is exactly the copy-paste drift the master template exists to eliminate.

**Unique to this project:** the Greek typographic details (GFS Complutum display font, polyglossia `variant=monotonic`, Greek note symbols α/λ), the 682-page production numbers as a worked KDP example, and the complete companion-album production line.
