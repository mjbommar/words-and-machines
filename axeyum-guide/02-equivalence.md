# 02 — Equivalence: deciding "these two programs agree" with the front door

## The shape

An instruction is a function on state; a program is a composition; equivalence is `∀s, p₁ s = p₂ s`. Over fixed-width words this is a QF_BV sentence, and its negation is a QF_BV query: **unsat means the equivalence holds.** Every Part I object is written this way — see `artifacts/words/*.smt2`:

```smt2
(set-logic QF_BV)
(declare-const x (_ BitVec 8))
(assert (not (= (bvudiv x #x00) #xff)))   ; negated theorem
(check-sat)                                ; expected: unsat
```

## Running it

The prebuilt example takes no cargo lock and is the right tool when other lanes are building:

```sh
AXEYUM=~/projects/personal/axeyum
$AXEYUM/target/release/examples/smtcomp_cli artifacts/words/bvudiv-by-zero-is-allones.smt2 --timeout-ms 60000
# -> unsat
```

`scripts/check_smt.sh FILE EXPECTED` wraps this and exits nonzero on anything but the expected verdict — including `unknown`, which is a first-class result in axeyum and never an error.

From source: `cargo run --release -p axeyum-solver --example smtcomp_cli -- FILE`. Under lane contention go through `scripts/cargo-serialized.sh` in the axeyum checkout (it holds a host-wide flock and a cgroup memory ceiling with swap capped — a ceiling without a swap ceiling is decoration).

## What the verdict carries — and what it does not

`smtcomp_cli` prints SMT-COMP-style output: `sat` / `unsat` / `unknown`, and per §7.1.2 of the competition rules an error prints `unknown`. Internally the front door (`solve_smtlib`) checks its own `unsat` — for QF_BV via a term-level exhaustive certificate on small instances, or Alethe (bit-blast → CNF → resolution) or DRAT otherwise — and replays every `sat` model against the original terms. **The CLI does not export that certificate.** So the ledger records these rows as `front-door-verdict`, `check_status: checked` (re-running reproduces the verdict; the negative control `W.ctl.udiv0-wrong` returns `sat`), and the exercise of exporting the Alethe proof and re-checking it with Carcara is left open.

Do **not** use `explain_corpus` as an oracle for these: it calls `check_auto_explained` on the flat view, not the shipped front door, and its output is prefixed (`flat-unsat`, `not-attempted`) precisely so it cannot be grepped as an answer.

## Width-independence

Every Part I theorem here is at a fixed width (8 or 32). Bhat et al. (OOPSLA 2025) decide the *width-independent* versions in Lean and report 100% of Hacker's Delight — and 27% of LLVM's peephole test suite. The remaining 73% are named open exercises with a public artifact; axeyum's route to them would be the QF_BV front door per width plus a kernel induction over `n`, which needs the word prelude of [01-words.md](01-words.md).

## Partial operators

Any object over `bvudiv`, `bvurem`, `bvsdiv`, `bvsrem`, `bvsmod` must carry the degenerate-divisor case explicitly. axeyum shipped a wrong-unsat once (`a946f925`) because div-by-*constant*-zero was folded to a fixed convention and the differential fuzz only ever emitted variable divisors. The Prologue's totality theorems exist to make that convention a checked fact rather than a folding rule.
