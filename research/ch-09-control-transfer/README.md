# Chapter 9 research contract

**Scope:** Architectural control transfer, exact target calculation, branch
predicates, links and indirect targets, control-flow structure, loop proof, and
the bridge from one-step semantics to current implementation and security
stakes
**Target capacity:** 12,000--16,000 words, governed by the obligations below
**Compelling question:** How can one small next-address rule turn finite stored
instructions into a path, a loop, a procedure, or a guarded choice?

## Close-up subjects

1. One taken and untaken A0 branch with byte-exact target calculations.
2. The same counted loop in A0, RV64I, and x86-64.
3. One RV64 B-type and one x86 relative-displacement derivation.
4. One link-producing jump and one indirect-target proof.
5. One loop invariant, natural-number variant, and exact iteration count.
6. One control-flow graph with dominance, a back edge, and an unreachable edge.
7. One branch-layout case that separates architecture from prediction cost.
8. One control-flow integrity case that separates target soundness from target
   validity and policy.

## Three lenses

| Lens | Depth | Required content |
|---|---|---|
| Origins | Medium | early conditional orders and repetition; flow diagrams and subroutines; stored links; structured-program debate; branch prediction as later implementation history; distinguish proposed notation, working machines, architecture, and compiler practice |
| Foundations | Deep | successor relation; partial transition and traces; predicates; signed displacement arithmetic; graph reachability, dominance, cycles, and strongly connected regions; induction invariants; well-founded variants; safety, progress, and termination; simulations with stuttering; sound/complete indirect-target sets |
| Industry and economics | Deep | code layout and density; branch prediction and misprediction cost without processor-wide slogans; indirect branches, switch lowering, dispatch, and returns; linkers/relocation and range extension; compiler if-conversion; control-flow integrity, shadow stacks, and speculative limits; debugging and profile evidence |

## Coverage routing

| Neighboring topic | Route |
|---|---|
| Arithmetic condition formulas | Use here; Chapter 8 owns their derivation |
| Encoded immediate reconstruction | Use one worked case; Chapter 6 owns decoding theory |
| Stack frames and return-address preservation | Prepare here; Chapter 10 owns procedures and ABIs |
| General equivalence and stuttering simulation | Use on the loop; Chapters 11--12 own the theory |
| Search cost and minimality | Name branch cost dimensions; Chapter 13 owns optimization objectives |
| Trace and certificate formats | Specify branch evidence; Chapter 14 owns the trust ladder |
| Prediction, speculation, timing, privilege, concurrency | Mark exact boundaries; Chapter 16 owns extensions |

## Questions the chapter must answer

1. Which address is fallthrough, which is the target base, and how is a
   displacement extended and scaled?
2. Why are predicate correctness and target correctness separate obligations?
3. How do A0, RV64I, and x86-64 encode the same mathematical choice in
   different state and instruction shapes?
4. How does a link turn a jump into preparation for a later return?
5. Why does an indirect transfer require an invariant over possible targets?
6. What do target soundness, completeness, validity, and policy approval each
   mean?
7. How do traces, control-flow graphs, reachability, dominance, and loop
   invariants differ?
8. What proves safety, progress, termination, and exact iteration count?
9. When can multiple steps on one machine correspond to one on another?
10. How do code placement, displacement range, prediction, and instruction
    density create current economic tradeoffs?
11. Which control-flow security properties are architectural, enforced, or
    outside the scalar model?
12. What must Axeyum decode, step, replay, mutate, solve, and record before a
    branch or loop claim is defensible?

## Feature inventory

- [x] Sourced history from early conditional orders through subroutines,
      structured control, and modern prediction/control protection.
- [x] Exact successor, fallthrough, target, link, and failure definitions.
- [x] Byte-exact A0, RV64I, and x86-64 direct-target derivations.
- [x] Complete predicate/read/write/frame obligations for selected forms.
- [x] Direct versus indirect target proof with soundness, completeness,
      validity, and policy distinctions.
- [x] Control-flow graph, reachability, dominance, cycle, and loop-region
      foundations.
- [x] Same counted loop in three machines with invariant, variant, iteration
      count, and stuttering relation.
- [x] Linker, relocation, range-extension, code-layout, and density stakes.
- [x] Prediction, if-conversion, and profile-guided tradeoffs with honest scope.
- [x] CFI, return protection, and speculation boundaries.
- [x] Honest Axeyum substrate audit and staged implementation obligation.
- [x] At least 40 exercises across execution, proof, break, history, graph,
      compiler, economics, security, Axeyum, and cross-ISA transfer.

## Chapter audit

Breadth-and-depth revision opened 2026-08-30. The inherited draft has 5,025
source words and 15 exercises. It already has a strong target-arithmetic,
three-machine loop, indirect-transfer, invariant, trace/graph, Axeyum, and
five-obligation spine. It does not yet meet the historical, graph-theoretic,
linking/layout, prediction/economic, security, exercise, source, or rendered
depth obligations above.

Chapter-level revision completed 2026-08-30. The revised source has 12,016
words and 48 exercises. It typesets on printed pages 225--258: 34 pages at the
book's 8-by-10-inch trim. New material covers the historical development from
Turing and stored-program flow diagrams through subroutines, structured
control, compiler graphs, and prediction; partial transition functions and
the halting boundary; physical selection and architectural abstraction; exact
RV64I B-type and x86-64 length-dependent target derivations; continuations;
jump tables; layout and relaxation; CFI; dominance, components, reducible
shape, and a worked graph; and an evidence-level-correct Axeyum route.

Validation passed with `make -C book check`, `make -C book simplified`,
`make -C book pdf`, `make -C book preflight`, and `git diff --check`. The final
Chapter 9 build has no local overfull boxes, no unresolved citations, embedded
fonts, no Type 3 fonts, and images at or above 300 ppi. A representative
eight-page contact sheet was inspected across the opening, foundations,
target arithmetic, layout, jump-table proof, loop proof, and exercises. The
Axeyum audit is tied to revision `a9991fda`; it records reusable generic and toy
VM control-flow substrate separately from the still-missing A0 and real-ISA
adapters.

## Cross-chapter connections

**Back:** Chapters 2, 5, 6, and 8 supply state, traces, decoding, arithmetic
conditions, and basic loop reasoning.
**Forward:** Chapter 10 turns links into procedure contracts; Chapters 11--14
relate paths and evidence; Chapters 15--16 apply and extend the control model.
**Through-lines:** a program is not merely stored instructions but a justified
successor path; a small branch rule can compress unbounded repetition while
also creating physical cost and a security boundary.
