# Chapter 12 historical timeline

| Period | Development | Contribution | Caution |
|---|---|---|---|
| Early stored-program era | programs are rewritten for machines with different orders and storage conventions | cross-machine use begins as manual redesign and recoding | not yet a reusable translation proof |
| 1950s--1970s | assemblers, compilers, and intermediate languages become retargetable | one source meaning can feed several machine back ends | a common compiler does not itself prove each target correct |
| 1970s--1990s | operational semantics, simulation, refinement, emulation, and binary compatibility mature | relations replace literal equality between unlike states | terminology and proof direction depend on the behavior model |
| 1990s--2000s | verified compiler passes and dynamic binary translation become practical systems | simulations compose transformations; runtime translators reuse guest binaries | compiler proof, binary translation, and full-system emulation remain different tasks |
| 2005 | Bellard documents QEMU's portable dynamic translator | concrete multi-guest, multi-host translation and emulation architecture | implementation evidence is not a universal semantic proof |
| 2000s--present | CompCert supplies machine-checked semantic preservation for realistic compilation | simulation diagrams become an industrial-strength proof method | theorem scope and trusted components remain explicit |
| 2020s | Rosetta 2 supports x86-64 applications on Apple silicon through JIT and AOT routes | translation becomes a platform migration and compatibility mechanism tied to loading and code provenance | current availability, supported extensions, and security rules are dated platform facts |
| Current | formal ISA languages such as Sail connect specification, execution, testing, and theorem provers | one precise ISA source can support several assurance routes | generated artifacts still need version and provenance binding |

## Narrative sequence

1. Porting begins as manual preservation of intent across unlike machines.
2. Retargetable compilers introduce shared intermediate meaning.
3. Operational relations state when different machine states correspond.
4. Simulation diagrams prove that execution preserves the relation.
5. Dynamic translators turn the method into runtime compatibility engineering.
6. Verified compilation and formal ISA descriptions reduce selected semantic
   gaps while keeping their trust boundaries explicit.
7. Modern migration systems expose economic, provenance, support-lifetime, and
   security costs alongside semantic correspondence.
