# Plain English for *Instruction Sets, Programs, and Proofs*

This is the book's language standard. It makes the promise in
[SPIRIT.md](../SPIRIT.md) usable on the page: a reader can see what a claim
means, what was checked, and what remains outside the claim. It works with
[VOICE.md](VOICE.md) and [CRAFT.md](CRAFT.md), and supplements
[STYLE.md](STYLE.md) and [SIMPLIFIED-ENGLISH.md](SIMPLIFIED-ENGLISH.md). When
their generic guidance conflicts with a book-specific guide, use the
book-specific guide.

Plain English here does not mean small words, a fake conversational voice, or
less mathematics. It means that each sentence lets a technically literate
reader recover the intended meaning without guessing the hidden premises.

## 1. Reader, voice, and teaching aim

Write for a practitioner who can read code and follow a proof, but may not
know SAT certificates, a particular ISA, or axeyum. Meet that reader as an
intelligent peer.

- Prose is precise, dry, and occasionally amused. It is kitchen-table prose:
  direct enough to read aloud without sounding like documentation or a paper.
- Definitions, formulas, object records, and code are blackboard material.
  They may be compact, but the prose before or after them must say what they
  establish and why the reader should care.
- Prefer `we` when genuinely discovering an argument with the reader; prefer
  a named actor for historical or technical actions. Use `you` only in an
  exercise or a direct instruction.
- Respect the reader's intelligence. Do not call a result "obvious," hide a
  qualification in a footnote, or replace an exact word with a vague one.

## 2. The explanatory order

Introduce an idea in the order a reader can use it. CRAFT gives the full
chapter pattern; this is the sentence-level version:

1. **Question.** State the concrete thing at issue.
2. **Meaning.** Give the exact term and define it in ordinary words.
3. **Concrete case.** Show the function, program, move, or smallest useful
   example before the general encoding.
4. **Reader argument.** Expose the invariant, contradiction, exhaustive split,
   construction, or other reason a person can follow.
5. **Machine evidence.** Say what was checked and how bad evidence would fail;
   call it a proof only when the object's status and route support that word.
6. **Boundary.** State the width, ISA subset, cost model, assumptions, or
   other limit that keeps the claim honest.
7. **Consequence.** Say what the result permits the reader to conclude, and
   no more.

Not every paragraph needs all seven moves. A new load-bearing concept does. An
artifact box normally carries evidence and boundary; surrounding prose must
still supply the question, meaning, reader argument, and consequence.

## 3. Claim grammar

Every material claim should answer these questions in visible prose:

| Ask | Write |
|---|---|
| What is the subject? | Name the program, function, object, or machine. |
| What is being claimed? | Use a concrete verb: computes, refutes, reproduces, checks, or leaves open. |
| Under what scope? | Name the width, instruction families, operands, cost model, or input class. |
| What supports it? | Name the artifact and checker, or the source for a historical claim. |
| What does it not show? | State the excluded machine behavior or unproved generalization. |

Use the ledger's words exactly. A result can be **proved**, **computed**,
**refuted**, or **open** only through its generated object status. In ordinary
prose, do not promote a solver verdict to a kernel theorem, a reproduced table
to a proof, or a bounded result to an all-width result.

Prefer:

> For every allowed A0 state, the two programs produce the same output word
> and outcome under the declared observation. The checker does not compare
> scratch registers or behavior after a memory trap.

Not:

> The programs do the same thing.

The first tells the reader what is true, why it is true here, and where it
stops. The second turns a scoped theorem into a slogan.

## 4. Terms, abbreviations, and notation

- Use one preferred term for one book concept. The declared terms in
  `book.yaml` are the spellings to retain. Do not alternate *record*, *entry*,
  and *object* when the ledger's object is meant.
- Define a term before its first load-bearing use. A good first use gives the
  name and a short ordinary-language definition: "A **negative control** is a
  deliberately false claim that the same checker must reject." Mark a true
  defining occurrence with `\keyterm{...}` where the authoring contract
  permits it.
- Expand an abbreviation at first use, then use the short form consistently:
  "the satisfiability solver (SAT solver)." Keep familiar specialist strings
  in code and object IDs exactly as the artifact requires.
- Keep notation close to its meaning. Tell the reader what a quantifier ranges
  over and what a symbol stands for before using it in an argument. Read a
  displayed formula in a sentence after showing it when its conclusion matters.
- Do not use a synonym merely to avoid repetition. In technical exposition,
  stable names reduce the reader's memory load.

## 5. Sentence and paragraph rules

- Use an active, named verb whenever possible: "the checker rejects the
  truncated proof," not "the proof is rejected."
- Give the main claim early. Put conditions after it unless the condition is
  the point of the sentence.
- Prefer one logical move per sentence and one teaching move per paragraph.
  Split a long sentence when it introduces both a new term and a qualification.
- Put a worked miniature before a large number when the mechanism is new. A
  number, formula, or artifact size needs context, not applause.
- Use contrast to teach real distinctions: theorem versus convention, witness
  versus refutation, computed result versus proof. Do not manufacture contrast
  with "however," "importantly," or other filler.
- Keep qualifiers next to the claim they qualify. A reader must not discover
  two sentences later that “x86-64” meant three selected scalar forms under a
  destination-only observation.

## 6. A revision test

For each new definition, theorem, artifact paragraph, and exercise, ask:

1. Can a reader say what problem this addresses before they reach the object ID?
2. Are the technical term and any abbreviation explained before they carry the
   argument?
3. Does the prose name the evidence route and the negative control where one
   is relevant?
4. Can the reader identify the scope without following a cross-reference?
5. Does the final sentence state the consequence or the remaining limit rather
   than repeat the claim?
6. Could the reader explain why the result holds without reciting the artifact
   metadata?

If any answer is no, revise the prose rather than adding an adjective, a
status word, or another artifact reference. Then run `make check` and
`make simplified`; treat their output as prompts for review, not substitutes
for this test.
