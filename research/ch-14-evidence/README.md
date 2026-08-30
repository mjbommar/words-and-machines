# Chapter 14 research contract

**Scope:** Evidence objects, claim binding, independent checking, negative
controls, reconstruction, and reproducible computational results
**Target capacity:** 12,000--18,000 words, governed by the obligations below
**Compelling question:** What must a successful check be able to reject before
its success supports a theorem?

## Close-up subjects

1. One historical transition from bare SAT verdicts to proof logging.
2. One pencil-checkable resolution refutation from input clauses to the empty
   clause.
3. One comparison of DRAT, LRAT, and an SMT proof format by producer burden,
   checker burden, expressiveness, and reconstruction route.
4. One manifest whose digests bind claim, semantics, formula, artifact,
   checker, and report.
5. One shell-pipeline example in which an exit status is accidentally lost.
6. One vacuous or irrelevant proof artifact and a reader proof of why it
   carries no information.
7. One negative-control matrix that attacks every link in the evidence chain.
8. One reconstruction example that distinguishes a checked theorem from an
   imported assumption.
9. One resource-exhaustion case that remains unknown rather than becoming
   false or proved.
10. One reproducibility case separating repeatability, reproduction with the
    supplied artifact, and independent replication.

## Three lenses

| Lens | Depth | Required content |
|---|---|---|
| Origins | Deep | mathematical proof checking; resolution; SAT competition proof logging; DRUP/DRAT; LRAT and certified checkers; SMT proof interchange; proof assistants and small kernels; research-artifact review without a progress myth |
| Foundations | Deep | propositions and clauses; models and refutations; resolution soundness; proof by contradiction; inductive checker invariants; trust graphs; content-addressed binding; exit-status logic; metamorphic and mutation testing; soundness, completeness, and scope |
| Industry and economics | Deep | solver and proof-file size; checker performance; preprocessing; storage and retention; CI failure modes; supply-chain provenance; reproducible environments; independent implementation cost; maintenance, incident diagnosis, and audit value |

## Coverage routing

| Neighboring topic | Route |
|---|---|
| Candidate languages and lower-bound strata | Import from Chapter 13 |
| Complete three-machine evidence package | Prepare here; Chapter 15 applies it |
| Axeyum solver and kernel routes | Audit concrete capability here; do not infer unsupported reconstruction |
| General proof theory | Teach only the resolution and kernel ideas needed for evidence checking |
| Software supply-chain security | Use provenance concepts that sharpen claim binding; exclude a general security survey |
| Empirical benchmarking | Cover artifact and reproducibility contracts; performance methodology remains distributed across earlier chapters |

## Questions the chapter must answer

1. Why is a satisfying model easier to check than an unsatisfiable verdict?
2. What does one resolution step prove, and why does the empty clause finish a
   refutation?
3. What are the distinct producer/checker tradeoffs of DRAT, LRAT, and Alethe?
4. Which parts of a proof-producing route remain trusted?
5. Why can a valid certificate still support the wrong claim?
6. How do digests bind bytes without establishing semantic correctness?
7. Which outcome states must a command wrapper preserve?
8. How do positive, negative, mutation, and metamorphic controls differ?
9. What makes a checker independent in a technically meaningful sense?
10. What does kernel reconstruction add, and what can an admitted axiom hide?
11. Why must timeout, memory exhaustion, parse failure, and unsupported theory
    remain distinct from a checked negative result?
12. How do repeatability, reproducibility, replication, availability, and
    artifact evaluation differ?
13. What does current Axeyum provide, and which book evidence objects remain
    absent?

## Feature inventory

- [x] Sourced history from resolution and SAT proof logging through certified
      and SMT proof checkers.
- [x] Complete clause, assignment, resolution, and empty-clause miniature.
- [x] DRAT/LRAT/Alethe tradeoff table with exact scope.
- [x] Six trust classes with scope separate from trust class.
- [x] End-to-end claim-binding chain.
- [x] Evidence-manifest fields and raw-byte binding.
- [x] Outcome contract for success, rejection, unknown, and infrastructure
      failure.
- [x] Negative controls and the vacuous-certificate case.
- [x] Mutation and metamorphic testing with an obligation matrix.
- [x] Trust graph and measured trusted-computing-base discussion.
- [x] Reproducibility terminology and artifact-review case.
- [x] Storage, compute, maintenance, and audit economics.
- [x] Honest Axeyum boundary.
- [x] Comparison with at least two substantial textbooks, handbooks, or course
      sources.
- [x] At least 50 exercises across trace, check, prove, break, manifest,
      history, industry, Axeyum, and transfer categories.

## Chapter audit

Breadth-and-depth revision opened 2026-08-30. The inherited draft has 5,526
source words and 18 exercises. It already has a strong conceptual spine:
six trust classes, claim-to-checker binding, manifests, raw bytes, outcome
contracts, negative controls, a hand-auditable checker design, the
vacuous-proof incident, formula-generation risk, independence, reconstruction,
resource outcomes, reproduction, and an honest Axeyum boundary.

The completed depth pass has 12,142 source words and 50 numbered exercises.
The printed chapter runs from page 387 through page 420 in the inspected
509-page PDF. It now includes the resolution miniature and checker invariant;
DRAT, LRAT, and Alethe tradeoffs; canonical-byte and provenance boundaries;
mutation and metamorphic controls; kernel trust graphs and reflection;
evidence economics; reproducibility terminology; an exact live Axeyum audit;
and an end-to-end evidence-package capstone. It is ready for whole-book
consistency review. The book-level PDF build produces a valid artifact but
currently reaches latexmk's pass limit because bibliography back-reference
page records alternate late in the reference list; this is a build-convergence
issue, not a Chapter 14 LaTeX error.

## Cross-chapter connections

**Back:** Chapter 13 supplies exact candidate strata, witnesses, formulas,
refutations, and coverage records.
**Forward:** Chapter 15 assembles the sustained A0/RV64/x86-64 case; Chapter
16 distinguishes evidence about architectural state from claims beyond the
model.
**Through-lines:** a checker establishes only a relation between the exact
bytes it reads; the book's claim needs every preceding semantic and provenance
bridge as well.
