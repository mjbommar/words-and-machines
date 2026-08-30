# Chapter 3 sources

Research checked on 2026-08-30. Search results are leads only. Manuscript
claims must use opened primary, standards, or official tool documentation.

## Origins and foundations

- John von Neumann, *First Draft of a Report on the EDVAC* (1945), sections
  14--15. The report says that control must receive and interpret orders and
  calls for their mathematical, logical, and operational meaning to be
  defined. It groups orders by work and source/disposal roles. Use this as an
  early stored-program design, not a sole-inventor claim.
- IBM, *System/360 Principles of Operation*, form A22-6821-0 (1964). The
  manual gives five basic formats: RR, RX, RS, SI, and SS. Their fields name
  register, storage-address, immediate, and length operands. Instruction
  length varies with the number of storage-address specifications. This is a
  primary example of systematic operand formats in a compatible family.
- Gene Amdahl, Gerrit Blaauw, and Frederick Brooks, "Architecture of the IBM
  System/360" (1964), for the programmer-visible architecture shared by
  different implementations.
- Maurice Wilkes and John Stringer, "Micro-programming and the Design of the
  Control Circuits in an Electronic Digital Computer" (1953), for control by
  a stored sequence of elementary control operations. Use it to separate an
  architectural instruction rule from one implementation technique, not to
  imply that every current instruction is implemented by microcode.

## Current authoritative sources

- RISC-V International, *The RISC-V Instruction Set Manual, Volume I*,
  revision 20260120. The base formats keep `rs1`, `rs2`, and `rd` in stable
  field positions. Integer `ADD` reads `rs1` and `rs2`, writes the low XLEN
  bits to `rd`, and does not expose x86-style arithmetic condition flags.
- Intel, *Intel 64 and IA-32 Architectures Software Developer's Manual*,
  version 092 (August 2026), Volume 2. `ADD` has register, memory, and immediate
  forms; its destination is also a source; it writes documented arithmetic
  status flags. Scope claims to the named form and mode.
- LLVM, *TableGen Overview* and *TableGen Programmer's Reference*. Target
  instruction records can include input and output operands, assembly syntax,
  selection patterns, encodings, implicit definitions, predicates, memory
  behavior, and scheduling facts. The official x86 example marks `EFLAGS` as
  an implicit definition. Do not treat LLVM's record as the ISA authority.
- GNU Compiler Collection, *GCC Internals: Machine Descriptions*. A target's
  machine-description file contains patterns for supported instructions,
  operand constraints, RTL effects, and assembly output. This establishes a
  current maintenance consumer, not a numerical cost claim.

## Coverage comparators

- Arvind and Shen, *Computer Architecture: A Constructive Approach*, connects
  instruction semantics to executable processor construction.
- Harris and Harris, *Digital Design and Computer Architecture*, develops
  instruction formats, operands, datapaths, and control together.
- Hennessy and Patterson, *Computer Architecture: A Quantitative Approach*,
  develops instruction-level parallelism through data and control
  dependencies and requires quantitative claims to name a resource and unit.
- Bryant and O'Hallaron, *Computer Systems: A Programmer's Perspective*, uses
  concrete instruction sequences, operands, registers, condition state, and
  memory to connect assembly behavior to compiled programs.

## Source cautions

- An instruction's architecture-level atomic transition does not assert that
  its circuit performs one indivisible physical action.
- A compiler target description is one engineering representation and may be
  incomplete for emulation or formal proof. It does not replace the official
  architecture manual.
- Static read/write sets may conservatively exceed the addresses actually
  touched in one state. State which kind is used.
- The cost of an instruction-set extension can be counted in affected
  descriptions, generators, tests, proof cases, silicon resources, or support
  years. Do not manufacture a universal dollar or cycle figure.

## Axeyum substrate audit

The 2026-08-30 search of the sibling checkout found reusable bit-vector terms,
solver transition-system traits, bounded and unbounded verification routes,
and typed LLVM scalar-instruction parsing. It did not find a book-specific A0
instruction type, operand resolver, decoder, complete state step, or public
Python replay route. Those generic layers are foundations, not evidence that
`OP.a0.step` has been discharged.
