# ADR 0006 — Build modes via pretex flags; out-of-tree builds; standard Makefile vocabulary

## Decision
One `main.tex` produces all output variants via conditionals set at build time:

- `\BleedMode` — trim + bleed geometry for POD wrap
- `\EbookMode` — screen geometry, colored links, no gutter
- `\GrayscaleMode` — B&W-safe colors for standard POD ink
- `\DraftMode` — watermark banner, line numbers off, `draft-` filename suffix
- `EDITION=<name>` — chapter include-list gating (ADR 0011)

Injected by the Makefile via `latexmk -usepretex='\def\BleedMode{1}'` with distinct `-jobname`s, building **out-of-tree** into `build/` (`-output-directory`). Target vocabulary standardized across the portfolio's Makefiles (RFC's 810-line Makefile is the reference; wiki/htsd/complexity confirm the vocabulary):

```
pdf quick bleed ebook grayscale draft          # interiors
cover-vars kdp-cover lulu-cover cover-image     # covers
epub epub-check                                 # digital
check stats doctor validate-all                 # QA
release watch clean                             # lifecycle
```

## Rejected
- Building inside `latex/` (RFC book): aux/log clutter got committed.
- Separate main-interior.tex/main-ebook.tex entry files (RFC): three entry docs drifted; conditionals in one entry file are easier to keep coherent. (Cover keeps its own entry file — it's a different document class.)

## Consequences
- `make doctor` verifies every target CLAUDE.md mentions actually exists (legal-tech's CLAUDE.md advertised targets its Makefile lacked).
- `release` copies artifacts to `releases/<date>-<printing>/` with SHA256SUMS.
