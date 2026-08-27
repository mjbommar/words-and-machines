# SIMD shuffle & permutation lowering: landscape and open problems

*Produced 2026-08-27 by an Opus 5 research agent (WebSearch + WebFetch + SerpApi Scholar). Reproduced verbatim. Variable counts, certificate-size estimates and difficulty ratings are the agent's derivations, not sourced numbers; it flags the model it used.*

---

## 1. The prior-art picture (and why the gap is real)

### 1.1 The one piece of genuinely adjacent prior art

**Buchwald, Mohr, Zwinkau, "Optimal Shuffle Code with Permutation Instructions"** (CC 2015; arXiv:1504.07073). The closest thing to this result in the literature, and **not the same problem**: it solves *register-allocation* shuffle code — factor a permutation of register *contents* into a minimal product of instructions that "arbitrarily permute the contents of up to five registers." Optimal, efficient — but the model is permutation-factorization over an explicitly enumerable generator set, and no certificate is produced.

**The distinction that justifies the paper:** for a generator set that is *finite and small* (Buchwald's ≤5-register permutes; LLVM's NEON operator list) you can BFS the Cayley graph and never need SAT. For `vpshufb` the control operand is a **128-bit register**, so the "generator set" has 16¹⁶ ≈ 1.8×10¹⁹ elements per operand choice. BFS is dead on arrival; a SAT encoding with the control mask as *free variables* is the only formulation that closes.

### 1.2 LLVM already does exhaustive shuffle optimality — for 4 lanes only

