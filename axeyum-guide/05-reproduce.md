# Reproduction

## Valid now

From the book repository root run make ledger, make artifact-check, make check,
and make check-run.

At this stage the active ledger contains definitions and implementation
obligations but no machine-proof artifact. The runtime gate therefore executes
zero evidence routes. That is an honest empty result, not proof of the planned
semantics.

## Promotion checklist

Before the first artifact becomes active:

1. inspect and record the sibling Axeyum revision;
2. build the relevant release route;
3. generate a versioned semantic package;
4. create the claim manifest and raw digests;
5. bind the manifest from the active object record;
6. run the positive checker;
7. run the negative control and confirm its failure class;
8. run the full object and artifact gates; and
9. make the chapter evidence wording match the manifest.

The old reproduction commands for vector shuffles and Bitmanip tables are in
the research archive. They are not part of the active gate.
