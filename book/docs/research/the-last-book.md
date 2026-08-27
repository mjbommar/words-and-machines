# Research: `the-last-book` ("The Offline Manual")

Reviewed: 2026-07-06. Source: `/home/mjbommar/projects/personal/the-last-book` (private git repo, master branch).

This is the most architecturally ambitious book project in the personal portfolio: not a manuscript but a **knowledge-graph compiler** that generates books. It is also the project whose docs explicitly state they were *synthesized from the house style of all the other book projects* (`history-through-rfc-book`, `wiki-history-book`, `ai-professional-services-book`, `ai-law-finance-book`, `datacenter-2026-book`), so it doubles as the current best consolidation of the author's cross-project craft standards.

---

## 1. Purpose & status

**What it is.** "The Offline Manual" (working title "The Last Book" — see `docs/decisions.md` #23; the repo dir and `authoring/lastbook.sty` still carry the old name). From `README.md`:

> The one book you would want your family to have if it were the last one they had — and if you weren't there to explain it.
>
> Not a single baked book: a knowledge graph that *generates* tailored artifacts — a printed book, an offline searchable website, and a resource pack for a small local LLM that runs off solar power.

Scope runs "from an 8-hour power outage to restarting civilization," organized along three time **horizons** (disruption / isolation / reconstitution) whose defining discriminator is "is restoration coming?" and whose resource model shifts consume → conserve → produce.

**Status** (from `docs/status.md`, 2026-06-11 — the README's "Status: scaffolding" is stale):

> **Structure: done. Content: substantial and largely verified.** 1,619 authored modules (~1.69M words), 95% verified against current authorities, plus four complete narrative book editions (~969 pp) that build clean and pass their gates.

Actual counts found on disk: **1,710 `.tex` modules** in `corpus/` (409 MB), 15 numbered narrative volumes plus a `prepare-before` prequel under `narrative/`, four narrative volumes fully adapted (Before 186 pp, Water 285 pp, Acute Care 257 pp, Hygiene 241 pp), a 740 MB reference `library/`, and a 13-book children's line under `young-readers/` (67 MB). The binding gap is 74 `needs-review` modules in the human sign-off queue; the safety gate hard-fails any profile that selects them.

---

## 2. Architecture: a structured-knowledge-driven book

Yes — this is fully structured-knowledge-driven. The book is a *projection*; the source of truth is a typed graph of atomic modules. From `docs/architecture.md`:

```
        KNOWLEDGE GRAPH                 corpus/**/*.tex  (LaTeX dialect)
        typed nodes + edges                   │
                                              │  build_corpus.py
                                              ▼
        INTERMEDIATE REPRESENTATION    build/ir/  (markdown+frontmatter, corpus.jsonl, graph.json)
                                              │
                profile (region × hazards × horizon × household × bloom_ceiling)
                                              │  build_profile.py — traverse subgraph, order by prereqs
                                              ▼
        CURRICULUM (ordered module set)
                                              │
                ┌─────────────────────────────┼─────────────────────────────┐
                ▼                             ▼                             ▼
        render/latex  → book.pdf      render/web → dist/ (Astro+   render/rag → pack
        (KDP / Lulu)                  Pagefind, offline)           (embeddings + manifest)
```

The five stated principles (verbatim from `docs/architecture.md`, condensed):

1. **Authoring format ≠ distribution format.** Author in the rich LaTeX dialect; *derive* the lean markdown/JSON. One-way, never round-tripped.
2. **The graph is source; everything else is a projection.**
3. **Stable IDs are the integration.** "A module id is a book page, a web anchor, and a RAG citation at once."
4. **One profile drives every modality** — depth (bloom ceiling from horizon), selection (region × scenarios), output format.
5. **Layers degrade gracefully** — print ⊃ web+search ⊃ local LLM; a higher layer never holds knowledge the layer below lacks.

### The data model, piece by piece

- **`ontology/`** — 12 YAML files of controlled vocabulary; every enum a module can carry validates against one: `strands.yaml` (5 top-level curriculum bands, "ascend together along Maslow ~= horizon ~= social scale"), `domains.yaml` (20), `capabilities.yaml` (~96 seed, 973 in the live graph), `concepts.yaml`, `conditions` (18, so medical `treats` edges have real targets), `horizons.yaml` (3), `bloom.yaml` (cognitive ladder remember→create + affective + psychomotor, each tier mapped to a section macro), `edge-types.yaml` (~15 typed edges: `prerequisite_of`, `enables`, `produces`, `requires_material`, `requires_tool`, `escalates_to`/`if_prolonged` horizon edges, `treats`, `mitigates_hazard`, `substitutes_for`, `taught_by`, `practiced_via`…), `regions.yaml`, `scenarios.yaml`, plus `volumes.yaml`/`volume-sequence.yaml` (the volume split is itself "a PROJECTION of the corpus," with a domain→volume map seeding primary assignment and an embedding pass proposing secondary cross-lists).

- **`schema/module.schema.yaml`** — the module contract, human-readable YAML enforced by `scripts/validate_corpus.py` against the IR. Key excerpt:

  ```yaml
  frontmatter:
    required:
      id:               { type: str,  pattern: kebab-case, must_match_filename: true }
      strand:           { type: str,  enum_from: ontology/strands.yaml }
      domain:           { type: str,  enum_from: ontology/domains.yaml }
      capability:       { type: str,  enum_from: ontology/capabilities.yaml }   # required if kind: skill
      concept:          { type: str,  enum_from: ontology/concepts.yaml }       # required if kind: concept
      scenarios:        { type: list, items_enum_from: ontology/scenarios.yaml, min: 1 }
      regions:          { type: list, items_enum_from: ontology/regions.yaml, min: 1 }
      horizon:          { type: list, items_enum_from: ontology/horizons.yaml, min: 1 }
      reader_floor:     { type: str,  enum: [anyone, basic, trained] }
      time_criticality: { type: str,  enum: [immediate, hours, days, none] }
      danger_if_wrong:  { type: str,  enum: [low, medium, high] }
      verification_status: { type: str, enum: [verified, needs-review, sources-conflict, reference, traditional] }
      last_reviewed:    { type: str,  pattern: "YYYY-MM-DD" }
      provenance:       { type: list, items: provenance_entry, min: 1 }
  ```

  Rules include: `verified` REQUIRES ≥1 provenance entry; `danger_if_wrong: high` SHOULD include an "If it fails / dangers" section; every edge endpoint SHOULD resolve to a node. Three module kinds: **skill** (action-led, documents a capability), **concept** (idea-led), **reference** (list/data/folk).

- **`corpus/`** — THE source of truth: `corpus/<strand>/<domain>/<id>.tex`, one `\begin{module}{id}…\end{module}` fragment per file, 200–1000 words. Notably, **context variants are separate files with a `__` suffix convention**: `co-poisoning-prevention-generators__population-infant.tex`, `__season-winter.tex`, `__horizon-isolation.tex` — the base module plus population/season/horizon specializations.

- **`graph/`** — generated-but-committed unified graph: `master.json` (~1,850 nodes / ~1,781 edges), `backlog.yaml` (**proposed** modules — "backlog ≠ corpus" is called out in `graph/README.md`: the backlog is the map of what to build, never ships), and `keystones.md` — an out-degree ranking that surfaces force-multiplier nodes ("fire, charcoal, lye/soap, wood, glass, smelting") automatically, confirming the tech-tree thesis.

- **`library/`** (740 MB) — the fact-checking reference library, organized by topic, with a license-aware git policy (`library/README.md`): public-domain works tracked; copyrighted works on-disk-only and gitignored; one PD weapons manual force-excluded by policy. Full text extracted to `build/resources-index/` for local fact-check only; a browsable catalog with per-work TOC/summary/coverage lives in `docs/reference-index/`.

- **`registry.yaml`** — a thin top-level index of the platform + its generated editions (profiles), each with id/title/path/region/horizons/status, plus commented-out planned profiles (`wallet-card`, `homestead-library`). Cheap and useful.

- **`research/`** — five per-tradition source reviews (military doctrine, homestead/AT, medicine, scouting/woodcraft, trades) each with `notes.md` + `sources.yaml` + `subgraph.yaml`; `build_graph.py` merges these subgraphs with the ontology into `graph/master.json`. Research → proposal → backlog → authored module, with provenance (`origin`) carried the whole way.

---

## 3. Authoring workflow

### The constrained LaTeX dialect (`authoring/lastbook.sty`, 357 lines)

The single cleverest mechanism in the repo. Modules are authored in a semantic LaTeX dialect that **both typesets the print book directly and is a deterministic parse target**. From the `.sty` header:

```tex
% A constrained LaTeX dialect: it typesets a module AND is the deterministic
% parse target for scripts/tex2md.py. Authors use ONLY the macros below in
% module bodies -- that constraint is what makes conversion lossless.
%
% PARSE CONTRACT (must not change): the *names*, *arity*, and *argument order*
% of \meta, \source, \edge, \mref, \dual, \step, \point, the section macros, and
% the module/steps/points environments are parsed by scripts/tex2md.py. Only the
% typeset *rendering* may change here. New helper macros are fine; renaming or
% re-arging the existing parsed macros is not.
```

Allowed vocabulary (per `CLAUDE.md`): `\meta`, `\source`, `\edge`; section macros `\concept \donow \procedure \resources \analyze \evaluate \verifysec \dangers \why \affective \practice \create` (each mapped to a Bloom tier in `ontology/bloom.yaml`); `steps`/`points` environments; a materials block `\begin{kit}` with `\have{item}{note}` / `\salvage{item}{source}` / `\swap{ideal}{substitute}` (typed items that both render inline AND lift into the IR to feed a cross-cutting Stockpile/Salvage/Substitution appendix via `build_materials_index.py`); `datatable`/`dosetable` with `;`-separated cells and **no math mode** ("formulas as ASCII prose"); `\textbf`, `\emph`, `\mref` (module cross-ref), `\dual{imperial}{metric}`. "No raw LaTeX in bodies — that constraint is what makes conversion deterministic."

The `.sty` also carries edition/feature gates read at print time: `\lastbookedition` (full | family | card — which Bloom tiers render), `\iflbnarrative` (suppress metadata stamps and section labels so a module reads as flowing prose — danger callouts stay, "safety"), a verification badge (`VERIFIED` / `REFERENCE -- not verified` / `TRADITIONAL -- not verified` / `PROVISIONAL`), grayscale-only box palette with FontAwesome icons for B&W print differentiation, and a `\lbwritedanger` hook that accumulates high-danger modules into a `.lbd` file for a front-of-book danger quick-reference (same two-pass mechanism as `.toc`).

### Prose layers on top of modules

- **`narrative/`** — per-volume narrative editions: `prologue.tex`, `epilogue.tex`, `note.tex`, `parts/*.tex` part-openers, `chapters/NN-<slug>/` with `chapter.tex`, per-section adapted prose, and `bridge` environments (cast-driven transitions ~110 words, e.g. "Cast: Maya, Iris"). Governing law from `docs/plans/narrative-layer.md`: "a narrative is a NEW EDITION, not a rewrite of the modules… Instructions live in the verified modules, never invented in narrative."
- **`foundations/`** — Book 2, "the knowledge behind the knowledge": a background-concept graph (`knowledge-graph.yaml`, merged from per-theme agent output in `raw/`), a gap registry, and a Bloom-layered `textbook-outline.md` covering 18 disciplines (chemistry, physics, microbiology, agronomy…). Answers "where is the book thin?" and "what must you understand to own it?"
- **`profiles/`** — scope filters that each generate one edition. `schema/profile.schema.yaml` shows two modes: the **scope-filter** mode (region × scenarios × horizons × strands × reader_floor × bloom_ceiling) and a **curated** mode (`sections:` — an ordered hand-picked reading list that bypasses scope filters but NOT the safety gate; used for the "Prepare Before" readiness volume). Profile build knobs: `include_verification: [verified]`, `show_tiers`, `page_size: 6x9`, artifact derived from horizons (card | manual | library).

### The AI workflow (heavily industrialized)

This is a multi-agent authoring factory, documented as process, not left implicit:

- **Adaptation loop** (`docs/adapt/README.md`): one section = one module, serial, with per-section status tracked by `scripts/adapt_progress.py` through `pending -> drafted -> content-edited -> copy-edited -> reader-ok -> done`. Four agent roles with their own prompt docs: `section-adapter` (Opus, writes the prose), `content-editor` (fidelity to the verified module + rubric), `copy-editor` (STYLE + AI-tells + `check_prose.py`), and `simulated-reader` ("reads it cold as a frightened, untrained person, as a learner, AND as a curious browser who is NOT in crisis — judging want-to-read too: would they turn the page?").
- **Verification loop** (`docs/verification-workflow.md` + `scripts/verify_modules.py` / `revise_with_codex.py` / `review_modules.py`): a tiered, danger-aware policy — low-danger concepts may auto-verify if the fact-check agent (codex + web search) confirms; medium is staged unless `--verify-medium`; **high danger is NEVER auto-verified**, always staged to `build/review/verify-queue.md` for human/expert sign-off. The doc records "the hard lesson (2026-06-09)": *"The first pass is gold"* (caught a fish-calorie table off ~3x, a reversed planting-depth rule) but *"number-dense modules do NOT converge to auto-verified"* — hence **"HARVEST ONCE, then HUMAN SIGN-OFF… The human is verifier-of-record; codex is the error-finder."*
- **Figures** (`scripts/figkit.py` + `figures/manifest/*.yaml`): pure hand-built SVG, one Python generator per figure (`build() -> Figure`), palette mirroring the `.sty`, projected to every edition (inline in HTML/EPUB, cairosvg→PDF for print). Per-volume YAML manifests specify each figure's `depict`, `why`, `data` (every number traced to the module), `fact_source`, `risk`, `confidence`. An automated legibility gate (`check_figures.py`) measures text with cairo and fails on overlapping labels / low contrast. For AI-image-assisted figures there is a judge panel and the "count rule — exact counts go deterministic, AI draws none."

---

## 4. Render / build / publish

### Print (pdflatex, `render/latex/`)

The print build takes the "print shortcut": modules are already LaTeX, so `master.tex` just `\input`s them; `build_corpus.py` only generates the ordering include `generated/_body.tex`. The Makefile parameterizes trim/edition/draft by writing a tiny `generated/_config.tex`:

```make
export TEXINPUTS := ../../authoring:$(TEXINPUTS)
TRIM    ?= 6x9
EDITION ?= full
DRAFT   ?= 0
$(CONFIG):
	@printf '\\def\\lbtrimsize{%s}\n' '$(TRIM)'    >> $(CONFIG)
	@printf '\\def\\lbedition{%s}\n'  '$(EDITION)' >> $(CONFIG)
	@printf '\\def\\lbdraft{%s}\n'    '$(DRAFT)'   >> $(CONFIG)
```

Plus `make validate` (checks output page size in points against the trim), `make kdp` / `make lulu` (spine-width math scaffold), `make draft`.

Geometry and fonts, verbatim from `render/latex/preamble.tex`:

```tex
% Binding-aware margins: a larger inner (gutter) than outer margin for a
% perfect-bound paperback. KDP/Lulu want the gutter to grow with page count;
% 0.875in inner / 0.625in outer is comfortable for a book of this length.
\usepackage[%
  paperwidth=\trimW, paperheight=\trimH,
  top=0.8in, bottom=0.8in,
  inner=0.875in, outer=0.625in,
  headsep=10pt, footskip=24pt,
]{geometry}

\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{microtype}
```

Other preamble features worth stealing: `imakeidx` with `\makeindex[title=Index, intoc, columns=2]` driven from module metadata; `titlesec` chapter format (`{\color{metagray}\large CHAPTER \thechapter}`); fancyhdr running heads (`\leftmark` left, page right, 0.2pt headrule); an **unmissable draft treatment** gated on `\lbdraft`:

```tex
\SetWatermarkText{DRAFT -- UNVERIFIED}%
\fancyfoot[C]{\footnotesize\color{donowred}%
  DRAFT preview -- includes modules not yet verified. Not for field use.}%
```

and a pragmatic hack — `&` made an active character that typesets itself ("There are no tabular/array environments anywhere in the corpus (audited)"), so generated titles like "Sense & Protect" never break the build.

### EPUB (`publish/epub/`)

A full in-repo LaTeX→XHTML converter package (`converter/`: parser, renderer, document, generators, context with a cross-ref pre-pass indexing every `\label`), driven by `build_epub.py`: flatten `master.tex` honoring `\IfFileExists`, split into front-matter/part/chapter segments, render to XHTML, generate `content.opf`/`nav.xhtml`/`cover.xhtml` itself, embed the locked cover PNG, zip with mimetype first/uncompressed. Run line: `uv run --with TexSoup,lxml,typer,rich,pyyaml,cairosvg python publish/epub/build_epub.py water`. A `check_parity.py` guards print/EPUB content parity. **Fonts are embedded IBM Plex** (Serif/Sans/Mono, full weight/style matrix as `@font-face` in `templates/stylesheet.css`), with body:

```css
body {
  font-family: "IBM Plex Serif", Georgia, "Times New Roman", serif;
  font-size: 1em;
  line-height: 1.6;
```

Caveat: the stylesheet header still reads "Rough Consensus - EPUB Stylesheet" — the whole EPUB toolchain was lifted from the predecessor book (`generators.py` is admitted "hardcoded to the htsd predecessor" in `build_epub.py`'s docstring). Evidence that this converter is already a de facto shared asset begging to be templated.

### Covers (`publish/covers/`)

Data-driven series cover system: `theme.yaml` holds shared design tokens with **geometry in fractions of the canvas** (resolution-independent), `covers.yaml` holds one-line per-volume deltas (muted tint color, hero image, growth-stage emblem, glyph):

```yaml
canvas:
  ebook: {w: 1600, h: 2560}          # KDP ebook 1.6:1
type:
  font: "Latin Modern Roman"
  title:    {size: 184}              # auto-shrinks for long titles (layout.py)
geometry:                            # all fractions of canvas w/h
  margin: 0.075
  wordmark_y: 0.072
  ...
```

The series identity device is charming: a "maturing oak" emblem that grows across the 16 volumes (stage 0 acorn → stage 15 oak-from-book). Print covers: `publish/print/kdp-cover.tex` + spine-width computation + ISBN barcode generator.

### Web and RAG (`render/web/`, `render/rag/`)

Both still README-only stubs, but fully designed: Astro 5 + Pagefind offline static site (module ids = URL anchors); RAG pack = `chunks.jsonl` (one chunk per module-section, node/edge metadata as filters) + precomputed `embeddings.f32` + `manifest.json`, "extractive-first," field device does only query-embed + dot product.

---

## 5. Variants: one source, many editions

This project is a masterclass in variant support — **five distinct variant mechanisms**, layered:

1. **Profiles** (edition = scope filter): region × scenarios × horizons × strands × reader_floor, or a curated `sections:` list. Same corpus → wallet card / family manual / homestead library.
2. **Bloom-tier gating at render time**: `make EDITION=card|family` drops deeper tiers per module (card = Apply only). Depth is a *render switch*, not a fork.
3. **Module context variants as files**: the `__population-infant` / `__season-winter` / `__horizon-disruption` suffix convention gives specialized versions of a base module without touching it.
4. **Narrative editions as additive layers**: prologues, preambles, bridges, sidebars stored in a parallel tree (`narrative/<volume>/…`) keyed to volume/chapter ids; the atomic modules are interleaved unchanged. Reference editions simply omit the layer.
5. **`young-readers/` — a full sibling brand** sharing only the verified knowledge: an independent children's/YA line (13 books planned, `book-01-the-poacher-at-birch-lake` …) where "the skill is the tool that solves the case." It replicates the parent's architecture in miniature: `knowledge/` (schemas for book/character/arc/storyboard/world/skill; world bible as data; per-character files with development arcs and "earned permits"), three age bands (K-4 / 5-8 / 9-12) with a difficulty "ladder," a regional "constellation" model, its own `docs/house-standard.md`, its own publish toolchain, and **`forge/`** — a `uv run` CLI with a deterministic management half (`stats`, `validate` — "every skill has a verified_source; the payoff skill solves the case" —, `coverage`, `arcs`, `skillmap`, `report`) and an LLM ideation half (`wheel → generate → gate → judge → rank` over a writing taxonomy). Key inherited rule: "Story motivates; it never instructs. Authority lives only in verified how-to" — real instructions live in a bounded, skippable back-of-book **Field Notes** element, every fact traceable to the parent corpus, but with "no shared-universe branding to the reader."

---

## 6. Testing / QA

Two complementary systems:

**Automated gates** (all runnable via `uv run`, chained in `.github/workflows/ci.yml` on every push):
- `validate_corpus.py` — schema + ontology enum + provenance + section-structure validation.
- `qa_corpus.py` — the *rubric lint*: the `[auto]` half of a 20-question lesson rubric (`docs/lesson-rubric.md`) spanning reader, context dimensions (time of day/season/weather/region/population/scenario/horizon), resource degradation, execution/feedback, danger. Unifying question: "what does this lesson assume, and does it degrade gracefully when that assumption fails?" Includes the "both-worlds-of-help" check.
- `check_prose.py` — prose lint that **reads its banned lists straight from `docs/STYLE-AI-TELLS.md`** (AI-tells + repetition + readability). Doc-as-config: the style guide is the lint ruleset.
- `check_figures.py` — SVG legibility gate (cairo-measured text collisions, contrast).
- `cluster_topics.py --check-planned` — embedding-based near-duplicate topic detector, exit 1 on dupes.
- `build_profile.py` — **the safety gate**: "HARD-FAILS (no output) if any is non-`verified`, stale (`last_reviewed` past `stale_after_days`), or high-danger without a dangers section, then orders by prerequisite topo-sort (cycle = error)." CI pins staleness with `--asof`.
- `tests/` (pytest, 39 tests) — regression tests explicitly written to cover "the bugs the systems/safety reviews found: unquoted-YAML crashes, nested inline markup, list handling, determinism, and the verification/staleness/cycle gate," with a nice `_module(body, **meta)` factory that synthesizes dialect fragments.
- `qa_narrative.py` — verifies verbatim tables/kits survive narrative adaptation.

**Adversarial review** (`review/`): three lens reviews (safety-trust, content-pedagogy, systems) written by review agents under a strict output contract (`review/README.md`): Verdict → Strengths → **Broader** (what is the project blind to?) → **Deeper** (cite `file:line`) → Expand & densify → Improve → Organize → P0/P1/P2 table with effort estimates. Rules: "Stay in your lens… Write ONLY `review/<lens>.md`… Propose; do not rewrite the repo." The safety review's verdict — *"the thinking here is unusually good and the enforcement is not there yet… 'nothing unverified ships' is a doc sentence with no code behind it"* — directly drove Phase 0.7 hardening in the roadmap, i.e., the review process demonstrably converted aspirations into enforced gates. There was also a six-lens holistic review of the finished narrative volumes (copy/content/fidelity-safety/novice/expert/voice) producing a tracked punch-list.

---

## 7. Scripts & dependencies

**`pyproject.toml`** is astonishingly lean for the scale:

```toml
requires-python = ">=3.11"
dependencies = [
    "pyyaml>=6.0",
    "cairosvg>=2.7",   # render hand-built SVG figures to PDF for the print builds
]
[tool.ruff]
target-version = "py311"
line-length = 100
```

Heavier deps are pulled ad hoc via `uv run --with` (pytest, TexSoup, lxml, typer, rich, kaos-nlp/kaos-graph for embeddings). Everything runs through `uv`; no lockfile bloat, no environment drift.

**`scripts/`** (~70 scripts) by function:
- *Pipeline spine*: `build_corpus.py` (tex→IR: md + corpus.jsonl + graph.json — "the hinge"), `tex2md.py`, `validate_corpus.py`, `build_profile.py` (safety gate + topo order), `build_graph.py`, `build_rdf.py`, `stats.py`.
- *Editions*: `build_narrative.py`, `build_foundations[_book].py`, `build_tier_b.py`, `build_toc.py`, `build_markdown.py`, `build_web.py`, `profile_to_sequence.py`, `assemble_sequence.py`, `assign_volumes.py` / `sequence_volumes.py` / `renumber_volumes.py`, `build_materials_index.py`.
- *QA*: `qa_corpus.py`, `qa_narrative.py`, `qa_fix.py`, `check_prose.py`, `check_figures.py`, `cluster_topics.py`, `cluster_resources.py`.
- *AI author/verify loop*: `new_module.py` (scaffolder), `author_lessons.py`, `review_modules.py`, `revise_modules.py`, `revise_with_codex.py`, `verify_modules.py`, `adapt_progress.py`, `narrative_context.py`, `plan_to_backlog.py`.
- *Figures*: `figkit.py` (+ `figkit_decision/scale/table`), `figure_pipeline.py`, `figures/` (one generator per figure), `build_figures.py`, `apply_figures.py`, `engrave_figures.py`, `judge_figures.py`, `figure_gallery.py`, `contact_sheet.py`, `count_panel.py`, `gen_manifest_from_specs.py`.
- *Library*: `index_library.py`, `organize_library.py`, `build_reference_catalog.py`, `index_resources.py`, `extract_book_toc.py`, `ocr_frontmatter.py`.
- *Misc*: `backup.py`, `retitle_chapters.py`, `title_fix.py`, `gen_cover_emblems.py`, `rewave.sh`.

---

## 8. Style & craft guides

`CLAUDE.md` (11 KB) and `AGENTS.md` (6 KB) are near-duplicates — CLAUDE.md is the fuller one (AGENTS.md lags: e.g. it lists two module kinds where CLAUDE.md lists three, and has a copy-pasted duplicated sentence). Both are structured as: name/branding note → "What this is" → **The prime directive** → rubric → authoring → build commands → conventions → open decisions. The prime directive:

> Every module must be usable by a frightened, untrained person — possibly a child, with the author absent — and must never present unverified advice as authoritative.

With the "both worlds" corollary: "Calling for help is never the only answer; self-rescue is never the only answer."

`docs/STYLE.md` — "the calm expert" voice, with four load-bearing consequences: (1) "Clarity is a safety property, not a stylistic preference"; (2) "Authority lives only in verified modules… narrative prose connects, motivates, and explains — never instructs. This is the load-bearing line of the whole project"; (3) name assumptions/both-worlds; (4) "Engagement is a safety property too. Unread knowledge saves no one." Includes sentence craft, rhythm, ASCII/dual-units/ISO-dates rules, per-edition voice deltas, and a prose-editing checklist. Explicitly synthesized (2026-06-06) from the author's other book projects — **this file is the closest thing to a ready-made master template STYLE.md that exists**.

`docs/STYLE-AI-TELLS.md` — the enforceable "do not write like this" companion: banned words/phrases, syntactic tells with named rules and quotas ("This" disease — "at most one 'This' opener per paragraph; never in consecutive sentences"; the gerund opener — "at most one per page"; the "As X, Y" construction; the compulsive triple), structural tells, repetition/fatigue patterns. Machine-read by `check_prose.py`. Framing: "AI prose is smooth, uniform, and predictable — low burstiness, low perplexity… the tells are almost all padding, and padding is the enemy of a frightened reader."

`docs/` overall is a 30+ file design corpus with a prescribed reading order (`docs/README.md`), split into **enduring design** (vision → horizons → taxonomy → bloom → knowledge-graph → architecture → module-schema → authoring-dialect → outputs → figures → rag → sourcing → safety) and **live planning state** (status, decisions log, reviews, mvp, roadmap). The **decisions log** (`decisions.md`, numbered entries with rationale, cross-referenced from code comments as "#21", "#23") and the **living status.md with regeneration commands** are both excellent practices. The **sourcing ethic** is spelled out twice over: paraphrase-only even for public domain, citation as "an ethical obligation, not optional," reference images gitignored/never shipped, figures "original drawings *informed by* them, not copies."

---

## 9. Verdict: what belongs in a master book template

### Steal wholesale (high value, low weight)

1. **One source of truth → deterministic fan-out** with the explicit principle "authoring format ≠ distribution format, one-way, never round-tripped." Even a plain prose book benefits from the print/EPUB/web triple sharing one source and one `_body` include.
2. **Stable IDs as the integration layer** (chapter/section/module id = anchor = citation = cross-ref target). Trivial to adopt, pays everywhere.
3. **The constrained-dialect idea with a written PARSE CONTRACT.** Whether the dialect is LaTeX or Markdown+frontmatter, the template should declare: authors use only this macro/element vocabulary; names/arity are frozen; only rendering may change. That single comment block is what makes N output formats safe.
4. **The Makefile → `generated/_config.tex` switch pattern** (`TRIM/EDITION/DRAFT`) with `\providecommand` fallbacks, `TEXINPUTS` export, and `make validate` page-size check. Directly reusable.
5. **The preamble geometry block** (6x9/7x10 parameterized, gutter-aware `inner=0.875in / outer=0.625in`), the draft watermark + footer treatment, and the indexed/fancyhdr/titlesec setup. Battle-tested KDP defaults.
6. **The covers system**: `theme.yaml` (tokens, fraction-based geometry) + `covers.yaml` (per-volume one-liners) + a Python compositor. The cleanest data-driven series-cover approach I've seen in these projects.
7. **The EPUB converter package** — it has now shipped two different books (htsd/"Rough Consensus" and this one) with admitted hardcoding each time. It is *the* prime extraction candidate for the template: parameterize `generators.py`, keep the flatten/split/xhtml/opf/zip driver, embedded IBM Plex fonts, `check_parity.py`.
8. **STYLE.md + STYLE-AI-TELLS.md + `check_prose.py` reading its rules from the doc.** The doc-as-lint-config pattern means style is enforced, not aspirational. These two files are already cross-project syntheses; the template should carry them (with the survival-specific safety framing made pluggable).
9. **The adversarial review harness** (`review/README.md` output contract + lens files) and the **multi-role adaptation loop** with per-unit status tracking (`adapt_progress.py`: drafted → content-edited → copy-edited → reader-ok → done). Both are book-agnostic AI workflow gold; the "simulated reader who judges would-they-turn-the-page" role generalizes to any book.
10. **Project hygiene**: numbered decisions log, living status.md with regenerate commands, docs reading order, `registry.yaml` edition index, lean pyproject + `uv run --with` for heavy optional deps, CI running the full build+gate chain.
11. **The `uv run --with pytest` regression-test pattern** with a fragment-factory helper, testing the *pipeline* (determinism, escaping, gates), not the content.

### Adopt selectively (valuable for some books)

- **Profiles/editions as data** (scope filter or curated `sections:` list → one generated edition) and **render-time depth gating** — essential the moment a template must support abridged/variant editions (the stated goal). The curated-`sections` mode alone covers most "abridged edition" needs without any ontology.
- **The `__variant` filename suffix convention** for context-specialized versions of a unit — a very cheap variant mechanism.
- **Narrative-as-additive-layer** (prologue/preamble/bridge files in a parallel tree keyed to structure ids, interleaved at build) — the right pattern for any project wanting both a reference edition and a readable edition from one source.
- **The figures manifest** (per-figure `depict/why/data/fact_source/risk/confidence`) and the SVG-single-source + cairosvg projection + automated legibility gate — for any technical/illustrated book.
- **Tiered human-in-the-loop verification** ("harvest once, then human sign-off"; high-danger never auto-verified) — for any nonfiction book with factual risk, this is the honest model; the general lesson (LLM as error-finder, human as verifier-of-record; don't loop to convergence) transfers everywhere.
- **License-aware reference library policy** (PD tracked / copyrighted gitignored / paraphrase-only / citation obligatory) — transfers to every nonfiction project.

### Overkill for a general template

- The **full ontology stack** (12 vocabularies, capabilities/conditions/edge-types, RDF export, keystone analysis). It earns its keep only because this corpus is 1,710 interlinked modules across 16 volumes serving generated curricula. A template should ship at most a minimal `ontology/` slot (tags + one edge type) with this project cited as the maximal case.
- **Graph-traversal curriculum ordering, the RAG pack, the offline Astro site** — projections specific to the survival-knowledge mission.
- **The 20-question lesson rubric and both-worlds doctrine** — safety-of-life framing; generalize only its skeleton ("what does this unit assume, and does it degrade gracefully?") as an optional QA idea.
- **The young-readers forge** — a whole second product line; mine it for the schema-driven series-bible idea (characters/arcs/world as validated data) if the template ever targets fiction series.

### Pitfalls observed (things the template should avoid or fix)

- **CLAUDE.md / AGENTS.md duplication drift** — AGENTS.md is already stale vs CLAUDE.md (missing the `reference` kind, duplicated sentence). The template should make one the source and generate/include the other.
- **Stale README status** ("Status: scaffolding" vs 1.6M words shipped) — status belongs in one regenerable file only.
- **Copy-paste toolchain hardcoding** — the EPUB generators "hardcoded to the htsd predecessor," the stylesheet still titled for the previous book. Exactly the problem the master template exists to solve: extract once, parameterize by metadata.
- **Name/rename debt** — brand changed but `lastbook.sty`, repo dir, macro prefixes didn't; the template should keep brand strings out of file/macro names (use a neutral prefix).
- **Build artifacts committed** in `render/latex`/`render/foundations` (`.idx`, `.ilg`, `.aux`, `texput.pdf`) despite "build/ is gitignored" — the template's gitignore should cover per-render-dir aux files.
- **Aspirational-vs-enforced gap** — the safety review's core finding. The template lesson: any promise in docs ("nothing unverified ships") must name the script that enforces it, and CI must run that script. This repo eventually did exactly that; the template should start that way.
