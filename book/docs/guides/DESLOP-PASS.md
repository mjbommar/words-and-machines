# A Detector-Guided De-Slop Pass

**One process, not the process.** This documents an approach that was developed and
run end-to-end on a single 79k-word narrative-nonfiction book (`history-through-rfc-book`,
23 chapters) in July 2026. It worked there. It is written down because the failures
along the way were instructive, not because it is the correct way to remove AI cadence
from a manuscript.

Plenty of books will not want it. A pure human line-edit, a persona-panel review pass
(see [REVIEW-QA.md](REVIEW-QA.md)), or simply reading the thing aloud will all catch
overlapping sets of problems, and some authors will reasonably object to letting a
commercial classifier anywhere near their prose. Treat what follows as a worked example
with its cost structure and blind spots exposed, and take the parts that fit.

## When this fits, and when it doesn't

**Reasonable fit:**
- A long manuscript where AI assisted with drafting, and you want a systematic sweep
  rather than a chapter-by-chapter feel.
- Prose that has *already* been through human revision — the pass is most valuable
  where it finds what revision missed.
- A project that can afford a detector API budget in the tens of dollars and several
  hours of hand-rewriting.

**Poor fit:**
- Short work. Read it aloud; you will find more, faster.
- Anything where the "tells" are the voice. A deliberately aphoristic or liturgical
  register will light up a detector, and chasing that score would destroy the book.
- Prose you did not write with AI assistance and have no reason to suspect. Do not go
  looking for a problem you do not have.

---

## The premise

An external AI-detector score, computed **per paragraph**, is a *finder* for craft
problems — not a judge of quality and not a target to optimize.

In practice, essentially every paragraph the detector flagged at ≥0.9 contained a
cadence that [STYLE-AI-TELLS.md](STYLE-AI-TELLS.md) already bans. The detector was not
teaching anything new about good prose. It was catching specific instances that the
style pass had walked past. That is genuinely useful and also strictly limited, and
most of the discipline below exists to keep the tool inside that limit.

**The corollary that matters: never edit to move the number. Edit to remove the tell,
and let the number do what it does.**

---

## The pipeline

```
1. SCAN     Per-paragraph scores across target chapters → hotspot map
2. REWORK   Hand-rewrite hotspots per the score policy
3. VERIFY   Prose linter + a re-scan of what you touched
4. REVIEW   Independent agent on the diff: structure, citations, facts
5. FIX      Apply the reviewer's findings — expect real catches
6. SHIP     Rebuild, regenerate any page-count-derived artifacts, commit
```

Batches of roughly four chapters. Commit a verified batch before starting the next, so
each review pass gets a clean diff to work against.

### 1. Scan

Score paragraphs, not documents. Whole-document scores saturate — a single hot
paragraph pulls an entire chapter to 1.00, which tells you nothing about where to look.
Score every paragraph over ~25 words.

Detex first: strip `\cite`, unwrap `\proto{}`/`\keyterm{}` and similar, and **normalize
typography** (see the confound in §"What the detector cannot do"). Then either use a
bulk-scan script or POST paragraphs individually to the detector API.

Useful calibration from the book this was built on: **mean ≈0.20, median ≈0.02** across
the first five files. A healthy chapter had 2–6 paragraphs over 0.5.

The finding that justified the sweep: one chapter had **eight paragraphs over 0.97
after multiple rounds of human revision**. Do not assume a revised chapter is clean.

### 2. Score policy

| Score | Action |
|---|---|
| ≥ 0.7 | Rework |
| 0.5–0.7 | Read it. Touch it only if you can name the tell |
| < 0.5 | Leave alone |
| Any score, deliberate craft | **Craft wins** |

The last row is not a courtesy. On this book a cinematic chapter opener scored **0.92
and was kept**, because it was doing exactly what it was written to do. If you cannot
name what is wrong with a paragraph in the vocabulary of §3, the correct action is to
leave it alone regardless of what the number says.

### 3. What actually triggers a high score

Six patterns accounted for essentially every hotspot:

| Tell | Example |
|---|---|
| **Tricolon** | "no charter, no budget, no formal authority" |
| **Anaphora stack** | "that carried… that let… that routed…" |
| **Aphorism fragment** | "Simplicity over paranoia. Speed over verification." |
| **Mirrored antithesis** | "might never come, or might come tomorrow" |
| **Staccato parade** | four or more short parallel declaratives in a row |
| **Moralizing tag** | a summary clause bolted onto a beat that already landed |

Rewrite moves that worked: merge fragments into one sentence with irregular rhythm;
turn a triple into a two-beat plus a plain sentence; swap an abstract turn for a
concrete image; let one member of a parallel list break the pattern.

**No model output goes into the manuscript verbatim.** Every fix is a hand-rewrite.

### 4. Stubborn paragraphs

If a rewrite re-scores high, the trigger is structural rather than surface. Write two or
three genuinely different candidates, score them *before* editing the file, and take the
one that also reads best. This was needed for 3 of the first 16 hotspots; all landed
≤0.17.

Known structural traps, which are worth restructuring hard on the first attempt:
retained parallel lists, bare aphorism fragments ("The math was fine."), and
one-sentence-per-step textbook rhythm.

### 5. Verify, then review

Re-run the prose linter and re-scan touched paragraphs — **polish passes can introduce
the tells they hunt.** One pass on this book created a fresh "She does not… She does
not… She does not" triple while removing a different one.

Then hand the uncommitted diff to an independent reviewer (human or agent), report-only,
with a fixed checklist: markup integrity, chapter seams, every citation in the diff
resolves, every *removed* citation still appears elsewhere or is flagged, no surviving
claim lost its only source, every rewritten sentence fact-checked against primary
sources, banned-word scan.

