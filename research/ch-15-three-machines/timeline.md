# Chapter 15 working timeline

## 2026-08-30 — contract opened

- Inherited manuscript: 6,304 source words and 22 exercises.
- Preserved spine: XOR-fold contract, empty case, alignment/range premises,
  logical invariant, A0/RV64I/x86-64 listings, local lemma decomposition,
  stuttering cut points, concrete trace, negative controls, cost caution,
  staged Axeyum design, and explicit stopping point.
- Set the completion target at 18,000--25,000 words and at least 50 exercises.
- Located primary Blelloch, MPI, MapReduce, RISC-V vector, LLVM vectorizer, and
  Intel optimization sources for the history, foundations, and industrial
  layers.
- Refreshed the live Axeyum boundary at commit
  `a9991fdad6c1e4b2bda596b46d2c8c715556ceae`; no A0/RV64/x86 machine package
  was found.

## 2026-08-30 — depth pass closed

- Expanded the chapter to 18,005 source words and 71 exercises.
- Added GF(2), commutative-monoid, fold-splitting, homomorphism, chunking,
  work/span, vector-order, and distributed-reduction foundations.
- Assembled the RV64I listing with LLVM 21.1.8 into 36 bytes and the x86-64
  listing into 21 bytes; recorded exact address, byte, and instruction tables.
- Added intermediate loop assertions, architecture-specific proof routes,
  frames, progress arguments, a global agreement theorem, and failure theorem.
- Added parity-to-parallel history and current compiler, vector, bandwidth,
  communication, failure, ABI, validation, and maintenance economics.
- Preserved the evidence boundary: the chapter does not claim executable
  Axeyum certificates for machine packages that are not present.
- `make -C book simplified` passed with warnings only.
- `make -C book check` passed with warnings only.
- `make -C book pdf` produced a 539-page, 7-by-10-inch PDF. Chapter 15 occupies
  printed pages 421--468. A 48-page contact-sheet inspection found a balanced
  mix of prose, proofs, code, tables, figures, callouts, and exercises.

## Next

Open the Chapter 16 contract and audit its inherited manuscript before making
the next sequential depth pass.
