# Outline composer — stateful, conditioned, idempotent

Design notes for `scripts/outline_composer.py`. The usage entry point is
[docs/guides/ONTOLOGY.md](../guides/ONTOLOGY.md); this file is the part
that matters only when you are changing the tool or arguing with its
state schema.

## The problem

The ontology ships five generative CLIs — `prompt_roller`,
`beat_scaffold`, `palette_sampler`, `variation_engine`,
`exercise_generator`. All five are single-shot rollers: independent,
stateless, and correct for what they do. Ideation wants a fresh roll.
An outline does not. An outline is one artifact that has to stay
internally consistent while it grows, and three properties fall out of
that requirement which no stateless roller can supply:

1. **State.** `beat_scaffold --template "man in hole"` prints a scaffold.
   Run it again tomorrow with a different seed and you get a different
   scaffold. There is nowhere for "the POV I chose last week" to live, so
   chapter 9's roll cannot know what chapter 1's roll decided.
2. **Downward conditioning.** A scaffold samples moves per beat by
   token-overlap with that beat's own name and purpose. It has no notion
   of a *parent*, so it cannot offer a scene the moves that fit both the
   chapter it sits in and the emotional position the arc puts it at.
3. **Idempotent deepening.** Re-rolling to expand chapter 7 re-rolls
   chapters 1-6 as well. Work already done is destroyed by the act of
   doing more work.

`outline_composer.py` is the generative counterpart of
`craft_brief.py`: craft_brief composes the seven diagnostics into one
brief, this composes the ontology into one outline and keeps it.

## The state file

`outline/composition.yaml` by default (`--file` overrides). One YAML
document, plain data, canonical and committed — it is the outline, not a
cache. Hand-editing is the documented primary way to change it; `lint`
is the safety net and `set` is a small validated escape hatch for
registry scalars.

```yaml
composer:  {version, tool, seed, created, reproduce}
meta:      {kind: fiction|nonfiction, title, premise, words}
registry:
  pov | narration | stance         # kind-appropriate identity slots
  tense: past|present              # derived from tense_strategy's name
  tense_strategy | register | tone | setting | protagonist | persona
  audience | venue | themes[]
  entities:  [{name, kind, introduced_at: NODE_ID, note}]
spine:
  template:  {name, branch, category, source: beats|curve}
  definition, note
  arc:       {name, branch, category, definition} | null
  curve:     [[position, valence], ...]      # verbatim from the ontology
  beats:     [{name, purpose, position: [start, end]}, ...]
nodes:       # ordered tree; the id is the identity
  - id, title, purpose, position: [start, end], words, valence,
    status: stub|deepened|locked,
    moves: [{name, branch, category, definition, why}],
    opens: [promise ids], pays: [promise ids], children: [...]
promises:
  - {id, kind: question|forward-ref|term|entity, text,
     opened_by, paid_by, intentional_open}
```

Every registry slot carries its `source` as `branch.category`, so any
choice can be traced back into `scripts/data/ontology/`. Node key order
is canonical and rewrites preserve it (`yaml.safe_dump(..., sort_keys=
False)` over dicts built in that order), which is what keeps a deepen's
diff to the subtree it touched.

One schema serves both kinds. `meta.kind` decides which registry slots
are rolled, which branches supply a spine, and which supply moves.
A crossover — a nonfiction book on a Vonnegut curve — is a note on
stderr, never a failure.

## Where the spine comes from

Templates are discovered at runtime: any ontology record carrying
`beats` or a `curve`. Branch filenames are the contract; categories are
not. By kind:

| kind | spine branches | arc |
|---|---|---|
| fiction | `story_beat_templates`, `narrative_structures`, `arc_shapes` (non-epistemic categories) | any non-epistemic `arc_shapes` curve |
| nonfiction | `argument_arrangements`, `arc_shapes` (epistemic categories) | `arc_shapes.epistemic_arcs` |

`narrative_structures` is a `term` branch today, so it contributes no
templates; it is listed because discovery is runtime and the branch may
grow records later.

