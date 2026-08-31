# RV64 and x86-64 adapters

Real-ISA work begins with sources, not code. Both selected routes described
here are implemented and replayable.

## Source manifest

Each adapter records an authoritative document revision, archived source,
selected state, selected instruction forms, encoding rules, normal effects,
exceptions, and exclusions. ABI sources remain separate from ISA sources.

## Decoder

The RV64 decoder covers only selected base forms and rejects encodings outside
that set. The x86-64 decoder returns the consumed length and exposes the exact
selected prefix, opcode, operand, and addressing forms.

The RV64 decoder is checked against thirteen exact words printed in the book,
including the complete XOR program, and against canonical re-encoding. The
source-digest and taken-branch-base mutations are active negative controls.
Independent differential decoding remains a stronger future check. The x86-64
route checks twenty-eight fixed instruction records, variable lengths, all six
manuscript programs, and source-digest and following-RIP branch controls.

## Step adapter

The RV64 adapter exposes x0 behavior, program-counter changes, memory effects,
and outcomes. The x86-64 adapter exposes implicit operands, selected flags,
subregister effects, address formation, length-dependent RIP changes, memory,
and outcomes.

The RV64 executor steps every selected form and checks its architectural
effect. It runs the printed XOR loop on three inputs, distinguishes five trap
classes, and exposes a canonical refinement-facing projection. This is finite
execution evidence, not a universal refinement result.

The x86-64 executor covers all seventeen selected form families. It preserves
defined and undefined flag results, partial-register clearing, following-RIP
branch targets, unaligned memory operands, and implicit stack effects. It runs
the XOR, count, leaf, non-leaf, absolute-value, and write-zero examples.

The first cross-machine refinement target is one scalar arithmetic instruction on each
architecture. No adapter claim may be inferred from an existing custom
synthesis encoder.
