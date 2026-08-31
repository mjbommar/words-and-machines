# Structure and artifact-redesign completion audit

Date: 2026-08-27

This audit covers the requested book-wide outline and structure revision and
the clean-sheet Axeyum artifact redesign. It does not claim that the planned
semantic packages or machine proofs have been implemented.

## Requirements and evidence

### Abstract ISA foundation

Evidence:

- MASTER.md defines A0 before either real architecture.
- A0-SPEC.md fixes state, code separation, encoding, operands, opcodes,
  condition rules, branches, memory, traps, exclusions, and controls.
- Chapters 1 through 5 follow words, state, instructions and operands, memory,
  then programs and control.
- Active A0 object records form the same dependency chain.

Assessment: satisfied for outline and structure.

### x86-64 and RISC-V throughout

Evidence:

- MASTER.md defines source-pinned RV64 and x86-64 teaching slices.
- Chapters 2 through 5 contain paired windows.
- Chapters 6 through 10 hold one semantic question fixed and develop both
  architectures beside A0.
- Chapters 11 through 15 use observations, state relations, refinement, and a
  scalar three-machine synthesis.
- Active RV64, X64, and REL objects name the required source, decoder, step,
  and relation layers.

Assessment: satisfied for outline and structure. Source revisions and semantic
implementations remain explicit obligations.

### Complete table of contents

Evidence:

- The full edition lists Chapters 1 through 16.
- The Introduction previews the same four-part route.
- All configured chapter IDs resolve to one canonical chapter file.
- The quick PDF build succeeds with 17 content entries including the
  Introduction.

Assessment: satisfied.

### Removal of legacy vector-led structure

Evidence:

- The canonical chapter directory contains no legacy permutation or
  vector-minimality chapter.
- The Introduction and Preface no longer use the former extension example as
  the book's premise.
- The active README, guides, object ledger, artifact tree, and Axeyum guide do
  not advertise the former result.
- A repository scan excluding the research archive returns no matching legacy
  extension names or instruction mnemonics.
- Superseded material is recoverably retained under research/archive and has no
  active build or ledger binding.

Assessment: satisfied.

### Clean-sheet object ledger

Evidence:

- The schema accepts only A0, RV64, X64, REL, EVID, and OP domains.
- Forty-one active records replace the forty-seven archived legacy records.
- The generator groups objects by the new four-part curriculum.
- The checker rejects missing dependencies, mismatched filenames, nonexistent
  chapter bindings, checked evidence without semantic inputs, and checked
  evidence without a negative control.
- The structural and runtime object gates report zero problems.

Assessment: satisfied.

### Clean-sheet Axeyum artifact design

Evidence:

- The active artifact tree contains a new manifest schema and design README,
  not renamed legacy evidence.
- The schema requires semantic package digests, scope, exclusions, trust
  class, artifacts, producer, checker, negative control, environment, and
  limitations.
- The artifact checker validates local paths and raw digests.
- The new Axeyum guide follows A0, real-ISA adapters, program relations,
  manifests, and reproduction.
- AXEYUM-EVIDENCE.md defines the dependency graph, flagship sequence,
  controls, migration rule, and implementation completion conditions.
- Legacy artifacts and producers are archived outside the active gate.

Assessment: the redesign now has its first active route. One A0 semantic
package and one width-8/16 finite-computation manifest are checked, including
a firing reversed-byte-order control. All later flagship routes remain open.

### Guidance and front matter consistency

Evidence:

- Root and book AI instructions require the abstract machine and sustained
  paired comparison.
- SPIRIT, VOICE, CRAFT, and PLAIN-ENGLISH use scalar semantic examples.
- Preface, Introduction, metadata, README, and master outline describe the
  same book.

Assessment: satisfied.

## Gates

The completion run requires:

    make check-run
    make -C book check
    make -C book quick
    git diff --check

It also requires an active-tree scan excluding research/archive for the former
extension name, instruction mnemonics, old object prefixes, the former
abstract-machine name, and the six-chapter structure. The expected result is
no matches.

## Remaining work after this redesign

This redesign record predates the executable-artifact pass. The active ledger
now contains checked A0 routes and two checked RV64 routes. The x86-64,
cross-machine relation, and remaining evidence interfaces are still the next
Axeyum-engineering phases. Only checked active objects, not this historical
audit paragraph, determine current status.
