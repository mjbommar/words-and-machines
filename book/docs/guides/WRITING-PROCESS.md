# WRITING-PROCESS — From Research to Publication

The phased workflow for any book in this template. Seven phases; the middle three form a
**loop** — a chapter cycles Draft → Review → Revise until it meets exit criteria, then
moves to single-pass Polish and Verify.¹

```
Research → Outline → Draft ⇄ Content-edit (review/revise loop) → Copy-edit/Polish
        → Review rounds (whole-manuscript) → Publication prep
```

The universal gate at every phase: **does this serve the book's SPIRIT and its reader?**
(For guides: "can the reader act on this?" For narrative: "does it touch a thread?")

---

## Phase 1: Research

- **Check existing resources first, research second.** Prior projects, wikis, datasets,
  and the reference library usually have the answer.
- Build the per-chapter research folder to the contract in [RESEARCH.md](RESEARCH.md)
  (README-as-contract, sources, timeline, vignettes, data notes).
- Identify gaps explicitly and list them; don't silently skip them.
- Verify anything after your knowledge cutoff via live search; document sources with full
  metadata *now* (see [CITATIONS.md](CITATIONS.md)).

**Exit:** research folder complete; key data verified; vignette candidates identified;
timeline built; open questions listed.

## Phase 2: Outline

- One outline per chapter, section-by-section, with word allocations, figure specs, and
  the chapter's *question* stated as the reader would ask it.
- Plan the chapter's recurring elements (anchor location, coda, callout budget) so they
  arrive by design, not improvisation.
- Structural review before drafting: clear argument? realistic word count? transitions to
  neighbors? dependencies on earlier chapters satisfied?
- For this book, pin the chapter's object spine before prose: each
  load-bearing object, its current status, evidence route, scope, reader-proof
  or reader-explanation miniature, negative control, and next-door question.
  An artifact without a teaching route is not ready to draft.
- **Stuck on the angle or the shape?** `scripts/prompt_roller.py --kind chapter` rolls
  constrained chapter/essay concepts out of the writing ontology, and
  `scripts/exercise_generator.py --topic "…"` runs one topic up the progymnasmata ladder
  when a passage needs a different attack. For structure,
  `scripts/beat_scaffold.py --list` shows the arcs and arrangements carrying beats, and
  `--template NAME --words N` instantiates one as a scaffold with per-beat word budgets.
  Name the arc shape you chose in the outline — `arc_profiler.py --target` checks the
  draft against it later. All advisory, all seeded ([ONTOLOGY.md](ONTOLOGY.md)).

**Exit:** outline reviewed; figures specified with data sources; hook identified (real
place/date/stakes).

## Phase 3: Draft

- **Read SPIRIT.md and the style guides immediately before drafting.**
- Follow the book-specific sequence in `CRAFT.md`: encounter → exact term →
  reader argument → formal object → machine evidence → attack → boundary →
  consequence. Vary the local rhythm, but do not omit the reader argument.
- Write the hook first, with care; then draft section by section without looping back.
- **The first draft's job is to exist.** Mark problems `TODO`, missing sources `CITE`,
  and keep moving. Don't polish.
- **Cite as you write** — deferred citations are forgotten citations.
- Apply the read-aloud test continuously, not at the end.
- Write callout boxes and data context inline while the material is fresh.
- **Draft with a palette.** `scripts/palette_sampler.py --for-prompt --seed N` prints a
  short set of named constructions, figures, and cadences plus its use-sparingly rules;
  paste it into the drafting prompt (or hand it to `chapter-drafter`). One palette move
  per paragraph, unused items free, never name the technique in the prose. Record the
  seed with the draft.

**Exit:** complete draft; TODOs/CITEs marked; a one-paragraph self-assessment.

## Phase 4–5: The content-edit loop (Review ⇄ Revise)

Each pass:

