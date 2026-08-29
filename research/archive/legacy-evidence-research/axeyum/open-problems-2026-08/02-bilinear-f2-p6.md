# 02. Bilinear complexity of 6-term binary polynomial multiplication

**One-line:** a single unknown bit, `R_F2(P_6) ∈ {16, 17}`, in a formula of ~7k variables,
underneath GHASH and every post-quantum code-based KEM.

| | |
|---|---|
| Statement | Minimum number of bilinear multiplications over `F_2` to multiply two degree-5 binary polynomials |
| Known | lower bound **16** (Wang 2026); upper bound **17** (Montgomery 2005) |
| Gap | **1** |
| Encoding | ~7k variables, ~30–60k clauses after Tseitin |
| Positive certificate | expand and XOR-compare 396 entries |
| Negative certificate | DRAT, plausibly GB scale |
| Effort | weeks with a good encoding |
| Risk | medium — symmetry, not size, is the wall |
| Audience | TLS/NIC vendors, PQC implementers, ZK circuit designers |

## The problem

`R_F2(P_n)` is the minimum number of bilinear multiplications needed to compute the product
of two degree-`(n-1)` polynomials over `F_2`. Schoolbook needs `n^2`; Karatsuba-style
formulae do better. Exhaustive results settle `n ≤ 5`
([Barbulescu et al., eprint 2012/110](https://eprint.iacr.org/2012/110);
[Covanov, arXiv:1705.07728](https://arxiv.org/abs/1705.07728)).

At `n = 6` the interval is `[16, 17]` and has never been closed.

## Neighbouring open cells

The same 2026 paper leaves a table of them. If `P_6` proves too hard, these are the fallbacks
— and `⟨2,3,4⟩` is *smaller*, so it is the right warm-up regardless:

| Instance | Interval | Gap |
|---|---|---|
| `⟨2,3,4⟩` matrix mult | `[19, 20]` | **1** |
| `P_6` | `[16, 17]` | **1** |
| `C_8` cyclic | `[19, 22]` | 3 |
| `P_7` | `[19, 22]` | 3 |
| `T_9` truncated | `[21, 26]` | 5 |
| `P_8` | `[21, 26]` | 5 |
| `⟨3,3,4⟩` | `[25, 29]` | 4 |

## Why it is still open

Naive enumeration over rank-1 tensors over `F_2` is roughly 8.1M candidates; choosing 16 of
them is hopeless without symmetry breaking. The symmetry group is large — independent
changes of basis on each of three factors, plus permutation of the 16 terms — and standard
symmetry breaking is incomplete.

**Nobody has thrown a modern SAT solver at the existence side.** The lower bound came from a
new algebraic framework, not from search.

## Encoding

The engineering sweep worked the numbers: 368 primary variables plus 576 and 6,336 auxiliary,
with 396 XOR-equations over 16 terms. **~7k variables, ~30–60k clauses after Tseitin.**

That is small by this stack's standards. `INPROCESS_MAX_CLAUSES` is 16,000,000; the
`WORD_ROUTE_MAX_NODES` cap of 200,000 is not in play. The difficulty is entirely search,
which is the regime where a CDCL core with good symmetry breaking earns its keep.

## Certificates

**Positive (a 16-multiplication scheme exists).** Expand the bilinear form and XOR-compare
396 coefficients. Microseconds, and checkable by a 40-line program with no solver in it.
This is a kernel-checkable algebraic identity, and it would be an excellent demonstration
for a proof-producing stack.

**Negative (`R_F2(P_6) = 17`).** DRAT straight out of the proof-producing core. On a
~50k-clause instance the proof is plausibly GB-scale — well inside what this repository has
already produced and checked, and roughly an order of magnitude below the Rado run.

## The precedent to imitate

Chengu Wang's `R(⟨3,3,3⟩) ≥ 20` over `F_2`
([arXiv:2603.07280](https://arxiv.org/abs/2603.07280), final version 2026-07-30) is the
first improvement on Bläser's 2003 bound at that format, and the *process* matters more
than the result:

> ~40 minutes to search on a laptop. Verifies in seconds. **Independently re-verified by a
> third party who wrote a checker from scratch in a different language.**

That is untrusted search and trusted checking, already demonstrated in exactly this domain,
by someone who is not us. It is the closest external validation of this project's thesis
found anywhere in the survey.

## Fit against this stack

Good, with one thing to build:

- Size is comfortable — no admission-control cap is near.
- The proof-producing CDCL core (`crates/axeyum-cnf/src/proof_sat.rs`) is the right engine,
  and its DRAT output feeds `check_drat_backward` directly.
- **What is missing: symmetry breaking.** This is the whole difficulty of the instance, and
  the repository has no general symmetry-breaking machinery. Expect to write it, and expect
  that to be most of the work.
- Beware inprocessing: BVE is enabled up to 16M clauses and emits RAT steps, which
  **cannot be expressed in LRAT** (`LratError` says so explicitly). If an LRAT-elaborable
  proof is wanted, inprocessing must be disabled.

## What "done" looks like

Either direction is publishable and both are small:

- **16 exists** — a scheme file, a 40-line checker, a claim with `novelty: new`. This is the
  outcome that gets used: it drops straight into GHASH and PQC implementations.
- **17 is optimal** — a DRAT certificate, backward-checked in-tree, and the first
  machine-checked bilinear-complexity optimality result at this size.

Warm up on `⟨2,3,4⟩ ∈ [19,20]`, which is smaller and has the same shape. If the encoding
cannot close that, it will not close `P_6`.

## What would kill it

**Symmetry breaking turns out to be the whole problem.** This is the honest risk. The
instance is small and has resisted attention precisely because the search space collapses
only under a good symmetry argument. If a generic solver plus naive lex-leader breaking does
not bite, the project becomes "invent symmetry breaking for bilinear tensors", which is
research, not engineering, and is not what the effort estimate above covers.

**Test for this early:** run `⟨2,3,4⟩` at `k = 19` first. If that does not close in
reasonable time with the symmetry breaking on hand, stop and reconsider — the estimate
above is void.

**Secondary:** if inprocessing is left on for speed, the proof is DRAT-only and cannot be
elaborated to LRAT. That is acceptable (DRAT is checked in-tree) but it limits external
re-verification to tools that accept DRAT.

## Sources

- [Wang, *Lower bounds for bilinear complexity over F2*, arXiv:2603.07280](https://arxiv.org/abs/2603.07280)
- [Barbulescu et al., eprint 2012/110](https://eprint.iacr.org/2012/110) — exhaustive results for `n ≤ 5`
- [Covanov, arXiv:1705.07728](https://arxiv.org/abs/1705.07728)
- Montgomery, *Five, six, and seven-term Karatsuba-like formulae*, IEEE Trans. Computers 2005 — the 17
- Downstream consumers: GHASH (`GF(2^128)`, every TLS stack and NIC offload), Classic McEliece / BIKE / HQC inner loops
