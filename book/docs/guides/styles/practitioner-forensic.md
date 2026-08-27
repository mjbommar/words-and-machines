# Style Profile: Practitioner Forensic

Layered over [STYLE.md](../STYLE.md) — select with `style.profile:
practitioner-forensic` in `book.yaml`. For books that teach professional
judgment *about rules*: accounting and finance curricula, forensic-analysis
handbooks, credentialed-professional textbooks. The recurring move is separating
what a rule says from what is economically true.

Portfolio exemplars, each for one thing: **Buffett**, Berkshire Chairman's
Letters, the 1983 appendix "Goodwill and its Amortization: The Rules and The
Realities" and the 1986 owner-earnings appendix — the arc and the paired
columns. **Graham and McGolrick**, *The Interpretation of Financial Statements*
(1955 revision) — rhythm, definitional method, three-tier case architecture.

**Schilit**, in the CFA Institute *Enterprising Investor* interview "The
Sherlock Holmes of Accounting" (Usman Hayat, 4 March 2014), read in full — the
register's thesis, the two questions, and the anti-cynicism fences.
**Damodaran**, *Musings on Markets* — owned uncertainty, and a measured
cautionary example of clause creep.

Scope note, because it bounds what the case-method guidance rests on: *Financial
Shenanigans* itself has **not** been read. The interview has. Claims about the
book's preface, its chapter structure, and its internal identifier scheme were
withdrawn as unsourced and are not restored here.

## Reader and register

A competent junior who can already do the bookkeeping and cannot yet decide what
a number means. Not frightened, not on a deadline. At some point they will be
asked to defend a judgment about a figure to someone senior.

**The second-chair test.** Could you say this with the filing open on the table
between you and one junior colleague, your finger on a line, expecting to be
interrupted? The senior voice may be exact, skeptical, or unimpressed. It may
not perform.

Rewrite if it sounds like a codification paraphrased into sentences, an investor
letter written to be quoted, a fraud documentary voiceover, a cram deck, or a
compliance memo.

The subject is the gap Schilit names, and his statement of it is the best
available:

> "The horrendous accounting fraud — what we saw in Enron, Tyco, and WorldCom —
> is relatively rare. It breaks the law and violates accounting standards.
> Accounting manipulation that I like to call accounting shenanigans is
> different. It tends to be done within the letter of the law and technical
> interpretations of accounting standards but present a misleading picture of the
> economic performance of the company. Sadly, this is quite common. I deal with
> accounting shenanigans. This is my world. There are no smoking guns here."

A book in this register exists to make a reader able to see that gap without
being told where to look.

## Person and tense

Buffett's first person does **not** transfer, and the reason is measurable. His
"we" runs 12.2 per 1,000 words in the 1983 appendix and is not a stance but
*evidence of standing*: he wrote the check, then had to book the charge, which is
why he may say the charge is not a cost. A textbook has written no checks, so an
editorial "we" claiming the same authority is a forgery of standing. Graham
resolves it the other way — first person effectively zero, the reader called
"the investor" in the third person — and earns trust by disappearing.

- **The company is the grammatical subject.** Where Buffett writes "we paid
  $25 million," write "Blue Chip Stamps paid $25 million in 1972." The reader can
  then go check the filing.
- **"We" only as author-and-reader on the same page.** "We have not yet booked
  the settlement." Never "in our view," never "our balance sheet."
- **"You" at exactly two moments**: when a prediction is requested before a
  reveal, and when a judgment is handed over.
- **"I" is permitted, rare, and reserved for a method choice the author actually
  made, or a change of mind.** One or two per chapter is enough, and it is the
  cheapest available signal that judgment is being taught rather than recited.
- **Present for rules in force, past for what a company did and reported**, with
  the date attached. The register's signature sentence carries both and looks
  like a tense error, so license it explicitly: "The standard requires the
  premium to be pushed into goodwill, and Blue Chip pushed $17 million there in
  1972."
