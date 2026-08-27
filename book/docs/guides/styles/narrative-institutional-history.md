# Style Profile: Narrative Institutional History

Layered over [STYLE.md](../STYLE.md) — select with `style.profile:
narrative-institutional-history` in `book.yaml`. For prose in which the history
of an institution, a rule, or a failure is told as a story, and the story is the
delivery mechanism for technical content: standards history, unit openings in a
professional curriculum, institutional biography with a teaching job.

This is a **teaching variant** of
[narrative-nonfiction](narrative-nonfiction.md), not a sibling of it. Three
instructions in the parent must be deleted rather than softened, and they are
listed first because they are the reason this profile exists.

## Where this breaks with the parent

**"Deliberate variance — follow a 30-word sentence with a 5-word one."** This
prescribes a move whose only function is to satisfy the profile's own metric.
`prose_metrics.py` gates on `burstiness_cv_min: 0.45`, and long-short alternation
is the cheapest way to manufacture that number; it produces the
fragment-for-emphasis cadence. Measured exemplars do not reach 0.45 at all: a
teaching passage on collateralized debt obligations runs cv 0.32, and expository
institutional-history prose runs about 0.13. Replace the alternation rule with
**clause-shape variance** and lower the floor to match. Variety in this register
comes from where the main clause sits, not from length whiplash.

**The "rotating benediction" coda.** A fixed gesture with rotating wording is the
definition of a template tell: rotating the words defeats the verbatim-duplicate
check in STYLE-AI-TELLS Part 5 while leaving the shape fully audible on a
read-aloud. Delete it. Rotate the *evidentiary type* of the ending instead — see
the ledger close below.

**"End technical explanations on a human consequence, not the mechanism."** In
this register that is the presentism trap. Rewrite as: end on the next
*institutional* action, dated. A human consequence is admissible when it is
documented and attached to a named person, never when it is civilizational.

Inherited unchanged: the removal test, one metaphor per concept, real examples
over hypotheticals, no balanced hedge.

## Reader and register

A working adult who wants the technique and will accept 3,000 words of history to
get it. Not a general browser being entertained, and not a student being drilled.

Two tests, both of which must pass.

**The seminar test.** Could you say this to a room of second-year students who
have the primary document open, with a specialist in the period sitting at the
back? A textbook, a museum placard, or a conference cadence fails. The specialist
is the load-bearing part of the image: this register's characteristic
embarrassment is not dullness but a claim the specialist would contradict.

**The footnote test.** Every sentence asserting causation must be one you would
be willing to footnote. If the footnote would have to read *inference*, the
sentence itself has to say so.

## Person and tense

- **"We" for the shared reading of a document, and only for that**: "the ledger
  tells us what the minister chose not to total." Third person past for the
  episode. "You" only inside exercise apparatus, never in narrative.
- **The tense boundary is the epistemic boundary**, and it does honesty work for
  free. **Past indicative** is what the record says happened. **Present** is what
  is still true of the technique — the accounting identity is present tense, the
  1781 deficit is not. Never let the present tense leak onto a historical event,
  because that is where causal overclaim hides. **Modal or conditional** marks
  reconstruction, and the sentence must also name its basis.
- **A reader meets a person, and here the verb is legitimate.** People genuinely
  are met: a minister, a branch manager, a geologist. A reader never meets double
  entry or a balance sheet. A person is met once, at first appearance, with a
  date and a place; later appearances use the bare name.

## Rhythm

- **Sentence average 21–26 words**, a deliberate six-word shift up from the
  parent's 15–20 and the most important delta in the profile. Subordination is
  where the teaching happens: the appositive that defines the term, the relative
  clause that carries the date, the concessive clause that marks the dispute.
- **No hard ceiling as an error.** `sentence_hard_max: 55` as a warning, since
  one periodic 70-word sentence per chapter is a legitimate instrument and the
  parent's 35 would flag most teaching sentences in the exemplars.
- **The floor is the real control: no sentence under 8 words outside quoted
  speech.** No lint key exists for a minimum, so this is a review-pass check —
  and it is the single rule that kills fragments, punchy closers, and the
  consulting cadence at the source.
- **Subordination target:** roughly 60% of sentences carry at least one
  subordinate or relative clause, and each paragraph contains at least one
  sentence with two levels.
- **Clause-shape variance replaces length alternation.** Three shapes, named so
  they can be counted in revision: **loose** (main clause first, subordination
  trailing), **periodic** (subordination first, main clause landing last), and
  **braided** (main clause interrupted by an appositive carrying the definition).
  Rough mix 50/30/20, never more than three consecutive sentences of one shape.
  This produces audible variety at a flat length, which is the point.
- **Paragraphs 4–9 sentences, 90–200 words.** The floor of 4 does taste work
  mechanically: the one-sentence paragraph is the natural habitat of the
  aphoristic closer, so forbid the habitat rather than policing the tenant.
- **Chapters 3,500–5,000 words**, longer than the parent's 2,500–3,500 because a
  worked computation has to fit. One figure or worked box per 1,200–1,800 words,
  sparser than the parent, since here the prose does the teaching and a box
  repeating the prose is padding.
