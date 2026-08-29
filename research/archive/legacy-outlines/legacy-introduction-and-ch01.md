# Superseded Introduction and Chapter 1 notes

This file is migration history. See `MASTER.md`.

This plan governs the opening of *Instruction Sets, Programs, and Proofs*. It records what the
reader must learn, in what order, and why each paragraph hands the reader to
the next one. The final prose may combine short beats, but it must preserve the
dependency order.

## Reader promise

By the end of Chapter 1, the reader should be able to distinguish a program
from a claim about that program; an example from a universal statement; a
witness from a lower bound; a solver verdict from an exported certificate; and
a checked fixed-width result from an all-width kernel theorem. The reader
should also have completed one small proof by cases and understood how the
same claim becomes a solver query with a negative control.

The opening must also establish the order of abstraction. Words, state, and
instruction functions come before named architectures. RISC-V and x86-64 are
later case studies in explicit semantic dimensions; AVX2 is a restricted
x86-64 vector extension, not a proxy for CISC.

## Concept and motivation DAG

```text
machine register + instruction
          |
          v
concrete byte-reversal problem ---- superoptimization history
          |                              |
          v                              v
candidate sequence (upper bound)   shortest-program claim
          |                              |
          +------------+-----------------+
                       v
          function computed by a program
                       |
          +------------+-------------+
          v                          v
   equivalence on all inputs    program language + cost model
          |                          |
          +------------+-------------+
                       v
              lower-bound question
                       |
          +------------+-------------+
          v                          v
       searcher                    checker
          |                          |
          v                          v
       witness       artifact + failure condition + scope
                                      |
                                      v
                       object + ledger + negative control
                                      |
                                      v
                      What do instructions act on?
                                      |
                                      v
natural numbers -> width n -> residues modulo 2^n -> bits -> word operations
                                      |
                                      v
                         instruction as total function
                                      |
                                      v
                    division-by-zero design convention
                                      |
                  +-------------------+------------------+
                  v                                      v
          human proof by cases                negated solver formula
                                                         |
                                           +-------------+-------------+
                                           v                           v
                                     UNSAT verdict              false-claim control
                                           |                           |
                                           +-------------+-------------+
                                                         v
                                         exact evidence boundary
                                                         |
                                                         v
                                  equivalence and minimality in Chapter 2
```

The history joins the technical argument at one point only: programmers have
searched for short programs for decades, so “shortest” is not a new desire.
The book's question is what a reader receives with a particular claim. The
design history joins at division by zero: a mathematical partial operation has
to become a specified machine result before tools and implementations can
agree.

## Introduction: paragraph-level flow

### 1. A small program and a large word

1. Put thirty-two bytes in one register and ask for their order to be
   reversed. Keep the opening physical: first byte, last byte, two machine
   moves.
2. Give a two-instruction candidate in words. This settles existence, not
   minimality. **Hook:** “Two instructions are enough. Why are they necessary?”
3. Try the reader's natural answers—inspection, compiler output, many tests—and
   show why each supplies examples rather than a lower bound. **Transition:** a
   shortest-program claim ranges over programs we did not run.

### 2. What “shortest” contains

4. Explain a program as a composition of functions, using a tiny lane example
   rather than notation first.
5. State why this definition precedes the RISC/CISC distinction. Name the
   semantic features that later comparisons must make explicit: operands,
   memory, flags, results, and encodings.
6. Name equivalence: same output for every allowed input. Contrast one passing
   test with the quantified claim.
7. Name the program language and cost model. One instruction is meaningful
   only after we say which instructions, operand forms, constants, and costs
   count. **Hook:** the scope is not fine print; it is part of the proposition.
8. Separate upper and lower bounds. A witness gives the upper bound; refuting
   every cheaper candidate gives the lower bound. Together they give the
   optimum. **Transition:** finding and checking now become different jobs.

### 3. A short history of the missing receipt

9. Place Massalin's superoptimizer, later automatically generated peephole
   superoptimizers, and current complete search in one compact line of descent.
   Say what each contributes to the live question, not the history of the
   whole field.
10. State the recurring gap with care: a search result may be right without
   leaving a small, independent object that establishes its lower bound.
   Avoid priority claims. **Hook:** a searcher may work for hours; a checker
   should not have to trust its judgment.

### 4. The book's unit of belief

11. Introduce an artifact as the bytes that carry evidence: a witness,
    formula, refutation, or transcript. Then introduce a checker as a program
    whose exit result changes when those bytes are wrong.
12. Introduce a negative control through a concrete mutation: give the checker
    a false claim or damaged proof. Explain that this tests the checker, not
    the theorem.
13. Introduce the object and ledger only after the artifact is understood. An
    object binds claim, scope, status, evidence, and control; the ledger lets
    the book avoid silently strengthening a result.
