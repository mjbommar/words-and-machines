# Chapter 15 research contract

**Scope:** One XOR reduction specified once and carried through A0, RV64I,
x86-64, three machine-to-logical simulations, concrete traces, costs,
controls, and honest evidence boundaries
**Target capacity:** 18,000--25,000 words, governed by the obligations below
**Compelling question:** What must remain the same when one algorithm becomes
three genuinely different machine programs?

## Close-up subjects

1. One finite-word XOR monoid, proved bitwise and lifted to folds.
2. One recursive and one indexed definition of the same memory reduction.
3. One loop invariant proved by initialization, preservation, exit, frame, and
   termination obligations.
4. Complete A0, RV64I, and x86-64 listings with exact cut points, read/write
   footprints, branch targets, and callable-interface boundaries.
5. One concrete byte-level or instruction-level trace per architecture.
6. One machine-to-logical simulation per architecture and a derived
   three-machine agreement theorem.
7. One stuttering diagram showing unequal instruction counts between common
   logical cut points.
8. One mutation matrix that attacks specification, memory, instruction,
   control, ABI, observation, and evidence bindings.
9. One static/dynamic cost table that refuses to equate instruction count,
   code bytes, memory traffic, and elapsed time.
10. One scalar-to-vector comparison that explains work, span, tree shape,
    floating-point order, bandwidth, and tail handling without claiming a
    vector theorem.

## Three lenses

| Lens | Depth | Required content |
|---|---|---|
| Origins | Deep | parity and error detection; algebraic folds; accumulator loops; parallel prefix and reduction trees; collective and distributed reductions; compiler recognition |
| Foundations | Deep | bitwise XOR; vector spaces over GF(2); monoids and folds; homomorphisms; induction; loop invariants and variants; frame conditions; modular-to-natural arithmetic; stuttering simulation; work and span |
| Industry and economics | Deep | ABI and encoding cost; memory bandwidth and locality; branches and front ends; compiler vectorization; SIMD/vector extensions; distributed communication and failure; evidence engineering and maintenance |

## Questions the chapter must answer

1. Why does XOR form a commutative monoid on fixed-width words?
2. How does bitwise parity connect XOR to the vector space over GF(2)?
3. Which algebraic laws permit reassociation and parallel reduction?
4. Why is floating-point addition a different reduction contract?
5. What does the loop invariant say at entry, after load, after combine, and
   at exit?
6. Which premise turns 64-bit modular pointer arithmetic into natural address
   arithmetic?
7. Why can the three machines agree without matching instruction for
   instruction?
8. Which parts of the cross-machine relation are functional, ABI-specific,
   harness-specific, or deliberately forgotten?
9. What are the exact static and dynamic instruction counts of the listings?
10. What can code size, memory traffic, work, span, and throughput each tell us?
11. How do LLVM, RISC-V vector reductions, MPI, and MapReduce exploit or demand
    algebraic structure?
12. What current Axeyum machinery exists, and which machine packages and
    evidence objects remain absent?

## Feature inventory

- [x] Sourced history from parity checks through parallel and distributed
      reductions.
- [x] Complete GF(2), monoid, fold, homomorphism, and chunking foundations.
- [x] Exact memory-region contract and empty-input case.
- [x] Reader proof of initialization, preservation, exit, and termination.
- [x] Intermediate invariants after load and after combine.
- [x] A0, RV64I, and x86-64 scalar listings.
- [x] Exact encoding, branch, footprint, and dynamic-count tables.
- [x] Separate machine-to-logical simulations and derived agreement theorem.
- [x] Stuttering/cut-point explanation.
- [x] Work/span and scalar/vector/distributed reduction comparison.
- [x] Industrial compiler, memory, ABI, and communication economics.
- [x] Negative controls and candid Axeyum stopping point.
- [x] At least 50 exercises across algebra, trace, proof, break, cost,
      evidence, industry, and transfer categories.

## Chapter audit

Opened 2026-08-30. The inherited manuscript has 6,304 source words and 22
exercises against an 18,000--25,000-word target. Its strongest material is the
precise reduction contract, loop invariant, three readable listings, local
lemma inventory, cut-point simulation, control ladder, and honest statement
that the machine artifacts do not yet exist.

The completed depth pass has 18,005 source words and 71 exercises. It occupies
printed pages 421--468 in the 7-by-10-inch edition: 48 pages. The added layers
develop the algebra that licenses chunking and parallelism, derive work and
span, bind exact real-ISA bytes, separate the three machine-to-logical proof
routes, and connect the example to compiler, bandwidth, vector, collective,
distributed, and maintenance economics. The inherited accumulator typo is
repaired.

The universal real-machine arguments remain reader proofs over pinned sources
and stated semantics. A later executable-artifact pass added a finite
machine-produced Axeyum report for eight declared cases, exact program bytes,
typed cut-point relations, cost accounting, and a firing pointer-step control.
That computation is not a universal certificate or a minimality result.

## Cross-chapter connections

**Back:** Chapters 1--10 supply words, state, memory, control, encoding, ABIs,
and local machine semantics. Chapters 11--12 supply observation and simulation.
Chapters 13--14 supply cost and evidence contracts.
**Forward:** Chapter 16 explains why vector state, weak memory, faults,
microarchitecture, and timing require extensions rather than informal
generalization.
**Through-line:** one algorithm is a mathematical relation, not a shared
surface syntax; agreement follows only after every machine is connected to
that relation under explicit scope and evidence.
