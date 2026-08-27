# Research Report: ovid-brainrot

**Project path:** `/home/mjbommar/projects/personal/ovid-brainrot`
**Reviewed:** 2026-07-06, for extraction into the master book template.

---

## 1. Purpose & Status

**The Brainrot Metamorphoses: A Terminally Online Translation** — a parallel Latin / English edition of Ovid's *Metamorphoses* (all 15 books, 453 stanzas, 11,996 lines), with the Latin from The Latin Library and a new 1:1 line-matched English translation in "brainrot" register produced by GPT-5.4. Like its siblings, it is simultaneously a **Latin reader**: 132 progressive grammar notes, per-stanza vocabulary notes, a 300-entry frequency-ranked glossary, and a back-matter appendix of Latin declension/conjugation reference tables.

- **Series:** *Brainrot Classics*, **Book 4** — after The Brainrot Iliad (979-8-9947460-2-8), Odyssey (979-8-9947460-3-5), and Aeneid (979-8-9947460-4-2). ISBN assigned: **979-8-9947460-5-9**. This is the 4th iteration of the pipeline, and it shows: everything the Iliad did manually or off-repo is a script here.
- **Status:** Translation, notes, and QA **complete** (453/453 stanzas, 4,291 notes, zero failures; content review graded A/A/A- across book ranges). Interior **built**: `latex/main.pdf` exists at **680 pages, 504×720 pt**, and a generated `kdp-cover-vars.tex` (2026-03-29, spine 1.59136") is present. Phase 5 (cover art finalization, KDP/Lulu submission, EPUB) still open per TODO.md.
- **Formats:** 7"×10" paperback (KDP + Lulu pb/hc). EPUB planned ("adapt from Aeneid `epub/` directory"); the Makefile retains `cover-image` but the `epub` target was removed. `epub/cover.jpg` exists.
- **No album/** directory — the companion-album concept is Iliad-only (so far).

## 2. Directory Layout

```
ovid-brainrot/
  pyproject.toml            # uv; pydantic, pydantic-ai-slim[openai], rich, lxml, typer, python-barcode, pillow
  CLAUDE.md / README.md / TODO.md / METADATA.md
  data/
    raw/                    # IMMUTABLE downloads — never edit
      met_latin_book_*_raw.html          # 15 Latin Library HTML files
      metamorphoses_english_1_7.txt      # Gutenberg #21765 (Riley 1851, Books I-VII)
      metamorphoses_english_8_15.txt     # Gutenberg #26073 (Riley, Books VIII-XV)
    processed/
      latin/book_01..15.txt + metamorphoses_latin_complete.txt
      english/book_01..15.txt            # Riley prose — COMPARISON ONLY, not line-aligned
      manifest.json, coverage_report.json  # provenance + 15-book coverage audit
    translations/book_01..15.json        # SOURCE OF TRUTH (post-translation)
    source.json                          # 453 stanzas / 11,996 lines, Pydantic-validated
    character_bible.json                 # 98 characters, 10 factions, 16 places, 8 conventions
    book_summaries.json                  # 15 books: latin/english/brainrot titles, scenes, arcs
    glossary.json                        # 300 entries, frequency-derived
  scripts/                  # 17 scripts — full end-to-end pipeline (see §5)
  latex/                    # same skeleton as iliad-brainrot, Latin-adapted (see §3)
    back-matter/latin-tables.tex         # NEW: declension/conjugation appendix
    front-matter/cover/{kdp,lulu-paperback,lulu-hardcover}-cover-vars.tex  # generated
  docs/
    editorial-guide.md                   # voice/register bible fed into the LLM prompt
    latin-curriculum-linear.md           # grammar curriculum (phases per book range)
    grammar-notes-diary.md               # cumulative reader-knowledge state per book
```

**Raw→processed discipline** is stronger than the Iliad's: raw HTML/Gutenberg files are checked in and declared immutable; `processed/` is fully regenerable; `manifest.json`/`coverage_report.json` record provenance and coverage. CLAUDE.md spells out the safety rules: never edit generated .tex, never treat Riley prose as line-aligned source, never overwrite `data/raw/*`, never hand-edit the complete Latin file.

## 3. LaTeX Pipeline

A direct fork of the Iliad preamble with Latin substitutions — the diff is small and instructive for template parameterization:

- **Class/engine identical:** `\documentclass[10pt,twoside]{book}`, XeLaTeX + latexmk, same 7×10 geometry block (inner 0.9" / outer 0.625" / top 0.75" / bottom 0.875").
- **Fonts:** Libertinus + libertinust1math + Latin Modern Mono, but **no decorative `\titlefont`** (GFS Complutum dropped — that was Greek-specific). Polyglossia switches language:

```latex
\usepackage{polyglossia}
\setdefaultlanguage{english}
\setotherlanguage[variant=classic]{latin}
% Note: install texlive-lang-european for Latin hyphenation patterns.
% Latin renders correctly without it; it simply won't hyphenate at line breaks.
...
% Let hyperref pass Latin text through to PDF bookmarks as-is
\pdfstringdefDisableCommands{\let\textlatin\relax}
```

- **Verse-layout learning:** widow/club penalties relaxed from 10000 → 9000 and, crucially:

```latex
% Allow pages to end naturally (standard for verse/poetry layout)
\raggedbottom
```

This is a deliberate post-Iliad refinement for parallel verse (avoids vertical-glue stretching between stanzas on short pages).

- **Same paracol 70/30 parallel layout**, same `\scenebreak`/`\stanzasync`, same notes-column format. Renames: `\gmarkdot`→`\lmarkdot`, `greekcolor`→`latincolor`. Note symbols swap the Greek letters for small caps:

```latex
\newcommand{\notesymgrammar}{\textsc{g}} % grammar note
\newcommand{\notesymvocab}{\textsc{v}}   % vocabulary note
```

- Book letters are Roman numerals I–XV (Liber) instead of Greek rhapsody letters; running header RO shows the Liber. `\unnumberedchapter` gained `\phantomsection` (hyperref anchor fix).
- **New back matter:** `back-matter/latin-tables.tex` — a "Quick Latin Reference" appendix: pronunciation table (booktabs), five-case explanation, all declension tables, conjugation tables, built to mirror the curriculum. Example header:

```latex
\unnumberedchapter{Appendix}{Quick Latin Reference}
\noindent These tables are a pocket reference, not a textbook.
```

- `main.tex` is leaner (scaffold comments removed); includes all 15 chapters plus `back-matter/latin-tables` before glossary/translator-note/about-source.

## 4. EPUB Pipeline

Not yet ported: no `epub/converter/` here (TODO Phase 5: "EPUB build (adapt from Aeneid `epub/` directory)"). The Makefile keeps `make cover-image` (cover-standalone.tex → 300 DPI JPEG → `../epub/cover.jpg`, which exists) but the `epub` target present in the Iliad Makefile was deleted. For the template: the EPUB builder clearly lives as a copy-around module in this series — a strong argument for making it a shared package.

## 5. Build Automation (scripts/)

Same Makefile as the Iliad minus the epub target (title/paths swapped). The Python side is where Ovid shines — a **complete, in-repo, resumable pipeline** (all `uv run`, Python ≥3.12):

| Script | Lines | Purpose |
|---|---|---|
| `models.py` | 143 | Pydantic schema (same shape as Iliad: BookSource/StanzaSource/BookTranslation/StanzaResult/MarginNote…, `MetamorphosesSourceModel`) |
| `import_sources.py` | 439 | Latin Library HTML + Gutenberg Riley → normalized per-book text, manifest.json, coverage_report.json. Handles FONT-tag line-number artifacts, entity decoding |
| `apply_supplements.py` | 199 | Inserts 17 lines missing from The Latin Library (Books 4, 8) from the Hugo Magnus 1892 critical edition via Perseus; anchored by exact-substring "insert after" definitions; full provenance comment |
| `build_source_json.py` | 128 | Processed Latin → `source.json` (stanza boundaries = blank lines = Latin Library paragraph indentation) |
| `build_glossary_json.py` | 506 | Frequency analysis of source.json → 300-entry glossary; ships a large `KNOWN_WORDS` dict of Latin lemma → (meaning, POS) |
| `fill_glossary.py` | 125 | GPT-5.4 batch fill of glossary entries with unknown meanings (pydantic-ai structured output) |
| `translate.py` | 771 | **The AI translation engine** (see §6) |
| `add_grammar_notes.py` | 649 | **Phase-B grammar pass**: LLM adds `grammar` notes with validated `marked_words`, driven by curriculum + diary docs |
| `qa_source.py` | 773 | 15 automated source checks (see §9) |
| `qa_translations.py` | 455 | 9+ automated translation checks (see §9) |
| `audit_notes.py` | 434 | Note audit: valid types, empty text, line_ref range, duplicates, type distribution, random spot-check of `latin` notes vs source |
| `validate_marked_words.py` | 250 | Every marked word must be a substring of the referenced Latin source line; `latin`/`vocabulary` notes must have non-empty marked_words |
| `fix_marked_words.py` | 208 | Auto-repair of broken anchors: relocate line_ref → fuzzy-match casing → clear; fixed 132 broken anchors (11.5% → 0%) |
| `generate_chapters_tex.py` | 348 | JSON → LaTeX; **upgraded escaper** vs Iliad: strips control chars from GPT output, converts markdown `**bold**`/`*italic*` in notes to `\textbf`/`\textit` (with inner re-escaping), handles `…` and `→`; marks words from grammar **and** latin **and** vocabulary notes |
| `generate_glossary_tex.py` | 329 | glossary.json → back-matter glossary |
| `generate_isbn_barcode.py` | 177 | as Iliad |
| `update_cover_vars.py` | 456 | as Iliad (KDP/Lulu spine math, hardcover lookup table); output sample in `front-matter/cover/kdp-cover-vars.tex`: `\CoverSpineWidth{1.591360in}`, `\CoverWidth{15.841360in}` for 680 pages |

`pyproject.toml` adds the AI deps directly: `pydantic-ai-slim[openai]>=1.66.0`, plus `python-barcode`, `pillow` (moved from PEP-723 inline metadata into project deps).

## 6. Data Pipeline (source → book)

The README contains the canonical diagram:

```
Latin Library HTML (15 files)        Gutenberg Riley (2 files)
         └──── import_sources.py ─────────────┘
                      │
     processed/latin/book_01..15.txt   processed/english/book_01..15.txt
                      │  (apply_supplements.py between import and build)
           build_source_json.py
                      │
               source.json (453 stanzas, 11,996 lines)
         ┌────────────┴────────────┐
  build_glossary_json.py    translate.py (GPT-5.4)
         │                         │
    glossary.json          translations/book_*.json
         │                         │
  generate_glossary_tex.py  generate_chapters_tex.py
         │                         │
  back-matter/glossary.tex  chapters/book_*.tex
         └────────── make pdf ─────┘  → main.pdf
```

**AI translation workflow (`translate.py`)** — the most template-worthy artifact:

- **Atomic unit = stanza.** Per call: exactly-N-lines contract, structured output into `StanzaTranslation` via **pydantic-ai** `Agent(output_type=...)` on `OpenAIResponsesModel("gpt-5.4")`, `temperature=1.0`, `openai_reasoning_effort="none"`, `retries=3`.
- **Context assembly:** previous 2 stanzas (Latin+English+mood+scene flags), **character bible filtered to the book's cast** (with careful name matching — handles `Jupiter/Zeus` composites, strips parentheticals, exact-word match to avoid `Mars`⊂`Marsyas`), book summary + emotional arc, and the full `docs/editorial-guide.md` appended.
- **The system prompt is a serious piece of prompt engineering** (~350 lines): register definition with paired GOOD/BAD register-3 examples ("BAD: 'She was transformed into a tree.' → GOOD: 'Bark crawled up her legs and her arms branched out overhead.'"); a 5-level register-shifting spectrum mapped to specific episodes; Metamorphoses theme guidance (transformation described anatomically; divine power asymmetry; art-as-testimony); per-character voice specs (Jupiter "entitled frat-god energy", victims "dignified. Never play their suffering for laughs"); a **CRITICAL: SEXUAL VIOLENCE** rules block (never joke, use clear modern language, frame injustice as injustice); and 10 structural rules (exact line count; per-stanza minimum 3 notes; mandatory vocabulary note with `marked_words`; no `grammar`/`mood` note types in this pass; `scene_break` semantics; mood field spec).
- **Validation loop:** post-hoc checks for line-count mismatch and empty lines with up to 3 stanza-level retries (appending an explicit "PREVIOUS ATTEMPT FAILED: produced wrong number of lines" correction); normalizes line_index; strips stray mood notes; clamps line_refs; clears marked_words on note types that shouldn't have them.
- **Resumability & concurrency:** saves the whole book JSON after *every* stanza; re-runs skip completed stanzas; `--book 1 | 1-4 | 1,5,9 | all`, `--start-stanza`, `--parallel 4` (asyncio semaphore over books), `--dry-run` prints the assembled prompts without API calls.
- **Phase-B enrichment (`add_grammar_notes.py`):** separate resumable LLM pass that reads the **curriculum** (`latin-curriculum-linear.md`) and **diary** (`grammar-notes-diary.md`) into the prompt, emits 1–2 grammar notes per stanza via a dedicated `StanzaGrammarNotesOutput` schema (field validators cap note count; `marked_words` must be verbatim substrings, validated with retries), and enforces "don't re-teach concepts the reader already knows."
- **Production result:** 453/453 stanzas, 4,291 notes (avg 9.5/stanza), 113 scene breaks, zero failed stanzas, 4 books concurrent.

## 7. Metadata & Publishing

`METADATA.md` (606 lines) is the same playbook format as the Iliad's, updated: series fields (**Brainrot Classics #4**), contributors (Ovid as Author; explicit note that Riley is *not* a contributor since his prose was comparison-only), AI content disclosure recommendations, Amazon HTML description + Bowker plain text + short/one-liner/taglines ("Bodies change. Power corrupts. Love destroys. The vocabulary updates." / "ft. OVIDIVS x Bommarito"), BISAC table (FRE025000 Latin, POE005020/POE005050, LIT004120), Bowker category options, 7 keyword slots with rationale, KDP print options (7×10 B&W white, matte, margin table vs KDP minimums), **Lulu setup section** (pb + case-wrap hc), and content-rating notes ("nothing outside PG-13 bounds"). Some stats still say "TBD (translation not yet complete)" even though the PDF is built — the doc lags the build, a small template lesson (stats should be generated, not typed).

Cover: `latex/kdp-cover.tex` + `cover-standalone.tex` (same TikZ architecture as Iliad), `figures/cover-art.png` + `cover-art-original.png` present; all three platform vars files already generated for 680 pages.

## 8. Style / Craft / AI-Tone Guides

- **`docs/editorial-guide.md`** — the distilled voice bible, *fed verbatim into every translation call*. Six core principles ("Ovid is already subversive… Translate honestly and the tone takes care of itself"; "Transformation is physical… Do NOT summarize: 'she became a tree.' SHOW IT"; "Victims are not punchlines"; register follows Ovid's range with a per-episode temperature map; episodic structure = generous scene breaks; the narrator's ironic voice is content). Then **QA principles learned from the Aeneid production** — institutional memory in prose: "Stock meme labels erode over 15 books"; "Register 2-3 is the correction target, not 1"; "Specific brainrot beats generic brainrot"; "Accuracy is non-negotiable." Then scene-specific guidance for ~15 flagship episodes ("Narcissus: do NOT play him as just vain. He is trapped. The pool is a prison." / "Philemon and Baucis: The sweetest story in the poem. Protect it.").
- **`docs/latin-curriculum-linear.md`** — text-anchored curriculum in phases (Books 1-2 foundations → cases → verbs → participles/ablative absolute → Ovidian style), with the same design constraint as the Greek version ("Every grammar note must point to a specific Latin word or phrase visible on that page") and a note budget (~130 across 15 books, front-loaded). Leverages Latin-specific advantages: shared alphabet, English-derivative memory hooks ("corpus→corpse, forma→form, mutatas→mutation").
- **`docs/grammar-notes-diary.md`** — compact per-book "After Book N: *Reader knows:* …" state ledger, the anti-re-teaching mechanism consumed by `add_grammar_notes.py`.
- **CLAUDE.md / README.md / TODO.md** — CLAUDE.md is the operational guide (structure, commands, data-flow safety, current state, stats table); README is the public/GitHub-facing summary with the architecture tree and series table; **TODO.md is a phase-gated production log** (Phases 0–5 with every completed check recorded, including exactly which lines were missing from Book 8 and how they were restored) — an excellent template for tracking a data-driven book build.

## 9. QA / Review Workflow

The most developed QA regime in the series — three layers:

1. **Source QA (`qa_source.py`, 15 checks):** book presence; line counts vs Hugo Magnus critical-edition expected counts; sequential stanza/line numbering; no empty content; no duplicates; HTML artifacts; encoding/mojibake; hexameter line-length sanity (30–80 chars); first/last-line verification against known incipit/explicit; stanza-size sanity; cross-check source.json ↔ processed text files; known-gap tracking; Roman numeral checks; trailing line-number artifacts; cross-stanza continuity. Result: 0 errors, 7 large-stanza warnings.
2. **Translation QA (`qa_translations.py`, 9+ checks):** completeness (15 books, right stanza counts); per-stanza line-count match vs source; no empty translations; note validation (types, line_ref bounds, marked_words on vocab/latin); ≥3 notes/stanza; vocabulary note in every stanza; mood populated; scene breaks present; translation-length sanity; character-name consistency vs bible; residual-untranslated-Latin detection; **register-quality heuristics detecting overly formal language** (the "beheld/resolved/gazed" failure mode from the prompt, mechanized).
3. **Note/anchor QA:** `audit_notes.py` (distributions, duplicates, random spot-checks), `validate_marked_words.py` (every underline anchor verified against the actual Latin line), `fix_marked_words.py` (dry-run-by-default auto-repair with a relocate→fuzzy→clear strategy).

Plus **LLM content review**: "3 sub-agent passes sampling ~45 stanzas across all 15 books — Books 1-5: A, Books 6-10: A, Books 11-15: A-" (TODO.md) — human/agent literary QA layered on top of the mechanical checks.

## 10. Verdict — What to Extract for the Master Template

**Take wholesale (highest value):**
1. **`translate.py` as the generic AI-translation/book-generation engine**: stanza-atomic structured output, exact-line-count contract with retry-with-feedback, cast-filtered context injection, previous-N-stanza continuity, editorial-guide injection, per-stanza checkpointing, `--dry-run`, bounded parallelism. Only the system prompt's middle section is work-specific — the scaffolding is 100% reusable.
2. **The two-pass enrichment pattern** (`add_grammar_notes.py`): base translation first, then targeted LLM passes with their own output schemas + validators, driven by *external state documents* (curriculum + diary). Generalizes to any layered annotation.
3. **The three-layer QA suite** (qa_source / qa_translations / anchor validation+auto-repair). Especially: expected-count tables from an authoritative edition, register heuristics, and the validate→fix pair for anchored annotations.
4. **Raw→processed→source.json data discipline**: immutable `data/raw/`, regenerable `processed/` with `manifest.json` + `coverage_report.json`, and `apply_supplements.py` as the model for **documented critical-edition patches** with provenance.
5. **Ovid's `escape_latex`** (markdown→LaTeX conversion, control-char stripping, unicode handling) — strictly better than the Iliad's; use as the template's canonical text escaper for LLM-produced note text.
6. **Verse-layout refinements:** `\raggedbottom` + softened widow/club penalties for parallel verse; `\pdfstringdefDisableCommands` bookmark fix; `\phantomsection` in `\unnumberedchapter`.
7. **`latin-tables.tex`** as the pattern for a language-reference appendix, and **TODO.md's phase-gated log** as the production-tracking template.
8. **`docs/editorial-guide.md` structure** (principles → QA lessons from previous book → scene-specific map) — the "QA principles from prior production" section is how series-level craft knowledge compounds; the template should institutionalize that file.

**Pitfalls / gaps:**
- EPUB never ported — third copy-paste of the converter pending; the template must make it a shared package with metadata drawn from one config.
- The Iliad→Ovid diff is nearly all mechanical renames (greek→latin, `\gmarkdot`→`\lmarkdot`, book letters, PDF metadata) — prime candidates for template variables (`{{lang}}`, `{{book_letters}}`, `{{note_symbols}}`, hyperref metadata block).
- README/TODO/CLAUDE.md drift (README says grammar notes complete; TODO Phase 4 still shows them unchecked; METADATA says "pages TBD" while main.pdf is 680 pp). Generated status/stats would fix this.
- `models.py` is duplicated per project with a renamed root model (`MetamorphosesSourceModel` vs `IliadSourceModel`) — should be one shared model with a generic name.
- Riley English comparison text is imported and processed but its role downstream is thin (the translator never sees it in translate.py) — decide in the template whether a reference translation belongs in the prompt or in QA.
- Committed LaTeX build artifacts (main.log/aux/fls/xdv) — template needs a proper .gitignore for `latex/`.

**Unique to this project:** the complete in-repo AI pipeline (the Iliad's translation lived elsewhere), the Perseus supplement mechanism, the QA/auto-repair suite, register-heuristic linting, the Latin reference appendix, and series metadata handling (series name/number, cross-ISBN references).
