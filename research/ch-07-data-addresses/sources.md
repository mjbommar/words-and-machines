# Chapter 7 sources

Research ledger opened 2026-08-30. Search results are leads only. Manuscript
claims must rest on opened primary papers, standards, official manuals,
curricula, or other authoritative sources.

## Opened origins and foundations

- EDVAC, Manchester, EDSAC, and early machine manuals already pinned in the
  bibliography for stored words and addressed operations.
- University of Manchester's Mark I history records that the 1949 machine had
  B-lines for modifying addresses. The manuscript uses this as a documented
  milestone, not as an unqualified claim that it invented every later index
  register.
- IBM System/360 architecture paper and original Principles of Operation for
  base, index, displacement, format, and compatibility context.

## Opened current authoritative sources

- RISC-V ratified unprivileged architecture, version 20260120, for RV64I load
  and store effective addresses, access widths, signed and unsigned loads,
  low-bit stores, x0 behavior, and execution-environment-dependent misalignment.
- Intel 64 and IA-32 Software Developer's Manual, version 092, for register
  widths, 32-bit zeroing writes, high-byte restrictions, ModR/M and SIB forms,
  displacement rules, address-size behavior, and RIP-relative addressing.
- LLVM alias-analysis source and documentation for NoAlias, MayAlias,
  PartialAlias, memory dependence, and optimization clients. Prefer current
  source/API material over the older narrative page when wording current behavior.
- Mark Horowitz's 2014 ISSCC plenary paper for the dated energy comparison that
  motivates reducing data movement. The chapter does not present its process-
  specific quantities as timeless constants.
- Current Intel optimization material for address-generation and load/store
  implementation examples; keep claims processor-specific.

## Coverage comparators

- Patterson and Hennessy, *Computer Organization and Design*, for load/store
  datapaths, effective addresses, alignment, caches, and performance.
- Bryant and O'Hallaron, *Computer Systems: A Programmer's Perspective*, for
  x86 addressing, data movement, arrays, pointers, memory hierarchy, and
  machine-code interpretation.
- Semantics and verification texts for state projections, frame conditions,
  commuting updates, aliasing, and memory models.
- Intel and RISC-V specifications for exact architecture behavior. The chapter
  selects forms needed by later proofs rather than reproducing instruction catalogs.

## Source cautions

- “Move” usually copies a value; it need not erase the source.
- Equal values do not imply equal locations, and different address expressions
  do not imply disjoint locations.
- Effective-address calculation does not establish translation, permission,
  alignment, range, device behavior, or successful completion.
- RISC-V misaligned load/store behavior depends on the execution environment;
  do not invent one universal RV64I outcome.
- Architectural loads and stores do not expose cache hits, physical transfers,
  speculation, or timing without an extended model.
- A compiler's NoAlias result and the ISA's byte-range disjointness live at
  different abstraction levels and require a proved bridge.

## Axeyum substrate audit

Inspected sibling repository `../axeyum` at revision
`a9991fdad6c1e4b2bda596b46d2c8c715556ceae` on branch
`research/open-problems-2026-08`. The live substrate includes array reasoning,
symbolic memory, memory-aware bounded model checking, and the toy bit-vector
virtual machine's word-addressed symbolic load and store operations. It does
not yet contain the book's A0, RV64I, or x86-64 architectural package. It also
lacks the A0 adapter that fixes byte-addressed ranges, byte order, traps, and a
complete architectural state. The chapter therefore distinguishes reusable
solver substrate from the still-required book-facing proof artifact. No Axeyum
files were changed during this audit.