---

## Cost control

This is where the process changed mid-flight, and the change is probably the most
portable part of it.

Scoring every fix, plus candidate loops, plus before/after chapter measurement, ran
**50–250 API calls per chapter — on the order of $250 to sweep the book.** That is a
lot of money to confirm something the rewrite already knew.

By roughly 200 fixes in, the scores had become confirmatory: **100% of ≥0.7 hotspots
had a nameable tell**, and tell-removal alone landed ≤0.1 about 90% of the time without
iteration. So:

- **Scan once, in bulk.** One submission for the whole manuscript, on the order of
  $4 for a 90k-word book, instead of thousands of realtime calls.
- **Rework without scoring.** Tell-removal is the acceptance criterion. Name the tell,
  rewrite, self-audit for invented claims and self-echoes.
- **Verify once, in bulk, at the end.** One whole-book scan confirms the sweep and
  catches stragglers; anything still ≥0.7 gets one more pattern-based pass.

If you are starting fresh, start here. The expensive version bought calibration that
this document now gives you for free.

---

## What the detector cannot do

Three experiments, run at the end of the sweep on the chapter the detector flagged
hardest. All three results argue for keeping the tool in its lane.

**1. Frontier-model rewriting does not pass a production detector.** A full
paragraph-level restructure — information order, sentence-length variance, every
nameable tell removed — left 15 of 20 paragraphs at 1.00. Production detectors appear
to detect model-generated text as such, not merely its cadence.

**2. An author-voice fine-tune passes sometimes, and it does not help.** A sampling
harness (generate N candidates → gate on anchor coverage → score) produced 5 genuine
passes in 15 after typography normalization. Every one of them lost to the in-book text
on editorial review: invented claims, garbled clauses, redundancy, style violations. At
edited-chapter quality, none were adoptable.

**3. ⚠ There is a typography confound. Normalize before scoring.** `---` (LaTeX-style
triple hyphen) versus `—` (a real em dash) **flips the verdict on otherwise identical
text, in both directions.** Models trained on LaTeX or plaintext emit `---` and can
score "human" partly on typing convention — a pass that evaporates the moment the book
renders real em dashes.

That third one inflated a measured acceptance rate from **5/15 to 11/15** before it was
caught. Any detector experiment must normalize candidate text to *published* typography
first, and any pipeline script should do this in its detex step.

**The conclusion drawn here:** a production detector partially measures typing
conventions. Editing toward its verdict costs verified content and buys a number. The
deliverable is the craft standard; the score is scaffolding.

---

## Voice models, if you use one at all

A local author-voice fine-tune can generate variations of a paragraph
(see [VOICE-MODELS.md](VOICE-MODELS.md) for setup). Rules learned expensively:

- **Idea quarry, never paste-in.** Roughly a 15% invention rate — fabricated biography,
  corrupted numbers, and invented imagery were all observed in output.
- **Any fact, name, number, or image not in the original is presumptively invented.**
- **Yield on polished prose is low.** Seven edits from nineteen paragraphs in one
  chapter; **zero from six** in another. Zero edits is a valid outcome — do not
  manufacture changes to justify the step.
- Best used on demand, for chapters that feel flat, rather than as a standing stage.

---

## Why the review step is not optional

Rewriting at volume produces a characteristic class of bug that scoring will never
catch. From this book:

- **Contradiction.** A new sentence ("Nobody turned anything off") contradicted the same
  chapter sixteen lines earlier.
- **Dangling antecedent.** A trim deleted the passage that defined "that path," leaving
  the reference stranded.
- **De-repetition creates orphans.** Cutting a duplicated passage can strand the other
  half of its metaphor, or its only citation. Check what the deleted text was
  load-bearing for.
- **Rewrites drift facts.** "Not stealing anything" had to become "not there to spy" to
  match the source assessment. Strengthened phrasing is a fact-check trigger, every
  time.

Two high-severity bugs in the first sixteen rewrites. Across the full sweep, review
rounds caught 55+ defects including roughly fifteen genuine factual repairs — an
incident that made one state both victim and amplifier, a product feature attributed to
the wrong carrier, an attack packet count off by an order of magnitude against the
primary source.

**If you adopt nothing else here, adopt this step.**

---

## Results, with calibration

For the book this was built on: ~290 paragraphs reworked across 23 chapters, four
adversarial review rounds, zero citations lost.

Final whole-book scan, normalized to published typography: **194 AI / 159 Human /
21 Mixed** across 374 paragraphs of 60+ words.

That is not a clean sweep, and reporting it as one would be dishonest. For calibration,
in this detector's terms a raw AI draft scores ~1.00 and a heavily edited chapter from a
human-authored house title scores ~0.91. The number moved; the book got better; those
are related but not the same fact, and the second one is the point.

---

## If you run this again

- Start with the cheap protocol. The expensive one bought calibration you now have.
- Normalize typography in the detex step before the first scan, not after.
- Decide the craft exceptions **before** scanning, so a high score on a deliberate
  passage does not create pressure to justify it after the fact.
- Budget the review step at roughly the same effort as the rewriting. It is where the
  factual errors are caught.
- Consider stopping at the scan. A one-time bulk scan plus hand-rewriting the top
  hotspots captures most of the value for a few dollars; everything past that is
  refinement with sharply diminishing returns.

## Related

- [STYLE-AI-TELLS.md](STYLE-AI-TELLS.md) — the tell catalog this pass depends on
- [REVIEW-QA.md](REVIEW-QA.md) §7 — the shorter operational summary
- [VOICE-MODELS.md](VOICE-MODELS.md) — local voice-model setup
- [WRITING-PROCESS.md](WRITING-PROCESS.md) — where this sits in the phase order
