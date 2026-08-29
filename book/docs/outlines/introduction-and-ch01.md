# Introduction and Part I: paragraph-level writing plan

This plan is subordinate to MASTER.md and A0-SPEC.md. It governs the
Introduction and Chapters 1--5. The paragraph numbers describe teaching moves,
not permanent labels for the finished prose. Each paragraph must earn the next.

## Concept dependency graph

The first part follows one main dependency chain:

    pattern of bits
      -> fixed-width word -> readings -> operations -> width changes -> bytes
      -> complete state -> architectural boundary -> observation
      -> operands -> decoded instruction -> explicit effects -> one step
      -> finite byte memory -> address range -> split/store/load/join -> aliasing
      -> immutable program -> PC-directed execution -> trace -> halt/trap/bound
      -> contextual replacement

Three threads cross that chain.

- **Real machines:** each chapter first builds the common idea in A0, then asks
  how an RV64 slice and an x86-64 slice realize it. The windows name one exact
  dimension; they do not use RISC and CISC as explanations.
- **Grounds for belief:** definitions and hand arguments come first. Each
  chapter then states the missing Axeyum obligation without pretending that an
  object ID or solver can fill it. Controls are designed beside the obligation.
- **History and design:** history appears when it explains a live constraint:
  finite storage, byte addressing, stored programs, explicit registers,
  implicit flags, and compatibility. It never becomes a detached chronology.

The reader should finish Part I able to execute A0 by hand and to identify the
semantic questions that a real-ISA model must answer. They should not yet be
asked to trust an unbuilt executable semantics.

## Introduction -- What does this instruction mean?

### Opening: one addition, several machines

1. Put 0xff in a one-byte place and add one. State the visible result, then
   vary width, carry observation, storage, and failure. **Hook:** the plus sign
   stayed fixed while its world changed.
2. Name the instruction set as the body of rules that supplies that world.
   Separate processor, assembler, ABI, and microarchitecture in ordinary
   language. **Transition:** to compare machines, first construct enough of one
   to finish its definition.

### A0: a machine small enough to finish

3. Introduce A0 through its purpose, then list only its reader-visible parts.
4. Explain why an artificial machine is useful: no inherited compatibility and
   nowhere for an architectural effect to hide. Do not call it ideal.
5. Pose the questions A0 lets us answer in order: value, location, action,
   memory, next instruction, end of execution. **Transition:** after each answer,
   the same question can be carried to a real architecture.

### Two sustained companions

6. Introduce RV64 and x86-64 as bounded slices, not representatives in a
   contest. Explain why exact manual revision, mode, forms, and ABI matter.
7. Give a compact paired example: three-register addition versus a
   destination-as-source form with condition flags. This is a preview, not a
   semantic claim about unpinned slices.
8. Replace the RISC/CISC slogan with named comparison dimensions: length,
   operands, memory access, condition state, and address formation.
   **Transition:** those differences matter only when we state what program
   behavior we intend to compare.

### From an execution to a claim

9. Ask whether two programs that leave the same output are equivalent.
10. Add the hidden differences one at a time: scratch register, flags, memory,
    trap, and control. Define neither state nor observation yet; create their
    need.
11. Contrast examples with a universal claim. A test can find an error but a
    successful test set does not cover every state.
12. Explain the semantic trust chain: statement, model, formula, result,
    checker. Use reversed byte order to show how perfect checking can establish
    the wrong claim. **Transition:** the book needs two forms of support.

### Reader proof, machine proof, and attack

13. Define the reader proof by what it supplies: a reason a person can rebuild.
14. Define the machine proof by what it supplies: coverage of the printed
    finite scope through evidence a checker can reject. Keep computations in
    their own category.
15. Introduce the negative control as a deliberate error, and state its limit:
    one rejected error does not prove the positive claim.
16. State the present boundary: the semantic design is ahead of the Axeyum
    implementation. **Transition:** drafting order is part of the book's honesty.

### Route and invitation

17. Preview the four parts as one argument rather than a contents list.
18. Explain the ledger in one paragraph: it prevents prose from outrunning
    evidence but is not the subject a beginner must learn first.
19. Close on the smallest shared object, one word, and the reach of a finite
    rule over every value of that width. **Hook:** first separate the stored
    pattern from the meaning an operation gives it.

## Chapter 1 -- Words and Their Meanings

### Opening: the pattern does not confess

1. Put 11111111 on the page and give several defensible readings.
2. Draw the governing distinction: storage supplies a pattern; an operation or
   convention supplies a reading. **Hook:** build the finite carrier first.

### A finite circle

3. Encounter a width-four counter wrapping from 15 to 0.
4. Define a width-\(w\) word as a residue modulo \(2^w\); explain the natural
   representative in prose.
5. Prove width-four increment wraparound by the remainder rule.
6. Generalize to \(2^w\) words and a finite domain for a fixed-width
   instruction. **Horizon beat:** a short rule reaches every member.

### Positions and bitwise action

7. Define bit position using a four-bit example before the formula.
8. Define Boolean operations position by position; work and and xor.
9. Explain left and logical-right shifts as multiplication and division.
10. Present arithmetic right shift as an operation tied to signed reading.
    **Transition:** the bits do not announce which reading applies.

