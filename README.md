# Words and Machines

*Instruction sets from first principles, with proofs you can check.*

This repository is a book, a paper, and the ledger that binds them — written in the manner of Spivak's *Calculus*: a tiny axiom base, every claim proved, and the exercises carrying the subject. The subject is instruction set architectures. The proofs are real artifacts produced and checked by [axeyum](https://github.com/mjbommar/axeyum), a Rust automated-reasoning stack whose identity is **untrusted fast search, trusted small checking.**

The book is not called a calculus; it borrows the *method*. What Spivak does for ℝ with thirteen axioms, this does for `Word n` with **zero** — words are constructed on the naturals, and the "obvious" facts (`bvudiv x 0` is all-ones; reversing 32 bytes takes two shuffles; Zbkb buys nothing on SHA-2's `Ch`) are theorems with certificates in the margin.

## The contract

Every definition, theorem, computation, exercise, and open problem in the book is an **object**: a JSON record in [`objects/`](objects/) modelled on axeyum's fact ledger, carrying a formal statement, a status on two axes (what *this repository* established; what the *literature or the ISA vendor* holds), the declared **scope** the claim is relative to, and evidence rows each with a real artifact in [`artifacts/`](artifacts/), a SHA-256, and a `checker_command` **whose exit status depends on the finding** — plus a `negative_control` that must fail.

The book's status boxes are *generated from the ledger* (`make ledger`) and never typed. A chapter cannot say "proved" about an object the ledger marks `open`. This is axeyum's rule — read the trusted base from the kernel, never from prose — applied to a book.

```
make reproduce     # pure-Python exhaustive reproductions (no axeyum needed, ~70 s)
make check         # validate every object record
make check-run     # ALSO execute every checker and negative control (needs axeyum prebuilt examples)
make book          # the PDF
make paper         # the paper PDF
```

Verified 2026-08-27: **34 objects, 0 problems, every negative control fired.** See [`objects/LEDGER.md`](objects/LEDGER.md).

## What is in the ledger today

| Part | Objects | Status |
|---|---|---|
| Prologue — Words | `Word n` defined; the three SMT-LIB totality conventions **proved** through axeyum's front door; one negative control **refuted** as it must be | 3 proved, 1 refuted |
| I — Instructions as functions | Hacker's Delight popcount = spec at width 32, **proved**; the equivalence-vs-minimality principle | 1 proved |
| II — Cost and certificates | the asymmetry; the three escape hatches; **a theorem the book found in its own artifacts**: a DRAT over a propagation-refutable formula carries no information, and one shipped certificate is exactly that | 1 computed |
| III — Permutations | provenance tags; the entropy bound (log₂ 32! < 128, so lower bounds are lane-structure facts) | 1 computed |
| IV — Particular machines | AVX2 byte reversal: **minimum length 2** in the unary five-family language and in the fourteen-family SSA language; **minimum cost 4** under the Haswell dependent-latency profile — three DRAT-certified theorems (1–13 MB, re-checked here, truncations rejected). RISC-V: the 256-function bit-logic table **reproduced 512/512** by exhaustive search; the Bitmanip byte-permutation bound and the **lost Table 2.2** (source URL now 404) recovered exactly | 3 proved, 3 computed |
| Open problems | sixteen curated, from the 90-odd in the surveys — the certified bit-logic table (days), the 5:6:5 RGB lower bound a spec asserts without proof, the Zbb table, `_MM_TRANSPOSE4_PS`, LLVM's PerfectShuffle table, `R_F2(P_6)`, Keccak χ₅, MixColumns' first lower bound, Unison via DRCP, the closure-transcript format, the word prelude | 16 open |

## Layout

| Path | What |
|---|---|
| [`book/`](book/) | The book — instantiated from [book-template](https://github.com/mjbommar/book-template). Chapters in `book/latex/chapters/`; the `artifact` box and `\ObjStatus` macros in `book/latex/preamble/objects.tex`. |
| [`paper/`](paper/) | The paper introducing axeyum to the compilers audience — instantiated from [paper-template](https://github.com/mjbommar/paper-template). |
| [`objects/`](objects/) | The ledger: one JSON per object, the schema, and the generated `LEDGER.md`. |
| [`artifacts/`](artifacts/) | The evidence: CNFs and DRATs (gzipped, raw SHA-256 recorded), SMT-LIB files, solver logs, exhaustive-search transcripts, the RISC-V source document. |
| [`axeyum-guide/`](axeyum-guide/) | How to use axeyum for each part of the book — what each route proves, what it doesn't, where the stack stops, and how to reproduce every number. |
| [`research/`](research/) | Everything the book rests on: the axeyum documents and ADRs behind every artifact, ten literature surveys (verbatim, with their own unverified-item flags), and the prior-art search for an existing book of this kind (negative, with controls). |
| [`scripts/`](scripts/) | The checkers and generators. `check_object.sh` re-verifies a certificate end to end; `up_refutes.py` decides whether a proof is load-bearing; `check_objects.py` gates the ledger; `gen_ledger.py` writes the views. |

## Three findings worth stating up front

1. **No superoptimizer from Massalin (1987) to HieraSynth (2025) emits a machine-checkable certificate of optimality.** Every system that proves minimality does so by exhausting a search with solver `unsat` answers and then discarding the refutation. The nearest antecedent — Franchetti & Püschel, CC 2008 — proved stride permutations minimal on SSE2 by a human-readable argument. The book's Part IV is that, for general permutations on a current ISA, with an artifact per instance.
2. **Real ISA design rests on uncertified exhaustive searches.** RISC-V's crypto repository answers "would NOR and NAND help? Not really" from a 256-function table whose only evidence is "our exhaustive search"; the Bitmanip draft asserts a bare lower bound ("at least 7 instructions") with no proof; the enumeration behind its permutation tables is a 404. This repository reproduces those tables exactly — and reproduction by a second uncertified search is still not a proof. Certifying them is days of work (`OP.riscv.bitlogic256-drat`).
3. **A proof can be accepted and still carry no information.** One of the three shipped DRAT certificates is over a formula that unit propagation already refutes; the checker accepts it with half the file deleted. The checker is sound; the certificate was decoration. The ledger says so, and `scripts/up_refutes.py` now runs before any small proof is believed.

## Status

Bootstrapped 2026-08-27 from a research session in the axeyum repository. The ledger, checkers, artifacts, and research corpus are complete and verified; the chapters are first drafts; the paper is a skeleton with its related-work map and reviewer objections worked out. See [`book/docs/SPIRIT.md`](book/docs/SPIRIT.md) before writing prose, and [`CLAUDE.md`](CLAUDE.md) for the rules.

## License

MIT (this repository). Documents under `research/axeyum/` are copied from axeyum (MIT OR Apache-2.0). The RISC-V `bitlogic.adoc` under `artifacts/riscv/` is reproduced from the riscv-crypto repository for verification and is under its own license.