- **Punctuation:** inherit the parent's hierarchy. Semicolons rank higher in
  practice here, because coordinate clauses of equal weight are how a two-sided
  dispute gets stated without a hedge.
- **No bold, no italic emphasis.** A technical term is introduced by syntax.
  Italics keep two jobs: titles of works, and a period or foreign term at first
  use.
- **Numbers.** All monetary amounts and measured quantities in numerals,
  overriding the base spell-out rule. Name the period currency, and give a modern
  equivalent at most once per chapter with the conversion basis and its date
  stated. Context means the period baseline — a sum against a laborer's daily
  wage — not a modern-city analogy. A bare modern equivalent with no stated basis
  is an error, not a preference.
- **"Worth" only for literal financial value.** "The estate was worth 40,000
  livres" is correct; "worth remembering" is out.

## Structural shape

**Opening — the document on the table.** 400–900 words, shorter than the
parent's 1,000–1,500, because the technical thread must begin by word 900. Open
on a specific artifact with a date and a physical description, not on a person
having a feeling. A dated object can be checked; an inferred mood cannot, and an
opening that cannot be checked mortgages the chapter's authority to buy 200 words
of atmosphere.

**Threading — one technical operation per episode, introduced at the moment the
actor needed it.** The operation arrives in the actor's vocabulary first and the
modern equivalent second, in the same sentence, so the concept and its history
are taught in one pass and "what we would now call" never appears twice. Target
roughly 60% narrative to 40% mechanism by word count, in three to five
alternations. Never one block of theory: the parent's removal test applies, and
the additional test here is that the reader could *perform* the operation at the
end of the chapter, not merely name it.

**Middle — the counter-ledger.** One paragraph, exactly one per chapter,
non-optional, giving the strongest version of the case against your own causal
reading, with a named scholar and the date of their work, placed *before* you
finish the argument. It is not a hedge; it is the price of the claim you want to
make, and it is what lets you make that claim in the indicative.

**Close — the ledger close, no moral.** Rotate among three kinds of factual
ending, rotating the *kind* rather than the wording:

1. **The next entry** — what the institution did next with the technique, dated.
2. **The open ledger** — what the record does not say, named precisely as a gap,
   with what would settle it.
3. **The practitioner's last word** — a verbatim quotation from someone who did
   the work, cited, with nothing after it. A quoted voice is evidence;
   commentary on a quoted voice is not.

Test the close by reading the final paragraph aloud to an imagined room of
specialists. A wince means a moral got in.

## Craft moves

- **The document on the table.** *Why it works:* it front-loads the checkable, so
  the reader extends credit to everything downstream.
- **The actor's own vocabulary first.** Period term, then modern equivalent,
  inside one sentence. *Why it works:* the anachronism problem and the definition
  problem are solved by the same clause, and the reader learns the concept has a
  history rather than a nature.
- **Teach through someone who is also learning.** *Why it works:* the reader's
  confusion is legitimized by a character's confusion, so the mechanism enters as
  narrative information rather than as an interruption.
- **Let the practitioner finish the paragraph.** Hand the last sentence of a
  technical explanation to a quoted expert and do not gloss it. *Why it works:*
  the claim closes on evidence, and authority becomes cumulative rather than
  asserted.
- **Follow the money to the office.** Trace the mechanism to the specific bureau,
  clerk, headcount, or line item that held the power. *Why it works:*
  institutional weight is built from named offices and counted staff, and every
  adjective you would have used instead is on the banned list.
- **One arithmetic per chapter, worked.** At least one real computation with real
  period figures. *Why it works:* it is the difference between a reader who can
  discuss the concept and one who has it, and it is this register's entire
  justification for spending narrative on technical content.

## The honesty problem

This is the register most prone to overclaiming causation and inflating one
figure's importance, and the failure is well documented in review literature —
one widely read history of double-entry bookkeeping was met with "this delightful
book is based on a false premise" and the flat judgment that "the importance of
Pacioli in the development of double entry bookkeeping is exaggerated." Books
arguing the opposite thesis draw the mirror charge. Nobody is exempt, so the
rules have to be mechanical.

**Three claim tiers, each with its own grammar.**

*Documented.* Simple past indicative, source anchored in the sentence or its
footnote. Adopt the strict rule as house law: anything inside quotation marks
comes from a letter, memoir, or other written document. No exceptions, including
for smoothed paraphrase that would read better in quotes.

*Reconstructed.* The inference and its basis both appear in the main clause:
"the ledger shows the wool posted on 14 March, which means the clerk closed the
account the same day." Front matter carries a reconstruction disclosure. **Hard
limit: no interior state is ever reconstructed.** Actions implied by the record,
yes; feelings, motives, and thoughts, never. "Must have felt," "surely knew," and
free indirect discourse into a historical figure's head are banned outright,
because they are the route by which missing evidence becomes narrative.

*Disputed.* Name at least two scholars in the sentence, with the dates of their
work, then say which way you read it and why. The disagreement must be *live*,
with the current state of play given; presenting a settled demolition where an
argument is ongoing is its own species of overclaim.

