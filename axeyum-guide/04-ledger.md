# 04 — The ledger: objects here, facts and claims there

## Two ledgers in axeyum, one here

axeyum keeps two: `artifacts/facts/` (one JSON per mathematical proposition, schema `artifacts/ontology/fact.schema.json`, gated by `scripts/validate-facts.py`) and `artifacts/claims/` (search-produced results with `witness-replay` / `unsat-certificate` / `instance-pin` evidence, ADR-0380). A fact carries a formal statement **and** a status on two axes — `epistemic_status` (what we established) and `external_status` (what mathematics knows) — and their disagreement in our favour is a new result the validator prints.

`objects/*.json` is the book's version of the same idea, with three additions the book needs and axeyum's facts do not have:

| Field | Why |
|---|---|
| `kind` | a book has definitions, principles, exercises and negative controls, not only propositions |
| `scope` (required for theorems/computations) | a minimality claim is meaningless without its declared subset and cost model |
| `evidence[].negative_control` | a command that **must fail**, so `make check-run` proves the checker can fail |

And two conventions carried over unchanged: `checker_command` exit status depends on the finding; `check_status` is per evidence row (`checked` / `replay-only` / `not-checked`), never per object.

## Mapping

| objects/ | axeyum |
|---|---|
| `epistemic_status: proved` with `front-door-verdict` | a fact with `proof_route: smt-term-level` (evidence `kind: witness-replay` or `unsat-certificate`) |
| `epistemic_status: proved` with `unsat-certificate` + `witness-replay` | a **claim** under `artifacts/claims/<family>/<id>/claim.json` — the shape the 21 `novelty: new` Rado/Schur results use |
| `epistemic_status: computed` with `exhaustive-enumeration` | a claim with `instance-pin` evidence; or a fact with `proof_route: search-certificate` |
| `external_status: computed-uncertified` / `asserted` | no axeyum equivalent — added because ISA specs assert counts without proofs |
| `epistemic_status: open` | a fact with `epistemic_status: open` and no evidence (the validator rejects an `open` fact carrying evidence — so does `check_objects.py`) |

## Promoting an object into axeyum

When a Part IV theorem is worth keeping in axeyum's ledger (a new certified number, not a reproduction):

1. Write `artifacts/claims/simd/<id>/claim.json` with `witness-replay`, `unsat-certificate` and `instance-pin` rows; pin the CNF and DRAT by SHA-256; make every `checker_command` discriminate (`grep -c` a verdict line and test the count — never `grep -q` under `pipefail`, never `echo "exit=$?"` after a pipe).
2. Set `novelty` honestly. The Rado frontier records model this: `>368` has five checked `witness-replay` rows and `novelty: None`, because dated negative retrieval is not a priority claim.
3. Run `python3 scripts/validate-facts.py` and `scripts/check-claim-certificates.py` there; regenerate the dashboard; commit with `scripts/lane-commit.sh` (never a bare `git commit` in a shared checkout).

## The trap this book's ledger caught

`M.avx2.reverse.len2.unary5` shipped a 957,982-byte DRAT that is accepted by the checker with half of it deleted. Nothing in the ADR's evidence section was false — the checker *does* accept it — but the proof carried no information, because the formula is refutable by unit propagation. The ledger now records this on the object (`note`), the theorem `C.thm.vacuous-certificate` states the general fact, and the checker for that object runs the UP test instead of a truncation control. The general rule, one arrow upstream from axeyum's own: **a proof that cannot be wrong is worse than no proof, because it reads as evidence.**
