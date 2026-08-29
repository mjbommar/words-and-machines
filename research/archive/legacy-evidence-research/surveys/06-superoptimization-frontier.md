# Superoptimization & the optimality frontier: state of the art, 2026-08

*Produced 2026-08-27 by an Opus 5 research agent. WebSearch was unavailable for its entire run (session budget exhausted); it worked from Google Scholar via SerpApi, OpenAlex, arXiv, and author/institutional PDFs, with primary text extracted where possible. ACM DL PDFs are behind Cloudflare, so MISAAL and HieraSynth were read from abstracts plus Lu's dissertation chapter. Reproduced verbatim.*

---

## 0. The one-sentence finding

**No superoptimizer in the literature — from Massalin (1987) to HieraSynth (OOPSLA 2025) — emits a machine-checkable certificate of optimality.** Systems that prove optimality do it by exhausting a search space with solver `unsat` answers and then *discarding the refutation*. Meanwhile both halves needed exist and are mature: checkable bit-vector refutations (Lean `bv_decide`/LRAT, CoqQFBV, cvc5) and checkable *optimality* proofs for combinatorial search (VeriPB, certified MaxSAT). Nobody has joined them for instruction-sequence minimality.

The nearest precedent in any field is sorting networks: Codish et al. proved S(9)=25 by SAT, and Cruz-Filipe et al. then produced a formally verified proof of that lower bound.

## 1. Per-system dossier

### 1.1 Massalin (1987)
Exhaustive over a 68020 *subset*; the exact test scaled to **3 instructions** at ~40 programs/sec; length-12 figure is with the **probabilistic** test. **No certificate — not even of correctness**: *"Currently, superoptimizer runs without the boolean check, and the author has yet to find an incorrect program."* Pruning tables are *human-authored*. Named results: `signum` in 4 instructions; a *negative* result about reciprocal multiplication offered "as a confirmation" — Massalin already understood he was making minimality claims, with no way to back them.

### 1.2 Bansal & Aiken (2006)
Length **3** peepholes (windows of 6); 162.1 billion → 8.6 billion canonical → 3.11 billion after pruning. Equivalence by zChaff — pre-DRAT, no artifact. *"Given more resources, we can easily scale the system to length 4… Going beyond length 4 requires additional techniques."* **Soundness caveat:** subsequence-optimality pruning "is always true when we are optimizing for codesize… **For runtime optimizations, this is not true in general.**" Any latency-model certificate must not use that lemma.

### 1.3 Denali (2002)
*(Read second-hand via Minotaur §4.1 and SuperStack §6.)* Minotaur's framing: *"give the SMT solver a conjecture of the form 'No program of the target architecture computes P in at most eight cycles'… this is very heavy lifting."* Optimality relative to the supplied axiom set; certificate none. **This is the exact query shape the paper answers with a certificate** — Denali asked and threw away the refutation.

### 1.4 STOKE (2013–2017)
MCMC over x86-64. **No completeness, no optimality, no certificate.** The correct citation for "fast and clever, unverifiable."

### 1.5 Souper (2017–2025)
arXiv:1711.04422. 51 IR instructions; cost-bounded CEGIS ("optimal" = minimum over the cost-bounded enumeration for the extracted LHS). *"When a solver is wrong, Souper will also be wrong. One time we saw a program … misbehave, and the root cause was an incorrect result returned by the Z3 solver."* Synthesizes P1–P17 and P19 of Hacker's Delight; **P18, P20–P25 not synthesized.**

### 1.6 GreenThumb / LENS (2016)
Bidirectional enumerative search with selective refinement; SuperStack classifies it as using incompleteness sources 1, 2, 3 **and** 4. No optimality certificate.

### 1.7 Minotaur (OOPSLA 2024)
40+ op types plus **165 x86-64 vector intrinsics**; depth bound B=4; **k = 1 with n ≈ 250** per HieraSynth's measurement. Correctness only, via Alive2 refinement (no proof object). **No optimality claimed.** Cost model: LLVM-MCA µops. 324 rewrites, 1.061× geomean, **integer-vector rewrites contribute 75.6%** — the payoff concentrates exactly in the data-movement region.

### 1.8 MISAAL (PLDI 2025)
*(Abstract only.)* Offline rule-space pruning from formal ISA semantics; 16× compile-time reduction vs Hydride. **No optimality claim.** Evidence that even 2025 synthesis compilers moved *away* from optimality toward compile time.

