# Superseded evidence-led structure

This file is retained temporarily as migration history. It is not an active
outline. See `MASTER.md` for the governing curriculum.

This is the governing content plan for *Instruction Sets, Programs, and
Proofs*. It replaces the evidence-led six-chapter draft. The old draft began
with the results already present in the ledger and worked backward. This plan
begins with what a reader must understand and then asks which claims the
ledger and Axeyum can support.

## Book promise

By the end of the book, a reader should be able to take a short sequence from
x86-64 or RISC-V and do four things:

1. state its meaning as a transformation of an explicit machine state;
2. state when another sequence is equivalent to it;
3. state the language and cost model needed for an optimization claim; and
4. distinguish a tested example, exhaustive computation, solver verdict,
   independently checked certificate, and kernel theorem.

The reader should also understand why x86-64 and RISC-V differ without reducing
them to slogans about complex and reduced instruction sets.

## Governing teaching machine

The common definitions use a small artificial machine called **M0**. M0 is not
a miniature RISC-V or x86-64. It is the least structure needed to ask an exact
question:

- four registers of (w)-bit words;
- byte-addressed finite memory;
- a program counter;
- four condition bits: zero, negative, carry, and overflow;
- normal and trapped outcomes;
- register, immediate, and base-plus-offset operands;
- arithmetic, logic, load, store, compare, conditional branch, and halt.

Every new semantic idea is first shown on a width-four or width-eight M0
instance that can be followed by hand. The same idea is then realized once in
RV64I and once in x86-64. M0 supplies pedagogy; the named ISAs supply reality.

## Part I — The common machine

### Chapter 1. Words and Their Meanings

Construct fixed-width words, bit positions, modular arithmetic, signed and
unsigned readings, endianness as a relation between words and memory, and total
versus trapping operations.

- Reader proof: wraparound at width four.
- Machine proof: the three existing width-eight division conventions.
- Paired windows: an RV64 register and an x86-64 general-purpose register both
  hold 64 bits; instruction semantics determine their interpretation.
- Ledger: `W.def.word`, `W.thm.*`, `W.ctl.*`.

### Chapter 2. State

Build the state tuple explicitly. Separate values from names, architectural
state from microarchitectural state, and normal results from traps. Define an
observation as the part of state a claim requires two programs to agree on.

- Reader proof: changing an unobserved scratch register preserves a chosen
  observation but not full-state equality.
- Paired windows: RISC-V's integer registers and program counter; x86-64's
  general-purpose registers, instruction pointer, and flags.
- New ledger: `I.def.machine-state`, `I.def.observation`.

### Chapter 3. Instructions and Operands

Define an instruction instance as an opcode plus operand form, and its meaning
as a state transformation. Cover explicit, implicit, immediate, memory, and
multi-result operands. Treat traps and undefined or constrained behavior as
part of the semantic relation rather than prose outside it.

- Reader proof: two spellings with different hidden writes are not equal as
  full-state functions.
- Paired windows: RV64I `add rd, rs1, rs2` and x86-64 `add r64, r64`; explicit
  destination versus destination-as-source and implicit flag writes.
- New ledger: `I.def.instruction`, `I.def.operand-form`.

### Chapter 4. Memory

Define byte-addressed memory, loads, stores, endianness, alignment, aliasing,
and fault outcomes. Show why a register-only equality does not automatically
remain valid when an instruction may touch memory.

- Reader proof: little-endian reconstruction of a four-byte word.
- Paired windows: RV64I load/store separation; x86-64 arithmetic with a memory
  operand.
- New ledger: `I.def.memory`, `I.thm.little-endian-roundtrip` when evidence is
  implemented.

### Chapter 5. Programs and Control

Begin with straight-line composition. Add the program counter, conditional
branches, finite traces, termination, and observational equivalence. Keep
whole-program behavior distinct from straight-line superoptimization.

- Reader proof: composition preserves equivalence under a common context.
- Paired windows: RISC-V compare-and-branch versus x86-64 compare, flags, and
  conditional branch.
- New ledger: `I.def.program`, `I.thm.context-congruence`.

## Part II — Two instruction sets

### Chapter 6. Encoding and Decoding

Separate instruction bytes, decoded instruction instances, and semantics.
Explain fixed 32-bit RV64I base encodings, the compressed extension as a
declared addition, and variable-length x86-64 encodings with prefixes. Show
why byte length and instruction count are different costs.

- Reader exercise: decode a constrained instance from each ISA.
- Evidence plan: independent decoder agreement and mutation controls; no
  decoder claim enters the ledger until exact source versions are pinned.
- New ledger: `M.def.riscv-slice`, `M.def.x86-slice`,
  `M.prin.encoding-is-not-semantics`.

### Chapter 7. Moving Data

Compare register moves, immediates, address formation, loads, stores, extension
and truncation. Cover RISC-V's zero register and x86-64 partial-register writes
as different forms of special state behavior.

