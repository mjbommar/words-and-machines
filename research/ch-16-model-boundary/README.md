# Chapter 16 research contract

**Scope:** the semantic boundary of the scalar machine and the disciplined
extension of state, transitions, observations, proofs, and evidence
**Target capacity:** 10,000--15,000 words, governed by the obligations below
**Compelling question:** When a machine theorem stops applying, what exactly
must be added before a stronger claim becomes meaningful?

## Three lenses

| Lens | Depth | Required content |
|---|---|---|
| Origins | Deep | scientific abstraction; IEEE floating-point standardization; vector and multiprocessor models; virtual-memory locality; self-modifying code; verified compilation; speculative leakage |
| Foundations | Deep | abstraction functions and relations; simulation; conservative extension; floating-point representation and error; event graphs and strict-order cycles; partial translation; noninterference; behavior refinement |
| Industry and economics | Deep | vector implementation freedom; reproducibility cost; weak-ordering engineering; translation and working-set costs; JIT publication; side-channel validation; compiler trust and maintenance |

## Required close-ups

1. One commuting-square account of abstraction.
2. One proved conservative-extension result.
3. One exact floating-point reassociation counterexample.
4. One vector element-class inventory with mask and tail policies.
5. One weak-memory litmus test and sequential-consistency cycle proof.
6. One stateful address-translation contract.
7. One explicit instruction-publication protocol.
8. One two-execution noninterference statement.
9. One compiler behavior-preservation route with its real endpoints.
10. One ledger and control plan for accepting a new semantic component.

## Feature inventory

- [x] Model purpose, abstraction function, relation, and observation.
- [x] Conservative embedding theorem and reader proof.
- [x] Floating-point representation, rounding, flags, error, and reproducibility.
- [x] Vector length, masks, restart, inactive and tail policies, and economics.
- [x] Event-graph concurrency, litmus test, SC cycle, and language/compiler/hardware stack.
- [x] Translation, permissions, TLB agreement, virtualization, locality, and resource economics.
- [x] Mutable-code versioning, RISC-V instruction synchronization, and publication costs.
- [x] Relational leakage, constant-time scope, speculation, and mitigation layers.
- [x] Compiler behavior refinement, undefined behavior, trust, and maintenance.
- [x] Extension gates, dependency ledger, refusal, and negative controls.
- [x] At least 50 exercises spanning execution, proof, break, design, cost, and transfer.

## Chapter audit

Opened 2026-08-30 at 4,565 source words and 22 exercises. The inherited chapter
had a sound omitted-state map but treated each boundary mainly as a feature
survey. It needed derivations, concrete counterexamples, historical lineage,
industrial tradeoffs, and proof obligations that a reader could execute.

The depth pass reached 10,450 source words and 54 exercises. It preserves the
scalar book's boundary: no section claims that the absent vector, concurrency,
virtual-memory, speculative, or verified-compiler packages already exist in
Axeyum. Each topic instead states the smallest meaningful semantic extension,
the claim it could support, and the controls needed before evidence.

## Cross-chapter connections

**Back:** Chapters 1--10 define scalar words, states, memory, control, encoding,
and ABIs. Chapters 11--12 define observation and simulation. Chapters 13--15
bind cost, evidence, and the complete three-machine scalar case.
**Forward:** the chapter is the book's research map. Each boundary can become a
later volume or Axeyum package without changing the meaning of the scalar core.
**Through-line:** a finite model gains reach by forgetting distinctions, and
honesty requires naming every distinction that a stronger claim needs back.