1. **Multi-perspective read** — 3–6 personas appropriate to the book (general reader,
   domain expert, skeptic, the person the book is about, fact-checker, line editor).
   Full recipe in [REVIEW-QA.md](REVIEW-QA.md).
2. **Mechanical checks** — `check_style.py` (banned lists, sentence stats, reading
   level), AI-tell patterns, repetition scan. Then the advisory craft sweep:
   `make brief` (`make craft` for the raw diagnostics) — construction variety, figures,
   cadence, register, arc shape, unpaid promises. Its findings feed the fix briefs; none
   of them gates anything.
3. **Compile a review report** per chapter: major (structural) → medium (clarity) →
   minor (style) issues, factual concerns, priorities.
4. **Revise in priority order**: structure/usefulness first, then clarity, then style.
   Never fix typos while restructuring — separate passes for separate levels.
5. Keep a revision log (what changed and why).

**Harden the argument before you convene a review panel** (nonfiction): run
`scripts/objection_engine.py --chapter chNN` to fire each argumentation scheme's
critical questions at the chapter's load-bearing claims, and
`scripts/sparring_partner.py --thesis "…"` for a seeded panel of adversarial personae
against the book's thesis. Both produce agendas of questions; the answers belong in the
draft, in your own words. Doing this first keeps the panel's attention on what only a
reader can see.

**Exit criteria (all must hold):**
- [ ] Zero violations from the style checker
- [ ] AI-tell audit clean; burstiness verified
- [ ] Every fact real and sourced (no hypothetical examples)
- [ ] Reading level within the book's target
- [ ] Persona reviewers score ≥ target on the rubric (REVIEW-QA.md)

## Phase 6: Copy-edit / Polish (single pass)

- **Compression:** cut 5–15% without losing content. Hunt "in order to," "the fact
  that," restatement sentences, summary paragraphs.
- **Burstiness pass** and **opener-variation pass** (see STYLE.md §3).
- **Cross-chapter consistency:** terminology, cross-references, one-home-per-fact,
  number agreement.
- Openers/closers refined; transitions checked in sequence reads.

## Phase 7: Verify

- Citation verification per [CITATIONS.md](CITATIONS.md) — every claim against its
  actual source, fetched, field by field.
- Fact-check pass with claim inventory and verdicts; canonical figures pinned.
- Final build validation (PDF/EPUB builds clean; word/page counts in range).

---

## The book_stats delta convention

`scripts/book_stats.py` reports word counts, sentence stats, readability, and banned-word
hits. **Every significant revision session brackets itself with it:**

```bash
uv run scripts/book_stats.py --json > /tmp/stats-before.json
# ... make revisions ...
uv run scripts/book_stats.py --json > /tmp/stats-after.json
# report the delta in the commit message / session summary
```

This makes edits accountable: a "tightening" pass that grew the chapter, or a fix pass
that tanked readability, is visible immediately.²

Four advisory companions quantify prose quality between rounds (none is a
gate; all support `--root` for use across books): `make metrics`
(prose_metrics.py — burstiness, MTLD/MATTR lexical diversity, specificity,
paragraph uniformity per chapter, compared against the house baseline in
scripts/data/prose-baseline.json), `make vocab` (vocab_variety.py —
overused words vs English base rates with OpenGloss synonym ideation),
`make slop` (slop_audit.py — slop constructions and vocabulary at every
granularity, plus a taxonomy-driven LLM judge), and `make pangram`
(pangram_check.py — external Pangram detector cross-check, paid; see
docs/guides/REVIEW-QA.md §2-3 for all four). `make prose-report` runs the
free three in one command and writes a single markdown report with
round-over-round deltas (add `--pangram` / `--deslop N` for the paid and
voice-model sections) — bracket each revision round with it the same way
book_stats brackets word counts.

Those tools say what is flat or overused. The craft side says what to reach
for instead: `make brief` (with `make craft` and `make ontology` behind it)
runs the writing-ontology diagnostics — construction variety, rhythm,
register, arc shape, discourse moves, unpaid promises — and the generative
samplers supply the named alternatives. Advisory too, and each diagnostic
takes `--root` for use across books; usage in [ONTOLOGY.md](ONTOLOGY.md).

