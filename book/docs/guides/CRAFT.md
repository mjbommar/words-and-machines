# Craft and pedagogy for *Instruction Sets, Programs, and Proofs*

This guide governs how the book teaches. Its central rule is simple:

> Every load-bearing theorem needs a reader proof and a machine proof.

The reader proof makes the reason visible. The machine proof establishes the
scoped claim through an artifact and a checker that can fail. A warm analogy
cannot replace checked evidence. A certificate cannot replace understanding.

A computed object follows the same teaching movement but keeps its honest
status: reader explanation plus checked reproduction, not two proofs. An open
object receives a precise statement, known footholds, and a clear missing
obligation, not manufactured closure.

## 1. The teaching movement: concrete to exact

For a new idea, use this movement unless the mathematics gives a better one:

1. **Encounter.** Give the reader a program, register, permutation, formula,
   failed search, or claim they can picture or try.
2. **Question.** Ask the exact thing at stake. Does the program work? Can one
   instruction suffice? What does the cost exclude?
3. **Notice.** Work a small case or failed attempt until the relevant pattern
   or obstruction becomes visible.
4. **Name.** Introduce the exact term after its meaning has begun to form.
5. **Reader argument.** Expose the invariant, contradiction, exhaustive cases,
   construction, or replay that explains why the result holds or how the
   computation covers its declared domain.
6. **Formal object.** State the quantified claim, program space, cost model,
   or definition without hidden premises.
7. **Machine evidence.** Show the artifact, checker, and evidence route; use
   *proof* only for a theorem whose route warrants it.
8. **Attack.** Give the checker a false claim, bad witness, damaged proof, or
   near-miss it must reject.
9. **Boundary.** Show a non-example or neighboring case the argument does not
   settle.
10. **Consequence.** End with what the reader can now conclude or ask next.
    At a major turn, let the exact result open onto its larger implication.

This is a movement, not a ten-heading template. Combine steps when the idea is
small. Slow down when a definition changes the rest of the book.

### The horizon beat

Some consequences deserve one further beat. After the proof and its boundary
are secure, show why the result changes how the reader may see computation.
The beat can connect:

- a finite alphabet to the range of things it can represent;
- a local instruction to the function it defines on every input;
- an explicit witness to existence;
- an exhaustive failure to a universal lower bound;
- a mechanical check to the human choice of definitions and scope;
- a proof boundary to the next real question.

This is not an additional proof step and must never repair an incomplete one.
Keep it to a sentence or short paragraph. Use it when the scale of the
consequence has genuinely changed, not on a fixed schedule.

## 2. The two proofs, when the object is a theorem

### The reader proof

A reader proof should be small enough to reconstruct without the solver. It
may be:

- a tagged four-lane version of a thirty-two-lane permutation;
- an invariant preserved by every allowed instruction;
- a contradiction reached from a one-instruction assumption;
- a truth table or complete split over a tiny domain;
- a witness replayed one instruction at a time;
- a diagram that makes a restricted movement impossible;
- a reduction whose two directions are checked in prose.

It need not prove the industrial-size instance by itself. Its job is to make
the reason and the encoding legible.

### The machine proof

The machine proof must name:

- the exact statement and scope;
- the artifact or witness;
- the program that checks it;
- the expected success condition;
- a negative control or mutation that fails;
- whether the evidence is a verdict, a load-bearing certificate, a
  computation, or a kernel-checked term.

The artifact box is where these facts become compact. It is not where the
reader first learns the idea.

For a computed object, replace this subsection's proof claim with the exact
reproduction contract: the finite domain, enumeration or search procedure,
independent check where available, and the condition under which the command
fails. Agreement between two computations is stronger evidence than one run;
it is still not a theorem certificate.

### The handoff between them

Tell the reader how the small proof becomes the large check. If four lanes use
tags, explain how thirty-two lanes use the same semantics. If a truth table is
replaced by SAT, say which choices became variables and what UNSAT rules out.
The encoding boundary is part of the lesson.

## 3. Example, non-example, boundary, control

Use four distinct teaching objects:

| Object | Question it answers |
|---|---|
| Example | What does the idea look like when it works? |
| Non-example | What tempting case fails the definition or argument? |
| Boundary case | Where does the current method stop deciding? |
| Negative control | Can the checker reject evidence or a claim that is wrong? |

Do not collapse them. A negative control is evidence about the checker, not
merely another example for the reader. A boundary case is not a failure of the
theorem; it marks where the theorem ends.

