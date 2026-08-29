# STYLE — Voice and Mechanics

The house style for any book built from this template. This file is both a guide for
humans/agents and a **lint source**: `scripts/check_style.py` parses the fenced
` ```banned-words ` and ` ```banned-phrases ` blocks below, so edits to those blocks
change what the linter enforces. Companions: [STYLE-AI-TELLS.md](STYLE-AI-TELLS.md)
(what not to write), [STYLE-CRAFT.md](STYLE-CRAFT.md) (positive craft).

For *Instruction Sets, Programs, and Proofs*, [VOICE.md](VOICE.md), [CRAFT.md](CRAFT.md), and
[PLAIN-ENGLISH.md](PLAIN-ENGLISH.md) are the book-specific authority. This file
continues to govern mechanics and the machine-readable lint lists.

Plain language need not produce flat language. In this book, wonder comes
from the reach of an exact result. Show the object, establish the claim, and
then allow one brief sentence of wider consequence. See VOICE.md section 7;
never use elevated language to replace evidence.

---

## 1. The core principle: the read-aloud test

Every book defines a reader and a register, then tests every paragraph against it aloud.
Pick the variant that fits the book (full definitions in STYLE-CRAFT.md §7):

| Test | Reader | Books it fits |
|---|---|---|
| **Coffee test** | Curious, intelligent friend, not technical | Narrative nonfiction, pop science |
| **Kitchen-table test** | Friend who hasn't done math in 20 years | Pop math/science with equations |
| **Neighbor test** | Angry, time-pressed person who needs to act by Tuesday | Practical/civic guides |

If a paragraph sounds like a press release, an academic paper, a TED talk, a government
brochure, or an LLM blog post — rewrite it. If it sounds like a competent human
explaining something they care about — keep it.

---

## 2. Person and tense — defaults by prose kind

Be consistent *within* a passage; shifts must be deliberate and felt.

| Prose kind | Person | Tense | Example |
|---|---|---|---|
| **Explanation / analysis** | "We" for shared discovery | Present | "To see why the township won the deal, we need to follow the power lines." |
| **Instruction / guide** | "You" + imperative | Present | "Request the application. Read the water section first." |
| **Narrative scene** | Third person, named people | Past | "Crocker wrote RFC 1 alone in his apartment at 3 a.m." |
| **Projection** | Neutral | Future / conditional | "The abatement will expire in 2038." |

Rules that hold everywhere:

- **Never "one."** ("One might consider..." is archaic and distancing.)
- **Past tense only for things that happened; present for things still true.** "DNS resolves
  names" (present, mechanism); "Postel published RFC 791 in 1981" (past, event). The tense
  shift itself can carry meaning — see SPIRIT-TEMPLATE.md.
- **Don't drift within a paragraph.** Pick the register and hold it.
- **"You" is either the default (guides) or rare (narrative).** In narrative books, avoid
  "you must understand that..." — just state it.
- Active voice by default. Passive only when the actor is genuinely unknown or irrelevant.

---

## 3. Sentences

**Target average: 12–18 words** for guides and instructional prose; **15–20 words** for
narrative nonfiction. **Hard ceiling: 30 words (guides) / 35 words (narrative).** If you
hit the ceiling, split.¹

**Variance matters as much as the average.** A wall of same-length sentences is the surest
sign of machine prose. Use the full range deliberately:

| Length | Words | Use |
|---|---|---|
| Ultra-short | 1–5 | Emphasis, turning points, the punch |
| Short | 6–12 | Most instructions; clarity |
| Medium | 13–25 | Development, the "why" |
| Long | 26–35 | Rarely; only when the logic genuinely needs it |

- **One idea per sentence.** If "and" joins two separate ideas, make two sentences.
- **Front-load.** Action or claim first, qualifiers after. The first four words should tell
  the reader whether to keep reading.
- **The three-sentence staccato check:** three consecutive prose sentences under ~10 words —
  deliberate rhythm or accidental chop? If accidental, recombine with "and/but/because."
  (Terse steps inside a numbered procedure are a checklist, not staccato.)
- **Vary openers.** If three consecutive sentences start with the same word ("The," "It,"
  "This"), revise.
- **Fragments:** permitted for effect, sparingly (~2 per page max), earned by a complete
  thought just before. Never a string of faux-profound fragments.

---

## 4. Paragraphs

- **3–7 sentences** (narrative) or **2–5** (guides). Vary the length — symmetry is a tell.
- Shape: **Point → Evidence → Implication.** State it, prove it, say what it means for the
  reader.
