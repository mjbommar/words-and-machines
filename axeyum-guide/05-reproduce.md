# Reproduction

## Valid now

From the book repository root run make ledger, make artifact-check, make check,
and make check-run.

The active ledger now contains one checked computation. `make check-run`
recomputes every 8- and 16-bit A0 byte round trip, checks the content-bound
report, and requires the reversed-byte-order control to exit nonzero with a
semantic mismatch. It does not run any general-width proof, RV64, x86-64,
cross-ISA, or minimality route because those remain open.

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

The current artifact pins Axeyum revision
`fab80468ed9252e3bf88826c4c2d864c851b9980` on branch
`book/executable-curriculum`. Until that work reaches Axeyum `main`, set
`AXEYUM` to a checkout of that exact revision before reproduction.

The old reproduction commands for vector shuffles and Bitmanip tables are in
the research archive. They are not part of the active gate.
