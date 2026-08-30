# Chapter 6 research contract

**Scope:** Instruction representation, staged decoding, legality, length,
canonicality, and the boundary from stored bytes to structured operations
**Target capacity:** 10,000--14,000 words, governed by the obligations below
**Compelling question:** How can a finite pattern of bits name one machine
action without ambiguity, and what must a decoder prove before execution may
begin?

## Close-up subjects

1. One complete A0 encode/decode derivation with a rejected near miss.
2. One RV64I R-type word and one split immediate reconstructed bit by bit.
3. One x86-64 register form and one memory form whose length depends on the
   decoding path.
4. One decoder represented as a total function with named rejection results.
5. One proof of field pack/extract inversion and one canonicality proof.
6. One ambiguity or desynchronization failure showing why length is semantic.
7. One control matrix covering legal, reserved, truncated, feature-gated, and
   out-of-scope inputs.

## Three lenses

| Lens | Depth | Required content |
|---|---|---|
| Origins | Medium | pre-stored-program setup; early stored orders in finite words; Manchester and EDSAC without sole-inventor myths; symbolic assembly; System/360 compatibility and instruction formats; the growth of x86 prefixes; RISC regularity and later compression |
| Foundations | Deep | finite alphabets and counting; products, sums, and tagged variants; bit-field packing and extraction; endianness versus bit numbering; sign extension; prefix-free and uniquely decodable codes; partial parsing versus total classification; soundness, completeness, injectivity, normalization, and composition with execution |
| Industry and economics | Medium | instruction density; fetch bandwidth, cache capacity, decoder width, energy, and latency; backward compatibility; code-size tradeoffs; security disassembly and malformed-input risks; JITs, assemblers, emulators, binary translators, and independent differential testing |

## Coverage routing

| Neighboring topic | Route |
|---|---|
| Memory fetch, permissions, and byte order | Work here; Chapter 4 owns the memory model |
| Instruction effects and operands | Work here; Chapter 3 owns transition semantics |
| Program stepping and next-PC behavior | Work here; Chapter 5 owns traces and outcomes |
| Full RV64I and x86-64 instruction families | Route to Chapters 7--9 |
| Relocation, linking, and procedure ABIs | Route to Chapter 10 |
| Cross-ISA semantic relations | Route to Chapters 11--12 |
| Search over instruction words and canonical forms | Route to Chapter 13 |
| Evidence manifests and replay | Route to Chapter 14 |
| Micro-op caches, fusion, speculation, and side channels | Name the boundary here; route to Chapter 16 |

## Questions the chapter must answer

1. Why are assembly text, bytes, decoded instances, and effects distinct?
2. Which historical constraints shaped fixed and variable formats?
3. How many operations and operands can a finite field distinguish?
4. When do pack and extract form inverse functions?
5. Why must split immediates be assembled before sign extension?
6. Why are byte order, instruction-bit numbering, and printed diagrams separate conventions?
7. What makes a decoder total even though some inputs are illegal?
8. When is an instruction code prefix-free or only uniquely decodable from a chosen boundary?
9. Why is consumed length part of decoder soundness?
10. How do aliases and multiple legal encodings change round-trip theorems?
11. What distinguish soundness, completeness, legality, canonicality, and execution correctness?
12. Which present costs and security properties lie outside pure decode semantics?

## Feature inventory

- [x] Sourced history from manual setup and early stored orders through
      System/360, x86 compatibility, RISC regularity, and compressed forms.
- [x] Exact domains for bytes, words, modes, feature sets, addresses, decoded
      instances, consumed lengths, and named rejection reasons.
- [x] Counting argument for opcode and operand-field capacity.
- [x] Pack/extract proof with width, range, shift, mask, and non-overlap premises.
- [x] Endianness, bit numbering, sign extension, and split-immediate derivations.
- [x] Prefix-free, uniquely decodable, and boundary-relative distinctions.
- [x] A0 canonical encoder/decoder with forward and accepted-byte converse proofs.
- [x] Source-pinned RV64I and x86-64 examples with exact legality and length.
- [x] Soundness, completeness, length, rejection, normalization, and composed-step contracts.
- [x] Partitioned control matrix, mutations, differential decoding, and source adjudication.
- [x] Current density, frontend, compatibility, tooling, and security stakes.
- [x] Honest Axeyum substrate audit and implementation obligation.
- [x] At least 30 exercises across derivation, proof, break, design, audit,
      history, security, economics, and transfer levels.

## Chapter audit

Breadth-and-depth revision complete, subject to the final whole-book audit.
The chapter has 10,129 source words and 42 exercises. It renders across printed
pages 133--160 (28 pages), with Chapter 7 beginning on page 162 after the
required recto break. The source ledger and chronology record the historical,
specification, textbook-comparison, current-practice, and live Axeyum sources
used or deliberately routed.

The full PDF build and print preflight pass. Chapter 6 has no Simplified Book
English findings and no chapter-local overfull boxes. Contact-sheet review and
close inspection of the opening, field algebra, RV64 transfer, current-cost
discussion, and both final exercise pages found no clipping, collision,
stranded heading, malformed formula, or missing exercise. All 42 exercise
items render before the Chapter 7 boundary.

## Cross-chapter connections

**Back:** Chapters 1--5 supply finite words, complete state, instruction
effects, memory bytes, fetch, and traces.
**Forward:** Chapters 7--9 use the decoder boundary for sustained RV64 and
x86-64 semantics; Chapters 11--14 relate and check decoded programs.
**Through-lines:** finite patterns acquire meaning only under a declared
interpretation; compatibility is both a promise and a cost; exact local maps
support global execution claims only when their composition is proved.