---

## Review rounds: the `docs/review-NN/` convention

Whole-manuscript review happens in numbered rounds, each a directory:

```
docs/review-03/
├── 00-synthesis.md        ← cross-cutting findings, prioritized into tiers
├── ch01-synthesis.md      ← per-chapter: all personas' findings merged
├── ch02-synthesis.md
├── ...
└── (optional) NN-persona-review.md   ← full persona reviews (WSJ critic, domain expert…)
```

Rules that make rounds work:³

1. **Reviewers never edit.** A review round produces *findings and edit lists*, not
   changed manuscript files. Per-chapter synthesis files contain concrete edits in
   find/replace form ("Find: `...` / Replace: `...` / Rationale: ...") so an executor can
   apply them without re-deriving the reasoning.
2. **Findings are tiered:** Tier 1 = fix before publication (factual errors, internal
   inconsistencies, credibility risks); Tier 2 = strengthen (analytical/structural gaps);
   Tier 3 = optional polish.
3. **Every finding names its evidence** — file, section, quoted snippet — and which
   reviewer(s) raised it. Convergent findings (multiple personas, same issue) outrank
   solo ones.
4. **Fix execution is assigned in non-overlapping briefs.** One agent (or session) per
   chapter, working from a shared `_AGENT-BRIEF.md` that names: required reading, the
   defect list, hard constraints (accuracy first; preserve thesis and balance; respect
   canonical homes), and the exact output template. Plans/edits for the same file never
   run concurrently.
5. **Plan, critique, then execute** for big restructures: agents write *plans*, a second
   round critiques the plans, the lead executes. For routine fixes, the synthesis edit
   list is executed directly.
6. **Bracket the round with book_stats** and re-run the mechanical checks after
   execution; a round isn't closed until the checker is clean and Tier 1 items are
   verified fixed.

Number rounds sequentially (`review-01`, `review-02`, ...) and never delete old ones —
they are the book's editorial memory.

---

## Roles (human or agent)

| Role | Produces | Never does |
|---|---|---|
| Researcher | research folders, verified sources | prose |
| Outliner | chapter outlines | drafting past the outline |
| Drafter | first-draft prose from outline + research | citation invention |
| Reviewer (persona) | findings, scores, edit lists | edits to manuscript |
| Fact-checker | claim inventory + verdicts + provenance log | silent fixes |
| Executor / line editor | applied edits per brief | new findings out of scope |
| Lead | synthesis, tiering, briefs, final calls | skipping the checker |

Not every chapter needs every step — judgment by draft maturity. But no chapter skips
the loop exit criteria or Phase 7.

---

## Common pitfalls

- **Perfectionism in Phase 3** — the draft's job is to exist.
- **Deferring citations** — you will forget the source.
- **Mixing revision levels** — structure, then clarity, then style, separately.
- **Adding instead of cutting in revision** — chapters should usually get shorter.
- **Reviewers editing directly** — destroys the audit trail and invites conflicts.
- **Exiting the loop early** — if the checker still flags, you're not done.
- **Trusting "verified" without a fetch** — see CITATIONS.md; this has failed before.

---

¹ Phase structure from datacenter-2026-book WRITING-PROCESS (7 phases, coffee-test-
continuously, weekly cadence) merged with htsd-book's explicit Draft⇄Review⇄Revise loop
and exit criteria.
² Delta convention from vibe-coding-for-lawyers CLAUDE.md revision workflow.
³ Round mechanics synthesized from htsd-book `docs/review-03/` (per-chapter syntheses with
find/replace edit lists, tiered priorities) and wiki-history-book `docs/revise-02/`
(_AGENT-BRIEF.md: plan-not-rewrite, hard constraints, one chapter per agent).
