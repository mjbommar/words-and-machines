# Open finite/combinatorial problems for a SAT/SMT + proof-kernel stack

*Produced 2026-08-25 by an Opus 5 research agent using WebSearch/WebFetch. Reproduced verbatim, including its own unverified-item flags. Bounds are as of the sources cited on that date.*

---

Two framing points before the list, because they change which problems are worth your time:

- **The asymmetry that matters for you.** For almost every problem here, a *positive* answer is a small object (a matrix, a coloring, a block list) that a 50-line independent checker verifies in milliseconds — a perfect fit for a trusted-kernel story. A *negative* answer needs an UNSAT proof, and the calibration points are brutal: Boolean Pythagorean Triples = 200 TB DRAT (68 GB compressed), Schur Number Five = >2 PB, Keller dimension 7 = hundreds of GB. If your differentiator is *checkable evidence*, the positive-witness problems are where you can win in weeks; the UNSAT problems are where you need the proof infrastructure to be the product.
- **Beware the 2026 preprint flood.** Several arXiv items surfaced (e.g. 2608.11211 on Conway-99, 2604.27645 on 3×3 matmul additions, 2605.01120 on Zarankiewicz, 2512.24061 on ES(7)) read as unrefereed, possibly machine-generated, and none of them resolve anything. Treat them as noise, not as the frontier.

## Tier 1 — best fits: small encoding, tiny positive witness, real open question

### 1. Binary q-analog of the Fano plane, S₂[2,3,7]
Does there exist a set of 381 planes of PG(6,2) such that every one of the 2667 lines lies in exactly one of them? Open for every prime power q; the automorphism group of such a design must be trivial (Braun–Kiermaier–Nakić 2015; Kiermaier–Kurz–Wassermann 2017), so the prescribed-automorphism lever is provably unavailable. **SAT instance is small**: 11,811 Boolean variables, 2,667 exact-cover constraints. Positive certificate: a 381-line list, ~30-line checker. Nobody has published a serious modern cube-and-conquer attack. *Positive side: months. Full resolution: years.* **Top pick.**

### 2. Three mutually orthogonal Latin squares of order 10
2 ≤ N(10) ≤ 6. arXiv:2509.09633 reproduced Delisle–Myrvold's 11,700 CPU-hour enumeration **in under 2 hours on a desktop** with a SAT encoding. 3,000 cell variables. Positive certificate: three 10×10 arrays, fully constructive. *Weeks-to-months to run; years to resolve.*

### 3. Conway's 99-graph: srg(99, 14, 1, 2)
**4,851 Boolean variables** — the smallest instance in this report. arXiv:2604.23037 reports off-the-shelf SAT cannot handle it. Negative needs UNSAT modulo graph isomorphism — not a plain DRAT object. *Years; the field expects a new encoding or certificate format.*

### 4. Rank of 3×3 matrix multiplication: is 22 possible?
19 ≤ R(⟨3,3,3⟩) ≤ 23. Heule–Kauers–Seidl found families of rank-23 schemes via SAT; ~500 solvers thrown at rank 22 without resolution. **A published, tuned SAT encoding exists.** Positive certificate is a kernel-checkable algebraic identity (expand and compare 81 coefficients). Adjacent: 4×4 over GF(2) below 47; provable lower bound above 19.

### 5. Minimum Kochen–Specker system in dimension 3
24 ≤ n ≤ 31. Lower bound raised 22→24 by SAT+CAS with isomorph-free orderly generation (Li–Bright–Ganesh, IJCAI 2024). **Hybrid**: SAT enumerates orthogonality hypergraphs; each candidate needs a nonlinear-real realizability check. Seven values in the gap, each independently publishable. **Single best fit for a stack combining SAT with real arithmetic and a proof kernel.**

## Tier 2 — genuinely open, plausible with serious effort

### 6. R(3,10): 40 or 41?
Upper bound 42→41 by Angeltveit (arXiv:2401.00392, 2024). DS1 rev. 18 (Jan 2026). Naive independent-10-set constraint is C(40,10) ≈ 8.5×10⁸ clauses — the encoding problem. Precedent: Li–Duggan–Bright–Ganesh, *Verified Certificates via SAT and CAS for R(3,8) and R(3,9)* (IJCAI 2025, arXiv:2502.06055). *Months, plausibly.* **If you want a Ramsey number, this one — not R(5,5).**

### 7. R(4,6) ∈ [36, 40]
C(39,2) = 741 variables; K₄-free C(39,4) ≈ 82k clauses; independent-6-set C(39,6) ≈ 3.3M — **the full CNF fits in memory**, unlike R(3,10). Improving the lower bound by one graph is a bounded, checkable increment.

### 8. Erdős–Szekeres ES(7) = 33?
ES(6) = 17 verified by SAT in 8.53 CPU seconds with Heule–Scheucher's O(n⁴) encoding (arXiv:2403.00737). ES(7) open. *Years; watch it.*

