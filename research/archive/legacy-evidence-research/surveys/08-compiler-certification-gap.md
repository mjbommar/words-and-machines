# The certification gap in compiler optimization — final

*Produced 2026-08-27 by an Opus 5 research agent; three parallel investigations consolidated. Quotations are from primary text (HTML or `pdftotext`). Pre-2020 work flagged with year; preprints and non-archival venues flagged. Reproduced verbatim.*

---

## 0. Four corrections

**C1 — There is a published antecedent that closed the shuffle-minimality gap, and the paper must position against it.** Franchetti & Püschel, *Generating SIMD Vectorized Permutations*, **CC 2008** (users.ece.cmu.edu/~franzf/papers/cc08.pdf) has exactly the two-layer structure the paper argues for, and closes it: Layer 1 — "dynamic programming with backtracking, which finds the optimal solution **within the space of possible solutions spanned by the rewriting rules**." Layer 2 — Floyd's exact block-transfer count "yields **a lower bound on the number of binary vector instructions** required to perform a stride permutation… On SSE2 and on Cell the corresponding instruction counts **match the lower bounds… and are hence optimal**." Scope: three classes of *stride* permutations, SSE2 and Cell SPU; **no per-instance machine-checkable artifact** — verified by reading Floyd's theorem. So "nobody has ever proven a SIMD shuffle sequence minimal" is **false**. **The correct novelty claim: certified minimality for general permutations on a current ISA, with a machine-checkable artifact per instance** — a defensible delta on all three axes. Cite it as the antecedent you extend.

**C2 — "Nobody certifies minimality" is false in the tractable half.** Ramos, Hulak, de Queiroz, *Checking Equality-Saturation Merge and Extraction Certificates*, **AFP, July 2026** (Isabelle/HOL): "a formal proof establishes **minimum additive cost** over every term represented by the designated class" — **for the polynomial tree-cost case only.** The NP-hard DAG-cost case has no certificate anywhere. **Revised claim: the tractable half is certified; the hard half is not.**

**C3 — E-graph extraction is worse than NP-hard.** Goharshady, Lam, Parreaux, OOPSLA 2024 Distinguished Paper: "hard to approximate within any constant ratio."

**C4 — The one system called "the first certifying equality saturation engine" certifies the wrong thing.** Flatt, Coward, Willsey, Tatlock, Panchekha, FMCAD 2022 certifies **equalities**; its "optimal" refers to **proof size**. *(Also: VeGen is ASPLOS 2021, not CGO.)*

## 1. The thesis, restated

Every combinatorial compiler backend claiming optimality establishes it by trusting a solver, and none emits a checkable certificate. Every neighbouring community has built the machinery — DRAT/LRAT (SAT), VIPR (MIP), VeriPB (PB), DRCP (CP), PB lower-bound certificates (planning) — with **formally verified checkers** (`cake_lpr`, `cake_vipr`, CakePB, GRAT, `FznDrcpCheck`) and **measured overheads as low as median 2.7%.** The word "certificate" already has a weaker meaning here: Unison uses it for **the solver's self-reported optimality gap**; SLOTHY's "auditable" means **human-traceable**; FMCAD 2022's "optimal" means **proof size**.

## 2. Map: certified vs. claimed

| Layer | Certificate required? | Format | Checker verified? |
|---|---|---|---|
| SAT Competition (Main) | **Yes, since 2013/14; invalid proof ⇒ disqualification** | DRAT/DPR/LRAT; VeriPB 2025–26 | `cake_lpr` yes, GRAT yes |
| Pseudo-Boolean Competition | Optional, separately ranked since 2024 | VeriPB | CakePB yes |
| MIP / MIPLIB | **No** — feasibility only | VIPR exists, unused | `cake_vipr` yes, outside MIPLIB |
| SMT-COMP | **No** — exhibition 2022–23; absent 2024–26 | Alethe/CPC/LFSC | Carcara not verified |
| MaxSAT Evaluation | **No** — zero mentions of "proof" in 2026 rules | — | — |
| MiniZinc / XCSP3 | **No** — self-reported flag | — | — |
| Classical planning | Yes (research) | PB lower-bound certs | Isabelle/AFP yes |
| Sorting networks | Yes (research) | lower-bound derivation | Coq/Isabelle yes |
| E-graph extraction, tree cost | **Yes (AFP 2026)** | DP witness | Isabelle yes |
| E-graph extraction, DAG cost | **No** — ILP status flag | — | — |
| Verified compilers | correctness yes; optimality **deliberately excluded** | Coq/HOL | n/a |
| Translation validation (Alive2, Arrival) | correctness yes | SMT refinement | n/a |
| Superoptimizers | equivalence yes; minimality not claimed | — | — |
| **Combinatorial backends** | **claimed optimal, nothing certified** | — | — |
| **Cost models** | **no guarantee of any kind** | — | — |

