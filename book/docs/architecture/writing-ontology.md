# Writing Ontology — macro-to-micro craft taxonomy and technique tools

A structured vocabulary of writing craft — from book-level arcs down to
clause-level constructions — plus scripts that sample from it (ideation,
drafting palettes, LLM prompting) and measure drafts against it
(revision diagnostics). It is the *generative* complement to the
detection tooling (`make metrics`, `make slop`, `make vocab`): those say
what is flat or overused; the ontology supplies the space of named
alternatives to reach for instead.

Covers fiction **and** general/argumentative writing. The unifying
substitution: fiction runs on narrative logic (characters and events,
emotional tension curves); argument runs on inferential logic (claims
supporting and attacking claims, certainty/doubt curves). Both share the
same three tiers: controlled vocabularies → arc/arrangement templates →
executable technique scripts.

All tools here are **advisory** — they inform the writer (or a drafting
LLM); none gate a release.

## Layout

```
scripts/data/ontology/*.json     20 branch files (the data)
scripts/writing_ontology.py      loader / lint / stats / sample CLI + library
scripts/<technique>.py           17 technique scripts (below)
docs/guides/ONTOLOGY.md          usage guide (ideation / drafting / revision)
```

## File schema

Each branch file is JSON:

```json
{
  "name": "syntactic_constructions",
  "level": "micro",                  // macro | meso | micro
  "entry_type": "record",            // "term" (strings) or "record" (objects)
  "description": "One-line scope statement.",
  "categories": {
    "absolute_constructions": [ ...entries... ]
  }
}
```

`term` entries are short lowercase strings (`"in medias res"`).
`record` entries are objects; **required**: `name`, `definition`.
Recommended where they apply: `example` (a real or invented sentence
showing the thing), `effect` (what it does to the reader), `register`
(where it belongs: formal/neutral/informal, fiction/nonfiction),
`caution` (failure mode / overuse risk), `aka`, `tags`. Records may
carry structured extras: arrangement templates use
`beats: [{name, position, purpose}]`; arc shapes use
`curve: [[position, valence], ...]`; argumentation schemes use
`critical_questions: [...]`; constructions may use `pattern` and
`renderings`.

Records may also carry `polarity: virtue | fault | neutral` (a *fault*
names a failure mode — samplers must never emit faults as positive
drafting directives, only as audit targets) and `see_also:
"branch/category"` cross-references for aspect-split concepts.

**Aspect ownership** (the cross-branch dedup rule): a concept lives
once per *aspect*, and the branch that owns the aspect owns the entry —
the figures file owns the figure-as-figure; the sound file owns only
its prosodic realization; the syntax file owns it only when there is a
grammatical `pattern` to state; macro files own arrangements, meso
files own paragraph-internal order. Legitimate aspect splits carry
`aka`/`see_also` both ways; cosmetic renames are duplicates and get
deleted. True homonyms (prolepsis-the-flashforward vs
prolepsis-the-preemption) state their sense in the definition.

**Descriptor banks vs craft branches**: `settings_and_environments`
and `tones_and_moods` are *descriptor banks* — concrete nouns and
atmosphere labels that fuel ideation prompts (`prompt_roller`), like
the story-generator's descriptor sets. They are not craft techniques:
palette/variation sampling excludes them; only ideation tools draw
from them.

`uv run scripts/writing_ontology.py lint` enforces the schema;
`stats` counts; `sample` draws seeded random entries; `show` browses;
`find QUERY` searches name/aka/definition across every branch and
lists all homes of a name. Library API for other scripts:
`load_branch(name)`, `load_all()`, `flatten(name)`,
`sample_entries(branch, category=None, n=1, seed=None)`,
`find_entries(query)`, `is_fault(entry, category)`.

## Branch inventory

The founding twenty are rows 1-20 below, with the later record branches
after them; the live count comes from `make ontology`. Not tabled:
`settings_and_environments` and `tones_and_moods` — the meso descriptor
banks — and `story_beat_templates`, macro records whose `beats` lists
make fiction scaffolding possible alongside the argument arrangements.