- **The counterfactual past is first-class.** "Had Berkshire not bought it, the
  company would have reported $40.2 million." This is the only grammar available
  for a control case, and reviewers must not flag it as evasion.

## Rhythm

Measured from primary texts, not asserted.

| | Buffett 1983 appendix | Graham 1955 Part I |
|---|---:|---:|
| Words | 2,576 | 12,511 |
| Mean sentence | 21.4 | 28.8 |
| Median | 20 | 25.0 |
| p90 | 34 | 51 |
| Maximum | 49 | — |
| Under 15 words | ~20% | 17% |
| Over 40 words | ~5% | 19% |
| Sentence-length cv | 0.48–0.52 | 0.58 |
| Semicolons | **0** | 1.6 per 1,000 |
| Latinate share | 0.365 | 0.413 |

- **Average 19–27 words. No error ceiling; warning at 46.** Note that 46 is a
  deliberate tightening rather than a figure fitted to the exemplars: Buffett's
  teaching appendix tops out at 49, and Graham's p90 is **51**, with **19%** of
  his sentences over 40 words. A ceiling of 46 will warn on roughly a tenth of
  Graham. That is defensible — 1955 print prose runs longer than a 2026 textbook
  should — but choose it knowingly.
- **Paragraphs 2–7 sentences.** The 1983 appendix measures 1 to 6, mean 3.2
  across 38 paragraphs.
- **Length does not come from deep subordination.** Buffett runs 0.80
  subordinators per sentence and 42% of his sentences have none. His long
  sentences are built from coordination and from **appositive glosses** set off
  by dashes or parentheses. Real length and real qualification are available
  without hypotaxis.
- **Do not prescribe alternation.** Length is set by how many conditions the
  claim carries. The 1983 appendix passes the house `burstiness_cv_min` of 0.45
  at 0.48–0.52 with no rhythm rule applied at all.
- **No Flesch-Kincaid target, deliberately.** FK on "amortization of the excess
  of cost over the fair value of net assets acquired" measures the domain's
  vocabulary, not the explanation's difficulty. Declare the omission in
  `SPIRIT.md`.
- Diagnostic in place of a short-sentence rule: Graham's 17% of sentences under
  15 words are almost all **definitions**. A chapter with no short sentences has
  probably stopped defining things.

## Structural shape: the rule-versus-reality arc

Buffett runs this eight-beat sequence in three independent places within his own
letters. Beat 7 is independently corroborated across three exemplars in three
different registers, which is why it is promoted to a required beat below; the
full eight-beat ordering is Buffett's and has not been tested against a second
author.

1. **Fence the term before arguing about it.** Say which sense you mean, which
   you exclude, and give a disconfirming pair.
2. **State the rule in the rule's own voice, completely, with thresholds and
   dates.** This is where the passive belongs, and the shift is measurable: in
   the 1983 appendix's rule paragraphs, be-plus-participle runs **27.4 per 1,000
   words**; in the economics paragraphs, **5.3**. The grammar tells the reader
   which voice is speaking, with no callout box.
3. **Close the rule section with an audible click, then declare the pivot.**
4. **Run the rule on one real company's real numbers until the reader could do
   it unaided**, labelling the general principle in the same paragraph as the
   figures that produced it.
5. **The pivot is one sentence, hinged on "but," with the same noun on both
   sides.** Not a flourish.
