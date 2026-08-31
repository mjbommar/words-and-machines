# AI Instructions (canonical — ADR 0012)

This is the single source of AI instructions for this book project.
AGENTS.md and GEMINI.md are pointers here; never let them diverge.
`make doctor` audits this file: every target/script referenced must exist.

## This book

*Instruction Sets, Programs, and Proofs* explains how to establish claims about instruction sets that a
reader can check. Its reader is a compiler, crypto-engineering, or
formal-methods practitioner who is comfortable with code and willing to learn
the mathematics, but has not already accepted the book's vocabulary or its
conclusions.

Build the common machine before introducing a named ISA: words, registers,
memory, state, operand forms, and instructions as transformations. Treat RISC
and CISC as clusters of concrete design choices, not complete semantics or
rival essences. Use RISC-V and x86-64 as sustained contrasts, and introduce
optional extensions only at a declared model boundary.

The prose is precise, dry, and occasionally amused. It must pass the
kitchen-table test; the objects must pass the blackboard test. Read
`docs/SPIRIT.md`, `docs/guides/VOICE.md`, `docs/guides/CRAFT.md`, and
`docs/guides/PLAIN-ENGLISH.md` before drafting or editing. These book-specific
guides take precedence over a generic template convention where they differ.

The manuscript completed its first sequential breadth-and-depth pass on
2026-08-30. Continue with whole-book technical and editorial review, and reopen
individual chapter contracts when evidence exposes a gap. For every major
concept, connect its sourced historical
origin, its mathematical, logical, physical, or computational foundation, and
its current practical industrial or economic consequence. Put each connection
where it explains the concept; do not append generic history and industry
boxes. A word band, page count, successful build, or complete table of
contents does not establish adequate breadth or depth.

## Project map

| Where | What |
|---|---|
| `book.yaml` | Single source of truth: title, author, ISBNs, trim, editions, keywords (ADR 0002) |
| `latex/chapters/` | Canonical content — the only place prose lives |
| `latex/generated/`, `build/` | Machine-written — **never edit, never commit** |
| `docs/architecture/authoring-contract.md` | The complete LaTeX vocabulary chapters may use |
| `docs/guides/` | VOICE, CRAFT, PLAIN-ENGLISH, and INDEX-GLOSSARY (book authority); inherited STYLE, STYLE-CRAFT, STYLE-AI-TELLS, SIMPLIFIED-ENGLISH, WRITING-PROCESS, CITATIONS, REVIEW-QA, RESEARCH, VOICE-MODELS, ONTOLOGY; `styles/` = genre profiles (`style.profile`) |
| `scripts/data/simplified_english/` | Simplified Book English: corpus-derived word tiers + curated substitution policy (guide: `docs/guides/SIMPLIFIED-ENGLISH.md`, derivation: `docs/architecture/simplified-english.md`) |
| `scripts/data/ontology/` | Writing ontology: 20 branch files, macro arcs → micro constructions (design: `docs/architecture/writing-ontology.md`, usage: `docs/guides/ONTOLOGY.md`) |
| `outline/composition.yaml` | Outline-composer state: registry, spine, node tree, promise ledger — canonical, hand-editable, committed (design: `docs/architecture/outline-composer.md`) |
| `docs/publishing/` | KDP runbook, metadata dossier, release checklist, cover spec, narration channels |
| `research/`, `outline/`, `notes/` | Research folders (README contract), outline, working notes |
| `docs/review-NN/` | Review-round findings and synthesis |

## Axeyum is the evidence stack