| # | File | Level | Contents |
|---|---|---|---|
| 1 | `arc_shapes.json` | macro | Story/certainty arc shapes with valence curves: Vonnegut shapes, rise/fall families, epistemic arcs (delayed thesis, reductio, converging proof) |
| 2 | `narrative_structures.json` | macro | Fiction structures: act models, quest/journey, mystery, episodic, experimental, screen/TV/game forms |
| 3 | `argument_arrangements.json` | macro | Nonfiction arrangements with beats: classical oration, IRAC/CREAC, IMRaD, SCQA/Minto, Monroe, Rogerian, dialectic, proof strategies, journalism and essay forms |
| 4 | `stakes_and_stasis.json` | macro | Stakes ladders, ticking clocks, stasis theory (fact/definition/quality/jurisdiction), burden of proof, claim types |
| 5 | `themes_and_questions.json` | macro | Themes, moral dilemmas, philosophical and research questions, motifs |
| 6 | `rhetorical_situations.json` | macro | Venue/genre/audience: exigence, audience models, constraints, occasion types, publication forms |
| 7 | `scene_patterns.json` | meso | Scene types/functions, scene-level patterns (scene-sequel, try-fail, yes-but), scene openings/endings/transitions |
| 8 | `paragraph_shapes.json` | meso | Paragraph architectures: point-evidence-analysis, they-say/I-say, cumulative-then-punch, question-answer, and kin |
| 9 | `discourse_moves.json` | meso | Coherence relations (RST-style), signposting, metadiscourse moves, transition families with cue phrases |
| 10 | `argumentation_schemes.json` | meso | Walton-style schemes with critical questions: expert opinion, analogy, sign, cause-to-effect, slippery slope, … |
| 11 | `fallacies_eristic.json` | meso | Informal fallacies + eristic stratagems, each with detection cues |
| 12 | `evidence_types.json` | meso | Evidence/example/authority types, statistics presentation modes, case selection strategies |
| 13 | `openings_and_closings.json` | meso | Hooks, ledes, cold opens, frames; closers, callbacks, codas |
| 14 | `character_and_persona.json` | meso | Character archetypes and stock types; argumentative roles (skeptic, steelman); authorial personae (audience models live in `rhetorical_situations`) |
| 15 | `interaction_moves.json` | meso | Character interaction families (emotional/social/conflict) + argumentative exchange moves (concede, rebut, undercut, distinguish, analogize) + dialogue-game moves |
| 16 | `syntactic_constructions.json` | micro | Clause/sentence machinery: absolutes (with English renderings of the Latin ablative absolute), periodic vs. loose/cumulative, parataxis/hypotaxis, clefts, fronting, appositives, resumptive modifiers |
| 17 | `rhetorical_figures.json` | micro | Schemes and tropes at Lanham scale: repetition, balance, omission, substitution, wordplay figures; metaphor/metonymy families; irony types |
| 18 | `sound_and_rhythm.json` | micro | Sound devices (alliteration family), prose rhythm: cadence/cursus patterns, sentence-final stress, length contours, meter basics |
| 19 | `diction_and_register.json` | micro | Register layers (Latinate/Germanic), hedges, boosters, attitude/engagement markers, connotation axes, word-choice strategies |
| 20 | `pov_and_narration.json` | micro | POV, psychic distance ladder, tense strategy, free indirect discourse, narrator reliability, narration modes for nonfiction |
| 21 | `revision_moves.json` | meso | The verbs of editing: cut, compression, expansion, reordering, splitting/merging and substitution moves, plus a diagnosis table pairing each measured symptom (`prose_metrics`, `construction_variety`, `register_report`, `slop_audit`, `setup_payoff`, `pangram_check`) with the named move that treats it |
| 22 | `humor_and_wit.json` | meso | Comic mechanisms: structures (setup-misdirection-punchline, rule of three, topper, callback), timing, comic personae, incongruity engines, the comic use of wit figures, and humor faults |
| 23 | `metaphor_domains.json` | meso | The anti-default-imagery bank: source domains with their entailments (and cautions on the exhausted journey/war/light defaults), target domains, mapping controls, domain-mixing rules |
| 24 | `information_release.json` | meso | Suspense and its nonfiction analogue: reader knowledge states, release moves, release schedules, promise management (what `setup_payoff.py` prescribes from), nonfiction release |
| 25 | `dialogue_mechanics.json` | micro | The mechanical layer of speech: tags and beats, typography of speech, exchange shapes, subtext techniques, silence and pause, dialogue faults (interaction moves owns what characters *do*; POV owns speech *representation*) |
| 26 | `genre_conventions.json` | macro | Per-genre reader contracts: genre promises with obligatory scenes and exhausted moves, standalone obligatory scenes, convention and subversion moves, worldbuilding basics |
| 27 | `persuasion_appeals.json` | meso | Classical appeals as working moves (ethos/pathos/logos/kairos), propaganda techniques with detection cues and polarity, copywriting concepts vetted against the vendor test, narrative persuasion |

