# axeyum reasoning stack: measured capability report

*Produced 2026-08-25 by an Explore agent instructed to read files, grep, and inspect JSON in the axeyum checkout — never to run a build. Every claim carries a `file:line` in that repository. Reproduced verbatim; line numbers are as of that date.*

---

## 1. SOLVER REACH — what is actually dispatched

### 1a. The progress-frontier ratchet (the pinned numbers)

`crates/axeyum-solver/tests/progress_frontier.rs` — **only five parametric families exist**, not one per logic. There is no `qf_bv`-general, `lra`, `uf`, `arrays`, or `quantifiers` frontier row at all.

| family | baseline | file:line |
|---|---:|---|
| `bv_reduction` (QF_BV word-level reduction, `N²`-multiplier tower) | **30** | `crates/axeyum-solver/tests/progress_frontier.rs:183` |
| `lia_cuts` (QF_LIA branch-and-bound, SAT + witness-checked) | **26** | `:189` |
| `string_bound` (bounded-string required length) | **8** | `:195` |
| `nra_degree` (QF_NRA even-degree sum-of-powers refutation, knob = half-degree) | **40** | `:210` |
| `nia_unsat` (QF_NIA `no-square-mod` integer-nonlinear refutation) | **40** | `:221` |

Context constants: `BUDGET = 4 s` per instance (`:124`), `OVERSHOOT = 3` (`:128`), `MAX_N = 40` (`:225`) — a hard sweep ceiling. Two of these are saturated at the sweep ceiling, not at the decider: `nra_degree` reaches 40 because a *syntactic* even-power pre-check (`nra_even_power`) recognizes `Σ tᵢ^{2kᵢ} + c < 0` in O(term size); `nia_unsat` reaches 40 via bound-aware exact int-blast (`decide_bounded_int_blast` in `auto.rs`). Neither number represents general NRA/NIA power. `string_bound = 8` is a *hard* packing bound (`STRING_MAX_LEN`), not a timing edge.

Doc-comment caveat: the module header at `:100-110` still describes `nra_degree` as falling off at degree ~4 and `nia_unsat` frontier as `0`. That prose is **stale** relative to the constants. Trust the constants.

### 1b. Fragments actually wired

Generated fragment ontology `artifacts/ontology/smt-fragments.json` has **10 rows**: `qf_bv, qf_abv, qf_uf, qf_ufbv, qf_lra, qf_lia, qf_dt, qf_fp, qf_nra, qf_nia`.

Four-axis machine-checked matrix, `docs/research/08-planning/support-matrix.md:38-56` (golden-tested against `crates/axeyum-solver/src/support_matrix.rs`):

- `decides` + proof `checked`: QF_BV, QF_UF, QF_LRA, QF_LIA·integer-infeasibility, QF_NRA·degree-2 SOS.
- `decides` + `partial-trust`: QF_ABV, QF_LIA (general), QF_IDL/QF_RDL, QF_UFLIA/QF_UFLRA, QF_FP, datatypes.
- **`sound, incomplete (unknown-safe)`** — routinely returns `unknown`: QF_NIA, QF_NRA (general), quantifiers, strings (bounded), optimization/OMT.
- `decides`, proof `none`: QF_NRA·CAD, QF_NRA·single-variable real-algebraic, incremental.

Measured decide-rates vs z3 4.13.3, `bench-results/SCOREBOARD.md:15-58` — 35 division baselines, 24 logics, **DISAGREE = 0 across all** (674 oracle-compared instances, 992 files, 762 decided). Weak spots: `LIA` quantified 0%, `QF_SLIA` 50%, `QF_UF` 54%, `QF_SEQ` 67%, `QF_S` 69%, `qf-nra-cvc5-regress-clean` 84%.

## 2. CAS / SYMBOLIC LAYER

`crates/axeyum-cas/`, ~45 modules, "proof-carrying computer algebra … certified by lowering to the decidable core" (`src/lib.rs:1-48`, ADR-0301).