**Five causation rules.**

1. **The priority check.** Before writing that anyone originated a technique,
   state the earliest surviving instance you found, with its date. If it predates
   your figure, the figure is a transmitter and the sentence must say which.
2. **Write the counterfactual down.** If you claim the decision caused the
   outcome, write the counterfactual sentence explicitly, look at it, then either
   support it or downgrade the verb. Claim the vocabulary, the availability, or
   the precedent; claim the cause only when you can name the mechanism.
3. **The verb ladder, one rung.** caused > precipitated > enabled > contributed
   to > coincided with > preceded. Use a verb at most one rung above the verb
   your best cited source uses, and put the source's own verb in the notes. This
   converts a taste judgment into a diffable record.
4. **The single-figure cap.** No individual is ever credited with a system. A
   named person may be credited with a document, an office, a decision, or a
   number.
5. **Superlatives take "surviving" or "known."** "First," "earliest," and "only"
   are permitted only with that qualifier unless an exhaustive search can be
   demonstrated. "The earliest surviving" is almost always the true sentence and
   costs one word.

**The hostile-review file.** For every chapter, write the one-sentence review a
specialist would publish, in their voice, and keep it in the chapter's notes. If
the chapter cannot answer that sentence, the claim comes out — not the sentence.

## Watch for

- **Single-figure inflation.** One named person absorbs credit for a diffuse,
  incremental system, because narrative wants a protagonist and diffusion has
  none.
- **The origin-story pull.** Narrative wants one beginning; institutions have
  several. Diagnostic symptom: the chapter has a birthplace.
- **Presentism as payoff.** Cashing an episode out as a lesson for today. This is
  the register's most seductive ending and its most expensive.
- **Cherry-picked confirmation across chapters.** Cure: one chapter per book is a
  counterexample chapter, chosen because the thesis is weakest there, and the
  thesis comes out the other side intact or amended in public.
- **The dramatized interior.**
- **Decorative technical content.** The reader can name the concept and cannot
  perform it. Test: write the exercise. If you cannot, the chapter did not teach.
- **Anachronistic vocabulary.** Calling a fourteenth-century entry an "asset"
  imports a modern conceptual scheme under cover of translation.
- **The dated museum placard**, where a real date props up an unreal adjective
  cluster.
- **Primary-quote inflation.** State an irresistible period quotation once, in
  its home chapter; reference it thereafter.

## Lint deltas

```style-targets
tell_budget: 2                     # this register earns authority on restraint
sentence_avg_lo: 21                # up 6 from the parent: subordination is where the teaching happens
sentence_avg_hi: 26
sentence_hard_max: 55              # warning only; one periodic 70-worder per chapter is an instrument
paragraph_sents_lo: 4              # the one-sentence paragraph is where aphoristic closers live
paragraph_sents_hi: 9
# prose_metrics.py
burstiness_cv_min: 0.28            # 0.45 rewards long-short whiplash; measured exemplars run 0.13-0.32
para_cv_min: 0.30
adverb_pct_max: 2.5
# rhythm_audit.py
cadence_share_max: 0.42            # looser than the parent's 0.38, since terminal technical nouns cluster by necessity
cadence_run_max: 3.0
uniform_para_pct_max: 20.0
# register_report.py
hedge_per_1000_max: 20.0           # RAISED: "no ledger survives" is the honesty apparatus, not evasion
booster_per_1000_max: 6.0          # TIGHTENED: over-boosting is this register's named failure, and this is its lint form
attitude_per_1000_max: 7.0
nominalization_per_1000_max: 42.0
latinate_ratio_max: 0.52
contraction_per_1000_min: 1.5      # a floor against dissertation drift
# arc_profiler.py
valence_range_min: 0.26
tension_range_min: 0.18            # RAISED: a failure episode must actually tighten
arc_correlation_min: 0.30
```

```banned-words-add
inevitable
inevitably
singlehandedly
visionary
watershed
linchpin
harbinger
birthplace
```

```banned-phrases-add
the father of modern
invented modern
gave birth to
ushered in
paved the way for
laid the foundations for
laid the groundwork for
sowed the seeds
changed the course of
would come to define
the rest is history
little did he know
must have felt
must have thought
must have known
surely knew
we can only imagine
it is easy to imagine
history teaches us
as history shows
well worth
worth remembering
worth asking
```

Note that the epithet bans will also fire when you quote an epithet in order to
demolish it, which is a legitimate and common move here. `check_style.py` has no
quote exemption, so expect one or two justified suppressions per book and log
them.

CLI-only tools the YAML block cannot reach:

- `uv run scripts/construction_variety.py --max-run 2 --min-odi 0.28` — dated
  openings converge fast, so opener monotony bites harder than in the parent.
- `uv run scripts/setup_payoff.py --kind term --status unpaid --strict` — **the
  register's most important gate, and the parent does not name it.** Every period
  term introduced in narrative is a promise; a term used once and never again was
  decoration. Run it per chapter, not per book.
