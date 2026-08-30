# Chapter 5 sources

Research ledger opened 2026-08-30. Search results are leads only. Manuscript
claims must rest on opened primary papers, standards, official manuals,
curricula, or other authoritative sources.

## Opened origins and foundations

- Alan Turing, "On Computable Numbers, with an Application to the
  Entscheidungsproblem" (1936), for a finite table of behavior governing an
  indefinitely continuing symbolic process. Do not recast the paper as a
  modern stored-program architecture. Publisher record and paper metadata
  checked through the London Mathematical Society, DOI
  `10.1112/plms/s2-42.1.230`.
- The EDVAC report and contemporary stored-program histories, for instruction
  order and conditional transfer in addressable memory. Avoid a sole-inventor
  narrative and separate design circulation from implementation milestones.
- Herman Goldstine and John von Neumann, flow-diagram work, for early explicit
  graphical reasoning about computational control. Institute for Advanced
  Study archive copy of *Planning and Coding of Problems for an Electronic
  Computing Instrument*, Part II, Volume I, dated 1947-04-01, opened.
- Robert Floyd, "Assigning Meanings to Programs" (1967), for inductive
  assertions attached to flowcharts and proofs of program properties. Primary
  reprint and AMS bibliographic record checked, DOI
  `10.1090/psapm/019/0235771`.
- C. A. R. Hoare, "An Axiomatic Basis for Computer Programming" (1969), for
  preconditions, postconditions, axioms, rules, and machine-checking ambition.
  ACM publisher record and Oxford repository metadata checked, DOI
  `10.1145/363235.363259`.
- Corrado Böhm and Giuseppe Jacopini (1966), plus later structured-program
  discussion, for the representation of flow by sequence, selection, and
  iteration. Do not claim that hardware branches ceased to matter.
  Primary paper and ACM DOI `10.1145/355592.365646` checked.

## Opened current authoritative sources

- Current RISC-V unprivileged architecture manual for direct conditional
  branches, JAL, and JALR, including bases, immediate scaling, alignment, and
  link-register effects in the selected RV64I slice.
- Current Intel instruction-set manual for Jcc, JMP, and selected indirect
  control forms in 64-bit mode, with exact relative-base and exception scope.
- RISC-V control-flow-integrity specification and Intel Control-flow
  Enforcement Technology documentation for the modern security consequences
  of indirect control. Scope features to supported implementations and enabled
  modes.
- LLVM documentation for basic blocks, terminators, CFG analyses, branch
  probabilities, and optimization consumers. Compiler IR structure is not
  identical to machine execution.
- Current curriculum guidance for transition systems, control flow,
  invariants, termination, testing coverage, performance, and security.

The RISC-V ratified specifications library was checked at version 20260120;
the CFI chapter documents Zicfilp landing pads and Zicfiss shadow stacks. Intel
official CET documentation was opened for shadow-stack and indirect-branch
tracking scope. LLVM's current Programmer's Manual was opened for the
single-entry, single-exit `BasicBlock` abstraction and mandatory terminator.
The exact Intel Jcc/JMP forms and current curriculum mapping remain to be
opened before those claims enter the manuscript.

## Coverage comparators

- Discrete mathematics and logic texts develop relations, reflexive transitive
  closure, induction, and well-founded order.
- Programming-language semantics texts develop small-step execution,
  determinism, progress, traces, contextual equivalence, and divergence.
- Compiler texts develop basic blocks, CFGs, dominators, dataflow, feasible
  paths, and optimization.
- Program-verification texts distinguish partial correctness, total
  correctness, invariants, variants, and proof obligations.
- Computer-architecture texts separate architectural control effects from
  prediction, speculation, pipeline, and timing costs.

## Source cautions

- A finite trace is evidence for its visited prefix, not for universal
  termination or absence of another path.
- A CFG edge admitted by syntax need not be feasible from an allowed entry.
- Bound exhaustion is a runner result, not an architectural halt.
- Determinism gives at most one successor, not the existence of a successor.
- An invariant proves preservation when reached; it does not by itself prove
  that a loop exits.
- A decreasing integer is not a termination argument unless it is bounded
  below in a well-founded set.
- Architectural equality does not imply equal branch-prediction cost, timing,
  speculation, or leakage.

## Axeyum substrate audit

The live sibling checkout was inspected on 2026-08-30 on branch
`research/open-problems-2026-08`, which also had an unrelated untracked
research directory. No files were changed there.

- `axeyum-solver/src/bmc.rs` defines a symbolic `TransitionSystem` through
  state variables, initial-state, transition, and bad-state predicates.
  `BmcOutcome` distinguishes a replay-checked reachable model,
  `UnreachableWithinBound`, and `Unknown`.
- `axeyum-verify/src/bmc.rs` supplies counter and general scalar-loop
  adapters. Its documented post-exit stutter is a bounded-model-checking
  convention, not A0 terminal-state semantics.
- The verification crate reflects selected MIR and LLVM graphs, has checked
  loop and CFG tests, and records branch decisions for a scoped control-flow
  constant-time goal.
- There is no A0 code map, fetch/decode/step package, complete A0 trace
  artifact, four-way concrete runner result, or book-facing Python runner.

The transition-system and replay substrate is reusable only through an
explicit A0 adapter. It is not evidence that `OP.a0.run` is discharged.
