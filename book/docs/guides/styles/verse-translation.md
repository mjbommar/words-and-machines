# Style Profile: Verse Translation / Parallel Text

Layered over [STYLE.md](../STYLE.md) — select with `style.profile:
verse-translation` in `book.yaml`. For line-matched translations that
set a source text against a modern-register English rendering, and
often double as a language reader.

Portfolio exemplars: *The Brainrot Iliad*, *The Brainrot
Metamorphoses* — classical verse in internet-native English, 1:1 line
matched, with a progressive Greek/Latin reader in the margins.

**Requires the verse module** (`modules.verse: true`, xelatex) for the
paracol parallel-text layout. Content is usually generated stanza by
stanza from structured JSON, not hand-written into chapters — so most
of this profile is guidance for the generation prompt and the sampling
QA, not for `check_style.py`.

## The one idea

**Register itself is the product.** The gap between the source's
weight and the English's voice is the whole effect. Pick the target
register deliberately (the brainrot books sit at a Discord/TikTok
"terminally online" level) and define it as a spectrum, not a single
setting — most lines live in the middle; the extreme is rare.

## The craft law that governs everything

**Earn the quiet moments by being loud everywhere else.** Grief,
tenderness, and death get *simpler* language and shorter sentences —
never forced slang. The loud register everywhere else is what makes the
plain moments land. A death scene written in memes is the signature
failure of the form.

Corollaries the portfolio learned the hard way:

- **Victims are not punchlines.** Where the source depicts violence
  (especially sexual violence), render it in clear modern language that
  names the injustice as injustice. Never joke it, never summarize it
  away.
- **Show the physical, don't summarize it.** "Bark crawled up her legs
  and her arms branched into limbs," not "she was turned into a tree."
- **Specific beats generic.** A precise, current reference beats a
  stock meme label; stock labels erode fast and date the book.

## Structural fidelity (non-negotiable)

- **1:1 line matching**: one English line per source line, nothing
  added, nothing removed. Where the source pauses, you pause. This is a
  hard structural contract, usually enforced in the JSON, not the prose.
- The stanza is the atomic unit: fixed line count, a mood field, scene
  breaks with defined semantics.
- **Character voices live as data**, not vibes — a character bible
  giving each figure a consistent register ("keep him slangy but never
  unserious in grief"). Generate against it; check against it.

## If it doubles as a language reader

- Margin notes anchor to a *visible* word — never teach grammar in the
  abstract.
- **Never re-teach; always build forward.** Keep a cumulative
  knowledge diary so a concept taught in book 3 is assumed, not
  re-explained, in book 30.

## Watch for (this register's failure modes)

- Forced slang in solemn scenes (the cardinal sin).
- Academic drift — "beheld," "resolved," "gazed," "whereupon" — the
  translation-ese the modern register exists to avoid.
- Register drift across stanzas; character voice drift across books.
- Meme labels that will read as dated in a year.

## Lint deltas

The house AI-tell budget doesn't fit generated verse (deliberate
fragments, one line per source line), so it's relaxed; the value here
is the banned translation-ese, caught per line. Register and
quiet-moment restraint are checked by **seeded stanza sampling** with a
rubric, not regex — see the book's sampling script.

```style-targets
tell_budget: 8
sentence_avg_lo: 6
sentence_avg_hi: 16
sentence_hard_max: 40
paragraph_sents_lo: 1
paragraph_sents_hi: 8
# Craft diagnostics (rhythm_audit.py, register_report.py) — see ONTOLOGY.md
cadence_share_max: 0.75           # a metrical line ends the same way on purpose; the prose default is meaningless here
cadence_run_max: 10.0             # consecutive identical endings are the meter, not a defect
uniform_para_pct_max: 60.0        # one line per source line: stanzas are uniform by construction
attitude_per_1000_max: 20.0       # verse carries stance openly; the prose ceiling would fire on every page
latinate_ratio_max: 0.35          # kept tight on purpose: translation-ese ("beheld", "whereupon") is Latinate drift
```

Register is the *product* of this profile, not a side effect — the numbers
above are loose so they stay out of the way, and the real check is seeded
stanza sampling against the rubric.

```banned-words-add
beheld
whereupon
resolved
gazed
henceforth
thus
```