### 1.9 SuperStack (PLDI 2024)
*"GASOL generally timeouts when optimizing sequences of >30 instructions, while SuperStack doubles this threshold"* (≈60); 724,336 EVM/Wasm sequences. MaxSAT; refutations discarded. **The taxonomy of five ways superoptimizers become incomplete:** (1) timeout, (2) splitting sequences, (3) weaker optimality notions (e.g. not handling memory), (4) stochastic/ML pruning, (5) dominance constraints that can lose optimality. Their scorecard: *"GASOL uses 1, 2, 3, and optionally 5; Souper uses 1 and 3; GreenThumb uses 1, 2, 3 and 4; SuperStack uses 1 and 3, and optionally 5."* They measured (5): **82 EVM sequences** where dominance constraints gave a worse objective. **This taxonomy is the single most useful citation in the survey** — the field admitting in print that "optimal" almost never means what a reader assumes.

### 1.10 HieraSynth (OOPSLA 2025) — the current frontier
Lu & Bodík, doi:10.1145/3763162; full text as Ch. 6 of Lu's UW dissertation. Decomposes on *n* (instruction-set size), preserving cost-model optimality; **"instruction sets with up to 700 instructions while synthesizing 7–8-instruction programs… previous approaches were limited to 1–3 instructions."** Bitwuzla 0.7.0, 3600 s, 72 cores. Power law for everyone else: log(k) = −0.81·log(n) + 5.10, R² = 0.862. **Certificate: none.** Five trust assumptions: bitwuzla's soundness, the Grisette encoding, their RVV semantics, lossless decomposition, sound unrealizability pruning. The word "certificate" does not appear. Named unsolved: **Min128** (found, unproven) and **SortPairsDistance1_128** (failure), both from Highway/vqsort at k ≥ 8, n ≈ 200–300; 6 of 26 vector benchmarks synthesized-but-unproven; Brahma's 12-component library "proves insufficient for optimal results in 14 of the 25." Future work: *"more parallelism might also help, we lack the resources to explore it."* Escape hatch: *"For applications requiring a definitive unrealizability proof, we can disable timeouts for leaf nodes."*

**Positioning:** concede scale immediately (k=7–8 at n≈700 vs k=2 over 5 instructions); compete on the axis they have no point on — epistemic status — and cite their own five trust assumptions.

### 1.11 CEGIS lineage and Hacker's Delight P1–P25
Brahma (ICSE 2010), Gulwani et al. (PLDI 2011) — where P1–P25 comes from; optimality only over an expert-selected component multiset. Sketch, Rosette, Metasketches/Synapse (POPL 2016) — cost-optimal synthesis, no certificate. **Status of P1–P25 today:** all solvable at small ISA sizes (HieraSynth 24/25 proven cost-model optimal at n=31–35 on RISC-V), Souper cannot do P18, P20–P25, and **nobody has produced a checkable optimality certificate for any of them on any ISA.**

