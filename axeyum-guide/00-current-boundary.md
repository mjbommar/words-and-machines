# Current capability boundary

The redesign audit found reusable bit-vector expressions, solver routes, SAT
and DRAT machinery, custom synthesis encoders, and kernel reconstruction
infrastructure in the sibling Axeyum checkout.

It did not find a reusable package for architectural state, byte-addressed ISA
memory, A0 execution, an RV64 decoder and semantics, an x86-64 decoder and
semantics, or typed cross-ISA refinement.

These distinctions govern every active claim:

- a bit-vector formula is not an instruction semantics;
- an instruction semantics is not a decoder;
- a decoded single step is not a program trace;
- matching destination words are not cross-machine refinement;
- a solver verdict is not an independently checked certificate; and
- an old synthesis artifact is not evidence for the revised curriculum.

Before promoting any obligation, inspect the current checkout, identify the
crate and public interface, run focused positive tests and a negative control,
and record the exact revision in the evidence manifest.