The book's solver-backed objects are produced or checked by the sibling
repository `../axeyum` (relative to this repository's root). Before saying
what axeyum can prove, reconstruct, check, or not do, inspect its current code
and tests. The copied material in `../research/axeyum/` records provenance; it
does not establish the present capability.

For a book change that affects a solver-backed object or its explanation:

1. Read the matching route in `../axeyum-guide/` and inspect the named crate
   and example in `../axeyum`.
2. From the repository root, set `AXEYUM=../axeyum` and run
   `$(MAKE) check-run`. This checks the positive evidence and the negative
   control. The required release-example build commands are in
   `../axeyum-guide/05-reproduce.md`.
3. Record the route, scope, and limitation in the object. In prose, describe
   only the result that this evidence supports.

The sibling checkout is evidence infrastructure, not a source of decorative
technical language. Do not edit it unless the assigned task explicitly includes
an axeyum change.

The current reader-facing Python surface includes complete concrete A0 words,
memory, states, state encoding, all seventeen instruction families, traps,
single steps, and bounded traces. It also includes complete selected single-step
projections for the source-pinned RV64I and x86-64 teaching slices: typed
instructions, canonical encode/decode, complete state, traps, and state
projection. Run the exact manuscript examples with
`AXEYUM=../axeyum make machine-example-check` from the repository root. Do not
describe real-ISA bounded traces or cross-machine Python relations as implemented.

## Hard rules

1. **Never edit `latex/generated/` or `build/`.** They are regenerated from
   `book.yaml` by the build; edits there are silently destroyed.
2. **Never introduce literal title/author/ISBN strings** in LaTeX, EPUB, or
   cover sources. Use the metadata macros (`\BookTitle`, `\BookAuthor`, …)
   from `latex/generated/metadata.tex`.
3. **Chapters use ONLY the authoring contract**
   (`docs/architecture/authoring-contract.md`). No raw TikZ, manual spacing,
   `\newcommand`, or low-level TeX in chapter files. `make check` and the
   EPUB coverage audit enforce this.
4. **Every claim that needs a source gets a verified citation.** Open and
   read the actual source before citing; `uv run scripts/verify_citation.py`
   checks reachability and stamp coverage (`--key`, `--unused`, `--stamp`),
   but confirming the source says what the prose claims is your job. Stamp
   `verified = {YYYY-MM-DD}` in `references.bib` only after reading. Never
   mark verified from a search snippet or memory. See `docs/guides/CITATIONS.md`.
5. **Reviewers never edit.** Persona-review agents produce scored findings;
   only revision work applies changes, from a synthesized fix brief.
6. Fix briefs assign **non-overlapping files** to parallel editing agents;
   run `make check` after parallel edits to catch cross-chapter repetition.
7. Don't hand-type build stats or metadata into prose or docs — derive them
   (`make stats`, `book.yaml`).
8. **Use the book's language contract.** Explain a new technical term in
   ordinary words before it does load-bearing work; retain the exact term after
   that. Give every material claim its subject, scope, evidence route, and
   limit. Do not let an artifact box, an object status, or a citation stand in
   for the explanation.
9. **Pair understanding with verification.** Before an artifact box carries a
   result, give the reader a concrete problem and a human-scale reason the
   result should hold. After it, show how the evidence can fail and state the
   boundary. See `docs/guides/CRAFT.md`.
10. **Earn the reader's wonder.** Let a proved relation, a finite object with
    universal reach, or an honest limit open onto the larger mystery of
    computation. Move from exact object to consequence; do not announce that
    something is beautiful or mysterious in place of showing why. Keep every
    historical or literary connection brief, exact, and verified. See
    `docs/guides/VOICE.md` and `docs/guides/CRAFT.md`.
11. **Research breadth before expanding prose.** For each chapter, compare the
    draft with authoritative ISA specifications, relevant course expectations,
    and at least two substantial textbooks. Its research contract must route
    every neighboring topic: derive here, work here, route to another named
    chapter, or exclude explicitly. Historical firsts need primary evidence;
    current prices, performance, market, energy, and manufacturing claims need
    dated sources and declared units.
12. **Maintain navigation as you write.** Keep the four-part spine and public
    Part--Chapter--Section hierarchy stable. Update `glossary.yaml` and curated
    `\indexentry` locators during each chapter revision. See
    `docs/guides/INDEX-GLOSSARY.md`; run `make structure` before building.
13. **Treat every code listing as runnable.** A future API belongs in prose,
    not a syntax-highlighted box. The repository-level `make code-check`
    parses A0, assembles RV64I and x86-64, verifies printed addresses, and
    rejects Python without a declared execution harness. Add the harness and a
    mutation control before adding a new executable language listing.

## Build targets (complete vocabulary — see docs/architecture/build-system.md)

| Target | What it does |
|---|---|
| `make pdf` / `make quick` | Print PDF (quick = single fast pass) |
| `make bleed` / `make ebook` / `make grayscale` / `make draft` | Mode variants |
| `make epub` / `make epub-check` | EPUB 3 + epubcheck / strict coverage audit |
| `make epub-a11y` | Ace by DAISY accessibility audit (fails on serious/critical) |
| `make cover-vars` | Page count → spine → `latex/generated/cover-vars.tex` |
| `make kdp-cover` / `make lulu-cover` / `make cover-image` | Wrap covers, Kindle raster |
| `make check` | Style + prose checkers on `latex/chapters/`; also runs the repository code-listing gate |
| `make structure` | Four-Part spine, heading hierarchy, title-length, and chapter-ending gate |
| `make preflight` | Font-embedding + image-DPI gates on interior and cover PDFs |
| `make cover-ink` | Cover total-ink (TAC ≤ 240%) gate |
| `make pdfx` | PDF/X-1a interior for IngramSpark/Lulu (KDP uses `make pdf`) |
| `make onix` | ONIX 3.0 metadata feed from `book.yaml`, onixcheck-validated |
| `make narration-export` | Per-chapter plain text for AI narration (`docs/publishing/NARRATION.md`) |
| `make verify-citations` | URL reachability + `verified=`/`archived=` gates (runs in `make release`; `--archive` pins Wayback snapshots) |
| `make stats` | Word counts + deltas (`book_stats.py`) |
| `make vocab` | OpenGloss vocabulary-variety ideation report — overuse, per-sense synonyms with usage examples, `--suggest-bans` profile candidates, optional OGBert `--embed` re-ranking (advisory; `vocab_variety.py --help`) |
| `make metrics` | Burstiness + lexical-diversity metrics per chapter (`prose_metrics.py`, advisory) |
| `make prose-report` | One-command quality report: metrics vs house baseline, slop signals, vocab overuse + ban candidates, optional `--pangram`/`--deslop N`, with round-over-round deltas (`prose_report.py`, advisory) |
| `make ontology` | Writing-ontology stats + schema lint (`writing_ontology.py`; also the loader/sampler library and browse CLI — `show`, `sample`) |
| `make craft` | Macro-to-micro craft diagnostics on chapters: construction variety, figure detection, rhythm/cadence, register, arc profile vs target shape, setup/payoff ledger, discourse-move coverage (all advisory; see `docs/guides/ONTOLOGY.md`) |
| — (no target) | Ontology generative CLIs — `prompt_roller.py` (ideation), `beat_scaffold.py` (outline scaffolds from 75+ beat templates), `palette_sampler.py` (drafting/deslop construction palettes), `variation_engine.py` (recast-directive sets for a passage), `exercise_generator.py` (progymnasmata drills), `objection_engine.py` + `sparring_partner.py` (argument red-team; `--llm` optional), `outline_composer.py` (stateful outline cascade: `init` → `deepen` → `lint` → `render`, state in `outline/composition.yaml`; children conditioned on the parent and the arc curve, deepening one node never touches its siblings) |
| `make slop` | Multi-level slop audit — quantitative signals + 54-tell LLM judge with unit sampling (`slop_audit.py --llm --unit … --sample …`, OpenAI or Anthropic via pydantic-ai; advisory) |
| `make pangram` | Pangram 4 AI-detector cross-check per chapter (`pangram_check.py`; needs `PANGRAM_API_KEY`; sends `model=pangram-4`, v3 deprecates 2026-09-30; `--api auto` = realtime for small runs, bulk queue for large; advisory). **Read `fraction_ai` as a verdict, never as a score** — it is 1-bit on single paragraphs; the continuous signal is `windows[].ai_assistance_score` (VOICE-MODELS.md §1b) |
| — (no target) | `scripts/deslop.py` — voice-model rewrites for revision: A/B variants, `--batch` fix briefs, and `--candidates N` (the automated §7 loop: N variants scored by faithfulness + quant slop + the *continuous* Pangram window score, ranked best-first), `--fewshot` (exemplars picked by detector verdict), `--notes` (regenerate from extracted facts), `--servers` (pool across endpoints). Needs a locally served author-voice GGUF — any OpenAI-compatible endpoint (auto-probes :8091 then :8092; model guidance in docs/guides/VOICE-MODELS.md, workflow in REVIEW-QA §7) |
| — (no target) | `scripts/rewrite_chapter.py` — whole-chapter rewrites through hosted models (GPT-5.6, Opus 5, Gemini 3.7, GLM 5.2, DeepSeek V4 Pro), one file per model for side-by-side comparison. The chapter-scale, hosted sibling of `deslop.py`: use that for paragraph ideation on a local voice model, this to hear a whole chapter in a different voice. `--brief-file` sets the direction, `--anchors` the bench, `--dry-run` prints the prompt for free. Guardrails run inside the retry loop and every rejected sample is kept as `.REJECTED.tex` — see the module docstring. **Never overwrites a chapter** — it writes candidates to `--outdir` and you choose |
| — (no target) | `scripts/phrase_check.py` — provenance spot-check: do long spans of the book appear verbatim in a 4.3T-token corpus (Ai2 infini-gram)? Answers "does my text contain someone else's words", not "does a detector call this AI". Free, no key — **serial + throttled by design**, see `docs/guides/PROVENANCE.md` |
| `make simplified` | Simplified Book English vocabulary report — unapproved words/phrases, terms used without an introduction, undefined abbreviations, declared-term drift; `% sbe-ok:` suppresses a line (`check_simplified.py`; `--terms`, `--glossary`, `--emit-config`, `--stats`, `--advisory`, `--explain`, `--strict`; advisory, not in `make check`) |
| `make simplified-lexicon` | Rebuild `scripts/data/simplified_english/lexicon.json` from 9 reference corpora + OpenGloss + `curated.yaml` (`build_simplified_lexicon.py`) |
| `make test-simplified` | SBE checker regression fixtures: first-use ordering, input-graph scope, glosses, names/codes, expansions, and policy grades |
| `make test-compose` | Outline-composer regression fixtures: determinism, idempotent deepening, budget partition, promise lint, fault/descriptor-bank exclusion |
| `make calibrate-simplified` | Current Markdown scorecard and term/abbreviation/substitution queues for the nine held-out sibling books (`calibrate_simplified.py`; `--format json`, `--projects-root`) |
| `make doctor` | Toolchain, placeholders, cover-vars freshness, this file's target audit |
| `make validate-all` | Everything above that gates a release |
| `make release` | `validate-all` → `releases/<date>-<printing>/` + SHA256SUMS |
| `make watch` / `make clean` | Rebuild loop / remove outputs |

Editions: `make pdf EDITION=<name>` (declared in `book.yaml`, ADR 0011).

## Writing workflow

Full workflow: `docs/guides/WRITING-PROCESS.md`. Summary:

```
research → outline → draft → edit (content, then copy) →
review panel (scored, no edits) → synthesize → revise → verify → polish
```

- Read `docs/SPIRIT.md`, `docs/guides/VOICE.md`, `CRAFT.md`,
  `PLAIN-ENGLISH.md`, `STYLE.md`, `STYLE-AI-TELLS.md`, and
  `SIMPLIFIED-ENGLISH.md` **before** drafting; run `make check` after and
  `make simplified` when terminology changes.
- Explain necessary jargon and unusual or restricted uses at first authorial
  use. `\keyterm{}` identifies a defining occurrence but still needs an inline
  explanation or a real glossary definition; `book.yaml` records terminology
  policy, not reader comprehension (SIMPLIFIED-ENGLISH.md §5).
- Cite as you write — never leave citations "for later".
- Each review round lives in `docs/review-NN/`; run `make stats` before and
  after to quantify the round.

## Agents (`.claude/agents/`)

| Phase | Agent | Role |
|---|---|---|
| Research | `researcher` | Fill research folders with sourced, verified material |
| Planning | `outliner` | Chapter outlines and structural balance |
| Drafting | `chapter-drafter` | Outline → prose within the authoring contract |
| Editing | `content-editor` | Structure, pacing, argument (developmental) |
| Editing | `copy-editor` | Line edits, consistency, mechanics |
| Enforcement | `style-enforcer` | STYLE/AI-TELLS conformance, runs the checkers |
| Verification | `fact-checker` | Claims vs. sources |
| Verification | `citation-verifier` | URL/metadata verification, `verified=` stamps |
| Review | `reviewer-trade-critic` | Persona review, scores rubric, never edits |
| Review | `reviewer-domain-expert` | Persona review, scores rubric, never edits |
| Review | `reviewer-general-reader` | Persona review, scores rubric, never edits |
| Synthesis | `review-synthesizer` | Panel findings → prioritized, non-overlapping fix briefs |

## When you finish a session

1. `make check` — style/prose gates green (or violations listed for the user).
2. `make stats` — record word-count deltas.
3. Update the project TODO / research trackers with what changed and what's next.
4. If you touched anything the build derives from, run the relevant target
   (`make pdf`, `make epub`) and report failures honestly.
