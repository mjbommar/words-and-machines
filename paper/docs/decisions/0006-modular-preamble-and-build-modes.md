# ADR 0006 — Modular preamble with fixed load order; build modes via pretex

## Decision
`preamble/main.tex` loads modules in a documented, dependency-ordered sequence
(packages → fonts → colors → styling → boxes → code → commands → hyperref-last).
Build variants come from `-usepretex` flags (`\DraftMode`, `\AnonMode`) with
distinct `-jobname`s, building out-of-tree into `build/`.

## Evidence
book-template's ADR 0005/0006; the SSRN cluster already used a
packages/fonts/colors/styling/commands split. hyperref-last avoids the standard
footgun (it patches refs/floats/footnotes); cleveref must follow hyperref.

## Rejected
- Monolithic preamble (the portfolio's older papers): chapters/sections pasted
  copies that drifted.
- Separate main-draft.tex/main-anon.tex entry files: they drift; conditionals
  in one entry file stay coherent.

## Consequences
Each module states what it provides, depends on, and its provenance. Retheming
= edit color primitives + font profile; nothing else.
