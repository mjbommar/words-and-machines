# 03. S-box gate complexity: three gap-1 intervals

**One-line:** three published intervals, each one hard UNSAT call from closed, where a
certified answer would be **the first machine-checkable S-box optimality result ever
produced**.

| | |
|---|---|
| Statement | Minimum gate / AND count for the S-boxes of Keccak, RECTANGLE, PRIMATEs^-1 |
| Known | published as intervals: UNSAT proven at `k-1`, SAT found at `k` |
| Gap | **1** on each of three instances |
| Encoding | 10^3–10^4 variables; encoding is published and public |
| Positive certificate | 32 evaluations |
| Negative certificate | DRAT, MB to GB |
| Effort | weeks |
| Risk | medium |
| Audience | NIST LWC, SHA-3 hardware, MPC / ZK / FHE cost models |

## The problem

Zhang & Huang ([eprint 2023/1721](https://eprint.iacr.org/2023/1721), Tables 9–11) report
S-box circuit complexity as **intervals** `[k1, k2]`, meaning UNSAT was proven at `k1 - 1`
and a circuit was found at `k2`. Three are one step wide:

| S-box | Metric | Interval | Where it ships |
|---|---|---|---|
| **Keccak / SHA-3 `chi5`** | bit-gate complexity | `[12, 13]` | FIPS 202, every SHA-3 core, Ethereum's Keccak-256 |
| **RECTANGLE** | bit-gate complexity | `[11, 12]` | lightweight block cipher |
| **PRIMATEs^-1** | multiplicative complexity | `[7, 8]` | AND count — the MPC/ZK/FHE cost metric |

Wider intervals in the same tables, if the narrow ones close quickly: Ascon BGC `[12, 16]`
and GC `[12, 15]`; Keccak `chi5` GC `[11, 13]`; ICEPOLE BGC `[12, 26]`.

Already settled, so do not re-derive: `MC(Ascon) = 5`, `MC(PRIMATEs) = 7`, and
`MaxMC = 6` over all 150,367 classes of 6-variable Boolean functions
([eprint 2018/002](https://eprint.iacr.org/2018/002)).

## Why this one is different: the soundness angle

Zhang & Huang's own Remark 1 states that **prior published optimality results "may cause
potentially incorrect results"**, and that they had to re-verify them. The field's optimality
claims rest on the authority of the implementation that produced them.

**No DRAT certificate has ever been produced for an S-box optimality result.** So closing
one of these intervals with a checked certificate is not a speed contribution — it is a
soundness contribution, and a first, in a field that has publicly asked for one.

This is the closest match in the whole survey to this repository's stated identity:
*untrusted fast search, trusted small checking.*

## Why it is still open

Pure solver capability, stated by the authors: "the SAT solver cannot always return the
results within a reasonable time (especially for the UNSAT instances)."

Their measured runtimes give the shape of it — UNSAT at `k = 8..10` in 1.4 to 341 s, but SAT
instances reaching 27,303 s. The hard direction at the boundary is the one that is open.

NIST states the general barrier plainly: "with currently known techniques, it is intractable
to find AND-optimal circuits for most Boolean functions with more than 6 input variables."
These S-boxes are 4- and 5-bit, which is why they are the tractable end.

## Encoding

Published and public. ANF-based encoding from
[eprint 2023/1721](https://eprint.iacr.org/2023/1721); prior art in
[Stoffelen, FSE 2016](https://ko.stoffelen.nl/papers/fse2016-sboxoptimization.pdf).
Roughly 10^3–10^4 variables for a 4- or 5-bit S-box at a fixed gate budget.

Trivially small for this stack. As with [02](02-bilinear-f2-p6.md), the difficulty is
symmetry and search, not size.

## Certificates

**Positive (a `k`-gate circuit exists).** Evaluate on all 32 inputs (5-bit) or 16 (4-bit).
Milliseconds, no solver. The engineering sweep did exactly this for a different circuit —
it downloaded NIST's current AES S-box straight-line program and verified 29 AND / 95 XOR /
14 XNOR against FIPS 197 on all 256 inputs, in about twenty lines of Python.

**Negative (no `k-1`-gate circuit exists).** DRAT out of the proof-producing core, MB to GB
on a 10^4-variable instance. Comfortably inside what this repository checks today, and one
to two orders of magnitude below the Rado calibration run.

## Fit against this stack

Strong:

- Size well inside every admission-control cap.
- `crates/axeyum-cnf/src/proof_sat.rs` produces DRAT by construction; `check_drat_backward`
  checks it; `crates/axeyum-search` gives cube-and-conquer if one instance needs splitting.
- Proof sizes are small enough that **LRAT elaboration is plausible**, unlike most targets
  here — which would allow external re-verification with a formally verified checker. Requires
  disabling inprocessing, since BVE emits RAT steps that LRAT cannot express.
- The evidence envelope (`Evidence::check_outcome`, three-valued, `NothingToCheck` explicitly
  not a pass) is exactly the right shape for this claim.

## A related instance worth noting

**AES S-box AND-depth is `[3, 4]`** and the lower bound is easy to re-derive: AND-depth `d`
bounds algebraic degree by `2^d`; every one of the 8 AES S-box coordinate functions has ANF
degree exactly 7, so `2^d ≥ 7` gives `d ≥ 3`. The upper bound is 4 (NIST "S-Box 3", 34 AND /
94 XOR).

A depth-3 circuit must place all nonlinearity in three layers, which is a strong structural
constraint — so the search is *small*, and it appears nobody has run it. The audience is FHE,
where multiplicative depth is the dominant cost parameter. Consider this a fourth instance in
the same lane.

## What "done" looks like

Close one interval, either direction:

- **SAT at `k-1`** — a better circuit, verified by exhaustive evaluation, plus an updated
  interval. Directly useful to implementers.
- **UNSAT at `k-1`** — optimality, with a DRAT certificate backward-checked in-tree. The
  first of its kind, and the result worth having.

Register as a claim with `novelty: new`, evidence rows `witness-replay` (the circuit) and
`unsat-certificate` (the DRAT), both `check_status: checked`.

## What would kill it

**The boundary UNSAT is exactly where the solver stops.** These intervals are one wide
*because* `k-1` is the first call that did not return. Zhang & Huang had modern hardware and
a tuned encoding. Assuming this stack closes it because the formula is small is the same
mistake as assuming `C500.9` is easy because it is 85,000 clauses.

**Test for this early:** reproduce their *known* UNSAT results first — the `k = 8..10` cases
that ran in 1.4 to 341 s. If this stack cannot reproduce a published UNSAT at the size where
they report seconds, the boundary instance is out of reach and the estimate is void.

**Secondary risk:** the positive direction may already have been closed by someone since
2023 and not propagated. Check forward citations of eprint 2023/1721 before starting — the
survey's own AES example had NIST's overview page four records behind its own data files.

## Sources

- [Zhang & Huang, eprint 2023/1721](https://eprint.iacr.org/2023/1721) — the intervals, Tables 9–11
- [Stoffelen, *Optimizing S-box implementations*, FSE 2016](https://ko.stoffelen.nl/papers/fse2016-sboxoptimization.pdf)
- [Jia et al., *How Small Can S-boxes Be?*, eprint 2025/386](https://eprint.iacr.org/2025/386)
- [NIST list of circuits](https://csrc.nist.gov/Projects/circuit-complexity/list-of-circuits) — note the overview page lags the data files
- [eprint 2018/002](https://eprint.iacr.org/2018/002) — 6-variable `MaxMC = 6`, settled
