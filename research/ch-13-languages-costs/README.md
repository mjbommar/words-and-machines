# Chapter 13 research contract

**Scope:** Finite candidate languages, contextual cost orders, and evidence
that a program has minimum cost within the printed search universe
**Target capacity:** 14,000--20,000 words, governed by the obligations below
**Compelling question:** What must a failed search contain before it can
establish that no cheaper program exists?

## Close-up subjects

1. One historical peephole optimization and its local correctness question.
2. Massalin's 1987 superoptimizer and the meaning of its smallest-program claim.
3. One complete finite candidate grammar with an exact cardinality derivation.
4. One candidate-language tree showing resources, operands, and program length.
5. One A0 \(x+2\) witness and complete zero/one-instruction lower bound.
6. One cost order where instruction count, bytes, and a processor model disagree.
7. One symmetry reduction with an explicit coverage proof.
8. One counterexample-guided synthesis trace.
9. One proof-of-exhaustion or per-stratum refutation package.
10. One industrial case where model-optimal code loses on measured hardware.

## Three lenses

| Lens | Depth | Required content |
|---|---|---|
| Origins | Deep | peephole optimization; instruction-sequence search; Massalin; Denali; Bansal--Aiken; equality saturation and instruction scheduling as neighboring optimization traditions; distinguish witness search, exhaustive search, and certified lower bounds |
| Foundations | Deep | finite grammars; products and sums for language cardinality; equivalence classes and quotienting; well-founded and lexicographic orders; Pareto fronts; upper and lower bounds; existential/universal quantifier order; CEGIS; symmetry; completeness; proof by exhaustion; certificates and trust boundaries |
| Industry and economics | Deep | compiler engineering time; code size; latency versus throughput; processor-specific scheduling; measurement noise; compilation budget; cache and energy consequences; solver resource cost; support and reproducibility; why model-optimal need not mean faster on silicon |

## Coverage routing

| Neighboring topic | Route |
|---|---|
| Program equivalence and observations | Import from Chapter 11 |
| Cross-ISA relations | Import from Chapter 12 |
| Decoder and byte provenance | Apply here; Chapter 6 owns the foundation |
| Proof formats, manifests, and trust ladders | Name exact needs here; Chapter 14 owns full treatment |
| Complete three-machine optimized case | Prepare contracts here; Chapter 15 owns the sustained case |
| Microarchitecture, timing leakage, vectors, and concurrency | Cost implications here; semantic extension in Chapter 16 |
| General compiler optimization | Exclude as a survey; use only cases that sharpen minimality |
| Equality-saturation extraction and global scheduling | Compare as neighboring optimization problems; do not claim the same candidate language or certificate |

## Questions the chapter must answer

1. Why does a witness establish an upper bound but not a lower bound?
2. Which clauses make a candidate language finite and reproducible?
3. How are decoded forms, byte strings, operand choices, and resources counted?
4. When is symmetry breaking a theorem-preserving quotient?
5. How does the observation change which candidate wins?
6. Why do instruction count, byte count, latency, throughput, energy, and
   compiler time define different optimization problems?
7. What makes a cost order well founded?
8. How do ties, uniqueness, lexicographic order, and Pareto order differ?
9. Why does a timeout or solver verdict fail to establish a lower bound?
10. How do exhaustive enumeration, SAT/SMT, and CEGIS cover cheaper strata?
11. What must a durable minimality artifact bind and retain?
12. What does current Axeyum provide, and what remains absent?

## Feature inventory

- [x] Sourced history from peephole optimization through current superoptimization.
- [x] Prior-art correction: no novelty or “first minimality” slogan.
- [x] Exact candidate-language grammar and cardinality derivation.
- [x] Resources, constants, temporaries, memory, faults, and stop policy.
- [x] Decoded-form versus byte-language distinction.
- [x] Equivalence classes, quotienting, symmetry, and coverage proof.
- [x] Instruction, byte, weighted, contextual, lexicographic, and Pareto costs.
- [x] Processor-specific latency/throughput and model-versus-measurement split.
- [x] Upper-bound witness plus complete lower-bound argument.
- [x] Full A0 \(x+2\) miniature with edge widths and negative controls.
- [x] Enumeration, SAT/SMT, CEGIS, quantifier order, and termination.
- [x] Proof-of-exhaustion and per-stratum certificate design.
- [x] Industrial comparison including a model-optimal measured slowdown case.
- [x] Honest Axeyum audit and staged implementation route.
- [x] Comparison with at least two substantial textbooks or course sources.
- [x] At least 45 exercises across count, execute, prove, break, cost,
      evidence, history, industry, Axeyum, and transfer categories.

## Chapter audit

Breadth-and-depth revision opened 2026-08-30. The inherited draft has 5,684
source words and 18 exercises. It correctly separates witness upper bounds
from cheaper-space lower bounds, declares the candidate-language contract,
compares several costs, gives a pencil-checkable A0 \(x+2\) lower bound, and
states the missing Axeyum route.

It is not yet complete. The history is thin after Massalin and Bansal--Aiken;
the candidate grammar has no general counting derivation; quotienting and
symmetry lack a reader proof; CEGIS and quantifier order need a complete
miniature; proof-of-exhaustion needs a concrete serialized design; real
processor and economic costs are brief; modern prior art and the
model-optimal/measured-performance split are missing; and the exercise set is
too small. Several inline mathematical symbols also lost their delimiters in
an earlier edit; those were repaired when this contract opened.

The first depth expansion on 2026-08-30 closed those feature gaps. It added
Denali and scoped prior art, exact grammar counts, a proved symmetry quotient,
well-founded and multi-objective orders, Unison's measured counterexample, a
complete CEGIS trace, a digest-bound proof-of-exhaustion design, an audited
Axeyum route, two textbook comparisons, and 51 exercises. The source now has
9,834 words.

The second depth pass on 2026-08-30 completed those obligations. It added a
stateful typed-resource grammar with an exact recurrence and reader proof; a
proof-producing Boolean encoding with separate soundness and completeness
directions; a finite-sample lower-bound derivation; group actions, orbit
counting, and the two-element case of Burnside's lemma; a mathematical account
of probabilistic test filtering; a sharper comparison of rewrite closure,
scheduling, and program-language minimality; and a deployment search-budget
model. The exercise set now has 63 problems.

The chapter source has 14,004 words. The canonical 7-by-10 print build places
Chapter 13 on numbered pages 349--386. The book check, Simplified Book English
check, and PDF build pass. The final PDF has no Chapter 13 overfull boxes,
unresolved citations, or unresolved references. A rendered contact-sheet
audit found no clipped tables, stranded headings, or broken display material.
The chapter is ready for the whole-manuscript consistency pass; Chapter 14 is
the next sequential depth target.

## Cross-chapter connections

**Back:** Chapters 6, 8, 11, and 12 supply bytes, arithmetic, observations,
equivalence, and cross-machine relations.
**Forward:** Chapter 14 turns lower-bound evidence into a trust ladder;
Chapter 15 applies the full contract to three machines; Chapter 16 separates
architectural cost models from hidden processor state.
**Through-lines:** a finite failure can support a universal lower bound only
when the language, cost, semantics, and coverage bridge are explicit.
