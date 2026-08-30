# Chapter 11 sources and claim routes

## Historical and mathematical foundations

- Robert W. Floyd, “Assigning Meanings to Programs” (1967), in *Mathematical
  Aspects of Computer Science*, Proceedings of Symposia in Applied Mathematics
  19. Use for assertions attached to control points and a rigorous basis for
  correctness, equivalence, and termination. Do not imply that Floyd supplied
  the later industrial translation-validation architecture.
- C. A. R. Hoare, “An Axiomatic Basis for Computer Programming” (1969). Use
  for precondition/postcondition reasoning and compositional program proofs.
- Standard transition-system and simulation literature. Use primary sources
  for the exact direction and hypotheses of forward simulation, backward
  simulation, bisimulation, and refinement. Do not treat these terms as
  interchangeable.
- Amir Pnueli, Michael Siegel, and Eli Singerman, “Translation Validation”
  (1998), LNCS 1384, pp. 151--166, DOI `10.1007/BFb0054170`. Use for checking
  individual compiler runs as an alternative to proving the entire compiler.
- Xavier Leroy, “Formal Verification of a Realistic Compiler” (2009),
  *Communications of the ACM* 52(7), pp. 107--115, DOI
  `10.1145/1538788.1538814`. Use for semantic preservation across a realistic
  verified compiler and the distinction between compiler proof and one-run
  validation.
- Nuno P. Lopes et al., “Alive2: Bounded Translation Validation for LLVM”
  (PLDI 2021), pp. 65--79, DOI `10.1145/3453483.3454030`. Use for modern
  bounded translation validation, SMT-backed refinement, explicit limits, and
  reported LLVM defects. Preserve the paper's boundedness and unsupported-case
  limits.

## Architecture and language authorities

- The book's pinned A0 semantics for complete-state examples and mutation
  controls. No current artifact yet implements those semantics.
- RISC-V unprivileged ISA and current psABI for selected scalar instruction and
  call-boundary effects. Equivalence claims must name the admitted extension
  and alignment/memory premises.
- Intel Software Developer's Manual and one named x86-64 ABI for selected
  instruction, flag, stack, and procedure observations.
- LLVM Language Reference for poison, `undef`, immediate undefined behavior,
  and refinement-sensitive examples. Pin the revision: these semantics and
  their wording evolve.

## Industrial and economic routes

- Compiler validation papers and official tool documentation for the cost of
  checking individual transformations, unsupported constructs, timeouts, and
  counterexample triage.
- Verified-compiler primary literature for proof-maintenance and trusted-base
  comparisons. Avoid unsourced claims that one approach is categorically
  cheaper or safer.
- Cryptographic implementation papers for observations that include timing or
  address traces. Chapter 11 should motivate them but route the full leakage
  model to Chapter 16.
- Safety standards only if the chapter makes a concrete certification or
  qualification claim. Current industry discussion should otherwise remain
  about actors and costs rather than unsourced market totals.

## Textbook coverage comparison

- Derrick and Boiten, *Refinement: Semantics, Languages and Applications*
  (Springer, 2018) develops labeled transition systems, automata and
  simulations, state-based refinement, and relational refinement. It is the
  depth reference for the chapter's order and simulation foundations. This
  book takes only the scalar-machine slice needed for later cross-ISA proofs.
  Publisher source: <https://link.springer.com/book/10.1007/978-3-319-92711-4>.
- de Roever and Engelhardt, *Data Refinement: Model-Oriented Proof Methods and
  their Comparison* develops simulation as a proof method, relations,
  recursion, Hoare logic, total correctness, and refinement calculus. It is a
  comparison for proof-rule depth and for the warning that a simulation rule
  has hypotheses. Chapter 11 adds executable ISA witnesses and modern compiler
  validation rather than attempting the book's full data-refinement theory.
  Publisher source:
  <https://www.cambridge.org/core/books/data-refinement/simulation-as-a-proof-method-for-data-refinement/2506C080E5B1D6BCA1C8A8849B94F152>.

## Live Axeyum audit, 2026-08-30

Inspected `../axeyum` at revision
`a9991fdad6c1e4b2bda596b46d2c8c715556ceae` on branch
`research/open-problems-2026-08`.

The inherited manuscript's statement that Axeyum only has generic bit-vector
infrastructure is stale. `crates/axeyum-verify/tests/cross_ir_equivalence.rs`
reflects selected Rust MIR and LLVM IR into one `axeyum-ir` arena over shared
input symbols. It proves equality for selected scalar fixtures, checks LLVM
definedness, and independently evaluates chosen samples. Cases include
straight-line algebra, signed shifts, branch-to-select conversion,
strength reduction, switches, and hypothesis-conditioned equivalence.

`cross_ir_refutation.rs` supplies the discriminating negative half. It requires
wrong transforms to return a countermodel and evaluates both reflected terms at
that input to confirm a real difference. Mutations include an off-by-one shift,
logical-for-arithmetic shift, flipped select arms, dropped mask, and signedness
error. Related checked LLVM CFG and source-contract tests add defined-operation
conditions, structured control, and modular scalar calls.

This is real translation-validation substrate, not the chapter's complete
machine-program route. The checked profile is selected scalar MIR/LLVM, not A0,
RV64, or x86-64 bytes. The tests primarily compare result terms and selected
definedness conditions, not the chapter's configurable architectural
observations over registers, flags, memory, traps, continuations, and traces.
The repository has no book A0 state/decoder/runner, no source-pinned real-ISA
decoder adapters for this claim, and no general cross-ISA refinement manifest.
The chapter must present the implemented route accurately and stage the missing
adapters without claiming they already exist.
