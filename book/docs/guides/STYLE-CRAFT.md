# STYLE-CRAFT — Positive Craft

[STYLE.md](STYLE.md) is the mechanics; [STYLE-AI-TELLS.md](STYLE-AI-TELLS.md) is what to
cut. This guide is what to *build*: the techniques that make prose worth reading.
Engagement is not optional polish — an unread book teaches, warns, and persuades no one.
It comes from stakes, concrete detail, a real voice, and momentum. Never from more words.

---

## 1. Burstiness: rhythm as craft

Alternate sentence lengths and shapes deliberately. A short sentence lands hardest
**after** a longer one that builds to it — development creates tension; the short
sentence releases it.

**Flat (every sentence 6–8 words, subject-verb-object):**
> The project requires a conditional use permit. The planning board reviews the application. The public hearing allows community input. The board makes a final decision.

**Bursty:**
> The project needs a conditional use permit. That means a public hearing — your chance to speak. The planning board reviews the application, hears from residents, and votes. Sometimes the same night. Sometimes after months of delay.

Short. Medium with a dash. Long with a list. Fragment. Fragment. That's the shape of a
human paragraph.

**Earn your short sentences.** The failure mode of "short sentences punch" is staccato —
choppy, list-like prose that hammers instead of lands:

> *Staccato:* The water was dirty. It had germs. They make you sick. You could die.
> *Flowing:* The water looks clean, but clear water can still carry germs that will put a child flat in a day. You can't see them. You boil anyway.

Measure it rather than guess: `construction_variety.py` reports opener
classes, length bands, clause architectures, and consecutive-repeat runs per
chapter; `rhythm_audit.py` reports how sentences *land* (cadence runs,
paragraphs stuck in one length band). Both name alternatives to reach for —
the full inventories live in the `syntactic_constructions` and
`sound_and_rhythm` ontology branches; browse with
`uv run scripts/writing_ontology.py find "periodic"` (see ONTOLOGY.md).

---

## 2. Concrete detail over abstraction

**The exposed particular:** one hyper-specific detail stands for a larger truth. Not "he
was wealthy" but "the marble in his foyer came from the quarry Michelangelo used."

**Sensory detail makes infrastructure visible:** the 70 dB roar of fans; the yellow
utility flags in a cornfield; the blast of heat in a hot aisle. If the subject is
abstract, find the room, the sound, the object.

**Scale contrasts:** juxtapose the intimate and the vast, and let the gap speak. Four
nodes → five billion users. A napkin sketch → exabytes daily. Don't explain the gap to
death — the juxtaposition does the work.

**Numbers become images:** "1.4 gigawatts — enough to power 800,000 homes." Every scale
claim gets a comparison a reader can see.

---

## 3. Scene vs. summary

A **summary** tells the reader what happened. A **scene** puts them somewhere specific at
a specific moment and lets it happen. Books need both; AI defaults to all-summary.

- Summary: "In 1973, Mead Corporation launched the first commercial legal database."
- Scene: "On the night before the demo, a programmer tried one more thing: instead of
  matching whole words, he told the machine to look for roots. He ran the query at 2 a.m.
  The terminal printed three cases. All relevant."

Use scenes for turning points, human stakes, and chapter openings. Use summary to move
time and compress the connective tissue. A vignette needs: third person, past tense, a
named person, and one concrete sensory moment. Specific, never melodramatic — drama comes
from the facts, not the adjectives. *"A person can bleed to death in five minutes. Move
fast."*

---

## 4. The Tracy Kidder model

*The Soul of a New Machine* is the house model for technical narrative.¹

1. **People first.** Don't just explain a technology; show a person struggling with it or
   a community debating it. The technology story IS the people story.
2. **The camera.** Move between long shots (global trends) and close-ups (the vibration
   of a server floor; a technician connecting a cooling hose). Micro to macro and back.
3. **The clock.** Keep time pressure visible. "They had six weeks. They were three weeks
   behind."
4. **Don't gloss the tedium.** Mistakes, false starts, and chaos make the eventual
   success believable — and human.
5. **Subtle author presence.** The author may step in, but rarely and lightly.
6. **The machine comes alive.** When the thing finally works, give the reader the moment
   of awe mixed with exhaustion.

---

## 5. Mentor-author moves

Pick 3–6 mentor authors for the book and steal their *moves*, not their sentences.
Absorb, don't imitate. The generic catalog (adapt names to your book's genre):