| capability | location |
|---|---|
| canonical multivariate polynomial normal form + decidable exact zero-test | `crates/axeyum-cas/src/lib.rs:1-48` |
| **resultant** / **discriminant** | `lib.rs:7914` / `:7956` |
| **factorization over ℚ** (univariate) | `factor_int.rs:84`, `lib.rs:2704` |
| **factorization over 𝔽_p** (Berlekamp) | `gfp.rs:697` |
| **Gröbner basis** (Buchberger, lex) + `reduce` + `ideal_contains` | `groebner.rs:394,448,496` |
| **Gröbner with cofactor witness** (checker shares no code) | `groebner_cert.rs:1-32`; consumer `crates/axeyum-solver/src/cas_certificate.rs` |
| **real root isolation** (Sturm) | `sturm.rs:92,135,220` |
| **real algebraic numbers** | `algebraic.rs:34-162` |
| **SOS / Positivstellensatz certificates** incl. a dual PSD moment functional proving a PSD polynomial is *not* SOS (Motzkin) | `sos.rs:1-45`, checker `sos.rs:414` |
| **Gosper**; **Zeilberger creative telescoping** (8 committed certificates) | `gosper.rs`, `telescoping.rs` |
| number theory: Legendre/Jacobi/Kronecker, `sqrt_mod`, primitive roots, discrete log, continued fractions, Pell | `ntheory_advanced.rs:145-660` |
| GF(2) polynomial machinery incl. sharded search | `gf2*.rs` |

**Hard numeric limit:** `MvPoly` coefficients are `i128`-backed `Rational`; overflow returns `None`/`Unknown`, never a wrong answer (`lib.rs:44-47`). A BigInt escape hatch exists only for the GCD/PRS inner loop (`mvpoly/big.rs:1-20`).

## 3. PROOF KERNEL — carriers, theorem counts, axiom footprint

Nine Lean-style preludes in `crates/axeyum-lean-kernel/src/`: `logic`, `nat`, `integer`, `rat`, `creal`, `complex`, `cpoint`, `string`, `axreal`.

Theorems per prelude (generated, `docs/plan/generated/theorem-production-ledger.md`):

| Prelude | Theorems (cumulative) | Originated here | Axiom-free | Axiom-bearing |
|---|---:|---:|---:|---:|
| `axreal` | 32 | 0 | 32 | 0 |
| `complex` | 1037 | 87 | 1037 | 0 |
| `cpoint` | 1040 | 90 | 1040 | 0 |
| `creal` | 950 | 205 | 950 | 0 |
| `integer` | 505 | 156 | 505 | 0 |
| `logic` | 32 | 32 | 32 | 0 |
| `nat` | 349 | 317 | 349 | 0 |
| `rat` | 745 | 240 | 745 | 0 |
| `string` | 96 | 64 | 96 | 0 |
| **distinct** | **1191** | **1191** | **1191** | **0** |

Axiom footprint (`docs/plan/generated/lean-axiom-ledger.md:24-34`): **30 total assumptions, all in `axreal`.** Every other prelude is 0/0/0 (Axiom/Opaque/Quotient). `axreal` is the *legacy axiomatized* ordered field; the reals the shipped route reasons over are `creal`, the Bishop setoid of regular rational sequences — constructed, zero axioms (ADR-0512).

Kernel has an official `lean4export` NDJSON **format 3.1.0** emitter that fails closed (`lean_export.rs:1-30`), written independently of the importer for differential testing.

## 4. RECONSTRUCTION — which verdicts become kernel terms

