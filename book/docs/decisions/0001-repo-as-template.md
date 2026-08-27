# ADR 0001 — Repo root is a buildable book, instantiated as a GitHub template

## Decision
The repository root **is** a complete, buildable book project with sample content. New books are created by GitHub's "Use this template" (or cloning) and running `scripts/init_book.py`, which personalizes `book.yaml`, README, and optionally clears sample chapters.

## Alternatives considered
- **`template/` payload + generator script** (cookiecutter-style): adds an indirection layer nobody in the portfolio ever used; beamer-template's copy-the-directory workflow shows direct-copy is the working habit.
- **Shared library repo + thin book repos**: attractive for the EPUB converter, but every book in the portfolio diverged from its predecessor precisely because cross-repo sharing was never set up; vendoring with a clean upstream is the pragmatic middle.

## Rationale
Every reviewed project began life as a copy of the previous book. The failure mode was never *copying* — it was *incomplete renaming*. So the template optimizes the rename: one config file, generated metadata everywhere else, `init_book.py` doing the rewrite mechanically, and builds failing on leftover placeholders (ADR 0002).

## Consequences
- The template must always build out of the box (CI enforces this).
- Sample content doubles as living documentation of every feature.
- Improvements made inside a book project should be upstreamed here; `docs/research/` records the provenance of each component.
