# ADR 0004 — Dual bibliography: natbib (default) or biblatex

## Decision
`citations.system` selects natbib+bibtex (default) or biblatex+biber, behind
one `\PrintBibliography` macro. biblatex is loaded with `natbib=true` so the
SAME `\citep`/`\citet` section source compiles under either system.

## Evidence
arXiv robustness favors natbib: its `.bbl` is version-agnostic and ships
trivially. The scholarly house block (datacenter/moratorium) uses biblatex
authoryear + biber. biblatex's `.bbl` must match arXiv's format version (3.3 on
TL2025), a real friction the default avoids.

## Rejected
- biblatex-only: the `.bbl`-format-mismatch error is a recurring arXiv
  submission failure; a template shouldn't default into it.
- natbib-only: loses the scholarly authoryear house block the SSRN papers want.

## Consequences
- `make arxiv` reports the detected biblatex `.bbl` format as a check.
- Section prose is citation-system-agnostic (never rewritten on a switch).