`crates/axeyum-solver/src/reconstruct.rs`, `pub enum ProofFragment` at `:944` — **65 variants** (64 routes + `Unsupported`), grouped: Bool/BV/structural (`QfBv` :946 …), UF/EUF, Arrays (incl. seven hand-built program shapes), Datatypes, Linear arithmetic (`Lra` :1027, `DisjunctiveLra`, `LraDpll`, `ArithDpll`, `IntFarkas`, `BoundedIntBlast` :1061, `Diophantine`, `IntInequality`), Nonlinear real (`Sos` :1075 — **only** the single-square shape; general SOS deferred at `:1332-1340`; `NraEvenPower`, `RealZeroProduct`, `RealProduct`, `MonomialBound`), Quantifiers (15 routes), Strings (`WordEquation` :1158, contradicted disequality / constant clash only).

**The distinction that matters most.** `LeanModuleContent` at `:1193` splits every route into two kinds, invisible in exit status, fragment name, or absence of `sorryAx`:

- **`TheoryReconstruction`** — the theorem is built from the query's own translated content; the kernel can reject it on the merits. Listed at `:1291-1325` (35 routes incl. `QfBv`, `Lra`, `IntFarkas`, `Sos`, `Forall`, `Exists`, `WordEquation`).
- **`StructuralAttestation`** — the module asserts `axiom P` and `axiom Not P` and applies them; **it contains none of the reasoning it attests to.** 29 routes at `:1262-1290`, including `FiniteDomainEnum`, `TermLevelEnum`, `SetCardinality`, `LraDpll`, `ArithDpll`, **`BoundedIntBlast`**, **`NraEvenPower`**.

So the two frontier families pinned at 40 reconstruct only as structural attestations; their verdicts do **not** become theorems with mathematical content.

## 5. PROOF ARTIFACTS

`crates/axeyum-solver/src/evidence.rs:1-55` is the envelope; `Evidence::check_outcome` is three-valued — `Verified` / `NothingToCheck` / `Failed`, and `NothingToCheck` is explicitly **not a pass** (`:33-45`, ADR-0384).

| format | status |
|---|---|
| **model replay** — every model replayed through the ground evaluator against the *original* terms | end-to-end, every SAT path |
| **term-level exhaustive certificate** (small QF_BV) — trusts only the evaluator | end-to-end, strongest |
| **DRAT** — re-parsed and re-run by `check_drat`; streaming producer (ADR-0381); backward/core-first checker (ADR-0382) incl. file-backed variant | end-to-end |
| **LRAT** — independent hint-based checker + DRAT→LRAT elaborator; **RAT steps cannot be expressed** and are a typed error (`lrat.rs:113`) | present |
| **Alethe** (Carcara-checkable) — complete bitblast→CNF→resolution | end-to-end |
| **Farkas / LraDpll / ArithDpll exact-arithmetic certificates** | end-to-end |
| **Lean export** — kernel-checked module, re-derived on `Evidence::check` | end-to-end for named fragments |
| **bare `unsat`** (`Evidence::Unsat(None)`) | carries nothing; **does not pass** |

**CI gating is the weak part.** `.github/workflows/ci.yml` has 13 jobs and **runs no workspace `cargo test`**; only `lean-inductive-crosscheck` runs solver proofs. Pushes touching only `docs/**`, `artifacts/**`, `bench-results/**`, `scripts/**` are paths-ignored. The real gate is local: `justfile:58` `check:` (~110 steps).

## 6. FACT LEDGER

`artifacts/facts/` — **696 fact JSON files.** epistemic: `proved` 498, `open` 189, `refuted` 4, `conjectured` 3, `computed` 2. external: `proved` 659, `unknown` 21, absent 8, `open` 5, `refuted` 3. Joint `(open, proved)` = **177** — the ledger's dominant "open" case is *axeyum hasn't done it, mathematics has*: a parity backlog, not a research frontier.

