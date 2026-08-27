# 05. Certify bounds that nobody has ever certified

**One-line:** across optimization, every *primal* result is checked rigorously and every
*dual* result is checked by nobody — an unoccupied niche that is this repository's stated
thesis, needing zero new mathematics.

| | |
|---|---|
| Statement | Produce machine-checkable certificates for published lower bounds that currently rest on solver authority |
| Known | no certificate exists for any of the targets below |
| Gap | not a numeric gap — a missing artifact class |
| Encoding | varies: exact rational LDL^T, VeriPB, DRAT |
| Positive certificate | n/a — the certificate *is* the deliverable |
| Effort | weeks (theta bounds) to months (proof-logging a solver) |
| Risk | **low** — no new mathematics, and failure is informative |
| Audience | MIPLIB, DIMACS, the SAT/CP proof-logging community, and any referee |

## The asymmetry, measured

The optimization sweep found this from six directions at once:

- **MIPLIB runs an exact GMP rational feasibility checker on every submitted solution and
  publishes no dual bound at all** for its 217 open instances.
- A nurse-rostering benchmark says it in plain text: *"It is not possible to verify lower
  bounds."*
- **No machine-checkable certificate exists for any job-shop instance — open or closed.**
- The state-of-the-art graph-colouring lower bounds (ZykovColor,
  [arXiv:2504.04821](https://arxiv.org/abs/2504.04821)) rest on a **custom CaDiCaL user
  propagator with no proof logging of any kind**. The sweep checked the paper directly: no
  discussion of proof logging, DRAT, or formal verification anywhere in it.
- A 2026 paper published a **0.0000% optimality gap that is refuted** by a better feasible
  solution which had been sitting on MIPLIB for nine months. The authors flagged the risk;
  nothing caught it.
- Meanwhile Waterloo can offer **$1,000 to strangers** for a better TSP tour and CVRPLib
  absorbed **1,932 anonymous improvements in 30 days** — precisely because a tour and a
  route are self-certifying.

The pattern is exact: **self-certifying results attract crowdsourced verification; dual
bounds attract none, because there is nothing to check.**

## Why this is the strategic pick

This repository's identity is *untrusted fast search, trusted small checking*, and its own
`CLAUDE.md` argues at length that **a checker which cannot fail is worse than no checker**.
Lane 05 is that argument applied outward instead of inward.

It also has a property none of the other four have: **failure is informative and publishable.**
If a certificate cannot be produced for a published bound, that is a finding about the bound.
Targets [01](01-rado-schur-frontier.md) through [04](04-simd-shuffle-minimality.md) all fail
silently — you run out of compute and learn nothing.

## Targets, in rising order of effort

### 5a. Exact-rational PSD certificates for the Krpan–Povh clique bounds — weeks

Krpan & Povh ([arXiv:2607.11726](https://arxiv.org/abs/2607.11726), July 2026) improved the
best certified upper bounds on three DIMACS max-clique instances whose clique numbers are
unknown — the largest movement on max clique in a decade:

| Instance | Vertices | Was | Now | Gap to LB |
|---|---|---|---|---|
| `C500.9` | 500 | 83 | **73** | 16 |
| `C1000.9` | 1000 | 122 | **115** | 47 |
| `C2000.9` | 2000 | 177 | **168** | 88 |

The bounds come from Lovász theta on a reduced graph, rounded with error control. A
**checkable** theta certificate is a PSD dual matrix in exact arithmetic — rational `LDL^T`,
or interval arithmetic with a verified positive-definiteness margin. At `n = 2000` that is
roughly 2x10^6 rationals, a few hundred MB, verifiable in minutes.

This turns three published numbers into three checkable objects. It is the cheapest real
contribution in this document.

*Note the proven barrier, so nobody wastes time trying to close the gaps instead:* for
`G(n, 0.9)`, `ω ≈ 80` at `n = 2000` while the Lovász theta function is `Θ(√n)`. That is a
proven `Θ(√n / log n)` multiplicative gap — the 168-vs-80 spread is inherent to the SDP
relaxation, not numerics. Escaping it needs Lasserre level ≥ 3, whose SDP has dimension
`n^3 = 8x10^9`. Infeasible. **Certify the bounds; do not try to improve them.**

### 5b. First certificate for a job-shop instance — weeks

`abz07 = 656` and `ta51 = 2760` are *closed* — the optimum is known and agreed. No
machine-checkable certificate exists for either, or for any other job-shop instance.

Starting with a closed instance is the right move: the answer is known, so the certificate
can be validated against ground truth. It is a pure artifact contribution with no
mathematical risk at all.

### 5c. Proof-log ZykovColor's chromatic lower bounds via VeriPB — months

The highest-value and hardest of the three. [VeriPB](https://gitlab.com/MIAOresearch/software/VeriPB)
natively supports symmetry and dominance breaking, which is exactly what a Zykov-tree solver
needs and exactly what DRAT cannot express.

The obstacle is structural and worth understanding before committing: ZykovColor's encoding
uses `s_uv` ("same colour") variables with `O(n^3)` transitivity constraints — `10^9` at
`n = 1000`, which **cannot be encoded and must be propagated**. The custom propagator is what
makes the solver work and what makes it unverifiable. Proof-logging a user propagator is the
actual research content here.

Context for how slowly this field moves: Brand & Held
([arXiv:2411.03003](https://arxiv.org/abs/2411.03003)) describe closing `r1000.1c` as *"one
of the few newly solved DIMACS instances in the last 10 years."* Two instances in a decade.

### 5d. Certify a bound its own maintainers call unverifiable — weeks

Nurse-rostering Instance24's lower bound of 33,724 is published alongside a statement that
lower bounds cannot be verified. Producing a certificate for exactly that number is a
pointed, self-contained demonstration.

## Fit against this stack

- **5a** needs exact rational linear algebra at 2000x2000. The CAS is `i128`-backed with a
  BigInt escape hatch only inside the GCD/PRS inner loop — **this is a real collision and must
  be checked first.** Rational `LDL^T` on a 2000x2000 matrix will produce large intermediate
  coefficients. Either confirm the BigInt path covers it or plan to widen it.
- **5b/5d** are mostly encoding and bookkeeping; the existing evidence envelope
  (`Evidence::check_outcome`, three-valued) is the right shape.
- **5c** needs a VeriPB emitter, which does not exist here. That is the months.
- Nothing in this lane needs the proof-producing SAT core to be fast, which sidesteps the
  "warm or proof-carrying, never both" constraint that binds every other target.

## What "done" looks like

A committed certificate, an independent checker that shares no code with the producer, and a
`checker_command` whose exit status depends on the finding — not on the run completing. Then
the same thing the field does with tours: publish it where the maintainers can see it.

The strongest version of this deliverable is **two** certificates: one for a bound that is
correct, and one attempt on a bound that turns out not to be. The second is worth more.

## What would kill it

**It is not a new theorem, and that may not be what you want.** Every other target in this
folder produces a number mathematics did not have. This one produces an *artifact* for a
number mathematics already has. If the goal is `external_status: open` flipping to a result,
this lane does not deliver it — the fact ledger would record these as `proved`/`proved` with
a new `proof_route`, not as novelty.

Be honest about that before picking it. It is the strategically strongest option and the
weakest one for the specific framing of "new mathematics".

**Secondary: 5a may hit the `i128` ceiling immediately.** Check this before anything else —
build a rational `LDL^T` on a few hundred rows of the `C500.9` theta dual and watch the
coefficient growth. If it overflows, the target becomes "widen the CAS to BigInt", which is
useful work but is not this project.

**Tertiary: 5c's propagator problem may be the whole thing.** Proof-logging a solver whose
correctness depends on an unlogged custom propagator is not a porting exercise. Scope it as
research, or start at 5a and 5b.

## Sources

- [Krpan & Povh, arXiv:2607.11726](https://arxiv.org/abs/2607.11726) — the 2026 theta bounds
- [ZykovColor, arXiv:2504.04821](https://arxiv.org/abs/2504.04821) — SOTA colouring, no proof logging
- [BPCOL+, arXiv:2606.08356](https://arxiv.org/abs/2606.08356) — branch-and-price, 96 of 137
- [Brand & Held, arXiv:2411.03003](https://arxiv.org/abs/2411.03003) — "two instances in a decade"
- [VeriPB](https://gitlab.com/MIAOresearch/software/VeriPB) — pseudo-Boolean proof logging with symmetry and dominance
- In-tree: `crates/axeyum-solver/src/evidence.rs`, `scripts/check-claim-certificates.py`