### 1.12 Related SIMD-synthesis systems
Swizzle Inventor (ASPLOS'19), Diospyros ('21), VeGen ('21), Rake ('22), MACVETH, Hydride ('24), MISAAL ('25), Axon (arXiv:2606.26344, unrefereed), æSIP (ISCA'26). *"All of these works show good performance results, but they focus on relatively narrow tasks."* None claims minimality.

## 2. The certificate landscape

**Checkable correctness for BV, production-grade:** CoqQFBV (CAV 2021); cvc5 proofs (IJCAR 2022); **Lean `bv_decide` — verified bit-blasting + LRAT (OOPSLA 2025, doi:10.1145/3763167)**; width-independent BV predicates (OOPSLA 2025, doi:10.1145/3763148); verified peephole rewriting in SSA IRs (ITP 2024).

**Checkable optimality — only in SAT/PB, never applied to code:** QMaxSATpb (SAT 2022); certified symmetry & dominance breaking (JAIR 2023, doi:10.1613/jair.1.14296); certified core-guided MaxSAT (CADE 2023); certified MaxSAT preprocessing (IJCAR 2024); efficient proof logging for MaxSAT (ASE 2025).

**Precedent for certified combinatorial minimality:** Codish, Cruz-Filipe, Frank, Schneider-Kamp, *Sorting nine inputs requires twenty-five comparisons* (JCSS 2016) → Cruz-Filipe, Larsen, Schneider-Kamp, *Formally proving size optimality of sorting networks* (JAR 2017). **The shape of what this paper does, transplanted from comparator networks to an ISA.**

## 3. Frontier table

| System | Year | ISA size n | Max k proven optimal | Notion | Certificate |
|---|---|---|---|---|---|
| Massalin | 1987 | ~10–15 | 3 exact / 12 probabilistic | shortest | none (manual) |
| Bansal & Aiken | 2006 | x86 subset | **3** | cost fn | none (zChaff) |
| Denali | 2002 | Alpha | axiom-relative | cycles modulo axioms | none |
| STOKE | 2013 | x86-64 | none | none | none |
| Souper | 2017 | 51 IR | cost-bounded CEGIS | per-LHS | none |
| Minotaur | 2024 | **165 x86 SIMD** | **1** | *none claimed* | correctness only |
| SuperStack | 2024 | EVM/Wasm stack ops | **~60** | stack ops only | none |
| **HieraSynth** | **2025** | **~700 (RVV)** | **7–8** | cost-model, exhaustive | **none** |
| **[this work]** | 2026 | 5 declared AVX2 unary ops | **2** (length), **4** (cost) | length + named latency | **DRAT** |

## 4. Sixteen open problems

**OP-1** certified minimality for HieraSynth's `Min128` (months; weeks on a declared subset). **OP-2** any solution for `SortPairsDistance1_128` (months; a sat witness with replay is weeks). **OP-3** Bansal–Aiken to length 4 with a certificate — a proof-of-exhaustion problem, not proof-of-unsat (months). **OP-4** certificates for Hacker's Delight P1–P25 on a declared ISA — k=2 cases < 5 MB each, weeks; P19–P21 need certified symmetry breaking (months). **OP-5** certified minimality for the standard SIMD permutation catalogue (reversal, 16/32-bit element reversal, 8×8/16×16 byte transpose, interleave, RGB→planar, base64, UTF-8 expansion) — weeks per permutation at k ≤ 3; the paper's natural sequel. **OP-6** does AVX-512 lower the minimum? a certified ISA-delta (weeks given OP-5) — makes Massalin's ISA-design pitch rigorous for the first time in 39 years. **OP-7** certify SuperStack's 82 dominance-loss sequences with VeriPB — **lowest-hanging certified-optimality result in the survey** (weeks). **OP-8** certifying a CEGIS *refutation* with symbolic constants — **needs new theory**; the paper sidesteps it by using a constant-free subset, and should say so as a design decision. **OP-9** a proof-of-exhaustion format ("we checked every candidate") — **highest-leverage item**; every minimality claim inherits it. **OP-10** certified symmetry/dominance breaking for instruction search (port VeriPB) — months. **OP-11** a certified cost model shipped as an artifact — **weeks, nearly free, do it in the paper.** **OP-12** certified minimum-length constant-multiplication sequences (Massalin's 1987 exhaustive claims, never rechecked) — weeks. **OP-13** the 6 unproven HieraSynth vector benchmarks — "the blocker is compute, and compute is buyable." **OP-14** certified MC / gate counts of S-box components (GF(2⁴) inverter first). **OP-15** certified size-optimal Boolean chains (Knuth's table) — months, contingent on OP-10. **OP-16** an interchange format for optimality certificates ("what DRAT is for unsat") composing per-query LRAT/VeriPB + exhaustion + symmetry lemmas + cost model — months; **the natural framing of the paper's contribution: first instance produced; the open problem is the format the second instance should use.**

## 5. Recommended framing

1. Lead with SuperStack's taxonomy. 2. Concede scale to HieraSynth immediately and completely; their five trust assumptions are the axis. 3. Massalin as bookend: 1987 manual inspection; 2025 a solver's word; 2026 a file anyone can re-check. 4. Cite the sorting-network precedent explicitly. 5. Say why a unary, constant-free subset was the right choice — it is a theorem-shaped fact, not a resource limit. 6. Ship the cost model as an artifact.

## 6. What could not be verified
Denali, GreenThumb/LENS, Unbounded Superoptimization read second-hand; MISAAL abstract only; HieraSynth figure-level details from the dissertation; which HD benchmark carries the "not proven optimal" mark (p21 inferred); certificate sizes are extrapolations from the 1.9 MB datum; grey literature unrepresented.
