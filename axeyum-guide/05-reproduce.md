# Reproduction

## Valid now

From the book repository root run make ledger, make artifact-check, make check,
and make check-run.

`make check-run` also invokes `make machine-example-check`. It uses
`$(AXEYUM)/.venv/bin/python` to execute all eight A0 listings from their exact
printed text, the exact Chapter 6 A0 Python listing, and the exact Chapter 14
manifest-interface listing. It assembles and decodes all seven RV64 and six
x86-64 listings and executes every listed real-ISA program. The unresolved
`helper` in each non-leaf listing is
linked to a return-only harness stub; the surrounding frame and continuation
effects remain the subject of the test. A wrong A0 result and an assemblable
but unsupported x86 instruction must fail. Before the first run, build the sibling editable
package from a clean worktree of current Axeyum `main`. Do not infer
compatibility from the directory name: a sibling checkout may be on an older
research branch while retaining stale build output.

```sh
git -C ../axeyum fetch origin main
git -C ../axeyum worktree add /path/to/axeyum-book-replay origin/main
cd /path/to/axeyum-book-replay
uv sync --dev
TMPDIR=/path/on/disk uv run --no-sync maturin develop
cd /path/to/words-and-machines
AXEYUM=/path/to/axeyum-book-replay make axeyum-checkout-check
AXEYUM=/path/to/axeyum-book-replay make machine-example-check
```

The active ledger contains twenty checked evidence routes: fourteen A0
routes, two RV64 routes, two x86-64 routes, and two cross-machine routes.
`make check-run`
recomputes the finite byte, word-operation, complete-state codec, observation,
addition-step, memory, branch,
runner, decoder, and step-coverage reports. It also rebuilds and checks the
fixed-width addition and memory-frame certificates. It also regenerates and
checks finite A0 equivalence with decoded-model replay, the bounded A0
scalar-minimality report, both official source pins, both real-ISA decoder/step
reports, the cross-machine absolute-value report, and the complete-program
three-machine XOR report. Every
route runs a negative control and
requires a nonzero exit with `semantic-mismatch`.

The certificate route checks eight separate widths. It does not run an
arbitrary-width kernel proof. The minimality and cross-machine routes are
finite computations within their declared scopes, not universal semantic,
minimality, or refinement theorems. Real-ISA candidate-language packages and
symbolic certification of the Chapter 15 routine remain open.

## Promotion checklist

The first artifact followed this checklist. Apply it again to every new route:

1. inspect and record the sibling Axeyum revision;
2. build the relevant release route;
3. generate a versioned semantic package;
4. create the claim manifest and raw digests;
5. bind the manifest from the active object record;
6. run the positive checker;
7. run the negative control and confirm its failure class;
8. run the full object and artifact gates; and
9. make the chapter evidence wording match the manifest.

Each artifact pins the Axeyum revision that produced it. The replay checkout
may be a descendant of that revision, but the semantic-source digest must
still match exactly; a later incompatible semantic edit therefore fails
closed instead of inheriting credit. The A0 manifests pin compatible ancestors
through `9bb3dd9ba07fc35d1d7f417556dadc27793cd8f3` and semantic package v10.
The RV64 manifests pin Axeyum revision
`b6f3a543b3cd2b418501927d615190b6821a241e`. The x86-64 manifests pin
`1cb53b9a940a4cc685b910441cb16b0dbb03fae5`.

The old reproduction commands for vector shuffles and Bitmanip tables are in
the research archive. They are not part of the active gate.
