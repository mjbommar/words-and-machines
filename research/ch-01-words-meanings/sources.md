# Chapter 1 sources

Research checked on 2026-08-30. Search results are leads only. Manuscript
claims must use opened primary, standards, or official architecture sources.

## Origins and foundations

- Gottfried Wilhelm Leibniz, "Explication de l'Arithmetique Binaire" (1703),
  for the demonstrated use of 0 and 1 in positional arithmetic. Do not claim
  invention of every binary-like notation.
- Carl Friedrich Gauss, *Disquisitiones Arithmeticae* (1801), sections 1--3,
  for the language and notation of congruence.
- George Boole, *An Investigation of the Laws of Thought* (1854), for an
  algebraic treatment of logical classes. Do not project modern bit-vector
  terminology backward into the book.
- Claude E. Shannon, "A Symbolic Analysis of Relay and Switching Circuits,"
  *Transactions of the AIEE* 57(12), 713--723 (1938), DOI
  10.1109/T-AIEE.1938.5057767. Shannon maps symbolic logic to relay and
  switching networks and studies equivalent and least-contact circuits.
- Sperry Rand, *UNIVAC 1108 Multi-Processor System: Processor and Storage,
  Programmer's Reference*, UP-4053 Revision 1 (copyright 1966, 1970), sections
  4.2.1--4.2.2. The manual specifies ones'-complement signed numbers and
  distinct all-zero +0 and all-one -0 patterns. It supports historical
  plurality, not a claim about a single inventor or inevitable transition.

## Current authoritative sources

- RISC-V International, *The RISC-V Instruction Set Manual, Volume I*, pinned
  project revision 20260120. RV64I `*W` operations ignore the upper 32 input
  bits, compute a 32-bit result, and sign-extend it; RV64 shift immediates use
  a six-bit shift amount.
- Intel, *Intel 64 and IA-32 Architectures Software Developer's Manual*,
  version 092 (August 2026), volumes 1 and 2. Use the exact instruction page
  for shift-count masking, rotate behavior, flags, and subregister writes.
- ISO/IEC JTC1/SC22/WG14 working drafts hosted at open-std.org, for the C rule
  that unsigned arithmetic is modulo \(2^N\). Pin one draft before manuscript
  use; do not transfer that rule to signed overflow.
- Oracle, *Java Language Specification*, section 15.19, for a contrasting
  language contract that fixes two's-complement shifts and masks the shift
  distance. Pin the edition if retained in prose.
- Rust Project, primitive `u8` documentation, standard library 1.97.1
  (2026-07-14), for the current named wrapping, checked, overflowing, strict,
  and saturating operation families. The chapter cites the API distinction,
  not build-profile defaults.

## Coverage comparators

Standard computer-organization texts normally cover data representation,
integer arithmetic, logic, and shifts, but often distribute formal residue
proofs, language contracts, and current ISA consequences across separate
chapters. This chapter should connect them while routing circuits, memory,
and full instruction semantics forward.

## Source cautions

- The dominance of two's complement was gradual. Early machines used several
  signed representations. Do not write an inventor or inevitability story
  without stronger primary evidence.
- A language rule, ISA rule, and mathematical operation are three different
  contracts even when one example produces the same bits.
- Current manuals can change. Cite the pinned revision and exact form, not a
  generic architecture label.

## Axeyum substrate audit

Inspected the sibling checkout on 2026-08-30:

- `crates/axeyum-property` exposes typed `Bv<W>` property construction,
  checked evidence reports, and deterministic counterexample rendering.
- `crates/axeyum-ir` and its Python binding support fixed and arbitrary-width
  bit-vector values, arithmetic, extraction, concatenation, zero/sign
  extension, rotation, evaluation, and width errors.
- `crates/axeyum-bv` lowers the admitted Boolean/bit-vector surface to AIG
  wires with maps for lifting assignments back to source terms.
- Property tests compare extraction, concatenation, extension, and rotation
  against integer reference functions across generated widths and values.

These are reusable expression, solving, and evidence layers. No inspected
package defines the book's A0 word carrier together with its unsigned/signed
readings, byte split/join API, named controls, and chapter artifact contract.
The manuscript must keep that package labeled as required work.
