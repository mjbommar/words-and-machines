# ONTOLOGY — using the writing ontology and craft tools

The writing ontology (design: `docs/architecture/writing-ontology.md`) is
a macro-to-micro taxonomy of writing craft — arc shapes and argument
arrangements down to clause-level constructions, figures, and cadences —
under `scripts/data/ontology/` (23 branch files, ~8,200 entries as of this
writing — `make ontology` prints the live count), plus **17 scripts**: the
`writing_ontology.py` loader, five generative samplers (`prompt_roller`,
`beat_scaffold`, `palette_sampler`, `variation_engine`,
`exercise_generator`), the stateful `outline_composer`, six diagnostics (`construction_variety`,
`figure_detector`, `rhythm_audit`, `register_report`, `arc_profiler`,
`setup_payoff`), three LLM-optional red-team tools (`move_annotator`,
`objection_engine`, `sparring_partner`), and `craft_brief.py`
(`make brief`), the one-command entry point.
Everything here is **advisory**: it feeds ideation, drafting prompts,
and revision; nothing gates a release, and no tool edits prose.

Day to day, `make brief` is the way in — it runs the craft diagnostics for
the round. The loader is for browsing the vocabulary itself:

```bash
make ontology                                   # stats + schema lint (and the entry count)
uv run scripts/writing_ontology.py show rhetorical_figures
uv run scripts/writing_ontology.py sample syntactic_constructions -n 3 --seed 7
uv run scripts/writing_ontology.py find "periodic"   # name/aka/definition, every branch
```

`find` is the one to reach for when a report or a review finding needs a
name: it searches every branch and lists all homes of a term, so
"periodic" turns up the sentence architecture, its cadence sibling, and
the unrelated statistics sense in one screen.

## Where each tool fits in the writing workflow

### Ideation (before outlining)

```bash
uv run scripts/prompt_roller.py --kind chapter -n 3        # constrained premises
uv run scripts/prompt_roller.py --kind essay --seed 11     # argument angles
uv run scripts/exercise_generator.py --topic "your theme"  # progymnasmata drills
```

The roller prints every slot's `[branch.category]` provenance and its
seed, so a good roll is replayable. It is also the only tool that reads
`book.yaml`'s `style.profile` for anything other than thresholds — but it
only *names* the profile in the header; it does not filter entries by
genre. Reading the roll against the profile is your job.

### Outlining

```bash
uv run scripts/beat_scaffold.py --list                     # templates with beats or a curve (220+)
uv run scripts/beat_scaffold.py --template "classical oration" --words 4000
uv run scripts/beat_scaffold.py --template irac --words 1500 --moves discourse_moves
```

Produces a markdown scaffold with per-beat positions, word budgets,
purposes, and sampled moves. Arc shapes with valence curves double as
revision targets for `arc_profiler.py` later.

`beat_scaffold` is a throwaway: one template, one print, no memory. When
the outline is the deliverable rather than a prompt, use the composer
instead — it keeps one YAML document and grows it breadth-first, then
depth-first, without disturbing what is already there.

```bash
uv run scripts/outline_composer.py init --kind fiction --words 80000 \
    --premise "your premise here" --seed 7      # registry + spine + chapters
uv run scripts/outline_composer.py deepen ch01                 # chapter -> scenes
uv run scripts/outline_composer.py deepen --all-stubs          # a whole level
uv run scripts/outline_composer.py lint                        # consistency pass
uv run scripts/outline_composer.py render --out outline/outline.md
uv run scripts/outline_composer.py render --format html --out outline/outline.html
```

State lives in `outline/composition.yaml` — canonical, hand-editable,
committed. Children are conditioned on their parent and on the spine's
valence curve (a falling span is offered setbacks, a rising one payoffs);
word budgets partition exactly; and deepening one node never touches its
siblings, so the outline can be grown a chapter at a time over a week.
`lint` catches what hand-editing breaks — budgets that no longer sum,
promises paid before they are made, a fault or a descriptor-bank noun
smuggled into a move list. `render` writes the markdown outline the
`outliner` agent and `chapter-drafter` work from; `--format json|toml`
emit the same resolved document for other tools to read (empty keys
omitted, so there is no null-vs-missing ambiguity), and `--format html`
writes one self-contained page — inline CSS, light/dark, an SVG of the
arc curve, the node tree, and a cross-linked promise ledger — with no
external requests. The composer sits between research and drafting, and
`make test-compose` is its regression suite. Design:
`docs/architecture/outline-composer.md`.

### Drafting (human or LLM)

```bash
uv run scripts/palette_sampler.py --seed 3 --for-prompt    # construction palette
```

Paste the palette block into a drafting prompt (or hand it to
`chapter-drafter`). It forces distributional spread at the micro level —
the thing burstiness metrics and Pangram windows reward — instead of the
model's default narrow syntax. STYLE-AI-TELLS bans the negative tail;
the palette supplies the positive complement.