14. Explain the two-proof rule: a human-scale argument makes the reason
    visible; a machine route checks the full scoped instance. State that
    computations and open problems use different evidence language.
15. Give the trust boundary: verdicts, certificates, and kernel terms support
    different conclusions. The book will name which one it has.

### 5. How to read the book

16. Explain the rhythm without presenting a workflow: problem, small case,
    exact claim, evidence, attack, boundary, exercise.
17. Orient the reader to Parts I–III in conceptual terms: words and program
    meaning; minimality on real instruction sets; evidence and what remains
    open. Keep this short and revise when the later table of contents settles.
18. End on the prerequisite question created by the opening: before two
    programs can be equal, what exactly is the value in a register? This hands
    the reader directly to Chapter 1.

## Chapter 1: paragraph-level flow

### 1. Eight lamps, one number

1. Begin with the byte `11111111`. It can be 255, -1, a mask, or a divisor's
   exceptional result; the bits do not choose the interpretation.
2. Use a four-bit counter that wraps from 15 to 0. The wrap is the concrete
   clue that ordinary natural-number arithmetic is not the machine operation.
3. Name width and define a word as a residue modulo `2^n`. Read the definition
   back into the counter: values differing by `2^n` are the same word.
4. Define bits and the basic operations only as needed. State why this carrier
   matters: later instructions are total functions on a finite set.
5. Place the definition object after the reader can reconstruct it. Explain
   its present limitation: Axeyum rebuilds fixed-width terms on demand and has
   no reusable all-width word prelude in the kernel. **Hook:** a definition
   tells us the values; a specification must still tell us what each operation
   does at its awkward edges.

### 2. Why division needs an answer

6. Work ordinary division first: `7/2`, then `7/0`. In mathematics the second
   expression has no value.
7. Explain the machine-design pressure without claiming that a physical
   divider alone determines semantics: a total formal operation gives every
   bit pattern a result, which lets tools and implementations compare the same
   function.
8. State the fixed-size bit-vector conventions for unsigned division,
   unsigned remainder, and signed division by zero, with a verified standard
   citation. Keep signed representation near the signed rule.
9. Use width four as the reader miniature. Enumerate the two signed cases and
   explain why all-ones represents both unsigned 15 and signed -1.

### 3. Proving a universal claim by refuting its opposite

10. State the width-eight unsigned-division claim in words, then as a
    quantified formula. Explain “for every” before negating it.
11. Negate the claim: ask for one byte that does not return all ones. A found
    byte refutes the theorem; no byte in the encoded domain establishes the
    fixed-width statement.
12. Give the reader proof from the operation's definition, explicitly noting
    that it is a proof of the specified semantics, not a derivation of why the
    standard chose the convention.
13. Place the unsigned-division object and interpret its scope and evidence
    route without hand-typing status language. **Hook:** one theorem can be a
    pattern; three in a row can still hide three distinct edge rules.

### 4. The other two edge rules

14. Prove unsigned remainder by zero at width four through the defining case,
    then scale the negated formula to width eight and place its object.
15. Explain the signed reading of a byte and split signed division into the
    negative and nonnegative cases. Place its object after the split.
16. Compare the three claims in a compact paragraph: same proof shape, three
    different returned words. **Transition:** now attack the checking route.

### 5. Make the checker lose

17. Propose the tempting false rule “unsigned division by zero returns zero.”
    At width four, any input supplies a counterexample because the specified
    result is 15.
18. Define a negative control in ordinary words, then place its object. The
    same route must accept the true formulations and reject the false one.
19. Explain what this rules out—a checker that reports the desired verdict no
    matter what—and what it does not rule out: a shared encoding error can
    infect the claim and control. **Hook:** this limit leads to the exact kind
    of evidence the current route exports.

### 6. What the verdict carries

20. Define a front-door verdict: the command reports SAT or UNSAT, while the
    current book route does not export a separate certificate for the reader.
21. State Axeyum's current internal checking and the external trust boundary
    only as confirmed by current code, tests, and the reproduction guide.
22. Separate the three layers: fixed-width claim checked by the current route;
    reusable all-width word theory not yet admitted to the kernel; exported
    independent certificate absent. Use generated object status where needed.
23. End with the turn to Chapter 2: now that a word and a checked equality have
    meaning, we can ask whether two instruction sequences compute the same
    function and whether a cheaper one exists.

### 7. Exercises

24. **Reproduce:** hand-check all four-bit inputs for one edge rule, then run
    the width-eight object.
25. **Break:** mutate the expected result and explain the counterexample before
    running the control.
26. **Generalize:** state an all-width theorem and identify the missing kernel
    construction; do not ask the student to mistake bounded checks for it.
