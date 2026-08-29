# ADR 0008 — Python tooling: uv run, PEP-723 self-contained scripts

## Decision
Every script is a standalone `uv run` script with PEP-723 inline dependency
metadata (`# /// script … ///`); no project install, no requirements file to
drift. The Makefile invokes them with `uv run --quiet [--with pkg]`.

## Evidence
book-template's ADR 0010; the portfolio's papers already lean on `uv run --with
matplotlib` for figures. Inline metadata means `uv run scripts/build_figures.py`
just works on a fresh clone.

## Consequences
- `pyproject.toml` lists deps only for editor tooling; the scripts are the
  source of truth for their own dependencies.
- Contributors need only `uv` + TeX Live + poppler.