**Certification tracks decision problems, not optimization problems.**

## 3. The base rate: how often "proved optimal" is wrong

**CP, 2016.** Gange, Chu, Stuckey, *Certifying Optimality in Constraint Programming* (2023) — an author of MiniZinc and Chuffed, about his own community: *"when a solver returns that it has proved optimality, how confident can we be in this result? The short answer is not very."* *"In the 2016 challenge, 7 of the 22 submitted solvers still reported at least one incorrect result (5 solvers incorrectly claiming optimality)."*

**CP, 2021.** Gocht, McCreesh, Nordström, CP 2022: *"at least 45 out of 3,500 claimed solutions were incorrect (either through falsely claiming unsatisfiability or optimality…)… not limited to one solver, one problem, or one global constraint."*

**CP, 2025.** MiniZinc Challenge news: *"2026-01-14 — Amendment made to the results to fix an issue with undetected incorrect optimality claims."*

**MIP.** MIPLIB 2017 §4.7: the `bc1` incident — *"The eighth solver cut off the optimal solution"* — and *"the definition of 'the optimal objective value' for a problem instance is ambiguous."* 328 (or 334 — the paper disagrees with itself) instances removed for cross-solver inconsistency. Footnote 8: on one instance *"two solvers agree on the optimal solution value although the instance should mathematically be infeasible."*

**Why cross-solver agreement cannot substitute:** it caught `bc1` and missed the two-solvers-agree case; XCSP3 codifies the blind spot (a solver is wrong only if a better solution "exists" *and someone finds it*). Compilers share a handful of backends and cost models, so correlated error is the expected case. MiniZinc docs: *"When a solver claims to prove optimality, we cannot easily verify this claim without solving the problem again."*

## 4. Combinatorial backends

**Unison** — the best data point. Gecode + Chuffed via MiniZinc, 15-min limit, 100 functions: *"the percentage of functions solved optimally ranges from 44% to 79%"*; Hexagon *"81% of the functions are proven optimal."* Cost model admitted: *"assumes a processor with constant instruction latencies."* The payoff: *"17.7% of the functions are actually slowed down (down by 11.1%), contradicting Unison's estimation"*; *"overestimates the actual speedup for 71% of the functions"* that err. **Ablation on an ideal Hexagon without pipeline stalls:** slowdowns 17.7% → 3.8%; Spearman 0.70 → 0.89 — *"the dynamic processor behavior is the sole responsible for overestimation."* **81% proven optimal; 17.7% slower on silicon. Both true.**

Also: Blindell's universal instruction selection — *"potentially optimal (w.r.t. the model)"*, proves to 1415 nodes, warns model-optimal "may still be inferior"; OptSched; goSLP ("pairwise optimal"); SLOTHY (TCHES 2024 — optimal "with respect to a model of the target (micro)architecture", OR-Tools CP-SAT, no export). Headroom check: list scheduling already achieves 98.9–99.6% optimal on single-issue basic blocks; the live claims are in *integrated* RA+scheduling, VLIW, SIMD synthesis.

**The supply side that never crossed over:** Gocht/McCreesh/Nordström CP 2022 (8.4–61× slowdown, proofs 10–100+ GB) → Flippo et al. CP 2024, **DRCP** (overhead "often less than 10%") → CP 2026 Rocq-verified checker for infeasibility *and* optimality → **Pumpkin**, a pure-Rust CP solver emitting DRCP with a verified checker, cumulative and disjunctive constraints, medalling at MiniZinc 2026 — **never pointed at a compiler.**

