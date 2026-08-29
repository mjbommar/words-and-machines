# Introduction and Part I: developmental critique

Date: 2026-08-27

Scope: Introduction and Chapters 1--5, read against SPIRIT.md, VOICE.md,
CRAFT.md, PLAIN-ENGLISH.md, A0-SPEC.md, MASTER.md, and the paragraph plan.

## What the draft now does

- The concept order is cumulative: word, state, instruction, memory, program.
- Each chapter opens on a concrete machine question and closes by creating the
  need for the next concept.
- Width-four examples remain reader miniatures; complete A0 states use widths
  divisible by eight.
- The paired ISA windows compare one named design dimension and avoid treating
  RISC or CISC as semantics.
- Each chapter states the Axeyum implementation boundary and proposes controls
  without claiming that an executable package exists.
- Chapters 2--5 now include execute, break, prove, and transfer exercises.

## Findings and revision decisions

1. **The Introduction carries too many questions in one run.** Six consecutive
   question openings create a questionnaire cadence. Keep the questions, but
   join them into a progression from value to execution.
2. **Several first-use terms are understood by specialists but not taught.**
   Define counterexample, minimality, wraparound, little-endian, and disjoint
   where they first carry an argument.
3. **Chapter 1 has a compressed definition sentence.** Split the conditions on
   byte width from the split formula so the reader meets one rule at a time.
4. **Chapter 2 repeats sentence openings in the state definition.** Vary syntax
   only where it improves the logical grouping; stable technical names remain
   more important than decorative variation.
5. **Chapter 5's first exercise supplies register values that the program
   immediately overwrites.** Turn that fact into the point of the exercise or
   remove the distracting values.
6. **The boundary sections risk sounding like project status reports.** Keep
   them brief and tie every implementation obligation to a semantic rule and a
   concrete control.
7. **No historical aside has yet earned its place.** Do not add unsourced
   chronology merely to satisfy a history quota. The design motives are
   already carried by finite storage, byte addressing, stored code, and
   compatibility. Add history later only from verified primary or
   authoritative sources.
8. **The prose is sometimes metrically even.** Sentence and paragraph metrics
   flag low variation in Chapters 1, 3, and 4. Revise local monotony, but do not
   chase lexical diversity by replacing exact terms with synonyms.

## Evidence-status audit

The draft contains definitions, hand calculations, and reader proofs. It
contains no artifact box and makes no claim that A0, RV64, or x86-64 semantics
have run in Axeyum. Objects OP.a0.word-package, OP.a0.state-memory,
OP.a0.step, and OP.a0.run still name implementation work. The prose must retain
that boundary until the same semantic route supports positive evidence and
failing controls.
