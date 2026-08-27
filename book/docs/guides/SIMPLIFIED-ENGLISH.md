# Simplified Book English (SBE)

A semi-controlled vocabulary for trade nonfiction: a core word list a
general reader already has, an open second tier, and a protocol for
admitting everything else. It borrows the *structure* of ASD-STE100
Simplified Technical English — writing rules, a dictionary, a named
allowance for domain terms — and changes what a book needs changed.

**Advisory. Not part of `make check`.** Run `make simplified`. Vocabulary is
a judgement call often enough that a lexical linter should not stand
between you and a release; add `--strict` to your own CI if you want a gate.

**Dictionary:** `scripts/data/simplified_english/lexicon.json`
**Policy you edit:** `scripts/data/simplified_english/curated.yaml`
**Per-book settings:** `simplified_english:` in `book.yaml`
**How it was built:** [architecture/simplified-english.md](../architecture/simplified-english.md)

Read after [STYLE.md](STYLE.md). SBE governs *which words*; STYLE governs
voice and sentences; [STYLE-CRAFT.md](STYLE-CRAFT.md) governs rhythm and
figure. Where they overlap, they defer (§8).

---

## 1. The reader this standard assumes

Every serious controlled language names its reader. STE's is a non-native
technician on a tarmac. VOA Special English's is an intermediate learner.
ISO 24495-1 makes identifying the reader the *first* thing you do, before
drafting.[^iso] So:

> **SBE is calibrated for an adult general reader of English trade
> nonfiction:** fluent, not a specialist in this book's field, reading in
> long stretches — in print, without a dictionary to hand.

**No CEFR claim.** An earlier draft of this section said "plausibly a
non-native speaker at around CEFR B2–C1". Nothing in the build supports
that. Graded against the CEFR-J Vocabulary Profile v1.5 and the Octanove
C1/C2 profile, 59.0% of the core tier sits at or below B2, 3.5% sits
above it, and **37.5% is not on any CEFR inventory at all**; across the
whole free vocabulary 70.4% carries no CEFR rating. The tiers are a
frequency artifact (§10), and frequency is not proficiency. A real B2
ceiling is buildable and cheap — the CEFR-J profile is a free CSV usable
commercially with attribution — but it has not been built, so it is not
claimed.

Every rule below is a bet about that reader. A book with a different reader
— a practitioner's manual, a textbook, a memoir for insiders — should change
the thresholds in `book.yaml` and say so in its own `SPIRIT.md`.

---

## 2. Why a controlled vocabulary, and why not the aerospace one

ASD-STE100 exists because a technician cannot ask the author what a
sentence meant. Issue 9 answers with 53 writing rules and a dictionary of
875 approved words and 1,274 unapproved ones with alternatives — each
approved word, *in general*, carrying one meaning and one part of speech.
Around that core sits an open allowance: 22 categories of **technical
nouns** and 4 of **technical verbs** that a company may add for its own
subject.[^ste] So STE is not a closed vocabulary; it is a small closed core
plus a category-gated open one. SBE has the same shape at a different scale.

