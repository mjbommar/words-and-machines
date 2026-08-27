# ADR 0002 — `book.yaml` is the single source of truth for all metadata

## Decision
All book identity and configuration lives in `book.yaml`: title, subtitle, author, publisher, imprint, year, ISBNs (per format), description, BISAC codes, keywords, trim size, font profile, citation style, editions, AI-disclosure text. `scripts/generate_metadata.py` derives:

- `latex/generated/metadata.tex` — `\BookTitle`, `\BookAuthor`, `\BookISBNPrint`, … macros consumed by titlepage, copyright, covers, headers
- EPUB `content.opf` / nav metadata (via the converter)
- `docs/publishing/KDP.md` dossier skeleton

Generated files are **gitignored and never hand-edited**. The generator **fails on placeholder values** (`TODO`, `[Author Name]`, empty ISBN when `formats.print: true`) unless `--allow-placeholders` (used only by template CI).

## Evidence
Five projects shipped or nearly shipped stale copied metadata: RFC book's OPF carried an old ISBN and subtitle vs. its own copyright page; vibe-coding's `epub/` still said "Rough Consensus"; legal-tech's OPF had `[Author Name]`; datacenter had title/subtitle inconsistency across files; iliad/ovid hand-typed stats drifted from builds.

## Consequences
- LaTeX sources reference only metadata macros, never literal title/author strings.
- The EPUB converter takes metadata exclusively from `book.yaml` — its templates contain no book strings.
- `make doctor` audits for literal occurrences of the title/author in places that should use macros.