- One-sentence paragraphs: fine for emphasis, once or twice per chapter.
- Never end a subsection by restating its point. End with the last piece of new
  information, then stop.

---

## 5. Punctuation

- **Em dashes: maximum one per paragraph.** Overuse is a well-known AI tell. Three or more
  in a paragraph is always a problem. Prefer, in order: commas → colons → new sentence →
  em dash → parentheses.
- **Parentheses:** abbreviation introductions ("Power Usage Effectiveness (PUE)") and truly
  optional asides only.
- **Semicolons:** almost never. A period reads cleaner. Exception: items in a complex list.
- **Exclamation points:** essentially never. If the content is urgent, the period carries it.
- **Colons:** for lists and "here's the rule:" explanations. Good.
- **Oxford comma: always.**

---

## 6. Numbers, dates, and data

- **Dates: ISO `YYYY-MM-DD`** in notes, bibliographies, and anywhere machine-read; in prose,
  full explicit dates ("on 2024-03-15" in reference matter, "in March 2024" in narrative).
  **Never mushy relative dates**: no "recently," "in recent years," "a few years ago,"
  "currently" without an anchor. Write "since 2020," "as of June 2026," "by 1993."²
- **Spell out one–ten in prose; numerals for 11+** — and numerals for *all* measurements,
  doses, times, money, and counts a reader acts on ("2 drops," "5 minutes"). Numbers that
  drive action are scannable; keep them numeric.
- **Every statistic gets context.** "1.4 gigawatts — enough to power 800,000 homes." Never
  drop a bare number.
- **Round for readability** ("$47 billion," not "$47,384,293,021") — except when precision
  serves the reader (hearing dates, doses, deadlines).
- **Every number gets a source**, integrated naturally ("According to the 2025 JLARC audit...").
- **Cross-chapter consistency:** a number that appears in two chapters must match, or the
  difference must be explained (see REVIEW-QA.md, canonical-figures file).
- **Approximate numbers say "about."** Preprints are labeled preprints. Ongoing proceedings
  say "ongoing." Claims are never broader than the evidence.
- Dual units (`2 in / 5 cm`) where an international or safety-critical audience acts on
  measurements.

---

## 7. Jargon and technical language

- **Define on first use**, in one clause, then use the real term. Readers need the real
  name of the thing to use it.
- **Manage concept load.** About 5–7 new terms per trade chapter is a pacing target,
  not a universal cap; adjust it to the reader, genre, and subject. Keep a necessary
  exact term even if it appears once, but do not introduce specialist vocabulary when
  a precise ordinary expression does the same job. A published, reachable glossary can
  supplement an inline explanation; a draft glossary worklist cannot replace one.
- **One good analogy per concept**, then commit to it. Don't re-analogize everything, and
  don't mix metaphors for the same concept.
- Prefer the plain word: use, help, ask, find, start, show.

---

## 8. Banned words

Never use these in prose. `scripts/check_style.py` reads this block verbatim (one entry
per line, lowercase; matching is case-insensitive, word-boundary).

```banned-words
delve
tapestry
myriad
plethora
multifaceted
paradigm
pivotal
crucial
paramount
leverage
utilize
utilization
streamline
synergy
synergies
holistic
embark
unveil
realm
intricate
bustling
nuanced
ever-evolving
seamless
seamlessly
cutting-edge
state-of-the-art
game-changer
game-changing
groundbreaking
transformative
empower
actionable
roadmap
foster
testament
cornerstone
bedrock
hallmark
underscore
underscores
underscoring
essentially
basically
interestingly
notably
importantly
fundamentally
inherently
proactive
innovative
facilitate
endeavor
noteworthy
stakeholder
stakeholders
best-of-breed
next-generation
meticulous
meticulously
showcase
showcases
showcasing
garner
garners
garnered
bolster
bolstered
bolstering
interplay
vibrant
renowned
```

**Replacements** (the usual fixes): delve → look at; leverage/utilize/harness → use;
facilitate → help; foster → support; streamline → simplify; myriad/plethora → many;
paradigm → model; realm → field; crucial/pivotal/paramount → important, or cut;
tapestry → the actual mix; testament/underscores → proof of / shows; empower → give
tools to; stakeholders → name the actual parties.

### Watch list — context-dependent words

Banned in their metaphorical/filler sense; legitimate in a literal or domain sense. The
linter warns; a human decides.

