# Architecture foundation contract

This file is subordinate to `MASTER.md`. It records the acceptance test for
the abstract-ISA and paired-architecture foundation.

## A0 acceptance test

A0 is ready for Parts II and III only when a reader and an executable model
can agree on:

1. the complete state and outcome types;
2. word and byte operations at a chosen width;
3. every operand's value, width, read set, and write set;
4. every core instruction's normal step and trap rule;
5. ordinary and branch program-counter updates;
6. little-endian load/store behavior and range failure;
7. finite traces ending in halt, trap, or a bound; and
8. observations used by equivalence and refinement.

No real-ISA theorem may compensate for a missing A0 rule with an informal
assumption.

## Paired-window acceptance test

Each foundational concept receives one RV64 and one x86-64 window. A window
must name the exact instruction form or state component, governing source
revision, state read and written, normal and exceptional behavior, relation to
A0, and deliberate exclusions.

A window remains explanatory until its source revision and semantics are
pinned. It must not be presented as an Axeyum-backed architectural result
before that route exists.

## Comparison rule

Compare one dimension at a time: instruction length, operand roles, implicit
state, memory access, address formation, control predicates, call mechanisms,
and ABI conventions. Never make “RISC” or “CISC” the cause of a semantic fact.

## Evidence acceptance test

The foundation is machine-backed only when the packages and controls in
`AXEYUM-EVIDENCE.md` exist and run. An object that records missing work does
not establish implementation.