A beat sheet says *what happens where*; an arc shape says *how it should
feel there*. Conditioning needs the second. When the chosen spine
carries no curve of its own (every `story_beat_templates` and
`argument_arrangements` record), a companion arc is picked — seeded from
the kind's curve-bearing records, or pinned with `--arc NAME` — and its
curve becomes `spine.curve`. A spine that already has a curve keeps it.

Level-1 nodes are the spine's beats, or — with `--chapters N` — an even
N-way grid over the whole work, each chapter taking its title and
purpose from the beats its span overlaps. Positions come from the beats'
declared positions, with `parse_position`/`interpolate` (adapted from
`beat_scaffold.py`) filling gaps.

## Conditioning rules

Everything below happens per child, at deepen time.

**Span.** Children tile the parent's `[start, end]` exactly, in order,
with no gaps. Each child gets a mild seeded emphasis weight
(0.8 … 1.3); positions and word budgets use the *same* weights, so a
node's share of the book and its share of the page agree.

**Budget.** `partition_words` is a largest-remainder split: children sum
to the parent exactly, every time, with the rounding remainder
distributed deterministically (largest fractional part first, index as
the tie-break). No drift accumulates down the tree.

**Valence.** Linear interpolation of `spine.curve` at the child's
midpoint; `null` when the spine has no curve. The child's local slope is
the same interpolation at its two endpoints.

**Mode.** Slope decides first (±0.05); when the slope is flat or absent,
the valence sign decides (±0.2). Three modes — `falling`, `rising`,
`flat` — each with a keyword set:

| mode | keywords |
|---|---|
| falling | setback, loss, confront, reversal, complicat, escalat, objection, doubt, conflict, refus, conced, withhold, cost |
| rising | resolution, recovery, reconcil, insight, answer, payoff, synthesis, triumph, reveal, resolve |
| flat | establish, exposition, setup, introduc, context, orient, background, definition |

Concession sits with the falling moves deliberately: conceding is what
being fair costs you, not a payoff.

**Moves.** The pool is every non-fault record in the kind's move
branches — fiction: `scene_patterns`, `interaction_moves`,
`dialogue_mechanics`, `information_release`; nonfiction:
`discourse_moves`, `evidence_types`, `paragraph_shapes`,
`argumentation_schemes` — matched case-insensitively against the mode's
keywords plus up to six content words from the parent's purpose. Each
emitted move records *which* keyword matched it and via which source,
in its `why`. An empty filtered pool falls back to the unfiltered pool
and says so in the same field.

**Registry.** Children inherit POV, tense, register and tone implicitly;
a node that declares one of those slots must also declare
`override: true`, which `lint` enforces. A fiction deepen may (seeded,
≈1 in 4) introduce one or two cast slots — never proper names, which are
the author's to invent, but `a rival`, `a donor`, stamped with the node
that introduces them.

**Promises.** The ledger mirrors `scripts/setup_payoff.py` and uses its
four kinds — `question`, `forward-ref`, `term`, `entity`. The difference
is direction: setup_payoff *discovers* promises in finished prose and
audits whether they were paid; the composer *plans* them, and every
promise is assigned a payer at the moment it is opened, from the nodes
that sit later in the book. A promise with no later node available is
marked `intentional_open: true` rather than left dangling.

## The idempotence contract

All randomness for a node's expansion comes from
`random.Random(f"{seed}:{node_id}")`, and each child re-seeds from
`f"{seed}:{child_id}"`. Consequences, all covered by
`tests/test_outline_composer.py`:

- Deepening `ch07` cannot change `ch01`–`ch06`. The test snapshots every
  node's own YAML text and requires byte equality across an unrelated
  deepen.
- Two `init` runs with the same seed produce byte-identical files.
- Deepening the same node twice is a no-op the second time (soft, exit
  0). `--reroll` opts in to replacing children, and refuses in turn if
  any child has itself been deepened or locked; `--force` overrides that.
- A rerolled subtree's promises are pruned, and any promise that pointed
  at a discarded node is unhooked and marked intentionally open rather
  than left pointing at nothing.
- A load/dump cycle over the state file is a no-op, so the only lines a
  deepen changes are the ones it meant to change.

`--seed-override` exists for the case where you want a different roll of
one node without changing the book's seed. It is recorded nowhere, so
the `composer.reproduce` line no longer reproduces that node — use it
knowingly.

