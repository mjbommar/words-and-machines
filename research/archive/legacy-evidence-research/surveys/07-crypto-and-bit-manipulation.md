# Certified minimality in cryptographic engineering and bit manipulation: 20 open problems

*Produced 2026-08-27 by an Opus 5 research agent (WebSearch, WebFetch, IACR ePrint, SerpApi Scholar, local `pdftotext`). Reproduced verbatim with its flags: `[OLD]` = pre-2020, `[PREPRINT]` = unrefereed.*

---

## 0. The landscape, in one table

**In cryptographic engineering, "optimal" is almost always a synonym for "best we found."** Four narrow counterexamples:

| Work | What it proves | Certificate shipped? |
|---|---|---|
| Turan & Peralta 2014 `[OLD]`; Çalık–Turan–Peralta 2018 — MC of all ≤6-variable Boolean functions (150,357 affine classes; max 6) | exact MC | **No** — exhaustive enumeration, asserted |
| Soeken, arXiv:2005.01778 `[PREPRINT]` | SAT-based exact MC, 5-input classes | **No** |
| Jia, Cui, Ling, He, Hu, Sun, Wang — *How Small Can S-boxes Be?*, ToSC 2025(1) / ePrint 2025/386 | **minimum area of optimal 4-bit S-boxes: 11 GE, depth 3** (UMC 180nm) | **No** — SAT-aided, UNSAT side unpublished |
| Zhao et al., *Parallel Assembly Synthesis*, LOPSTR 2024 | "guaranteed to synthesize the shortest program"; HD benchmarks at 2–5 instructions | **No**; concedes heuristics "may not be minimized" |
| Peralta, Circuit Minimization Work | "SAT solver proved that neither function has a circuit with 6 XOR gates" | **No** |

**That is the entire published frontier of proven minimality in this area. Every one asserts an UNSAT with nothing a referee can re-check.**

**The verified-crypto stack proves correctness, never cost:**

- **CryptOpt** (Kuepper et al., PLDI 2023): *"The task is split between **finding** performant program variants and **checking** that they have preserved program behavior. The former works via random search, and the latter via a formally verified program-equivalence checker… the random-search procedures need not be trusted."* Docs: "We do not claim these are the optimal implementations."
- **Fiat Cryptography**, **HACL\***, **Jasmin/EasyCrypt** — functional correctness, memory safety, constant-time. No cost claim.

**"CryptOpt proves the code is right; we prove nothing shorter exists" is the paper's one-line positioning.**

## Group A — SIMD shuffle model

**P1. Minimum shuffle count for one AES round in the `pshufb`/`tbl` model (vpaes).** Best: **15 byte permutations per round** (Denis, *AES gets swizzled*, 2026-07 blog; re-deriving Hamburg CHES 2009). Shipping in OpenSSL `vpaes-x86_64.pl`. **Lower bound: none. Nobody has ever asked.** QF_BV over 128-bit; certificate DRAT, low MB. **Weeks. Strongest single follow-on to the AVX2 result.**

**P2. AVX2 vector rotate: is 3 instructions minimal for r ∉ {8,16,24}?** Folklore: 1 for r∈{8,16} (`vpshufb`), 3 otherwise. ChaCha20 uses r ∈ {16,12,8,7}. Nobody has ruled out 2 for r=7 or 12. Tiny; certificate KB. **Days — the paper's warm-up table**, plus a clean AVX-512 (`vprold`) comparison.

**P3. Keccak ρ/π lane permutation on AVX2; bit-interleaving on RV32.** RISC-V adds `zip`/`unzip` *specifically* for the SHA-3 interleave and publishes no instruction count for the alternative. (b) weeks.

## Group B — Bitsliced cipher linear layers

**P4. Is the fixsliced AES linear layer minimal? (27 XOR + 16 ROT)** Adomnicai & Peyrin (TCHES 2021 / ePrint 2020/1123), Table 1: classical bitsliced 780 ops vs fixsliced 372 over 4 rounds; round-3 MixColumns alone is "27 XORs and 16 rotations." No lower bound. RustCrypto has an open issue asking for fixslicing. Months; MixColumns-only weeks.

**P5. Fixsliced GIFT-128 linear layer: 42 nibble rotations minimal?** TCHES 2020(3). `NIBBLE_ROR` = 3 instructions; proving 3 minimal is days; the "42" is a re-representation claim, months / new theory.

**P6. PRESENT pLayer / arbitrary bit permutations: SWAPMOVE stage count.** Real theoretical anchor: Benes needs 2·log₂n − 1 = 11 stages for n=64 (Lee–Shi–Yang 2001; Shi–Lee 2003 `[OLD]`); no bound in the general instruction model. Weeks–months.

## Group C — Gate-model minimality

**P7. Minimum XOR count of AES MixColumns — no lower bound has EVER been published.** 88 XOR (Jean, ePrint 2026/1481 `[PREPRINT]`); descent 94→92→91→89→88 over a decade (Kranz et al. ToSC 2017; Xiang et al. ToSC 2020). **Only the trivial ≥32.** You do not need to close the gap: **a certified "≥55" would be the first nontrivial lower bound in the literature.** Months; **highest-prestige item.**

