# Master Book Template — Plan

**Repo:** `mjbommar/book-template` (private GitHub template repo)
**Date:** 2026-07-06
**Sources:** 15 project reviews in [`docs/research/`](research/) covering every book project in `~/projects/personal` (7 published or near-published, 4 in-progress, 2 data-driven classics, 2 early-stage, plus `beamer-template`).

## 1. What this repo is

A **ready-to-build book project**. You create a new book by instantiating this repo ("Use this template" on GitHub, or `scripts/init_book.py`), filling in `book.yaml`, and running `make`. Everything — print PDF, bleed PDF, ebook PDF, EPUB, wrap cover, KDP dossier — builds from that one configuration plus the `.tex` chapters.

It consolidates the house architecture that evolved across ~10 books:

- `book` class, 6×9 US Trade (configurable trim), LuaLaTeX/XeLaTeX + fontspec
- Modular `preamble/` with documented load order
- 4-layer color system (primitives → semantics → components)
- Semantic tcolorbox environments and semantic inline macros that map 1:1 to EPUB CSS classes
- Build-mode flags (`\BleedMode`, `\EbookMode`, `\GrayscaleMode`, `\DraftMode`) injected by the Makefile — one source, many outputs
- Custom LaTeX→EPUB converter (generic core + handler registry, generated nav/OPF, epubcheck gate)
- TikZ wrap-cover + page-count-driven spine math (KDP + Lulu paperback/hardcover)
- Style/craft/AI-tells guides enforced by deterministic checker scripts
- `.claude/agents/` library + CLAUDE.md orchestrator for the AI-assisted writing workflow
- Citation-verification workflow (the datacenter book measured a 57% URL error rate before verification)
- KDP/publishing runbook, timestamped releases with SHA256SUMS

## 2. The one problem this template must solve

Every mature project in the portfolio was created by copying the previous book and renaming. The reviews found the same failure in five separate projects: **stale metadata and book-specific strings surviving the copy** — wrong ISBN in the RFC book's OPF, "Rough Consensus" leftovers in vibe-coding's `epub/`, RFC handlers in the datacenter converter, `[Author Name]` placeholders shipping in legal-tech's OPF, hand-typed stats drifting from builds.

Therefore the non-negotiable design rule:

> **`book.yaml` is the single source of truth.** Title, author, ISBNs, publisher, trim, fonts, editions, keywords, BISAC — everything derives from it. Generated files (`latex/generated/*.tex`, OPF metadata, KDP dossier skeleton) are never hand-edited and never committed. Builds **fail loudly** on unfilled placeholders.

## 3. Architecture summary

```
book.yaml ──► scripts/generate_metadata.py ──► latex/generated/metadata.tex
         │                                 ──► epub OPF/nav metadata
         │                                 ──► docs/publishing/KDP.md skeleton
         │
latex/chapters/*.tex  (canonical content, constrained authoring dialect)
         ├──► latexmk (LuaLaTeX) ──► print / bleed / ebook / grayscale PDFs
         ├──► epub converter     ──► EPUB 3 ──► epubcheck (0 errors gate)
         └──► scripts/check_*.py ──► style / prose / repetition gates
latex/cover/cover.tex + scripts/update_cover_vars.py ──► KDP & Lulu wrap covers
```

Component specs live in [`docs/architecture/`](architecture/); decisions with rationale in [`docs/decisions/`](decisions/).

## 4. Key decisions (see ADRs for rationale)

| # | Decision |
|---|----------|
| [0001](decisions/0001-repo-as-template.md) | Repo root is a buildable book; instantiate via GitHub template + `init_book.py` |
| [0002](decisions/0002-single-source-metadata.md) | `book.yaml` single source; generated artifacts gitignored; placeholder = build failure |
| [0003](decisions/0003-latex-canonical-source.md) | `.tex` chapters are canonical; EPUB is converted from LaTeX (documented parse contract), not pandoc |
| [0004](decisions/0004-engines-and-fonts.md) | LuaLaTeX default, engine-conditional; font profiles `libertinus` (default) / `garamond` / `plex` |
| [0005](decisions/0005-modular-preamble.md) | Load-order-documented preamble modules; 4-layer color system |
| [0006](decisions/0006-build-modes-and-makefile.md) | Mode flags via generated pretex; out-of-tree builds; standard Makefile target vocabulary |
| [0007](decisions/0007-epub-converter.md) | Book-agnostic converter package, handler registry, generated nav/OPF, epubcheck + validation gates |
| [0008](decisions/0008-cover-system.md) | TikZ wrap cover + spine formulas (KDP/Lulu) from page count; Ghostscript flatten |
| [0009](decisions/0009-style-enforcement.md) | STYLE / STYLE-CRAFT / STYLE-AI-TELLS guides with checker scripts; docs and checkers kept in sync |
| [0010](decisions/0010-python-tooling.md) | uv + one `pyproject.toml` for the converter package; PEP 723 headers for standalone scripts |
| [0011](decisions/0011-editions-and-variants.md) | Editions declared in `book.yaml` (chapter include-lists), built via `make EDITION=name` |
| [0012](decisions/0012-ai-workflow.md) | CLAUDE.md is the one canonical AI-instruction file (AGENTS.md points to it); phased agent library; citation verification from day one |

## 5. What we deliberately leave out

- **Knowledge-graph/ontology machinery** (the-last-book's RDF stack, legal-tech's SKOS graph) — overkill for a template; a plain `research/` scaffold with README contracts suffices.
- **TTS/audiobook tooling** — the one shipped audiobook used human narration from a script export; documented as a workflow note, not code.
- **pandoc EPUB pipeline** — proven inferior to the house converter for code/boxes; not worth maintaining two paths.
- **Book-specific data pipelines** (brainrot translation loops, Suno album kit) — documented as patterns in guides, not shipped as code.

## 6. Execution

See [`ROADMAP.md`](ROADMAP.md) for phases, deliverables, and acceptance gates. The build is done when `make validate-all` passes on the shipped sample book: print PDF, bleed PDF, ebook PDF, EPUB (epubcheck 0 errors), cover PDF with computed spine, style checks green, and `init_book.py` produces a renamed, buildable project.
