# Program relations

## A0 equivalence

Generate equivalence queries from executable A0 semantics. A satisfiable model
must decode into a complete allowed initial state and replay into two traces
whose observations differ. An unsatisfiable result retains the trust class of
its actual evidence route.

## Real instruction refinement

Relate one selected RV64 or x86-64 step to an A0 operation. The relation names
inputs, outputs, scratch state, memory, program locations, condition state, and
outcomes. Removing an observed component supplies a control when it creates a
known counterexample.

## Cross-ISA simulation

Cross-ISA work composes two real-to-A0 relations. It does not compare unrelated
handwritten formulas. Different numbers of steps are permitted at declared
simulation boundaries.

## Scalar minimality

Begin with a tiny A0 language printed extensionally. Bind candidate syntax to
A0 semantics and a separate cost function. A witness supplies the upper bound;
coverage of every cheaper well-formed candidate supplies the lower bound.

Only after that route works may the project define scalar RV64 and x86-64
languages over their source-pinned decoded forms.
