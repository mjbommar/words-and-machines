# ADR 0011 — Editions declared in book.yaml as chapter include-lists

## Decision
`book.yaml` declares editions; each names an ordered chapter list (and may override title-suffix, ISBNs, trim):

```yaml
editions:
  full:
    default: true
    chapters: [ch01, ch02, ch03, ...]
  essential:
    title_suffix: "Essential Edition"
    isbn: { print: "...", epub: "..." }
    chapters: [ch01, ch03, ch07]
```

`make pdf EDITION=essential` generates `latex/generated/edition.tex` (an `\input` list) and builds with edition-specific metadata macros. The EPUB converter takes the same edition argument. Editions share every chapter file — **no forked prose**.

## Evidence
- datacenter's Essential Edition duplicated the preamble and hand-maintained abridged XHTML that bypassed the converter — the drift this ADR prevents.
- ai-law-finance's minibooks forked chapter content outright (review flagged content divergence).
- the-last-book's profiles-as-data (scope filters / curated section lists, `make EDITION=card|family`) is the proven clean version; this is its simplification.

## Consequences
- An edition needing *rewritten* (not re-selected) prose is a new book, not an edition.
- Serialized excerpts (ai-law-finance's `latex/serial/` 10-line wrapper docs) are documented in `docs/guides/WRITING-PROCESS.md` as a lightweight cousin of editions.
