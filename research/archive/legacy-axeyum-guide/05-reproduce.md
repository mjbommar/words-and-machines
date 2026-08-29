# 05 — Reproduce everything

## Without axeyum (pure Python, ~70 s)

```sh
make reproduce        # RISC-V bitlogic table (1.5 s) + Bitmanip permutation tables (~65 s)
make check            # schema + semantic validation of every object record
make ledger           # regenerate objects/LEDGER.md and the book's status macros
```

`scripts/bitlogic_bfs.py` exits 0 only if all 512 table entries reproduce; `scripts/byte_perm_bfs.py` exits 0 only if the 24-permutation bound *and* both rows of Table 2.2 reproduce. Both write JSON reports into `artifacts/riscv/`.

## With axeyum prebuilt binaries (~2.5 min)

```sh
export AXEYUM=~/projects/personal/axeyum      # a checkout with target/release/examples built
make check-run
```

This executes every `checker_command` and every `negative_control`:

| Objects | Binary | What runs |
|---|---|---|
| `W.thm.*`, `I.thm.popcount32`, `W.ctl.*` | `smtcomp_cli` | decides five QF_BV files; four must be `unsat`, the control `sat` |
| `M.avx2.reverse.len2.unary5` | `synthesize_unary_avx2` | hash check → regenerate CNF → check DRAT → **UP-refutability test** (declared vacuous); negative control: empty DRAT must be rejected |
| `M.avx2.reverse.cost4.haswell` | `synthesize_weighted_unary_avx2` | hash → regenerate → check 12.5 MB DRAT → 2-byte truncation must be rejected |
| `M.avx2.reverse.len2.ssa14` | `synthesize_multisource_avx2` | same, 1.9 MB DRAT |
| `C.thm.vacuous-certificate` | — | UP conflicts on the unary CNF; negative control: UP reaches fixpoint on the SSA CNF |
| `M.riscv.*` | — | the two BFS scripts |

Verified 2026-08-27: 34 objects, 0 problems, all negative controls fired.

## Building the binaries

```sh
cd $AXEYUM
scripts/cargo-serialized.sh build --release -p axeyum-search --examples
scripts/cargo-serialized.sh build --release -p axeyum-solver --example smtcomp_cli
```

Use the serialized wrapper on a shared host: it takes a host-wide flock and runs under a cgroup with **both** `MemoryMax` and `MemorySwapMax`. Cargo decides freshness by mtime, so a checkout extracted with `git archive` needs `scripts/lane-snapshot.sh` (which passes `--touch`) or the build will silently skip stale files.

## Regenerating a certificate from scratch

```sh
B=$AXEYUM/target/release/examples
$B/synthesize_multisource_avx2 reverse 1 120 --dimacs reverse-k1.cnf
cadical --no-binary --seed=1223 reverse-k1.cnf reverse-k1.drat     # exit 20 = UNSAT
$B/synthesize_multisource_avx2 reverse 1 120 --check-drat reverse-k1.drat
python3 scripts/up_refutes.py reverse-k1.cnf                          # exit 1 = load-bearing proof
```

Different seeds give different (all valid) proofs; the CNF is deterministic and its SHA-256 is the pin.

## Building the book and paper

```sh
make book     # book/Makefile pdf  — TeX Live (LuaLaTeX, latexmk, biber), uv, poppler
make paper    # paper/Makefile pdf
```

`make -C book doctor` audits the toolchain. The book's status boxes read `book/latex/preamble/objects-generated.tex`, written by `make ledger`; **never edit it.**
