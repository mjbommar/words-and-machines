<!-- ============================================================
CLAUDE.md TEMPLATE — copy this file to the repo root as CLAUDE.md
when you start a book, then:
  1. Fill in every ⟨bracketed⟩ value in "This book".
  2. Delete this comment block and any section that doesn't apply.
  3. Keep AGENTS.md and GEMINI.md as one-line pointers to CLAUDE.md
     (ADR 0012) — never let them diverge.
  4. Run `make doctor` — it audits that every build target this file
     mentions actually exists in the Makefile.
Everything below travels with the repo: the guides, scripts, and
targets referenced here ship in docs/, scripts/, and the Makefile.
============================================================ -->

# AI Instructions — ⟨Book Title⟩

This is the single source of AI instructions for this book project.
Read "This book" before writing a word of prose; obey "Hard rules"
always; use the rest as the operating manual.

## This book

- **Premise (one quotable sentence):** ⟨the thesis — if it takes two
  breaths, it isn't the thesis yet⟩
- **Reader & register:** ⟨who is this for?⟩ — read-aloud test:
  ⟨coffee | kitchen-table | neighbor⟩ (definitions: STYLE.md §1)
- **Style profile:** ⟨narrative-nonfiction | practical-guide |
  technical-handson | young-readers | verse-translation⟩ — set the same
  value in `book.yaml` `style.profile`; the profile in
  `docs/guides/styles/` defines POV, structure, and lint deltas
- **Voice:** ⟨three adjectives, e.g. "dry, precise, quietly amused"⟩;
  mentor authors for feel, not formula: ⟨e.g. Kidder, McPhee⟩
- **Comparable titles:** ⟨2–3 comps and what this book does differently⟩
- **Emotional threads:** see `docs/SPIRIT.md` (create it from
  `docs/guides/SPIRIT-TEMPLATE.md` **before drafting**; every drafting
  or review prompt starts with "read SPIRIT.md first")
- **Status:** ⟨phase — research | outline | draft | review round N⟩;
  current chapter state lives in `outline/` and the project TODO

## Project map

| Where | What |
|---|---|
| `book.yaml` | Single source of truth: title, author, ISBNs, trim, fonts, editions, keywords, DRM, AI disclosure (ADR 0002) |
| `docs/SPIRIT.md` | Why the book exists — the soul document; highest-priority context for drafting |
| `latex/chapters/` | Canonical content — the only place prose lives |
| `latex/generated/`, `build/` | Machine-written — **never edit, never commit** |
| `docs/architecture/authoring-contract.md` | The complete LaTeX vocabulary chapters may use |
| `docs/guides/` | STYLE, STYLE-CRAFT, STYLE-AI-TELLS, WRITING-PROCESS, CITATIONS, REVIEW-QA, RESEARCH |
| `docs/publishing/` | KDP runbook, metadata dossier, release checklist, cover spec, narration channels |
| `research/`, `outline/`, `notes/` | Research folders (README contract), outline, working notes |
| `docs/review-NN/` | Review-round findings and synthesis |

## Hard rules

1. **Never edit `latex/generated/` or `build/`.** They are regenerated
   from `book.yaml` by the build; edits there are silently destroyed.
2. **Never introduce literal title/author/ISBN strings** in LaTeX,
   EPUB, or cover sources. Use the metadata macros (`\BookTitle`,
   `\BookAuthor`, …) from `latex/generated/metadata.tex`.
3. **Chapters use ONLY the authoring contract**
   (`docs/architecture/authoring-contract.md`). No raw TikZ, manual
   spacing, `\newcommand`, or low-level TeX in chapter files.
   `make check` and the EPUB coverage audit enforce this.
4. **Every claim that needs a source gets a verified citation.** Open
   and read the actual source before citing. Stamp
   `verified = {YYYY-MM-DD}` only after reading; pin an `archived =`
   Wayback snapshot (`verify_citation.py --archive`). Never mark
   verified from a search snippet or memory. See guides/CITATIONS.md.
5. **Reviewers never edit.** Persona-review agents produce scored
   findings; only revision work applies changes, from a synthesized
   fix brief.
6. Fix briefs assign **non-overlapping files** to parallel editing
   agents; run `make check` after parallel edits to catch
   cross-chapter repetition.
7. Don't hand-type build stats or metadata into prose or docs —
   derive them (`make stats`, `book.yaml`).

## Typesetting & formatting

- `book.yaml` decides trim, paper, font profile, base size, citation
  style, editions, and modules. Change design there, never in chapters.
