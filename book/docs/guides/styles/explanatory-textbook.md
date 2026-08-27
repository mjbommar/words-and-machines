# Style Profile: Explanatory Textbook

Layered over [STYLE.md](../STYLE.md) — select with `style.profile:
explanatory-textbook` in `book.yaml`. For prose whose only job is to make a hard
technical subject genuinely understood by a motivated novice: curriculum lesson
bodies, concept articles, standards explainers, university textbooks. No
narrative scaffolding, no runnable artifact, no deadline.

Distinguish it from its neighbours. `practical-guide` assumes the reader wants
to act and needs equipment. `technical-handson` makes runnable code the
pedagogy and demands opinions. This register makes **the derivation** the
pedagogy and demands that no step of it be missing.

## Reader and register

A motivated novice who chose to be here, will be examined on this, has read the
section once already, and is stuck on one specific joint in the reasoning.

**The office-hours test.** Could you say this to one student across a desk, with
a pencil and one sheet of paper between you, three minutes into a conversation
that began "I don't see how you got from the invoice to the income statement"?
If it sounds like a lecture-hall performance, an exam-review sheet, a
codification paraphrase, or a study guide, rewrite it.

The defining posture is patience under load: neither breathless nor neutral to
the point of emptiness. The writer has decided what matters, will spend 200
words on the one step everyone skips, and will then say plainly what the
explanation left out.

## Person and tense

- **"We" for shared derivation** — the dominant person. "We can pay the invoice
  in either period, so we need a rule that decides which income statement
  carries the expense."
- **"You" only where the reader acts on the page**: reads a statement, computes
  a ratio, commits to a prediction before a reveal. Never for hortatory address.
- **Third person, named, for the entity in the running example.** A real filer
  with a real filing date wherever one exists.
- Present for mechanism, past for events and for a standard's history.
- Never "one." Never "the student" or "students should be able to" in body
  prose; that is syllabus voice and belongs in an objectives block.
- Passive is permitted where the actor genuinely is the accounting system
  ("the balance is carried forward"), and forbidden where a person exists
  ("the entry should be made" → "the bookkeeper records the entry").

## Rhythm

The largest deviation from base STYLE.md, and deliberate. Measured against
exemplars: Feynman's atomic-hypothesis passage averages **40.8 words** per
sentence at a coefficient of variation of **0.26** — the longest sentences and
the *lowest* variance in a six-sample calibration set.

- **Sentence average 19–26 words.** Base house is 14–20. A causal chain with
  real subordination runs 28–35 words and must not be broken into three.
  Prose averaging 15 words in this register has almost always achieved it by
  deleting the connectives, which is the same as deleting the explanation.
- **No error ceiling.** `sentence_hard_max: 55`, warning only. Past 55 words the
  fault is two independent claims in one sentence, or a list that should be
  displayed — not length itself.
- **The floor is the real constraint.** No more than two consecutive sentences
  under 12 words outside a numbered procedure. **Zero fragments**, overriding
  base STYLE.md §3, which permits about two per page. **Zero one-sentence
  paragraphs**, because that is the natural habitat of the aphoristic closer.
- **Never prescribe alternation.** Do not follow a 30-word sentence with a
  5-word one on purpose. Length variance is a byproduct of clause architecture:
  a two-clause step is shorter than a four-clause one because it has fewer
  conditions. Choreographed alternation is itself a detection signature.
- **Paragraphs 4–9 sentences, 110–200 words.** One paragraph does one step of
  the derivation. The shape is **the question the reader is holding → the step →
  why the step is forced → what the step now permits.**
- **Never end a paragraph on an aphorism.** End on the last piece of new
  information. If the closing sentence could be lifted out and quoted
  approvingly, it is decoration and it misrepresents how much work the
  paragraph did.
- **No bold or italic emphasis.** A term is introduced by syntax — an
  appositive, a colon, a definitional relative clause. Italics keep two jobs:
  titles of works, and a foreign term at first use.

## Density

The **instructional unit** is the smallest thing a reader can be examined on.

- **350–700 words per instructional unit.** Under 350, the compressed step is
  still compressed. Over 700, two units are wearing one heading.
