# Chapter 4 sources

Research checked on 2026-08-30. Search results are leads only. Manuscript
claims must use opened primary, standards, official architecture, government,
or curriculum sources.

## Origins and physical foundations

- F. C. Williams and Tom Kilburn, "Electronic Digital Computers" (1948), a
  contemporary report of the Manchester experimental stored-program machine
  built to test an electronic storage principle. Avoid later priority slogans.
- Tom Kilburn's 1947 report, "A Storage System for Use with Binary Digital
  Computing Machines," and the related Williams--Kilburn work. It describes
  charge patterns on a cathode-ray tube, short retention, and periodic
  regeneration. This connects remembered bits to sensing and refresh.
- Computer History Museum's core-memory history documents several contributors,
  patent disputes, hand-threaded manufacture, and Forrester's coincident-current
  method. Use it to avoid a sole-inventor account and to connect physical
  geometry with industrial labor.
- Robert Dennard, US Patent 3,387,286, filed 1967 and issued 1968. One disclosed
  cell uses one field-effect transistor and one capacitor; stored charge leaks,
  so information must be regenerated periodically. A patent is evidence for
  this disclosed design, not a universal history of semiconductor memory.
- Tom Kilburn, David Edwards, Michael Lanigan, and Frank Sumner, "One-Level
  Storage System" (1962), for Atlas's automatic combination of fast core and
  drum storage behind one address system. Do not reduce all virtual memory to
  disk overflow; translation also supports placement, sharing, and protection.

## Current authoritative sources

- RISC-V International, *Unprivileged Architecture*, revision 20260120.
  Integer loads and stores use base-plus-signed-offset addresses; the execution
  environment defines accessible regions and behavior of misaligned accesses.
  Naturally aligned accesses do not raise address-misaligned exceptions.
  Misaligned behavior and atomicity require exact scoping.
- RISC-V International, *Privileged Architecture*, current ratified manual,
  for page-based translation, permissions, access and page faults, and the
  documented latitude in exception priority. Use only when the chapter names
  the privileged environment.
- Intel, *Intel 64 and IA-32 Architectures Software Developer's Manual*,
  version 092, Volumes 2 and 3. Volume 2 supplies selected load/store and
  memory-operand behavior; Volume 3 supplies paging, protection, and fault
  rules. Scope every statement to the selected mode and form.
- CISA and partner guidance on memory-safe roadmaps (2023--2025) treats memory
  safety defects as a material product-security and maintenance concern. The
  architectural byte map alone does not supply spatial or temporal object
  safety.

## Coverage comparators

- ACM/IEEE-CS/AAAI CS2023 Architecture and Organization includes memory
  technology, hierarchy, locality, latency, bandwidth, virtual memory,
  protection, faults, performance, energy, and reliability.
- Arvind and Shen, *Computer Architecture: A Constructive Approach*, connects
  memory requests, architectural state, and processor construction.
- Harris and Harris, *Digital Design and Computer Architecture*, connects
  storage circuits, byte-addressed memory, loads/stores, hierarchy, and virtual
  memory.
- Bryant and O'Hallaron, *Computer Systems: A Programmer's Perspective*,
  develops locality, caches, virtual memory, address translation, allocation,
  and memory-related program behavior.
- Hennessy and Patterson, *Computer Architecture: A Quantitative Approach*,
  keeps capacity, latency, bandwidth, miss behavior, and energy as distinct
  quantitative resources.

## Source cautions

- Architectural memory is an abstraction over physical cells and hierarchy;
  it is not the claim that one byte occupies one fixed cell at all times.
- Random access means selection by address without serial traversal as the
  architectural interface requires; it does not mean uniform physical timing.
- Virtual memory is address indirection and policy, not merely an extension of
  DRAM onto a storage device.
- A0's all-or-trap store is single-thread sequential atomicity. It does not
  imply multi-hart atomicity or a memory-ordering guarantee.
- Device mappings may make reads and writes stateful or non-repeatable. Do not
  apply ordinary-memory replay laws without an idempotence premise.
- A source-language object can be invalid even when every addressed byte is
  mapped and architecturally readable or writable.

## Axeyum substrate audit

The 2026-08-30 live checkout contains bit-vector arrays and terms, transition
systems, typed LLVM scalar load/store parsing, and checked-memory tests in the
verification crate. It does not contain the book's A0 finite byte map,
canonical memory serialization, checked split/join operations, atomic trap
frame, or Python replay route. Those generic mechanisms are foundations, not
evidence that `OP.a0.state-memory` is discharged.
