# REVIEW-QA — Persona Panels, Audits, and Anti-Drift Checks

The quality-assurance playbook: how to review a manuscript so problems are found by
design, not luck. Companion to [WRITING-PROCESS.md](WRITING-PROCESS.md) (which defines
the `docs/review-NN/` round mechanics and the reviewers-never-edit rule).

---

## 1. The persona panel

Review every chapter (and the whole book) through a fixed panel of personas. Each persona
reads independently and produces findings + scores; a synthesis merges them.¹

### The standard panel (adapt names to the book)

| Persona | Reads for | Example instantiations |
|---|---|---|
| **Trade critic** | Craft, prose quality, argument, market fit | WSJ reviewer, New Yorker critic, Kirkus, NYRB essayist |
| **Domain expert** | Technical/factual accuracy, insider credibility | energy reporter, protocol engineer, practicing lawyer, historian |
| **The person the book is about** | Fair portrayal, real-world usability | township supervisor, community organizer, working analyst |
| **General reader** | Accessibility, engagement, jargon, pacing | smart friend with no background |
| **Skeptic** | Balance, overclaiming, scope of evidence | reader hostile to the thesis |
| **Fact-checker** | Every number, name, date, quote | — |
| **Line editor** | Sentence-level craft, AI tells, repetition | — |

Panel size 3–6 per round; the trade-critic + domain-expert + general-reader trio is the
minimum. Persona reviews are written *in character* (a full mock review, with a headline)
— the register surfaces different problems than a checklist does.

### Scoring rubric

Each persona scores 1–5 on their axes; the round has numeric before/after accountability.

| Axis | 1 | 3 | 5 |
|---|---|---|---|
| Accuracy | errors an expert catches instantly | minor imprecision | survives hostile expert read |
| Craft | AI-flavored, monotone | competent, flat in places | quotable; rhythm and surprise |
| Usefulness / stakes | reader can't act / doesn't care | some takeaways | reader acts / feels the thread |
| Structure | buried lede, redundancy | mostly sound | shape carries the argument |
| Voice fidelity | violates STYLE/SPIRIT | drifts occasionally | unmistakably the house voice |

**The scored loop:** run the panel, execute fixes, re-run the *same* personas on changed
chapters; repeat (typically 3–5 rounds) until scores plateau at/above target (≥4 on every
axis is the usual bar). Log scores per round in `00-synthesis.md` so the plateau is
visible.

### Synthesis and tiering

`docs/review-NN/00-synthesis.md` merges findings into tiers:
- **Tier 1 — fix before publication:** factual errors, internal inconsistencies,
  citation problems, anything an opposing expert/journalist would catch.
- **Tier 2 — strengthen:** analytical gaps, structural weaknesses flagged by 2+ personas.
- **Tier 3 — polish:** style, taste, optional additions.

Each finding: evidence (file, section, quote), source persona(s), proposed fix. Per-
chapter synthesis files carry executable find/replace edit lists.

---

## 2. Grep audits

Cheap, mechanical, catch what read-throughs miss. Run at every round:

```bash
# Banned words/phrases, AI-tell patterns, forbidden constructs
uv run scripts/check_style.py            # add --strict-tells to fail on any tell

# Repetition: n-grams, monotone sentence starts, duplicate sentences
uv run scripts/check_prose.py

# Burstiness + lexical diversity + specificity per chapter, compared
# against the house baseline (scripts/data/prose-baseline.json — percentile
# bands from 128 chapters of edited house books)
uv run scripts/prose_metrics.py

# Slop constructions, slop vocabulary, repetitive-paragraph outliers,
# ranked worst paragraphs with file:line anchors (advisory)
uv run scripts/slop_audit.py --level paragraph

# A suspected repeated phrase or stat, across the whole manuscript
grep -rn "48 cents" latex/chapters/

# Vocabulary ruts: overused words vs their English base rates, with
# OpenGloss synonyms annotated by in-book usage (replaces the manual
# word-frequency grep)
uv run scripts/vocab_variety.py --sort ratio --band mid

# Craft diagnostics: sentence-opener and architecture monotony, figure
# density, cadence runs, hedge/booster/Latinate register, chapter arc
# shape, unpaid promises — the ontology's revision suite (advisory)
make craft

# The same thing packaged as one brief for the round (advisory)
make brief

# Provenance: do long spans appear verbatim in a 4.3T-token corpus?
# (a different risk from detectability — see docs/guides/PROVENANCE.md)
uv run scripts/phrase_check.py --chapter ch07 -n 40

# Every number in a chapter, for cross-chapter agreement checks
grep -on "[0-9][0-9,.]*\s*\(percent\|%\|billion\|million\|GW\|MW\)" latex/chapters/*.tex
```

