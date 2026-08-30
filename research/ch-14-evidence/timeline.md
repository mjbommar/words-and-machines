# Chapter 14 working timeline

## 2026-08-30 — contract opened

- Inherited manuscript: 5,526 source words, 18 exercises.
- Preserved spine: trust classes, binding chain, manifest, raw-byte rule,
  outcome contract, negative controls, small-checker design, vacuous proof,
  formula-generation boundary, independence, reconstruction, resource
  outcomes, reproduction, Axeyum route, and explicit stopping point.
- Opened research on resolution, DRAT, LRAT, Alethe, checker invariants,
  mutation and metamorphic controls, trusted-base measurement, artifact-review
  terminology, provenance, proof retention, and evidence economics.
- Located primary DRAT-trim, LRAT, Alethe, and ACM artifact-policy sources.
- Located the official *Software Foundations* and *Concrete Semantics*
  teaching sources and the current in-toto specification for the proof,
  pedagogy, and provenance comparisons.

## 2026-08-30 — foundations and evidence routes expanded

- Read the primary DRAT, LRAT, and Alethe papers and added a complete small
  resolution refutation, its inductive checker invariant, and a format
  tradeoff table.
- Added separate treatments of hashes, signatures, provenance, canonical
  bytes, mutation controls, metamorphic controls, evidence economics, and the
  ACM repeatability/reproducibility/replicability distinctions.
- Audited Axeyum at commit
  `a9991fdad6c1e4b2bda596b46d2c8c715556ceae`. Recorded the RUP-only LRAT
  boundary, three-way evidence-check result, route-specific Alethe variants,
  per-result trust ledger, and missing unified book-manifest interface.
- Expanded the exercise sequence from 18 to 50 problems, including resolution,
  proof formats, canonical encoding, provenance, controls, economics,
  reproduction, and an end-to-end evidence-package capstone.
- Compared the chapter's external-artifact pedagogy with the editable proof
  scripts of *Software Foundations* and the prose-plus-Isabelle route of
  *Concrete Semantics*.
- Closed at 12,142 source words and 50 numbered exercises. The inspected print
  render places Chapter 14 on pages 387--420; the chapter has no local overfull
  boxes and its 34-page contact sheet is visually balanced.
- `make -C book check` and `make -C book simplified` pass. LuaLaTeX produces a
  valid 509-page PDF. The `make pdf` wrapper still exits nonzero after reaching
  latexmk's pass limit because late bibliography back-reference page records
  alternate by one page; record this separately from manuscript correctness.

## Next

1. Resolve the book-level bibliography back-reference convergence defect.
2. Begin Chapter 15's sequential depth pass.