### Revision — diagnostics

```bash
make brief            # the round's craft brief (the usual entry point)
make craft            # the raw diagnostic suite behind it
```

| Script | Question it answers |
|---|---|
| `construction_variety.py` | Are my sentence openers/architectures monotone? (+ what to reach for instead) |
| `figure_detector.py` | Which figures am I actually using, and are they clumped? |
| `rhythm_audit.py` | How do my sentences *end*? Cadence runs, uniform paragraphs |
| `register_report.py` | Hedge/booster balance, Latinate share, nominalizations vs profile targets |
| `arc_profiler.py` | Does the chapter's valence/tension curve match the intended arc? (`--target "man in hole"`) |
| `setup_payoff.py` | Which promises (questions, forward refs, Chekhov's guns) are unpaid? |
| `move_annotator.py` | Paragraph-by-paragraph discourse moves; families never used; monotony runs |

All seven take `--root`, `--chapter`, `--text FILE` (arbitrary prose or a
single `.tex`), and `--json`. Beyond that they are **not uniform**, and
the differences bite:

- **What they scan.** `rhythm_audit`, `register_report`, and `arc_profiler`
  read `latex/chapters/` only. `construction_variety`, `figure_detector`,
  `move_annotator`, and `setup_payoff` also pick up `latex/frontmatter/`
  and `latex/backmatter/` (the hyphenated spellings too) — the same
  discovery `make metrics` uses. So a front-matter-heavy book gets more
  units from the second group than from the first; don't compare their
  unit counts.
- **`--strict`.** Present only where a threshold exists to fail:
  `construction_variety`, `figure_detector`, `rhythm_audit`,
  `register_report`, `arc_profiler`, `setup_payoff`. `move_annotator`,
  `objection_engine`, and `sparring_partner` have **no `--strict`** — they
  always exit 0. None of these belongs in a release gate regardless.
- **Genre-profile overrides.** Three scripts read the active profile's
  ```style-targets``` block (`docs/guides/styles/<style.profile>.md`):
  `rhythm_audit` (`cadence_share_max`, `cadence_run_max`,
  `uniform_para_pct_max`), `register_report` (`hedge_per_1000_max`,
  `booster_per_1000_max`, `attitude_per_1000_max`,
  `nominalization_per_1000_max`, `latinate_ratio_max`,
  `contraction_per_1000_min`), and `arc_profiler` (`valence_range_min`,
  `tension_range_min`, `arc_correlation_min`). `construction_variety` and
  `figure_detector` thresholds are **command-line only** (`--min-odi`,
  `--max-run`, `--max-subject-share`, `--max-density`, …) — put the flags
  in the profile's prose, not in its YAML block, or they will be ignored.
- **`--json` shape.** Two conventions. `rhythm_audit`, `register_report`,
  and `arc_profiler` emit **JSON-lines** — one object per unit, one per
  line (`… --json | jq -s '.'` to collect them). Everything else emits a
  **single JSON document**: `{"units": [...]}` from `construction_variety`
  and `figure_detector`, a keyed object from `setup_payoff`,
  `move_annotator`, `objection_engine`, `sparring_partner`, and the
  generative tools.

### Revision — directed rewrites

```bash
uv run scripts/variation_engine.py --text draft.txt -n 3   # 3 labeled directions
uv run scripts/palette_sampler.py --for-deslop --seed 5    # deslop directives
```

`variation_engine` emits direction-sets anchored to real sentences
("your longest sentence, sentence 11, 51 words — recast on the
resumptive modifier"); feed a chosen set to a human pass or a
`deslop.py --batch` fix brief. REVIEW-QA §7 workflow applies unchanged.

### Argument hardening (nonfiction)

```bash
uv run scripts/objection_engine.py -n 10                   # critical questions vs claims
uv run scripts/sparring_partner.py --thesis "your thesis" --seed 2
```

Both draw on the 84 argumentation schemes (each with Walton-style
critical questions) and 160 fallacies with detection cues. `--llm`
sharpens both (pydantic-ai, same provider setup as `slop_audit.py`);
they are fully functional without a key.

## Rules of the road

1. **Directives, not edits.** Ontology tools emit prompts, palettes,
   scaffolds, and reports. Prose changes happen in the normal revision
   flow (fix briefs, deslop passes, human editing).
2. **Seeds are part of the record.** Every sampling tool prints its
   seed; keep it in the round notes so a palette or roll can be
   reproduced.
3. **Suggestions respect the ban lists.** Anything the palette or a
   report suggests still has to pass `make check` — STYLE.md bans and
   AI-tell patterns outrank ontology suggestions.
4. **Data lives in `scripts/data/ontology/*.json`** — one branch per
   file, schema in the design doc, `make ontology` lints it. Add
   entries there (with `name` + `definition` minimum), never inline in
   scripts.