**The raw-draft fingerprint** (calibrated against an unedited
claude-sonnet-5 chapter vs the house baseline): sentence-length cv *below*
house p10, paragraph-length cv below p10, adverb share *above* p90 — and
MTLD/MATTR **above** p90, not below. Raw model prose over-rotates synonyms
("elegant variation"), so unusually *high* lexical diversity is as much a
draft signal as unusually low. A chapter tripping three or more house notes
at once is almost certainly under-edited; single notes are usually genre.

**External detector cross-check** — `make pangram`
(scripts/pangram_check.py, needs `PANGRAM_API_KEY`; realtime API for small
runs, bulk queue at $0.04/1k for large ones) scores
each chapter with the Pangram production detector: fraction AI /
AI-assisted / human plus every flagged window. Calibration (July 2026):
known-human Gutenberg prose scored 1.00 human; a raw claude-sonnet-5 draft
1.00 AI; a style-gate-passing edited house chapter still 0.91 AI. Read the
axes separately: the house tools measure *craft* (is the prose good?),
Pangram measures *detectability* (does it statistically resemble model
output?) — editing improves both, but passing `make check` does not defeat
a production detector, and that is not the goal of this pipeline.
Two further calibration results (2026-07, history-through-rfc-book):
frontier-model *rewriting* does not move the production verdict (15/20
restructured paragraphs still 1.00 AI), and **typography is a confound** —
`---` vs a real `—` flips the verdict on otherwise identical text, so any
experiment must normalize candidate text to published typography before
scoring (an author-voice fine-tune's apparent pass rate halved once its
LaTeX-style dashes were normalized).

**Craft evidence, before and after.** Run `make brief` *before* the panel
convenes and hand the output to the reviewers and to `review-synthesizer`:
it names what is monotone and where, with file and line anchors, so persona
findings can be corroborated instead of argued. Run it again after the
round's fixes land and record the deltas next to the `book_stats` numbers —
opener runs closed, cadence share down, promises paid. Read them exactly
like the metrics above: **advisory**. A craft WARN is a place to look, never
a gate, and "craft wins" beats every number here (§7 score policy).
`docs/guides/ONTOLOGY.md` covers what each diagnostic measures, which ones
honor the genre profile's ```style-targets```, and which corpus each scans.

Standing audit targets:²
- **Repeated statistics/quotes across chapters** — a striking stat cited in 4+ chapters
  is noise, not signal. One home chapter; callbacks elsewhere.
- **Thesis hammer** — grep the thesis's key phrases; count restatements per chapter.
- **Structural clones** — list every chapter's opening type and closing gesture in a
  table; identical adjacent entries are findings.
- **Filler-transition openers, "This"-openers, gerund openers** — density counts per
  chapter (see STYLE-AI-TELLS tell-patterns block).

---

## 3. Random span sampling

Reviewers unconsciously oversample chapter openings. `scripts/sample_text.py` pulls
random contiguous prose spans (LaTeX stripped) for stratified line-editing:³

```bash
uv run scripts/sample_text.py --spans 5 --seed 1      # 5 random spans, reproducible
uv run scripts/sample_text.py --chapter ch07 --spans 5 # from a specific chapter
uv run scripts/sample_text.py --sentences 6            # longer spans

# Stratified pass: 10 batches across the book
for i in $(seq 1 10); do uv run scripts/sample_text.py --spans 5 --seed $i; done
```

The same sampling philosophy extends to the LLM slop judge: audit a random
slice instead of (or before) the whole book —

```bash
uv run scripts/slop_audit.py --llm --sample random --n 5 --seed 1   # 5 paragraphs
uv run scripts/slop_audit.py --llm --unit sentence --pct 2          # 2% of sentences
uv run scripts/slop_audit.py --llm --sample all --limit 0           # entire book
```

Each verdict cites per-tell evidence from the 54-tell taxonomy
(`--list-tells`); the aggregate table at the end gives per-violation counts
and locations. Judges: `anthropic:claude-sonnet-5` (default),
`anthropic:claude-fable-5`, `openai:gpt-5.6-terra`.

Workflow: sample 5–10 spans per chapter → line-edit each against STYLE + AI-TELLS → if
2+ spans in a chapter fail, the whole chapter gets a full line-edit pass. Random sampling
is the honesty check on "the book is basically clean."

---

## 4. The canonical-figures file (numeric anti-drift)

Cross-chapter numbers drift: "8,000 generators" in ch. 2 becomes "9,000" in ch. 5;
"about 9 million" becomes "nearly 10 million." Fix by pinning a single source of truth:⁴

**`research/fact-check-NN/00-canonical-figures.md`** — one table per figure family:

| Figure | Previous (in book) | Canonical | Source |
|---|---|---|---|
| Documented projects | 604 | **609** | project database, updated 2026-04-10 |
| Announced investment | $1.1T | **$1.18T** (round: "nearly $1.2 trillion") | same |

