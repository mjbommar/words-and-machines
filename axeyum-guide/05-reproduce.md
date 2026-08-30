# Reproduction

## Valid now

From the book repository root run make ledger, make artifact-check, make check,
and make check-run.

The active ledger now contains one checked finite computation and one checked
trace. `make check-run` recomputes every 8- and 16-bit A0 byte round trip and
the declared narrow-versus-broad state observation. It requires both the
reversed-byte-order control and the requested-component-omission control to
exit nonzero with a semantic mismatch. It does not run any general-width
proof, RV64, x86-64, cross-ISA, or minimality route because those remain open.

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
closed instead of inheriting credit. Until this work reaches Axeyum `main`,
set `AXEYUM` to the published `book/executable-curriculum` branch.

The old reproduction commands for vector shuffles and Bitmanip tables are in
the research archive. They are not part of the active gate.