6. **Measure the gap with the same company's later figures.**
7. **Concede the standard-setter's problem in the same breath as the criticism.
   This beat is required, not optional** — it is the best-evidenced move in the
   profile, appearing in three exemplars in three registers: Buffett's standing
   disclaimer that he has no better accounting system to suggest, Graham's
   refusal to discard book value after demolishing it as a liquidation measure,
   and Schilit's two separate fences, one on auditors ("There is no reason to
   assume that auditors are not good decent people trying very hard to do their
   job well") and one on executives ("I don't think business executives are
   crooks either. There is tremendous pressure from the market on short term
   results"). This is the beat that keeps the rule from sounding arbitrary,
   and it is the intellectual core of the profile: **a rule sounds arbitrary
   only when its constraint is unstated.** Name what the rule is trying to make
   comparable and what forbids a better one. "Forty years is arbitrary" is
   defensible; "the requirement to pick some period is not, because a standard
   letting each firm choose would destroy cross-firm comparability, and no
   auditor can verify a forecast of a franchise's decay" is a sentence a learner
   can carry to a rule you never covered. "The rule is stupid" is not.
8. **Fence the exception before the reader over-generalizes it.** The reader's
   next mistake is generalizing your exception; fencing it now is cheaper than
   un-teaching it later.

Graham compresses the whole arc into a two-word hinge worth stealing outright:
**"In theory … But."**

## How real-company cases teach

An illustration shows that a thing happened. A case teaches a mechanism when the
reader can re-derive the disputed number from figures printed on the page and can
see which single input would change the answer.

- **The re-derivation test.** Six numbers carry the entire See's argument. If a
  reader cannot recompute your conclusion from the page, you wrote an anecdote.
- **The paired-column identity.** Two presentations of one business, the
  identity withheld for a beat, the delta narrated between them. Buffett does it
  with two columns of Scott Fetzer earnings, the identity of the business
  withheld for two paragraphs. Independently corroborated, so it stands as a
  register invariant rather than one writer's device. **Lead with the stronger
  pedagogical variant, which is Schilit's:** a manufacturer reported sales down
  1% and operating profit up 38%, which read as a strong result after the 2011
  tsunami; in reality sales were down 21% and there was a large loss, and the
  company disclosed the comparison in a footnote. Schilit's finding is the part
  that teaches: "I looked at all the sell-side research reports on the company,
  and none had figured it out. … They probably overlooked the footnote." Here the
  second column exists in the filing and the reader has to build it, which is a
  harder and better exercise than being handed two columns already drawn.
- **The one-variable twin.** A hypothetical is permitted here — against
  STYLE-AI-TELLS §2.7 — only when the real case supplies all its numbers and the
  twin varies exactly one input. It is then a *control*, not an illustration.
- **Three tiers of case, not one company per chapter.** A population benchmark
  for norms, a recurring named company for presentation, and one end-to-end
  walkthrough. Buffett's accumulating version revisits See's years later as the
  *test* of the earlier chapter's prediction. Accumulation is the only thing a
  case does that an illustration cannot; a new company every chapter cannot
  accumulate.
- **Cluster questions at the pivot; do not sprinkle them.** Buffett's
  corpus-wide question rate is 1.1 per 1,000 words and **6.7 at the
  owner-earnings pivot** — a six-fold local spike, four questions in a row, none
  answered in the next sentence.
- **The test that keeps a case from being trivia**: to what extent did the
  accounting choice hide a problem in the business? A case that answers only
  "someone got caught" is a news item.

## Craft moves

- **The mouthful, then the handle.** Quote the codification's full official label
  once, in quotation marks, then license a short name. The reader can find the
  term in the standard and still follow your prose.
- **The grammar switch.** Passive while the rule acts on the numbers; active with
  a named company as subject the moment economics is discussed.
- **Scare-quoting the term of art.** Marks a word as the rule's word rather than
  the writer's, which is the exact distinction this register teaches — and does
  it in punctuation instead of typography. Buffett quotes 15 terms in 2,576 words
  and uses zero bold or italic markup in the entire letter.
- **The two questions**, Schilit's, and the strongest craft move in the profile:
  "Once you have found it, the questions to ask are not 'Is it legal?' and 'Is it
  permissible?' The questions to ask are 'Why?' and 'Why now?'" *Why it works:*
  the compliance question is answerable from the standard and therefore teaches
  nothing; motive and timing are answerable only by judgment.
