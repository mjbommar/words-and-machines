# Chapter 10 sources and claim routes

## Historical foundations

- Arthur W. Burks, Herman H. Goldstine, and John von Neumann, *Preliminary
  Discussion of the Logical Design of an Electronic Computing Instrument*
  (1946). University of Michigan archival copy. Use for the stored-program
  control and machine-organ setting; do not project a modern ABI into it.
- Maurice V. Wilkes, David J. Wheeler, and Stanley Gill, *The Preparation of
  Programs for an Electronic Digital Computer* (1951). Use for working EDSAC
  closed subroutines, link orders, a subroutine library, and programming
  practice on an operational stored-program machine.
- David J. Wheeler, “The Use of Sub-routines in Programmes” (1952),
  *Proceedings of the 1952 ACM National Meeting (Pittsburgh)*, pp. 235--236,
  DOI `10.1145/609784.609816`. Use for contemporary subroutine organization
  and linkage. Bibliographic metadata verified 2026-08-30.
- Revised Report on the Algorithmic Language ALGOL 60 and early implementation
  reports. Use for recursive procedures, block activation, parameter modes,
  and the need for per-activation storage. Keep language definition separate
  from one implementation's stack design.

## Architecture and ABI authorities

- RISC-V Unprivileged ISA specification, pinned 2026-01-20 snapshot. Use only
  for `JAL`, `JALR`, loads, stores, integer arithmetic, and architectural state.
- RISC-V ELF psABI repository and current calling-convention source
  (`riscv-cc.adoc`). Use for register roles, 16-byte standard stack alignment,
  scalar/aggregate/variadic classification, frame-pointer convention, return
  values, and vector variants. Record the exact commit used in the chapter.
- Intel 64 and IA-32 Software Developer's Manual, Volume 2, pinned edition.
  Use for selected `CALL`, `RET`, push/pop, load/store, and fault semantics.
- System V AMD64 ABI, x86-64 psABI project, pinned revision. Use for register
  classes, argument classification, stack alignment, red zone, return values,
  variadic register-save area, ELF linkage, and unwind conventions.
- Microsoft Learn, “x64 Calling Convention,” pinned retrieval and toolset view.
  Use for four register parameters, caller-reserved parameter area, alignment,
  volatile/nonvolatile registers, leaf/non-leaf constraints, and unwindability.
  Treat it as Microsoft x64, not as a fact about all x86-64 code.
- DWARF Version 5, especially call frame information. Use for the canonical
  frame address, register recovery rules, and row changes across instruction
  ranges. Do not treat plausible debugger output as validation of metadata.

## Compiler, runtime, and security routes

- LLVM and GCC official documentation/source for tail-call eligibility, frame
  lowering, stack probes, and unwind table generation. Use current behavior as
  one implementation, not as the definition of an ABI.
- Platform object-format and dynamic-linker specifications for procedure
  linkage tables, lazy binding, symbol interposition, and compatibility. Keep
  linkage semantics separate from the procedure's body theorem.
- Intel CET and RISC-V CFI specifications for shadow stacks and landing rules.
  Import the target-policy distinctions from Chapter 9; focus here on matching
  call/return history and saved continuation integrity.
- Language FFI specifications only for the selected worked boundary. Name
  representation, ownership, lifetime, panic/exception, and calling-convention
  assumptions; matching integer registers alone is insufficient.

## Live source notes, 2026-08-30

- The current RISC-V psABI source states that `a0`--`a7` are argument
  registers; `s0`--`s11` are preserved; `ra` is not preserved; standard RV32I
  and RV64I stack alignment is 16 bytes; the stack grows down; and values below
  `sp` do not persist under the standard convention.
- Its integer convention passes values up to XLEN in one argument register,
  uses two registers for selected values up to 2*XLEN, passes larger aggregates
  by reference, and gives variadic aligned-pair and stack-continuation rules.
- The same source distinguishes the standard vector convention from a vector
  calling-convention variant. Saving every vector register in a dynamic
  resolver has material stack and performance cost.
