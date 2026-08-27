# ADR 0003 — LaTeX chapters are the canonical source; EPUB is converted from LaTeX

## Decision
Chapters are written in a **constrained LaTeX dialect** (the environments and macros defined by the preamble — nothing else). Print builds typeset it directly; the EPUB converter parses it. The allowed vocabulary is documented in `docs/architecture/authoring-contract.md` and doubles as the converter's parse contract (pattern proven by the-last-book's `lastbook.sty` PARSE CONTRACT).

## Alternatives considered
- **Markdown source + pandoc to both**: used only for early drafting (legal-tech's md→tex bridge); loses print typographic control (boxes, verse, precise floats) that every published book relied on.
- **Structured data (JSON) source**: right for data-driven books (brainrot series) — supported as an optional pattern (generate `.tex`, never edit it), not the default.

## Rationale
Every published book in the portfolio (datacenter, htsd, wiki, RFC) ended at .tex-as-source with a custom TexSoup converter for EPUB, after pandoc proved inadequate for code listings, semantic boxes, and footnote→endnote conversion. The converter beats pandoc *because* the input dialect is constrained.

## Consequences
- Adding a new environment/macro means adding both a LaTeX definition and a converter handler; `make epub-check` audits handler coverage and fails on unknown commands.
- Authors (human or AI) may not introduce raw low-level TeX in chapters; `check_style.py` flags it.
