# 03 — Minimality: certifying "no shorter sequence exists"

## The shape

Minimality is a non-existence claim over a declared finite space: *no program of length < k in instruction set S computes π.* Encode "a program of length ≤ k−1 computes π" as CNF; UNSAT is the theorem; the DRAT refutation is the certificate; a satisfying model at length k, lifted to typed instructions and **replayed** through an independent evaluator, is the matching upper bound.

The encoding trick that makes this pure SAT (ADR-0559): lanes hold **provenance tags**, not bytes. A YMM value is 32 distinct optional tags; an instruction is a finite-domain function on tag vectors. No bit-vector arithmetic, so no bit-blasting layer — and DRAT falls out of the proof-producing core natively.

## The three encoders (`crates/axeyum-search/src/`)

| Module | Language | Object | ADR |
|---|---|---|---|
| `simd.rs` | unary `{vpshufb, same-source vperm2i128}` — one-step eligibility, calibration | (ADR-0559) | 0559 |
| `simd_synthesis.rs::encode_unary_avx2_sequence` | unary five-family: `vpshufb`, `vpermd`, `vpermq`, same-source `vpalignr`, same-source `vperm2i128`; multi-step | `M.avx2.reverse.len2.unary5` | 0566 |
| `simd_synthesis.rs::encode_weighted_unary_avx2_sequence` | same, plus a checked weighted-at-most CNF (`axeyum-cnf::encode_weighted_at_most`) over a named cost profile | `M.avx2.reverse.cost4.haswell` | 0583 |
| `simd_program_synthesis.rs::encode_multisource_avx2_sequence` | fourteen-family SSA language: two-source `vpalignr`/`vperm2i128`, eight unpacks, `vpblendd`, … | `M.avx2.reverse.len2.ssa14` | 0585 |

Each is deterministic and resource-bounded; each rejects non-permutation targets rather than silently searching a reduced language; each lifts models to typed instructions and replays them (a model that fails replay is rejected, and a replay mismatch is a soundness alarm).

## Running the checkers (no cargo lock)

```sh
B=$AXEYUM/target/release/examples
$B/synthesize_unary_avx2       reverse 1 120 --check-drat one-step.drat          # unary five-family
$B/synthesize_weighted_unary_avx2 3   120 --check-drat reverse-haswell-latency-le3.drat
$B/synthesize_multisource_avx2 reverse 1 120 --check-drat reverse-k1-seed1223.drat
```

Each regenerates the formula (byte-identical: the unary one-step CNF re-hashes to `7da5e266…`), runs axeyum's file-backed backward DRAT checker against it, and prints `verdict=unsat-checked` on success. `--dimacs PATH` writes the CNF instead of checking. `scripts/check_object.sh` wraps the hash verification, the positive check, and the truncation control.

To produce a fresh certificate with an external solver, write the CNF with `--dimacs`, run `cadical --no-binary FORMULA PROOF` (the shipped proofs are CaDiCaL 3.0.1, seeds recorded in `*.time.log`), then check as above. The native core can also refute these directly (`prove_unsat`); it is a reference core, deliberately not the fast path.

## The vacuity check — read this before trusting any certificate

**A DRAT over a formula that unit propagation already refutes carries no information.** The backward checker starts from the final empty clause and asks whether it is RUP from the formula; if propagation alone conflicts, the answer is yes for *any* proof whose last step is `0`. `M.avx2.reverse.len2.unary5` is exactly this: its 2,663-variable formula conflicts under UP, and the checker accepts the shipped proof with its first half deleted. The checker is sound; the *certificate* is decoration, and the load-bearing evidence is the CNF plus `scripts/up_refutes.py`.

The other two formulas are **not** UP-refutable (fixpoint without conflict), their proofs are load-bearing, and their truncation controls fail as they should. Every certificate object in the ledger records which case it is. Run `scripts/up_refutes.py FORMULA.cnf` before believing a small DRAT.

## What "proved" means here, and what it does not

- **Scope is the theorem.** "Minimum length 2" is a fact about the *named* language. ADR-0566: *"Calling a small model 'AVX2 minimality' would overstate its coverage."* The `scope` field is printed in every artifact box.
- **Cost is a named profile.** `intel-haswell-dependent-latency-cycles` (`vpshufb=1, vpermd=3, vpermq=3, vpalignr=1, vperm2i128=3`) is a serial dependency-chain proxy — Intel scopes added latency to dependency chains — not throughput, port pressure, or whole-machine cost. Ship the profile as data (`OP.format.cost-model-artifact`).
- **Not a kernel theorem.** These routes reconstruct as `StructuralAttestation`. The result is a checked claim with an independently re-checkable certificate, which is more than the field has, and less than the book wants (`OP.kernel.word-prelude`).
- **Not a priority claim.** ADR-0566: current searches "do not justify a novelty-priority claim." Franchetti & Püschel (CC 2008) proved stride permutations minimal on SSE2/Cell by a human-readable argument; LLVM already lowers reversal in two operations. What is new is the per-instance machine-checkable artifact on a current ISA.

## Extending to a new target

1. Define the target as tags (`ByteTags::new`), refuse non-permutations.
2. Add the instruction family's semantics to the evaluator **and** to an independent oracle (the ADRs used GCC intrinsics on AVX2 hardware, and each rejected a one-control mutation — keep that control).
3. Encode; solve at `k−1` and `k`; check the DRAT; replay the model.
4. Run `scripts/up_refutes.py` on the `k−1` formula and record whether the proof is load-bearing.
5. Write the object record with `scope`, both evidence rows, and a `negative_control`. `make check-run`.
