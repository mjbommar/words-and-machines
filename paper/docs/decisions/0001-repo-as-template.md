# ADR 0001 — A dedicated paper template, sibling to book-template

## Decision
Build a standalone `paper-template` repo for arXiv/SSRN papers, mirroring
`book-template`'s architecture (single-source metadata, modular preamble,
self-documenting Makefile, uv-run scripts, ADRs, `.claude/agents`) rather than
extending book-template or copying a single existing paper.

## Evidence
A survey of 11 `paper/` repos and 5 `latex/`-dir papers found the same
boilerplate copy-pasted with drift across 8+ papers: the package stack, the
hyperref color+metadata block, the LLM-assistance `\thanks`, URL-break hacks,
and the latexmk `clean` recipe. arXiv packaging was re-implemented per repo.
A template centralizes exactly this shared DNA.

## Rejected
- Extending book-template: books (memoir/book class, EPUB, covers, ISBNs, KDP)
  and papers (article class, arXiv source rules, JEL, referee review) diverge
  too far; one config schema would serve neither well.
- Copying one paper (e.g. ioctl-census): captures the arXiv house style but not
  the SSRN cluster's biblatex/JEL/disclosures world.

## Consequences
Two sibling templates share conventions (Makefile vocabulary, ADR format,
`make doctor` drift audit) without sharing a codebase.
