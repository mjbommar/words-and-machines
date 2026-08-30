# Chapter 8 sources

Research ledger opened 2026-08-30. Search results are leads only. Manuscript
claims must rest on opened primary papers, standards, official manuals, or
other authoritative sources.

## Opened origins and foundations

- Leibniz's 1703 explanation of binary arithmetic for the early printed
  arithmetic lineage. Do not turn a published explanation into a claim that
  one person invented every binary representation or practice.
- George Boole's 1854 *Laws of Thought* and Shannon's 1938 relay-and-switching
  paper for the algebra-to-circuit lineage. Arithmetic gates are an engineering
  construction from Boolean relations, not evidence that logic and arithmetic
  are the same interpretation.
- IBM System/360 architecture paper and original *Principles of Operation* for
  a documented architectural condition code and arithmetic instruction rules.
- Andrew D. Booth's 1951 paper, “A Signed Binary Multiplication Technique,”
  for a uniform complementary-number method motivated by equipment cost.
- Kogge and Stone's 1973 parallel recurrence paper as one origin of a widely
  used parallel-prefix carry structure. Do not claim that all fast adders use
  one network or that the paper prescribed a modern processor implementation.
- Gauss's 1801 treatment of congruence for the mathematical language behind
  fixed-width modular identities.

## Opened current authoritative sources

- RISC-V ratified unprivileged architecture, version 20260120, for RV64I ADD,
  SUB, shifts, SLT/SLTU, direct branches, and the M-extension multiplication
  and division boundary where used. The opened M-extension page pins its
  all-ones quotient and dividend remainder for division by zero, and its
  least-signed divided by negative-one result.
- Intel 64 and IA-32 Software Developer's Manual, version 092, for exact ADD,
  ADC, SUB, SBB, CMP, shifts, rotates, multiplication, division, condition
  flags, and form-specific defined or undefined state.
- LLVM Language Reference and Undefined Behavior Manual, checked 2026-08-30,
  for modular integer results, `nuw`/`nsw` poison, propagation, and `freeze`.
- Rust 1.97.1 integer documentation for current checked, wrapping,
  overflowing, strict, and saturating method families. Treat the version and
  API surface as dated.
- MITRE CWE-190, version 4.20, for current security consequences and mitigation
  categories associated with unexpected integer overflow or wraparound.
- Horowitz's 2014 ISSCC plenary paper for dated operation-energy comparisons.
  Use the paper to motivate physical cost differences, not as a timeless
  table for every process or processor.

## Coverage comparators

- Patterson and Hennessy, *Computer Organization and Design*, for arithmetic
  datapaths, ALU control, multiplication/division, and performance tradeoffs.
- Bryant and O'Hallaron, *Computer Systems: A Programmer's Perspective*, for
  integer arithmetic, condition codes, shifts, assembly, and language-level
  consequences.
- Computer-arithmetic texts by Koren and Parhami for wider algorithm and
  circuit coverage. The chapter teaches proof-bearing foundations rather than
  reproducing an arithmetic-hardware catalog.
- Intel and RISC-V manuals for architectural behavior; compiler and language
  documents for contracts above the ISA.

## Source cautions

- A circuit diagram does not define an ISA rule unless the architectural
  manual makes its output observable.
- “Overflow” is incomplete without a reading and policy: carry, signed
  overflow, language error, saturation, trap, or poison are different claims.
- x86 flags are instruction- and form-specific. Do not generalize one policy
  to every arithmetic, logic, shift, rotate, multiply, or divide form.
- Base RV64I has no x86-style arithmetic flag register. Optional extensions
  and compiler idioms must be named separately.
- LLVM poison is not an immediate hardware trap and is not merely an arbitrary
  architectural word.
- A faster carry network trades logic depth against wiring, fan-out, area,
  switching, and implementation constraints. “Faster” needs a cost model.
- Constant instruction count or branch-free source does not by itself prove
  constant time on a physical processor.

## Axeyum substrate audit

Inspected sibling repository `../axeyum` at revision
`a9991fdad6c1e4b2bda596b46d2c8c715556ceae` on branch
`research/open-problems-2026-08`. The Rust IR already provides fixed-width
addition, subtraction, multiplication, unsigned and signed comparisons,
shifts, rotations, extension, and explicit unsigned/signed overflow predicates
for addition, subtraction, and multiplication. The AIG lowering includes a
ripple-carry addition network. Python bindings expose these operations, and
property tests compare the overflow builders with independent unbounded Python
integer definitions across generated widths and boundary values. QF_BV solver
and proof-export routes are reusable.

The checkout does not yet provide the book's A0 `Z,N,C,V` arithmetic record,
instruction policies, four-quadrant census, condition-liveness lesson, negative-
control manifest, or thin RV64I/x86-64 adapters. Existing property tests are
strong substrate evidence; they are not the complete book-facing artifact or a
width-parametric kernel proof. No Axeyum files were changed during this audit.
