# Chapter 16 working timeline

## 2026-08-30 — audit opened

- Inherited manuscript: 4,565 source words and 22 exercises.
- Preserved spine: omitted-state map; floating point; vectors; concurrency;
  privilege and translation; mutable code; leakage; compilation; four
  extension gates; Axeyum stopping point.
- Identified the main gap: the sections named boundaries but rarely derived a
  concrete theorem, counterexample, state relation, or industrial tradeoff.

## 2026-08-30 — depth pass drafted

- Expanded to 10,450 source words and 54 exercises.
- Added abstraction functions and relations, a commuting-square proof pattern,
  and a proved invariant-transport proposition.
- Added an exact three-bit floating-point reassociation counterexample and
  separated bit equality, numerical error, exception history, and reproducibility.
- Added RISC-V vector element classes, mask and tail policy, a lane invariant,
  scalable-length proof scope, and implementation economics.
- Added the store-buffering litmus test, sequential-consistency cycle proof,
  operational/axiomatic distinction, and language/compiler/hardware stack.
- Added partial stateful translation, cross-page access, TLB agreement,
  two-stage translation, Denning's working-set history, and cloud resource costs.
- Added versioned code publication and the exact local limit of RISC-V
  \`FENCE.I\`.
- Added relational noninterference, declassification, constant-time evidence
  layers, speculative projections, and mitigation boundaries.
- Added compiler behavior refinement, real CompCert endpoints, undefined
  behavior, toolchain trust, and maintenance accounting.

## 2026-08-30 — depth pass closed

- `make -C book simplified` passed with warnings only.
- `make -C book check` passed with warnings only after replacing one banned
  register word.
- `make -C book pdf` produced a 553-page, 7-by-10-inch PDF.
- Chapter 16 occupies printed pages 471--499: 29 pages.
- A 29-page contact-sheet inspection found a balanced progression of prose,
  derivations, proof boxes, figures, tables, warnings, and exercises, with no
  chapter-local overfull boxes.

## Next

Perform the whole-book completion audit rather than assuming that the last
sequential depth pass makes every publication artifact complete.
