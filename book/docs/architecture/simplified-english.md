# How the Simplified Book English lexicon is derived

Design notes for `scripts/build_simplified_lexicon.py`. The author-facing
standard is [docs/guides/SIMPLIFIED-ENGLISH.md](../guides/SIMPLIFIED-ENGLISH.md);
this file is the part that matters only when you are changing the build or
arguing with its numbers.

## Tooling boundary

The project environment and `uv.lock` own this toolchain. SBE scripts do not
carry PEP 723 dependency blocks or create private one-off environments.

- `simplemma` owns Unicode-aware token boundaries and known-word lemmatization.
- `inflect` supplies a guarded fallback for unknown technical plurals. Its
  result is accepted only when pluralizing the candidate recreates the source
  form; known singulars are protected from its noun heuristic.
- `TexSoup` is the project's LaTeX parser. The canonical verbatim vocabulary
  lives in `converter.latex_source` and is imported by both the EPUB converter
  and SBE checker. EPUB stashes those bodies because it must render them; SBE
  blanks them because they are not prose. The SBE extractor also discovers
  legacy listing environments from their actual preamble declarations and
  walks TexSoup's positioned tree. Same-length blanking keeps source lines
  stable. A differential run over all 183 canonical calibration files must
  parse without fallback; malformed input fails loudly rather than selecting a
  second permissive parser.
- The checker itself owns only SBE policy: corpus tiers, book-wide first-use
  order, gloss acceptance, abbreviation expansion, and explicit exceptions.

Inflection and derivation are intentionally different. A plural or tense does
not introduce a new concept, so a library lemma can inherit the base word's
tier. A derivation can introduce one (`surprise` does not automatically admit
`surprisal`; `mechanize` does not automatically admit `mechanizable`), so no
project suffix table promotes derived forms. Corpus evidence, an introduction,
or an explicit book policy must admit them.

The EPUB converter's runtime dependencies remain in `[project.dependencies]`.
SBE analysis dependencies live in the local `sbe` dependency group, and the
large dataset and Arrow stack used only to rebuild the shared lexicon lives in
the nested `sbe-build` group. The supported entry points are therefore
`uv run --group sbe scripts/check_simplified.py` and
`uv run --group sbe-build scripts/build_simplified_lexicon.py` (the Makefile
wraps both).

## Inputs

Seven prose corpora, sampled by streaming and reduced to word counts. Only
aggregate counts are stored — a word and a number — never text.

| Cache | Dataset | Sample | Register |
|---|---|---:|---|
| `gutenberg` | `manu/project_gutenberg` | 2,500 books / 169.2M tokens | book English, largely pre-1930 |
| `books` | `lucadiliello/bookcorpusopen` | 325 books / 20.0M | modern published books |
| `fineweb` | `HuggingFaceFW/fineweb-edu` sample-10BT | 20,000 docs / 14.9M | modern educational web |
| `web` | `HuggingFaceFW/fineweb` sample-10BT | 29,027 docs / 15.0M | modern general web |
| `news` | `cnn_dailymail` 1.0.0 | 25,557 docs / 15.0M | journalism |
| `simplewiki` | `wikimedia/wikipedia` 20231101.simple | 50,399 docs / 12.0M | plain English by construction |
| `explain` | `sentence-transformers/eli5` | 165,218 answers / 12.0M | lay explanation |
| `billsum` | `FiscalNote/billsum` train | 8,000 bills / 10.1M | US federal legislation |
| `billsum-ca` | `FiscalNote/billsum` ca_test | 1,237 bills / 1.85M | California legislation (replication) |

Plus `mjbommar/opengloss-v1.3-dictionary` (CC-BY 4.0) for direct headword
recognition, inflections, and a Wikipedia frequency rank, read from the slim cache
`scripts/vocab_variety.py` builds.
Single-word headwords feed the vocabulary evidence classes. Exact multiword
headwords are retained separately so `--explain` can answer literal OpenGloss
membership queries without treating phrase membership as automatic admission.

