# Chapter 15 sources and claim routes

## Algebra, algorithms, and history

- Hamming, “Error Detecting and Error Correcting Codes” (1950), already in the
  bibliography. Use for the coding-theory question of which error patterns a
  check detects or corrects. Do not describe XOR folding as a cryptographic
  hash or general error-detecting code.
- Blelloch, *Prefix Sums and Their Applications*, CMU-CS-90-190 (1990).
  Primary report located 2026-08-30. Use for scan as a reusable parallel
  primitive, the distinction between total reduction and all-prefix results,
  and the work/span tree. Do not imply that Blelloch originated every fold or
  reduction operation.
- Dean and Ghemawat, “MapReduce: Simplified Data Processing on Large Clusters”
  (OSDI 2004). Primary Google publication page located 2026-08-30. Use for the
  map/reduce interface, automatic partitioning, scheduling, failure handling,
  and inter-machine communication. Do not equate its keyed reduce phase with
  this scalar fold without explaining the additional grouping and runtime.

## Current architecture and compiler sources

- RISC-V unprivileged ISA, ratified V extension 1.0, official specification.
  Its integer reduction instructions include `vredxor.vs`; inactive elements
  are excluded and the scalar seed is included. Use only as a boundary and
  extension comparison because the flagship listing is RV64I scalar.
- LLVM Auto-Vectorization documentation, current official page checked
  2026-08-30. It explicitly recognizes reduction variables and supports XOR,
  AND, OR, multiplication, and addition reductions. The loop vectorizer uses a
  cost model and may choose vectorization and unrolling factors. Treat this as
  current implementation documentation, not a theorem about every target.
- Intel 64 and IA-32 Architectures Optimization Reference Manual, official
  current volume. Use for memory and vectorization considerations only after
  reading the relevant sections. Do not turn processor-family guidance into a
  context-free cycle claim.
- Pinned RV64I and x86-64 architectural sources already recorded in the
  book-wide ISA source inventory remain authoritative for the scalar listings.

## Parallel and distributed contracts

- MPI Forum, global reduction operations. The standard assumes a user-defined
  operation is associative and may exploit associativity or commutativity to
  change evaluation order. It warns that reordered floating-point addition may
  change the result. Use for the distinction between algebraic permission and
  bitwise reproducibility.
- Work is the total number of primitive operations. Span is the longest
  dependency path. A balanced tree reduction over `n` values has linear work
  and logarithmic span under the ideal binary-combine model; the scalar fold
  has linear work and linear span. State the machine and communication
  assumptions before turning these into performance claims.

## Textbook comparison

Compare the final treatment with at least two of:

1. CLRS material on loop invariants and parallel algorithms.
2. *Concrete Semantics* for small executable semantics and induction.
3. *Software Foundations* for proof-script presentation and exercises.
4. A computer-architecture text's scalar/SIMD loop treatment.

The comparison should sharpen the chapter's distinctive route: one complete
mathematical fold, three byte-level machine obligations, a stuttering
simulation, and a fail-closed evidence boundary.

## Live Axeyum audit

This is the 2026-08-30 pre-implementation snapshot. The implementation
follow-up below supersedes its capability conclusions while preserving the
research trail.

Refreshed 2026-08-30 against `../axeyum`, branch
`research/open-problems-2026-08`, commit
`a9991fdad6c1e4b2bda596b46d2c8c715556ceae`.

- Searches over `crates/` and `python/` found no reusable A0, RV64, or x86
  state/decoder/step package.
- Existing bit-vector, SAT/SMT evidence, DRAT/LRAT, Alethe, and Lean routes are
  ingredients, not machine semantics for these listings.
- The illustrative Python import in the manuscript remains future design.
- Do not claim machine-produced evidence, assembled-byte replay, or a universal
  cross-ISA theorem until the decoders, semantics, harnesses, relations, and
  manifests exist and run.

## Implementation follow-up

Refreshed 2026-08-31 against the integrated Axeyum checkout at commit
`a257d7cd639caf101c03e9bba21864267b97b66e`.

- `axeyum-machine` now supplies the A0, RV64I, and x86-64 concrete machine
  surfaces required by the book.
- `axeyum-machine-evidence` executes the exact complete Chapter 15 programs
  over eight declared lists and checks typed cut-point relations.
- The active manifest runs its producer, positive checker, and firing negative
  control. This is finite executable evidence, not the universal loop theorem.
- The former illustrative Python listing has been removed. The manuscript now
  prints only interfaces exercised by the repository's exact-listing gate.

## Build and tooling observations

- `llvm-mc`, `clang`, the system x86-64 assembler, and `objdump` are available
  locally. Use independent assembly/disassembly to derive exact x86 bytes.
- No dedicated `riscv64-linux-gnu-as` was found on the initial path check.
  `llvm-mc` can be evaluated for the RV64I listing, with target and feature
  flags recorded.
- Keep source syntax, assembler version, target triple, entry address,
  disassembly command, and raw byte digest together. Assembly output is an
  artifact, not a source-of-truth replacement for the ISA specification.
