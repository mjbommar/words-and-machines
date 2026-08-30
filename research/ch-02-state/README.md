# Chapter 2 research contract

**Scope:** Machine state as the sufficient architectural memory of execution,
and observations as declared ways of distinguishing states
**Target capacity:** 9,000--12,000 words, governed by the obligations below
**Compelling question:** What must a machine remember now so that its next
step needs no secret history?

## Close-up subjects

1. Two executions with the same destination word but different next steps.
2. A two-state storage element as the physical foothold for remembered state.
3. The A0 state product, its well-formed subset, and complete update rules.
4. Moore's distinguishability question recast as a declared observation.
5. RV64 and x86-64 inventories that do not pretend unlike states are equal.

## Three lenses

| Lens | Depth | Required content |
|---|---|---|
| Origins | Medium | the stored-program need in the EDVAC report; feedback and bistable storage without a single-inventor myth; Moore's experiments on distinguishable sequential-machine states; System/360's architecture/implementation boundary |
| Foundations | Deep | state sufficiency; product types and invariants; finite state-space counting; deterministic and relational transition systems; frame conditions; observations as functions and induced equivalence classes; factorization and information order; state relations versus observations |
| Industry and economics | Medium | compatibility as preservation of architectural state; context save/restore and migration burden; register and extension state as operating-system and hypervisor work; state-space growth in testing and formal verification; hidden implementation state in performance and leakage questions |

## Coverage routing

| Neighboring topic | Route |
|---|---|
| Transistors, latches, flip-flops, clocks, and metastability | Derive the minimum feedback/bistability bridge here; route circuit timing and implementation detail to Chapter 16 |
| Byte-addressed memory contents | Include memory as one state component; derive loads, stores, alignment, and aliasing in Chapter 4 |
| Instruction transition functions | Define their state-domain contract and frame discipline here; work complete instruction rules in Chapter 3 |
| Programs and traces | Use a one-step successor miniature; derive composition, stopping, and traces in Chapter 5 |
| Privileged registers, interrupts, and virtual-machine state | Use save/restore as a present consequence; route full privileged semantics to Chapter 16 |
| Caches, predictors, queues, and speculative state | Distinguish them from architectural state here; route timing and leakage models to Chapter 16 |
| Concurrency and weak memory | Exclude from A0 state and route explicitly to Chapter 16 |
| Cross-ISA simulation relations | Distinguish relations from observations here; derive them in Chapter 12 |

## Questions the chapter must answer

1. Why is a state more than a list of registers?
2. In what exact sense does state summarize the relevant past?
3. How can a physical circuit retain one bit after its input disappears?
4. Why is an architectural state smaller than the physical processor state?
5. How many A0 register-and-condition assignments exist before memory enters?
6. Why must an update say both what changes and what remains fixed?
7. How does an observation group complete states into indistinguishable classes?
8. When does agreement under one observation imply agreement under another?
9. Why do cross-ISA proofs need a relation rather than raw state equality?
10. What costs arise when an architecture exposes more persistent state?

## Feature inventory

- [x] History from stored-program organs through sequential-machine state and
      the architecture/implementation distinction.
- [x] Physical miniature from feedback to two stable regions and a stored bit.
- [x] Formal sufficiency criterion with a hidden-history counterexample.
- [x] Product-state construction, well-formed subset, equality, and update law.
- [x] Quantitative state-space growth example.
- [x] Frame-condition reader proof and an omitted-write attack.
- [x] Observation equivalence, partition, factorization, and ordering proofs.
- [x] Moore-style distinguishing experiment tied to a later branch.
- [x] Source-pinned RV64 and x86-64 architectural-state windows.
- [x] Context-switch, virtualization, and verification-cost consequences.
- [x] Axeyum substrate audit and honest A0 state-package obligation.
- [x] Exercises at execute, explain, break, prove, design, economics, audit,
      and transfer levels.

## Coverage comparison

Substantial architecture texts commonly separate sequential storage, finite
state machines, ISA-visible state, datapath implementation, and operating-
system state management. Harris and Harris connect architectural state to
instruction semantics; Arvind and Shen distinguish architecturally visible
state from implementation state; Parhami and Comer derive circuits that retain
state. Hennessy and Patterson emphasize quantitative architecture and the cost
of design choices. This chapter must join those layers around one semantic
spine without absorbing later chapters on circuits, memory hierarchy, or
privilege.

## Chapter audit

- **Draft reviewed:** 2026-08-30
- **Length:** approximately 9,050 source words, within the 9,000--12,000
  capacity band.
- **Rendered review:** 23 pages at the 7-by-10 draft trim. The state inventory,
  complete-update figure, observation factorization, equations, ISA comparison,
  proof panels, and 27 graded exercises are legible. The chapter produces no
  overfull box in the full-book build.
- **Claim discipline:** the historical chain uses the EDVAC report, Moore's
  primary sequential-machine chapter, and the System/360 paper. Current RV64
  and Intel state claims point to pinned official manuals. The 512-byte Intel
  example is bounded to its documented legacy save area and does not become a
  generic context-switch measurement.
- **Deferred by design:** complete instruction transitions belong to Chapter
  3; byte-memory operations to Chapter 4; programs and traces to Chapter 5;
  cross-ISA simulations to Chapter 12; timing, privilege, concurrency, weak
  memory, and leakage to Chapter 16.
- **Status:** breadth-and-depth pass complete for this chapter, subject to the
  final cross-book consistency, bibliography, evidence, and production audits.

## Cross-chapter connections

**Back:** Chapter 1 supplies the fixed-width values stored in each component.
**Forward:** Chapter 3 defines instructions as complete transformations of
state.
**Through-lines:** relevant history compressed into a sufficient present;
visible versus hidden difference; complete effects and explicit frames;
representation relations between unlike machines.
