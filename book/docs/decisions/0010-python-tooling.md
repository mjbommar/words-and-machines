# ADR 0010 — uv everywhere; one pyproject for the converter; PEP 723 for standalone scripts

## Decision
- `pyproject.toml` (uv-managed, committed `uv.lock`) covers the `epub/converter/` package and shared script deps: `texsoup`, `lxml`, `pyyaml`, `jsonschema`, `pillow`
- Standalone QA/utility scripts (`check_style.py`, `check_prose.py`, `book_stats.py`, `verify_citation.py`, `update_cover_vars.py`, `generate_metadata.py`, `init_book.py`) carry **PEP 723 inline metadata** and run via `uv run scripts/<name>.py` with zero project install
- Heavy optional deps (Playwright for citation verification) are *not* project deps: `uv run --with playwright` at point of use (the-last-book pattern)
- Makefile calls scripts only through `uv run`; no bare `python3`

## Evidence
The portfolio split between vestigial pyprojects (ai-law-finance — reviewed as dead weight) and working PEP 723 + uv (RFC, htsd, the-last-book). The RFC book's *lack* of a lockfile caused duplicated `uv run --with` strings across Makefile targets — hence one pyproject for anything imported by more than one entry point.

## Consequences
- CI needs only `uv` + TeX Live + epubcheck.
- Scripts stay individually runnable and copy-outable; the converter package does not.
