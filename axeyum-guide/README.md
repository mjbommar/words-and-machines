# Axeyum route for the revised book

This guide follows the semantic order of the book:

1. A0 words, state, memory, decoding, steps, and traces;
2. source-pinned RV64 and x86-64 adapters;
3. equivalence and cross-machine refinement;
4. bounded scalar languages and costs; and
5. manifests, controls, certificates, and reproduction.

The sibling checkout now has complete concrete A0 words, state, memory,
encoding, decoding, steps, and bounded traces. Its first source-derived
symbolic route proves addition result and conditions at all eight supported
fixed widths with DRAT and LRAT. Its source-pinned twelve-form RV64I slice now
has executable decoder/step evidence and failing controls. The seventeen-form
x86-64 slice now does too. It does not yet have cross-machine relations. No guide page may describe
a planned route as an implemented capability.

The reader-facing Python projection covers the complete concrete A0 surface:
words, finite memory, complete states and their canonical codec, all seventeen
instruction families, categorized traps, steps, and bounded traces. The book
executes its Chapter 6 listing through that interface. The source-pinned RV64I
and x86-64 slices also expose complete selected single-step Python projections.
A typed Rust relation now replays the three printed absolute-value routines for
ten distinct boundary and branch-shape inputs. Universal cross-machine proofs,
the Chapter 15 XOR relation, and Python relation projection remain open.

The old vector-shuffle and Bitmanip guide is preserved in the research archive
and has no authority over active objects.

The active pages cover the current boundary, A0, real-ISA adapters, program
relations, evidence manifests, and reproduction in that order.
