# ADR 0009 — Style guides paired with deterministic checkers

## Decision
Three author-facing guides in `docs/guides/`, each paired with mechanical enforcement:

| Guide | Contents | Enforced by |
|-------|----------|-------------|
| `STYLE.md` | voice, sentence-length targets (12–18 word average, variance required), banned-word list, punctuation rules | `scripts/check_style.py` |
| `STYLE-AI-TELLS.md` | rule-per-tell catalog of AI writing patterns (not-X-but-Y, triadic flourish, "delve/tapestry/testament" lexicon, uniform paragraph rhythm, …) | `scripts/check_style.py` + `check_prose.py` repetition/n-gram checks |
| `STYLE-CRAFT.md` | positive craft: burstiness, concrete detail, scene-vs-summary, the Tracy Kidder model, before/after rewrites | review agents (not mechanically checkable) |

The checkers **read their word/pattern lists from the guide files** where practical (the-last-book's doc-as-lint-config pattern), so guide and lint cannot drift. `make check` runs everything; CI treats failures as errors.

## Evidence
Every mature project carried this trio (names varied); htsd/wiki/RFC/the-last-book have the most complete versions and wiki added a meta-audit that the checker implements the guide. The datacenter book's 5-round scored persona review moved its rating 7.67→8.47 — the guides are the highest-leverage quality artifact in the portfolio.

## Consequences
- Template guides are synthesized best-of versions, not copies of any single book's.
- Guides are register-agnostic; each book adds a `SPIRIT.md` (RFC pattern) for its specific emotional/tonal targets.
