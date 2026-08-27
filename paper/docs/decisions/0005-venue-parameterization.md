# ADR 0005 — Venue is a first-class knob (preprint/arxiv/ssrn)

## Decision
`venue.target` drives venue-specific behavior: `arxiv` adds alt-text linting, a
`00README.json`, `make arxiv` packaging, and a license line; `ssrn` adds the
JEL block, the "Working paper — draft" line, the Disclosures back-matter, and
`make ssrn` dossier; `preprint` is the clean intersection.

## Evidence
The portfolio's arXiv and SSRN papers differ precisely along these axes (the
survey's SSRN-vs-arXiv table): JEL codes, disclosures, submission-metadata
files, packaging. Encoding the venue lets one source serve both.

## Consequences
- The submission mechanics follow the venue automatically; the author sets one
  field.
- SSRN's 2026-06-15 AI-disclosure requirement is enforced by `--strict`.
