# Style Profile: Practical Guide

Layered over [STYLE.md](../STYLE.md) — select with `style.profile:
practical-guide` in `book.yaml`. For books whose readers must **act**:
civic handbooks, how-to guides, field manuals, business advisories.
Usefulness beats beauty; the reader arrives already motivated (or
already frightened) and needs equipment, not a pep talk.

Portfolio exemplars: *How to Fight a Data Center* (civic handbook),
*The Offline Manual* (survival manual), *Building AI-Native
Professional Services Firms* (business advisory).

## Reader & register

A specific person with a problem and a deadline. **Neighbor test**:
a knowledgeable friend explaining across the fence — if it sounds
like a press release, an academic paper, a TED talk, an **activist
pamphlet**, or a government brochure, rewrite it. The calm expert:
never breathless, never scolding.

## Person & tense

- **"You" is the default**; imperatives for actions ("Request the
  application. Read the water section first."); "we" for shared
  walkthroughs; third person for examples. Never "One must consider,"
  "Citizens should be aware," or "Folks."
- Present tense throughout except narrated examples (past).

## Rhythm

- Sentences average **12–18 words, hard ceiling 30**. If you hit 30,
  split it.
- Paragraphs 2–5 sentences, **Point → Evidence → Implication**.
- Reading level: Flesch-Kincaid grade 7–9 for general-public guides
  (professional advisories may run higher — declare it in SPIRIT.md).

## Structure

- Chapters cold-open on a real situation (a real community, a real
  outcome), then hold roughly a **60/40 explain/equip ratio**.
- Close with a takeaway box: 3–5 action items, each bold-led, timed,
  and standalone.
- **Callout-box governance**: a box does exactly one of three jobs —
  warn, clear up a confusion, or say what to do right now. 3–5
  sentences, 80 words max, at most 3 per chapter plus the takeaway,
  never two in a row. If it fails the box test, it's body prose.

## Craft moves

- **The "So what?" test**: every action item names who to contact,
  what to ask for, and where to find it.
- Name your assumptions; when help matters, give both worlds —
  calling for help is never the only answer, self-rescue is never
  the only answer.
- **The downside-risk framework** for uncertainty: don't cherry-pick
  and don't false-balance. Ask who bears the downside if the optimistic
  case is wrong, and say so plainly.
- **Emotional calibration by triplet.** For each register, name the two
  failure modes and the target between them, then aim for the middle:
  urgency without panic, anger without polemic, honesty without doom,
  confidence without cheerleading, empathy without pity. The reader's
  motivation is the problem next door — the Erin Brockovich register:
  "Nobody's coming to save you. Here's what you can do." Don't amplify;
  equip.
- Examples are real, with real outcomes and dates — invented
  hypotheticals read as padding here.

## Watch for (this register's failure modes)

- Motivational closers and pep-talk padding (see banned phrases).
- Disclaimer sludge — one clear scope note beats hedging every page.
- Box inflation: boxes doing body-prose work, or three boxes saying
  one thing.
- Audience-coding: phrasing that reads as partisan to part of your
  readership; audit for it in review rounds.

## Lint deltas

```style-targets
tell_budget: 2
sentence_hard_max: 30
sentence_avg_lo: 12
sentence_avg_hi: 18
paragraph_sents_lo: 2
paragraph_sents_hi: 5
# Craft diagnostics (register_report.py, rhythm_audit.py) — see ONTOLOGY.md
booster_per_1000_max: 14.0        # "you have the right to" is the product; certainty is what equips the reader
attitude_per_1000_max: 14.0       # the Brockovich register runs on stated stance, not neutral exposition
hedge_per_1000_max: 12.0          # tighter than house: disclaimer sludge is this register's named failure mode
contraction_per_1000_min: 3.0     # it must sound spoken; zero contractions means the brochure voice crept in
cadence_run_max: 5.0              # imperative sentences land alike by nature; don't chase that number
```

Imperatives and second person are *expected*: `move_annotator.py` will
show `directive` as a dominant move here, and a long directive run is the
form working, not monotony.

```banned-words-add
folks
empower
toolkit
roadmap
actionable
```

```banned-phrases-add
now you're ready to
knowledge is power
make your voice heard
empower yourself
the good news is
you've got this
take a deep breath
```
