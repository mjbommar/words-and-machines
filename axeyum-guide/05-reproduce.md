# Reproduction

## Valid now

From the book repository root run make ledger, make artifact-check, make check,
and make check-run.

The active ledger contains ten checked A0 evidence routes. `make check-run`
recomputes the finite byte, word-operation, observation, addition-step, memory, branch,
runner, decoder, and step-coverage reports. It also rebuilds and checks the
fixed-width addition certificates. Every route runs a negative control and
requires a nonzero exit with `semantic-mismatch`.

The certificate route checks eight separate widths. It does not run an
arbitrary-width kernel proof, RV64, x86-64, cross-ISA, or minimality route;
those remain open.

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
closed instead of inheriting credit. The current manifests pin Axeyum `main`
revision `b3efd2ed0edbafa73b0c9fd86906d0019d88d191` and semantic package v7.

The old reproduction commands for vector shuffles and Bitmanip tables are in
the research archive. They are not part of the active gate.
