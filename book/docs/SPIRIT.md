# SPIRIT — why this book exists

Read this before drafting a sentence.

**The one quotable sentence.** In this book nothing is asserted: every claim about a machine is an object with an artifact and a checker that can fail.

**What the reader should feel.** The quiet shock Spivak gives on page 9 — that the obvious thing (1 > 0; that `bvudiv x 0` is all-ones; that byte reversal needs two shuffles) is a *theorem*, and that proving it teaches you something the assertion did not.

**What it is not.** Not a survey of open problems (that is `research/`). Not a paper about a solver (that is `paper/`). Not a Lean tutorial. It is a book whose margins are filled with real certificates, and whose status words are generated, never typed.

**Threads.** (1) Words are constructed, not assumed. (2) An instruction is a function; equivalence is a ∀, minimality is a ¬∃ — and the second has never been certified in this field. (3) The asymmetry: improvement is cheap to check, optimality is not, except in three shapes. (4) A proof can be vacuous and still be accepted; the book found one in its own artifacts. (5) Every ISA design document in Part IV rests on an uncertified exhaustive search — and the machinery to certify it fits in an appendix.

**Register.** Precise, dry, occasionally amused. Read-aloud test: kitchen-table for the prose, blackboard for the objects.
