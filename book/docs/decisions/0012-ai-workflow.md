# ADR 0012 — One canonical AI-instruction file; phased agent library; verification built in

## Decision
- **`CLAUDE.md` is the single canonical AI-instruction file.** `AGENTS.md` and `GEMINI.md` are one-line pointers to it. It stays short (orchestration + hard rules) and links to `docs/guides/` for everything else.
- **`.claude/agents/`** ships a curated ~12-agent library distilled from the 22–27-agent sets that datacenter/legal-tech/RFC forked among themselves: `researcher`, `outliner`, `chapter-drafter`, `content-editor`, `copy-editor`, `style-enforcer`, `fact-checker`, `citation-verifier`, three persona reviewers (trade-critic, domain-expert, general-reader), `review-synthesizer`. Generative agents may be model-pinned; **reviewers never edit** (datacenter rule).
- **Citation verification from day one**: `CITATIONS.md` claim classification, `verify_citation.py` (Playwright fetch), `verified={ISO-date}` annotations in the .bib, per-chapter verification worksheets.
- **Review rounds** live in `docs/review-NN/` with per-chapter findings + synthesis (RFC convention); `book_stats.py` before/after deltas quantify each round.

## Evidence
- Three AI-instruction files diverging (legal-tech CLAUDE/AGENTS/GEMINI described different phases and titles) — hence one canonical file.
- Datacenter's citation audit measured a **57% URL error rate** pre-verification; legal-tech's audit removed 9 hallucinated citations — hence verification is not optional.
- The multi-role loop (adapter → content-editor → copy-editor → simulated-reader) with per-section status tracking is the-last-book's proven adaptation pipeline.

## Consequences
- CLAUDE.md's claims are audited by `make doctor` (every referenced target/script must exist).
- Cross-chapter repetition risk from parallel agent rewrites (htsd finding) is mitigated by `check_prose.py` n-gram checks across chapters and non-overlapping file assignments in fix briefs.