27. **Transfer:** count words and word-to-word functions, then explain why raw
    function count does not predict the ease of the division-by-zero proof.
28. **Design:** choose a different total convention and list what must change
    in a compiler, solver, and checker for the system to stay consistent.

## Object spine

| Object | Reader question | Human-scale argument | Machine route | Attack | Boundary |
|---|---|---|---|---|---|
| `W.def.word` | What is in a register? | Four-bit wraparound and residue classes | Definition record | Compare width four with unbounded naturals | No reusable kernel word prelude |
| `W.thm.udiv0` | What does unsigned division by zero return? | Direct defining case at width four | Negated width-eight SMT formula through the front door | `W.ctl.udiv0-wrong` | Width eight; no exported certificate |
| `W.thm.urem0` | What does unsigned remainder by zero return? | Direct defining case at width four | Negated width-eight SMT formula | Mutate expected result | Same route and width limit |
| `W.thm.sdiv0` | What does signed division by zero return? | Split negative and nonnegative four-bit values | Negated width-eight SMT formula | Swap branch results | Same route and width limit |
| `W.ctl.udiv0-wrong` | Can this checker reject a false claim? | All width-four inputs contradict zero | Same solver path expects a counterexample | The object is the attack | Does not exclude a shared encoding error |

## Draft review ledger

### First-draft critique

The first draft follows the DAG and reaches the planned handoff. Its strongest
choice is structural: the introduction earns the evidence vocabulary through
the missing lower bound, while Chapter 1 earns the solver query through a
four-bit case. The artifact boxes arrive after the reader knows what their
formulas mean. The three division rules have distinct human arguments, and the
negative control is not confused with a non-example.

The first draft also had five defects:

1. The opening said that two instructions reverse the register before naming
   the restricted single-register language. That made a scoped upper bound
   sound like an ISA-wide claim.
2. The HieraSynth sentence mixed the completeness of a search method with the
   fact that a particular run finishes. The revision now separates exhaustive
   coverage, termination, and the cost model.
3. Several exact terms arrived without an ordinary explanation:
   minimality, superoptimization, and counterexample. Each now receives a
   short definition at first use.
4. The prose checker found smart quotation marks in machine-facing chapter
   source. They were replaced with semantic emphasis.
5. Two arithmetic expressions lost their math delimiters during the initial
   edit. The revision restores them and the source check now passes.

Against VOICE.md, the draft is calm and concrete, but the unit-of-belief
section has six definitions in quick succession. The ideas depend on one
another, so removing one would break the chain; the second-draft reader pass
must test whether the pace feels like instruction or a glossary.

Against CRAFT.md, Chapter 1 has the full movement from encounter through
attack and boundary. The unsigned proof is load-bearing and has both forms.
The remainder and signed claims have shorter reader proofs appropriate to
their size. The main remaining craft risk is that the artifact boxes may feel
too similar when read in sequence.

Against PLAIN-ENGLISH.md, sentences are short and actors are usually named.
The first draft used unary, permute, and nonnegative before the checker could
recognize an explanation. The revision uses ordinary alternatives.

### Second-draft student read

I read the revised opening as a systems reader who has used compilers but has
not used this ledger or Axeyum.

- The byte-reversal question gives me a reason to learn the machinery. I can
  explain upper and lower bounds before any solver appears.
- The evidence terms are individually clear, but the unit-of-belief section
  still asks me to retain six nouns. I want one pass back through the opening
  example before the book moves on.
- I understand the four-bit wrap, but the symbol Z appears as if I have already
  agreed to quotient notation. I need one sentence that tells me what Z is and
  how to calculate without the notation.
- Axeyum first appears as a proper name beside a kernel limitation. I need to
  know its job before I can understand the limit.
- The signed division rule assumes I recall two's-complement interpretation.
  A one-line width-four calculation is enough; a sidebar would be too much.
- The sequence of three artifact boxes is repetitive, but the repetition now
  teaches a stable audit pattern: meaning, negation, route, scope. The short
  comparison after the third box keeps them from merging.
- The final boundary is demanding but fair. It tells me exactly why a green
  solver run is not yet an all-width kernel theorem.

The third draft responds with three small insertions rather than a new
structure: a byte-reversal recap maps all six evidence nouns onto one argument;
the word definition explains the integer notation; and Chapter 1 defines both
Axeyum's role and the needed two's-complement calculation at first use.

### Render review

The print build places the Introduction in roman-numbered front matter and
starts Basic Properties of Words as Chapter 1. The Introduction fills four
pages without a stranded heading. Chapter 1 fills five pages; its definition,
artifact, key-idea, and exercise blocks stay inside the text area and do not
split in confusing places. The first render exposed numbered 0.x Introduction
sections, so the generated wrapper now suppresses section numbers there while
leaving Chapter 1 numbering unchanged.