Kuhn's survey classifies STE as **P2 E5 N5 S1** — full natural
expressiveness, full naturalness, natural-language complexity.[^kuhn] By
that scheme SBE sits beside Plain Language and Basic English, not beside
anything formal. Two prior languages already do what §5 does — Wycliffe
EasyEnglish (two lexicon levels, plus any word "explained in separate
EasyEnglish sentences") and Ericsson English (a closed list, "but other
words can be introduced if accompanied by a definition"). The closest
working precedent is **VOA Special English**: ~1,500 core words plus
whatever a story needs, in daily use since 1959.[^kuhn]

Three differences from STE are deliberate:

| ASD-STE100 | Simplified Book English | Why |
|---|---|---|
| 875 approved words, one meaning each | ~20,800 core forms, open beyond that | A book's subject is unbounded; a maintenance manual's is not |
| One word, one part of speech | One *term* per concept; ordinary diction stays varied | Enforced synonym-poverty reads as machine prose — the thing [STYLE-AI-TELLS.md](STYLE-AI-TELLS.md) exists to prevent |
| ≤20-word procedures, ≤25-word descriptions | Length caps live in the genre profile; **variance** is required | A wall of same-length sentences is itself a tell ([STYLE.md §3](STYLE.md)) |

What SBE keeps whole is the part that actually protects readers: **necessary
jargon and unusual or restricted uses are not banned; they are explained.**
Current federal and W3C guidance make the same distinction: use a technical
term when it is the clearest name, then define it for the intended reader.
Corpus rarity alone does not prove that a reader lacks a word.[^digital-jargon]

---

## 3. Vocabulary evidence classes

| Tier | What it is | Rule |
|---|---|---|
| **Core** | About 20,800 word forms — common in at least one register of ordinary English | Free. Never reported. |
| **Open** | 45,330 further attested English words | Free. **Enforced identically to core**; the split only feeds the statistics. |
| **Recognized** | OpenGloss headwords below the corpus threshold | A real dictionary entry, but not proof that this audience knows this use. Review recurring uses in context. |
| **Declared** | Terms this book records in `book.yaml` | Not reported. This is a terminology-policy decision, not evidence that the reader was given a definition. |
| **Unlisted** | Not found in OpenGloss or the corpus tiers | Review as a domain term, coined form, name, or possible error. Introduce it if the reader needs help (§5). |

Outside the tiers:

- **Names** — capitalized words the lexicon doesn't know. STE Issue 9 would
  call these technical nouns of category 11; WCAG's reading-level criterion
  likewise measures *after* removing proper names.[^wcag] Counted, never
  reported.
- **Sensitive** — a narrow curated set of slurs and outdated ethnonyms and clinical terms that a
  frequency list will otherwise bless (`negro` reached the core tier on
  civil-rights educational material and 19th-century fiction). Demoted to
  unlisted, so a first use has to be a deliberate act — right for a
  historical quotation, wrong for careless reuse. This is the editorial
  pass a derived list cannot do for itself, and the reason STE hand-curates
  its 875 words.
- **Unapproved words and phrases** — the substitution list (§4). Reported
  whatever tier they sit in.

### Core coverage does not measure plainness

The tempting metric is "what share of my words are core?" It is worthless
as a quality signal, and the standard's own corpora prove it:

| Corpus | Core coverage | Register markers /1k |
|---|---:|---:|
| Simple English Wikipedia | 89.73% | 0.17 |
| Project Gutenberg (books, pre-1930) | 91.67% | 1.27 |
| FineWeb general web | 92.42% | 0.71 |
| FineWeb educational web | 92.49% | 0.64 |
| BookCorpusOpen (modern books) | 93.04% | 0.43 |
| CNN/DailyMail (news) | 93.23% | 0.25 |
| ELI5 (lay explanation) | 96.22% | 0.35 |
| **US federal bills** | **95.56%** | **16.71** |
| **California bills** | **96.16%** | **24.32** |

Statute text scores *higher* core coverage than five of the seven prose
corpora, because legalese is built from hyper-frequent function words
(`shall`, `under`, `section`) with a thin Latinate layer on top.
Frequency tiering cannot see the difference.

What *does* separate them is the **register-marker rate** — hits from the
error/warn substitution list plus a narrow set of replicated legal markers,
per 1,000 words. The corpus table uses the same complete word-and-phrase marker
set as the checker, measured during ingestion from revision-pinned datasets.
`such` is excluded even though it is common in federal bills: it is ordinary
prose and occurs twenty-three times less often in the California replication
set. Run `--markers` to see every component of a book's score. The rate is a
comparison signal, not a quality threshold, and policy-and-law titles can be
expected to sit above narrative books.

---

## 4. The rules

Eight rules. Each says who enforces it: **gate** (fails `--strict`), **warn**
(reported), **read** (yours to hold). Sentence-level plain-language
mechanics — one idea per sentence, active voice, base verbs, prefer the
plain word — are [STYLE.md](STYLE.md) §2–§3 and §7. SBE does not restate
them.

**R1. Do not use an unapproved word or phrase.** 67 words and 48 phrases,
each with a replacement and a grade:

<!-- sbe:generated:lists — regenerate with `uv run --group sbe scripts/check_simplified.py --emit-guide-blocks` -->

**`error`** — fails `--strict`; no defensible use in trade prose.

- 12 words: *aforementioned*, *aforesaid*, *hereby*, *herein*, *hereinafter*, *hereto*, *heretofore*, *therefrom*, *therein*, *thereof*, *thereto*, *thereunder*
- 21 phrases: *at this point in time*, *due to the fact that*, *during the course of*, *for the reason that*, *give consideration to*, *in accordance with*, *in close proximity to*, *in spite of the fact that*, *in the amount of*, *in the event that*, *is of the opinion that*, *it is incumbent upon*, *make a determination*, *pursuant to*, *set forth in*, *shall be deemed*, *subsequent to*, *under the provisions of*, *until such time as*, *with a view to*, *with reference to*

**`warn`** — usually the wrong word, sometimes exactly right.

- 15 words: *ascertain*, *commence*, *disseminate*, *expedite*, *expeditious*, *expeditiously*, *expend*, *interpose*, *notwithstanding*, *obligate*, *practicable*, *promulgate*, *remuneration*, *timely*, *whatsoever*
- 13 phrases: *and/or*, *at this time*, *by virtue of*, *for the purpose of*, *in excess of*, *in lieu of*, *in regard to*, *in the absence of*, *pertaining to*, *prior to*, *with regard to*, *with respect to*, *with the exception of*

**`idea`** — shown only with `--advisory`.

- 40 words: *additional*, *allocate*, *assist*, *attempt*, *cognizant*, *commenced*, *constitutes*, *convene*, *designate*, *discontinue*, *enumerate*, *equitable*, *expiration*, *feasible*, *finalize*, *implement*, *initiate*, *inquire*, *liaison*, *methodology*, *notify*, *obtain*, *participate*, *preclude*, *prioritize*, *proficiency*, *promulgated*, *promulgation*, *purchase*, *regarding*, *relocate*, *requirement*, *reside*, *retain*, *solicit*, *submit*, *subsequent*, *sufficient*, *terminate*, *transmit*
- 14 phrases: *a majority of*, *a number of*, *as to whether*, *has the ability to*, *in conjunction with*, *in order to*, *in terms of*, *in the near future*, *is able to*, *on a daily basis*, *on a regular basis*, *take into account*, *the fact that*, *the majority of*

Tiers: **20,794** core forms, **45,330** open, **67,632** OpenGloss-recognized, **38** sensitive; **67** word and **48** phrase substitutions (lexicon v1, built 2026-08-12).
<!-- /sbe:generated -->

The demotions are measured, not felt: an earlier draft graded fifteen more
words as errors, and across nine shipped books that grade produced nine
findings and nine false positives — quoted statutes, terms of art (*Payment
in Lieu of Taxes*), and domain verbs a subject genuinely needs
(*promulgated*, in a chapter about the Federal Register). A grade that only
fires on correct prose is a grade authors switch off.

A second context-stratified audit separated **register evidence** from
**revision advice**. Words such as *implement*, *requirement*, *submit*, and
*transmit* strongly identify institutional or technical register, yet most
sampled uses named an exact software, regulatory, filing, or network action.
Those substitutions are now `idea` prompts under `--advisory`, while
`marker_only` keeps them in the comparison score. A word can describe a
register without being wrong in the sentence where it appears.

**R2. One term per concept.** Pick the name your book uses and never use
another. Declare it in `book.yaml` with the spellings it must not take, and
the checker enforces them: *data center* stays *data center*, never
*datacenter*. Ordinary diction is the opposite — vary it, which is what
`make vocab` is for. *(gate for declared terms)*

**R3. One concept per term.** The converse, and the half STE spends four
rules on: a word doing duty for two ideas in one book is a trap even when
both uses are ordinary English. Not machine-checked; it needs you.
Terminology practice has the vocabulary for this — a **preferred term** is
the one this book uses, **admitted terms** are tolerated synonyms,
**deprecated terms** are gated. SBE's `error`/`warn`/`idea` grades are an
acceptability rating scale in exactly that sense.[^iso1087] *(read)*

**R4. Explain jargon and words used in an unusual or restricted way at first
authorial use.** Use an inline definition or point to a real glossary entry
(§5). The checker cannot determine that
semantic fact. It therefore reports recurring words outside the ordinary
corpus tiers as **review candidates**, while telling you whether OpenGloss
recognizes the form. A recognized headword can still be specialist jargon;
an absent form can still be a transparent compound. Neither result is a
violation by itself. `--advisory` includes single-use candidates, and
`--glossary` includes all candidates. *(warn / idea)*

**R5. Identify an abbreviation the first time it appears in the book.** The
usual form is "Federal Energy Regulatory Commission (FERC)." A conventional
short name that is not literally built from initials can instead be named in
plain prose ("often abbreviated TOFU") or declared in `book.yaml`. No first-use
identification is needed when everybody knows it
(the exempt list covers *AI, CEO, DNA, EU, GPS, PDF, UK, US, USB, …*) or the
book declares it. Federal guidance goes further — prefer a nickname (*the Act*, *the
committee*) and hold a document to two or three abbreviations — but that is
advice for a form, and it does not survive at book length.[^fplg-abbr] An
unanchored *the Act* two hundred pages later is unsearchable and
un-re-findable, which is worse than the acronym for a screen-reader user
and for anyone reading in sittings. At book scale: keep the abbreviation,
expand it at its first use, and give it a glossary entry. The checker accepts
ordinary initialism shapes rather than one rigid spelling of the long form:
connector words may contribute an initial (*NPOV*) or not (*ENIAC*), and a
hyphenated component may contribute one initial (*VOC*) or several (*LSTM*).
The long form must be close in visible prose; comments, citations, and URLs do
not consume that allowance. If the checker reports thirty undefined acronyms,
though, the chapter has a different problem. *(warn)*

**R6. Do not redefine a common word silently.** If a word means one thing in
ordinary English and another in your field, either choose a different word or
flag the collision on the spot. Readers revert to the common meaning within a
page.[^dickerson] The usual offenders in nonfiction are *significant*
(statistics vs. "large"), *robust*, *material*, *bias*, and *theory*.
*(read)*

**R7. Skip the Latin abbreviations.** Write *for example*, *that is*, *and
so on* — not *e.g.*, *i.e.*, *etc.* STE Issue 9 recommends against all
three for the same reason: they confuse a reader who has not met them.[^ste]
*(read)*

**R8. No `and/or`.** Write "a or b, or both".[^fplg] The same judgement
applies to any slash the reader has to interpret, though a slash in a unit,
a date, or a path is fine — that half is yours to hold. *(warn on `and/or`)*

---

## 5. Explaining and routing terms

Any word may enter a book. The substantive question is whether the intended
reader can recover the meaning used here. Only two mechanisms answer that
question.

**Route 1 — explain it in place.** Define the term where it first matters,
within a sentence or so: an em-dash clause, a parenthetical, "that is",
"which means", "known as", or a colon. Wrap the defining occurrence in
`\keyterm{...}`. It renders bold in print and as `<dfn class="keyterm">` in
EPUB, so reading tools can identify the term being defined. The surrounding
prose still has to supply the definition; markup alone conveys no meaning.

```latex
A \keyterm{gigawatt} is a billion watts: roughly one large nuclear
reactor, or the draw of a mid-sized American city.
```

The checker looks for explanation cues bound to the term, from just before it
to the end of the following sentence, and stops at a paragraph break.

> Chips are made by *fabs* — the fabrication plants that turn wafers into
> processors — and almost all of the advanced ones sit in two countries.

**A gloss must be built from words the reader already has.** An explanation
leaning on two more uncommon candidates has moved the problem, not solved it.
Both prior languages that shipped this door required the gloss itself to be
in the controlled vocabulary,[^kuhn] and the checker enforces a weak version:
a gloss that introduces more than one new recognized-or-unlisted word does not suppress
the warning.

**Route 2 — provide a real glossary definition.** This is useful when an
inline explanation would damage a scene or when the term recurs throughout the
book. The published book must contain the definition and a usable way to reach
it. `--glossary` only emits a draft JSON worklist; it does not create, link, or
publish a glossary, and therefore does not satisfy R4 by itself.

Several checker controls route editorial decisions but do **not** explain
anything to a reader:

- `\term{...}` names or styles a preferred term. It is not a definition.
- `terms:` in `book.yaml` records the preferred spelling and deprecated
  spellings. It suppresses the lexical candidate because the author has made
  an explicit terminology decision; it is not reader evidence.
- `allow:` and `ignore:` record book-wide decisions that a form is ordinary or
  deliberately retained. `% sbe-ok:` records the same decision for one
  occurrence. These prevent repeated tooling arguments; they do not make the
  prose clearer.
- Quoted material is not checked as authorial diction. If the author uses the
  term later in exposition, that authorial use must stand on its own.

Sometimes the word *is* the scene: a character's jargon or a concrete
particular whose strangeness does the work. [STYLE-CRAFT.md](STYLE-CRAFT.md)
§2 asks for exactly these—*crossarm*, *ductwork*, *samovar*—and an inline
gloss can kill the image. Leave it unglossed in the scene, define it in a real
glossary if the audience needs that support, and record the editorial decision
so the same candidate does not return every round:

```yaml
ignore: ["crossarm", "ductwork", "samovar"]   # retained deliberately
```

A term of art can likewise keep its exact diction. Put the decision on the
line when it applies only there:

```latex
Public Act 198 permits an abatement only if construction of the facility
commenced no earlier than six months before the filing.  % sbe-ok: commenced — statutory language, the argument turns on it
```

Name the words you are excusing. The comment covers its own line and the
one after it, and silences only findings that quote a word you named —
naming nothing silences everything on those lines, which is why
`--suppressions` prints the scope beside the reason. A pragma with no
reason at all is itself a finding. Remember that this house writes one
paragraph per line, so "the line" is usually the whole paragraph: re-read
it before adding a pragma, and again after any revision that touches it.

Use `ignore:` in `book.yaml` when a word is right *everywhere*; use this
when it is right *here*.

**Concept load.** [STYLE.md](STYLE.md) §7 gives 5–7 new terms per chapter as a
house pacing target, not a vocabulary law. A long list is a reason to inspect
the chapter's conceptual load and scaffolding; it is not evidence that a fixed
number of terms must be deleted.

The checker deliberately does not equate `\keyterm` or `\term` with an
explanation. A marked term without recognizable defining context remains a
candidate. This matches the reader-facing rule instead of treating a visual
style as comprehension.

---

## 6. The dictionary

`scripts/data/simplified_english/lexicon.json`, rebuilt by
`make simplified-lexicon`. Word tiers are derived; policy is hand-written.
The full derivation, thresholds, sensitivity table and known statistical
weaknesses are in
[architecture/simplified-english.md](../architecture/simplified-english.md).
In brief: seven prose corpora spanning ~258M tokens (books old and modern,
news, two webs, Simple English Wikipedia, lay explanation) decide what is
ordinary; OpenGloss supplies direct dictionary recognition and morphology;
two legislatures supply the
register contrast. Only aggregate counts are stored, never text.

`--explain` accepts either a word or an exact multiword phrase. For a phrase it
answers the literal OpenGloss membership question, but phrase membership is
not treated as audience familiarity or automatic approval.

### How the substitution list was graded

Honestly: **by editorial judgement**, seeded from the plainlanguage.gov
list (US government work, public domain).[^fplg] An earlier draft of this
guide claimed a measured "register index" did the grading. It did not — the
statistic separates the shipped `error` entries from the rest at AUC 0.575,
which is barely better than a coin flip, and eleven error-grade words score
below the weakest measured one. The number was decoration and is now
labelled as such.

Two register statistics *are* reported per entry, because they rank
candidates for review:

- **`register_lift`** — the rate in legislative text over the rate in
  prose, Jeffreys-smoothed, taken as the geometric mean of a federal and a
  Californian estimate so a word must behave the same way in two
  legislatures. *pursuant to* and *promulgate* clear 100×; *however* is
  eighteen times *less* common in statutes than in prose, which is why the
  plainlanguage.gov list flags it for forms and a book keeps it.
- **`doc_spread`** — the share of federal bills using the word at all. Real
  boilerplate is everywhere; a topic word is bursty. Measured against a
  labelled set it beats the lift ratio (AUC 0.811 vs 0.762).

Neither is good enough to gate a build. Both are good enough to sort a
worklist. Entries marked `source: judgment` carry no measurement at all —
argue with those first.

---

## 7. Per-book configuration

```yaml
simplified_english:
  enabled: true
  terms:
    - term: "callout"
    - {term: "data center", not: ["datacenter", "data-center"]}
  abbreviations: ["ADR", "ISBN", "FERC"]   # bare use allowed
  names: ["LEXIS", "RANDU"]                 # official all-cap names
  ignore: ["enumerate", "with respect to"] # words/phrases this book keeps
  allow: []                                # extra core words
  deny: []                                 # extra error-grade bans
  thresholds:
    unintroduced: warn        # warn | error | off
    undefined_abbreviation: warn
    unintroduced_min_uses: 2 # recurring terms warn; --advisory shows singletons
    gloss_window: 400         # characters searched for a gloss
    max_findings_per_file: 40
```

`ignore:` takes phrases as well as words, and is the STE technical-verb
allowance in miniature: a computability book keeps *enumerate*, a
quantitative book keeps *with respect to*, an energy book keeps
*interconnection*. Use it, and say why in a comment. Note that declaring a
multi-word term also declares each of its words.

---

## 8. Running it, and what to do with the output

```bash
make simplified                                  # the run
uv run --group sbe scripts/check_simplified.py --terms       # work list
uv run --group sbe scripts/check_simplified.py --emit-config # book.yaml block
uv run --group sbe scripts/check_simplified.py --stats       # tier coverage
uv run --group sbe scripts/check_simplified.py --markers     # register score
uv run --group sbe scripts/check_simplified.py --advisory    # + idea/single-use
uv run --group sbe scripts/check_simplified.py --glossary    # draft JSON glossary
uv run --group sbe scripts/check_simplified.py --suppressions # audit escapes
uv run --group sbe scripts/check_simplified.py --explain gigawatt promulgate
uv run --group sbe scripts/check_simplified.py --root ../other-book
make simplified-lexicon                          # rebuild the dictionary
make test-simplified                             # checker regression tests
make calibrate-simplified                        # nine held-out book scores
```
The calibration scorecard also prints term, abbreviation, substitution, and
other finding queues per book; use `--format json` when comparing runs.

Chapters only by default (`--all` adds front and back matter, which are
metadata and will light up). Only `error` findings fail; `--strict` fails on
warnings too. TexSoup parsing plus the vocabulary passes take several seconds
for a 100k-word book; the nine-book calibration is the coarse behavior check.

### Working a term list

The default list prioritizes recurring candidates; `--advisory` includes
single-use forms, and `--glossary` includes every candidate. The queue
intentionally mixes genuine technical terms with transparent compounds,
concrete particulars, and possible mistakes. Work it in this order:

1. **`--terms`** sorts by how often the term is used. A term used twenty
   times is a concept the book is built on. Use `--advisory --terms` when
   you deliberately want the single-use word-choice sweep.
2. **Read the OpenGloss result.** "Recognized" means the form is present in
   the dictionary, not that a general reader knows the concept. "Unlisted"
   means OpenGloss does not contain the form, not that the form is wrong.
   Decide from the sentence and the intended reader.
3. **Separate inflection from derivation.** The checker uses maintained
   libraries for ordinary tense/number families, including unknown technical
   plurals when the candidate round-trips. It deliberately does not infer that
   `verify` makes `verifier` familiar or that `satisfy` makes
   `unsatisfiable` familiar. A derived concept can still need an explanation;
   decide from the reader and context instead of deleting it mechanically.
4. **Decide the concrete particulars.** *Crossarm*, *ductwork*, *samovar* —
   often retain them in the scene and route any needed explanation to the
   published glossary. Do not gloss the scene to death.
5. **What is left is the real list.** Explain what the intended reader needs
   and record the deliberate exceptions.
6. **`--emit-config`** writes a `terms:`/`abbreviations:` block from the
   current findings. It is a decision worksheet, not an allow-list to paste
   wholesale. Keep only entries for which you made an explicit spelling,
   explanation, or exception decision.

### At the desk

| You are about to write | Do |
|---|---|
| a word or acronym you suspect | `--explain word APIs`; reports vocabulary tier or acronym policy |
| a term the reader won't have | `\keyterm{...}`, gloss in the same sentence |
| an acronym | identify once: usually `Full Name (ABBR)`, or explicit prose such as "abbreviated ABBR" |
| a quoted statute or contract | `\begin{quotation}` or `\begin{archive}` (both exempt) |
| a term of art the argument turns on | keep the exact term; explain it if the audience needs help; use `% sbe-ok:` to record a local exception |
| a concrete particular | write it; consider a glossary definition; record the decision with `ignore:` |
| the same concept twice | one name, declared with its `not:` spellings |

**Before review:** clean of *errors*. Warnings are a reading list, not a
punch list; a chapter with six unintroduced terms and six good reasons is
finished.

---

## 9. What this does not check

One fault, one gate. Everything else already has an owner:

| Concern | Owner |
|---|---|
| Sentence and paragraph length | `check_style.py` (`style-targets`) |
| AI tells, slop words, machine artifacts | `check_style.py` (STYLE.md, STYLE-AI-TELLS.md) |
| Repetition, duplicate sentences, n-gram echo | `check_prose.py` |
| Latinate share, nominalization, hedges | `register_report.py` (`make craft`) |
| Vocabulary variety and overuse | `vocab_variety.py` (`make vocab`) |
| Burstiness, lexical diversity | `prose_metrics.py` (`make metrics`) |
| EPUB structure, navigation, metadata, image alt text | `make epub-a11y` (Ace by DAISY) |
| Reading level | **nobody** — see below |

### There is no owner for reading level, and Ace is not one

Ace by DAISY runs axe-core plus a fixed list of EPUB rules — metadata
completeness, TOC order, `epub:lang`, page-list integrity, image alt text.
Not one of them looks at a word.[^ace] Nothing in this repo measures
reading level, and no green gate should be read as if something did.

What SBE lines up with is not WCAG 3.1.5 but the two criteria beside it:
**SC 3.1.3 Unusual Words** — a mechanism for identifying definitions of
words used in an unusual or restricted way, including jargon — and **SC
3.1.4 Abbreviations**, a mechanism for identifying expanded forms.[^wcag]
R4 is 3.1.3; R5 is 3.1.4. Their sufficient techniques are inline
definitions (G112), the `dfn` element (H54), and—for *every* occurrence,
not just the first—a glossary (G62). SBE's `\keyterm` now emits `dfn`, but
conformance still depends on the surrounding definition or an actual
published glossary. The `--glossary` JSON worklist is authoring assistance,
not a conformance mechanism.

**And the largest lever is not here at all.** Martínez, Mollica and Gibson
compared the candidate causes of processing difficulty across ~10M words
and two experiments: **center-embedded clauses inhibited recall more than
low-frequency jargon did**, and the effect held even for experienced
readers. Their conclusion is that difficulty comes from working-memory load
imposed by long-distance syntactic dependencies — poor writing — rather
than from vocabulary.[^martinez] SBE reviews words. If you run it without
`check_style.py` and `make craft`, you have optimised the smaller lever and
called it done.

The fair statement of SBE's benefit is the one the controlled-language
evidence actually supports: Boeing's own trials found Simplified English
improved comprehension **for the harder procedure only**, with non-native
readers gaining most, and **no reading-speed effect at all**.[^holmback]
Expect that. It will not make an easy chapter easier.

---

## 10. Known limits

- **No summary percentage is a quality score** (§3). Core coverage measures
  corpus overlap; the register-marker rate compares register. Neither means
  "this prose is plain," and neither is a release threshold.
- **The core list is a frequency artifact.** A word can be common and hard
  (*notwithstanding*) or rare and easy (*ductwork*). Frequency is a proxy
  for familiarity, not a measure of difficulty.
- **Coverage is not comprehension.** Nation's novel study puts 2,000 word
  families at ~87.8% coverage and 9,000 families at ~98.2%; the
  comprehension thresholds in that literature are 95% (minimal) and 98%
  (optimal).[^nation] SBE's core sits well below those on purpose — it is a
  drafting prompt, not a reader model. Do not read 92% as a comprehension
  figure.
- **The list moves when the sample moves.** Redrawing the reference sample
  at the same size shifts roughly 7% of the core list; about one core word
  in eight sits close enough to a threshold to be a coin flip. Corpus
  samples are the first N documents or tokens from revision-pinned streaming
  datasets; the artifact records both revisions and aggregate-cache digests.
- **Names are detected by capitalization.** A capitalized word the lexicon
  doesn't know is treated as a name, so a genuinely new lowercase term that
  only ever appears sentence-initially is missed.
- **Abbreviations are 3–7 capital letters**, minus roman numerals, ordinary
  words in caps, and anything adjacent to a capitalized name. A lowercase
  plural or possessive ending is normalized (`APIs` → `API`, `NATO's` →
  `NATO`). An uppercase filename suffix after a dot (`HOSTS.TXT`) is not an
  abbreviation. Expansion matching keeps the first-use rule: a later long
  form does not excuse an earlier bare use. A reverse expansion must be in
  the same sentence; a preceding long form may be within 80 visible words,
  and a following parenthetical or appositive within 25. Company and product
  names in capitals still slip through — list their official spelling under
  `simplified_english.names`.
- **Configuration is fail-fast, not extensible.** Unknown keys under
  `simplified_english` or its `thresholds` mapping are errors; this prevents a
  spelling mistake from silently disabling a policy decision.
- **The gloss test is a cue test.** It cannot read; it can only see that an
  explanation-shaped construction sits within reach of the term. It errs in
  both directions: an em dash, colon or parenthesis inside 90 characters
  counts as an explanation whether or not it is one, and a definition that
  puts the explanation *before* the term ("a formula true in at least one
  row is *satisfiable*") is only caught by the strong lexical cues. Treat a
  gloss warning as "the checker did not recognise your gloss", not "you
  did not gloss".
- **Lemmatization is inflectional, not derivational.** Simplemma handles known
  English forms; `inflect` is a guarded fallback for unknown plurals. Imported,
  irregular, and domain-specific forms can still be misanalysed, which is why
  accepted fallback singulars must pluralize back to the observed word.
- **The running checker is word-centered.** `--explain "machine learning"`
  can report an exact OpenGloss phrase entry, but recurring-term collection
  still evaluates word tokens and hyphenated compounds. OpenGloss phrase
  membership is lookup evidence, not a silent exemption for every component.
- **LaTeX structure is parsed, but semantics remain a contract.** TexSoup owns
  command/environment boundaries, verbatim listing names are discovered from
  preamble declarations, and opaque keys/options are excluded. Unknown commands
  with arguments are treated as transparent presentation wrappers so older
  books retain visible prose; a custom command whose argument is actually
  metadata must be added to the shared opaque-command set.
- **This is not an accessibility conformance tool.** Easy-to-Read and Easy
  Language (Inclusion Europe; DIN SPEC 33429) are a different discipline for
  a different reader, and should not be confused with plain language.

---

## 11. Sources

[^ste]: ASD-STE100 Simplified Technical English, Issue 9 (January 2025),
maintained by the Simplified Technical English Maintenance Group; free at
<https://www.asd-ste100.org/>. 53 writing rules; Part 2 lists 875 approved
and 1,274 unapproved words. Rule 1.5 gives 22 categories of *technical
noun* — Issue 9 retired the older term *technical name* — and Rule 1.12
gives 4 categories of technical verb. GR-6 advises against *e.g./i.e./etc.*

[^kuhn]: Tobias Kuhn, "A Survey and Classification of Controlled Natural
Languages," *Computational Linguistics* 40(1), 2014, 121–170.
<https://aclanthology.org/J14-1005.pdf>. Source of the PENS classification
(STE = P2 E5 N5 S1), of VOA Special English's history, and of the Wycliffe
EasyEnglish and Ericsson English precedents for admitting a word with a
definition.

[^iso]: ISO 24495-1:2023, *Plain language — Part 1: Governing principles and
guidelines*. Four principles: readers get what they need (relevant), can
easily find it (findable), understand it (understandable), and use it
(usable). Clause 5.1.2 puts identifying the reader first; Principle 4 is
operationalised as evaluation *with readers*. Its scope names controlled
languages explicitly. The three-verb "find / understand / use" formula is
the International Plain Language Federation's definition, which the standard
quotes. Part 2 (legal communication) followed in 2025.

[^fplg]: *Federal Plain Language Guidelines* (2011) and the plainlanguage.gov
word-substitution list — 230 pairs, US government work, public domain, now
archived at <https://github.com/GSA/plainlanguage.gov> (the live site
redirects to digital.gov).

[^fplg-abbr]: Same source, "Minimize abbreviations": define at first use,
skip the definition for abbreviations everyone knows, prefer a plain-English
nickname, and hold a document to two or three.

[^digital-jargon]: Digital.gov, "Avoid jargon," current federal plain-language
guidance: necessary technical terms are not prohibited; use the clearest
subject term and define it where it appears.
<https://digital.gov/guides/plain-language/principles/avoid-jargon>

[^nation]: I.S.P. Nation, "How Large a Vocabulary Is Needed for Reading and
Listening?", *Canadian Modern Language Review* 63(1), 2006, 59–82; with
Laufer & Ravenhorst-Kalovski (2010) on the 95%/98% coverage thresholds.

[^martinez]: Eric Martínez, Francis Mollica & Edward Gibson, "Poor writing,
not specialized concepts, drives processing difficulty in legal language,"
*Cognition* 224 (2022), 105070.

[^holmback]: Holmback, Shubert & Spyridakis, "Issues in Conducting Empirical
Evaluations of Controlled Languages," CLAW '96 — 130 subjects on real Boeing
procedures; gains on the complex procedure only, largest for non-native
readers, no speed effect. Chervak et al. (1996) replicated the pattern with
working technicians.

[^iso1087]: ISO 1087:2019 and ISO 704:2022 supply the terminology-management
vocabulary — preferred / admitted / deprecated terms on an acceptability
rating scale — that R3 borrows. Issue 9 of ASD-STE100 normatively references
both.

[^wcag]: WCAG 2.2 SC 3.1.5 *Reading Level* (AAA) measures "after removal of
proper names and titles," and asks for supplemental content rather than
simplification. The Working Group's own note concedes reading level was
adopted because they "could not find a way to test" clear language directly.

[^dickerson]: Reed Dickerson, *Fundamentals of Legal Drafting* (2nd ed.,
1986), on not defining a word away from its ordinary sense — quoted in the
Federal Plain Language Guidelines' "Minimize definitions".