- Styling lives in `latex/preamble/` modules (geometry, colors,
  styling, boxes, code). If a chapter needs a visual effect the
  contract lacks, extend the preamble + contract + EPUB handler
  together — don't improvise in prose files.
- Figures: `\includegraphics` + `\caption` + `\label` + `\figalt{…}`
  (≤140 chars; `\figalt{}` = decorative). A figure with no alt and no
  caption fails the EPUB gate.
- The EPUB claims **EPUB Accessibility 1.1 / WCAG 2.2 AA** and
  `make epub-a11y` (Ace) enforces it — keep headings hierarchical,
  images described, and semantics inside the contract.

## Build targets (complete vocabulary — see docs/architecture/build-system.md)

| Target | What it does |
|---|---|
| `make pdf` / `make quick` | Print PDF (quick = single fast pass) |
| `make bleed` / `make ebook` / `make grayscale` / `make draft` | Mode variants |
| `make epub` / `make epub-check` | EPUB 3 + epubcheck / strict coverage audit |
| `make epub-a11y` | Ace accessibility audit (fails on serious/critical) |
| `make cover-vars` | Page count → spine → `latex/generated/cover-vars.tex` |
| `make kdp-cover` / `make lulu-cover` / `make cover-image` | Wrap covers, Kindle raster |
| `make check` | Style + prose checkers on `latex/chapters/` |
| `make preflight` / `make cover-ink` | Font/DPI gates; cover total-ink ≤ 240% |
| `make pdfx` / `make onix` | PDF/X-1a interior (IngramSpark/Lulu); ONIX 3.0 feed |
| `make verify-citations` | URL reachability + `verified=`/`archived=` gates |
| `make narration-export` | Per-chapter plain text for AI narration |
| `make stats` | Word counts + deltas (`book_stats.py`) |
| `make doctor` | Toolchain, placeholders, cover-vars freshness, this file's target audit |
| `make validate-all` | Everything above that gates a release |
| `make release` | `validate-all` → `releases/<date>-<printing>/` + SHA256SUMS |
| `make watch` / `make clean` | Rebuild loop / remove outputs |

Rhythm: after editing prose → `make check`; to see pages → `make
quick`; before a review round → `make epub-check` + `make stats`;
before upload → `make validate-all`. Editions:
`make pdf EDITION=<name>` (declared in `book.yaml`, ADR 0011).

## Craft, style, and AI tells

Read **before** drafting, in order:

1. `docs/SPIRIT.md` — the why; every paragraph touches an emotional thread.
2. `docs/guides/STYLE.md` — voice and mechanics. Non-negotiables:
   the read-aloud test (register chosen above); sentence averages
   12–18 words (guides) / 15–20 (narrative) with a 30/35-word ceiling;
   deliberate variance — a wall of same-length sentences is machine
   prose; front-load the claim. §8–9's fenced blocks are the **lint
   source** for `make check` — editing them changes enforcement.
3. `docs/guides/STYLE-AI-TELLS.md` — the rule-per-tell catalog ("This"
   disease, gerund openers, triadic flourishes, not-X-but-Y, hedging
   clusters, summary openers…). The checker budgets ⟨3⟩ tell matches
   per chapter; the goal is zero.
4. `docs/guides/STYLE-CRAFT.md` — positive craft: burstiness, concrete
   detail over abstraction, scene vs. summary, tension as the engine
   of explanation, openers/closers (the coda move varies its wording).
5. `docs/guides/styles/<profile>.md` — your genre profile: the POV,
   chapter shape, structural conventions, craft moves, and failure
   modes specific to this register, plus the banned-list and
   tell-budget deltas `make check` enforces on top of the base.

The order matters: SPIRIT beats profile beats STYLE beats convenience.
A sentence that passes every lint but touches no thread is still dead —
rewrite it.

## Writing workflow

Full workflow: `docs/guides/WRITING-PROCESS.md`. Summary:

```
research → outline → draft → edit (content, then copy) →
review panel (scored, no edits) → synthesize → revise → verify → polish
```

- Cite as you write — never leave citations "for later".
- Each review round lives in `docs/review-NN/`; run `make stats`
  before and after to quantify the round.

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

Drafting and review prompts always include: "read `docs/SPIRIT.md`
first," the chapter's research folder, and the register chosen in
"This book".

## When you finish a session

1. `make check` — style/prose gates green (or violations listed for the user).
2. `make stats` — record word-count deltas.
3. Update the project TODO / research trackers with what changed and what's next.
4. If you touched anything the build derives from, run the relevant
   target (`make pdf`, `make epub`) and report failures honestly.
