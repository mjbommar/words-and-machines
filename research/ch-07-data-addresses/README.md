# Chapter 7 research contract

**Scope:** Movement among registers and memory, subregister views, effective
address calculation, access widths, extension, overlap, aliasing, and the
boundary between address formation and memory access
**Target capacity:** 10,000--14,000 words, governed by the obligations below
**Compelling question:** When an instruction says “move,” which value moves,
which location does it name, and what must remain unchanged?

## Close-up subjects

1. One register transfer with exact read, write, and preservation sets.
2. One overlapping x86 subregister example with a full 64-bit before/after word.
3. One A0 load and store with address, range, byte order, and outcome checks.
4. One RV64 signed and unsigned load pair that differs only in extension.
5. One x86 base-plus-index-times-scale-plus-displacement address derivation.
6. One aliasing example where two different address expressions name the same bytes.
7. One commutation proof and one near miss caused by partial overlap.

## Three lenses

| Lens | Depth | Required content |
|---|---|---|
| Origins | Medium | accumulator and memory-address orders; index registers and array traversal; base/index/displacement formats; load/store regularity; x86 subregister inheritance; distinguish machine milestones from later terminology |
| Foundations | Deep | values versus locations; reads, writes, and frames; finite partial maps and byte intervals; address arithmetic modulo a width; effective address versus access; overlap and alias relations; extension and truncation; commuting updates; lenses or projections for register views; fault ordering |
| Industry and economics | Deep | bytes moved versus operations; caches and bandwidth; load/store and address-generation resources; code density; compiler alias analysis; copy avoidance; alignment; vector/DMA boundary; memory safety, bounds, and speculative leakage limits |

## Coverage routing

| Neighboring topic | Route |
|---|---|
| Physical and virtual memory | Work here; Chapter 4 owns the memory model |
| Encoding of operand fields | Work here; Chapter 6 owns decoding |
| Arithmetic flags and overflow | Route to Chapter 8 |
| Branch addressing | Route to Chapter 9 |
| Stack frames, calls, and ABI argument locations | Route to Chapter 10 |
| Memory-aware refinement | Route to Chapters 11--12 |
| Candidate-language and cost models | Route to Chapter 13 |
| Evidence manifests and traces | Route to Chapter 14 |
| Caches, concurrency, speculation, and vectors | Name limits here; route to Chapter 16 |

## Questions the chapter must answer

1. Why are a value and the location holding it different mathematical objects?
2. What does “move” preserve, and why is it often a copy rather than relocation?
3. How do overlapping register names change the write footprint?
4. How is an effective address derived from base, index, scale, and displacement?
5. Why does a valid address calculation not prove a successful memory access?
6. How do width, byte order, alignment, permissions, and range affect a load or store?
7. Why must sign or zero extension specify every destination bit?
8. When do distinct expressions alias, and when do byte ranges partially overlap?
9. Under which disjointness and read-dependence premises do two movements commute?
10. How do A0, RV64I, and x86-64 differ without relying on RISC/CISC slogans?
11. Which compiler transformations depend on may-, must-, partial-, or no-alias facts?
12. Which movement costs and security effects lie outside the scalar ISA model?

## Feature inventory

- [x] Sourced history from early address orders and index registers through
      modern load/store and subregister conventions.
- [x] Exact value, location, view, read-set, write-set, and frame definitions.
- [x] Register overlap model with complete x86-64 subregister cases.
- [x] Effective-address algebra with fixed-width and mathematical-integer views.
- [x] Separation of calculation, translation, permission, alignment, range,
      byte transfer, extension, and architectural result.
- [x] A0 load/store derivations with byte-exact states and negative controls.
- [x] Source-pinned RV64I load/store widths, signedness, alignment scope, and x0 effects.
- [x] Source-pinned x86-64 ModR/M, SIB, displacement, RIP-relative, and partial-register examples.
- [x] Alias, overlap, dependence, and commuting-movement proofs.
- [x] Current bandwidth, energy, cache, compiler, safety, and security stakes.
- [x] Honest Axeyum substrate audit and implementation obligation.
- [x] At least 30 exercises across execution, proof, break, history, design,
      audit, economics, security, and cross-ISA transfer.

## Chapter audit

Depth pass completed 2026-08-30, subject to the final whole-book audit. The
chapter has 10,007 source words and 46 exercises. In the current print build it
runs from printed page 163 through page 189. The PDF build, Simplified Book English check, prose check, and
chapter-local overfull-box inspection pass. A rendered-page review covered the
opening, address algebra, architecture comparisons, industry discussion, and
exercise close.

## Cross-chapter connections

**Back:** Chapters 2--6 supply state, instruction effects, byte-addressed
memory, traces, and decoder results.
**Forward:** Chapters 8--10 use these locations for arithmetic conditions,
control, stacks, and calling conventions; Chapters 11--13 reason about
memory-aware equivalence and cost.
**Through-lines:** a short mnemonic expands into a complete state update;
different names may denote overlapping storage; moving information has a
physical and economic cost hidden by the architectural word “move.”
