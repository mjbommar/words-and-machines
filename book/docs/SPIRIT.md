# SPIRIT — why this book exists

Read this before drafting a sentence.

**The one quotable sentence.** Every machine claim is an object; every
machine-backed claim has evidence and a checker that can fail.

**What the reader should feel.** The quiet shock Spivak gives on page 9: a
familiar fact becomes a theorem, and proving it teaches something the assertion
did not. In this book, wraparound, byte reconstruction, instruction effects,
and program replacement receive that treatment.

**How the reader gets there.** Begin with a machine problem they can picture
or try. Let the obstruction become visible before naming it. Then give the
exact definition, a human-scale proof, the machine-checkable evidence, an
attack the checker must reject, and the boundary of the result. The symbols
compress the idea; they do not replace the idea.

**What it is not.** Not a survey of open problems. Not a paper about a solver.
Not a Lean tutorial. It is a book whose machine-backed claims will carry
evidence that a reader can attack, and whose status words are generated rather
than typed.

**Threads.** (1) Words and machine state are constructed before any particular
ISA appears. (2) RISC and CISC are families of design choices, not substitutes
for semantics; compare explicit and implicit operands, memory effects,
encodings, flags, and extensions one feature at a time. (3) An instruction is
a function; equivalence is a ∀, minimality is a ¬∃ — and the second has never
been certified in this field. (4) The asymmetry: improvement is cheap to check,
optimality is not, except in three shapes. (5) A proof can be vacuous and still
be accepted; the book found one in its own artifacts. (6) ISA design documents
in Part IV rest on uncertified exhaustive searches — and the machinery to
certify them fits in an appendix.

**Register.** Precise, dry, occasionally amused. Warmth comes from working
beside the reader, not from cheerleading. Read-aloud test: kitchen-table for
the prose, blackboard for the mathematics, workbench for the artifacts.

**The two proofs.** A load-bearing theorem needs a reader proof and a machine
proof. The reader proof supplies understanding: a small case, invariant,
contradiction, or replay a person can follow. The machine proof supplies
coverage: a scoped artifact and a checker that can fail. Neither is enough by
itself. A computation receives a reader explanation and checked reproduction;
the book does not promote it to a proof.
