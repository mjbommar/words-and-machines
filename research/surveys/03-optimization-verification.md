# Open optimization instances and the verification gap — addendum

*Produced 2026-08-25 by an Opus 5 research agent. Only the agent's ADDENDUM reached the coordinator; its main report (open MIPLIB/JSP/QAP instances, quantum circuit synthesis, open decidability fragments, proof-complexity families) was not recovered. Reproduced verbatim.*

---

## A meta-finding that reframes Part A of the report

The agent checked update dates on every registry it touched. **Six of eight benchmark libraries are unmaintained, offline, or publish no status at all:**

| Registry | Last update | Consequence |
|---|---|---|
| [SteinLib](https://steinlib.zib.de/steinlib.php) | **2015-03-30** | PUC table still marks instances open that were closed by 2020 |
| [DIMACS11 Steiner](https://dimacs11.zib.de/) | news ends **2016**, bounds **2014-09-12** | Frozen |
| [sbeyer/steiner-tree-results](https://github.com/sbeyer/steiner-tree-results) | **2020-03-20** | Best public table, 6 years stale |
| [Trick's DIMACS COLOR](https://mat.tepper.cmu.edu/COLOR/instances.html) | ~2002 | Still marks `queen10_10` unknown — **settled 2004** |
| [Mascia's clique page](https://iridia.ulb.ac.be/~fmascia/maximum_clique/DIMACS-benchmark) | **2015-10-26** | Stale |
| [BPPLIB](https://site.unibo.it/operations-research/en/research/bpplib-a-bin-packing-problem-library) | undated | Publishes **no optimality status** |

Plus: **QAPLIB has had no What's-New entry since 2011-07-20**, Waterloo's VLSI TSP pages stop at **2017**, and **CVRPLIB was entirely offline all session**.

**An "open instance" claim sourced from any of these is a claim about 2011–2020, not 2026.**

## A14. Steiner tree PUC: two instances with a gap of exactly one unit

From [`steinlib.csv`](https://raw.githubusercontent.com/sbeyer/steiner-tree-results/master/steinlib.csv): **28 of 50 PUC instances open.**

| Instance | \|V\| | \|E\| | \|T\| | LB | UB | Gap |
|---|---|---|---|---|---|---|
| **cc3-10u** | 1000 | 13,500 | 50 | **124** | **125** | **1 (0.81 %)** |
| **bip52u** | 2200 | 7,997 | 200 | **232** | **233** | **1 (0.43 %)** |
| cc3-11u | 1331 | 19,965 | 61 | 151 | 153 | 2 |
| bip62u | 1200 | 10,002 | 200 | 216 | 219 | 3 |
| hc9u | 512 | 2,304 | 256 | 287 | 292 | 5 |
| hc11u | 2048 | 11,264 | 1024 | 1126 | 1144 | 18 |
| hc12u | 4096 | 24,576 | 2048 | 2234 | 2256 | 22 |

**Barrier — PUC was built to defeat what makes SteinLib easy.** `hc*` are hypercubes (**automorphism group order ~2×10¹² for hc12u**). Nothing fires in reduction tests. **Symmetry-breaking machinery was never ported from ILP to Steiner branch-and-cut**, and there is a genuine bidirected-cut integrality gap. **DRAT will explode on `hc*`** — hypercube symmetry is the canonical DRAT-hard structure. **PR/SR/DSR or VeriPB with symmetry and dominance rules is the right target; this is the clearest place where proof-system choice, not solver speed, is the bottleneck.**

## A15. Bin packing — the benchmark closed in April 2026, and not by a bigger solver

From da Silva, de Lima, Schouery, Côté & Iori, [arXiv:2604.05152](https://arxiv.org/abs/2604.05152): *"13 out of 500 AI and ANI instances remain unsolved within standard time limits"* — and the same paper closes them, with *"polynomial-time algorithms for the AI class and pseudopolynomial-time algorithms for the ANI class."* **There is no named open instance in classical one-dimensional bin packing as of this session.** AI/ANI were *designed* to be hard and defeated MIP solvers for a decade; the resolution was a structural theorem.

## A16. MIRUP — open, and shaped exactly right for a proof-carrying stack

For the Gilmore–Gomory relaxation of 1D cutting stock, MIRUP asserts `z_IP ≤ ⌈z_LP⌉ + 1`. **Open; no counterexample known.** Kartak, Kurz, Ripatti & Scheithauer ([arXiv:1405.5988](https://arxiv.org/abs/1405.5988), 2015): all instances with n ≤ 9 item types are proper IRUP; **worst known gap 1.0625** against a conjectured supremum of 2. Encodability: **Σ₂ᵖ**, natural CEGIS; exact rational `z_LP` required. **A counterexample certificate is single-digit MB, verifiable in seconds** — three independently checkable pieces. All the difficulty is in search, none in verification. Extending exhaustive coverage from n ≤ 9 to n ≤ 12–13 publishes either way.

## A17. `flat1000_76_0` — the answer provably exists and nobody can find it

1,000 vertices, 246,708 edges, **constructed to be 76-colourable**; best heuristic ~81–82. Verification is O(m). SOTA: **ZykovColor** (Brand, Faber, Held & Mutzel, [arXiv:2504.04821](https://arxiv.org/abs/2504.04821)) — CaDiCaL via IPASIR-UP with a user propagator; 94 of 137 DIMACS instances in one hour. **BPCOL+** (Zheng et al., [arXiv:2606.08356](https://arxiv.org/abs/2606.08356)) — 96 of 137.

Genuinely unknown χ: `latin_square_10`, `DSJC1000.5`, `C2000.5`, `r1000.5`, `DSJC500.5`, `DSJC1000.1/.9`, `DSJR500.5`, **queen14_14 / 15_15 / 16_16**. Trick's "?" for `queen10_10` is 20+ years stale: **χ(Q_n) for n = 2..13 is 4,5,5,5,7,7,9,10,11,11,12,13** (Vasquez 2004, OEIS A088202).

**Rate of progress, measured.** Brand & Held ([arXiv:2411.03003](https://arxiv.org/abs/2411.03003)): `r1000.1c` is *"one of the few newly solved DIMACS instances in the last 10 years."* **Two instances in a decade.** **A proven barrier:** the linear flow relaxation on exact decision diagrams **equals the fractional chromatic number**, with integrality gap O(log n) — no LP-based lower bound over this formulation can close these instances.

**Checkability — a verified gap.** *"The [ZykovColor] paper contains no discussion of proof logging, DRAT certificates, or formal verification mechanisms."* **The current SOTA chromatic-number lower bounds rest on unverified solver code, including a custom CaDiCaL propagator.** VeriPB is the right vehicle. **No published DRAT proof of any DIMACS chromatic-number lower bound was found.** `queen16_16` at k=16–17 is ~4,400 vars / ~215k clauses — the best pure SAT+DRAT candidate.

## A18. `C500.9` — an 85,000-clause CNF nobody can refute

Krpan & Povh, [arXiv:2607.11726](https://arxiv.org/abs/2607.11726) (July 2026): certified integer upper bounds **C500.9 83→73, C1000.9 122→115, C2000.9 177→168** via (k,ω^u)-core/truss peeling feeding Lovász theta. **A proven barrier:** for G(n,0.9), ω ≈ 80 at n=2000 while θ is Θ(√n) — a Θ(√n/log n) multiplicative gap inherent to the relaxation. **C500.9 at k=58 is ~85k clauses, open since the 1993 DIMACS challenge, and fits in a repository.** A checkable theta certificate is a PSD dual matrix in exact arithmetic — ~2×10⁶ rationals, a few hundred MB, verifiable in minutes. *Producing exact-rational certificates for the 2026 theta bounds: weeks.*

## A19. Set covering — probably nothing genuinely open

OR-Library's text is Beasley's from the early 1990s; modern MIP closes instances of that size routinely. The agent declined to name an open SCP instance without a recent exact-SCP paper.

## Corrections and additions to the filed report

**The one pattern, confirmed in eight libraries:** primal results are trivially and often *exactly* checkable; dual results are checked by nobody.

- **MIPLIB runs an exact GMP rational feasibility checker on every submitted solution and publishes no dual bound at all** for its 217 open instances.
- The nurse-rostering benchmark: *"It is not possible to verify lower bounds."*
- **Smoothie published a 0.0000% optimality gap on `supportcase35` that is refuted by a better feasible solution already on MIPLIB nine months earlier.**
- Waterloo offers **$1,000 to strangers** for a better mona-lisa100K tour, and **CVRPLib absorbed 1,932 anonymous BKS improvements in 30 days**, precisely because a tour is self-certifying.

**Tiers.** Tier 1 (answer provably exists): `flat1000_76_0`, `le450_25c/d`. Tier 2 (gap of one): Steiner `cc3-10u`, `bip52u`; PACE `instance200`. Tier 3 (proof-object gaps needing zero new mathematics): proof-log ZykovColor via VeriPB; exact-rational PSD certificates for Krpan–Povh; a certificate for an already-closed job-shop instance (abz07 = 656, ta51 = 2760) — **none exists for any job-shop instance, open or closed**; certify nurse-rostering Instance24's LB of 33,724.

**Two negative controls worth keeping:** `pythago7825` — infeasible, proven, machine-checked at 200 TB DRAT, **and still listed "open" on MIPLIB because no MIP solver can reproduce it.** `C500.9` at k=58 — 85,000 clauses, open since 1993.
