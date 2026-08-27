# RESEARCH — The Per-Chapter Research Folder Contract

Research is organized per chapter, and each chapter's `README.md` is a **contract**: it
states what the chapter must cover, at what depth, what remains unknown, and how the
chapter connects to its neighbors. Drafting does not start until the contract is
satisfied or its gaps are explicitly accepted.¹

---

## 1. Directory layout

```
research/
├── _shared/                  ← cross-chapter resources
│   ├── people/               ← one file per recurring figure
│   ├── organizations/        ← one file per key entity
│   ├── themes/               ← book leitmotifs (one file per through-line)
│   └── data/                 ← shared datasets (CSV/JSON)
├── _templates/               ← blank README + note templates
└── ch-XX-[slug]/             ← one folder per chapter
    ├── README.md             ← THE CONTRACT (schema below)
    ├── sources.md            ← curated sources, full citations, access dates
    ├── timeline.md           ← event chronology with dates and sources
    ├── vignettes.md          ← narrative scene candidates (people, places, moments)
    ├── data-notes.md         ← statistics with sources; derived-number math shown
    ├── entities.md           ← orgs/people specific to this chapter
    ├── debates.md            ← where scholars/experts disagree, and on what evidence
    ├── fact-check/           ← memos on contested or fragile claims
    └── downloads/            ← source PDFs/HTML/images (gitignore as needed)
```

Not every book needs every file — but **README, sources, and timeline are mandatory**,
and a file that exists must be maintained.

**Check existing resources first, research second.** Prior projects, wikis, and datasets
usually already contain the answer; extract with citations to the *original* sources.

---

## 2. The README contract schema

```markdown
# Chapter X: [Title]

**Period/Scope:** [...]   **Word target:** [...]
**Compelling question:** [The one question the chapter answers, phrased as the
reader would ask it.]

## Scope
### Close-up subjects        ← treated in depth, with scenes
1. [Subject A] — [what specifically]
2. [Subject B]
### Panoramic subjects       ← covered briefly, for context
- [Subject C], [Subject D]

## Dimension depths
| Dimension | Depth (Deep/Medium/Light) | Key content |
|---|---|---|
| [book-specific dimension 1] | Deep | [...] |
| [dimension 2] | Medium | [...] |

## Key questions
### Supporting questions
1. [...]
2. [...]
### Questions we can't fully answer      ← honesty section; feeds hedging in prose
- [...] (why: evidence gap / scholarly dispute)

## Volatility watchlist
| Watchlist item | Applies? | Handling |
|---|---|---|
| Population/size estimates | Yes | "roughly," "scholars estimate" |
| "Firsts" claims | Yes | "one of the earliest known" |
| [book-specific fragile claim types] | ... | ... |

## Signature scenes to seek
- [ ] [A concrete, sensory scene candidate — person, place, moment]
- [ ] [...]

## Feature inventory (planned)
- [ ] [Figure/map/table/box the chapter owes, with data source]

## Research gaps
- [ ] [What's missing, specifically enough that someone else could fill it]

## Cross-chapter connections
### Links back — [what earlier chapters established that this one uses]
### Links forward — [what this chapter sets up]
### Through-lines active — [which book themes from _shared/themes/ this chapter carries]
```

### Why each section earns its place

- **Compelling question** keeps the chapter an argument, not a topic dump.
- **Dimension depths** force explicit coverage decisions (the same table, summed across
  chapters, is the book's balance audit).
- **Questions we can't answer** is where honest hedging in the prose comes from — decided
  at research time, not improvised while drafting.
- **Volatility watchlist** pre-registers the claim types that get books embarrassed
  (population numbers, "firsts," technology-diffusion stories, anything moving faster
  than the publication cycle) and the hedging protocol for each.
- **Signature scenes** make the drafter hunt concrete moments while sources are open.
- **Research gaps** convert "I'll figure it out later" into assignable work.
- **Cross-chapter connections** are the anti-duplication device: they name the canonical
  home of shared material before two chapters both explain it.

---

## 3. Shared resources (`_shared/`)

- **people/** and **organizations/**: one dossier per recurring figure/entity — role,
  verified biographical facts with sources, best quotes with provenance. Chapters link
  here instead of re-researching.
- **themes/**: one file per book leitmotif (from SPIRIT.md). Records where each theme
  appears, so refrains accumulate instead of repeating.
- **data/**: canonical datasets. Derived statistics show their math. Numbers used in
  prose must trace here or to sources.md — and, at fact-check time, to the canonical-
  figures file (REVIEW-QA.md §4).

---

## 4. Research standards

- **Source hierarchy:** (1) government/regulatory/primary documents, (2) official
  org/company materials, (3) quality journalism and trade press, (4) academic and think-
  tank work. Sibling-project research is a starting point — verify and cite the primary.
- **Full metadata at capture time**: title, author, publication, exact date, URL,
  access date. Sloppy capture is what the 57%-error audit looks like later
  (see CITATIONS.md §1).
- **Paraphrase, never reproduce.** No source text — even public-domain — enters the
  manuscript. Cite and point the reader to the source.
- **Track down the primary for famous quotes/anecdotes** — many are apocryphal.
- **Date-stamp the research vantage point.** Note when a folder was last verified
  current; anything past the model/author's knowledge horizon needs live verification.
- **Interviews:** if none were conducted, say so in the folder and the book's author
  note; composite characters are labeled fictional and grounded in cited public sources.

---

## 5. Research runner workflow (for agents)

1. Read the book's SPIRIT.md, the chapter outline (if any), and `_shared/themes/`.
2. Create the folder from `_templates/`; draft the README contract *first*.
3. Fill sources/timeline/data-notes, checking existing project resources before
   searching the web.
4. Mark every unresolved item in **Research gaps** — never silently skip.
5. Fact-check memos for any claim on the volatility watchlist.
6. Hand off: the drafter reads README top to bottom, then vignettes + data-notes, and
   should never need to open a browser for anything the contract promised.

**Definition of done** for a research folder:
- [ ] README contract complete (every section filled or marked N/A with a reason)
- [ ] 2–3 real case studies / scenes with outcomes and sources
- [ ] Timeline covers the chapter's span with sourced dates
- [ ] Key statistics in data-notes with sources and shown math
- [ ] Gaps listed; volatility items memo'd
- [ ] Cross-chapter section names canonical homes for shared material

---

¹ Schema distilled from history-book `research/ch-*/README.md` (dimension-depth tables,
compelling questions, volatility watchlist, signature scenes, cross-chapter links) and
the folder layouts of datacenter-2026-book and htsd-book (sources/vignettes/data-notes/
entities/timeline/downloads; procedural-notes and examples for guide books). Sourcing
ethic from the-last-book CLAUDE.md.
