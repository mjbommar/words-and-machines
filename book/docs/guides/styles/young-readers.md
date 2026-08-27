# Style Profile: Young Readers

Layered over [STYLE.md](../STYLE.md) — select with `style.profile:
young-readers` in `book.yaml`. For narrative nonfiction and educational
books aimed at roughly ages 9–14: a warm narrator, real curiosity,
inquiry over recitation.

Portfolio exemplar: *History of the World: A Book for Curious Kids*
(Gombrich-model narrator, inquiry pedagogy).

## Reader & register

A curious 10-to-14-year-old, read alone or aloud at home. **Kitchen
table test**: would this hold a bright kid's attention if a parent
read it across the kitchen table? A warm, trustworthy narrator who
respects the reader's intelligence and never talks down.

## Person & tense

- A narrator who addresses the reader directly and kindly ("you"),
  and steps back to third person for the story. Present for framing
  ("here is the puzzle"), past for events.
- Never "one"; never a lecturing "we must understand that."

## Rhythm

- Sentences average **12–18 words, hard ceiling 30**; Flesch-Kincaid
  grade 6–8.
- Short sentences for emphasis and turning points. Vary length — a
  wall of same-length sentences loses a young reader fastest.
- Concrete nouns and strong verbs; introduce every big word in plain
  language the first time it appears.

## Structure

- **Concrete-first is the single most important rule here**: every
  abstraction arrives through a specific person, object, place, or
  moment a child can picture.
- Inquiry architecture: open on a **compelling question**, investigate
  it, and give the reader something to decide or wonder about — not a
  moral to memorize.
- Keep "Questions We Can't Fully Answer" honest and open; kids trust
  a narrator who admits uncertainty.
- Pedagogical boxes (source-check, two-views, what-if, meanwhile) each
  do one job and stay within their word budget.

## Craft moves

- **The prime directive — neutral, objective, true.** For young
  readers this is a constitution, not a preference. The **Full Picture
  rule**: on any contested topic, give the real range of views and
  each side's strongest case. The **Framing Symmetry rule**: describe
  comparable actors in comparable terms — every civilization gets its
  achievements *and* its dark sides, and "both were true" is a
  complete, honest ending.
- **The zoom**, at least twice a chapter: drop from the panoramic
  ("across three continents…") to one child, one object, one afternoon.
- Wonder over cleverness — the narrator is delighted by the world, not
  performing for adults.
- Sensory, specific detail: what it looked, sounded, and smelled like.

## Watch for (this register's failure modes)

- Talking down: rhetorical "isn't that amazing?" and forced
  enthusiasm.
- Definition dumps — teaching a word by stopping the story cold.
- Motivational or moralizing closers ("And that's why you should
  always…").
- Vocabulary or sentence length creeping above grade level in the
  explaining passages.

## Lint deltas

Banned framing words enforce the prime directive: "primitive" and
"civilized" rank cultures; "discovered" erases the people already
there; "vanished" denies living descendants.

```style-targets
tell_budget: 2
sentence_hard_max: 30
sentence_avg_lo: 12
sentence_avg_hi: 18
paragraph_sents_lo: 2
paragraph_sents_hi: 5
# Craft diagnostics (register_report.py, rhythm_audit.py) — see ONTOLOGY.md
latinate_ratio_max: 0.30          # grade-level vocabulary is Germanic; -tion words are the drift
hedge_per_1000_max: 10.0          # say what is true; adult hedging reads as evasion to a child
nominalization_per_1000_max: 20.0 # verbs, not buried nouns ("they decided", not "the decision")
cadence_run_max: 3.0              # read-aloud prose chants when endings repeat; catch runs early
```

```banned-words-add
primitive
civilized
savage
backward
```

```banned-phrases-add
isn't that amazing
believe it or not
little did they know
and that's why you should
as you can imagine
```
