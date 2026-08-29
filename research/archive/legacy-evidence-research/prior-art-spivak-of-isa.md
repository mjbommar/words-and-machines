# Is there an existing "Spivak of ISA"?

*Searched 2026-08-27. Google Scholar via SerpApi failed two positive controls (exact titles of well-known papers returned nothing), so every Scholar zero is void; Google web plus direct fetch of repositories and documentation was the working instrument and found the real libraries on the first pass.*

**Question.** Does a from-first-principles treatment of an instruction set exist — a small axiom base, every theorem machine-checked, minimality claims as theorems, exercises carrying the subject — the way Spivak's *Calculus* treats the reals?

**Answer.** Not as a single thing. The pieces exist, all in Lean, none assembled, and nobody has written the book.

| Spivak part | State | Where | Verified how |
|---|---|---|---|
| Prologue — properties of words | **done** | Isabelle AFP `Word_Lib` (seL4 team, 2016): "an extensive library of properties about generic fixed-width words"; Coq `mit-plv/bbv`, `coq-community/bits`; Lean 4 core `BitVec` + `bv_decide` (trusted base: one axiom, `Lean.ofReduceBool`) | AFP entry and repos fetched |
| Exercises — the bit identities | **done, all widths** | Bhat, Stefanesco, Hughes & Grosser, *Certified Decision Procedures for Width-Independent Bitvector Predicates*, OOPSLA 2025 (doi:10.1145/3763148): *"Our tools solve 100% of Hacker's Delight … and up to 27% of peephole rewrites extracted from LLVM's peephole rewriting test suite."* Artifact badges: Available, Reusable, Results Reproduced. | Abstract fetched from the OOPSLA proceedings page |
| Part I — the ISA as kernel definitions | **done, unproven** | `opencompl/sail-riscv-lean`: the official Sail RISC-V spec translated to Lean 4, 161 files, type-checks. README: *"neither executable nor polished."* | Tree inventoried via GitHub API: **zero** files named like theorems, lemmas, or proofs |
| Part I — a theorem library over that ISA | absent | — | |
| Part II — minimality as a theorem | absent | Franchetti & Püschel (CC 2008) proved stride-permutation sequences minimal on SSE2/Cell by a human-readable Floyd argument; never generalized, no artifact | six agents, ~40 formulations |
| The DAG / ledger driving production | absent | — | |
| The book | absent | `"Spivak" "instruction set"` returns noise; no textbook or curriculum with "every theorem proved" for a machine ISA | |

**Near-misses worth knowing.** Nipkow & Klein, *Concrete Semantics*, is exactly a Spivak-of-programming-language-semantics — small base, everything in Isabelle, exercises carry it — for an idealized language, not a machine. Knuth's TAOCP §7.1.2 (Boolean chains, in Vol. 4A) and MMIX have the *method* — an axiomatic machine, obvious claims settled by exhaustive search presented as exercises — with nothing machine-checked and results surviving only as Goucher's `Optimal5` lookup table. Warren's *Hacker's Delight* is the exercise set with informal proofs. The Lean reference manual's bitvector chapter uses Warren's popcount (Fig. 5-2) as its worked example and proves it with `bv_decide`; `leanprover/vstte2024` does the same inside a toy imperative language — demos, not a book.

**Consequence for this repository.** Three of seven rows are filled, all in one ecosystem, by people who could fill the rest. The technical substrate exists; what does not is the *production method* — a ledger of objects with checkers whose exit status depends on the finding, and a concept DAG that says what to prove next. That is what `../objects/` and axeyum's flywheel are for.

Two concrete unclaimed items fell out of the search: Bhat et al.'s **27% on LLVM peepholes** means the other 73% are named open exercises with a public artifact; and `sail-riscv-lean` being definitions-only means **the first theorem library over the official RISC-V semantics** is unclaimed and small to start.