Usage rules (copy these into the file):
1. Exact figures are canonical; rounding for readability is fine but must not contradict
   them ("more than 600," never "about 650").
2. Every changed claim gets a row in the chapter's provenance log with full source and
   access date.
3. The file states the book's **vantage date** ("the book speaks from June 2026; events
   through May are past; 'this year' = 2026") so tense and currency stay consistent.
4. Before finalizing any chapter, grep the manuscript for every number in that chapter
   and check each against this file.

---

## 5. Cross-chapter repetition checks

Beyond grep, once per round:

1. **Canonical-homes table:** every big fact/story/explainer → its home chapter. Other
   appearances must be one-sentence callbacks ("Chapter 2 laid out the numbers: ...").
2. **Adjacent read-aloud:** read two adjacent chapters back to back; you *hear* echoes
   that page-by-page review misses.
3. **Opening/closing inventory:** table of every chapter's hook type and final gesture;
   diversify where adjacent rows match.
4. **Refrain audit:** deliberate leitmotifs (from SPIRIT.md) are exempt — but each
   occurrence must accumulate meaning, not just recur.

---

## 6. Reading-level and stats gates

- Flesch-Kincaid per chapter against the book's target (set in STYLE/CLAUDE.md; e.g.
  grade 7–10 for civic guides, 10–12 for narrative nonfiction).
- Average and max sentence length per chapter (see STYLE.md §3).
- Word count per chapter vs. outline allocation (±20% triggers a look).
- All via `book_stats.py`; bracket every round with before/after JSON (the delta
  convention in WRITING-PROCESS.md).

---

## 7. Detector-guided de-slop pass⁵

An external AI-detector (Pangram) scored per paragraph is a *finder* for AI-cadence
prose, not a judge. Paragraphs flagged ≥0.9 almost always contain a tell that
STYLE-AI-TELLS.md already bans — the detector catches instances the style passes missed.
Chapters that have survived multiple human revision rounds still turn up hotspots (the
pilot found eight ≥0.97 paragraphs in a heavily-revised chapter, including its opener).

**Granularity:** whole-document scores saturate — one hot paragraph pushes a full
chapter to 1.0. Score paragraphs (`pangram_check.py --unit paragraph`). Healthy
baseline: mean ≈ 0.2, median ≈ 0.02, a handful of paragraphs over 0.5 per chapter.

**Which number to read (Pangram 4).** `fraction_ai` is a word-weighted average
of *hard* segment labels, so a single-paragraph submission (one window) returns
only 0.0 or 1.0 — useful as a verdict, useless as a score or a ranking key.
The continuous signal is `windows[].ai_assistance_score`; `deslop.py` ranks on
its token-weighted mean. Measured constants on the house corpus: **label
boundary ≈ 0.37**, and the scale **saturates above ~0.98**, so a paragraph at
0.99 will read unchanged until it moves a long way. Also: **a paragraph scored
alone is not the paragraph the book gets scored on** — a rewrite at 0.00 in
isolation scored 1.00 back between its original neighbours (CRF label
smoothing), and three isolated 0.00 rewrites scored 1.00 concatenated. Treat
isolated paragraph scores as a triage signal, never as a chapter forecast.

**Score policy:**

| Score | Action |
|---|---|
| ≥ 0.7 | Rework by hand |
| 0.5 – 0.7 | Read; touch only if you can name the tell |
| < 0.5 | Leave alone |
| Any score, deliberate craft | Craft wins — never edit to move the number |