| Move | Model | What it does |
|---|---|---|
| **The cosmic zoom** | Harari, *Sapiens* | Zoom to geological time, snap back with a provocative claim; make the familiar strange |
| **The weight of power** | Caro, *The Power Broker* | Physical detail of rooms and silences; accumulate evidence until inevitability lands; then the human cost |
| **The engineering sprint** | Kidder | Constraint → cast → grind → breakthrough; the 3 a.m. moment |
| **The myth inversion** | Graeber, *Debt* | State the conventional wisdom, check the record, propose the opposite, reveal the stakes of the myth |
| **The deep comparison** | Fukuyama | Two societies/systems side by side; the puzzle of why they diverged; path dependence |
| **Structure as meaning** | McPhee | The shape of the piece IS the argument; end where you started, transformed |
| **The dual timeline** | Larson | Past event + present understanding; dramatic irony; chapter endings that force the page-turn |
| **Personal obsession** | Stoll, *The Cuckoo's Egg* | A 75-cent anomaly unravels everything; real-time confusion as narrative engine |

**Before/after (the mentor-rewrite exercise²):** take a flat sentence from the draft and
rewrite it in a mentor's register. Do this in review, not just drafting.

- Flat: *"The vertical filing cabinet was invented in the 1890s and quickly adopted by law firms."*
- Kidder/Caro-ized: *"In 1893, between the Ferris wheel and the electric lights at the
  Chicago World's Fair, Melvil Dewey showed off a wooden cabinet with a peculiar feature:
  the drawers were deep, not wide. You stood papers on edge. It sounds trivial. It was
  revolutionary — the senior partner's memory had been the index, and his death a
  catastrophe. Dewey's tabs and manila folders broke the monopoly on institutional memory."*

**The iceberg principle:** know 10× more than you write. Expertise shows through
specificity, confidence, and what you choose *not* to explain.

---

## 6. Tension is the engine of explanation

The risk in explanatory prose is textbook drift — informing without pulling forward. The
fix: give the reader a question to chase ("why does this work, and where does it break?")
and thread the answer instead of dumping it.

- Static: *Charcoal adsorbs impurities. It has a large surface area. This makes it useful.*
- Dynamic: *Charcoal is mostly surface — a single gram has the area of a tennis court,
  riddled with pores. Dissolved gunk sticks in those pores as water passes. That's also
  the catch: pores fill up, and a spent filter quietly stops working while still looking fine.*

Interleave stakes with mechanism. Convert lists to narrative where you can. For technical
explanation, the three-beat: **analogy first → direct explanation → why it matters to
this reader.** One analogy per concept; then commit to the technical term.

Every explanatory section still owes the reader a "so what?" — if a paragraph explains
without connecting to the reader's situation or the book's question, it hasn't earned its
place.

---

## 7. The read-aloud test family

All variants of one move: define the reader precisely, then perform the paragraph for them.

- **The coffee test** (narrative/pop-science): could you say this aloud to a curious,
  intelligent friend over coffee without feeling ridiculous? They're interested, not
  polite; they'll interrupt if you're boring.
- **The kitchen-table test** (pop math/science): the friend hasn't done math in twenty
  years. Every equation needs a sentence saying what it *means*; every concept needs to
  survive being spoken across a kitchen table.
- **The neighbor test** (practical guides): the reader is angry, time-pressed, and has a
  hearing in two weeks. Stricter than the coffee test — they need answers, not charm.
  Don't talk down, don't waste time, don't tell them to calm down.

Failure modes are the same in all three: press release, academic paper, TED talk, vendor
pitch, government brochure → rewrite.

---

## 8. Chapter openers and closers

### Openers (the hook)
Open with a concrete situation — a real place, real number, real consequence — that
raises the question the chapter answers. Never a definition, never background, never
"In this chapter."

> Weak: *Water is one of the most important resources to consider when evaluating a data center project.*
> Strong: *Chandler, Arizona gets 8 inches of rain a year. It also hosts 22 data centers. In 2024, data centers used 30% of the city's non-residential water. Residents found out when the city proposed a rate increase.*

Vary hook *types* across adjacent chapters (scene, statistic, question, quote, artifact) —
an identical opening formula chapter after chapter reads as a template. The named hook
and closer types are catalogued in the `openings_and_closings` ontology branch
(`uv run scripts/writing_ontology.py show openings_and_closings`) — useful when the
inventory table in REVIEW-QA §5 shows two adjacent chapters opening the same way and you
need a third option that isn't the two you already used.

### Closers
- End on the last piece of concrete information, a forward question, or a controlled
  recurring gesture — never a motivational closer, never a summary.
