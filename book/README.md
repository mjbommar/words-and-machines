# book-template

A complete, configurable book-production template distilled from ten-plus
real book projects (several published on KDP and Lulu). One `book.yaml`
drives everything: print interiors, ebook PDF, an accessibility-audited
EPUB 3, wrap covers with computed spine widths, PDF/X-1a and ONIX 3.0
distribution artifacts, KDP metadata, and the AI-assisted writing
workflow — with release gates that make the result reproducible
byte-for-byte.

## Quickstart

```bash
# 1. Instantiate ("Use this template" on GitHub, or clone)
git clone <your-new-repo> mybook && cd mybook

# 2. Personalize (rewrites book.yaml + README; --fresh clears sample chapters)
uv run scripts/init_book.py --title "My Book" --author "A. Name" \
  --publisher "My Press" --description "One-paragraph back-cover copy." --fresh
# (omit --description and builds will refuse to run until you write one
#  in book.yaml — it feeds the cover and the EPUB metadata)

# 2b. Adopt the AI-instructions template for YOUR book
cp docs/CLAUDE-TEMPLATE.md CLAUDE.md   # then fill in the "This book" block

# 3. Build
make pdf            # print interior (trim size, black links)
make epub           # EPUB 3, validated with epubcheck
make kdp-cover      # wrap cover with spine computed from page count
make check          # style + prose gates
make validate-all   # every gate below
```

Requires: TeX Live (LuaLaTeX/XeLaTeX + latexmk + biber), `uv`,
poppler-utils, Ghostscript, ImageMagick, epubcheck, Java, Node.js
(for the Ace accessibility audit; fetched via `npx` on first run).
Run `make doctor` to audit your toolchain and fonts.

## What's inside

| Where | What |
|-------|------|
| `book.yaml` | Single source of truth: title, author, ISBNs, trim, fonts, editions, Kindle DRM, per-type AI disclosure — everything derives from it (ADR 0002) |
| `latex/` | Modular preamble (3 font profiles, 4-layer color system, semantic boxes, code listings, build-mode flags), sample chapters exercising every feature |
| `epub/converter/` | Book-agnostic LaTeX→EPUB 3 converter with handler registry, generated OPF/nav, and an EPUB Accessibility 1.1 / WCAG 2.2 AA conformance claim backed by the Ace gate |
| `scripts/` | Metadata generation, spine math, style/prose gates, print preflight, cover ink gate, PDF/X-1a distill, ONIX 3.0 export, citation verify+archive, narration export, stats, plus advisory prose-quality tools (OpenGloss vocabulary variety, burstiness/lexical-diversity metrics vs a house baseline, multi-level slop audit with LLM judge, Pangram detector cross-check) — all `uv run`, zero install |
| `docs/guides/` | STYLE / STYLE-AI-TELLS / STYLE-CRAFT, writing process, review-QA recipes, citations, research contracts |
| `docs/publishing/` | KDP runbook, metadata dossier template, release checklist, cover spec, narration channels |
| `docs/CLAUDE-TEMPLATE.md` | Per-book AI instructions to copy over `CLAUDE.md` and adapt (premise, voice, register + the full operating manual) |
| `docs/decisions/` | Twelve ADRs recording why the template works this way |
| `docs/research/` | Reviews of the fifteen source projects this template distills |
| `.claude/agents/` | Curated agent library for the AI-assisted workflow (`CLAUDE.md` orchestrates) |

## The gates (`make validate-all`)

| Gate | Catches |
|------|---------|
| `epubcheck` + strict coverage audit | Invalid EPUB; any LaTeX construct the converter didn't handle |
| `make epub-a11y` (Ace by DAISY) | Serious/critical accessibility violations — backs the OPF's EPUB Accessibility 1.1 / WCAG 2.2 AA claim (the EAA has required this in the EU since 2025) |
| `make preflight` | Non-embedded fonts, Type 3 fonts, images under 300 ppi — the top POD rejection causes |
| `make cover-ink` | Cover total ink above the 240% press cap (measured per pixel via separations) |
| `make check` | Style violations, banned words/phrases, AI-tell patterns |
| `make doctor` | Missing tools, unresolvable fonts, stale cover vars, placeholder values, doc/Makefile drift |

`make release` adds `make pdfx` (PDF/X-1a:2001 interior for
IngramSpark/Lulu), `make onix` (onixcheck-validated ONIX 3.0 feed with
accessibility codes), and `make verify-citations` — then packages
everything with SHA256SUMS and a `TOOLCHAIN.txt` rebuild recipe. Builds
are byte-reproducible: `SOURCE_DATE_EPOCH` is pinned to the last commit,
and CI runs a frozen TeX Live container.

## The rules that keep books shippable

1. **Never hand-edit `latex/generated/` or `build/`** — regenerate from `book.yaml`.
2. **No literal title/author strings in sources** — metadata macros only.
3. **Chapters use only the authoring contract** (`docs/architecture/authoring-contract.md`); it's what the EPUB converter parses.
4. **Verify and archive citations before shipping** — `uv run scripts/verify_citation.py --archive` stamps `verified=` and pins a Wayback `archived=` snapshot per URL (a prior book measured 57% URL rot/error before verification); the release gate requires both.
5. **`make release` refuses** a dirty tree, failing gates, or missing ISBNs.

## Editions

Declare variant editions (abridged, essential) in `book.yaml` as chapter
include-lists and build with `make pdf EDITION=essential`. Same chapter
files, no forked prose (ADR 0011).
