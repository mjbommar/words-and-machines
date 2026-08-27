# Style Profiles

A **style profile** adapts the house style to a genre. [STYLE.md](../STYLE.md),
[STYLE-CRAFT.md](../STYLE-CRAFT.md), and [STYLE-AI-TELLS.md](../STYLE-AI-TELLS.md)
hold what every book obeys — the read-aloud test, the banned-word core,
the AI-tell quotas, the sentence/paragraph metrics. A profile layers the
register-specific parts on top: point of view, chapter shape, reading
level, box economy, emotional engineering, and domain vocabulary.

Distilled from the portfolio (`docs/research/`): the same base style
recurs across fifteen books, but they split into a handful of registers
that genuinely differ. These profiles are those registers.

## Choosing one

Set it in `book.yaml`:

```yaml
style:
  profile: narrative-nonfiction
```

| Profile | For | Read-aloud test | POV | Sentence avg / max |
|---|---|---|---|---|
| [narrative-nonfiction](narrative-nonfiction.md) | Reportage, pop-science, sweep/thesis history | Coffee / vendor | "we" + 3rd-person scenes | 15–20 / 35 |
| [practical-guide](practical-guide.md) | Civic handbooks, how-tos, field manuals, advisories | Neighbor | "you" + imperatives | 12–18 / 30 |
| [technical-handson](technical-handson.md) | Code-first tutorials, hacking, practitioner how-tos | Whiteboard / lab-bench | "we"/"you" build it | 12–20 |
| [young-readers](young-readers.md) | Narrative nonfiction / education, ages ~9–14 | Kitchen table | warm narrator "you"/3rd | 12–18 / 30, FK 6–8 |
| [verse-translation](verse-translation.md) | Line-matched translation / parallel text + language reader | (register is the product) | source voice per character | n/a (verse) |
| [explanatory-textbook](explanatory-textbook.md) | Curriculum lesson bodies, standards explainers, university textbooks | Office hours | "we" derive, "you" act | 19–26 / no ceiling |
| [practitioner-forensic](practitioner-forensic.md) | Accounting and finance judgment, forensic case teaching | Second chair | named company as subject; "you" decides | 19–27 / 46 (warn) |
| [narrative-institutional-history](narrative-institutional-history.md) | Standards history, unit openings, institutional biography that teaches | Seminar + footnote | "we" read the document; 3rd-person past | 21–26 / 55 (warn) |

No profile set = base STYLE.md behavior, unchanged. If your book is a
blend, pick the closest and note the deviations in `docs/SPIRIT.md`.

## How a profile works (mechanically)

A profile is a Markdown file, `docs/guides/styles/<name>.md`. It is both
human guidance and **lint config** — the same doc-as-config contract as
STYLE.md. `scripts/check_style.py` (via `make check`) reads these fenced
blocks and layers them over the base lists:

- ` ```banned-words-add` / ` ```banned-words-remove` — adjust the base
  banned-word list (one entry per line; `#` comments allowed).
- ` ```banned-phrases-add` / ` ```banned-phrases-remove` — same, for
  phrases.
- ` ```style-targets` — a small YAML block:
  - `tell_budget:` AI-tell matches allowed per chapter before the run
    fails (base default 3).
  - `sentence_hard_max:` if set, flags sentences over this many words
    as **warnings** (never errors — LaTeX sentence extraction is
    approximate; it's a nudge, not a gate).
  - `burstiness_cv_min:` / `mtld_min:` / `mattr_min:` /
    `adverb_pct_max:` / `para_cv_min:` — threshold overrides for
    `scripts/prose_metrics.py` (`make metrics`), the advisory
    burstiness / lexical-diversity report. Verse or fragment-heavy
    registers should lower `burstiness_cv_min` and `para_cv_min`;
    see the script docstring for the defaults and their basis.

`book.yaml`'s `style.profile` is validated by `generate_metadata.py` and
`check_style.py`; an unknown name fails fast with the list of available
profiles.

## Writing a new profile

Copy the closest existing file and change the deltas — don't fork the
whole style guide. A good profile answers, in one page: who the reader
is and the read-aloud test; person and tense; sentence/paragraph
targets and reading level; chapter/structural shape; the two or three
craft moves that define the register; the failure modes it fights; and
the lint deltas that back all of the above. Keep the prose short — the
base guides carry the shared bulk.

Fiction profiles (kids, adult) are a deliberate gap: fiction needs
craft material this template doesn't yet ship (POV discipline, dialogue
mechanics, scene/sequel structure). Add a `STYLE-CRAFT-FICTION.md`
companion before writing those profiles, so they layer over real
fiction craft the way these layer over STYLE-CRAFT.md.