- **One new concept per unit, at most 5 per chapter. 6–9 new named terms per
  chapter.** Every term is defined by apposition at first use, then used by its
  real name forever after.
- **At most 3 new notational objects per chapter.**
- **One running entity per chapter**, carried start to finish, amounts in
  numerals throughout.
- **One analogy per concept, then commit.** Re-analogizing doubles the reader's
  model count while appearing generous.
- Budget: at least 60% mechanism, at most 25% worked computation, at most 15%
  apparatus. Inverting the first two makes a problem set with commentary.

## Structural shape

1. **The question, in the form a practitioner is actually asked.** Not "in this
   chapter we examine revenue recognition" but the question a controller gets.
2. **The compressive claim** — the one sentence that would regenerate most of
   the chapter. State it flatly, before any formalism, undecorated.
3. **The concrete instance, magnified.** One object at human scale, then
   increase resolution until the mechanism is visible. Keep the same object
   across magnifications.
4. **The reader's wrong model, once, immediately before the correction.** See
   the next section; this step is mandatory.
5. **The derivation, with every step written.** Where the register earns its
   existence and where the expert blind spot destroys books.
6. **The boundary, stated once and specifically.** What was simplified, what the
   standard actually says that we did not, where the model stops predicting.
   Never "a full treatment is beyond the scope of this book," which names
   nothing.
7. **The transfer case, or the last new fact.** No summary. No restatement of 2.

## The mandatory misconception step

Every instructional unit inhabits at least one misconception before stating the
correct rule. This is empirically grounded rather than a taste preference, and
the research also constrains *how* it is done.

Refutation texts outperform plain exposition at a pooled **g = 0.41**
(Schroeder and Kucera 2022, *Educational Psychology Review* 34(2), k = 44,
n = 3,869, p < .001). Conceptual change requires coactivation of the wrong and
right ideas (Kendeou and van den Broek 2007), so the wrong idea has to be on the
page. The old worry that repeating a misconception reinforces it does not
survive review: Swire-Thompson, DeGutis and Lazer (2020) conclude that
"backfire effects are not a robust empirical phenomenon" and that "avoiding the
repetition of the original misconception within the correction appears to be
unnecessary and could even hinder corrective efforts."

The design constraints that follow, from the *Debunking Handbook 2020* (p. 13):
**"Repeat the misinformation, only once, directly prior to the correction. One
repetition of the myth is beneficial to belief updating."**

- **Once, not scattered.** One statement of the wrong idea, adjacent to its
  correction, never restated later in the unit.
- **Never leave it unrefuted on the page.** The correction lands in the same
  section, not a later one.