- Paired proof: loading the same little-endian bytes produces the same word
  under matched preconditions.
- Scope includes privilege-independent, non-faulting ordinary memory only.

### Chapter 8. Arithmetic, Logic, and Condition State

Develop add, subtract, Boolean operations, shifts, signedness, carry, and
overflow. Contrast RISC-V's explicit comparisons and branch predicates with
x86-64's implicit condition flags.

- Existing `I.thm.popcount32` becomes a later worked identity, not the
  definition of instruction semantics.
- New paired examples state which flags are observed or ignored.

### Chapter 9. Calling, Stacks, and Boundaries

Explain calls and returns as ISA operations plus an ABI contract. Separate
architectural facts from operating-system and calling-convention choices.
Cover stack alignment, return addresses, caller/callee saves, and the limits of
the book's user-mode model.

- No claim about “x86-64” or “RISC-V” may silently import a particular ABI.
- Exercises compare System V AMD64 and a named RISC-V psABI slice only after
  their source versions are pinned.

## Part III — Claims about programs

### Chapter 10. Equivalence and Refinement

Define full-state equivalence, observational equivalence, and refinement under
preconditions. Translate the negation of a fixed-width equivalence into a
solver query. Present the reader proof and the machine route together.

- Existing `I.prin.equivalence-vs-minimality` and `I.thm.popcount32` move here.
- Paired exercises prove an algebraic rewrite once for each ISA realization.

### Chapter 11. Languages, Costs, and Minimality

Define the candidate program language extensionally: decoded instructions,
operand forms, constants, available temporaries, memory policy, and maximum
length. Define instruction count, byte length, latency, throughput, and code
size as distinct models.

- The witness/lower-bound meeting is the central proof movement.
- AVX2 and RISC-V results appear only after their exact languages are printed.

### Chapter 12. Evidence That Can Fail

Develop solver verdicts, models, exhaustive enumerations, CNF, DRAT, independent
checking, negative controls, and kernel reconstruction. Retain the vacuous
certificate discovery as the chapter's warning.

- Existing `C.prin.*` and `C.thm.vacuous-certificate` move here.
- The chapter distinguishes the current Axeyum front door from absent ISA
  semantic and decoding layers.

## Part IV — Case studies and frontier

### Chapter 13. Permutations and Bit Manipulation

Build lane tags and permutation networks. Then present AVX2 byte reversal and
RISC-V Bitmanip reachability as separate applications of the common method.
State explicitly that one is a checked minimality result over restricted
vector languages and the other is a reproduced computation over draft
instruction families.

- Existing `P.*`, `M.avx2.*`, and `M.riscv.*` live here.
- Add a transfer exercise that maps both to M0-style state transformations.

### Chapter 14. What Remains to Be Built

Organize open objects by missing layer rather than estimated duration:

1. common word, state, and memory foundations;
2. ISA decoding and semantic slices;
3. equivalence certificates;
4. minimality certificates;
5. cost-model evidence; and
6. research applications.

The present catalogue remains available, but it no longer substitutes for a
textbook conclusion.

## Migration from the six-chapter draft

| Old chapter | Destination | Action |
|---|---|---|
| Introduction | Introduction | Rewrite promise and reading map to match all four parts |
| Basic Properties of Words | Chapter 1 | Keep the core proof; add endianness and paired ISA windows |
| Instructions as Functions | Chapters 2, 3, and 10 | Replace; retain popcount only in Chapter 10 |
| Cost, Certificates, and What a Proof Is Worth | Chapters 11 and 12 | Split cost from evidence |
| Permutations | Chapter 13 | Retain after the foundations |
| Particular Machines | Chapters 6–9 and 13 | Dissolve; foundational ISA material moves earlier, research results later |
| Open Problems | Chapter 14 | Reorganize by missing semantic/evidence layer |

## Axeyum capability boundary, audited 2026-08-27

Axeyum currently supplies:

- fixed-width bit-vector terms and solver routes;
- QF_BV equivalence queries with checked internal UNSAT handling;
- SAT/DRAT machinery and custom permutation synthesizers;
- the present AVX2 restricted-language and RISC-V enumeration artifacts.

Axeyum does **not** currently supply a reusable book-level model of:

- architectural machine state;
- byte-addressed instruction memory semantics;
- x86-64 or RISC-V decoding;
- general x86-64 or RISC-V instruction semantics;
- flags, traps, privilege, or ABI state; or
- a cross-ISA refinement relation.

The book may define and teach these objects before Axeyum implements them, but
the ledger must mark them as definitions or open implementation obligations.
No prose may imply that a QF_BV formula handwritten for one instruction is an
ISA semantics layer.

## Drafting order

Draft and verify in dependency order: Chapters 1–5, then 6–9, then 10–12,
then migrate the existing case studies into Chapter 13, and finally rewrite
Chapter 14 and the front matter. Do not write all machine proofs first. A proof
is drafted with the definition and example it serves.
