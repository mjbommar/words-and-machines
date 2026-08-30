# Chapter 16 source ledger

Access dates are 2026-08-30 unless otherwise recorded in the bibliography.

## Floating point

- IEEE 754-2019, *IEEE Standard for Floating-Point Arithmetic*. Primary
  standard for formats, operations, rounding, exceptions, and special values.
- David Goldberg, “What Every Computer Scientist Should Know About
  Floating-Point Arithmetic,” *ACM Computing Surveys* 23(1), 1991. Historical
  systems tutorial for representation error, exact rounding, exceptions,
  languages, and compilers.

## Vectors

- RISC-V International, ratified “V” Standard Extension, version 1.0:
  <https://docs.riscv.org/reference/isa/unpriv/v-st-ext>. Primary source for
  vector state, active/inactive/prestart/tail element classes, masks, restart,
  and agnostic versus undisturbed policies.

## Concurrency

- Leslie Lamport, “How to Make a Multiprocessor Computer That Correctly
  Executes Multiprocess Programs,” 1979. Primary definition of sequential
  consistency.
- Scott Owens, Susmit Sarkar, and Peter Sewell, *A Better x86 Memory Model:
  x86-TSO*, UCAM-CL-TR-745, 2009:
  <https://www.cl.cam.ac.uk/techreports/UCAM-CL-TR-745.pdf>. Formal operational
  and axiomatic treatment with litmus validation.

## Virtual memory

- Peter J. Denning, “The Working Set Model for Program Behavior,”
  *Communications of the ACM* 11(5), 1968. Primary source connecting locality,
  memory demand, allocation, and thrashing.
- Current RISC-V privileged and Intel system-programming manuals already pinned
  in the shared bibliography for translation and privileged-state boundaries.

## Mutable code and leakage

- RISC-V International, “Zifencei” Extension, version 2.0:
  <https://docs.riscv.org/reference/isa/unpriv/zifencei.html>. Primary source
  for local instruction/data synchronization and its multiprocessor limit.
- Paul Kocher et al., “Spectre Attacks: Exploiting Speculative Execution,”
  2019. Primary security paper establishing a difference between rolled-back
  architectural effects and retained microarchitectural observations.

## Verified compilation

- Xavier Leroy, “Formal Verification of a Realistic Compiler,” 2009.
- Official CompCert manual, “CompCert C: a trustworthy compiler”:
  <https://compcert.org/man/manual001.html>. Used to check the semantic
  preservation statement and its actual endpoints: elaborated CompCert C AST
  to assembly AST before assembling and linking.

## Deliberate omissions

- No current product-performance quantities are quoted. Such figures depend on
  machine, workload, version, and measurement controls.
- No complete formal memory model, virtual-memory model, speculative machine,
  or compiler is reproduced. The chapter teaches extension obligations and
  small derivations, not a survey masquerading as implementation.
- Axeyum implementation claims remain limited to the live checkout boundary
  already recorded for Chapter 15.