- **The no-allegation clarifier**, the model for introducing any real company
  that got something wrong: "in any example I give, I make no assertion that the
  company concerned is doing anything illegal or willful to violate accounting
  standards. I am just sharing my analysis without alleging wrongdoing." *Why it
  works:* it lets a case teach a mechanism without the book making a legal claim
  it cannot support.
- **The standard-setter's constraint.** Converts "this rule is wrong" into "this
  rule is a compromise with a stated price."
- **The fence after the exception.**
- **The numbered line item.** Number the statement lines, then write every ratio
  twice, once symbolically and once in dollars. For a graph-native curriculum
  this is a line-item dependency graph rendered in prose.

If cutting, keep the grammar switch, the standard-setter's constraint, and the
fence. The register cannot be written without those three.

## Watch for

- **Cynicism about standards**, the characteristic collapse. Once you have shown
  one rule diverging from economics, contempt for the standard-setter is the
  cheapest next move, and Buffett takes it. Entertaining, and it teaches nothing
  about reading a standard. Test: after every divergence, can the reader state
  what the rule was protecting?
- **Folksiness.** Works for a man who owns the company and writes once a year to
  people who chose to read him. In a textbook the same lines are an instructor
  performing charm at a captive audience.
- **Aphoristic closers.** Both principal exemplars break this. Buffett's teaching
  appendix ends 28.1% of sentences on a punch cadence; his polemical
  owner-earnings riff, 34.8%. Drifting from teaching into letter-writing is
  measurable. Usable test: **the closer must name something from the page.**
- **Cases that entertain without teaching.** Strip the company name and the
  year. Does a mechanism remain? If the only content is that someone got caught,
  it is a news item.
- **Rule-recitation drift**, the opposite failure. The diagnostic is Latinate
  share, and it is load-bearing: Buffett's teaching appendix measures 0.365 and
  Graham 0.413, both *below* the house ceiling, despite being entirely about
  purchase accounting. Past 0.45 the prose has stopped explaining and started
  reciting.
- **The reorganization effect.** Lifting a practitioner's argument into
  curriculum strips the grammar that made it teachable. Measured on one
  editor's pedagogical reorganization of Buffett: nominalizations rise from 30.1
  to 40.0 per 1,000 words, first person falls from 12.2 to 0.0, contractions
  from 4.1 to 0.4. The themes survive; the sentences that made them teachable do
  not. Budget for rewriting connective tissue in the register, not just
  re-heading it.
- **Clause creep**, measured across one author's own posts over fifteen years:

  | Post | Mean | Median | Under 15 words | Over 40 words |
  |---|---:|---:|---:|---:|
  | 2010, accounting inconsistencies | 19.1 | 15 | 49% | 5% |
  | 2022, lease accounting | 35.9 | 33.5 | 11% | 20% |
  | 2023, a single-company valuation | 38.4 | 35 | 6% | 30% |

  The median sentence more than doubled and the share under 15 words collapsed
  from 49% to 6%. The 2010 post sits inside this profile's band and reads as
  teaching; the 2023 post sits far outside it and reads as being talked at. Audit
  late-drafted chapters against early ones, and note that this is the argument for
  holding `sentence_avg_hi` at 27 rather than relaxing it.
- **The named antagonist.** Personifying the rule-writers so they can be argued
  with — "Until accountants came to their senses in 2019" — is powerful and is
  where the sneer enters. Test: after every divergence, can the reader state what
  the rule was protecting?
- **Hindsight certainty.** State what was knowable from the filing on its
  publication date, separately from what the restatement later showed.

## Three absolute word rules

No exceptions outside direct quotation. All three are already Buffett's practice:
every monetary amount in the 1983 appendix is a numeral, and all four uses of
"worth" are literal valuation with a number attached.

1. **"Worth" is reserved for literal financial value.**
2. **Monetary amounts and measured quantities are numerals.**
3. **A reader meets a person, never an idea.**

