# Chapter 14 sources and claim routes

## Proof logging and certified checking

- Wetzler, Heule, and Hunt, “DRAT-trim: Efficient Checking and Trimming Using
  Expressive Clausal Proofs” (SAT 2014). The authors' DRAT-trim page and
  original paper were located 2026-08-30. Use for DRAT expressiveness,
  additions and deletions, backward checking, trimming, and the practical
  checker resource tradeoff.
- Cruz-Filipe, Heule, Hunt, Kaufmann, and Schneider-Kamp, “Efficient Certified
  RAT Verification” (CADE 2017). Original paper located 2026-08-30. Use for
  LRAT hints and the demonstrated Coq and ACL2 certified checker routes.
- Schurr et al., “Alethe: Towards a Generic SMT Proof Format” (PxTP 2021).
  Original paper located 2026-08-30. Use for the history from veriT proofs
  toward an SMT interchange format and for the format-development caveats.
- Carcara (TACAS 2023) is a relevant independent Rust checker and elaborator
  for Alethe. Read the primary paper before adding quantitative claims.

Do not say that a proof format removes all trust. Separate formula generation,
parser, checker rules, arithmetic implementation, proof-assistant kernel, and
the prose-to-formula bridge.

## Reproducibility and artifacts

- ACM Artifact Review and Badging, version 1.1 (2020), current policy page
  checked 2026-08-30. Use its distinct definitions of repeatability,
  reproducibility, and replicability, and its independent badges for Artifacts
  Evaluated, Artifacts Available, and Results Validated.
- The ACM policy explicitly distinguishes functional and reusable evaluation,
  archival availability, reproduction using author artifacts, and replication
  without them. Do not collapse these into one “reproducible” label.
- Research artifact badges are review outcomes under venue-specific processes,
  not proof certificates for every claim in a paper.
- in-toto's current specification and reference documentation were checked
  2026-08-30. Its signed layouts declare steps and authorized functionaries;
  signed link metadata records materials, products, commands, and byproducts.
  Use it as an industrial comparison for a chained evidence manifest. Its
  integrity and process-attestation goals do not establish the semantic truth
  of an arbitrary theorem carried through the chain.

## Mathematical foundations

- Propositional clauses, assignments, unit propagation, resolution, and proof
  by contradiction.
- Checker invariant: every accepted derived clause is entailed by the original
  formula and previously accepted clauses; acceptance of the empty clause
  implies unsatisfiability.
- Hashes and content addressing establish byte identity under a named digest
  algorithm. They do not establish meaning, correctness, authorship, or
  availability.
- Mutation testing changes an artifact or checker input and requires rejection.
  Metamorphic testing applies a transformation with a predicted relation
  between outcomes. Use both as controls, not as substitutes for a checker
  soundness proof.

## Textbook and handbook comparison

Located for primary reading:

1. *Handbook of Satisfiability*, second edition: inspect its proof-complexity
   and proof-logging coverage relevant to a worked certificate checker.
2. *Software Foundations: Logical Foundations*: its official text is itself a
   Coq proof script, including exercises. Compare proof-as-program pedagogy
   with Chapter 14's external artifact, parser, and checker boundaries.
3. *Concrete Semantics*: the official book combines detailed informal
   explanation with Isabelle formalizations and 115 exercises. Compare its
   small formal examples and executable theories with the chapter's
   certificate route.
4. ACM Artifact Review and Badging supplies the reproducible-research
   comparison. Keep artifact evaluation and result validation distinct from
   logical certificate checking.

## Live Axeyum audit

This is the 2026-08-30 pre-implementation snapshot. The implementation
follow-up below supersedes its capability conclusions while preserving the
research trail.

Refreshed 2026-08-30 against sibling checkout `../axeyum`, branch
`research/open-problems-2026-08`, commit
`a9991fdad6c1e4b2bda596b46d2c8c715556ceae`. The checkout contained unrelated
untracked research documentation; it was not modified.

- `axeyum-cnf` contains forward DRAT checking plus streaming, backward,
  file-backed, and budgeted routes. These capabilities must not be shortened to
  one undifferentiated “verified SAT” claim.
- `crates/axeyum-cnf/src/lrat.rs` implements an independent clausal,
  hint-following LRAT checker and DRAT-to-LRAT elaboration. The inspected route
  is RUP-only: positive hints are supported and RAT additions are explicitly
  rejected as unsupported.
- `crates/axeyum-solver/src/evidence.rs` defines `EvidenceReport` as evidence,
  versioned provenance, and a per-result trust-step ledger. `EvidenceCheck` is
  intentionally three-way: `Verified`, `NothingToCheck(reason)`, and `Failed`.
  An absent certificate therefore cannot become a successful check.
- The evidence enum contains route-specific DRAT, Alethe bit-vector,
  arithmetic-aware Alethe, guarded finite-instantiation, model, and other
  variants. Comments and checking paths distinguish certified reductions from
  trusted steps. State claims by exact variant and checker.
- The propositional solver's `SatUnsatEvidence` distinguishes unchecked proof
  availability from a DRAT proof produced and independently accepted by the
  checker.
- The repository has extensive Lean reconstruction and dependency reporting,
  but the footprint is route-specific. Inspect imported assumptions for the
  exact result before using “kernel checked.”
- No unified A0/RV64/x86 book-manifest API was found. The chapter's Python
  listing remains explicitly illustrative. Rust should own canonical bytes and
  evidence semantics; Python may expose them without collapsing outcome types.

## Implementation follow-up

Refreshed 2026-08-31 against the integrated Axeyum checkout at commit
`a257d7cd639caf101c03e9bba21864267b97b66e` and the book repository's active
manifest layer.

- Axeyum now owns the concrete A0, RV64I, x86-64, and finite cross-machine
  semantics used by the active evidence routes.
- `scripts.evidence_manifest.EvidenceManifest` is a real typed reader-facing
  orchestration interface. Its exact printed listing is imported and executed
  by the code-listing gate.
- The interface preserves the manifest's trust class, scope, exclusions,
  limitations, checker version, and Axeyum revision. Producer, positive
  checker, and negative control execution remain explicit.
- This interface does not claim a general kernel-reconstruction API. Rust
  remains authoritative for machine semantics and certificate checking.
