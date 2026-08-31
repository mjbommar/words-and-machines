# Reproduction

## Valid now

From the book repository root run make ledger, make artifact-check, make check,
and make check-run.

`make check-run` also invokes `make machine-example-check`. It uses
`$(AXEYUM)/.venv/bin/python` to execute the exact Chapter 6 A0 Python listing,
assemble and decode all seven RV64 and six x86-64 listings, and execute every
listed real-ISA program. The unresolved `helper` in each non-leaf listing is
linked to a return-only harness stub; the surrounding frame and continuation
effects remain the subject of the test. A wrong A0 result and an assemblable
but unsupported x86 instruction must fail. Before the first run, build the sibling editable
package from the selected Axeyum checkout:

```sh
cd ../axeyum
uv sync --dev
TMPDIR=/path/on/disk uv run --no-sync maturin develop
cd ../words-and-machines
AXEYUM=../axeyum make machine-example-check
```

The active ledger contains sixteen checked evidence routes: twelve A0 routes,
two RV64 routes, and two x86-64 routes. `make check-run`
recomputes the finite byte, word-operation, complete-state codec, observation,
addition-step, memory, branch,
runner, decoder, and step-coverage reports. It also rebuilds and checks the
fixed-width addition and memory-frame certificates. It also regenerates and
checks both official source pins and both real-ISA decoder/step reports. Every
route runs a negative control and
requires a nonzero exit with `semantic-mismatch`.

The certificate route checks eight separate widths. It does not run an
arbitrary-width kernel proof, cross-ISA, or minimality route; those remain
open. The real-ISA computations are not universal semantic or refinement
theorems.

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
