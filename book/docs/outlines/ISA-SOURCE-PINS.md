# ISA source pins

This file records the architectural sources used for load-bearing claims in
Parts II and III. A current vendor page is useful for discovery, but a chapter
claim must name a document version or a stable snapshot as well.

Verified: 2026-08-29.

## RISC-V

- Normative family: *The RISC-V Instruction Set Manual, Volume I:
  Unprivileged Architecture*.
- Current ratified release named by RISC-V International: version 20260120.
- Stable HTML library used for section-level links:
  `https://docs.riscv.org/reference/isa/unpriv/`.
- Exact archived PDF usable for page-stable checks when the newer rolling PDF
  lacks a permanent version URL: version 20240411,
  `https://docs.riscv.org/reference/isa/v20240411/_attachments/riscv-unprivileged.pdf`.
- Scope used by this book: RV64I base integer ISA, version 2.1, plus only the
  extensions a chapter names explicitly.

The GitHub release feed contains frequently generated draft builds. Do not
silently treat its newest build as the ratified architecture. If a later
ratified release changes a load-bearing rule, update the bibliography, this
pin, the affected chapter, and its tests together.

## x86-64

- Normative family: *Intel 64 and IA-32 Architectures Software Developer's
  Manual*.
- Version: 092, published by Intel and verified on 2026-08-29.
- Instruction reference: combined Volumes 2A--2D, document
  `325383-092`, exact download target
  `https://cdrdv2-public.intel.com/922478/325383-092-sdm-vol-2abcd.pdf`.
- Discovery and update page:
  `https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html`.
- Scope used by this book: 64-bit mode and the exact instruction forms named
  in each example. Legacy, VEX, EVEX, APX, privileged, and system forms are
  outside a claim unless named explicitly.

Intel may replace discovery links when it publishes a new revision. Keep the
document number and revision in citations and evidence manifests. Do not use
an assembler or disassembler as the sole architectural source.

## Axeyum boundary at this pin

The initial source audit used sibling revision
`a9991fdad6c1e4b2bda596b46d2c8c715556ceae`. The executable-curriculum work now
pins RV64 evidence to revision
`b6f3a543b3cd2b418501927d615190b6821a241e` and x86-64 evidence to
`1cb53b9a940a4cc685b910441cb16b0dbb03fae5`.

The current route contains reusable A0 state and step semantics plus
source-pinned RV64I and x86-64 decoders and executors. Four active manifests
pin the two official sources and replay the selected forms, printed programs,
traps, projections, and mutations. The typed cross-ISA refinement route remains
unimplemented. Chapters must keep that relational interface as a construction
plan or obligation.

## Procedure ABI slices

Chapter 10 uses ABI rules in addition to instruction-set rules. The two layers
have separate source pins.

- RISC-V: *RISC-V ABIs Specification*, version 1.0, from the RISC-V Ratified
  Specifications Library. Stable PDF:
  `https://docs.riscv.org/reference/abi/_attachments/riscv-abi.pdf`.
- RISC-V scope: the ordinary RV64 integer calling convention, including the
  integer register convention, downward-growing stack, and 128-bit stack
  alignment rule. Floating-point, vector, aggregate, variadic, system-call,
  and platform-specific rules are outside the chapter's worked example.
- x86-64: *System V Application Binary Interface: AMD64 Architecture Processor
  Supplement*, version 1.0, dated 2023-09-26. Exact project PDF:
  `https://gitlab.com/x86-psABIs/x86-64-ABI/-/wikis/uploads/221b09355dd540efcbe61b783b6c0ece/x86-64-psABI-2023-09-26.pdf`.
- x86-64 scope: the LP64 ordinary integer calling sequence, selected
  general-purpose register convention, and stack alignment at ordinary
  calls. Microsoft x64, ILP32, floating-point and vector classes, aggregates,
  variadic calls, system calls, dynamic linking, and unwinding are excluded.

Both sources were opened and checked on 2026-08-29. A later chapter must not
infer an ABI rule from the ISA manual or silently combine two platform ABIs.