**The tells that trigger ≥0.9** (all bannable on style grounds anyway): tricolons
("no charter, no budget, no formal authority"), anaphora stacks ("that carried… that
let… that routed…"), aphorism fragments ("Simplicity over paranoia."), mirrored
antitheses ("might never come, or might come tomorrow"), staccato parallel parades, and
moralizing tags bolted onto a landed beat. Fixes: merge fragments into one flowing
sentence with irregular rhythm, convert triples to two beats plus a plain sentence,
swap the abstract turn for a concrete image.

**The candidate loop:** when a rework re-scores high, the trigger is structural. Write
2–3 genuinely different rewrites, score them all via the API *before* editing the file,
apply the winner that also reads best aloud.

**Voice-model variants** (`scripts/deslop.py`, optional): a local author-voice rewrite
model generates 3 sampled variations per paragraph as ideation. Idea quarries, never
paste-ins — expect a ~15% invention rate and flattened craft; any fact/name/image not in
the original is presumptively invented. Yield is low on polished prose; zero edits is a
valid outcome.

Every variant now carries a mechanical **faithfulness verdict** (invented and
dropped numbers/proper nouns, length ratio, quant-slop delta), and
`deslop.py --batch` ranks a whole book's paragraphs by slop signals and emits
a fix brief (`--out brief.md`, or `--format jsonl` for the revision agent) —
original and rewrite side by side, never touching the chapters. The server is
auto-discovered on :8091 then :8092 (any OpenAI-compatible endpoint);
model selection, serving recipe, and failure modes:
[VOICE-MODELS.md](VOICE-MODELS.md).

**Model calibration.** Two measurements, in order of authority:

> **Superseded metric.** The numbers in this paragraph were computed on
> `fraction_ai`, which is 1-bit for single-paragraph submissions. Re-measured
> on the continuous window score the same campaign reads **0.878 → 0.410**.
> Directions hold; precision does not. See VOICE-MODELS.md §1b.

*Pangram 4 (2026-07-29, 8 real paragraphs, weighted-AI = fraction_ai +
0.5x fraction_ai_assisted):* v4 is far harder than v3 — the same best-of-3
recipe that scored 0.38 on v3 scores 0.70 on v4. Deterministic edits move
it **not at all**; the ladder that works is sampling + detector selection
(0.875 -> 0.70), few-shot with detector-verified exemplars (0.63), model
diversity (0.50), and notes-reconstruction (0.42), reaching **0.31** with a
wide pool. Tiers, findings, and caveats: [VOICE-MODELS.md](VOICE-MODELS.md)
§1a. Run it with `deslop.py --candidates N --fewshot --notes --servers ...`.

*Earlier full bench (2026-07-26, 8 real paragraphs — 4 detector-flagged, 2 stylized
front-matter, 2 raw-draft; typography confound audited):* the
**Qwen3.5-4B-voice fine-tune led every axis at once** — 162 tok/s, 6/8
faithful with zero invention, Pangram 0.75→0.38 (5 rewrites at 0.00), best
OGBert voice-sim. Larger prompt-only Gemmas (26B-A4B, 31B) tied its 0.38 at
1.5–6.5× less speed; gemma-4-E4B (the model README's original pick) did not
move detector scores at all on this eval; gpt-oss-20b made them worse. Full
table and machine-independent guidance: [VOICE-MODELS.md](VOICE-MODELS.md).

*Earlier single-chapter probe (one raw draft, 6 paragraphs):* Qwen stripped
every quant signal yet stayed 1.00 AI; Gemma moved Pangram to 0.42/0.58
assisted. That result did not generalize — prefer the full bench.

Still true either way: no model reached the human band on flagged prose;
sampling variance + scoring (`deslop.py --candidates`) finds 0.00-AI variants
that single-shot rewriting misses; hand-rework closes. Use the briefs as
quarries.

**The safety net is mandatory.** After a rework batch, run an independent review agent
on the git diff (report-only): LaTeX integrity, chapter seams, every cite in the diff
exists, every removed cite still cited elsewhere, fact-check of every rewritten
sentence, banned-word scan. In the pilot this caught, per ~16 rewrites: a new sentence
contradicting its own chapter sixteen lines up, a dangling antecedent left by a cut, and
two fact drifts introduced by "stronger" phrasing. Rewriting at volume produces these;
budget for the net.

**Mechanics:** batches of ~4 chapters; verify (prose checker + re-score touched
paragraphs — polish passes can introduce the very tells they hunt); review; fix; rebuild;
commit the batch before starting the next so every review agent gets a clean diff.

---

## 8. Round exit checklist

- [ ] All personas ran; scores logged; plateau or target reached
- [ ] `00-synthesis.md` written; findings tiered; Tier 1 empty *after* execution
- [ ] check_style / check_prose clean
- [ ] Random-span sample pass ≥ 80% clean
- [ ] Canonical figures verified against every chapter touched
- [ ] Repetition inventory updated; no new cross-chapter duplicates
- [ ] book_stats delta reported
- [ ] `make brief` re-run after execution; craft deltas noted in the round's
      synthesis (advisory — a remaining WARN does not hold the round open)

---

¹ Panel + scored rounds from htsd-book `docs/reviews-02/` (WSJ, New Yorker, Kirkus,
township supervisor, community organizer, energy reporter → 00-synthesis with tiers) and
`docs/review-03/` (five personas per chapter with find/replace edit lists); perspective
lists also from datacenter (6 perspectives) and legal-tech (7 reader personas).
² Repetition taxonomy and real examples from wiki-history-book
REPETITION-AND-FATIGUE-GUIDE (a quote verbatim in 7+ chapters; one stat in 15+ locations).
³ `sample_text.py` design from history-through-rfc-book `docs/SCRIPTS.md`.
⁴ Canonical-figures pattern from htsd-book `research/fact-check-2026-06/00-canonical-figures.md`.
⁵ Pipeline, score policy, tell taxonomy, and pilot results from history-through-rfc-book
`docs/DESLOP-PIPELINE.md` (2026-07 pass over prologue/ch1/ch22/ch23/epilogue: 16 hotspots
reworked, all facts and citations preserved, verified by independent diff review).
