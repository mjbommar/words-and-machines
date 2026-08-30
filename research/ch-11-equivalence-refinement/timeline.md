# Chapter 11 historical timeline

| Date | Development | Contribution to this chapter | Caution |
|---|---|---|---|
| Early programming era | programmers hand-transform and optimize instruction sequences | replacement creates an implicit behavior-preservation promise | examples and testing are not universal equivalence proofs |
| 1960s | formal semantics and assertion methods develop | programs receive mathematical meanings; control points carry propositions | no single paper created every later notion of equivalence |
| 1967 | Floyd publishes “Assigning Meanings to Programs” | rigorous basis for correctness, equivalence, and termination arguments over flowcharts | later simulation and compiler-validation frameworks add machinery |
| 1969 | Hoare publishes an axiomatic basis for programming | preconditions and postconditions support local and compositional reasoning | a Hoare triple is not automatically a symmetric equivalence statement |
| 1970s--1990s | operational semantics, simulations, bisimulations, and refinement calculi mature | relations compare states and behavior sets across abstraction levels | proof-rule direction and completeness depend on the semantic model |
| 1998 | Pnueli, Siegel, and Singerman formulate translation validation | check the result of each compiler run rather than prove the whole compiler | validator semantics and coverage become part of the trusted route |
| 2000s | CompCert demonstrates realistic machine-checked compiler preservation | end-to-end semantic preservation becomes an implemented engineering object | theorem scope, source subset, target, and trusted base remain explicit |
| 2010s--2020s | SMT-backed optimization verification and Alive2 deployment | industrial compiler changes can be checked and wrong transforms produce small witnesses | bounded loops, unsupported features, timeouts, and evolving IR semantics limit conclusions |
| Current | compiler, binary-translation, JIT, crypto, and verification systems use different observations | equivalence affects correctness, compatibility, security, performance work, and maintenance cost | “same output” remains too weak until behavior and observation are named |

## Narrative sequence

1. Optimization begins as a practical replacement promise.
2. Mathematical semantics makes the promise stateable.
3. Preconditions and assertions make proofs local enough to compose.
4. Relations and simulations connect different states and abstraction levels.
5. Compiler correctness asks for preservation across a transformation chain.
6. Translation validation checks one produced result and returns actionable
   counterexamples.
7. Modern tools make observation choice, undefined behavior, solver scope, and
   replay part of both technical assurance and engineering cost.
