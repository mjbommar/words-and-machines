# ADR 0005 — Modular preamble with documented load order; 4-layer color system

## Decision
`latex/main.tex` inputs `latex/preamble/main.tex`, which loads modules in a documented, dependency-ordered sequence:

```
packages → fonts → colors → geometry → styling → boxes → code → [verse] → commands → hyperref-last
```

Colors use the 4-layer architecture (matured in vibe-coding/law-finance/beamer-template):
1. **Primitives** — Tailwind-style scales (`gray-50`…`gray-950`, one accent family)
2. **Semantics** — `text-primary`, `link`, `rule`, `callout-warning-bg`, …
3. **Components** — per-box/per-element bindings referencing semantics only
4. ~~Legacy aliases~~ — omitted; the template starts clean

## Rejected
- Single monolithic `preamble.tex` (ai-law-finance's 744-line version): review found four chapters had pasted copies of it, which then drifted.
- Color names carrying stale values (RFC book's `cyan-*` holding gold): semantic names must stay truthful; retheming swaps primitive values only.

## Consequences
- hyperref loads last (standard footgun), followed only by its setup.
- Each module has a header comment stating what it provides, what it depends on, and its provenance in `docs/research/`.
- Retheming a book = editing primitive scale values + font profile; nothing else.
