# 01 — Words: the Prologue's carrier, and what axeyum has and lacks

## What the book needs

`Word n` as the ring ℤ/2ⁿℤ, constructed — not assumed — with bitwise operations defined from the binary expansion and the SMT-LIB totality conventions (`bvudiv x 0 = all-ones`, `bvurem x 0 = x`, …) as *theorems*. Spivak's Prologue gives thirteen axioms for ℝ; the book's Prologue gives **zero**, because words are built on the naturals.

## What axeyum has

- The `nat` prelude in `crates/axeyum-lean-kernel/src/nat_prelude*.rs`: 351 theorems, **0 axioms** (Axiom/Opaque/Quotient all zero per the generated `lean-axiom-ledger.md`), including `modular.rs`, `division.rs`, `binary.rs`, `fermat.rs`, `euler.rs`, `group.rs`. ℤ/2ⁿ arithmetic is reachable through `Nat.mod`.
- QF_BV is the foundation layer: `decides` with proof `checked` in the support matrix; the `QfBv` reconstruction route is `TheoryReconstruction` (the kernel checks it on the merits).
- Every rendered natural prints as `AxNat` — that is `lean_pp`'s non-shadowing root for the **constructed, inductive** naturals, not an axiomatized carrier. (The `Ax` means *axeyum*; `AxReal` is the one axiomatized package, at 30 assumptions, and nothing shipped reaches it.)

## What axeyum lacks

- **No `word_prelude`.** `BitVec w` exists only as `bv_value_types: BTreeMap<usize, DatatypeInductive>` built on the fly inside `ReconstructCtx` (`crates/axeyum-solver/src/reconstruct.rs` ~line 370). Each proof gets its own copy; no theorem about words survives one reconstruction to the next. There are no `Nat.land/lor/xor/shiftl/testBit` declarations in the nat prelude to build on either.

## The first increment (`OP.kernel.word-prelude`)

1. `word_prelude.rs`: `Word n := Nat mod 2^n`; ring laws from the nat prelude; `testBit`, `and`, `or`, `xor`, `shl`, `lshr` by definition; the four totality theorems of the Prologue as kernel theorems.
2. Re-point `bv_value_types` at the prelude so `QfBv` reconstructions accumulate.
3. Add a `machines` volume to `docs/curriculum/curriculum.toml` with a `words` node (layer 1, `axeyum_theory = "QF_BV"`, `decidability = "decidable"`) — the curriculum is a validated prerequisite DAG and the `modular-arithmetic` node already exists to hang it on.

Before naming anything, run `prelude_theorem_inventory --include-constructed --release` across the **whole** inventory: a prelude may declare into another's namespace, and a clash surfaces only when a downstream prelude builds (230 failures that name a `NameId`, not a string).

## How the Prologue's theorems are checked today

By the front door, not the kernel: see [02-equivalence.md](02-equivalence.md). The objects `W.thm.udiv0`, `W.thm.urem0`, `W.thm.sdiv0` are `proved` with `front-door-verdict` evidence. When the word prelude lands, they should be re-admitted as kernel theorems and their evidence rows upgraded to `kernel-term`.