## What lint guarantees

`lint` is the consistency pass, and it is written to survive a
hand-edited file: it reports, it does not crash, and every check
degrades to a finding when the data is the wrong shape.

- children's word budgets sum to their parent within 1%
- child spans nest inside the parent, are ordered, and tile it (±0.5%)
- positions are ordered `0 ≤ start < end ≤ 1`; word budgets are positive
  integers; node ids are unique; statuses are known
- every promise's `opened_by` and `paid_by` name real nodes, and the
  payer sits strictly later than the opener — or the promise is marked
  `intentional_open: true`
- no entity is named in a node that sits before its `introduced_at`
- no node overrides POV/tense/register/tone/setting/stance/narration
  without `override: true`
- no move name is a fault anywhere in the ontology (the aggregate check
  from `prompt_roller.py`, so aspect homonyms cannot leak through)
- no move comes from a descriptor bank
- no node's recorded valence disagrees with the spine curve by more
  than 0.15
- no node has `status: deepened` and no children

Exit 0 always, except `lint --strict` with warnings → 1. Nothing else in
the composer exits nonzero except hard user errors: a missing state
file, an unknown node or template, a refused overwrite, a refused
reroll.

## Output formats

`render [--format md|json|toml|html] [--out FILE]`. Default `md`; `--json`
survives as a deprecated alias for `--format json`. Every format writes to
`--out` or, without it, to stdout.

**One document, two serializations.** `json` and `toml` dump the *same*
dict — `document(state)` is built in one place and only the encoder
differs, so the two files can never drift. The document is the state with
its derived numbers resolved: `position_pct`, `share` of the whole book,
`spine_valence` (the curve read at the node's midpoint, next to the
node's own recorded `valence`), and `depth`. Key order is canonical
construction order (`sort_keys=False`).

**Omit-empty is the convention**, so a loader never has to distinguish
null from missing: a key whose value is `None`, `""`, `[]` or `{}` is
dropped entirely. `False` and `0` are real values and survive — an unpaid
promise has no `paid_by` key but keeps `intentional_open: false` when the
gap is not deliberate. This is also what makes TOML, which has no null,
carry the same document as JSON. A stub node has no `children` key at
all; a curve-less spine has no `valence` on its nodes.

TOML nests as arrays of tables — `[[nodes]]`, `[[nodes.children]]`,
`[[nodes.children.children]]` — written by `tomli-w` (stdlib `tomllib`
reads TOML but cannot write it). The writer is imported lazily and
declared both in the script's PEP 723 block and in the project's
`compose` dependency group, which is what `make test-compose` runs
against. A test round-trips a three-level tree through `tomllib` and
asserts equality with the JSON parse.

**`html` is one self-contained static page**: inline `<style>` with CSS
custom properties, light and dark through
`@media (prefers-color-scheme: dark)` on the tokens, a system font stack,
and no scripts, no fonts, no images, no network requests of any kind —
the only `url()` on the page is the internal SVG gradient fragment. It
carries a header (title, premise, kind, spine, arc, target, seed), an
inline SVG of the spine curve with a zero axis and dashed chapter
boundaries, the node tree as nested cards with a signed valence bar and a
status pill per node, the promise ledger as a table whose rows anchor-link
to and from the node cards, and the registry. Levels three and deeper sit
in `<details open>`. Wide content scrolls inside `overflow-x:auto`
wrappers; the page itself never scrolls horizontally.

## Boundaries

- Nothing here writes prose or touches `latex/`.
- No LLM calls, no network. Plain stdlib plus `pyyaml`, PEP 723 inline.
- Titles below level 1 are placeholders derived from the parent's title
  and the child's role (`open`, `develop`, `turn`, `close`). They are
  meant to be renamed; the purpose line carries the actual direction.
- `set` handles `registry.*` and `meta.*` scalars only. Changing
  `meta.words` does **not** rescale existing node budgets — `lint` will
  show the drift, which is the honest behavior for a hand-editable file.
- Depth is capped at 3 by default (`--max-depth`), which is chapter →
  scene/section → beat.
