# Chapter 11 research contract

**Scope:** Behavioral semantics, observations, equivalence, refinement,
contextual replacement, simulations, counterexamples, and translation
validation for the book's selected scalar machines
**Target capacity:** breadth governed by the obligations below; word and page
counts are diagnostics, not completion conditions
**Compelling question:** What must two programs preserve before one may safely
replace the other?

## Close-up subjects

1. One historical move from informal optimization to mathematical program
   meaning and correctness.
2. One complete behavior space containing normal return, trap, and divergence.
3. One observation lattice in which stronger observations imply weaker ones.
4. One A0 pair that agrees on a result but differs in conditions and context.
5. One real RV64 pair and one x86-64 pair with exact preconditions and effects.
6. One refinement example in which implementation and specification have
   different states or different permitted behavior sets.
7. One forward-simulation proof over several steps, with a failed simulation
   as a non-example.
8. One contextual-equivalence argument that names the allowed contexts.
9. One undefined-behavior or poison case that prevents symmetric equality.
10. One translation-validation case with a replayed miscompilation witness.

## Three lenses

| Lens | Depth | Required content |
|---|---|---|
| Origins | Medium | early program transformations; Floyd assertions and formal program meaning; Hoare-style contracts; simulation and refinement; compiler correctness; translation validation |
| Foundations | Deep | relations and equivalence relations; preorders and partial orders; set inclusion; projections and observation lattices; traces; partial and total correctness; may/must quantifiers; contextual closure; forward and backward simulation; induction and composition |
| Industry and economics | Deep | compiler optimization and miscompilation; binary translation; JITs; cryptographic constant-time observations; validation latency and solver cost; proof maintenance; trusted computing base; counterexample triage; compatibility and safety-critical compilation |

## Coverage routing

| Neighboring topic | Route |
|---|---|
| State, transition, and observation definitions | Import from Chapters 2 and 5 |
| Branch traces and control-flow graphs | Apply here; Chapter 9 owns the foundation |
| Procedure and ABI contexts | Apply here; Chapter 10 owns the boundary contract |
| Full cross-ISA control-point simulations | Introduce the proof rule here; Chapter 12 owns sustained machine-to-machine cases |
| Candidate languages, costs, and minimality | Equivalence is a premise; Chapter 13 owns search and cost |
| Certificates and trust ladders | Name the evidence route; Chapter 14 owns the full treatment |
| Whole-program three-machine proof | Prepare relations; Chapter 15 composes them |
| Concurrency, weak memory, probability, timing, and leakage | State the boundary; Chapter 16 owns extension design |

## Questions the chapter must answer

1. What is a behavior, and why is a final value insufficient?
2. When is equivalence symmetric, and when is refinement directional?
3. How do observations form a useful order from coarse to fine?
4. Where do preconditions come from, and who must establish them?
5. What is the relation among trace equivalence, final-state equivalence,
   observational equivalence, and contextual equivalence?
6. Why does a compiler transformation often require refinement rather than
   plain equality in the presence of undefined or nondeterministic behavior?
7. What does a forward simulation prove, and when is a backward simulation or
   another argument needed?
8. How do simulations compose across passes or state spaces?
9. What makes a counterexample architectural and replayable?
10. How do finite enumeration, SMT, proof assistants, and translation
    validation support different scopes?
11. What does the current Axeyum MIR/LLVM route actually establish?
12. Which A0, RV64, x86-64, memory, and procedure adapters remain absent?

## Feature inventory

- [x] Sourced history from formal program meaning through verified compilation
      and translation validation.
- [x] Exact separation of behavior, trace, terminal state, and observation.
- [x] Equivalence relation and refinement-preorder foundations.
- [x] Observation ordering, products, kernels, and information loss.
- [x] Preconditions, weakest sufficient conditions, and caller discharge.
- [x] Result-only, full-state, trace, termination, and contextual comparisons.
- [x] A0, RV64, and x86-64 worked examples with concrete witnesses.
- [x] Forward simulation, stuttering boundary, and composition proofs.
- [x] Nondeterministic may/must and behavior-set inclusion.
- [x] Undefined behavior, poison, traps, and asymmetric compiler refinement.
- [x] Translation-validation economics and industrial failure modes.
- [x] Honest live Axeyum MIR/LLVM audit with replay and limitations.
- [x] Comparison with at least two substantial textbooks or course texts.
- [x] At least 40 exercises across execute, prove, break, history, real ISA,
      compiler, security, Axeyum, and transfer categories.

## Chapter audit

Breadth-and-depth revision opened 2026-08-30. The inherited draft has 5,544
source words, 18 exercises, and no citations. It has a useful behavior,
precondition, observation, contextual-replacement, composition, and checking
spine. It is not yet a complete textbook chapter. It lacks sourced history,
order-theoretic foundations, sustained simulation rules, real-ISA examples,
undefined-behavior refinement, industrial translation validation, textbook
comparison, and adequate exercises. Its Axeyum section is stale: the live
checkout already contains checked scalar MIR-to-LLVM equivalence and replayed
wrong-transform counterexamples, although it still lacks the book's A0 and
real-ISA program layers.

Revision closed 2026-08-30 at 9,936 source words and 50 exercises. The
typeset chapter spans 30 pages in the 7-by-10 print build (printed pages
291--320). The selected RV64I and x86-64 bytes were independently checked with
`llvm-mc`. The chapter-level Simplified Book English report has no warnings;
the full book check and PDF build pass. The final PDF has no Chapter 11
overfull boxes or undefined citations. A visual check covered the opener,
refinement-preorder proof, real-ISA example, simulation proof, production-cost
table, and exercise opening. The source comparison and live Axeyum audit are
recorded in `sources.md`.

## Cross-chapter connections

**Back:** Chapters 2, 5, 9, and 10 supply state, execution, traces, control,
observations, and procedure contexts.
**Forward:** Chapter 12 develops cross-ISA simulations; Chapters 13--15 depend
on equivalence before discussing cost, evidence, and the whole case study.
**Through-lines:** sameness is not found inside the instruction bytes. It is a
relation chosen for a use, proved over declared behaviors, and attacked by the
smallest context or input that can expose a difference.