## Lint deltas

Every threshold is set from a measurement, given in the comment. Ceilings were
chosen so Buffett's *teaching* appendix and Graham's Part I pass, and Buffett's
*polemical* passage fails.

```style-targets
tell_budget: 2
sentence_avg_lo: 19
sentence_avg_hi: 27
sentence_hard_max: 46             # warning only, and a deliberate tightening: Buffett tops out at 49, Graham's p90 is 51 with 19% over 40 words
paragraph_sents_lo: 2
paragraph_sents_hi: 7
burstiness_cv_min: 0.45           # house floor holds: the 1983 appendix measures 0.48-0.52 with no length rule applied
para_cv_min: 0.30                 # measured 0.41
# register_report.py
hedge_per_1000_max: 28.0          # "about $8 million" is STYLE section 6's rounding rule, not apology; measured 26.0 Buffett, 24.9 Graham
booster_per_1000_max: 6.0         # the numbers are the emphasis. Teaching appendix 4.9 passes; owner-earnings polemic 8.9 fails
attitude_per_1000_max: 4.0        # the anti-folksiness gate: Buffett 0.4, Graham 0.1
nominalization_per_1000_max: 36.0 # Buffett 30.1; Graham's 39.3 fails on purpose, since his agentless nominal style is the part not to take
latinate_ratio_max: 0.45          # UNCHANGED and load-bearing: over 0.45 means the codification is being recited
contraction_per_1000_min: 1.5     # catches the codification voice; Graham's 0.0 fails deliberately
cadence_share_max: 0.34           # the anti-aphorism gate: teaching appendix 28.1%, Graham 31.6%, polemic 34.8%
cadence_run_max: 4.0
uniform_para_pct_max: 25.0        # measured 11.1%, 0.0%, 0.0%
```

`cadence_share_max: 0.34` leaves Graham only 2.4 points of headroom, so
`rhythm_audit --strict` should stay out of the release gate for this profile.

**Carve-outs from the base guides, each narrow:**

- **Rhetorical questions** (STYLE-AI-TELLS §1.9): not a raised cap but a
  *cluster budget* — one cluster of up to four questions per chapter, at the
  rule-versus-reality pivot, none answered in the following sentence.
- **Em dashes** (STYLE §5, one per paragraph): raise to two, for the appositive
  gloss only. Seven of 38 paragraphs in the 1983 appendix carry two; three still
  fails.
- **"Not X but Y"** (§1.5): permitted when both X and Y are named, checkable
  quantities, because it is then a definitional correction.
- **Hypotheticals** (§2.7): stands, with the one-variable-twin carve-out.

```banned-words-add
gimmick
gimmicks
chicanery
egregious
savvy
optics
bean-counter
whitewash
takeaway
takeaways
learnings
```

```banned-phrases-add
cooking the books
smoke and mirrors
creative accounting
the numbers don't lie
cash is king
follow the money
the market saw through it
here's the kicker
let that sink in
accounting is not an exact science
as any analyst knows
in my years of
three key takeaways
at a high level
double-click on
worth noting
it is worth noting
well worth
```

Keep `significant`, `robust`, `framework`, and `optimize` as warning-only
watch-list entries; each has a literal domain sense this register needs. If this
profile ships into a repository that already carries a `domain-exceptions` block
for financial leverage and significant influence, reuse that rather than
removing base bans.

One rule needs a mechanism the profile format cannot provide. "A reader meets a
person, never an idea" is not expressible in a banned-phrase list in its
inflected forms, and belongs as a candidate addition to STYLE-AI-TELLS' shared
`tell-patterns` block:

```
\b(meet|meets|introduc\w+\s+(you\s+)?to)\s+(the\s+)?(concept|idea|principle|framework|standard|rule|ratio|equation|doctrine)\b
```

`move_annotator.py` will show `concession` and `contrast` as the dominant
families here. A long concession run is the form working, not monotony.
