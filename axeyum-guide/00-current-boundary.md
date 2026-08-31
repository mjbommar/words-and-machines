# Current capability boundary

The sibling Axeyum checkout now contains a reusable `axeyum-machine` package
for A0 architectural words, state, finite byte memory, instruction effects,
canonical encoding and strict decoding, complete concrete steps, and bounded
traces. Its word layer includes explicit zero extension, sign extension, and
truncation, and complete states have a canonical binary codec.
`axeyum-machine-evidence` produces sixteen book routes and their negative
controls. Twelve cover A0. Two pin and execute the twelve-form RV64I slice.
Two more pin and execute the seventeen-form x86-64 slice, including all six
x86-64 manuscript listings, variable lengths, flags, memory, and implicit
stack control. The addition and
memory-frame routes construct symbolic terms through
the same operation structures used by concrete execution and save term-bound
DRAT and LRAT certificates. The memory route also rechecks array elimination
and its select-congruence witness.

Axeyum still does not contain typed cross-ISA refinement or an A0 symbolic
theorem for every operation. The real-ISA routes are finite executable
evidence, not universal refinement theorems. The addition certificates are eight
fixed-width theorems, not one arbitrary-width kernel theorem.

These distinctions govern every active claim:

- a bit-vector formula is not an instruction semantics;
- an instruction semantics is not a decoder;
- a decoded single step is not a program trace;
- matching destination words are not cross-machine refinement;
- a solver verdict is not an independently checked certificate; and
- a checked clausal certificate does not remove the symbolic-adapter or
  term-to-CNF trust boundary;
- an old synthesis artifact is not evidence for the revised curriculum.

Before promoting any obligation, inspect the current checkout, identify the
crate and public interface, run focused positive tests and a negative control,
and record the exact revision in the evidence manifest.
