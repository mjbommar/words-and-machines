# Master structure: an abstract ISA, x86-64, and RISC-V

This document governs *Instruction Sets, Programs, and Proofs*. Chapter files,
objects, exercises, artifacts, and front matter must agree with it. The
presence of an old artifact does not earn a place in the curriculum. The
curriculum determines which evidence the project must build.

## Subject and method

The book teaches how instruction sets give exact meaning to programs and how
we can prove claims about those programs. It develops the subject in three
layers:

1. **A0**, a small abstract instruction set whose complete semantics fits in
   the book;
2. **x86-64 and RV64**, two real instruction-set slices used to test every
   abstract idea against different design choices; and
3. **proof and evidence**, the methods used to establish equivalence,
   refinement, translation, and bounded optimization claims.

Readers first learn the shared concept. They then see how the real
architectures realize or complicate it. Only then does the book ask a solver
or proof checker to carry a universal claim.

This is not an architecture reference manual, a catalogue of
superoptimization results, or a history of the RISC/CISC debate. It is a
foundations textbook with two sustained architectural companions.

## Promise to the reader

By the end, a reader should be able to take a short user-mode integer program
from either architecture and:

1. identify the words, state components, operands, memory effects, control
   effects, and exceptional outcomes on which its meaning depends;
2. express its behavior over explicit machine state;
3. distinguish encoding, syntax, semantics, ABI rules, operating-system rules,
   and microarchitectural performance;
4. state an equivalence or refinement claim with its precondition and
   observation;
5. translate a small algorithm between the declared x86-64 and RV64 slices;
6. define the candidate language and cost behind an optimization claim; and
7. explain what a test, computation, solver result, certificate, or kernel
   theorem does and does not establish.

## A0: the abstract ISA

A0 is a teaching definition, not a miniature x86-64 or RISC-V.

### State

- configurable word width \(w\), a positive multiple of eight; width-four
  examples remain reader-proof miniatures rather than executable A0 states;
- eight \(w\)-bit general registers \(r_0,\ldots,r_7\);
- finite byte-addressed memory;
- a \(w\)-bit program counter;
- condition bits \(Z,N,C,V\);
- running, halted, or trapped outcome.

A separate finite program supplies immutable instruction bytes and an entry
address. It is not mutable data state in the first model.

### Operands and instructions

A0 has register and immediate operands, base-plus-signed-offset memory
operands, and relative branch targets. Its core instructions are `mov`,
`load`, `store`, `add`, `sub`, Boolean logic, three shifts, `cmp`, conditional
and unconditional branches, and `halt`.

Every instruction has a printed read set, write set, normal next-state rule,
and trap rule. The first edition uses deterministic sequential execution and
a little-endian memory relation. Concurrency, weak memory, virtual memory,
self-modifying code, floating point, and vectors are outside A0.

## The two real slices

Exact manual revisions must be pinned before these become architectural
claims.

### RV64

The base is a named version of the RISC-V unprivileged ISA, initially limited
to user-mode RV64I integer forms. It includes the integer register file and
`x0`, program counter, base encoding, arithmetic and logic, shifts and
comparisons, ordinary loads and stores under declared assumptions, branches
and direct jumps, and one named RISC-V ABI example.

### x86-64

The base is a named revision of an authoritative architecture manual,
initially limited to selected 64-bit user-mode integer forms. It includes
general-purpose registers, `RIP`, a declared `RFLAGS` subset, selected
variable-length encodings, integer register/immediate and register-memory
forms, shifts and comparisons, branches, direct calls and returns, and one
System V AMD64 ABI example.

No chapter may silently import privileged state, every historical x86 mode,
all extensions, or one processor's timing into the phrase “x86-64.”

## Comparison discipline

RISC and CISC are architectural families, not semantics. Use the labels only
after naming the dimension being compared.

| Dimension | RV64 teaching slice | x86-64 teaching slice |
|---|---|---|
| Instruction length | fixed base width | variable length |
| Destination role | usually separate from sources | often also a source |
| Condition state | predicates commonly use explicit values | arithmetic commonly writes flags |
| Memory operands | separate loads and stores | selected arithmetic forms access memory |
| Register special cases | `x0` | width-specific subregister effects |
| Address formation | base plus immediate; separate arithmetic | base, index, scale, displacement |
| Calls and returns | control transfer plus ABI | control transfer, stack effects, plus ABI |

The table is a question generator, not a scorecard.

## Part I — Constructing an instruction set

Each chapter defines A0 and ends with paired RV64 and x86-64 windows.

### 1. Words and Their Meanings

Bits, words, modular arithmetic, signed and unsigned readings, logic, shifts,
extension, truncation, and byte decomposition. Reader proof: width-four
wraparound and two's complement. Machine obligation: width-parametric word
laws plus a small checked instance.

### 2. State

Registers, memory, program counter, condition state, outcomes, architectural
versus microarchitectural state, and observations. Reader proof: equality
under a projection does not imply full-state equality. Machine obligation:
executable A0 state construction and projection laws.

### 3. Instructions and Operands

Decoded instructions, explicit and implicit operands, read/write sets,
immediates, destination-as-source forms, traps, and transition rules. Paired
window: RV64 three-register addition and x86-64 two-operand addition with
declared flag effects. Machine obligation: A0 single-step semantics with
controls for hidden writes and wrong PC updates.

### 4. Memory

Byte addressing, loads, stores, little-endian assembly, valid ranges,
alignment policy, effective addresses, aliases, and traps. Reader proof:
store/load reconstruction. Machine obligation: A0 round trip with reversed
byte-order and invalid-range controls.

### 5. Programs and Control

Instruction maps, composition, PC updates, branches, traces, halt, trap, and
looping behavior. Reader proof: composition plus a contextual-replacement
counterexample. Machine obligation: bounded A0 trace replay with wrong-target
and execution-after-trap controls.

