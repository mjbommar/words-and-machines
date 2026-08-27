# Open-problem targets, August 2026

Five candidate targets for producing a **genuinely new mathematical result** with this
stack — one where `external_status` says mathematics does not know the answer, not one
where mathematics knows and we have not formalized it.

Assembled 2026-08-25 from four parallel sweeps: three literature surveys (finite
combinatorics; engineering and industrial mathematics; optimization and verification) and
one read-only survey of this repository's measured capability.

Pick **one**. Each file is self-contained and ends with a `What would kill it` section,
which is the part to read first when choosing.

## The decision table

| # | Target | Gap | Encoding | New result? | Effort | Risk |
|---|---|---|---|---|---|---|
| [01](01-rado-schur-frontier.md) | Rado / off-diagonal Schur frontier cells | open-ended | 10^3–10^4 vars | yes, incremental | days–weeks per cell | **low** |
| [02](02-bilinear-f2-p6.md) | `R_F2(P_6)` = 16 or 17 | **1** | ~7k vars, ~50k clauses | yes, single bit | weeks | medium |
| [03](03-sbox-optimality-trio.md) | S-box gate-complexity, three gap-1 intervals | **1** each | 10^3–10^4 vars | yes, first-of-kind certificate | weeks | medium |
| [04](04-simd-shuffle-minimality.md) | Minimal AVX2 shuffle sequences | unmeasured | few 10^3 vars | yes, nothing published | weeks | medium-high |
| [05](05-certification-lane.md) | Certify bounds nobody has certified | n/a | varies | new *artifact*, not new theorem | weeks–months | **low** |

## The one structural fact behind all five

Three independent literature sweeps converged on this without being asked to look for it:

> **Improvement verifies in milliseconds. Optimality almost never verifies at all.**

A better circuit, a shorter tour, a valid colouring, a rank-22 scheme — you replay the
object, no solver in the loop. The other direction cost 2 PB for Schur number five and
200 TB for Boolean Pythagorean triples, and for most *published* lower bounds no
certificate format exists in the first place.

There are exactly three shapes where the negative direction is also cheap:

1. **Univariate nonnegativity on an interval.** Sum-of-squares is *complete* here via
   Markov–Lukács — no degree bound to guess, no relaxation gap, certificate is exact
   rational.
2. **SDP infeasibility with a rational dual ray.** One small rational matrix and one
   inner product; sometimes smaller than the positive certificate.
3. **Small pure-SAT instances.** DRAT falls straight out of a proof-producing CDCL core,
   which this repository already has.

Targets 02, 03 and 04 are all shape 3. Target 05 is shape 2. Target 01 is shape 3 at a
scale where checking, not searching, is the binding cost.

Reject anything that fits none of the three shapes unless you are only chasing the
positive direction.

## Three constraints from this repository, measured

Read these before believing any effort estimate.

**Checking costs more than searching.** The `R_4(5(x-y)=3z) = 625` run emitted 220,077,720
DRAT steps / 19.9 GB in 8,762 s of search, then took **14,500 s to check** — the claim's own
notes say so. The fp16 add-monotonicity miter is worse in ratio: 24 s of search producing
193 MB, then over three hours in `check_drat` plus LRAT elaboration. Certificate
*production* is fast; certificate *checking and elaboration* is what fails to terminate.

**Backward checking costs 6.6–10x proof size in RAM**, measured, against an assumed 1.5x
(ADR-0426). A host with 26 GiB cannot re-check a 5 GB proof, and the way it finds out is
the OOM killer — which is indistinguishable from a refuted claim.

**Warm or proof-carrying, never both.** The fast default is the batsat adapter, which emits
nothing. The proof-producing CDCL core has **no assumption interface**, so cubes enter as
root-level unit clauses with no learned-clause reuse and every cube pays full startup.

## What a result here lands as

Not a kernel theorem. Enumeration and int-blast reconstruction routes are
`StructuralAttestation` — modules that assert `axiom P` and `axiom ¬P` and contain none of
the reasoning they attest to (29 of 65 routes). A new result lands as a **checked claim**
in [`artifacts/claims/`](../../artifacts/claims/README.md), the way the existing 21
`novelty: new` entries did, or as a fact under
[the fact schema](../../artifacts/ontology/fact.schema.json).

That is sufficient for a novelty hunt and insufficient if the goal is to close the
kernel arrow of the flywheel. Decide which you are doing before picking.

## A warning about the sources

The optimization sweep checked update dates on every benchmark registry it touched.
**Six of eight are unmaintained, offline, or publish no status at all** — DIMACS COLOR
still marks an instance unknown that was settled in 2004; QAPLIB's last update was 2011;
SteinLib still lists instances closed in 2020. An "open instance" sourced from any of them
is a claim about 2011–2020.

This applies to the files in this folder too. Every bound here is as of 2026-08-25 and
inherits its source's staleness. **Re-verify currency before committing effort**, and if a
source turns out to be stale, fix the file rather than working around it.

One inversion makes the point: classical one-dimensional bin packing has *no* named open
instance as of April 2026. The AI and ANI classes were built to be hard, defeated MIP
solvers for a decade, and then fell — not to a bigger solver, but to a structural theorem
showing the restricted problem is not strongly NP-hard, followed by a polynomial-time
algorithm. A benchmark can measure the wrong thing for ten years.

## Related

- [`PLAN.md`](../../PLAN.md) — generated; current queue and resume protocol
- [`docs/research/08-planning/roadmap.md`](../research/08-planning/roadmap.md) — phase exit criteria
- [`docs/research/08-planning/foundational-dag.md`](../research/08-planning/foundational-dag.md) — check before adding public surface
- [`artifacts/claims/DASHBOARD.md`](../../artifacts/claims/DASHBOARD.md) — generated; the 21 `novelty: new` claims and 3 frontier records
- [`docs/research/09-decisions/`](../research/09-decisions/README.md) — close a target choice with an ADR
