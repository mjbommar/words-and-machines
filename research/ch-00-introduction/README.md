# Introduction research contract

**Scope:** Why instruction-set claims need semantics and checkable evidence
**Target capacity:** 6,000--9,000 words, governed by the obligations below
**Compelling question:** What turns bytes executed by a physical machine into
a claim about every allowed execution, and what should make us believe it?

## Close-up subjects

1. A short replacement claim that passes examples but fails on hidden state.
2. The chain from physical state through bits, instruction semantics, programs,
   quantified claims, evidence, and independent checking.
3. A0, RV64, and x86-64 as a teaching construction and two sustained tests.
4. The asymmetry between finding a better program and ruling out all better
   programs.

## Three lenses

| Lens | Depth | Required content |
|---|---|---|
| Origins | Medium | Leibniz's binary arithmetic; Turing's finite symbolic machine; the EDVAC stored-program report; System/360 compatibility and the naming of computer architecture |
| Foundations | Deep | representation versus denotation; state-transition systems; functions and relations; existential witnesses and universal claims; checking versus trusting |
| Industry and economics | Medium | software compatibility as an asset and constraint; the cost of miscompilation and hardware errata; why validation, proof production, and proof checking have different costs |

## Coverage comparison

The Introduction must orient readers more precisely than a standard survey
chapter while refusing to duplicate later chapters.

| Neighboring topic | Route |
|---|---|
| Information representation | Work here with one small example; derive in Chapter 1 |
| Physical realization of bits | Name the abstraction boundary; derive the needed model in Chapters 1, 2, and 4 |
| Digital logic and datapaths | Route to Chapters 3, 5, and 16 |
| ISA versus microarchitecture | Define the distinction here; work it throughout Chapters 2--10 |
| Operating systems and privilege | Exclude from A0; route to Chapter 16 |
| Equivalence and refinement | Motivate here; derive in Chapters 11 and 12 |
| Solver and certificate mechanics | Motivate here; derive in Chapters 13 and 14 |
| Full RISC-V and x86-64 manuals | Exclude; the book uses pinned teaching slices |

Comparison anchors are the CS2023 Architecture and Organization knowledge
area, the official RISC-V and Intel manuals, the published contents of
*Computer Systems: A Programmer's Perspective*, and substantial Springer
computer-architecture texts. The comparison is for coverage, not imitation.

## Questions the Introduction must answer

1. What is an instruction set, and what is it not?
2. Why do examples establish existence but not a universal claim?
3. Why can two programs agree on outputs and disagree under a larger
   observation?
4. What distinct work belongs to a reader proof, a solver, a certificate, and
   a checker?
5. Why compare a constructed machine with both RV64 and x86-64?
6. What will the reader be able to do by the end of the book?

## Questions deliberately left open here

- How the selected real instructions decode and execute: Chapters 6--10.
- How equivalence, refinement, and minimality are formalized: Chapters 11--13.
- Which current Axeyum routes warrant theorem language: Chapter 14 and the live
  object ledger.
- How concurrency, weak memory, privilege, vectors, floating point, and timing
  change the model: Chapter 16.

## Feature inventory

- [x] One motivating trace in which hidden condition state breaks a replacement.
- [x] An interpretation stack from physical state to computation, with every
      abstraction boundary named. The complete physical realization belongs
      in Chapter 2; the Introduction uses a compact `goingdeeper` panel.
- [x] A witness-versus-lower-bound miniature.
- [x] A compatibility-cost example grounded in System/360 and a current
      architecture, without turning compatibility into a morality tale.
- [x] A trust map distinguishing test, computation, solver verdict,
      certificate, and kernel theorem.
- [x] Exercises that classify claims, repair scopes, and attack a checker.

## Research gaps

- [x] Do not force a modern failure anecdote into the opening. The Introduction
      states the present validation costs it can support. Chapter 16 will use a
      sourced industrial failure case where the mechanism and consequence can
      be treated at full depth.
- [x] Use Amdahl, Blaauw, and Brooks (1964) for the architecture/implementation
      distinction. Avoid claiming that the paper coined the term.
- [x] Keep the compact interpretation stack here. Put the full
      physical-to-semantic figure and derivation in Chapter 2.
- [x] Inspect current Axeyum routes before revising any capability claim. The
      Introduction now states that A0, RV64, x86-64, and cross-ISA packages are
      required work, not current Axeyum capability.

## Chapter audit

- **Draft reviewed:** 2026-08-30
- **Length:** approximately 6,100 source words, within the 6,000--9,000
  capacity band.
- **Rendered review:** pages are balanced; the interpretation stack, claim
  chain, comparison table, route map, proof panels, and exercises are legible
  at the 7-by-10 draft trim.
- **Claim discipline:** historical assertions have primary or authoritative
  citations; current ISA claims point to pinned official manuals; planned
  Axeyum work is labeled as an obligation.
- **Deferred by design:** circuit derivation, complete instruction semantics,
  formal equivalence, proof-certificate mechanics, and a documented industrial
  failure case belong to later named chapters.
- **Status:** breadth-and-depth pass complete for this chapter, subject to the
  final cross-book consistency, bibliography, and production audits.

## Cross-chapter connections

**Back:** The Preface's promise of understanding plus verification.
**Forward:** Chapter 1 constructs the first exact object, a fixed-width word.
**Through-lines:** representation and meaning; compatibility and constraint;
witness versus universal claim; evidence that can fail; exactness as the
source of wonder.
