# Program relations

## A0 equivalence

The first route binds the Chapter 11 `movi r0,0` and `xor r0,r0,r0` bytes,
width, one-step bound, precondition, observation, and finite state family. It
exhaustively executes the declared width-eight states. A mismatch model is a
canonical complete A0 state that must decode and replay into the same two
successors and first observed difference. Equivalent verdicts carry only the
declared finite computation scope; they are not solver certificates or
width-parametric theorems.

## Real instruction refinement

Relate one selected RV64 or x86-64 step to an A0 operation. The relation names
inputs, outputs, scratch state, memory, program locations, condition state, and
outcomes. Removing an observed component supplies a control when it creates a
known counterexample.

## Cross-ISA simulation

Cross-ISA work composes two real-to-A0 relations. It does not compare unrelated
handwritten formulas. Different numbers of steps are permitted at declared
simulation boundaries.

## Three-machine XOR reduction

The Chapter 15 route executes the exact 44-byte A0, 36-byte RV64I, and 21-byte
x86-64 listings through their separate step functions. It retains entry,
loop-head, after-combine, and terminal states and checks nine typed clauses.
Eight named lists of length zero through three exercise the empty path,
identity, high bit, byte order, cancellation, overlapping bits, backward edge,
and three-word fold. Changing RV64I's pointer increment from eight to one must
fail at the second loop head.

This is a finite concrete relation. The reader invariant carries the universal
loop argument. Symbolic certification, arbitrary addresses, timing,
optimization, and minimality remain outside the artifact.

## Scalar minimality

Begin with a tiny A0 language printed extensionally. Bind candidate syntax to
A0 semantics and a separate cost function. A witness supplies the upper bound;
coverage of every cheaper well-formed candidate supplies the lower bound.

The first route now does exactly this for the Chapter 13 width-eight `x + 2`
case. It enumerates all 1, 6, and 36 programs at instruction costs zero, one,
and two from the printed six-instance alphabet, executes each over all 256
inputs, and retains complete behavior and witness digests. The language-
omission control changes both identity and cardinality; a separate witness
mutation fails at input one. This is direct finite execution, not a solver
certificate or an arbitrary-width result.

Only after that route works may the project define scalar RV64 and x86-64
languages over their source-pinned decoded forms.
