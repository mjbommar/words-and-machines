# Clean-sheet Axeyum evidence design

This is the target evidence architecture for the book. It is a design, not a
claim about current Axeyum capability.

## Dependency graph

```text
words -> A0 state and memory -> A0 step -> A0 traces
                                      -> equivalence and minimality
RV64 decode and step ----\
                          -> state relations -> cross-ISA refinement
x86-64 decode and step --/
```

A handwritten formula may prove that formula. It may not stand in for a
decoder, instruction semantics, or architectural state model.

## Semantic packages

- `a0-words`: modular values, readings, bit operations, byte split/join.
- `a0-state`: registers, byte memory, PC, conditions, outcomes, observations.
- `a0-step`: decoded instructions, read/write sets, step and trap rules.
- `a0-run`: bounded traces, halt, trap, bound exhaustion, continuation.
- `rv64-slice`: source-pinned decoder and semantics for selected RV64 forms.
- `x86-64-slice`: source-pinned decoder and semantics for selected 64-bit
  forms, including lengths, implicit effects, flags, and addresses.
- `machine-relations`: typed A0/RV64/x86-64 state relations that declare
  input, output, scratch, memory, PC, flag, and outcome components.

Definitions carry versions, provenance, and canonical digests. They are inputs
to claims, not evidence that a claim holds.

## Evidence classes

1. **Example trace:** initial state, decoded instructions, every step, final
   outcome; checker recomputes it from semantics.
2. **Finite computation:** exact domain, enumerator, count, result digest, and
   independent reproduction where available.
3. **Solver query:** semantic digests, reader statement, generated formula,
   expected verdict, model decoder, and counterexample replay.
4. **Certificate:** exact formula, exported refutation, independent checker,
   and damage control.
5. **Kernel reconstruction:** source semantics, theorem, route, kernel version,
   and term digest without any widening of scope.

## Manifest contract

Every active machine claim points to one versioned manifest containing:

- stable claim ID and schema version;
- human statement, scope, and exclusions;
- source and semantic-package digests;
- artifact paths and raw digests;
- producer and checker commands with versions;
- expected positive result;
- negative control and expected failure class;
- trust class: trace, computation, verdict, certificate, or kernel;
- reproducibility environment; and
- known limitations.

The manifest is the interface to `../axeyum`. The book must not infer assurance
from ad hoc solver logs.

## Required controls

| Route | Control |
|---|---|
| Word | wrong edge result or width |
| State | omitted observed component |
| A0 step | wrong destination, hidden write, or PC increment |
| Memory | reversed byte order or invalid range accepted |
| Trace | wrong branch target or execution after trap |
| RV64 decode | field mutation or illegal encoding accepted |
| x86-64 decode | prefix/opcode/modifier mutation or wrong length |
| ISA refinement | one related source/target state made unequal |
| Equivalence | concrete counterexample must replay |
| Certificate | truncation or clause mutation |
| Minimality | known cheaper witness invalidates the lower bound |

Checkers must distinguish semantic mismatch, malformed data, digest mismatch,
unexpected verdict, and control failure.

## First flagship sequence

1. A0 byte split/join round trip.
2. A0 addition, including flags and PC update.
3. A0 load/store round trip and trapped boundary.
4. A0 conditional-branch trace.
5. One RV64 arithmetic instruction refining A0.
6. One x86-64 arithmetic instruction refining A0 under a declared observation.
7. One short scalar routine in all three machines.
8. Cross-ISA refinement for that routine.
9. Tiny A0 scalar minimality under a printed language.

No vector-extension result belongs in this sequence.

## Legacy migration

Existing vector-shuffle and old Bitmanip artifacts do not migrate into the new
active ledger. If kept for provenance, they move to a marked research archive
and lose all chapter and status bindings. Their formats may teach engineering
lessons; their IDs and assumptions do not define the new schema.

## Completion conditions

The redesign is implemented only when:

1. the active ledger contains no legacy machine-result object;
2. every active machine claim depends on source-pinned semantic packages;
3. both real slices have decoder and step controls;
4. counterexample models replay through executable semantics;
5. each flagship UNSAT claim has independent checking or a narrower trust
   label;
6. every route has a firing negative control;
7. the full gate runs from a clean current-main checkout after
   `AXEYUM=/path/to/axeyum make axeyum-checkout-check`; and
8. chapter prose matches each manifest's trust class and boundary.

Until all eight hold, this file remains a roadmap.
