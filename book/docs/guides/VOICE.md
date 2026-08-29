# Voice for *Instruction Sets, Programs, and Proofs*

This is the book's voice authority. It combines the discipline of a
from-first-principles textbook with the companionship of a patient teacher and
the narrative tension of a book about trust. It does not imitate any source
book's surface mannerisms. It takes what each model is good at:

- from Spivak, the pleasure of proving what the reader thought was merely true;
- from Da Vinci Math, the movement from a concrete encounter to an exact name;
- from *The Certainty Machine*, the felt question of what deserves belief;
- from axeyum, the refusal to claim more than the evidence checks.

The result should sound like one technically serious person working beside
another at a kitchen table, with a blackboard nearby and a terminal open.

The book also carries a quiet sense of wonder. Its source is not grand
language. It is the moment when a small exact object reaches farther than it
seemed able to reach.

## 1. The relationship with the reader

The reader knows systems, code, or formal reasoning well enough to distrust a
hand-wave. They may not know a particular instruction, proof format, solver
route, or piece of notation. Treat that as missing context, never as missing
intelligence.

- Use **we** for a discovery or calculation the author and reader genuinely
  perform together.
- Use **you** for an action, choice, or exercise the reader can actually take.
- Name the actor when a compiler, solver, checker, standard, or researcher did
  something. Do not hide agency behind passive voice.
- Never flatter the reader, congratulate them for reaching a page, or announce
  that an idea is fascinating. Make the idea earn the reaction.
- Never call a step obvious. If it is easy, show it cleanly and move on.

## 2. The four registers

The book moves among four registers. A passage may change register, but the
change should be visible and purposeful.

### The kitchen table: ordinary explanation

Use familiar syntax and concrete verbs. Begin with the machine, program,
permutation, failed attempt, or question the reader can hold in mind. This is
the default register.

> Two programs leave 7 in the output register. One also changes the flag read
> by the next branch.

### The blackboard: definitions and reader proofs

Become compact, exact, and cumulative. Introduce notation before using it.
Read the point of a formula back into prose. The symbols shorten an idea the
reader already has; they do not manufacture understanding by themselves.

> A program is a composition of functions. Two programs are equivalent when
> that composition gives the same result for every allowed input.

### The workbench: artifacts and checking

Name files, hashes, formulas, proof logs, commands, and exit conditions without
turning the paragraph into build documentation. Tell the reader what each
piece contributes to belief and what failure would look like.

> The checker rebuilds the formula, reads the refutation, and rejects a
> truncated proof. That rejection is part of the evidence.

### The ledger: status and boundary

Use the generated vocabulary without drama: proved, computed, refuted, open.
State scope next to the claim. The ledger register should feel calm because it
is accountable.

> The result covers the selected scalar instruction forms under the printed
> observation. Memory faults and unlisted forms remain outside the claim.

Do not let the workbench or ledger register leak into every paragraph. A reader
needs the production facts only when they change what can be believed.

## 3. The characteristic sound

The voice is:

- **precise**, because scope is part of the theorem;
- **plain**, because complexity should live in the idea rather than the syntax;
- **dry**, because the evidence does not need promotion;
- **curious**, because familiar machine facts become strange when asked to
  justify themselves;
- **occasionally amused**, usually at a checker, specification, or proof that
  fails in an instructive way;
- **unsentimental about limits**, because an honest `unknown` teaches more than
  a broad claim the artifacts cannot support.

Humor should arise from the object: a million-byte certificate that carries no
information; a specification whose proof is a dead link; a negative control
that catches the checker. Do not add jokes around the mathematics.

## 4. Tension without theater

The book's tension is epistemic: a claim looks settled, then the reader asks
what would establish it. Use real oppositions:

- a sequence versus a lower bound;
- examples versus a universal statement;
- a witness versus a refutation;
- search versus checking;
- a solver verdict versus an exported certificate;
- a checked claim versus a kernel theorem;
- an instruction count versus a named cost model.

Do not inflate these distinctions with suspense language. State the familiar
belief, expose the missing warrant, and let the gap create the pressure.

## 5. What this book must not sound like

Avoid the voices of:

- a research paper compressing every premise into terminology;
- product documentation listing features and commands;
- a solver paper treating benchmark success as explanation;
- a school text that gives the name before the idea;
- a popular-science narrator replacing proof with wonder;
- an AI essay built from slogans, balanced triads, and repeated summaries;
- *The Certainty Machine* retold in miniature. That book owns the broad
  history of proof, trust, SAT, and proof assistants. This book applies the
  architecture to particular machine claims.

Internal words such as *pipeline*, *manifest*, *gate*, *projection*, and
*workflow* belong in reader prose only when the engineered mechanism itself is
the subject. Prefer the actual action: the checker reads, the solver searches,
the artifact records, the proof refutes.

## 6. Read-aloud and belief tests

Read every explanatory paragraph aloud. Keep it if it sounds like a competent
person explaining something they care about. Rewrite it if it sounds like a
paper abstract, a status report, a product page, or a transcript of terminal
output.

Then ask a second question: after hearing the paragraph once, can the reader
say both what the claim means and why they are entitled to believe it? If only
one survives, the paragraph is unfinished.

## 7. Beauty and mystery, earned by exactness

The book should help the reader love the subject. Do this by showing the
source of the feeling. Two symbols can encode every fixed-width word. A short
program denotes a function on every allowed input. A finite refutation can
rule out every program in a declared search space. These are precise facts,
and their reach is what makes them arresting.

Use this three-part movement at important turns:

1. Put an exact object before the reader: a bit, word, instruction, program,
   witness, invariant, or certificate.
2. Establish what it does or what has been proved about it.
3. Widen the view by one step. Show the finite object touching a universal
   claim, the written symbol becoming machine action, or a limit becoming new
   knowledge.

The widening sentence should be brief. It may invite a pause, but it must not
blur the evidence status. A bounded computation remains bounded. A solver
verdict does not become a theorem because its consequence feels profound.

Do not write, "This beautiful result reveals the mystery of computation."
Write the result clearly enough that the reader can see the source of wonder:

> We checked finitely many programs. Because those programs exhaust the
> declared language, their failure says something about every program in it.

Use such horizon moments sparingly: near the opening, after a major proof, at
a genuine boundary, and at a chapter turn. If every section reaches for the
cosmos, none of them will reach it. Words such as *beautiful*, *elegant*,
*astonishing*, and *mysterious* are conclusions, not substitutes for an
account. Prefer to make the reader feel them without being told.

Historical and literary voices may help articulate the horizon. Quote them
only when their words name the same live idea on the page. Verify the wording,
translation, edition, and context; cite the source; quote briefly; and return
at once to the mathematical object. The book may share Leibniz's amazement at
binary arithmetic or Stephenson's sense of a mathematical skeleton without
borrowing their cosmology, plot, or style.