### Two integer readings

11. Define unsigned reading.
12. Build two's-complement reading from the high-bit split; work 0111, 1000,
    and 1111.
13. Prove the signed range; separate stored addition from signed overflow.
14. Give a non-example: calling a stored word negative without naming a
    reading. **Transition:** readings also govern width changes.

### Changing widths

15. Define truncation by remainder and show information loss.
16. Contrast zero extension and sign extension on 1111.
17. Prove the two small preservation claims.
18. Preview real-ISA narrow-result rules. **Transition:** byte-multiple widths
    admit the structure needed for memory.

### One word, several bytes

19. Define a byte and motivate byte-addressed memory without defining memory.
20. Define little-endian split and join after working 0x12345678.
21. Prove round trip first for two bytes and then for the finite sum.
22. Give the reversed-order non-example and name what changed.
23. Name the boundary: width-four is a proof miniature; full A0 widths are
    positive multiples of eight.

### Companion windows and evidence boundary

24. Explain how fixed-width values, readings, and width rules become questions
    for the two later companion slices.
25. State what the definitions establish and what the open A0 word package
    must implement in Axeyum.
26. Design controls: wrong modulus, wrong sign extension, reversed byte
    weights, and a damaged round trip.
27. Close on what a word lacks: location, next instruction, conditions, and
    outcome. **Hook:** those facts belong to state.

### Exercises

28. Execute: wraparound, readings, extension, and byte joining.
29. Break: construct a false join or extension rule and a witness.
30. Prove: split/join for two bytes and arbitrary byte count.
31. Transfer: state the width rule for one pinned form from each companion ISA.

## Chapter 2 -- State

1. Freeze execution between instructions and inventory what remains.
2. Define complete A0 state, including running, halted, and trapped outcomes.
3. Explain why program code is separate and immutable in the first model.
4. Distinguish architectural from microarchitectural state through functional
   and timing questions.
5. Give a missing-component non-example.
6. Introduce observation after the scratch-register problem is clear.
7. Prove that equality under a projection need not imply full equality.
8. Require the observation to be chosen before seeing the result.
9. Carry the inventory to RV64 x0 and selected x86-64 flags as obligations.
10. State the open Axeyum state/memory obligation and projection controls.
11. Close on motion: state is a snapshot; an instruction gives the next one.

## Chapter 3 -- Instructions and Operands

1. Show why the mnemonic add is not an instruction meaning.
2. Build an instruction instance from operation, form, and concrete operands.
3. Define operands by value source, access role, width, and hidden effects.
4. Work A0 add r0,r1,r2, naming every read, write, flag, and PC change.
5. Define a single step as decode plus transition.
6. State the explicit-effects principle; attack hidden writes and wrong PCs.
7. Compare a three-role RV64 form with a destination-as-source x86-64 form.
8. Prove that equal destination values need not make equal state transformers.
9. Explain immediate, memory, and relative-target operands.
10. Introduce composition and show why halt or trap has no successor.
11. State the open Axeyum step obligation without claiming a decoder exists.
12. Close on the operand that reaches outside registers: memory.

## Chapter 4 -- Memory

1. Store one 32-bit word and ask what each address receives.
2. Define finite byte-addressed data memory and separate it from program code.
3. Define valid range and A0's unaligned-access policy.
4. Work the little-endian store, then load it back.
5. Prove store/load reconstruction under the valid-range premise.
6. Break the premise at memory's end; explain atomic trap behavior.
7. Define effective address as wrapped word addition plus a range check.
8. Define aliasing by overlapping byte ranges; work overlapping stores.
9. Prove why disjoint stores commute and why overlap breaks the proof.
10. Compare separate RV64 loads/stores with selected x86-64 memory forms.
11. State the open Axeyum obligation and its controls.
12. Close on time: memory makes order visible, and the PC decides order.

## Chapter 5 -- Programs and Control

1. Put two instructions beside each other and ask why the second runs.
2. Define an A0 program as immutable bytes, entry PC, and code range.
3. Define a trace and hand-run a short straight-line program.
4. Separate sequential PC update from textual adjacency.
5. Trace taken and untaken A0 branches.
6. Compare RV64 register predicates with an x86-64 flag predicate.
7. Distinguish halt, trap, bound exhaustion, and continued execution.
8. Give the contextual-replacement counterexample.
9. Repair it by requiring agreement on every component a suffix can read.
10. State the open Axeyum trace obligation and its controls.
11. Review Part I by executing one complete A0 trace.
12. Close toward decoding: the machine has meaning, but bytes need a decoder.

## Part I acceptance tests

- Every A0 definition agrees with A0-SPEC.md; width-four examples are never
  presented as executable full A0 states.
- Every chapter contains an encounter, a worked miniature, a non-example or
  attack, a boundary, a paired real-ISA window, and exercises that execute,
  break, prove, and transfer.
- Definitions and reader proofs are not described with generated status words.
- Open Axeyum obligations are visible, but implementation metadata never
  replaces an explanation.
- Historical material answers a live design question and carries a verified
  citation if it makes a factual claim beyond the definitions on the page.
- The end of each chapter creates the need for the next concept.
