# Author Guides

Best-of syntheses of the style, craft, and process guides across the author's book
projects (htsd-book, history-through-rfc-book, the-last-book, datacenter-2026-book,
wiki-history-book, history-book, complexity-book, vibe-coding-for-lawyers,
legal-tech-history-book, hacking-with-ai-book). Written for both human authors and AI
agents. Per-book deltas belong in the book's own `docs/`, which should *inherit* these
and state only differences.

**Read before writing prose:** the book's SPIRIT.md → VOICE → CRAFT →
PLAIN-ENGLISH → STYLE → STYLE-AI-TELLS → STYLE-CRAFT → SIMPLIFIED-ENGLISH →
the genre profile in [styles/](styles/).

| Guide | What it covers |
|---|---|
| [VOICE.md](VOICE.md) | **Book voice authority**: the working-beside-the-reader relationship, four registers, humor, status language, and what this book must not sound like. |
| [CRAFT.md](CRAFT.md) | **Book pedagogy and chapter craft**: concrete-to-exact teaching, the two proofs for theorems, checked reproduction for computations, examples/non-examples/boundaries, artifact placement, exercises, and chapter promises. |
| [PLAIN-ENGLISH.md](PLAIN-ENGLISH.md) | **Book language standard**: the reader, explanatory order, claim grammar, terminology, and revision tests. This book-specific guide resolves the inherited guides for its technical subject. |
| [STYLE.md](STYLE.md) | Voice, person/tense, sentence/paragraph targets, punctuation, numbers/dates. **Lint source:** machine-readable `banned-words` / `banned-phrases` blocks parsed by `scripts/check_style.py`. |
| [STYLE-AI-TELLS.md](STYLE-AI-TELLS.md) | Rule-per-tell catalog of AI writing patterns with detection heuristics and rewrites; machine-readable `tell-patterns` regex block. |
| [SIMPLIFIED-ENGLISH.md](SIMPLIFIED-ENGLISH.md) | **Simplified Book English**: the controlled-vocabulary layer — a named reader, evidence-labelled word tiers, 8 writing rules, and reader-facing explanation guidance for jargon and unusual uses. Dictionary: `scripts/data/simplified_english/lexicon.json`; advisory report: `make simplified`; derivation: [../architecture/simplified-english.md](../architecture/simplified-english.md). |
| [STYLE-CRAFT.md](STYLE-CRAFT.md) | Positive craft: burstiness, concrete detail, scene vs. summary, the Kidder model, mentor-author moves, openers/closers, the read-aloud test family. |
| [styles/](styles/) | **Genre style profiles** layered over the three above (narrative-nonfiction, practical-guide, technical-handson, young-readers, verse-translation). Each carries register-specific POV, structure, craft moves, and lint deltas. Select with `style.profile` in `book.yaml`. |
| [SPIRIT-TEMPLATE.md](SPIRIT-TEMPLATE.md) | Fill-in template for the book's soul doc: thesis, emotional threads, reader's journey, tempo map, recurring moves. With a filled mini-example. |
| [CODE-STYLE.md](CODE-STYLE.md) | Code in print: 72-char limit, line-breaking recipes, output truncation, prompts/responses, platform handling. |
| [WRITING-PROCESS.md](WRITING-PROCESS.md) | The phased workflow and content-edit loop; book_stats delta convention; `docs/review-NN/` round mechanics; reviewers-never-edit; fix briefs. |
| [REVIEW-QA.md](REVIEW-QA.md) | Persona-panel reviews with scoring rubric, grep audits, random span sampling, canonical-figures anti-drift file, repetition checks. |
| [ONTOLOGY.md](ONTOLOGY.md) | The macro-to-micro writing ontology (~5,000 entries: arcs, arrangements, moves, constructions, figures, cadences) and its 15 technique scripts — ideation rollers, beat scaffolds, drafting palettes, and the `make craft` diagnostic suite. Design doc: `docs/architecture/writing-ontology.md`. |
| [DESLOP-PASS.md](DESLOP-PASS.md) | **One** worked approach to a detector-guided de-slop sweep, with its cost structure and blind spots. Optional, not part of the required flow — read the "when this fits" section before adopting any of it. |
| [CITATIONS.md](CITATIONS.md) | Claim classification, verify-before-cite with the tested fetch escalation ladder (httpx → Playwright `--fetch` → Chrome DevTools MCP → Wayback), `verified =`/`archived =` bib fields, per-chapter worksheets, the 57%-error cautionary tale. |
| [RESEARCH.md](RESEARCH.md) | Per-chapter research folder contract: README-as-contract schema, shared dossiers, sourcing standards, definition of done. |