## Part II — Reading two real instruction sets

Each chapter holds one semantic question fixed and develops both architectures
beside A0.

### 6. Encoding and Decoding

Assembly syntax, instruction bytes, fields, decoded instances, illegal
encodings, fixed and variable length, and the separation between decoding and
meaning. Readers decode one constrained instruction from each ISA. Evidence
requires independent decoder agreement and mutation controls.

### 7. Data Movement and Address Formation

Moves, immediates, extension, truncation, loads, stores, effective addresses,
RV64 `x0`, and selected x86-64 subregister effects. Evidence relates selected
real instructions to A0 data and memory operations.

### 8. Arithmetic, Logic, and Condition State

Addition, subtraction, Boolean operations, shifts, carry, signed overflow,
comparisons, explicit Boolean results, and implicit flags. Evidence must test
both flag-sensitive and flag-insensitive observations.

### 9. Control Transfer

Conditional and direct transfers, link values, return addresses, relative
targets, register predicates, and flag predicates. Readers build and trace the
same small loop in A0, RV64, and x86-64.

### 10. Procedures, Stacks, and ABIs

Call/return mechanisms, stack memory, arguments, results, saved and scratch
registers, alignment, and named ABI slices. The chapter separates ISA facts
from agreements among programs. Evidence checks one small call/return
refinement under printed preservation conditions.

## Part III — Proving claims about programs

### 11. Equivalence, Observation, and Refinement

Full-state and observational equivalence, preconditions, traps, termination,
refinement, contexts, and counterexamples. Solver models must replay as A0
state traces.

### 12. Relating Different Instruction Sets

State relations, input/output conventions, stuttering, simulations, memory
agreements, and abstraction of flags or scratch state. The central reader
proof is a forward simulation for one scalar routine in all three machines.
Machine evidence requires independent real-ISA semantic adapters.

### 13. Program Languages, Costs, and Minimality

Candidate instructions, operand forms, constants, temporaries, memory policy,
maximum length, instruction count, byte length, and declared abstract costs.
The flagship result is a tiny scalar A0 minimality theorem, followed only then
by carefully scoped scalar counterparts for the two real slices.

### 14. Evidence That Can Fail

Tests, enumeration, solver models, UNSAT, formula generation, certificates,
independent checking, kernel reconstruction, hashes, provenance, and negative
controls. The vacuous-certificate discovery belongs here because its lesson is
general.

## Part IV — Synthesis and boundary

### 15. One Algorithm, Three Machines

Select one useful scalar routine that uses words, memory, arithmetic or logic,
and control; has clear implementations in A0, RV64, and x86-64; can be traced
by hand; and does not rely on an optional extension. Develop it from
specification through three implementations, reader proof, simulation,
machine evidence, controls, and boundary.

### 16. The Edge of the Model

Organize limits by missing concept: floating point; vectors and packed data;
atomics and weak memory; privilege and virtual memory; self-modifying code;
timing, leakage, and contention; and larger-scale verified compilation.
Optional vector extensions may appear here as examples of state beyond the
scalar core. They receive no flagship result because old artifacts happen to
exist.

## Proof spine

1. Word construction and width laws.
2. State and observation laws.
3. Single-step A0 semantics.
4. Load/store reconstruction.
5. Trace composition and branch execution.
6. Selected RV64-to-A0 instruction refinement.
7. Selected x86-64-to-A0 instruction refinement.
8. Program equivalence and contextual replacement.
9. Cross-ISA routine refinement.
10. Bounded scalar minimality under a printed language and cost.
11. Independent evidence replay with firing negative controls.

No later result may bypass a missing semantic layer with a handwritten formula
and still be described as an ISA result.

## Exercise spine

Every chapter includes four roles: **execute** a state or trace; **break** a
premise, transition, or artifact; **prove** a small general statement; and
**transfer** the idea among A0, RV64, and x86-64. Research questions must be
identified as such and cannot masquerade as routine exercises.

## Legacy decisions

| Legacy material | Decision |
|---|---|
| Byte-reversal opening | Remove; it makes an optional extension look foundational |
| Restricted vector-shuffle minimality | Remove from the claim spine and active ledger |
| Processor-weighted vector claim | Remove from the foundations |
| Old RISC-V Bitmanip tables | Remove from the claim spine; archive only if useful as provenance |
| Permutation chapter | Remove as a core chapter |
| Popcount identity | Retain only if rebuilt as a scalar cross-ISA example |
| Vacuous-certificate discovery | Retain in Chapter 14 |
| Open-problem catalogue by duration | Replace with Chapter 16's model boundaries |

Historical research may remain in `research/` if it has no active chapter or
ledger binding. Active objects and artifacts must follow the new proof spine.

## Axeyum boundary and drafting order

The current sibling checkout has useful bit-vector, solver, SAT, and
certificate machinery. It does not yet provide the state, decoder, memory,
x86-64 semantics, RV64 semantics, or cross-ISA refinement layers this outline
requires. The clean-sheet design is `AXEYUM-EVIDENCE.md`.

Work in this order:

1. Stabilize A0 and Chapters 1–5.
2. Pin authoritative RV64 and x86-64 source revisions and exact slices.
3. Draft Chapters 6–10 while recording honest semantic obligations.
4. Implement A0 state, memory, and execution in Axeyum.
5. Implement the two real-ISA adapters and constrained decoders.
6. Draft Chapters 11–14 beside the first genuine proof artifacts.
7. Select Chapter 15 only after both adapters work.
8. Write Chapter 16, then reconcile the Introduction, Preface, and builds.

Do not write all proofs first. Draft each definition, reader argument,
executable semantics, machine claim, negative control, and exercise family as
one teaching unit.
