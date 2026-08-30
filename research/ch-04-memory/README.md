# Chapter 4 research contract

**Scope:** Byte-addressed architectural memory, checked loads and stores, and
the abstractions between a program address and physical storage
**Target capacity:** 10,000--14,000 words, governed by the obligations below
**Compelling question:** What must be true between naming an address and
receiving a value?

## Close-up subjects

1. One 32-bit word distributed across four byte addresses.
2. A physical storage cell that leaks and must be refreshed.
3. Complete little-endian load and store functions with failure frames.
4. Overlapping byte ranges that make instruction order observable.
5. One virtual page translation with permissions and a page fault.
6. Exact RV64 and x86-64 accesses whose alignment and exception rules differ
   from A0.

## Three lenses

| Lens | Depth | Required content |
|---|---|---|
| Origins | Medium | early delay, drum, cathode-ray, and core storage without a sole-inventor myth; Williams and Kilburn's regenerative store; Dennard's one-transistor/one-capacitor cell; Atlas one-level storage and automatic address translation |
| Foundations | Deep | finite partial maps; domains and pointwise equality; byte sequences and positional reconstruction; effective-address arithmetic; checked ranges and holes; frame laws; alignment predicates; alias geometry; translation as a partial function with permissions; abstraction from physical state |
| Industry and economics | Medium | capacity, latency, bandwidth, energy, locality, and transfer granularity as separate cost units; virtual-memory isolation and page-fault work; memory-mapped device side effects; compiler alias analysis; memory-safety limits; compatibility and validation surfaces |

## Coverage routing

| Neighboring topic | Route |
|---|---|
| Circuit timing, sense amplifiers, refresh scheduling, ECC, and reliability | Give one physical cell and regeneration foundation here; route implementation detail to Chapter 16 |
| Cache organization and replacement | Explain locality, lines, and why architectural equality omits cache contents; route detailed hierarchy and leakage to Chapter 16 |
| Page replacement and operating-system allocation policy | Explain translation, pages, permissions, faults, and sharing here; route policy algorithms to operating-systems sources and Chapter 16 |
| Concurrent memory ordering and cache coherence | Distinguish sequential A0 atomic failure from inter-thread atomicity here; route full models to Chapter 16 |
| Addressing-mode encodings | Use effective-address semantics here; derive instruction bits in Chapter 6 and paired forms in Chapter 7 |
| Language objects, allocation, and undefined behavior | Explain why byte-address validity is weaker than language memory safety; route language semantics to Chapters 10--12 and specialist sources |
| Procedures, stacks, and heaps | Use regions as examples of policy and convention; develop stacks and ABIs in Chapter 10 |

## Questions the chapter must answer

1. How can changing physical storage technologies preserve one memory
   abstraction?
2. Why is an architectural byte neither a type nor a physical cell?
3. Why must memory be modeled as a partial map rather than an unchecked array?
4. Which premises make store followed by load return the original word?
5. Why are address formation, alignment, presence, permission, and device
   behavior separate checks?
6. How do overlapping ranges create dependencies even when starting addresses
   differ?
7. What relation connects virtual addresses, physical frames, and permissions?
8. Why can two virtual addresses share physical storage?
9. Which costs are measured by capacity, latency, bandwidth, transfer size,
   page faults, and energy rather than by one vague claim that memory is slow?
10. Why does a valid architectural address fail to prove source-language
    memory safety?

## Feature inventory

- [x] Sourced storage history from regenerative electronic memory through
      semiconductor cells and one-level storage.
- [x] Physical derivation from charge, leakage, sensing, and refresh to a
      stable architectural byte abstraction.
- [x] Finite partial-map model with domain, equality, update, and frame laws.
- [x] Formal split/join load and store functions and two round-trip directions.
- [x] Complete range, wrap, hole, alignment, permission, and trap distinctions.
- [x] Alias geometry for load/store and store/store interactions.
- [x] Virtual-to-physical translation, permissions, sharing, and page-fault
      miniature with an explicit boundary.
- [x] Memory-mapped device warning and idempotence boundary.
- [x] Source-pinned RV64 and x86-64 access comparisons.
- [x] Current performance, economic, and security consequences with named
      resources and measurement units.
- [x] Honest Axeyum substrate audit and byte-memory implementation obligation.
- [x] At least 25 exercises across execute, explain, break, prove, design,
      audit, economics, security, and transfer levels.

## Coverage comparison

Current architecture curricula expect memory technology, hierarchy, locality,
latency, bandwidth, virtual memory, translation, faults, protection, and
reliability. Constructive architecture texts connect byte storage to load and
store semantics. Systems texts connect addresses to caches, page tables,
allocation, and protection. Quantitative architecture texts require distinct
cost metrics. This chapter must establish one semantic path through those
layers while routing cache algorithms, operating-system policy, concurrency,
and circuit detail rather than pretending to complete those fields.

## Chapter audit

The revised chapter contains 10,126 source words and 37 exercises. The print
edition renders the chapter on numbered pages 79--105, a 27-page span. The
complete feature inventory above was checked against the manuscript on
2026-08-30. The source ledger covers every historical and current factual
claim that carries the chapter's argument, including the labor and disputed
invention history of magnetic-core memory.

The full book builds successfully at the configured 8-by-10-inch trim. The
chapter has no local overfull boxes and no Simplified Book English warnings.
A 27-page contact sheet plus close readings of the opening, quantitative-cost,
and final-exercise pages found no clipping, collision, stranded heading, or
unreadable figure. Final cross-book continuity and bibliography review remain
part of the whole-manuscript audit; they are not Chapter 4 blockers.

## Cross-chapter connections

**Back:** Chapters 1--3 supply byte/word interpretation, complete state, and
operand evaluation.
**Forward:** Chapter 5 composes memory effects in traces; Chapters 6--7 encode
and compare real addressing forms.
**Through-lines:** physical difference hidden behind an architectural
relation; partial functions made explicit as traps; local changes with global
frames; costs named by resource and unit.