- If the book has a **coda convention** (a recurring closing move defined in SPIRIT.md),
  vary its wording between adjacent chapters. Benediction, not boilerplate.
- Transitions to the next chapter: brief (a few sentences), pose the question the next
  chapter answers.

---

## 9. Emotional calibration

Calibrate between the failure modes, per the book's SPIRIT doc. The generic pattern —
find the two wrong registers, then write the third:

| Dimension | Too much | Too little | Calibrated |
|---|---|---|---|
| Urgency | panic | complacency | "The deadline is 30–60 days out. That's enough if you start now." |
| Anger | polemic | dismissal | validate it, then channel it into the mechanism |
| Confidence | hype | hedging mush | claim what the evidence supports; name the one real uncertainty |
| Empowerment | patronizing | deflating | honest about limits, specific about leverage |

**Uncertainty without false balance:** state what's known including the range, name the
source of the uncertainty, then ask who bears the downside risk if the optimistic case is
wrong — and what the reader should demand in writing.

**Domain register:** some books should adopt their community's own ethical voice rather
than a corporate one — e.g., a security book states disclosure ethics as a community norm
("if you find this in the wild, report it — the developer probably doesn't know it's
there"), not as terms-of-service boilerplate.³ Find the community's honest register and
write in it.

---

## 10. Manuscript-level craft

Problems visible only across the whole book:

- **One home per fact.** Every fact, example, and statistic has one home chapter where it
  appears in full with citation; elsewhere, a one-sentence callback or cross-reference.
- **Cause before effect; number before verdict.** Give the evidence, then the conclusion.
  Introduce the problem before the tool that solves it.
- **Scope matches evidence.** No verb or qualifier broader than what's actually true.
  Preprints labeled; ongoing cases "ongoing"; approximations "about."
- **Don't conflate.** If a sentence links A to B, make sure A causes B — not that they
  merely coexist.
- **Terminology stable.** One term per concept, book-wide.
- **Numbers agree everywhere** (see REVIEW-QA.md canonical-figures file).

---

## 11. Humanization moves — what human prose has that models lack

Detection (STYLE-AI-TELLS) removes machine fingerprints; these moves add the
human ones. Each is grounded in the stylometry literature comparing human and
LLM prose (Reinhart et al., PNAS 2025, "Do LLMs write like humans?": LLMs use
present-participial clauses at ~5x the human rate, more nominalizations,
fewer human subjects, fewer epistemic stance markers; corroborated by the
L2-writing metadiscourse studies). `make metrics` and `make slop` measure the
negative side; this section is what to write instead.

`register_report.py` puts numbers on most of this dimension — hedge, booster
and attitude-marker rates, Latinate share, buried-verb (nominalization) rate,
contractions — per chapter against the genre profile's targets. The named
alternatives (stance markers, register layers, connotation axes) live in the
`diction_and_register` branch; `move_annotator.py` does the same job one level
up, labeling what each paragraph is *doing*.

**Put people in subject position.** LLM prose favors abstractions as
grammatical subjects ("The implementation of the policy resulted in...");
humans put agents there ("The county board gutted the policy"). In revision,
scan paragraph subjects: if three in a row are abstractions, recast one with
the person or institution that acted.

**Take a stance — hedges with an owner.** Models hedge with mush ("may
potentially suggest"); humans hedge with stance: *I doubt it. Probably.
Nobody has checked. The figure looks too clean.* Attitude markers
(*oddly, to my surprise, frankly, worse*) are among the strongest human
signals precisely because models under-produce them. One per section is
seasoning; don't shake the jar.

**Spend sentiment honestly.** LLM text runs relentlessly positive-to-neutral.
Human nonfiction gets irritated, bored, delighted, and disappointed in
proportion to the material. If nothing in a chapter annoyed you, the reader
won't believe you were there.

**Raise specificity density, not adjective density.** The human signature is
checkable particulars — names, dates, dollar figures, places — not vivid
modifiers. When a paragraph feels vague, the fix is a proper noun or a
number, not "notably". (`prose_metrics.py` reports `spec` — digits + named
entities per 100 words — so you can see a chapter's particularity flatten.)

**Convert participial trailers into finite verbs.** The single most
over-produced LLM structure is the present-participial clause ("...,
signaling a shift in the industry"). Rewrite as a sentence with a subject
and a finite verb, and make it prove its claim ("Industry filings shifted
within a year: ...") — or delete it.

**One asymmetry per chapter.** Human structure is lopsided: a digression the
author couldn't resist, a section that's twice as long because the material
deserved it, an aside in parentheses that talks to the reader. Templates are
machine; asymmetries are signatures. Plant one deliberately and prune the
rest.

---

## 12. The humanization pass — twelve operations, in order

Section 11 says what human prose has. This is how to put it into a
paragraph that lacks it. Apply in this order: the cuts first (they reveal
what the paragraph actually contains), then evidence, then sentence
architecture, then the additions. Adding before cutting decorates an
assembled paragraph instead of rewriting it.

1. **Delete the first sentence.** If the paragraph still stands, leave it
   deleted. Otherwise promote its most concrete sentence to the front.
   *Check:* the first seven words contain a name, numeral, date, or object.
2. **Delete the last sentence.** If the new last sentence states a
   conclusion, implication, or trade-off, delete that too. Keep going until
   the paragraph ends on a checkable fact. *Check:* the last sentence could
   be verified against a source.
3. **Cut 25% without losing a fact.** Delete inferable definitions,
   transitional lubricant, and any sentence restating an earlier one.
   *Check:* word count down a quarter; count of proper nouns, numerals, and
   dates unchanged. If you can't reach 25%, the paragraph was written to
   length and needs another fact, not a trim.
4. **Repair every number.** Source's exact figure, not the round one; one
   number per sentence; say where a figure is soft or sources disagree.
   *Check:* every numeral appears in the cited source in that form.
5. **Name the record once.** Add a clause saying how this is known — the
   filing, the log, the transcript, or the absence of one.
6. **Move the news to the end of the sentence.** In the two longest
   sentences, put the load-bearing word, name, or number in the last three
   words; shift dates and attributions to the front. *Check:* read the last
   three words of each sentence alone — they should be the memorable part,
   not "in the industry" or "at the time."
7. **Convert one hedge into a retraction.** Split the self-qualifying
   sentence in two and let the second take something back rather than
   soften. *Check:* no sentence opens with "While" or "Although"; one
   sentence contradicts the one before it.
8. **Break one parallel.** Where three items share a shape, rewrite one out
   of shape. Where three consecutive sentences are within five words of each
   other, make one under seven words and one over thirty.
9. **Undo one elegant variation.** Give each entity exactly one name and
   accept the repetition.
10. **Restore one detail that serves no argument** — from the research
    record, never invented. Place it in the middle third, connected to
    nothing. *Check:* it traces to a source, and deleting it costs no
    information. If the record has none, skip this step.
11. **Pick a temperature and commit once.** Irritation: offending party in
    subject position, plain verb, under fifteen words. Excitement: one
    sentence past thirty-five words, stacked appositives. Boredom: state
    the dull fact flat and refuse to elaborate. One per paragraph, licensed
    by a fact rather than an adjective.
12. **Move the paragraph break by one sentence** so the paragraph doesn't
    end exactly where its thought does.

Two cautions from the measurement work (VOICE-MODELS.md §1b): rhetorical
schemas — tricolon, anaphora, direct address — are *structured redundancy*
and read as more machine-like, not less, so budget them; and steps 10–11
are where a rewriting model will fabricate, which is why the fact-guards in
`deslop.py` exist.

## Quick reference

| Element | Guideline |
|---|---|
| Opening | Real place, real number, stakes within 2 sentences; vary hook types |
| Explanation | Analogy → mechanism → why it matters; a question to chase |
| Scenes | Named person, sensory moment, the clock running |
| Rhythm | Short after long; no staccato; fragments earned |
| Detail | Exposed particulars; scale comparisons; show, don't label |
| Emotion | Between the two failure registers; drama from facts |
| Closing | Last concrete thing, forward question, or varied coda — then stop |
| Book-level | One home per fact; cause before effect; scope = evidence |
| Humanizing | People as subjects; hedges with an owner; honest sentiment; particulars over adjectives; finite verbs over participial trailers; one asymmetry per chapter |

---

¹ Kidder model detailed in datacenter-2026-book STYLE-CRAFT and history-through-rfc-book
STYLE-AI-TELLS Part 6 (with the full comparable-authors shelf).
² Mentor-author technique + before/after pairs adapted from legal-tech-history-book
`prose_craft_guide.md` (Harari/Caro/Kidder/Graeber/Fukuyama).
³ Community-ethic voice from hacking-with-ai-book STYLE-CRAFT Part 6. Read-aloud test
variants: datacenter (coffee), complexity-book (kitchen table), htsd-book (neighbor).