Caches live in `~/.cache/book-template/sbe/counts-<name>.json` and are
shared across every book from this template. Prose is tokenized
`[a-z][a-z'-]*` (contractions kept); bills are tokenized `[a-z]+`, because
`[a-z][a-z'-]*` swallows drafting punctuation and turns 22% of the bill
vocabulary into artifacts like `amended--` and `act''`.

## Why seven corpora

Because one is demonstrably not enough. Rebuilding the identical rule with
news in place of educational web changes **half the core list**; Wikipedia
in place of it changes 45%. Only ~7.5 points of that is sampling noise, so
the choice of a single proxy was moving ~40% of the vocabulary.

The failure was visible in the output, too: with educational web as the only
modern corpus, `whispered`, `shrugged`, `doorway` and `sofa` all fell
outside the core tier. An educational filter is a bad model of a book.

## The rule

```
modern  = max(rate in books, fineweb, web, news, simplewiki, explain)
core   := (modern >= 10/M)
          or (gutenberg >= 10/M and modern >= 1/M)     # still current
       and (attested >= 1/M in >= 2 of the 7 prose corpora
            or Wikipedia rank <= 30,000)
       and (known to OpenGloss, or modern >= 50/M)
       + OpenGloss inflections that are themselves attested >= 0.5/M
       - the curated never_core list
open   := known to OpenGloss, >= 0.5/M in some prose corpus, not core
recognized := all remaining single-word OpenGloss headwords
```

`recognized` is deliberately not an approval tier. OpenGloss answers the
literal dictionary question—whether the form has an entry. It does not prove
that this book's general reader knows the concept or the sense used here. The
checker keeps recurring recognized and unlisted forms in the same contextual
review queue, but labels the evidence accurately. This prevents corpus-tail
words from being misreported as nonexistent while avoiding the opposite error
of silently admitting every specialist dictionary entry.

Two clauses are load-bearing and worth keeping honest about:

- **The inflection filter.** Expanding a headword to every OpenGloss
  inflection without checking attestation invents words: an earlier build
  shipped `accompannies`, `aboves` and `actioned` in the core tier, and 8%
  of core forms had zero corpus attestation. Requiring 0.5/M somewhere fixes
  it.
- **The "still current" branch.** It is what admits narrative vocabulary
  (`whispered`, `hearth`, `carriage`) without admitting dead vocabulary.
  Archaisms that survive in modern religious and literary quotation —
  `thou`, `thy`, `whilst` — still get through. They are harmless in
  practice, since core and open enforce identically, but the tier label
  overstates what has been proved about them.

## Thresholds are chosen, not discovered

Coverage is smooth and roughly log-linear in the modern-frequency cutoff —
about −3.6 points per doubling — with no cliff or plateau anywhere. This
table was measured on the earlier three-corpus build; the shape is what
matters, not the exact rows.

| modern cutoff | core forms | Gutenberg | fit corpus | held-out news | held-out Wikipedia |
|---:|---:|---:|---:|---:|---:|
| 2.5/M | 27,350 | 91.85% | 93.98% | 92.28% | 88.68% |
| 5.0/M | 20,055 | 89.72% | 92.51% | 90.31% | 86.26% |
| **10.0/M** | **13,854** | **86.98%** | **90.07%** | **87.20%** | **82.96%** |
| 20.0/M | 9,093 | 83.42% | 86.40% | 83.37% | 78.57% |
| 50.0/M | 4,692 | 76.97% | 79.10% | 76.02% | 70.72% |

`core + open` coverage is *identical* at every row, because a word demoted
from core lands in open. The core/open split therefore carries no
enforcement consequence at all — it feeds the statistics and nothing else,
and the guide says so.

## Statistical weaknesses, stated

- **Sampling.** Empirical overdispersion across disjoint samples of the same
  source is φ ≈ 4 (variance / mean), so the effective sample is four times
  smaller than Poisson assumes. The honest 95% band at a 10/M cutoff is
  6.8–13.2/M. Two disjoint samples of the same corpus disagree about
  membership for ~16% of words near the threshold; resampling moves ~7.5% of
  core forms, and ~13% of core does not survive ten redraws.
