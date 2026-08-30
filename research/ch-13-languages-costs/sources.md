# Chapter 13 sources and claim routes

## Historical and superoptimization sources

- Henry Massalin, “Superoptimizer: A Look at the Smallest Program” (ASPLOS
  1987). Original PDF read 2026-08-30. The system targets the 68020, orders
  exhaustive search by length and estimated cost, filters with selected test
  values, and reports useful programs commonly 4--13 instructions long. Do not
  convert its historical claim into a modern certificate claim.
- Rajeev Joshi, Greg Nelson, and Keith Randall, “Denali: A Goal-Directed
  Superoptimizer” (Compaq SRC report 171, 2001; PLDI 2002). Original report
  read from Bitsavers 2026-08-30. Use for the overnight-versus-interactive
  compile-time trade, E-graph matching plus SAT, budget search, and the
  authors' explicit near-optimal caveat: matching completeness depends on
  axioms, time, and heuristics.
- Sorav Bansal and Alex Aiken, “Automatic Generation of Peephole
  Superoptimizers” (ASPLOS 2006). Original PDF read 2026-08-30. Use for
  systematic offline peephole superoptimization, harvested targets, finite
  operand/constant choices, register and symbolic-constant canonicalization,
  and approximate processor or byte costs.
- Lubodík et al. (2025) is already cited for current scaling through
  decomposition and parallel search. Recheck the exact claimed scope.

## Prior-art and novelty controls

- Franchetti and Püschel, “Generating SIMD Vectorized Permutations” (Compiler
  Construction 2008), original PDF read 2026-08-30, is a direct antecedent for
  scoped instruction-count optimality: dynamic programming inside a
  rewrite-rule space plus a matching lower bound for selected stride
  permutations. Use it to prevent false “nobody proved machine sequences
  optimal” language.
- Current equality-saturation certificate work may certify minimum additive
  tree cost inside a represented equivalence class. Treat tree extraction,
  DAG extraction, and instruction-sequence search as different problems.
- The archived surveys in
  research/archive/legacy-evidence-research/surveys/06-superoptimization-frontier.md
  and 08-compiler-certification-gap.md are routing aids, not publication
  sources. Reopen every primary source before moving a claim into the book.

## Cost and industrial sources

- Castañeda Lozano et al., “Combinatorial Register Allocation and Instruction
  Scheduling” (TOPLAS 2019; arXiv 1804.02452v5), original PDF read
  2026-08-30. The speed objective assumes constant instruction latencies.
  Hexagon reaches a zero reported gap on 81% of the 100 selected functions.
  Measured hot MediaBench functions are faster in 60.8% of cases and slower in
  17.7%, by as much as 11.1%. In the ideal no-stall experiment, the slowdown
  share falls to 3.8% and Spearman correlation rises from 0.70 to 0.89.
- Architecture optimization manuals can inform named processor models, but
  vendor latency/throughput data and third-party measurements are not
  interchangeable. Date the processor, stepping or family, tool version,
  workload, warm-up, and unit.
- Current compiler implementation examples should come from pinned source
  revisions. A heuristic, fixed-depth search, or first-match rewrite is not a
  lower bound.

## Mathematical and formal foundations

- Finite combinatorics for candidate counts: product rule for independent
  choices, sum rule for disjoint forms, and geometric sums for all lengths up
  to \(k\).
- Finite group actions for symmetry reduction: orbit representatives,
  fixed-point counting, and Burnside's lemma. The chapter derives the
  two-element swap case for the reader before stating the general finite
  formula.
- Elementary probability for candidate filtering: if a wrong function fails
  on \(b\) of \(N\) inputs, \(q\) independent uniform tests miss all failures
  with probability \((1-b/N)^q\). This models a filter, not a correctness
  certificate.
- Order theory for preorders, quotient orders, well-founded descent,
  lexicographic products, partial orders, Pareto fronts, ties, and uniqueness.
- Program synthesis literature for \(\exists P\,\forall s\) and
  counterexample-guided inductive synthesis (CEGIS). Keep candidate generation,
  verification, and finite-cost-stratum exhaustion separate.
- SAT, SMT, pseudo-Boolean, MaxSAT, and constraint-programming proof logging
  differ. Chapter 13 should name what a lower-bound package needs; Chapter 14
  owns detailed certificate formats and checker trust.

## Live Axeyum audit

Inspected 2026-08-30 at commit
'a9991fdad6c1e4b2bda596b46d2c8c715556ceae' on branch
'research/open-problems-2026-08'; the checkout has an unrelated untracked
'docs/open-problems-2026-08/' directory. Findings:

1. Fixed-width bit-vector, SAT, model replay, DRAT production, and DRAT
   checking routes exist.
2. The axeyum-search crate has complete bounded unary and multi-source AVX2
   shuffle synthesis, typed model lifting, and independent replay.
3. Weighted unary AVX2 synthesis supports declared family weights and bounded
   cost formulas.
4. The AVX2 byte-reversal example constructs a two-step witness and checks a
   zero/one-step DRAT lower bound in a selected provenance semantics.
5. The cover machinery checks branch membership, exact Cartesian-product cell
   coverage, uniqueness, and every cell refutation, and can compose a proof.
6. These routes do not supply reusable A0, RV64, or complete x86-64 semantics
   or candidate-language packages; the AVX2 provenance model is not a full
   x86-64 machine semantics.
7. The planned Python teaching API is absent. Rust must own the semantics and
   evidence meaning before such an API is added.

Do not infer a certificate-carrying minimality route from generic SAT/SMT or
optimization support.

## Textbook and course comparison

Completed 2026-08-30:

1. Cooper and Torczon, *Engineering a Compiler*, 3rd edition (publisher
   description and contents read). Its 848-page construction course gives
   separate chapters to optimization, instruction selection, instruction
   scheduling, and register allocation. Chapter 13 imports that practical
   compiler context but concentrates on the neighboring question the contents
   do not make central: what exact language and lower-bound evidence justify
   “minimum.”
2. Nipkow and Klein, *Concrete Semantics with Isabelle/HOL* (2026-01-21 PDF
   read from the official book site). It derives operational semantics,
   compiler semantic preservation, program analysis, Hoare logic, and
   soundness/completeness with executable Isabelle material and extensive
   exercises. Chapter 13 imports its insistence on formal meaning and
   machine-checked reasoning, but works at bounded ISA candidate languages,
   contextual cost, and refutation packages rather than IMP compiler
   correctness.

Derived here: grammar cardinality, quotient proof, cost orders, upper/lower
meeting, typed resource recurrence, orbit counting, test-filter probability,
CEGIS trace, proof-producing CNF obligations, and proof-of-exhaustion shape.
Routed to Chapter 14: certificate formats and trust ladders. Routed to Chapter
15: the sustained three-machine case. Excluded: a general compiler
construction or Isabelle tutorial.