`llvm/utils/PerfectShuffle/PerfectShuffle.cpp` generates the `AArch64PerfectShuffle.h` / `ARMPerfectShuffle.h` tables shipped in LLVM: all shuffles of two 4-element vectors (65,536 masks, ~6,561 valid); a **fixpoint** over a hand-listed NEON operator set (`vrev`, `vdup`, `vzip`, `vuzp`, `vtrn`, `vext`, plus lane inserts added 2022); a **CSE-aware, non-additive** cost model; **no certificate**, optimal only relative to its hand-chosen operator set. Still maintained (GlobalISel port 2024; moved out-of-line June 2026, llvm/llvm-project#202617).

Two consequences: **there is no x86 equivalent** — `lowerVECTOR_SHUFFLE` is a hand-ordered heuristic cascade, so every x86 optimality question is open by construction; and **the existing tables are certifiable and possibly wrong**, because non-additive cost + hand-picked operators means fixpoint relaxation does not guarantee true-cost optimality.

### 1.3 Synthesis-based compilers that stop short of minimality

| Work | Venue | What | Why not this |
|---|---|---|---|
| **Hydride** | ASPLOS'24 | 3,557 x86/Hexagon/ARM instructions via 397 AutoLLVM IR ops | finds *a* sequence; no minimality, no certificate |
| **Diospyros** | ASPLOS'21 | equality saturation + Rosette | optimal only within the e-graph |
| **VeGen** | ASPLOS'21 | vectorizer generator | heuristic |
| **MISAAL** | 2025 | rewrite rules from ISA semantics | same |

### 1.4 Permutation-network theory

Waksman (1968): n·log₂n − n + 1 switches. Beneš. CayleyPy Growth (arXiv:2509.19162, **unrefereed**): fast Cayley-graph growth on Sₙ, conjectured diameter formulas — all with *finite* generator sets, hitting exactly the wall of §1.1. Helfgott–Seress (Annals 2014): quasipolynomial diameter bound.

**A theoretical point for the paper:** the naive entropy bound is *not* the obstruction. log₂(32!) ≈ 117.7 bits, and one `vpshufb` control mask carries 32×4 = 128 bits — enough to encode any 32-permutation. So the length-2 lower bound cannot be information-theoretic; it is purely a **lane-structure** argument. That is why it needed a solver, and the cleanest one-paragraph justification of the approach.

## 2. Evidence that LLVM lowers shuffles sub-optimally

LLVM tracker, queried 2026-08-27 (`label:missed-optimization` + `shuffle in:title` = **42 issues**). Open, most recent first:

| Issue | Date | What |
|---|---|---|
| #216906 | 2026-08-18 | [X86] fold paired post-mask users of constant-data PSHUFB |
| #203132 | 2026 | **Shuffle lowering regressions on x86** (Clang 17→18 `vblendps`→`vinsertf128`; port-5 bottleneck on Haswell–Skylake), assigned RKSimon |
| #174602 | 2026-01 | [META][VectorCombine] recursive shuffle combining |
| #167260 | 2025-11 | reassociation with variable shuffles |
| #144227 | 2025-06 | **Shuffle pyramid not eliminated: ~7 → 3** |
| #122243 | 2025-01 | AMDGPU shuffle lowering doesn't use `v_pk_mov_b32` |
| #121823 | 2025-01 | **[X86] Deoptimization of shuffle intrinsics** — user's `vpshufb+vpermd` becomes `vpshufb+vpermd+vpblendd`; GCC and MSVC do better |
| #114001 | 2024-10 | [AVX-512] decompose `vpermb` into broadcast+`vpshufb` — an explicit **1 vs 2 instruction cost dispute**, Zen 4 |
| #96754 | 2024-06 | **[X86][AArch64][RISCV] dynamic shuffle idiom** — AArch64 stack-spills element-by-element; **RISC-V fails to emit `vrgather.vv` at all** |
| #22154 | 2014-12 | **open 12 years** |

Also WebAssembly/simd#196 — *"LLVM's optimization of shuffles penalizes x64 codegen"* by breaking v8's pattern matching. **Bottom line: LLVM demonstrably lowers shuffles sub-optimally, it is publicly tracked, and nobody can say by how much — because there is no lower bound to compare against.**

## 3. Encoding-cost model (used for every estimate below)

State: `k+1` levels × 32 lanes × one-hot tag; n² vars/level. Control operands per step (one-hot): `vpshufb` 512, `vpermd` 64, `vpermq` 16, `vpalignr` 16, `vperm2i128` 8, selector 5 → ~620/step. ~16k transfer clauses/step (vpshufb-dominant). Depth 1 ≈ 2.7k vars / 50k clauses; depth 2 ≈ 4.3k / 100k; depth 3 ≈ 6.0k / 150k. Extrapolating 1–2 orders of magnitude per level: **depth 2 → 0.1–50 GB DRAT, depth 3 → likely needs symmetry breaking.**

**The lever that decides most difficulty ratings:** instructions with *immediate* control (`vpermq`, `vperm2i128`, `vpalignr`) give a finite generator set → **meet-in-the-middle BFS**, SAT only to certify layer closure. Instructions with *register* control (`vpshufb`, `vpermd`, `vpermb`, `tbl`, `vrgather`) **must** be SAT. The hybrid is the most publishable technical contribution after the results.

## 4. Open problems

### Tier 1 — tractable now (weeks)

**P1. Exact length-diameter of the AVX2 unary subset on S₃₂.** Is 2 the diameter? ∀π∃seq is a 2-QBF or a symmetry-reduced per-target sweep. Months; the aggregation certificate is the hard part.

**P2. Cost-diameter under the named latency profile.** Cost- and length-minimality diverge (three `vpshufb` at cost 3 beat `vpermd+vpshufb` at cost 4) — **itself publishable**, and it answers #114001 in kind. Weeks for specific π.

**P3. Is `_MM_TRANSPOSE4_PS` (8 instructions) minimal?** 4×4 transpose of four xmm; canonical 4×unpck + 4×shufps = 8 over {shufps, unpcklps, unpckhps, movlhps, movhlps, blendps, pshufd}. **Everyone believes 8 is optimal; nobody has proved it.** 16 tags, 4 registers, ~2.5k vars at depth 8; requires register-file state (the main engineering step for P3–P6). **Weeks. Start here.**

**P4. Is the 24-instruction AVX 8×8 transpose minimal?** Long-running SO dispute (vblendps port balancing). 64 tags, ~100k vars; depth-23 refutation likely infeasible directly. fgiesen's "three passes" argument is a per-pass bound, **not** an instruction bound — do not conflate; page 403'd, unverified. Months; a certified *cost* bound at fixed depth is weeks.

**P5. Certify (or refute) LLVM's shipped `AArch64PerfectShuffle` table.** ~6,561 entries, 8 tags, ~300 vars each, embarrassingly parallel; per-entry DRAT 1 KB–10 MB. **Best effort-to-impact ratio in this document**; a headline if any entry is suboptimal.

### Tier 2 — months

**P6. Settle #114001 (`vpermb` vs broadcast+`vpshufb`) with a certificate.** A live compiler decision blocked on a cost question. Microarchitecture-parameterized — the profile becomes a named parameter of the theorem.

**P7. Arbitrary 64-byte permutation on AVX-512BW without VBMI** (SKX/CLX). Folklore 4–6; no bound. Entropy again non-binding (log₂64! ≈ 296 < 2×256).

**P8. RISC-V RVV cost-minimal shuffles under the LMUL² model.** The RISC-V Optimization Guide publishes the cost model *as a conjecture* ("likely proportional to LMUL²"). LLVM currently fails to emit `vrgather.vv` for the dynamic idiom (#96754). VLEN=256 reuses the 32-lane infrastructure directly — **cheapest ISA port; strong second-ISA candidate.**

**P9. WASM `i8x16.shuffle` → x64.** ARM64 does it in one `tbl2`; x64 has no equivalent. A table of certified minimal x64 lowerings for v8's canonical set (`simd-shuffle.h`) is immediately actionable by three browser engines. 16 tags, two sources — **cheapest per shuffle. Weeks.**

**P10. 3-way deinterleave (RGB→planar) on AVX2/AVX-512.** NEON does it in one `vld3`; x86 8–12 instructions, no consensus. 96 tags; needs decomposition — a stress case for composing certified lemmas.

**P11. SVE/SVE2 vector-length-agnostic reversal and transpose.** `TBL` is not VLA. Parametric in VL (128–2048): per-VL SAT plus a kernel-checked induction — **where the Lean kernel earns its place.**

### Tier 3 — theory where a certified answer would be new

**P12. Beneš/Waksman lower bounds transferred to lane-restricted SIMD.** The reduction from switch/stage counts to instruction counts has never been made rigorous for lane-restricted ISAs. Needs new theory; **highest-value item** — converts per-instance certificates into a general bound.

**P13. Certified Cayley-graph diameters for immediate-controlled subsets.** {`vpermq`, `vperm2i128`, `vpalignr`} generate a concrete finite subgroup of S₃₂ — BFS-able, exact diameters with layer-closure certificates. **Weeks; cheapest genuinely new mathematics here.**

**P14. Does cost-minimality diverge unboundedly from length-minimality?** Bounded by max/min latency (3) for a fixed set; the real question is growing n with richer ISAs.

### Tier 4 — application-driven

**P15. Base64 shuffles (Muła–Lemire)** — weeks; "certified minimum matches hand-tuned code" or a quotable miss. **P16. UTF-8→UTF-16 expansion shuffles (simdutf)** — turns Keiser–Lemire's measured "less than one instruction per byte" into a theorem. **P17. AVX2 emulation of `vpcompressb`** — a ∀-mask uniform-minimality claim; most technically interesting encoding. **P18. GPU `prmt` / DPP sequences** — NVIDIA `prmt`: 16 output bytes / 4 per instruction ⇒ ≥4; is 4 achievable for all? SCALE's Jan 2026 post makes no optimality claims. Weeks.

## 5. Recommendations

1. **P3** (4×4 transpose). 2. **P5** (PerfectShuffle table). 3. **P9** (WASM→x64). 4. **P13** (exact diameters). 5. **P6** (#114001 with a certificate — strongest evidence certified minimality is *useful*).

**Framing:** the reversal result is a *lower bound nobody could previously state*, in a domain where the literature reports measured upper bounds. Entropy does not obstruct; lane structure does. Immediate-controlled generators are BFS-able; register-controlled ones are not — the cleanest justification that SAT is *necessary* here.

**Honesty flags:** fgiesen unverified; CayleyPy unrefereed.