**P8. Multiplicative complexity of the Ascon/Keccak χ₅ S-box.** Best 5 ANDs (the χ construction). No tight lower bound (single-output 5-var MC ≤ 4; vectorial case open; Bilgin et al. ToSC 2020's ≥2n−3 needs max degree, which χ lacks). **Excellent encodability** — inside Soeken's exact-synthesis frontier. Certificate small DRAT. **Ascon is NIST SP 800-232; AND count is the masking/MPC/FHE cost unit.** **Weeks — best ratio of citability to effort.**

**P9. MC of the AES S-box (32 AND, Boyar–Peralta 2010–12, unbeaten) and of its GF(2⁴) inverter (5 ANDs).** (a) out of reach; (b) in reach now. Weeks for (b).

**P10. Re-derive "11 GE minimum for optimal 4-bit S-boxes" with a certificate, then 5-bit.** The strongest exact-minimality claim in symmetric crypto, refereed, prestigious, currently unfalsifiable; the addendum (ePrint 2025/961) is not an erratum. **Replication-with-certificate: weeks. Top candidate.**

## Group D — RISC-V bit manipulation: an entire uncertified standards document

**P11. Certified minimum RV32I/RV64I sequence length for every Zbb/Zbkb/Zbs/Zbkx instruction.** **Nothing is published.** The current B spec and Zbkb doc give qualitative motivations (`orc.b` for `strlen`; `zip` "useful for implementing SHA3 on a 32-bit architecture") and **not one instruction count.** Targets easiest first: `andn/orn/xnor` (2), `rori` (3), `min/max`, `sext.b/h`, `rev8`, `orc.b`, `clz/ctz`, `cpop`, `pack`, `brev8`, `zip/unzip`, `xperm4/8`, `clmul`. **Best ISA on Earth for this**: ~40 instructions, no flags, register-register, formally specified; constants handled by a declared immediate pool, which is itself an honest, statable model. **Weeks for a 6–10 row table. Top recommendation for the paper's centrepiece.**

## Group E — Hacker's Delight bit tricks

**P12. 32-bit bit reversal.** Warren `reverse.c.txt`: best routines 17 ops = 25 full RISC instructions. No lower bound; superoptimizers never reached this length (PASSES/Aquarium 2024 prove minimality only at 2–5). Declare a mask pool. Weeks. **P13. 32-bit popcount** — ~15 basic RISC (verify against `pop.c.txt`); RISC-V `cpop` makes it 1. **P14. Magic-number division** — native QF_BV, 2–4 instructions; **days; the paper's smallest reproducible example.** **P15. PEXT/PDEP emulation (ZP7)** — months at 64 bits; weeks at 8/16.

## Group F — Addition chains: the cleanest published gap between best-known and proven

Schönhage: `l(n) ≥ log₂n + log₂ν(n) − 2.13`. Best-known from Brian Smith's reference page, which says: *"We have no proofs that the addition chains presented here are optimal. In fact it is almost certainly the case that at least a couple of the ones presented here are not optimal."*

| Exponent | ν | Best known (S+M) | Schönhage floor | Gap |
|---|---|---|---|---|
| secp256k1 `p−2` | 249 | 255+14 = **269** | **262** | **7** |
| NIST P-256 | 128 | 255+11 = **266** | **261** | 5 |
| NIST P-384 | 318 | 383+13 = **396** | **391** | 5 |
| Curve25519 `2²⁵⁵−21` | 253 | 254+11 = **265** | **261** | **4** |
| BLS12-381 seed `0xd201000000010000` | 6 | 63+5 = **68** | **65** | **≤3** |

*(Floors are the agent's own arithmetic; recompute before publishing.)*

**P16. Curve25519 inversion: is 265 optimal?** Arguably the most-executed addition chain on the internet. Unrestricted: out of reach (exact `l(n)` tabulated only to small n; `addchain` is heuristic — it beat the human on the Curve25519 *scalar* chain, 283 vs 284). **Tractable restriction:** fix the squaring backbone and ask for the minimum number of non-doubling steps — QF_BV-encodable. Months. **P17. secp256k1 (gap 7), P-256, P-384** — note libsecp256k1 moved main inversion to safegcd. **P18. BLS12-381 seed: 64 bits, weight 6 — small enough to *settle*, not just bound.** Months, genuinely settleable; who cares: blst, Ethereum consensus.

## Group G — Masking

**P19. Minimum randomness for d-probing-secure multiplication, d ≥ 5.** Belaïd et al. EUROCRYPT 2016: linear lower bound, constructions matching only for d ≤ 4. ∀∃ — needs QBF or bounded expansion. Months / encoding research. **P20. Minimum AND count for a d-th-order masked Ascon/AES S-box** — downstream of P8: settling χ₅ = 5 ANDs immediately certifies masked cost at every order.

## Recommended shortlist (weeks)

1. **P11** RISC-V Zbb/Zbkb certified table — centrepiece. 2. **P2** AVX2 rotates — days, warm-up. 3. **P8** χ₅ MC — weeks, cascades into masking. 4. **P10** replicate 11 GE with a DRAT — purest thesis demo. 5. **P14** magic division — days. 6. **P1** AES round in the `pshufb` model. 7. **P9(b)** GF(2⁴) inverter ≥ 5 ANDs.

**Months:** P4, P6, P12, P13, P16-restricted, P18, P3(b), P15-restricted. **Needs new theory:** P7 (to 88), P9(a), P16/P17 unrestricted, P19.

## Two framing points

1. **The strongest foil is CryptOpt, not a compiler.** It argues in a PLDI paper for untrusted search plus trusted checking, then checks only correctness.
2. **The field's few exact-minimality results are exactly the ones a certificate would protect** — 11 GE, the 6-variable census, Peralta's "SAT solver proved" — none checkable by a referee, believed because the authors are trustworthy. That is the precise failure mode the architecture removes, available at 4- and 5-bit sizes today.

**Caveats.** HD popcount count, ZP7 count, and blst's seed chain length unverified to the digit; Schönhage floors are the agent's computation; three PDFs (CryptOpt, Maximov–Ekdahl, Parallel Assembly Synthesis) quoted via `pdftotext`.
