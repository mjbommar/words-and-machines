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

### The book-scale spine and heading hierarchy

The contents page must expose the proof spine, not every local turn in the
prose. The print and EPUB navigation therefore use three public levels:

1. **Part** -- one major stage of the book's argument;
2. **Chapter** -- one durable subject or proof obligation;
3. **Section** -- one major conceptual movement within that chapter.

Subsections are local teaching aids. They may separate a derivation, worked
example, historical cause, present consequence, attack, or boundary inside a
section, but they do not appear in the print contents. Do not use a subsection
before its parent section, use a starred structural heading, or create a
subsection merely to label one or two paragraphs.

Parts and chapters use title case. Sections and subsections use sentence case.
Prefer a short noun phrase or direct question that names the object on the
page: ``Effective addresses and valid ranges,'' not ``A range is a set of byte
addresses, not two unchecked endpoints.'' A heading is navigation, not the
first sentence of the argument. As working limits, keep section titles at ten
words or fewer and subsection titles at twelve words or fewer. Exceed those
limits only when the exact technical name requires it.

Parallel jobs receive parallel names. Every chapter ends with ``Exercises.''
Use ``Implementation boundary'' for the Part I construction chapters and
``Where the model stops'' for later chapters that apply a selected real-ISA or
proof model. Do not cycle among decorative synonyms for the same structural
function.

The index and glossary serve different jobs. Mark the defining occurrence of
a durable term with `\keyterm`. Add `\indexentry` at its defining passage and
at later passages that compare, derive, or materially qualify the concept. The
two actions are separate because a bold local definition does not always merit
a durable index entry. The glossary gives a short recovery
definition for terms the reader must carry across chapters. It does not replace
the in-place explanation and should not collect every bold phrase.

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

### Three explanatory lenses

Every chapter must explain its subject through three connected lenses. These
are not three detachable sidebars. They belong where they change the reader's
understanding of the object on the page.

1. **Origins.** Recover the problem that made the concept necessary, the
   people and machines that gave it a durable form, and the alternatives that
   were still live at the time. Prefer original papers, manuals, standards,
   patents, oral histories, and surviving machines to a story repeated from a
   later textbook. Avoid simple invention myths: distinguish the first known
   instance, independent development, standardization, and widespread use.
2. **Foundations.** Build the relevant mathematics, logic, physics, electrical
   engineering, and computer science from the smallest model that explains the
   behavior. Connect levels explicitly: charge or timing to a stored bit;
   Boolean algebra to logic; congruence to wraparound; a state transition to
   execution; a relation to refinement. State which physical details the ISA
   abstracts away.
3. **Present consequences.** Show what the concept costs or permits in current
   practice: silicon area, energy, latency, bandwidth, code size, compiler
   freedom, compatibility, verification effort, licensing, manufacturing,
   cloud cost, security, or maintenance. Name the relevant actor and unit of
   account. Do not turn a vendor claim, benchmark, list price, or market
   estimate into a timeless fact; date it, source it, and state its limits.

History earns its place when it explains why the present object has its shape.
Industry and economics earn their place when they explain a real constraint or
choice. Foundations earn their place when they let the reader derive rather
than memorize. None may become a general survey detached from the chapter's
semantic spine.

### Breadth and depth, not page quotas

A chapter is not complete because it reaches a word band. Before declaring it
complete, compare its coverage with authoritative specifications, university
course expectations, and at least two substantial textbooks. Record the
comparison in the chapter research contract. Then classify every neighboring
topic as one of:

- **derive here** -- the reader needs the mechanism or argument in this
  chapter;
- **work here** -- the reader needs several examples or exercises, but an
  earlier chapter supplied the definition;
- **route explicitly** -- another named chapter owns the full treatment;
- **exclude explicitly** -- the book does not teach it, and says why.

Coverage requires enough independent examples for transfer, not repeated
versions of one example. A central concept normally needs a smallest case, a
real-machine case from each sustained ISA, a failure or edge case, and an
exercise that changes an assumption. A chapter whose central mechanism fits
in fourteen pages may be sound, but a broad chapter called "Memory" is not
complete if those pages must also carry representation, addressing, physical
storage, ISA behavior, performance, safety, and proof.

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

Code in a listing is an executable promise, not a picture of a future API.
Keep it short enough to teach one move, but require a parser, assembler, or
runtime harness that the repository gate executes. Put an unimplemented
interface contract in prose until that harness exists. If an algorithm sketch
is more useful than source code, call it pseudocode in both the lead-in and the
caption and give it a structural checker. Introduce inputs and outputs before
the listing. After it, point to the line that carries the proof obligation. A
full command belongs in a reproduction guide unless running it is itself the
lesson.

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
