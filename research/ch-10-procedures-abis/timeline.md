# Chapter 10 historical timeline

| Date | Development | What it contributes | Caution |
|---|---|---|---|
| 1946 | Burks, Goldstine, and von Neumann describe logical organization for an electronic computing instrument | Stored instructions, control, memory, and automatic execution create the setting in which reusable control sequences matter | Not a modern procedure ABI |
| 1949--1951 | EDSAC operates; Wilkes, Wheeler, and Gill document closed subroutines and a library | Working-machine evidence for reusable routines, linkage, parameters, and shared program construction | Link mechanisms differ from modern link-register and stack conventions |
| 1952 | Wheeler publishes on the use of subroutines | Contemporary account of organizing calls and reusable program sections | Verify exact bibliographic metadata |
| 1960s | ALGOL 60 and its implementations make recursive procedure activation central | Each live activation needs its own parameters, locals, links, and return context; a stack is a natural representation | The language semantics do not require every implementation to use one physical hardware stack |
| 1960s--1980s | Linkers, operating systems, compilers, and debuggers standardize object and calling conventions | Separate compilation expands from local practice to a platform-wide binary contract | ISA, object format, ABI, and language runtime remain distinct layers |
| 1980s--1990s | Register-rich RISC conventions and 64-bit platform ABIs mature | Explicit caller/callee register classes, aligned frames, argument classification, and unwind rules | No single “RISC ABI” or “x86-64 ABI” exists |
| 2000s--present | Cross-language runtimes, dynamic linking, JITs, profilers, sanitizers, and hardening depend on stable boundaries | ABI choices affect compatibility, performance, security, tooling, and long-lived industrial ecosystems | Current tool behavior requires pinned primary sources |
| Current | System V AMD64, Microsoft x64, and RISC-V psABI coexist with vector variants and control-flow protection | Concrete comparisons show how one ISA can host different social contracts and one ABI can evolve without changing base arithmetic semantics | State the selected revision and feature profile for every claim |

## Narrative sequence

1. Reuse saves program storage but creates a return and parameter problem.
2. Closed subroutines turn that problem into a documented calling method.
3. Recursion creates many simultaneous activations of one procedure body.
4. Stack discipline represents nested lifetimes and last-created continuations.
5. Separate compilation expands a local convention into an ABI.
6. Modern ABIs trade registers, memory traffic, code size, compatibility, and
   tooling while preserving a stable component boundary.
7. Unwinders, FFIs, dynamic linkers, and return protection reveal that the
   boundary is broader than an argument-register table.
