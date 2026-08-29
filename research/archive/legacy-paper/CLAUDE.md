# AI Instructions (canonical)

This is the single source of AI instructions for this paper project.
`AGENTS.md` and `GEMINI.md` are pointers here; never let them diverge.
`make doctor` audits this file: every `make <target>` it mentions must exist.

> Starting a paper from this template? Run
> `uv run scripts/init_paper.py --title "…" --author "…" --venue arxiv --fresh`,
> then fill in `paper.yaml` and replace this "About this paper" note with your
> premise, thesis, and target venue.

## About this paper

_(Replace: one paragraph — the paper's thesis, method, and where it's going.
Name the venue: arXiv category, or SSRN networks + JEL codes.)_

## Project map

| Where | What |
|---|---|
| `paper.yaml` | Single source of truth: title, authors, abstract, keywords, JEL, engine, fonts, bib, venue, disclosures |
| `latex/sections/` | Canonical content — the only place prose lives (numbered `NN_*.tex`) |
| `latex/generated/`, `build/` | Machine-written — **never edit, never commit** |
| `latex/preamble/` | Modular preamble (fixed load order); font profiles, colors, styling, boxes, code |
| `latex/frontmatter/`, `latex/backmatter/` | Title block, disclosures — template internals |
| `docs/guides/` | STYLE-PAPER (authoring contract), FIGURES, CITATIONS, **SUBMISSION** (arXiv/SSRN 2026) |
| `docs/architecture/`, `docs/decisions/` | Build system, config schema, layout; ADRs |
| `.claude/agents/` | The AI-assisted paper workflow agents |

## Hard rules

1. **Never edit `latex/generated/` or `build/`.** They are regenerated from
   `paper.yaml`; edits there are silently destroyed.
2. **Never hard-code title/author/keywords/JEL** in the LaTeX. Use the metadata
   macros (`\PaperTitle`, `\PaperAuthorBlock`, `\KeywordsLine`, …) from
   `latex/generated/metadata.tex`.
3. **Sections use only the authoring contract** (`docs/guides/STYLE-PAPER.md`):
   the semantic macros (`\term`, `\keyterm`, `\code`, …) and environments
   (callout boxes, `codelisting`, `figure`, `table`, theorems). No raw
   `\color`, manual `\vspace`, or `\newcommand` in `sections/`. `make check`
   enforces this.
4. **Every claim that needs a source gets a real citation.** Open and read the
   source before citing; add `note = {verified YYYY-MM-DD}` to the bib entry
   only after reading. See `docs/guides/CITATIONS.md`.
5. **Every figure needs `alt=` text** on its `\includegraphics` (arXiv HTML /
   screen readers). `make check` (`check_refs`) fails without it.
6. **Don't hand-type build stats or metadata into prose** — derive them
   (`make wordcount`, `paper.yaml`).
7. **No `minted`/`--shell-escape`** — arXiv does not run shell-escape. Use the
   `codelisting` environment (pure `listings`).

## Build targets (complete vocabulary — see docs/architecture/build-system.md)

| Target | What it does |
|---|---|
| `make pdf` / `make quick` | The paper PDF (quick = single fast pass) |
| `make draft` / `make anon` / `make grayscale` | DRAFT (line numbers + banner) / double-blind (identity + PDF metadata stripped) / B&W-safe |
| `make figures` | matplotlib (`build_figures.py`) + standalone TikZ (`build_tikz.py`) |
| `make arxiv` | Hardened arXiv bundle + `ARXIV-SUBMISSION.md`: ships `.bbl`, inlines metadata, verifies a standalone compile (exit 0, no errors, 0 undefined refs); refuses lualatex |
| `make ssrn` | SSRN PDF + paste-ready `SSRN-METADATA.md` (see `docs/TODO-SSRN.md`) |
| `make check` | `check_style` (authoring contract) + `check_refs` (refs/alt-text/dead sections) |
| `make lint` | chktex LaTeX lint on sections (advisory; skips if chktex absent) |
| `make wordcount` | Per-section word counts (texcount) |
| `make repro` | Build twice at a fixed epoch (+ FORCE_SOURCE_DATE); assert byte-identical PDFs |
| `make doctor` | Toolchain, packages, fonts for THIS config; CLAUDE.md ↔ Makefile drift |
| `make validate` | Everything a release must pass |
| `make release` | `validate` → `releases/<date>-<slug>/` + SHA256SUMS + TOOLCHAIN.txt |
| `make watch` / `make clean` | Rebuild loop / remove outputs |

Engine, font profile, bibliography system, and venue all come from
`paper.yaml`; the Makefile reads them via `generate_metadata.py`.

## Switching venue / engine / fonts

Edit `paper.yaml` (or pass flags to `init_paper.py`), then `make pdf`:

- `venue.target: arxiv|ssrn|preprint` — apparatus, packaging, and the
  submission dossier follow.
- `typography.engine: pdflatex|xelatex|lualatex` — `pdflatex` is arXiv-safest;
  the Unicode engines need the OTF fonts visible (`make doctor` checks).
- `typography.font_profile` and `citations.system` — see the README table.

## Writing workflow

```
research → outline → draft → edit (content, then copy) →
review panel (scored, no edits) → synthesize → revise → verify → polish
```

- Read `docs/guides/STYLE-PAPER.md` **before** drafting; run `make check` after.
- Cite as you write — never leave citations "for later".
- Keep statistics in `paper.yaml` or `\newcommand` number-macros in the
  preamble, never hand-typed in prose (the single-source-of-truth rule).

## Agents (`.claude/agents/`)

| Phase | Agent | Role |
|---|---|---|
| Research | `researcher` | Fill research notes with sourced, verified material |
| Drafting | `section-drafter` | Outline → prose within the authoring contract |
| Editing | `copy-editor` | Line edits, consistency, mechanics |
| Verification | `citation-verifier` | URL/metadata verification, `verified=` stamps |
| Review | `reviewer-referee` | Persona review (a journal referee), scores, never edits |
| Synthesis | `review-synthesizer` | Panel findings → prioritized, non-overlapping fix briefs |

Reviewers **score but never edit**; only revision work applies changes.

## When you finish a session

1. `make check` — style/reference gates green (or violations listed).
2. `make wordcount` — record deltas.
3. If you touched anything the build derives from, run the relevant target
   (`make pdf`, `make arxiv`) and report failures honestly.
