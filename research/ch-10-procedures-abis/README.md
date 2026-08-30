# Chapter 10 research contract

**Scope:** Procedure boundaries, continuation storage, activation records,
stack invariants, calling conventions, argument and result classification,
separate compilation, linkage, unwinding, security, and proof evidence
**Target capacity:** breadth governed by the obligations below; the source
word count is a diagnostic, not a completion condition
**Compelling question:** How can separately written machine-code components
trust one another when the machine itself knows only words, addresses, and
control transfers?

## Close-up subjects

1. One early EDSAC closed-subroutine linkage and its limitations.
2. One recursive activation tree represented by a last-in, first-out stack.
3. One byte-exact RV64 prologue, nested call, epilogue, and return.
4. One byte-exact System V AMD64 call frame and return.
5. One direct contrast with Microsoft x64 argument and shadow-space rules.
6. One worked argument-classification boundary: registers, stack, aggregate,
   and hidden result pointer.
7. One unwind row checked against changing stack and saved-register locations.
8. One tail-call proof that transfers the original continuation safely.
9. One stack-probing or guard-page case that separates arithmetic balance from
   resource safety.
10. One cross-language FFI boundary with ownership, layout, and unwind rules.

## Three lenses

| Lens | Depth | Required content |
|---|---|---|
| Origins | Medium | early subroutine libraries and linkage; closed subroutines; separate assembly and linking; ALGOL recursion and activation storage; the growth from local convention to published platform ABI |
| Foundations | Deep | contracts and assume-guarantee composition; last-in, first-out sequences; activation trees versus linear stack memory; half-open intervals, modular alignment, ownership and separation; liveness; induction over call depth; partial versus total correctness; normal and exceptional continuations |
| Industry and economics | Deep | register allocation and spill cost; leaf and non-leaf transformations; argument classification; System V versus Microsoft x64; tail calls; red zone and shadow space; stack probes and guard pages; unwind metadata; debugging and profiling; FFI and stable binary boundaries; dynamic linking and interposition; return protection |

## Coverage routing

| Neighboring topic | Route |
|---|---|
| Direct and indirect target arithmetic | Import from Chapter 9 |
| General memory validity and aliasing | Apply here; Chapter 4 owns the foundation |
| Full equivalence and refinement theory | Use procedure contracts; Chapter 11 owns the general theory |
| Cross-ISA simulations | Use one shared boundary; Chapter 12 owns the general method |
| Candidate cost and minimality | Name frame/call costs; Chapter 13 owns optimization proofs |
| Evidence formats and certificates | Specify a procedure artifact; Chapter 14 owns the trust ladder |
| Whole multi-machine case study | Prepare components; Chapter 15 composes them |
| Full exceptions, concurrency, privilege, and side channels | Mark exact boundary; Chapter 16 owns extensions |

## Questions the chapter must answer

1. Which facts come from the ISA, object format, ABI, language runtime, or one
   procedure's own contract?
2. Why is a continuation an address with provenance rather than merely a word?
3. How do caller-saved and callee-saved rules compose with liveness?
4. What interval, alignment, ownership, and no-wrap facts make a frame safe?
5. Why can an activation tree be represented by a linear stack, and when can it
   not?
6. How do RV64 and x86-64 store continuations differently while owing the same
   return property?
7. How do System V AMD64 and Microsoft x64 differ on arguments and caller stack
   areas despite sharing the x86-64 ISA?
8. How are scalars, aggregates, variadic arguments, and large return values
   classified in the selected ABI slices?
9. What must hold at every nested call checkpoint?
10. How do tail calls, red zones, stack probes, unwind rows, and return
    protection change the proof?
11. What does an FFI need beyond matching machine register locations?
12. What can Axeyum already reuse, and which procedure/ABI adapters remain
    missing?

## Feature inventory

- [x] Sourced history from early subroutine linkage through recursive language
      implementations and published ABIs.
- [x] Exact ISA/object-format/ABI/language/procedure layer separation.
- [x] Six-part contract plus assume-guarantee composition theorem.
- [x] Stack interval, alignment, ownership, alias, and resource-safety proofs.
- [x] Activation tree, recursion, and induction over call depth.
- [x] Byte-exact RV64 and x86-64 call/prologue/return examples.
- [x] System V AMD64 and Microsoft x64 comparison.
- [x] Worked scalar, stack, aggregate, variadic, and hidden-result cases.
- [x] Nested-call, tail-call, and continuation-provenance proofs.
- [x] Red-zone, shadow-space, stack-probe, guard-page, and return-protection
      boundaries.
- [x] Unwind metadata checked against instruction effects.
- [x] FFI, separate compilation, dynamic linkage, and compatibility economics.
- [x] Honest Axeyum substrate audit and staged implementation obligation.
- [x] At least 40 exercises across execution, proof, break, history, stack,
      ABI comparison, compiler, economics, security, Axeyum, and transfer.

## Chapter audit

Breadth-and-depth revision opened 2026-08-30. The inherited draft has 5,131
source words, 17 exercises, and a 14-page typeset span. It has a strong
six-part procedure contract, stack-interval, A0-boundary, RV64/System V,
nested-call, observation, and evidence spine. It lacks the historical,
recursive, classification, Microsoft x64, unwind, linkage, stack-resource,
security, exercise, and byte-level depth required above. Its Axeyum section
also needs a live substrate audit rather than a generic statement that the
real-ISA adapters are absent.

Revision closed 2026-08-30 at 11,801 source words and 54 exercises. The
typeset chapter spans 32 pages in the 7-by-10 print build (printed pages
259--290). The chapter-level Simplified Book English report has no warnings;
the full book check, PDF build, and publication preflight pass. The final PDF
has no Chapter 10 overfull boxes or undefined citations. A visual check covered
the opener, ABI comparison, return-protection comparison, and exercise opening.
The source comparison with two substantial textbooks and the live Axeyum audit
are recorded in `sources.md`.

## Cross-chapter connections

**Back:** Chapters 4, 7, and 9 supply memory intervals, address formation,
continuations, indirect targets, and CFG reasoning.
**Forward:** Chapters 11--12 turn the boundary into equivalence and cross-ISA
relations; Chapter 15 uses a real multi-machine procedure.
**Through-lines:** the machine does not know what a function is; a durable ABI
turns local instruction effects into a social and technical promise across
people, compilers, languages, libraries, and decades.
