# Style Profile: Narrative Nonfiction

Layered over [STYLE.md](../STYLE.md) — select with `style.profile:
narrative-nonfiction` in `book.yaml`. For books that tell true stories
with scenes, people, and an argument carried by narrative: reportage,
pop-science, sweep history, thesis-driven institutional history.

Portfolio exemplars: *This Is Server Country* (reportage), *Rough
Consensus* (protocol history), *From Clay to Code* (sweep history),
*The Math Inside the Machine* (pop-science), *The Commons Captured*
(argument-driven history).

## Reader & register

Curious general reader, no domain background assumed. **Coffee test**:
explain it to a smart friend over coffee — if it sounds like a
textbook, a press release, a vendor pitch, or a TED talk, rewrite it.
The sharpest sub-test is the **vendor test**: could this sentence
appear in a press release? If yes, delete it.

## Person & tense

- **"We" for shared discovery** ("to see why the township won, we need
  to follow the power lines"); third person for narrative scenes;
  "you" rare and deliberate; never "one."
- Present tense for mechanisms and current state; past for events;
  future/conditional for projections. The tense shift itself carries
  meaning — don't drift within a paragraph.

## Rhythm

- Sentences average **15–20 words, hard ceiling 35**; deliberate
  variance — follow a 30-word sentence with a 5-word one.
- Paragraphs 3–7 sentences, **Point → Evidence → Analysis**.
- **Punctuation preference hierarchy**: reach for commas, then colons,
  then semicolons, then a new sentence, then em dashes (max 1 per
  paragraph — the classic AI tell), then parentheses (rare).
- Every number gets context ("1.4 gigawatts — enough to power a city
  of 800,000"); round for readability; cite everything.

## Structure

- Chapters are **A–B–A′ (+ coda)**: novelistic opening scene
  (1,000–1,500 words; real date, place, person, action, stakes) →
  mechanism/analysis → return to the opening thread transformed → a
  short "and yet" coda. The coda is a **rotating benediction** — same
  move ("and still, it runs"), different words every chapter; identical
  wording reads as boilerplate.
- End technical explanations on a human consequence, not the mechanism
  ("because the card had 80 columns, the welfare state became possible").
- Chapter lengths 2,500–3,500 words read best in this register;
  one figure or visual per 700–1,200 words.
- Transitions by echo, time, or contrast — never "In this chapter."

## Craft moves

- **Concrete first, concept second** — every abstraction arrives
  through a specific person, object, place, or moment.
- The removal test: delete the theory paragraph; if the argument
  doesn't change, it was inserted, not integrated.
- Explaining complexity: **analogy → direct explanation → implication**,
  in that order.
- Mentor authors, for feel not formula. The portfolio's working set,
  each reduced to one move: **Kidder** (people first, micro→macro,
  prose-as-camera), **Harari** (cosmic zoom then ground), **Caro**
  (follow the power, institutional weight), **Graeber** (invert the
  assumption), **Fukuyama** (the long comparison). Name your book's own
  in `docs/SPIRIT.md` and steal one move at a time, never a whole voice.
- **One metaphor per concept — then commit.** A concept that picks up a
  second and third metaphor across chapters reads as indecision.
- Emotional threads: two or three, defined in SPIRIT.md; every
  paragraph touches at least one.
- Attribution grammar: mark documented vs. reconstructed vs. disputed
  claims differently in prose; composite characters and reconstructed
  dialogue get a front-matter disclosure.

## Watch for (this register's failure modes)

- The balanced hedge — "some argue X, others Y" with no position.
  Make claims; carry the argument.
- Theory inserted rather than integrated (see removal test).
- Cross-chapter repetition of signature phrases and reused quotes —
  keep a repetition ledger during revision rounds.
- Decapitated hooks: an opening scene whose thread never returns.
- The both-and rhetorical template ("not X but Y") — at most once
  per few chapters.

## Lint deltas

```style-targets
tell_budget: 3
sentence_hard_max: 35
sentence_avg_lo: 15
sentence_avg_hi: 20
paragraph_sents_lo: 3
paragraph_sents_hi: 7
# Craft diagnostics (rhythm_audit.py, register_report.py, arc_profiler.py) — see ONTOLOGY.md
cadence_share_max: 0.38           # narrative lives on varied sentence endings; the house 0.45 is slack here
cadence_run_max: 3.0              # three identical landings in a row is audible in a read-aloud
uniform_para_pct_max: 20.0        # same-length paragraphs are the genre's template tell
hedge_per_1000_max: 14.0          # the balanced hedge is this register's named failure mode
valence_range_min: 0.30           # a chapter with no emotional movement has no arc
arc_correlation_min: 0.35         # chapters are outlined to a named arc shape, so hold them to it
```

Opener monotony matters more here than the defaults assume, but
`construction_variety.py` takes its thresholds only from the command line —
run it as `uv run scripts/construction_variety.py --max-run 2 --min-odi 0.25`
for this register (adjacent chapters opening the same way is a REVIEW-QA §5
finding, not a lint error).

```banned-phrases-add
some argue that
others contend
it remains to be seen whether
only time will tell
```
