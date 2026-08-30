# Chapter 8 research contract

**Scope:** Fixed-width integer arithmetic and logic, the facts retained as
condition state, and the bridge from mathematical laws to ISA rules, circuits,
compiler contracts, and proof evidence
**Target capacity:** 12,000--16,000 words, governed by the obligations below
**Compelling question:** When a finite machine produces one result word, which
mathematical facts were lost, which were retained, and who is allowed to rely
on them?

## Close-up subjects

1. One width-four addition in each carry/overflow quadrant.
2. One gate-level full-adder derivation and one carry-propagation comparison.
3. One subtraction read as a modular result, unsigned order, and signed order.
4. One A0 flag-producing sequence with a later flag-reading suffix.
5. One RV64I comparison sequence and one x86-64 condition-code sequence.
6. One two-limb carry-chain proof that composes local identities.
7. One compiler example where a no-wrap promise enables a transformation.
8. One checked, wrapping, saturating, and trapping policy comparison.

## Three lenses

| Lens | Depth | Required content |
|---|---|---|
| Origins | Medium | positional and binary arithmetic; mechanical carrying; Boolean switching; stored condition codes; signed multiplication; the development of faster carry networks; distinguish mathematical ideas, circuits, and published architectures |
| Foundations | Deep | rings modulo powers of two; widened arithmetic and Euclidean division; signed interpretation; carry, borrow, and overflow; Boolean algebra and full adders; comparisons; shifts and rotations; multiplication/division boundary cases; flag projections, liveness, and observational equivalence |
| Industry and economics | Deep | delay, area, switching energy, wiring, and verification tradeoffs; multiprecision and cryptography; checked/wrapping/saturating language policies; compiler no-wrap facts; condition dependencies and instruction selection; packed arithmetic and accelerator boundaries |

## Coverage routing

| Neighboring topic | Route |
|---|---|
| Word encodings and interpretations | Use here; Chapter 1 owns the base definitions |
| Instruction operands and state transition | Use here; Chapters 2--3 own the general framework |
| Branch execution | State predicates here; Chapter 9 owns control transfer |
| Procedure-level arithmetic routines | Motivate here; Chapter 10 owns ABI mechanics |
| Equivalence and refinement | Use one local context; Chapters 11--12 own the general theory |
| Candidate costs and minimality | Name arithmetic costs here; Chapter 13 owns search objectives |
| Evidence manifests | Specify arithmetic evidence here; Chapter 14 owns the full trust ladder |
| Floating point, vectors, timing, and side channels | Mark the boundary here; Chapter 16 owns extensions |

## Questions the chapter must answer

1. Why does modular arithmetic describe stored integer results without claiming ordinary integer equality?
2. Why are unsigned carry and signed overflow independent facts?
3. How do subtraction carry and borrow conventions differ?
4. Why do (Z), (N), (C), and (V) require instruction-specific write policies?
5. How do Boolean gates implement one-bit addition, and why does carry propagation affect delay?
6. When do (N\ne V), (\neg C), and (Z) recover signed order, unsigned order, and equality?
7. Which shift-count, shifted-out-bit, and division cases require separate rules?
8. How do multiplication and division expose high products, remainders, and exceptional inputs?
9. How can hidden flags, explicit Boolean registers, and direct comparisons carry the same fact?
10. When may a compiler ignore or exploit overflow behavior?
11. Why do checked, wrapping, saturating, and trapping arithmetic serve different products?
12. What must Axeyum enumerate, solve, replay, mutate, and record before claiming the rules are checked?

## Feature inventory

- [x] Sourced history from binary arithmetic and switching logic through
      condition codes, signed multiplication, and parallel carry methods.
- [x] Exact modular, unsigned, signed, and widened readings for core operations.
- [x] Gate-level half-adder/full-adder derivation and carry-network tradeoff.
- [x] Complete A0 arithmetic, logic, shift, and condition policies in scope.
- [x] Source-pinned RV64I and x86-64 arithmetic/condition comparisons.
- [x] Multiplication, division, rotation, saturation, and packed-operation boundaries.
- [x] Flag liveness, contextual observation, and replacement counterexamples.
- [x] Language and compiler overflow contracts with optimization consequences.
- [x] Physical delay, area, wiring, energy, and verification stakes.
- [x] Multiprecision and constant-time/security stakes without timing overclaim.
- [x] Honest Axeyum substrate audit and staged artifact obligation.
- [x] At least 40 exercises across execution, proof, break, history, circuit,
      design, compiler, economics, security, Axeyum, and cross-ISA transfer.

## Chapter audit

Depth pass completed 2026-08-30, subject to the final whole-book audit. The
chapter has 12,000 source words and 47 exercises. It runs from printed page 191
through page 223 in the current 8-by-10-inch print build. The PDF build,
Simplified Book English check, prose check, bibliography resolution, and
chapter-local overfull-box inspection pass. A rendered-page review covered the
opening, modular algebra, counted overflow proof, multiplication and division,
software policy, and both closing exercise spreads.

## Cross-chapter connections

**Back:** Chapters 1--7 supply finite words, state, operands, byte movement,
program traces, decoding, and locations.
**Forward:** Chapters 9--10 consume conditions in branches and routines;
Chapters 11--14 state and check arithmetic equivalence; Chapters 15--16 apply
the rules and expose timing, vector, and floating-point boundaries.
**Through-lines:** the result word is only one projection of an arithmetic
event; every retained or discarded fact has mathematical, physical, and
software consequences.
