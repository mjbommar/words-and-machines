# Simplified Book English calibration — 2026-08-12

This is a compact engineering check across nine sibling books. It is not a
reader study, a ranking of books, or a precision claim. The books are not used
to construct the shared vocabulary.

Run `make calibrate-simplified` to reproduce it. The checker follows each
book's canonical LaTeX input graph and excludes front matter, back matter,
generated files, verbatim material, and quotations. The last exclusion is
substantive: quoted language is evidence or character voice, not the author's
expository diction.

## Current result

| Book | Words | Core | OpenGloss-recognized | Unlisted | Markers/1k | Errors / warnings |
|---|---:|---:|---:|---:|---:|---:|
| Foundations | 82,796 | 93.6% | 0.81% | 0.24% | 0.43 | 0 / 99 |
| AI Professional Services | 66,487 | 95.9% | 0.25% | 0.09% | 0.20 | 0 / 49 |
| History Through RFCs | 67,353 | 96.1% | 0.31% | 0.14% | 0.34 | 0 / 102 |
| Wiki History | 42,862 | 95.6% | 0.32% | 0.11% | 0.12 | 0 / 32 |
| Data Center 2026 | 93,134 | 94.9% | 0.31% | 0.37% | 0.39 | 0 / 73 |
| HTSD | 39,121 | 96.9% | 0.30% | 0.04% | 0.77 | 0 / 26 |
| Legal Tech History | 94,016 | 95.2% | 0.34% | 0.12% | 0.30 | 0 / 72 |
| Agents in Law and Finance | 54,748 | 92.5% | 1.08% | 0.14% | 1.50 | 1 / 70 |
| Complexity / Pop Science | 49,046 | 95.1% | 0.55% | 0.17% | 0.27 | 0 / 35 |

Total: 589,563 expository words; one error; 558 warnings. The work queues are
332 recurring term candidates, 201 abbreviation candidates, 26 substitutions,
and no other findings.

The one error is *combinations thereof* in *Agents in Law and Finance*. The
warning count is not a target. A warning asks for contextual review; it does
not assert that the prose is wrong.

## What the calibration changed

- First use is book-wide and ordered. A definition in a later chapter cannot
  excuse an earlier unexplained use.
- Simplemma handles tokenization and ordinary lemmatization. A guarded
  `inflect` fallback handles unknown technical plurals. The project does not
  maintain a suffix or prefix stemmer and does not treat derivation as
  inflection.
- The shared TexSoup prose extractor excludes code, opaque keys, and dropped
  environments while retaining reader-visible semantic wrappers.
- Mixed-case names and digit-bearing identifiers are not vocabulary terms.
  Plural and possessive abbreviations retain their base identity.
- Quoted spans are excluded consistently from substitutions, register
  markers, vocabulary tiers, term prompts, and abbreviation first-use checks.
- `\keyterm` now emits semantic `<dfn>` in EPUB, but neither `\keyterm` nor
  `\term` suppresses a candidate without explanatory context. This is why the
  current term queue is larger than the earlier markup-as-definition run.
- OpenGloss membership is now preserved directly. A `recognized` result means
  the form has an OpenGloss headword but falls below the ordinary-corpus
  thresholds. An `unlisted` result means neither source contains it. Both are
  evidence for editorial review, not automatic accept/reject decisions.
- Explicit prose such as "often abbreviated TOFU" counts as first-use
  identification. Gloss cues include ordinary forms such as "This is X,"
  "which means," and "meaning."

## Standard rationale

[ASD-STE100 Issue 9](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf)
allows necessary subject-field technical nouns and verbs. [Digital.gov's
plain-language guidance](https://digital.gov/guides/plain-language/principles/avoid-jargon)
distinguishes unnecessary jargon from necessary technical terms that should
be defined for the audience. [W3C's unusual-words guidance](https://www.w3.org/WAI/WCAG22/Understanding/unusual-words.html)
targets jargon and unusual or restricted meanings, not every low-frequency
surface form.

That is the SBE rule: explain necessary jargon and unusual or restricted uses.
Corpus frequency and OpenGloss membership help find candidates; neither can
determine what a specific reader understands in a specific sentence.

## Limit

This run establishes that the current checker operates across varied real
books and that its output remains bounded. It does not establish reader
comprehension. The author still decides whether a use is jargon, unusual,
restricted, or already clear to the intended reader.