- Microsoft x64 uses four register parameter positions and requires caller
  stack space that the callee may use for those register parameters. Its unwind
  rules constrain prologues and epilogues. These facts must not be blended with
  the System V six-integer-register and red-zone rules.
- DWARF call frame information is a program-point-indexed recovery description,
  not a claim that the physical frame has one fixed layout throughout a body.

## Axeyum substrate audit

Inspected sibling repository `../axeyum` at revision
`a9991fdad6c1e4b2bda596b46d2c8c715556ceae` on branch
`research/open-problems-2026-08`. It provides generic transition systems,
array-free and memory-aware bounded model checking, k-induction, certified
array-free QF_BV safety paths, symbolic execution, and replay-checked models.

More specifically, `axeyum-verify` already has an opt-in checked scalar LLVM
direct-call route. `ScalarCallContract`, `ScalarContractExpr`,
`DirectCallResolver`, and `VerifiedContractResolver` can verify a selected leaf
body, replace it with a modular contract, compare modular and inlined transition
systems, carry requirements and definedness, attribute a failing call site, and
feed bounded checking or k-induction. The acceptance tests pin source/body
digests, use large differential enumerations, mutation controls, source replay,
and fail-closed declaration/signature/resource checks.

That capability is not a platform ABI verifier. The admitted profile rejects
callee memory, nested calls, indirect calls, non-scalar signatures, and broader
control flow. It works at checked LLVM scalar semantics rather than A0, RV64I,
or x86-64 instruction bytes. It has no architectural stack pointer or frame,
saved continuation, System V or Microsoft register classes, argument
classification, unwind rows, red zone, shadow space, stack probes, or
cross-language FFI contract. The word `tail` can be parsed on a direct LLVM
call, but the current scalar route does not establish the machine-level tail
call obligations required by this chapter.

The staged book route should therefore reuse the verified modular-call and
transition-system patterns, then add a memory-owning procedure adapter rather
than beginning with an endpoint-only checker. A first A0 slice still needs A0
bytes and step semantics, an explicit continuation convention, owned frame
intervals, and replay. Real-ISA layers then need source-pinned decoders and
selected ABI packages. No Axeyum files were changed during this audit.

## Textbook coverage comparison

Checked 2026-08-30 against publisher descriptions and tables of contents:

- Bryant and O'Hallaron, *Computer Systems: A Programmer's Perspective*, 3rd
  ed. Pearson describes Chapter 3 as an x86-64 machine-code treatment that
  includes procedures and code vulnerabilities, with linking and exceptional
  control flow developed in Chapters 7 and 8. This is the strongest comparison
  for the programmer-visible x86-64 frame, control, linkage, and security
  material. Chapter 10 retains those subjects but makes its proof obligations
  explicit and adds sustained RV64, System V/Microsoft comparison, unwind-row
  validation, and an Axeyum implementation boundary.
  Source: <https://www.pearson.com/en-us/subject-catalog/p/computer-systems-a-programmer-s-perspective/P200000003479/9780134071930>.
- Patterson and Hennessy, *Computer Organization and Design: The
  Hardware/Software Interface, RISC-V Edition*, 2nd ed. Elsevier routes the
  ISA-facing procedure material through Chapter 2, “Instructions: Language of
  the Computer,” within a broader hardware/software-interface course. This is
  the strongest comparison for RISC-V procedure instructions, register use,
  and course-level exercises. Chapter 10 retains that executable ISA footing
  but derives activation-stack invariants and crosses into platform ABIs, FFI,
  unwind metadata, compatibility economics, and return protection.
  Source: <https://shop.elsevier.com/books/computer-organization-and-design-risc-v-edition/patterson/978-0-12-820331-6>.

The comparison supports the chapter's routing decisions. Processor datapaths,
cache hierarchy, general linking, and full exceptional-control semantics belong
to neighboring chapters or lie outside the scalar core. Procedure state,
activation storage, selected calling conventions, nested-call preservation,
argument classification, unwind recovery, binary boundaries, and their proof
obligations are derived here. The combined scope is intentionally not a copy of
either textbook's organization.
