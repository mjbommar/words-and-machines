# Chapter 1 research contract

**Scope:** Fixed-width patterns, their mathematical carrier, and the readings
and operations that give them meaning
**Target capacity:** 9,000--12,000 words, governed by the obligations below
**Compelling question:** How can one finite pattern support several meanings
without allowing those meanings to blur into one another?

## Close-up subjects

1. One eight-bit pattern read as an unsigned integer, signed integer, mask,
   field collection, byte, and instruction fragment.
2. The width-four residue circle as a complete proof miniature.
3. Two's-complement negation, range, extension, and overflow boundaries.
4. Split and join as the bridge from words to byte-addressed memory.

## Three lenses

| Lens | Depth | Required content |
|---|---|---|
| Origins | Medium | positional arithmetic; Leibniz's binary arithmetic; Gauss's congruence notation; Boole's algebra of logical classes; Shannon's use of symbolic logic for relay and switching networks; historical alternatives to two's complement without a false single-inventor story |
| Foundations | Deep | finite sets; residues and equivalence classes; positional expansion and uniqueness; Boolean algebra; bit extraction; signed and unsigned interpretation maps; information loss under truncation; split/join bijection; proof by cases and algebra |
| Industry and economics | Medium | why exact widths survive in ISAs and language standards; storage, bandwidth, vector-lane, and compatibility costs; narrow values in 64-bit registers; shift-count and upper-bit rules as compiler obligations; modular, checked, and saturating arithmetic as different contracts |

## Coverage routing

| Neighboring topic | Route |
|---|---|
| Physical realization of a bit | Explain Shannon's abstraction bridge; derive thresholds and storage in Chapter 2 |
| Complete arithmetic circuits | Use Boolean truth tables here; route gates, adders, timing, and datapaths to Chapters 3, 8, and 16 |
| Floating-point representation | Exclude from the teaching core; identify it as a separate representation contract in Chapter 16 |
| Character and text encodings | Use only as a reminder that patterns admit nonnumeric readings; exclude a Unicode survey |
| Language-level integer rules | Compare selected contracts here; keep compiler correctness for Chapters 12 and 16 |
| Memory layout | Define bytes and split/join here; derive addressed loads and stores in Chapter 4 |
| Real instruction details | Ask exact width questions here; answer source-pinned RV64 and x86-64 forms in Parts II and III |

## Questions the chapter must answer

1. Why is a numeral not yet a fixed-width word?
2. Why do residues modulo \(2^w\) model stored arithmetic?
3. Why are modular operations independent of the chosen integer representative?
4. Which facts belong to a bit pattern, and which belong to an interpretation?
5. Why does two's complement share an adder with unsigned arithmetic?
6. What do shifts, rotates, masks, extraction, extension, and truncation preserve?
7. Why do overflow, carry, saturation, and wraparound name different contracts?
8. How does a word become an ordered sequence of bytes and return unchanged?
9. Which present engineering decisions depend on width and representation?

## Feature inventory

- [x] Interpretation map and width-four residue circle.
- [x] Residue-class derivation with well-defined operation proofs.
- [x] Boolean truth tables and a Shannon relay/switching bridge.
- [x] Full two's-complement derivation, negation law, asymmetry, and historical alternatives.
- [x] Shift, rotate, mask, insertion, and extraction laws with boundary rules.
- [x] Modular versus checked versus saturating arithmetic comparison.
- [x] A quantitative storage/register/vector-width example.
- [x] Extension, truncation, and split/join reader proofs.
- [x] Paired source-pinned RV64 and x86-64 width-rule windows.
- [x] Exercises at execute, explain, break, prove, design, economics, audit,
      and transfer levels.

## Research gaps

- [x] Use a primary-source contrast without assigning two's complement to one
      unsupported inventor. The UNIVAC 1108 programmer's reference specifies
      36-bit ones'-complement signed numbers and separate +0/-0 patterns; the
      chapter uses it only to establish that signed representation was a live
      architectural choice.
- [x] Pin a current software contract that exposes the alternatives directly.
      Rust 1.97.1 documents named `wrapping_add`, `checked_add`,
      `overflowing_add`, `strict_add`, and `saturating_add` families on
      fixed-width integers; the chapter uses these as interface examples, not
      as definitions of the underlying mathematics.
- [x] Select exact forms from the pinned manuals: RV64I `SRAI` and `ADDIW`;
      x86-64 `SAR r64, CL` and `MOV r32, r/m32`.
- [x] Inspect Axeyum bit-vector APIs and distinguish reusable substrate from
      the missing A0 word package. Current substrate includes typed
      `Bv<W>`, arbitrary-width IR values, arithmetic and structural builders,
      evaluation, AIG lowering, property solving, evidence reports, and model
      replay. It does not supply the book's A0 word/readings/byte package or
      its named proof-and-control bundle.

## Chapter audit

- **Draft reviewed:** 2026-08-30
- **Length:** approximately 9,360 source words, within the 9,000--12,000
  capacity band.
- **Rendered review:** 25 pages at the 7-by-10 draft trim. The residue circle,
  interpretation map, proof panels, width-change diagram, comparison tables,
  and graded exercises are legible. No Chapter 1 overfull box remains in the
  build log.
- **Claim discipline:** the historical path uses primary works by Leibniz,
  Gauss, Boole, and Shannon plus a period UNIVAC manual; current instruction
  and language claims point to dated official specifications.
- **Deferred by design:** physical storage belongs to Chapter 2; addressed
  loads and stores to Chapter 4; complete arithmetic condition behavior to
  Chapter 8; floating point to the model boundary in Chapter 16.
- **Status:** breadth-and-depth pass complete for this chapter, subject to the
  final cross-book consistency, bibliography, evidence, and production audits.

## Cross-chapter connections

**Back:** The Introduction's interpretation stack and claim/evidence boundary.
**Forward:** Chapter 2 places words in registers, memory, condition state, and
outcomes.
**Through-lines:** pattern versus meaning; finite rules with exact boundaries;
one mathematical carrier supporting several industrial contracts; proof
miniatures that expose the reason before machine evidence covers scale.