## 5. Correctness certified, minimality excluded by design

**CompCert already runs the paper's architecture, for the wrong property.** Monniaux (arXiv:2312.08117) on CompCert's AArch64 peephole optimizer: *"An untrusted oracle proposes a new instruction sequence; its result is validated by performing symbolic execution on both the original and modified sequences."* **And the exclusion is deliberate** — Yang, Shirako, Sarkar, OOPSLA 2024: *"Our scheduler… abstracts away the outside scheduling heuristic as a universal parameter so it is flexible to modify without touching any correctness proof."*

Superoptimizer table (Massalin — probabilistic test, no cert; Denali — UNSAT at k−1 *is* the proof, **discarded**, with a completeness obligation admitted unproved since 2003; Bansal–Aiken length 3; Gulwani component-multiset; Optgen — "complete up to cost k" is a property of a run, not an artifact; Swizzle Inventor — "first solution found is often optimal," verifier sound-but-incomplete; Rake — "Sub-optimal Sketches" section; Souper; Minotaur — explicitly none; Hydra; SuperStack). **No superoptimizer in any year emits a machine-checkable minimality proof** — three independent passes with positive controls.

**The standard blocks it:** SyGuS-IF 2.1 defines `optimize-synth` but says its objective does "not impact correctness" and "We do not define the correctness of an infeasible response."

**Equality saturation:** egg's own words — optimal only "with respect to the given rewrites"; SPORES has the one rule-completeness proof and then trades optimality for compile time; non-saturation reintroduces phase ordering (Hartmann et al., PACT 2024); Tensat's "globally optimal" is over a cycle-filtered e-graph; Cranelift's aegraph retrospective (2026 blog): cost-based extraction nets "~0.1%… in the noise."

## 6. Cost models: the load-bearing weakness

BHive (IISWC 2019) Table IV: **llvm-mca 25–28% average error** on Ivy Bridge/Haswell/Skylake; IACA 16–18%; Ithemal ~10%; OSACA 33–36%. Three findings that matter more: (1) accuracy is corpus-relative by 65× — uiCA 0.45% on BHive, **29.59%** on CesASMe; (2) ranking is what an optimizer consumes and ranking is worse — CesASMe Kendall τ 0.57–0.59 (≈21% of pairs ordered wrongly); DiffTune improves MAPE while degrading τ; (3) optimality claims are LLVM-version-relative — AnICA: **23% inconsistency between llvm-mca 9 and 13.** Models are structurally partial: uops.info has no port mapping for 67% of Zen schemes; a 2026 WiP reports port assignment depending on the *data*. Wilhelm & Reineke (ERSA 2024): *"Formal verification of the soundness is infeasible in the absence of formal models of the underlying execution platforms"* — and propose "WCET certificates" as future work. **The sound-cost-model people are asking for this paper's artifact.**

## 7. Benchmarks and the SIMD-shuffle picture

**No compiler-optimization benchmark suite records an optimum.** Certificate scale: PB Competition 2024 proof logging **median 2.7% overhead, median 1.43× checking**; one VIPR certificate tightened 10 GB → 8 kB; Pythagorean triples ~200 TB; Schur Five ~2 PB; empty hexagon streamed LRAT to `cake_lpr`. Exact MIP in production (SCIP 10.0): 6.8–10.8× slowdown.

**Unifying insight: optimality certification is a lower-bound problem, and every lower bound is an infeasibility claim.** Every domain that succeeded reduced "no smaller solution exists" to SAT/CP UNSAT and logged it.