Facts that would be NEW results: `F-rado-r4-a5-b4.json` (`computed`/`open`, R₄(5(x−y)=4z)=741 — "no published value existed"), `F-rado-r4-a5-b3.json` (625), three GF(2) closed-form/classification facts at `proved`/`unknown`, one `refuted`/`unknown`. Everything else in the `unknown` bucket is self-referential (properties of axeyum's own kernel) or a queue of synthetic Mathlib mutations.

Companion claim ledger `artifacts/claims/` — 104 claims (`offdiag-schur` 48, `rado` 43, `vdw` 13). **`novelty: new` 21**: 18 off-diagonal Schur numbers plus 3 Rado cells. 266 evidence rows: `checked` 262.

Schema for a new fact (`artifacts/ontology/fact.schema.json`): required `schema_version, id, title, statement, formal{language,statement,fragment}, epistemic_status, depends_on, evidence[{id,kind,supports,check_status}], provenance{date}`; optional `external_status, proof_route, axiom_footprint, concept_refs, notes, supersedes`.

## 7. SCALE LIMITS

Admission control defaults all `None` (`backend.rs:366-385`). Hard-coded caps: `INPROCESS_MAX_CLAUSES = 16_000_000` (`sat_bv_backend.rs:1056`); `WORD_ROUTE_MAX_NODES = 200_000`; `MAX_MILP_NODES = 2_000`; MBQI caps; `PRE_SOLVE_ALETHE_MAX_NODES = 2_000`.

**SAT core.** Default is the `rustsat-batsat` adapter; `native_cdcl` defaults **false**. The in-tree proof-producing CDCL core (`proof_sat.rs`) is 1-UIP + two-watched-literal, every learned clause RUP by construction; its own doc: *"a proof/correctness reference; the fast default solving path remains the rustsat-batsat adapter"*; `prove_unsat` doc: *"not scalable."*

**Incremental path exists but is not proof-producing.** `grep -c assum proof_sat.rs` returns **0** — the proof core has no assumption interface (confirmed in ADR-0543). Warm-and-fast **or** proof-carrying, not both.

**DRAT checking memory** (`drat_resource.rs`, ADR-0426): backward checking footprint *assumed* 1.5× proof size, **measured 6.6× on a 1.87 GB certificate and 8.0–10.0× on the four largest.** *"A host with 26 GiB of RAM cannot re-check a 5 GB proof, and the way it finds out is the OOM killer… An OOM kill is indistinguishable from a refuted claim."*

**Existence proof at scale.** `artifacts/claims/rado/rado-r4-a5-b3/claim.json`: `p cnf 2500 224248`; **220,077,720 DRAT steps, 19.9 GB, 8,762 s search; checked in 14,499.6 s** — *"CHECKING COST MORE THAN SEARCHING."* First attempt destroyed by `systemd-oomd` at 83.6 GB peak.

## 8. GAPS — what a large search hits first

1. **DRAT checking and LRAT elaboration, not search.** `F-fp16-add-monotone-rne.json`: 24.2 s search → 193 MB proof → >3 hours of check + elaborate. *"What scales badly is elaboration in proof size."*
2. **Memory via the 6.6–10× multiplier**, failing as an OOM kill that looks like a refutation.
3. **LRAT is a dead end above trivial sizes** — RAT steps inexpressible; BVE emits them.
4. **Slow engine required for a proof at all, and no assumption interface** — every cube pays full startup.
5. **Encoding-stage ceilings** with no admission control by default.
6. **Cube-and-conquer composition is designed but `proposed`** (ADR-0543); `axeyum-search`'s harness works for the colouring family.
7. **Scratch filesystem** — `/tmp` tmpfs fills.
8. **Nothing of this is in CI.**

### Where the reach actually is

The stack has *already produced* new results in exactly one shape: **finite Ramsey-type colouring numbers via SAT + self-checked DRAT + independent witness replay.** The reconstruction layer will *not* turn such a search into a theorem: `BoundedIntBlast` and the enumeration routes are `StructuralAttestation`, and there is no route from a cube cover to a kernel term. The 1,191 axiom-free kernel theorems are an elementary-arithmetic library, not a base for Ramsey theory. So: combinatorial search with checkable-but-unreconstructed DRAT evidence is in reach and proven. Anything requiring a *kernel-level* proof of a nontrivial mathematical statement, or high-degree/large-coefficient algebra, is not.
