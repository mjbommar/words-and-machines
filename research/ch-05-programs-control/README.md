# Chapter 5 research contract

**Scope:** Programs as finite code maps, execution traces, control transfer,
loops, termination, contextual replacement, and bounded execution evidence
**Target capacity:** 10,000--14,000 words, governed by the obligations below
**Compelling question:** How can a finite program describe a computation whose
path and duration are not fixed in advance?

## Close-up subjects

1. One complete straight-line trace with every state component accounted for.
2. One conditional branch derived from flags, signed displacement, and program
   counter convention.
3. One loop proved safe by an invariant and terminating by a decreasing natural
   measure.
4. One nonterminating loop and the exact evidence a finite runner may report.
5. One control-flow graph whose syntactic edges exceed its feasible edges.
6. One contextual-replacement theorem with an explicit observation boundary.
7. Exact RV64 and x86-64 branch examples whose bases, ranges, and side effects
   differ from A0.

## Three lenses

| Lens | Depth | Required content |
|---|---|---|
| Origins | Medium | stored-program control without a single-inventor myth; Turing's finite descriptions and unbounded computation; early conditional transfer; flow diagrams; Floyd and Hoare on inductive assertions; structured-program debates without reducing machine control to source syntax |
| Foundations | Deep | finite programs and transition systems; reflexive transitive closure; determinism and partiality; traces and prefixes; reachability; control-flow graphs versus feasible paths; invariants; well-founded variants; partial versus total correctness; contextual equivalence and replacement; bounded evidence |
| Industry and economics | Medium | branch prediction and pipeline disruption as routed costs; compiler CFGs and optimization; coverage and path explosion; watchdogs and timeouts; worst-case execution bounds; indirect-control security and control-flow integrity; reproducible trace evidence |

## Coverage routing

| Neighboring topic | Route |
|---|---|
| Instruction encoding and decoder legality | State fetch/decode premises here; derive bytes in Chapter 6 |
| Detailed RV64 and x86-64 data movement and branch encodings | Compare semantic contracts here; expand ISA forms in Chapters 7 and 9 |
| Procedures, calls, returns, stacks, and ABIs | Mention control successors; develop in Chapter 10 |
| Full program equivalence and refinement | Prove a bounded contextual replacement miniature here; develop relations in Chapter 11 |
| Cross-ISA simulations | State why traces need related control points; construct in Chapter 12 |
| Search, synthesis, and path explosion | Establish finite bounds and path structure here; develop costed search in Chapter 13 |
| Evidence manifests and replay | Require trace binding here; develop assurance levels in Chapter 14 |
| Timing, prediction, speculation, and side channels | Name the architectural/microarchitectural split here; extend the model in Chapter 16 |

## Questions the chapter must answer

1. Why does textual adjacency not determine the next instruction?
2. How does a finite code map generate arbitrarily long behavior?
3. What is the exact relation between one step, a finite trace, and zero or more steps?
4. Which conclusions follow from determinism, and which require existence or termination?
5. Why does a control-flow graph overapproximate feasible executions?
6. What distinguishes halt, trap, bound exhaustion, and a still-runnable state?
7. How does an invariant prove safety without proving termination?
8. Which well-founded measure is needed for a termination proof?
9. Why do partial and total correctness have different logical forms?
10. Under which state, observation, and context premises may one trace segment replace another?
11. How do real branch conventions and indirect targets enlarge A0's contract?
12. Which industrial costs require timing, predictor, security, or workload state outside A0?

## Feature inventory

- [x] Sourced history from finite machine descriptions and stored programs to
      inductive assertions and structured control.
- [x] Exact finite program, fetch, one-step, trace, and multi-step definitions.
- [x] Proofs of identity, concatenation, prefix closure, and deterministic
      uniqueness with all existence premises visible.
- [x] Conditional branch derivation including predicate, signed displacement,
      scale, base, range, alignment, and fetch consequences.
- [x] CFG construction plus explicit syntactic, feasible, and observed edge
      distinctions.
- [x] Reachability and bounded-run outcome taxonomy with no halt-by-timeout bug.
- [x] Invariant induction and a complete well-founded termination proof.
- [x] Partial and total correctness with vacuity and nontermination examples.
- [x] Contextual replacement proof with frame and observation requirements.
- [x] Source-pinned RV64 and x86-64 direct and indirect control comparisons.
- [x] Current compiler, testing, security, performance, and operational stakes.
- [x] Honest Axeyum substrate audit and trace implementation obligation.
- [x] At least 25 exercises across execution, proof, break, design, audit,
      security, economics, and transfer levels.

## Chapter audit

Breadth-and-depth revision complete, subject to the final whole-book audit.
The chapter has 9,999 source words and 44 exercises. It renders across printed
pages 107--132 (26 pages), with Chapter 6 beginning on page 133. The source
ledger and chronology record the primary and official sources used, including
Turing, Goldstine and von Neumann, Böhm and Jacopini, Floyd, Hoare, the ratified
RISC-V specifications, Intel's architecture material, and LLVM documentation.

The full PDF build and print preflight pass. Chapter 5 has no Simplified Book
English findings and no chapter-local overfull boxes. A contact-sheet review,
close inspection of the opening, middle transitions, ISA comparison, and final
exercise page, and inspection of the Chapter 6 boundary found no clipping,
collisions, stranded headings, or missing exercises. The Axeyum discussion was
checked against the live sibling repository and distinguishes reusable BMC
substrate from the still-missing A0 fetch/decode/step/trace runner.

## Cross-chapter connections

**Back:** Chapters 2--4 supply complete state, instruction effects, and checked
memory.
**Forward:** Chapter 6 turns code bytes into instruction instances; Chapters
9--12 deepen control transfer, procedures, equivalence, and cross-machine
simulation.
**Through-lines:** finite description and unbounded consequence; one-step laws
composed into global claims; bounded observation kept distinct from semantic
termination; visible state separated from hidden cost state.
