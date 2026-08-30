# Chapter 3 research contract

**Scope:** Decoded instructions, operand roles, and complete one-step state
transitions
**Target capacity:** 10,000--14,000 words, governed by the obligations below
**Compelling question:** How can a short instruction line determine one
complete next state?

## Close-up subjects

1. One A0 addition whose destination is correct while a hidden effect is wrong.
2. The path from stored-program orders to typed instruction instances.
3. Source values, destination locations, addresses, and control targets as
   different mathematical functions.
4. Old-state evaluation followed by success or trap commit.
5. An exact RV64/x86-64 addition comparison that restores implicit effects.
6. Read and write footprints used to prove or refute reordering.

## Three lenses

| Lens | Depth | Required content |
|---|---|---|
| Origins | Medium | EDVAC orders and their operational meaning; System/360's five basic formats and explicit operand classes; microprogramming as an implementation technique below the architectural rule, without a single-inventor myth |
| Foundations | Deep | instruction instances as tagged products; legality and partiality; source-value and destination-location functions; old-state snapshots; total success-or-trap results; frame laws; dynamic and conservative footprints; dependence and a sufficient commutation theorem |
| Industry and economics | Medium | architecture manuals as compatibility contracts; assembler, disassembler, emulator, compiler, and verification consumers; LLVM TableGen and GCC machine descriptions; maintenance and validation work caused by instruction forms and extensions |

## Coverage routing

| Neighboring topic | Route |
|---|---|
| Instruction bits and variable-length decoding | Keep bytes, decoded instances, and semantics separate here; derive encodings in Chapter 6 |
| Byte-memory access, alignment, and alias geometry | Define memory operand stages here; derive their laws in Chapter 4 |
| Branches, jumps, traces, and loops | Include next-PC and target roles; develop traces in Chapter 5 and control transfer in Chapter 9 |
| Arithmetic flags and exceptional arithmetic | Use addition as the close-up; derive arithmetic and condition state in Chapter 8 |
| Procedures and implicit stack operands | Use as a boundary example; develop ABIs and stacks in Chapter 10 |
| Equivalence and refinement | State observation-sensitive comparison here; prove the hierarchy in Chapters 11--12 |
| Microcode, pipelines, renaming, and retirement | Mark the architecture/implementation boundary here; develop implementation detail in Chapter 16 |
| Concurrency, interrupts, and weak memory | Exclude from A0 single-step atomicity and route to Chapter 16 |

## Questions the chapter must answer

1. Why is a mnemonic not an instruction meaning?
2. What distinguishes bytes, assembly, a decoded instance, and a transition?
3. Why are source values, destination locations, and control targets different
   operand roles?
4. Where do implicit reads and writes enter a complete rule?
5. Why must every source be evaluated in the old state?
6. What state accompanies a failed fetch, decode, or execution?
7. How do dynamic footprints differ from conservative static footprints?
8. Which premises make two straight-line instruction effects commute?
9. Why do RV64 and x86-64 additions with the same numerical result remain
   different state transformations?
10. What present engineering work follows from adding or changing one
    instruction form?

## Feature inventory

- [x] Sourced history from stored-program orders through durable instruction
      formats and the architecture/implementation boundary.
- [x] Formal instruction-instance type with a legality predicate.
- [x] Separate source-value, destination-location, address, and target rules.
- [x] Complete success and trap commit laws with reader proofs.
- [x] A full A0 addition and single-step derivation with failing mutations.
- [x] Dynamic and conservative read/write footprints and a frame theorem.
- [x] A sufficient commutation theorem plus counterexamples to weaker tests.
- [x] Source-pinned RV64 and x86-64 operand/effect comparisons.
- [x] Current compiler-description and validation consequences with explicit
      engineering units rather than unsupported dollar estimates.
- [x] Honest Axeyum substrate audit and A0 executor obligation.
- [x] At least 25 exercises across execute, explain, break, prove, design,
      audit, economics, and transfer levels.

## Coverage comparison

Constructive and digital-design texts usually connect instruction forms to a
datapath and control implementation. Architecture texts classify addressing
modes and instruction formats, then use dependencies to motivate pipelines.
Compiler texts and the official LLVM and GCC documentation show the same
contract from the producer side: operand classes, constraints, implicit
definitions, selection patterns, and assembly output must stay aligned. This
chapter must unite those views around complete state transitions without
prematurely absorbing encoding, memory hierarchy, pipelines, or compiler
construction.

## Chapter audit

- **Draft reviewed:** 2026-08-30
- **Length:** approximately 10,150 source words, within the 10,000--14,000
  capacity band.
- **Rendered review:** 27 content pages at the 7-by-10 draft trim, printed
  pages 51--77. The instruction-layer diagram, complete-addition derivation,
  operand-role functions, success/trap commit laws, paired ISA table,
  commutation proof, tool-consumer table, and 35 exercises are legible. The
  chapter produces no overfull box in the full-book log.
- **Claim discipline:** the historical chain uses the EDVAC report, the
  original System/360 manual and architecture paper, and the Wilkes--Stringer
  paper. Present RISC-V, Intel, LLVM, and GCC claims point to pinned official
  manuals or official project documentation. Microprogramming is presented as
  an implementation technique, not a property inferred for every processor.
- **Axeyum boundary:** the live checkout has bit-vector and transition-system
  foundations but no A0 instruction, operand, decoder, state-step, or public
  replay package. The chapter preserves `OP.a0.step` as an implementation
  obligation and gives an ordered Rust/PyO3 milestone rather than claiming
  machine evidence.
- **Gates:** the full PDF build, prose check, Simplified Book English check,
  PDF preflight, and `git diff --check` pass. Chapter 3 has no Simplified Book
  English warning; remaining warnings are routed to chapters not yet revised.
- **Deferred by design:** exact encodings belong to Chapter 6; byte-memory
  laws to Chapter 4; traces to Chapter 5; arithmetic derivations to Chapter 8;
  program equivalence to Chapter 11; and pipelines, microcode choices,
  concurrency, interrupts, weak memory, and leakage to Chapter 16.
- **Status:** breadth-and-depth pass complete for this chapter, subject to the
  final cross-book consistency, bibliography, evidence, and production audits.

## Cross-chapter connections

**Back:** Chapters 1--2 supply fixed-width values and complete machine states.
**Forward:** Chapter 4 gives memory operands their byte-level meaning; Chapter
5 composes steps into traces.
**Through-lines:** short notation backed by complete meaning; visible and
implicit effects; architecture separated from implementation; evidence that
attacks one boundary at a time.