- **Give it its strongest case.** Explain why a reasonable person holds it and
  where it came from. A subordinate clause ("students sometimes think X, but
  actually Y") does not satisfy this.
- **Supply an alternative account that fills the causal gap**, of no greater
  complexity than the idea it replaces.
- **Respect before repair.** "A student who learned the words there learned them
  correctly" does work that "watch this fail" only performs.

**Replace, never merely negate.** This is the one place the literature shows
actual harm, and it dictates a sentence-level rule. Autry and Levine (2021),
*Applied Cognitive Psychology* 35(4), 960-975, contrasted a negated correction
("not blue") with a replacement ("red"): "when not exposed to the concept,
negated corrections increased mentions relative to no correction." The
replacement did not produce the effect. In a textbook, where many readers never
held the misconception you are staging, a correction whose entire payload is a
negation makes things worse for them. Any sentence whose only content is "X is
not true" is a defect.

**Give the repair more words and more mechanism than the wrong idea got.**
Swire, Ecker and Lewandowsky (2017) found a main effect of explanatory detail
(F(1,90) = 15.38, p < .001) that grew with delay: detailed explanations sustained
belief change where brief ones did not. The one-clause refutation decays fastest.
Budget the wrong idea at 80-150 words and the repair at 150-300.

**Assume the correction expires.** The same study found "a striking asymmetry in
that belief change was more sustained after fact affirmation compared to myth
retraction -- retractions thus seemingly have an 'expiration date'." Myth belief
rebounds while fact belief stays stable. Re-break the same misconception in a
later chapter's worked example as spaced practice, deliberately.

**The correct rule owns every summary position; the wrong rule owns none.** The
repaired rule takes the closing declarative, the glossary entry, the index term,
and the assessment item. The misconception is never a heading and never appears
in a chapter summary. This substitutes structural salience for the typographic
emphasis this profile forbids, and it is the stronger instrument anyway.

**The misconception must have a real owner, not an author's guess.** Expert blind
spot cuts both ways here: Nathan and Petrosino (2003) found that participants
with more advanced subject knowledge were *more* likely to assume symbolic
mastery precedes problem solving, contrary to how students actually perform. An
author's intuition about reader error is systematically miscalibrated toward the
discipline's own formalisms. Draw the misconception from graded student work,
examiner reports, office-hours patterns, or the published education literature.

**Two honest limits.** No study manipulates the *number* of misconceptions per
document as an independent variable, so "one per unit" is a precaution rather
than a finding. And belief change does not reliably become behavior: Ferrero and
colleagues (2020) found refutation corrected educators' false beliefs but had "no
beneficial effect on teachers' intention to implement educational practices"
based on them. A student who can state that depreciation does not accumulate cash
may still compute as though it does, which is an argument for putting the
assessment item next to the refutation rather than at the end of the module.

**A caution about the form's best-known exemplar.** The question-and-answer
textbook often praised as Socratic is not doing this. Its questions are
exposition headings, answered in the next sentence, that the reader was never
invited to attempt -- the §1.9 tell at a rate of twenty to forty per chapter. A
question is an elicitation only when the text can state in advance the specific
wrong answer a reader would give, places work between the question and its
resolution, and marks that answer wrong within the same section. An undeclared
question is a rhetorical-question transition however well it would have scored.

## Craft moves

- **The compressive claim.** Open on the sentence that regenerates the rest.
  *Why it works:* it gives the novice somewhere to hang what follows, and unlike
  a summary it is checkable, so the reader can catch you if the derivation stops
  supporting it.
- **Magnify the ordinary object.** *Why it works:* novices acquire domain
  knowledge through concrete representations first. Nathan, Koedinger and
  Alibali (2001) measured ninth-graders solving verbal problems above 50% and
  symbolic ones below 30%, while high-school teachers ranked the symbolic ones
  easiest.
- **The blind-spot pass.** A named revision pass: mark every place the prose
  moves from A to C, and write B. Then give the marked draft to someone who has
  not learned the material and keep only the B-steps they needed. *Why it
  works:* the compression is invisible to its author by construction. Experts
  "are less likely to have access to memory traces of their cognitive
  processes… due to the automatization of certain cognitive processes," while in
  novices those processes "leave a memory trace which is more likely to be
  inspectable and verbalizable" (Nathan et al. 2001). Rereading cannot catch it.
- **The question in the reader's mouth.** Pose the question the reader is
  forming, in the reader's vocabulary, then answer it in sentences containing
  something the question did not. *Why it works:* writing the question first
  forces the author to model the novice's state rather than the subject's
  structure, and an answer that does not answer its own question becomes visible
  on the page.
- **The subordinated because-chain.** Carry causal structure in syntax —
  because, so that, unless, which means, only when — not in bullet lists.
  *Why it works:* a dependency between two facts is a grammatical relation, and
  moving it into a list deletes which fact depends on which.
- **One example, held.** *Why it works:* every new example costs a
  re-orientation paid out of the same working memory as the concept.

## Watch for

- **Step compression**, the signature failure. "Then we net the two" where three
  operations occurred.
- **The symbol-first slide** — opening on the formalism because it is most
  compressed and therefore feels efficient. This is the documented expert
  blind-spot behavior and it is what killed New Math.
- **Definition stacking.** Three terms defined before any does work.
- **Syllabus voice in body prose.**
- **The reassurance reflex** — "simply," "just," "straightforward,"
  "obviously," "intuitively." Each is a lie about difficulty told to a reader
  currently finding it difficult, and an admission that a step was skipped.
- **Emphasis doing syntax's job.**
- **The summary close and its worse cousin the aphorism.** A section that has
  just done hard work feels owed a flourish. It is owed nothing; it ends.
- **The exhaustive taxonomy.** Five classifications where the mechanism needs
  two, because completeness reads as rigour.
- **Tidy invented numbers.** A reader who never sees $8,432.17 has never seen a
  rounding decision.
- **The placeholder entity.** "Company C," "a small manufacturer." Name a real
  filer; where none exists, use the closest real case and say how it differs.
- **False hedging of a definition.** Hedge the boundary cases, never the rule.

## Three absolute word rules

No exceptions outside direct quotation.

1. **"Worth" is reserved for literal financial value.** Never "worth noting,"
   "worth knowing," "worth asking." In a book about measuring value, the loose
   use trains the wrong instinct.
2. **Monetary amounts and measured quantities are numerals.** `$8,000`, not
   "eight thousand dollars." Anything that could appear in an entry, a schedule,
   or a statement is a figure.
3. **A reader meets a person, never an idea.** Ideas are used, applied, faced,
   or learned.

## Lint deltas

```style-targets
tell_budget: 2
sentence_avg_lo: 19
sentence_avg_hi: 26
sentence_hard_max: 55             # warning only; past 55 the fault is two claims or a buried list
paragraph_sents_lo: 4
paragraph_sents_hi: 9
# prose_metrics.py
burstiness_cv_min: 0.32           # base 0.45 rewards long/short whiplash. Do NOT chase this by inserting short sentences
para_cv_min: 0.22
mtld_min: 70.0                    # defined terms repeat verbatim; thesaurus variation of a term of art is an error here
adverb_pct_max: 3.0
# register_report.py
latinate_ratio_max: 0.40          # discriminating: Feynman 0.364 and Buffett 0.305 pass; abstract textbook mush at 0.486 fails
nominalization_per_1000_max: 65.0 # Feynman measures 61.3 on domain nouns; a corpus lesson at 84 should still fail
hedge_per_1000_max: 56.0          # Feynman measures 55.2. Epistemic care is not apology; the base 18 flags him as evasive
booster_per_1000_max: 7.0
attitude_per_1000_max: 6.0
contraction_per_1000_min: 0.0     # deliberately disabled: an unhurried explanatory voice can run zero
# rhythm_audit.py
uniform_para_pct_max: 40.0
cadence_run_max: 4.0
```

```banned-words-add
obviously
trivially
intuitively
merely
unpack
straightforward
```

`clearly` and `simply` are deliberately absent: "clearly stated in the note" and
"simply because" are legitimate. Treat them as watch-list items, banned in the
epistemic sense and permitted in the descriptive one.

```banned-phrases-add
worth noting
worth knowing
worth remembering
worth understanding
worth considering
well worth
meet the concept
meet this concept
meet the idea
meet the term
we first meet
students should be able to
this chapter will introduce
this chapter covers
as we will see
for now, just accept
beyond the scope of this book
at its core
at a high level
the bottom line is
boils down to
you might be wondering
you may be wondering
the answer is simple
let that sink in
and that changes everything
put simply
simply put
nothing more than
```

Four constraints cannot be expressed in these blocks and belong on the review
checklist instead. `check_style.py` reads only `style-targets` and the
banned-word/phrase blocks from a profile; `tell-patterns` come exclusively from
STYLE-AI-TELLS.md, so regex additions must be proposed as edits to that file.

- **Fragments and one-sentence paragraphs: zero.** No fragment detector exists.
- **LaTeX `\textbf{}` / `\emph{}` in prose** passes lint; catch it in review.
  Markdown `**bold**` is already an `artifact-patterns` error.
- **"Meets an idea"** in inflected or distant forms.
- **No prescribed alternation.** Read `rhythm_audit.py`'s contour column:
  `sawtooth` on more than a quarter of paragraphs means someone is
  choreographing lengths.

Two CLI-only diagnostics matter more here than any threshold, because a
six-sample calibration found they were the only measures that separated teaching
prose from step-walking:

- `uv run scripts/move_annotator.py --text <file>` — **discourse-move
  diversity**. A unit showing one move at 100% is walking steps, not teaching.
  Exemplars run two to five distinct moves per passage.
- `uv run scripts/construction_variety.py --text <file>` — the **LB%**
  (left-branching) column. Near-zero left-branching means every conditional was
  flattened into a separate assertion, which is the failure this profile exists
  to prevent.
