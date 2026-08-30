# Chapter 12 research contract

**Scope:** Relations and simulations connecting A0, selected RV64I, and
selected x86-64 programs, with compiler-retargeting and binary-translation
consequences
**Target capacity:** breadth governed by the obligations below; word and page
counts are diagnostics, not completion conditions
**Compelling question:** How can machines with different registers, flags,
instruction lengths, and step counts implement one computation?

## Close-up subjects

1. One historical compiler-retargeting or machine-translation problem.
2. One modern dynamic binary translation system and its semantic boundary.
3. One state relation that aligns registers, memory, control, and outcomes.
4. One byte-exact A0/RV64I/x86-64 routine with full decoded traces.
5. One relation table at every synchronization point.
6. One segmented forward simulation with unequal step counts.
7. One stuttering example with a progress rank.
8. One memory injection or address-translation example.
9. One fault mismatch and one continuation/ABI mismatch.
10. One current compatibility case connecting translation to migration cost.

## Three lenses

| Lens | Depth | Required content |
|---|---|---|
| Origins | Medium | retargetable compilers; emulation and compatibility; compiler correctness; static and dynamic binary translation; the growth from handwritten ports to reusable ISA semantics |
| Foundations | Deep | heterogeneous relations; simulation diagrams; traces and labels; stuttering and well-founded progress; memory injections; commuting diagrams; composition; determinism; forward versus backward reasoning |
| Industry and economics | Deep | software migration; installed binaries and plug-ins; JIT versus AOT translation; translation caches; code signatures and provenance; startup and steady-state cost; unsupported instructions; maintenance lifetime; testing and security boundaries |

## Coverage routing

| Neighboring topic | Route |
|---|---|
| General equivalence, observations, and simulations | Import from Chapter 11 |
| ISA decoding and byte provenance | Apply here; Chapter 6 owns the foundation |
| Procedures and ABI preservation | Apply here; Chapter 10 owns the boundary |
| Candidate languages and cost optimality | State translated cost but route proofs to Chapter 13 |
| Certificates and trust | Name the cross-ISA evidence; Chapter 14 owns the ladder |
| Whole three-machine XOR case | Prepare the method; Chapter 15 owns the sustained proof |
| Vector, concurrency, weak memory, timing, and speculation | Exclude or route to Chapter 16 |

## Questions the chapter must answer

1. Which semantic levels are related in compiler retargeting, lifting, binary
   translation, and emulation?
2. What belongs in a cross-machine state relation?
3. Why do corresponding program counters need a relation rather than equality?
4. How are flags related to a flagless machine?
5. How do different memory bases, block layouts, and ownership rules relate?
6. What makes a local simulation diagram sufficient for an endpoint theorem?
7. When may one source step match several target steps or no target step?
8. Which rank prevents infinite stuttering?
9. When does determinism turn a forward result into the needed behavior claim?
10. How do faults, returns, and externally visible traces correspond?
11. What do QEMU and Rosetta demonstrate about practical translation boundaries?
12. What can current Axeyum reuse, and which real-ISA adapters remain missing?

## Feature inventory

- [x] Sourced history of retargeting, emulation, and binary translation.
- [x] Exact separation of compiler correctness, lifting, translation, and emulation.
- [x] State-relation anatomy across registers, control, memory, and outcomes.
- [x] Byte-exact A0, RV64I, and x86-64 worked program.
- [x] Complete synchronization-point and local-segment tables.
- [x] Forward-simulation, stuttering, rank, and composition proofs.
- [x] Determinism and reverse-direction boundaries.
- [x] Memory relation, injection, ownership, and alias cases.
- [x] Fault, trap, continuation, and ABI correspondence.
- [x] Current QEMU and Apple Rosetta case studies with dated limits.
- [x] Compatibility, migration, latency, cache, provenance, and support economics.
- [x] Honest Axeyum substrate audit and staged adapter plan.
- [x] Comparison with at least two substantial textbooks or course texts.
- [x] At least 40 exercises across execution, proof, break, history, translation,
      memory, ABI, industry, Axeyum, and transfer categories.

## Chapter audit

The 2026-08-30 revision contains 9,673 source words and 42 exercises. The print
edition places the chapter on numbered pages 321--347, a 27-page span. Its
absolute-value case now fixes complete A0, RV64I, and x86-64 byte strings,
addresses, decoded instructions, branch displacements, synchronization points,
and both branch traces. LLVM assembly and disassembly independently checked
the two real-ISA byte sequences; the chapter keeps that transcription check
separate from the still-open Axeyum architectural simulation.

The chapter now derives heterogeneous state relations, commuting diagrams,
stuttering and rank, relational composition, memory injection and allocation
extension, fault policies, ABI continuations, and determinism limits. Its
historical and current cases use Bellard's QEMU paper, current QEMU translator
documentation, current Apple developer documentation, Apple platform-security
documentation, CompCert, and the adopted RISC-V Sail model. The textbook
comparison records the distinct systems and verified-compilation baselines.

The live Axeyum audit distinguishes reusable MIR/LLVM scalar translation
validation and replay infrastructure from absent A0/RV64/x86 decoders, states,
relations, memory injections, faults, and ABI adapters. No prose promotes the
worked reader simulation to machine-established evidence.

The full 8-by-10-inch book builds at 467 pages. Chapter 12 has no local
overfull box, undefined citation or reference, or Simplified Book English
warning. A 30-page contact sheet and close readings of the byte and
synchronization tables found no clipping, collision, stranded heading, or
unreadable code. Full PDF preflight passes with embedded fonts, no Type 3
fonts, and acceptable image resolution. Final cross-book continuity and
bibliography review remain part of the whole-manuscript audit.

## Cross-chapter connections

**Back:** Chapters 6, 9, 10, and 11 supply bytes, control, procedures,
observations, refinement, and the general simulation rule.
**Forward:** Chapters 13--15 add cost, evidence, and the complete three-machine
case; Chapter 16 states the larger machine-model boundary.
**Through-lines:** different instruction sets need not resemble one another.
They must preserve a relation at the points where the proof says their
meanings meet.
