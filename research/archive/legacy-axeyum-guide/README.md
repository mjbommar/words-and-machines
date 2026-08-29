# Using axeyum for this book

[axeyum](https://github.com/mjbommar/axeyum) is a Rust automated-reasoning stack: typed term IR → rewriting → solver backends (a pure-Rust bit-blast-to-SAT path with a proof-producing CDCL core; native oracles behind feature flags) → models, proofs, and checkable evidence, with a Lean-style proof kernel. Its identity in one sentence: **untrusted fast search, trusted small checking.** This book is that sentence applied to instruction sets.

Every object in `../objects/` names the axeyum route that produced or checks its evidence. This guide says how to run each route, what it proves, what it does not, and where the stack currently stops — read from axeyum's own measurements, not its prose.

| Guide | Book part | axeyum surface |
|---|---|---|
| [01-words.md](01-words.md) | Prologue — words | the `nat` prelude (0 axioms), the absent `word_prelude`, `BitVec w` in reconstruction |
| [02-equivalence.md](02-equivalence.md) | Part I — instructions as functions | `smtcomp_cli` / `solve_smtlib` over QF_BV; what "unsat" carries |
| [03-minimality.md](03-minimality.md) | Parts III–IV — permutations and machines | `axeyum-search::simd*`, the three `synthesize_*_avx2` examples, `check_drat_backward`, and the vacuity check |
| [04-ledger.md](04-ledger.md) | the whole book | how `objects/*.json` maps onto `artifacts/facts/` and `artifacts/claims/` in axeyum |
| [05-reproduce.md](05-reproduce.md) | everything | the exact commands, what needs a build and what runs from prebuilt binaries, expected runtimes |

## The three rules this book inherits from axeyum

1. **A checker that cannot fail is worse than no checker.** Every `checker_command` in the ledger must exit nonzero when the finding does not hold, and every certificate object carries a `negative_control` that must fail. `make check-run` executes both. When the book's own artifacts violated this (a DRAT that any file ending in `0` would satisfy), the object says so — see `C.thm.vacuous-certificate`.
2. **Read status from the ledger, never from prose.** The book's status words are generated (`make ledger`). A chapter cannot say "proved" about an object the ledger marks `open`.
3. **Scope is part of the theorem.** A minimality claim without its declared instruction subset and cost model is meaningless. `scope` is a required field for every theorem and computation, and the `artifact` box prints it.

## Where the stack stops (measured 2026-08-25, see `../research/surveys/04-axeyum-capability-report.md`)

- **No word prelude in the kernel.** `BitVec w` is a per-width inductive rebuilt during each reconstruction. Nothing accumulates. Building one is `OP.kernel.word-prelude`.
- **Search results do not become kernel theorems.** Enumeration and int-blast routes reconstruct as `StructuralAttestation` — a module that asserts `axiom P` and `axiom ¬P` with none of the reasoning inside. So every minimality theorem in Part IV is a *checked claim*, not a kernel theorem. Closing that gap needs proof by reflection (a kernel-run enumerator for small cases; a verified DRAT checker for large ones).
- **Checking costs more than searching at scale.** Backward DRAT checking measured 6.6–10× proof size in RAM; a 19.9 GB proof took 8,762 s to produce and 14,500 s to check. The certificates in this book are 1–13 MB and check in under a second — deliberately.
- **The proof-producing core has no assumption interface**: warm-and-fast or proof-carrying, never both.
