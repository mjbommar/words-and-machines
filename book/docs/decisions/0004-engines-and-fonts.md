# ADR 0004 — LuaLaTeX default with engine-conditional fontspec; three font profiles

## Decision
Default engine **LuaLaTeX** (needed for luaotfload fallback fonts, microtype protrusion at its best); the fonts module is engine-conditional so XeLaTeX also works (needed by the verse/polyglossia profile). Font profile selected in `book.yaml`:

| profile | body | sans | mono | provenance |
|---------|------|------|------|-----------|
| `libertinus` (default) | Libertinus Serif | Libertinus Sans | Libertinus Mono | datacenter, wiki, the-last-book print |
| `garamond` | EB Garamond | Source Sans 3 | Noto Sans Mono | complexity, htsd, legal-tech (trade/pop-sci voice) |
| `plex` | IBM Plex Serif | IBM Plex Sans | IBM Plex Mono | RFC, hacking, vibe-coding (technical voice; optical sizes, SemiBold-as-bold) |

Each profile ships complete: bold/italic mappings, figure styles (lining in tables, oldstyle in text), CJK/emoji fallback hooks, and a tuned microtype block.

## Rationale
These three stacks cover every published book; each is print-proven. Fonts are loaded by family name (never file path — hard-coded paths broke htsd portability), with a `make doctor` check that required fonts resolve.

## Consequences
- EPUB embeds the matching OTFs so digital matches print.
- The verse module (paracol + polyglossia Greek/Latin) documents its XeLaTeX requirement; Makefile switches engine per book.yaml.