**LLVM's shuffle lowering, from the source** (`X86ISelLowering.cpp` at main, 2026-08-27): `MaxShuffleCombineDepth = 8`; **~38 hand-written `lowerShuffleAs*` strategies tried in fixed order, first match wins**; in-source *"FIXME: We will currently miss some cases."* No search, no objective, no lower bound. Tracker: `label:missed-optimization shuffle` = **144 issues, 72 open, 51 backend:X86.** McFarlin–Arbatov–Franchetti–Püschel (ICS 2011): shortest-sequence search as binary matrix factorization, "four billion variants of the unary LRB shuffle alone," exhaustive search "about 10²⁹ years," pruning by "a **likely** lower bound." Two clean negatives: no minimality work for AVX-512 or NEON; no measurement of LLVM's shuffle counts against a known optimum.

## 8. Twelve open problems

1. **Minimal-length SIMD shuffles on a modern ISA with a checkable lower bound** — extend Franchetti–Püschel from stride/SSE2 to general/AVX-512, Floyd → DRAT. Weeks.
2. **One proven instance of "LLVM emits N, the optimum is M."** Denali's *"to the best of our knowledge, this five cycle program is optimal"* is what needs replacing. Weeks for ten entries.
3. **Are any of Minotaur's rewrites minimal?** Artifact public. Weeks–months.
4. **Discharge Denali's completeness obligation and emit the refutation.** The field has been one flag away since 2002. Months.
5. **Certify one Unison schedule.** FlatZinc route into Pumpkin exists. **The single most compelling available result** — converts a published optimality claim into a checked one. Months.
6. **Point Pumpkin at any compiler problem.** Weeks. Highest result-per-effort.
7. **Certify a SLOTHY schedule.** The crypto community already demands machine-checked artifacts. Months.
8. **Certify a Blindell selection optimum or an OptSched B&B result.** Months.
9. **The x86 inversion study** — how often `cost_M(a) < cost_M(b)` while `time_hw(a) > time_hw(b)`. Largest empirical gap in the area. Weeks–months.
10. **Certified optimality under a sound cost model** — needs the verified metric-to-cycles transfer theorem. New theory.
11. **A certificate format for "no shorter program exists"** binding ISA semantics + instruction pool + cost function + UNSAT proof, with **the cost model named inside the certificate.** Sub-items: wire superoptimization to VeriPB; certify DAG-cost extraction; make exhaustive enumeration replayable; fix SyGuS-IF. Months. **Most durable contribution.**
12. **A MIPLIB for compiler optimization, plus non-vacuity for its checker.** Fixed discrete objective; two certificates per entry; best-known vs proven ledger; mandatory-certificate tier on small instances; a negative-control corpus the checker must reject. **Mutation testing cannot find a missing guard** — the right test is an adversarial fixture over a *satisfiable* instance. Months.

## 9. What a CGO / PLDI / ASPLOS reviewer will find compelling

**Rank 1** — OP-1 and OP-5 as a pair, with Franchetti–Püschel positioned correctly (**do not claim first-ever proven-optimal shuffles**). **Rank 2** — the base rate (§3): Stuckey's sentence does more work than any argument the paper could make. **Rank 3** — cost-model honesty (§6): state plainly that a certificate certifies optimality relative to a model, and give the measured distance from model to machine; put it in the paper, not the rebuttal. **Rank 4** — the certificate format, with affordability pre-answered (median 2.7%). **Rank 5** — the CompCert framing as the opening: the architecture is not novel; the property is.

**Two things to avoid.** Do not claim certified-optimal code is faster — Unison's data contradicts it. Do not claim minimality certificates are unprecedented — AFP tree-cost (2026) and Franchetti–Püschel (2008) exist. **Claim the checkable artifact for the hard case.**

## 10. Caveats
WebSearch exhausted early; WebFetch summarizes PDFs unreliably (it fabricated a title once) — every quotation is from direct extraction. Verify before citing: MIPLIB's 328-vs-334; Koehler et al.'s 2-of-7 table; whether Maroneze's verified WCET tool has the microarchitectural layer inside the Coq proof; the exact year SAT's proof requirement moved to the Main track; Kudriavtsev & Kogge full text. Non-refereed: Stepp 2011, Harder 2020, EGRAPHS 2023, Fallin's blog, DiffTune-Revisited, Yang & Sergey 2026. Not investigated: addition chains, SMTCoq status, whether OR-Tools CP-SAT emits proofs.
