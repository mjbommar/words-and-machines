# Chapter 6 sources

Research ledger opened 2026-08-30. Search results are leads only. Manuscript
claims must rest on opened primary papers, standards, official manuals,
curricula, or other authoritative sources.

## Opened origins and foundations

- Computer History Museum, “The Stored Program,” for the distinction between
  laborious setup and stored instructions, the 1948 Manchester Baby run, and
  the warning that the stored-program idea has no secure sole inventor.
- Computer History Museum EDSAC records, for the 1949 practical stored-program
  machine, initial orders, paper tape, and reusable subroutine library.
- Wilkes, Wheeler, and Gill, *The Preparation of Programs for an Electronic
  Digital Computer* (1951), identified as the primary route for any later
  detailed claim about EDSAC order coding or symbolic programming. The present
  chapter makes only the narrower machine, loading, and library claims supported
  by the opened museum records.
- Amdahl, Blaauw, and Brooks, “Architecture of the IBM System/360” (1964),
  DOI `10.1147/rd.82.0087`, for the compatible-family architecture and its
  range of implementations.
- Original *IBM System/360 Principles of Operation*, A22-6821-0 (1964), for
  the published format families and program-visible interface.

## Opened current authoritative sources

- RISC-V ratified unprivileged architecture, version 20260120, for the base
  instruction-length convention, major opcodes, field layouts, immediates,
  reserved encodings, and extension-dependent legality.
- Intel 64 and IA-32 Software Developer's Manual, current version 092, for
  instruction format, prefixes, opcode maps, ModR/M, SIB, displacement,
  immediate, maximum length, and selected ADD forms.
- Intel 64 and IA-32 Optimization Reference Manual, for frontend length
  determination, decoder behavior, length-changing prefixes, and the boundary
  between architectural decode and implementation cost.
- Intel XED documentation, for a mature independent encode/decode tool and
  explicit mode, chip, operand, length, and error interfaces.
- IBM current z/Architecture Principles of Operation and assembler
  documentation, for 2-, 4-, and 6-byte format families and enduring
  compatibility examples.

## Coverage comparators

- Patterson and Hennessy, *Computer Organization and Design*, as the
  architecture-text comparator for instruction fields, stored programs,
  RISC formats, immediates, and datapath control. This chapter adds explicit
  decoder theorem shapes, rejection taxonomy, canonicality, and evidence
  controls.
- Bryant and O'Hallaron, *Computer Systems: A Programmer's Perspective*, as
  the systems-text comparator for machine bytes, disassembly, x86 instruction
  forms, linking, relocation, and executable code. This chapter adds a formal
  decode/execute boundary and sustained RV64/x86/A0 transfer proofs.
- Current Intel and RISC-V manuals as specification comparators for exact
  field positions, lengths, modes, feature gates, and legality. The chapter
  deliberately selects a finite teaching slice rather than paraphrasing the
  full instruction catalogs.
- Digital-design texts derive masks, shifts, concatenation, sign extension,
  decoders, and combinational selection from Boolean circuits.
- Information-theory texts distinguish prefix-free and uniquely decodable
  codes; machine instruction streams add modes, boundaries, and legality.
- Compiler and systems texts distinguish source syntax, assembly, object code,
  relocation, loading, disassembly, emulation, and execution.
- Security texts treat instruction-boundary disagreement, malformed binaries,
  gadget discovery, and decoder differential bugs as attack-relevant surfaces.

## Source cautions

- Do not call Turing's abstract machine table a stored-program ISA.
- Do not assign stored-program invention to one person or report a design
  document as a completed machine.
- A fixed base format does not imply that every extension has that length.
- A legal no-visible-effect encoding, a hint, a reserved encoding, and an
  illegal encoding are different specification categories.
- An instruction diagram's left-to-right bit numbering need not match memory
  address order or another manual's drawing convention.
- Decoder agreement is defect evidence, not an authority above the pinned
  specification.
- Decoder correctness does not prove execution semantics, fetchability,
  timing, frontend energy, or side-channel behavior.

## Axeyum substrate audit

The live sibling checkout was inspected on 2026-08-30 at revision
`a9991fdad6c1e4b2bda596b46d2c8c715556ceae`, on branch
`research/open-problems-2026-08`. It had an unrelated untracked research
directory; no sibling files were changed.

- `crates/axeyum-bv/src/lib.rs` implements bit-vector extraction,
  concatenation, zero and sign extension, bit-level lowering, and tests for
  LSB-first concatenation and narrow extraction behavior.
- Solver, SAT/DRAT, replay, and kernel-reconstruction routes can support finite
  field identities and counterexample searches after a book-owned encoding is
  supplied.
- No reusable A0 decoder, RV64 decoder and semantics, or x86-64 decoder and
  semantics was found. The bit-vector substrate is not itself evidence for an
  architectural decoder claim.
- A chapter artifact still needs a declared decoded-instruction type, total A0
  result taxonomy, encoder, exhaustive or solver-backed round trips, replay,
  source binding, and negative controls.