### 9. Optimal binary code A(17,4) ∈ [2816, 3276]
**Smallest completely open case** in Brouwer's tables. Upper bound is a Delsarte LP bound — **a rational certificate, small, exactly checkable.** Lower-bound side movable: Rosin (arXiv:2603.00174) improved 24 constant-weight entries with tabu search. *Weeks to attack; years to close.*

### 10. Chromatic number of the plane ≥ 6
509-vertex Parts graph (2020) is the smallest known 5-chromatic unit-distance graph. Generation half has resisted eight years; colouring-test half is solved technology. *Needs construction ideas first.*

### 11. Crossing number of K₁₃ ∈ {223, 225}
Binary decision with a small witness on one side. Under-attacked by the SAT community.

### 12. Earth–Moon problem: biplanar chromatic number ∈ [9, 12]
No progress on either endpoint in 45 years. Epoch AI notes *"verifying that chromatic number exceeds 9 may become computationally infeasible for large graphs"* — the certificate is the bottleneck.

## Tier 3 — open, well-defined, but scale or missing theory

### 13. Schur S(6), WS(6) ≥ 646
S(5)=160 needed >2 PB. Lower bounds: weeks, trivially kernel-checkable witness; WS(6) moved 582→642→646 in five years.

### 14. Pythagorean triples with three colours
Completely open. Extending the known 3-colouring record: weeks, trivially checkable. Full resolution needs theory.

### 15. Folkman F_e(3,3;4) ∈ [21, 786]
Upper bound unchanged 14 years. Positive certificate is a small graph **plus an UNSAT proof that it arrows (3,3)** — exactly the witness+refutation shape. *Months.*

### 16. Multicolor Ramsey: R(3,3,5) etc.
Only R(3,3,3)=17 and R(3,3,4)=30 known. Wesley (arXiv:2509.03784) showed SAT search for *structured* colourings is productive. **Lower bounds: weeks. Most reliably harvestable Ramsey lane.**

### 17. Rado numbers for specific equations
Chang–De Loera–Wesley (ISSAC 2022, arXiv:2210.03262); symbolic-set follow-up (arXiv:2505.12085). Both-direction certificates small. **Best flywheel-throughput domain on the list.**

### 18. Zarankiewicz z(m,n;3,3)
12×22: 264 variables, ~1.4M clauses. Both directions LRAT-checkable. *Weeks.* (2026 preprints on this read as LLM-assisted; verify.)

### 19. Optimal sorting network size S(13)
Known through n=12. Lower-bound certificate format exists (Harder 2020, Isabelle-checked). *Needs a new symmetry-breaking lemma first.*

### 20. Queen domination γ(Q_n), n=20
n=19 resolved by proof-producing SAT (arXiv:2508.11945). *Weeks.*

### 21. (3,13)-cage: 202 ≤ n(3,13) ≤ 272
Smallest open trivalent case; record graph 272 (Hoare). Girth constraints favour lazy clause generation / SMT over pure CNF. *Months for a record improvement.*

### 22. Kissing number in dimension 5 ∈ {40..44}
Not SAT — SDP + exact rational rounding. **"Exactify an SDP certificate" sub-problem is weeks and broadly reusable.**

### 23. Packing 11 unit squares s(11); Heilbronn n ≥ 10
Continuous with combinatorial structure; the QF_NRA lane. **Unusually well-matched to an SMT stack; MIP competitors do not produce checkable certificates.**

## Tier 4 — famous, do not lead with these

**24. R(5,5) ∈ [43, 46]** (Angeltveit–McKay 2024) — needs new theory. **25. Hadamard order 668** — apparently resolved by construction in 2026 (Alpöge et al., unpublished); **target the verification, not the problem.** **26. Costas arrays 32/33** — 45,000 processor-years estimated; needs an algebraic idea. **27. Projective plane of order 12** — needs new theory. **28. Perfect 1-factorization of K₁₂₈.** **29. Golomb rulers OGR-29** — no compact certificate format for exhaustive optimality; *skip unless inventing the format*. **30. No-three-in-line** — live and fast-moving (n=76 by Heule, Aug 2026); racing Heule directly.

## Where to put effort

**One trophy with a small witness:** #1 or #2. **SMT-with-proofs demonstration:** #5, then #23. **Measured throughput:** #17 and #18, then #16 and #20. **Largest checkable-evidence flex:** #15. **Avoid:** R(5,5), S(6), Costas, plane of order 12, Golomb.

**Checks not completed:** current S(6)/vdW bounds; the 3-colour Pythagorean record; R(3,3,5) against DS1 rev. 18 (chain traces to 2006); La Jolla Covering Repository (DNS failure); current S(13) bounds; OGR-29 status.