Good proofs welcome attacks. Ask the objection a skeptical systems reader
would ask: another operand form, a different width, a memory instruction, a
cleverer schedule, a truncated certificate, a solver that prints UNSAT for
everything. Answer it or put it visibly outside the scope.

## 4. Artifact placement

An artifact box should arrive after the reader can answer three questions:

1. What concrete claim is being checked?
2. Why would SAT, UNSAT, a witness, or a replay bear on that claim?
3. What space of alternatives does the encoding cover?

After the box, interpret it. State the consequence, the trust boundary, and
the nearest excluded case. Never strand a box between two sections without a
sentence that says what changed in the reader's knowledge.

Keep command transcripts and metadata proportional to their teaching value.
A hash matters when it pins the checked bytes. A variable count matters when
it explains scale. A file name matters when the reader can reproduce the
claim. Otherwise the detail belongs in the ledger or reproduction guide.

## 5. Chapter architecture

Before drafting, give the chapter an object spine. For every load-bearing
object record:

- its question in reader language;
- the prerequisite idea;
- the reader-proof miniature;
- the formal claim;
- the current ledger status and evidence route;
- the attack or negative control;
- the boundary case;
- the larger implication, if the object earns one;
- the exercise or next-door question it unlocks.

A typical chapter then follows this arc:

1. **Opening problem.** A real machine claim whose missing warrant can be
   felt immediately.
2. **Construction.** Build only the definitions needed to state it.
3. **First payoff.** Let the reader prove or replay a small version.
4. **Scale-up.** Translate the same reason into a search space and artifact.
5. **Audit.** Attack the checker and name the trust boundary.
6. **Turn.** Reveal the distinction or obstruction that motivates the next
   chapter.
7. **Exercises.** Let the reader reproduce, break, generalize, or transfer the
   method.

Historical material belongs only when it sharpens the live machine question.
Do not rebuild a general history of logic or automated reasoning; that is not
this book's job.

## 6. Exercises carry the subject

Exercises are not review questions appended after the lesson. They are the
next layer of the book. Use four kinds:

- **Reproduce:** run or hand-check an existing object on a smaller instance.
- **Break:** mutate a claim, proof, scope, or checker and observe the failure.
- **Generalize:** change the width, instruction family, operand model, or cost
  profile and state what new proof obligation appears.
- **Transfer:** apply the method to another ISA, compiler rewrite, circuit, or
  published exhaustive table.

Give enough information for a serious attempt. Supply solutions or durable
solution sketches for closed exercises. If the answer is not known, make it an
open object and say so; do not disguise a research problem as routine practice.

At least one exercise per chapter should make the reader act as the checker.
At least one should expose a boundary rather than extend a success.

## 7. Openings, endings, and promises

Open with the object or belief, not with the chapter's taxonomy. Prefer
"Two programs leave the same output and different flags" to "This chapter
introduces observational equivalence." Let the exact term arrive after the
question has shape.

End a section with new leverage: a result, distinction, failure, or question.
Do not summarize the section back to itself.

Track book-scale promises. When the Prologue says that a checker must be seen
to fail, later chapters should call back to the first negative control. When
Part I distinguishes equivalence from minimality, every later lower bound
should pay that promise with a declared search space. A callback must add
meaning; repeated wording is not a callback.

## 8. Figures and code

Use a figure when it makes a relationship visible: lane movement, a search
tree, a certificate dependency, an hourglass of trust, or the boundary of an
instruction language. The prose must interpret the figure, and meaning must
not depend on color.

Code should be executable enough to inspect and short enough to teach one
move. Introduce inputs and outputs before the listing. After it, point to the
line that carries the proof obligation. A full command belongs in a
reproduction guide unless running it is itself the lesson.

## 9. Draft and revision tests

Before calling a chapter draft complete, ask:

- Can the reader picture the opening problem?
- Does each exact term arrive after or with its meaning?
- Is there a reader proof for every load-bearing theorem and a reader
  explanation for every computation?
- Does the formal statement match the checked object exactly?
- Can the reader tell what the negative control attacks?
- Is there a non-example and a genuine boundary case?
- Does each artifact box change what the reader knows?
- Do the exercises advance the subject?
- Does the close open the next question instead of repeating the chapter?
- Where does exactness earn a moment of wonder, and is that moment supported
  by what the chapter has actually established?

Mechanical style and vocabulary reports cannot answer these questions. They
are editorial gates, checked by reading the chapter in order.
