# RV64 and x86-64 adapters

Real-ISA work begins with sources, not code.

## Source manifest

Each adapter records an authoritative document revision, archived source,
selected state, selected instruction forms, encoding rules, normal effects,
exceptions, and exclusions. ABI sources remain separate from ISA sources.

## Decoder

The RV64 decoder covers only selected base forms and rejects encodings outside
that set. The x86-64 decoder returns the consumed length and exposes the exact
selected prefix, opcode, operand, and addressing forms.

Each decoder is compared against an independent implementation or authoritative
test vectors. Field, opcode, prefix, modifier, and length mutations are
negative controls.

## Step adapter

The RV64 adapter exposes x0 behavior, program-counter changes, memory effects,
and outcomes. The x86-64 adapter exposes implicit operands, selected flags,
subregister effects, address formation, length-dependent RIP changes, memory,
and outcomes.

The first refinement target is one scalar arithmetic instruction on each
architecture. No adapter claim may be inferred from an existing custom
synthesis encoder.