- **In-sample coverage.** Every coverage figure computed on a corpus the
  tiers were fit to is optimistic by 3–7 points relative to held-out prose.
  The 2026-08-12 held-out calibration spans nine book projects and about
  590,000 expository chapter words, which the build never sees: weighted core coverage is
  about 95%. Register rates are reported per book rather than collapsed into one
  number because subject mix is the signal; see
  `docs/research/simplified-english-calibration-2026-08-12.md`.
- **Reproducibility.** Samples are the first N documents or tokens of a
  *streaming* dataset. Every source is pinned to a full repository revision;
  the artifact also records a SHA-256 prefix of each aggregate counts cache.
  A source can still become unavailable, so the cache digest identifies the
  exact inputs even when the pinned stream cannot be fetched again.
- **Truncation.** Counts are stored for the top 120,000 types per corpus.
  The rarest kept type is far below every threshold in use, so this is
  benign for the tiers; it does bias any statistic computed on absence.

## The register statistics

Reported per substitution entry, advisory only:

```
register_lift = geometric mean of
                (federal bill rate / prose rate, Jeffreys-smoothed)
                (California bill rate / prose rate, Jeffreys-smoothed)
doc_spread    = share of federal bills containing the word at all
```

The geometric mean across two legislatures is a replication requirement: a
single-legislature ratio has a federal-vs-California correlation of only
r = 0.17 on log lift, so most of a one-corpus ranking does not reproduce.
Jeffreys smoothing `(c + 0.5) / (N + 1)` replaces an earlier hard floor on
the denominator, which had been manufacturing enormous ratios out of
absence — 42% of bill vocabulary fell below that floor.

Both statistics are weak instruments. Against a labelled set (plain-language
targets vs frequency-matched controls) document spread reaches AUC 0.811 and
the lift ratio 0.762 — enough to rank candidates for human review, not
enough to decide anything. **They do not grade the substitution list**; the
grades are editorial judgement seeded from plainlanguage.gov, and the
measured separation between the shipped `error` entries and the rest is AUC
0.575.

The policy therefore stores two independent decisions. A substitution grade
controls whether an occurrence is revision work; `marker_only` can retain an
idea-grade technical word in the aggregate register comparison. Deriving the
score directly from warning severity made correct technical prose noisy and
made metric stability depend on editorial triage.

## What the build deliberately does not do

- It does not read part of speech, though OpenGloss ships it. STE's "one
  word, one part of speech" rule has no analogue here.
- It does not turn OpenGloss's multiword entries into free vocabulary. The
  phrase list supports exact `--explain` lookup only; many entries are ordinary
  collocations rather than terminology, and membership says nothing about the
  intended reader.
- It measures the checker marker set, including multi-word phrases, while it
  streams each corpus. Phrase register lift and document spread therefore use
  the same combined matching semantics as the book report.
- It does not measure difficulty. `reading_level` is available in OpenGloss
  but is a target label in a synthetic encyclopedic dictionary, not validated
  evidence of audience familiarity. Frequency is only a candidate-generation
  heuristic, which is why corpus-tail findings require editorial review rather
  than automatic revision.

## Checker ordering and abbreviation recognition

The lexicon artifact is unordered, but first authorial use is not. The checker
walks the canonical LaTeX input graph in reading order. Inline quotations and
dropped quotation environments are excluded from author-diction checks; an
authorial use after a quotation must carry its own explanation when the reader
needs one. `\keyterm` and `\term` do not suppress a finding: semantic markup
can identify a defining occurrence, but only the surrounding explanation
conveys meaning.

An abbreviation candidate is three to seven capital letters after normalizing
a lowercase plural or possessive. Roman numerals, ordinary all-cap words,
declared names, name-adjacent tokens, and uppercase filename suffixes are
excluded. Expansion matching generates plausible initials both with and
without connector words and from hyphenated components, then requires the long
form near the first occurrence in visible-word distance. Reverse expansions
cannot cross a sentence boundary. This is deliberately a conservative shape
test, not a claim that the checker understands the abbreviation.