Target: thousands of entries total; micro branches are `record` files,
macro/meso mix `term` and `record`.

## Technique scripts (17)

| Script | Kind | What it does |
|---|---|---|
| `writing_ontology.py` | core | Load, lint, stats, browse, seeded sampling |
| `prompt_roller.py` | generative | Constrained ideation prompts (fiction premise, essay angle, chapter concept) honoring `style.profile` |
| `beat_scaffold.py` | generative | Instantiate an arc/arrangement into an outline scaffold: per-beat position, purpose, tension target, suggested moves |
| `palette_sampler.py` | generative | Sample construction/figure palettes as drafting directives; `--for-deslop` emits directive lines for `deslop.py` |
| `variation_engine.py` | generative | For a passage: N distinct recast-directive sets (axes of variation drawn from the ontology) |
| `exercise_generator.py` | generative | Progymnasmata-style drills: same topic through the fable→thesis ladder |
| `outline_composer.py` | generative | The stateful one: `init`/`deepen`/`lint`/`render` build one outline in `outline/composition.yaml`, children conditioned on their parent and the spine's valence curve, deepening idempotent per node (design: `outline-composer.md`) |
| `construction_variety.py` | diagnostic | Syntax overuse: sentence-opener types, branching direction, length shapes — the construction sibling of `make vocab` |
| `figure_detector.py` | diagnostic | Heuristic detection of alliteration, anaphora, epistrophe, anadiplosis, tricolon/isocolon, polysyndeton/asyndeton; density + distribution |
| `rhythm_audit.py` | diagnostic | Cadence report: sentence-final stress patterns, clause-length contour, cursus-like endings |
| `register_report.py` | diagnostic | Hedge/booster density, Latinate/Germanic ratio, metadiscourse profile vs. style-profile targets |
| `arc_profiler.py` | diagnostic | Per-chapter valence/tension curve (lexicon-based) compared against a target arc shape |
| `setup_payoff.py` | diagnostic | Ledger of promises (questions raised, terms introduced, deferred objections) audited for payoff |
| `move_annotator.py` | LLM-optional | Classify paragraphs by discourse move; coverage audit vs. genre profile (cue-lexicon fallback without a key) |
| `objection_engine.py` | LLM-optional | Fire each scheme's critical questions at a draft's claims; ranked objection list |
| `sparring_partner.py` | LLM-optional | Dialogue-game red team: personae make taxonomy-sampled moves against a thesis |
| (integration) | — | `make ontology` (stats+lint), `make craft` (diagnostic suite); generative CLIs documented without targets, like `deslop.py` |

## Conventions

- Scripts follow the house pattern: `#!/usr/bin/env -S uv run --script`
  with PEP 723 inline deps; default corpus `latex/chapters/` with
  `--root`; accept `--text FILE` for arbitrary plain prose; advisory
  (exit 0) unless `--strict`; LaTeX stripped the way
  `prose_metrics.py` does it.
- Seeded randomness everywhere (`--seed`) so prompts and palettes are
  reproducible.
- Entries are established, nameable craft concepts — no invented
  jargon, no duplicated entries across categories within a file.
- The ontology never edits prose. Generative scripts emit prompts and
  directives; diagnostic scripts emit reports; humans (or a revision
  pass like `deslop.py`) apply changes.
