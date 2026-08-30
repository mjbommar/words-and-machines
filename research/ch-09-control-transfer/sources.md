# Chapter 9 sources

Research ledger opened 2026-08-30. Search results are leads only. Manuscript
claims must rest on opened primary papers, standards, official manuals, or
other authoritative sources.

## Opened origins and foundations

- Turing's 1936/1937 paper for a mathematical machine whose next
  configuration depends on current configuration and scanned symbol. Do not
  describe it as a stored-program ISA.
- Goldstine and von Neumann's 1947 *Planning and Coding* report for flow
  diagrams, induction assertions, and structured reasoning about iterations.
- Böhm and Jacopini's 1966 result and Dijkstra's 1968 letter for the
  structured-control lineage. Keep the mathematical sufficiency result
  separate from later programming-method arguments.
- Floyd's 1967 assignment of meanings to programs and Hoare's 1969 axiomatic
  basis for assertions, invariants, and program proofs.
- Wilkes, Wheeler, and Gill's 1951 EDSAC programming book for closed
  subroutines and the library context. Use it as a documented early method,
  not an unsupported sole-invention claim.
- Frances Allen's 1970 control-flow analysis paper for directed-graph
  codification of flow relationships and compiler optimization questions.
- Lengauer and Tarjan's 1979 dominator paper for the formal dominance relation
  and a historically important fast algorithm. The chapter teaches the
  relation, not the full algorithm.
- James E. Smith's 1981 study for the branch-prediction research lineage.
- Abadi, Budiu, Erlingsson, and Ligatti's 2005 CFI paper for the policy that
  dynamic execution follows a declared control-flow graph under an attack
  model.

## Opened current authoritative sources

- RISC-V ratified unprivileged architecture, version 20260120, for branch,
  JAL, JALR, target alignment, immediate reconstruction, and link behavior.
- Intel 64 and IA-32 Software Developer's Manual, version 092, for Jcc, JMP,
  CALL, RET, relative bases, displacement widths, flags, canonical targets,
  and form-specific behavior.
- Current RISC-V control-flow integrity extension and Intel CET material for
  landing-pad, indirect-branch, and shadow-stack boundaries. State exact
  extension and platform assumptions.
- Intel optimization material for dated, processor-specific prediction,
  branch layout, macro-fusion, and if-conversion considerations.
- Compiler documentation and primary algorithm papers remain to be opened for
  switch lowering.
- Current LLVM machine block-placement source for branch probability, block
  frequency, loop, post-dominator, alignment, and profile-guided placement
  inputs. Treat source-code details as versioned implementation evidence.

## Coverage comparators

- Patterson and Hennessy, *Computer Organization and Design*, for datapath,
  control hazards, prediction, and instruction-level loop coverage.
- Bryant and O'Hallaron, *Computer Systems: A Programmer's Perspective*, for
  x86 condition codes, branches, loops, switch tables, linking, and machine
  control flow.
- Compiler texts for control-flow graphs, dominators, loop recognition,
  if-conversion, block placement, and indirect-branch lowering.
- Program-verification texts for invariants, variants, reachability, partial
  versus total correctness, and simulations.

## Source cautions

- A branch target formula does not prove that target bytes fetch and decode.
- A graph edge absent from sampled traces is not proved unreachable.
- A cycle is not by itself a loop invariant or a proof of nontermination.
- “Branch cost” depends on processor, path history, layout, prediction,
  surrounding work, and observation; avoid one universal penalty.
- Architectural equivalence does not imply equal speculative, timing, cache,
  or power behavior.
- A target set seen in tests has no soundness claim without a source invariant.
- CFI landing pads and shadow stacks enforce selected policies; neither proves
  arbitrary whole-program control-flow correctness.

## Axeyum substrate audit

Inspected sibling repository `../axeyum` at revision
`a9991fdad6c1e4b2bda596b46d2c8c715556ceae` on branch
`research/open-problems-2026-08`. The solver crate provides a symbolic
`TransitionSystem`, bounded model checking, memory-aware bounded checking,
k-induction, certified QF_BV safety paths, and replay-checked counterexample
models. Its `toy_bv_vm` is already a real control-flow teaching substrate:
register/constant and register/register equality branches, explicit true and
false targets, validated programs, static CFG edges and basic blocks, symbolic
exploration, target and edge reachability reports, assembly labels/source
lines, concrete traces, and independent replay.

The checkout still lacks the book's A0 decoder and byte-addressed program
counter, A0 `Z,N,C,V` branch family, exact RV64I/x86-64 decoder adapters, the
three-machine counted-loop relation, dominance/loop proof objects, and the
chapter's publication manifest. The toy VM uses instruction-index targets and
its own outcome/fuel rules; it cannot be relabeled as A0. Existing generic
BMC and certified safety routes are stronger than the inherited manuscript
reported but need a book-specific transition adapter. No Axeyum files were
changed during this audit.
