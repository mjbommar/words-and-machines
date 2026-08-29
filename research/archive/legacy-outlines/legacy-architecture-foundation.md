# Superseded architecture-foundation notes

This file is migration history. See `MASTER.md` and `AXEYUM-EVIDENCE.md`.

This plan prevents the available evidence from narrowing the subject of the
book. The ledger presently has substantial AVX2 and RISC-V objects. Those
objects are case studies, not the foundation or boundary of instruction-set
semantics.

## Governing distinction

The book first defines the common objects on which any later ISA claim depends.
It then compares named machines by exact semantic features. The labels *RISC*
and *CISC* may orient the reader, but they never determine a theorem's scope.

AVX2 is a vector extension within x86-64. It supplies an unusually clean
permutation problem and a real certificate. It does not represent x86-64 as a
whole, and x86-64 does not define every design commonly called CISC.

## Part I: the common machine

Part I must establish these objects before a named ISA carries an argument:

1. **Words and interpretations.** Fixed width, modular arithmetic, bits,
   signed and unsigned readings, and total operations.
2. **Machine state.** Registers, memory, a program counter where needed,
   condition state, and named exceptional outcomes.
3. **Instruction semantics.** An instruction as a state transformation, with
   explicit read and write sets and a declared treatment of traps or undefined
   behavior.
4. **Operand forms.** Register, immediate, memory, implicit, and multi-result
   operands. Syntax and encoding are kept separate from meaning.
5. **Programs.** Straight-line composition first. Control flow enters only
   with its additional state and proof obligations made explicit.
6. **Equivalence and cost.** Observed state, allowed contexts, program
   language, and cost model are part of the proposition.

Each construction needs a tiny artificial machine on which the reader can
enumerate all states and instructions by hand. This machine is pedagogical,
not a claim that real ISAs are simple.

## Comparative dimensions

Later chapters compare machines along dimensions that are often bundled into
RISC and CISC:

| Dimension | More regular case | More implicit or combined case | Proof effect |
|---|---|---|---|
| Operand location | register-register operations | memory operand or read-modify-write | changes the candidate language and state read |
| Memory access | separate load and store | arithmetic instruction reads or writes memory | adds memory and fault behavior to equivalence |
| Operands | fields name every input | accumulator, flags, stack, or fixed registers | adds hidden reads and writes |
| Encoding | fixed or few instruction widths | variable-length encodings and prefixes | separates byte length from instruction count |
| Condition state | explicit comparison result | implicit flags | changes observable and preserved state |
| Results | one named destination | flags, paired registers, or several results | changes the codomain of the instruction function |
| Extension model | named modular extensions | overlapping legacy and extension spaces | changes which language a lower bound quantifies over |

These are tendencies, not definitions of two pure camps. A theorem names the
actual features and instructions it covers.

## Concrete case studies

- **RISC-V:** explicit integer registers, load-store structure, fixed base
  encodings with compressed and named extensions, and instruction-set design
  tables recovered by this repository.
- **x86-64:** variable encodings, memory operands, implicit condition flags,
  partial-register concerns, and instruction families with several operand
  forms.
- **AVX2:** a deliberately restricted x86-64 vector sublanguage for byte
  reversal, SSA operand availability, and a named Haswell cost profile.
- **A small stack or bytecode machine:** a useful transfer exercise because it
  replaces named registers with implicit stack operands. WebAssembly is a
  possible concrete case when the evidence is ready.

The case-study order should follow the proof need, not a historical march from
RISC to CISC or vice versa.

## Acceptance test for the eventual Part I

Before Part I is complete, a reader should be able to:

- define a small machine without borrowing the syntax of RISC-V or x86-64;
- state the full read and write effect of an instruction;
- explain why a memory operand, implicit flag, or variable encoding changes a
  minimality claim;
- translate one RISC-V and one x86-64 instruction into the common state model;
- identify which parts of an AVX2 result belong to general semantics and which
  belong only to its declared sublanguage.