| Word | Banned as | Legitimate as |
|---|---|---|
| landscape | "the AI landscape" | actual terrain |
| ecosystem | "the startup ecosystem" | actual biology |
| navigate / navigating | "navigating complexity" | actual navigation |
| framework | "a framework for thinking" | software frameworks, physical frames |
| robust | "a robust solution" | statistics, engineering tolerance |
| optimize | "optimize your workflow" | mathematical optimization, code |
| unlock | "unlock potential" | actual locks |
| harness | "harness the power of" | actual harness |
| illuminate | "illuminate the issue" | actual light |
| toolkit | "your negotiation toolkit" | an actual set of tools/software |
| catalyst | "a catalyst for change" | actual chemistry |
| comprehensive | "a comprehensive guide" | rarely; prefer thorough/complete |
| elevate | "elevate the discussion" | first aid ("elevate the limb"), physical raising |
| vital | "vital importance" | vital signs |
| profound | "profound implications" | profound deafness |
| revolutionary | hype | actual revolutions (history books) |
| unprecedented | hype | literally the first occurrence, stated as such |
| significant / significantly | unquantified emphasis | statistics, quantified claims |
| ultimately | filler adverb | genuine end states |
| imperative | "it is imperative that" | grammar (imperative mood) |
| disruptive | "disruptive innovation" hype | literal disruption (an outage, a protest) |
| enduring | "enduring legacy/appeal" | an enduring treaty still in force, named as such |
| enhance / enhancing | vague improvement claims | image processing, measured gains |
| emphasize / emphasizing | "emphasizing the importance of" | reporting what a source actually stressed |
| align / resonate | "aligns with values," "resonates with audiences" | mechanical alignment, acoustics |
| nestled | "nestled in the heart of" (promotional) | literal physical nesting (spheres nestled into hollows) |

---

## 9. Banned phrases

Same lint contract: one entry per line, lowercase, substring match, case-insensitive.

```banned-phrases
it's important to note
it is important to note
it should be noted
it's worth noting
it is worth noting
it's worth mentioning
it bears mentioning
let's dive in
dive deep
deep dive
here's the thing
here's the kicker
at the end of the day
when all is said and done
that being said
having said that
with that in mind
with this in mind
on that note
building on this
taking this further
moving forward
going forward
against this backdrop
in light of this
navigating the landscape
navigating the complexities
in today's fast-paced
in today's world
in the world of
in the realm of
the reality is that
the truth is that
it goes without saying
needless to say
the key takeaway
what's interesting is
the question becomes
the challenge lies in
in summary
to sum up
in conclusion
all in all
as we have seen
as mentioned earlier
to recap
to put it simply
in other words
armed with this knowledge
now you're ready to
now you are ready to
with these tools in hand
knowledge is power
make your voice heard
empower yourself
the good news is
your voice matters
every journey begins
in this chapter, we will
in this section, we will
this chapter explores
this section covers
let me walk you through
now let's turn
have you ever wondered
wouldn't you agree
might potentially
could possibly
may perhaps
seems to suggest
appears to indicate
a testament to
serves as a reminder
stands as a
plays a vital role
plays a crucial role
plays a pivotal role
studies have shown
experts agree
it is widely accepted
some experts believe
in recent years
rich tapestry
both were true
both are still true
both remain true
```

Filler transitions ("Furthermore," "Moreover," "Additionally," "Indeed," "Thus,"
"Consequently") are handled as sentence-opener patterns in STYLE-AI-TELLS.md — delete
them; use real connectors ("but," "because," "so," "yet," "still") or none at all.

---

## 10. Pre-submission checklist

- [ ] Read aloud — passes the book's read-aloud test.
- [ ] No banned words or phrases (`scripts/check_style.py` clean).
- [ ] Sentence average within target; nothing over the ceiling; lengths actually vary.
- [ ] No three-in-a-row identical openers; no accidental staccato.
- [ ] Em dashes ≤ 1 per paragraph; parentheses rare; Oxford commas.
- [ ] Person and tense consistent within each passage; correct for the prose kind.
- [ ] Every statistic has context and a source; numbers consistent across chapters.
- [ ] Dates explicit (no "recently"); ISO format in apparatus.
- [ ] Jargon defined on first use; within the chapter's budget.
- [ ] Delete the first sentence as an experiment — keep it deleted if the prose improved.

---

¹ Sentence targets synthesized from the house books: 12–18/30 (How to Fight a Data
Center), 15–20/35 (This Is Server Country, Rough Consensus, The Offline Manual).
² ISO-dates-everywhere and no-relative-dates are the author's standing preference; the
"temporal waffling" ban comes from Rough Consensus STYLE-AI-TELLS §3.4.
Banned lists are the deduplicated union of htsd-book, the-last-book, datacenter-2026-book,
history-through-rfc-book, legal-tech-history-book, and vibe-coding-for-lawyers.
