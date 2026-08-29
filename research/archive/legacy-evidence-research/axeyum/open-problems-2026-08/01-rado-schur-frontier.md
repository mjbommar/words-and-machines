# 01. Rado and off-diagonal Schur frontier cells

**One-line:** keep turning the one pipeline in this repository that has already produced
new mathematics, at the exact cells its own ledger names as next.

| | |
|---|---|
| Statement | Determine `R_k(E)` for named equations `E` and colour counts `k`, and `S(3; a,b,c)` for untried triples |
| Known | 21 values already established here; 3 frontier records name the next cells |
| Gap | open-ended — a supply of instances, not a single bit |
| Encoding | `kn` Booleans, one clause per (solution, colour); 10^3–10^4 vars |
| Positive certificate | a colouring — `n` trits, checked in one pass |
| Negative certificate | DRAT, GB scale, already produced and checked in-tree |
| Effort | days to weeks per cell |
| Risk | **low** — the pipeline is built, exercised, and gated |
| Audience | small (additive combinatorics), plus a Nullstellensatz proof-complexity connection |

## The problem

For an equation `E` and `k` colours, `R_k(E)` is the least `n` such that every `k`-colouring
of `{1..n}` contains a monochromatic solution to `E`. Off-diagonal Schur numbers
`S(3; a,b,c)` are the analogous quantity for `x + y = z` with per-colour clique bounds.

Most `(E, k)` pairs have never been computed. This is a *volume* opportunity rather than a
single hard target.

## What this repository has already done

[`artifacts/claims/DASHBOARD.md`](../../artifacts/claims/DASHBOARD.md) carries **104 claims**
across three families, of which **21 are marked `novelty: new`**:

- 18 off-diagonal Schur numbers, `S(3;4,4,11) = 120` through `S(3;6,6,7) = 202`
- `R_4(5(x-y)=2z) = 625`, `R_4(5(x-y)=3z) = 625`, `R_4(5(x-y)=4z) = 741`

Two of the Rado values carry `external_status: open` in the fact ledger — no published
value existed when they were computed. That is the only status pair the validator reports
as NOVEL, and it is this project's sole existing claim to having produced new mathematics.

Three **frontier records** name the next cells explicitly, as `open` claims:

| Record | Assertion |
|---|---|
| `rado-r4-a6-b5-frontier` | `R_4(6(x-y)=5z) > 1500` — the shell construction at the next point of the `k=4` row |
| `rado-r5-a3-b1-frontier` | `R_5(3(x-y)=1z) > 243` — the `a^k` law fails at five colours |
| `rado-r5-a3-b2-frontier` | `R_5(3(x-y)=2z) > 350` — first five-colour bound for this family |

## Why it is still open

Nothing structural. Each cell is a well-posed finite problem of increasing size, and the
literature moves one paper at a time. Chang–De Loera–Wesley (ISSAC 2022,
[arXiv:2210.03262](https://arxiv.org/abs/2210.03262)) established the SAT route; a 2025
follow-up ([arXiv:2505.12085](https://arxiv.org/html/2505.12085v3)) extracts *symbolic
patterns* from SAT-found colourings to prove general lower-bound formulas, which is a
hybrid of search and synthesis worth reading before starting.

The independent combinatorics sweep, which knew nothing about this repository, picked this
family as **the best throughput domain in all of finite combinatorics** for a proof-carrying
stack. That convergence is the strongest signal in the whole survey.

## Encoding

Standard and small: one Boolean per (integer, colour), one clause per (solution, colour)
forbidding monochromatic solutions, plus symmetry breaking on colour permutation. For
`n` around 600–1500 and `k = 4` or `5` that is a few thousand variables and 10^5–10^6
clauses.

The formula is trivially small. The *search* is what costs, and it grows fast in `n`.

## Certificates

**Positive (lower bound: a valid colouring of `{1..N}`).** `N` trits, verified by iterating
every solution of `E` in range and checking no colour class contains one. Cheap enough to
be a proof term. This is the direction that produces frontier records.

**Negative (upper bound: no colouring of `{1..N+1}` exists).** DRAT. The existing
`R_4(5(x-y)=3z)` run is the calibration point and it is sobering:

```
p cnf 2500 224248            (6.6 MB instance)
220,077,720 DRAT steps
 19,877,980,843 bytes        (19.9 GB)
  8,762.2 s search
 14,499.6 s backward check   <- checking cost more than searching
```

Run as a memory-bounded transient systemd user scope, `MemoryHigh=70G / MemoryMax=90G`, on
a 123 GiB / 16-core host. A first attempt was destroyed at 2h15m when `systemd-oomd` killed
the whole session cgroup at 83.6 GB peak — **not** a kernel OOM, so `nohup` was irrelevant.

## Fit against this stack

The best of any target here, because it is the pipeline that exists:

- `crates/axeyum-search` — the cube-and-conquer harness, with per-cell DRAT checked
  immediately, models fsync'd inside the worker, and models re-evaluated against the
  *original* formula (a mismatch raises `SearchError::ModelDoesNotSatisfy`).
- Cover validity is four separate obligations in `cover.rs`: every cell refuted; every
  at-least-one clause present verbatim in `F`; cells exactly the cartesian product, once
  each; no duplicate ledger rows.
- `check_drat_backward` with a `MemoryBudget` that declines *before* memory is committed.
- The claim ledger and `scripts/check-claim-certificates.py` already model this family.

## What "done" looks like

One new cell, registered as a claim with `novelty: new`, carrying `witness-replay`,
`unsat-certificate` and `instance-pin` evidence rows, all `check_status: checked`. The
frontier record it supersedes gets updated rather than deleted.

Realistically: pick `R_5(3(x-y)=2z)`, whose frontier record already says `> 350`, and
either close it or push the bound.

## What would kill it

**The certificate outgrows the checker.** Each step up in `k` or `n` multiplies proof size,
and the check is already the dominant cost at 19.9 GB. At 6.6–10x memory for backward
checking, a 5 GB proof needs more than 26 GiB and a 10 GB proof does not fit on most hosts.
The failure mode is an OOM kill that is indistinguishable from a refutation.

**Mitigation before starting:** decide the target `N` in advance, estimate proof size from
the existing runs, and confirm the check fits in the host's budget. If it does not, this
is the wrong cell — pick a smaller one rather than discovering it four hours in.

**Secondary risk:** the audience is small. These are real results and nobody outside
additive combinatorics will notice. If the goal is external credibility rather than
measured throughput, prefer [03](03-sbox-optimality-trio.md).

## Sources

- [Chang, De Loera & Wesley, *Rado Numbers and SAT Computations*, ISSAC 2022](https://arxiv.org/abs/2210.03262)
- [*Symbolic Sets for Proving Bounds on Rado Numbers*, SC-Square 2025](https://arxiv.org/html/2505.12085v3)
- [Heule, *Schur Number Five*, AAAI 2018](https://arxiv.org/abs/1711.08076) — the 2 PB calibration point
- In-tree: `artifacts/claims/rado/`, `artifacts/claims/offdiag-schur/`, `crates/axeyum-search/`
