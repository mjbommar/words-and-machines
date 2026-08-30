# Chapter 12 sources and claim routes

## Historical and formal foundations

- Primary compiler-correctness and operational-semantics literature for
  simulation diagrams, trace preservation, determinism, and composition.
  CompCert's current top-level theorem uses composed simulations and should be
  described from the live theorem and published papers, not a simplified
  secondary diagram.
- Xavier Leroy, “Formal Verification of a Realistic Compiler” (2009). Use for
  realistic source-to-machine semantic preservation and simulation across
  compiler passes. Keep its language, target, and theorem scope explicit.
- Fabrice Bellard, “QEMU, a Fast and Portable Dynamic Translator” (USENIX ATC
  2005). Use for a documented portable dynamic translator that supported
  several guest and host architectures, full-system emulation, and user-mode
  translation. Source:
  <https://www.usenix.org/conference/2005-usenix-annual-technical-conference/qemu-fast-and-portable-dynamic-translator>.

## Current architecture and translation authorities

- Pinned RISC-V unprivileged specification and current adopted Sail RISC-V
  model for selected decode and execution rules. The Sail repository includes
  assembly formats, encoders/decoders, semantics, executable generation, and
  theorem-prover generation. Source: <https://github.com/riscv/sail-riscv>.
- Intel Software Developer's Manual for selected x86-64 bytes and effects.
- Apple Platform Security, “Rosetta 2 on a Mac with Apple silicon,” for the
  distinction between JIT and AOT translation, code-page hash checks, trust
  caches, and unsigned translated code. Source:
  <https://support.apple.com/guide/security/rosetta-2-on-a-mac-with-apple-silicon-secebb113be1/web>.
- Apple Developer documentation for the current Rosetta compatibility purpose,
  process-wide translation boundary, unsupported executable classes, and
  instruction-extension limits. Treat availability statements as dated and
  recheck before publication. Source:
  <https://developer.apple.com/documentation/Apple-Silicon/about-the-rosetta-translation-environment>.

## Industrial and economic routes

- QEMU and Apple primary documentation for what is translated, when code is
  translated, and where system services participate. Do not infer semantic
  equivalence, performance ratios, or security properties not stated by the
  source. The QEMU master development manual inspected 2026-08-30 describes
  translation blocks, virtual-CPU assumptions, block chaining, translated-code
  invalidation, guest/host program-counter maps for exceptions, and software
  MMU behavior:
  <https://www.qemu.org/docs/master/devel/tcg.html>.
- Compiler and binary-translation measurements only with dated hardware,
  workload, mode, warm/cold cache state, and baseline. Startup cost, cached
  translation cost, and steady-state execution are different units.
- Compatibility claims should identify the actor: application developer,
  platform vendor, plug-in vendor, user, or cloud operator. The value is time
  to migrate and retained software access; the cost includes translator
  engineering, testing, support surface, translation storage, and execution.

## Live Axeyum audit, 2026-08-30

Inspected `../axeyum` at revision
`a9991fdad6c1e4b2bda596b46d2c8c715556ceae` on branch
`research/open-problems-2026-08`.

Axeyum already reflects selected Rust MIR and LLVM IR into one term arena and
proves scalar equality for admitted transformations. Its wrong-transform
corpus requires replayed countermodels for shift, select, mask, and signedness
errors. Generic transition-system, bounded-checking, k-induction, bit-vector,
solver, digest, and replay infrastructure is also reusable.

This is not the Chapter 12 route. It does not decode or execute A0, RV64, or
x86-64 program bytes and does not relate three architectural state spaces. It
has no book-level synchronization-point manifest, flag-to-predicate relation,
memory injection, continuation relation, or cross-ISA fault correspondence.
The chapter should reuse the proven translation-validation patterns without
promoting MIR/LLVM scalar equality to real-ISA simulation.

## Textbook and course comparison

The completed comparison used two different teaching baselines because no
single ordinary architecture text carries the whole Chapter 12 obligation.

1. Bryant and O'Hallaron, *Computer Systems: A Programmer's Perspective*,
   together with the official CMU curriculum pages, establishes the expected
   systems path through data representation, machine-level code, optimizing
   compilers, procedures, linking, exceptional control flow, virtual memory,
   and performance. Its deliberate programmer perspective gives students a
   deep encounter with one platform. Chapter 12 imports those concrete machine
   and operating-boundary expectations, but changes the central question from
   “what does this x86-64 program do?” to “which relation lets two unlike
   machines implement one contract?” Sources:
   <https://csapp.cs.cmu.edu/3e/perspective.html>,
   <https://csapp.cs.cmu.edu/3e/curriculum.html>, and
   <https://csapp.cs.cmu.edu/3e/pieces/preface3e.pdf>.
2. The CompCert manual and live correctness development establish the
   verified-compilation baseline: pass simulations compose; determinacy and
   source receptiveness justify derived backward simulations; the top theorem
   relates whole-program behaviors rather than selected output registers. The
   chapter derives the heterogeneous relation, control-point segments,
   stuttering rank, memory injection, determinism boundary, and composition in
   a smaller three-machine setting. Sources:
   <https://compcert.org/man/> and
   <https://compcert.org/doc/html/compcert.driver.Compiler.html>.

The comparison changed the draft in three ways. It added exact bytes and ABI
and fault boundaries expected by a systems reader; it added memory injection,
rank, and directional-simulation depth expected by verified compilation; and
it made the gap between those traditions explicit rather than treating
translation as register-result testing.

Chapter 15 owns the sustained loop, repeated synchronization points, and
memory-bearing three-machine proof. Chapter 16 owns concurrency, weak memory,
interrupts, vector state, timing, speculation, and architecture-hidden state.
This chapter deliberately excludes detailed dynamic-translator implementation,
operating-system exception delivery, and a general compiler-correctness
development.
