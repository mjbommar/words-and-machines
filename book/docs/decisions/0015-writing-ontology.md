# ADR 0015 — Writing ontology and craft tooling (advisory, generative)

## Decision
- **A controlled craft vocabulary ships as data**, not as prose advice:
  `scripts/data/ontology/*.json`, one branch per file (23 today), each
  declaring `name`, `level` (macro | meso | micro), `entry_type`
  (`term` = strings, `record` = objects), `description`, and `categories`.
  Records require `name` + `definition`; `example`, `effect`, `register`,
  `caution`, `aka`, `tags` are recommended where they apply, and structured
  extras carry the machine-readable part (`beats` on arrangements, `curve`
  on arc shapes, `critical_questions` on argumentation schemes, `pattern` /
  `renderings` on constructions, `cues` where a tool matches text).
  `scripts/writing_ontology.py lint` (`make ontology`) is the schema gate;
  entries are **established, nameable craft concepts** — Lanham's figures,
  Walton's schemes, Hyland's metadiscourse, the cursus, the progymnasmata —
  never invented jargon.
- **Everything built on it is advisory.** No ontology tool gates a release
  and none appears in `validate-all`; the six threshold diagnostics carry
  `--strict` for local use only, and `move_annotator`, `objection_engine`,
  and `sparring_partner` have no `--strict` at all. **No tool edits prose**:
  generative scripts emit prompts, palettes, and scaffolds; diagnostics emit
  reports; humans (or a `deslop.py` pass) apply changes.
- **Aspect ownership** is the dedup rule: a concept lives once *per aspect*,
  and the branch owning the aspect owns the entry (figures own the
  figure-as-figure, sound owns its prosodic realization, syntax owns it only
  when there is a grammatical pattern to state). Legitimate splits carry
  `aka`/`see_also` both ways; cosmetic renames are duplicates and get cut.
- **Descriptor banks are separated from craft branches.**
  `settings_and_environments` and `tones_and_moods` are concrete-noun and
  atmosphere banks that fuel ideation only; palette and variation sampling
  never draws from them.
- **Polarity is explicit.** Records may carry `polarity: virtue | fault |
  neutral`. A *fault* names a failure mode: samplers must never emit one as
  a positive drafting directive — faults exist as audit targets.
- **Integration follows the house pattern**: `make ontology` (stats + lint),
  `make craft` (the diagnostic suite), `make brief` (the round's craft
  brief); the generative CLIs are documented without targets, like
  `deslop.py`. Genre profiles tune the profile-aware diagnostics through the
  existing ```style-targets``` block (ADR 0009's doc-as-lint-config), so
  thresholds live with the register that justifies them. Design:
  `docs/architecture/writing-ontology.md`; usage: `docs/guides/ONTOLOGY.md`.

## Rationale
The template's prose tooling was complete on the *negative* side — banned
lists and AI-tell patterns (ADR 0009), burstiness and lexical diversity
(`make metrics`), vocabulary ruts (`make vocab`), slop taxonomy
(`make slop`), external detection (`make pangram`). Every one of them says
what is flat, overused, or machine-shaped; none says what to write instead.
A writer who is told "opener monotony, run of six" needs the *space of named
alternatives*, and so does a drafting model — a palette of named
constructions changes a draft in a way that "vary your sentences" does not.

The shape is borrowed from the story-generator's descriptor sets: controlled
vocabularies plus seeded sampling plus provenance, so a good roll is
reproducible and a bad one is diagnosable. Applied to prose, the
vocabularies become craft taxonomies rather than scene descriptors — which
is why the two descriptor banks that *are* scene-like are fenced off from
the craft samplers.

Naming everything with established terms is what makes the output
assignable: a fix brief that says "recast as a periodic sentence" or "this
run needs a concession move" survives the handoff between a synthesizer, an
editing agent, and a human in a way that ad-hoc description does not.

## Consequences
- New: 23 branch files under `scripts/data/ontology/`, 16 scripts (the
  loader, five generative samplers, six diagnostics, three LLM-optional red
  teams, and `craft_brief.py`), the `ontology` / `craft` / `brief` targets,
  `docs/guides/ONTOLOGY.md`, and the design doc.
- The workflow is wired end to end: ideation and scaffolding in
  WRITING-PROCESS Phases 2–3, `make brief` as pre-round evidence and
  post-round delta in REVIEW-QA §2/§8, measurement pointers in STYLE-CRAFT,
  a drafting palette for `chapter-drafter`, structural templates for
  `outliner`, developmental and line-level diagnostics for the two editors,
  an advisory-only sweep for `style-enforcer` (craft WARNs are never gates),
  citable evidence for the three reviewers, and ontology names as the
  directive vocabulary for `review-synthesizer`.
- Growing the data sharpens the tools without touching their code:
  `register_report` and `move_annotator` merge a branch's `cues` lists into
  their lexicons at runtime, and `figure_detector`, `construction_variety`,
  `rhythm_audit`, and `arc_profiler` degrade to a shorter report when a
  branch is absent.
- Costs accepted: the data is now the largest artifact in the repo and needs
  lint discipline; the diagnostics are heuristic by design (lexicon valence,
  POS-lite syntax, orthographic figure matching), so a flag is a prompt to
  reread, never a verdict; and the LLM-optional tools need an API key,
  falling back to cue lexicons and templates without one.
