# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Personalize a fresh copy of the template into a new book project.

    uv run scripts/init_book.py --title "My Book" --author "A. Name" \
        --publisher "My Press" [--subtitle "..."] [--description "..."] \
        [--year 2026] [--fresh]

Run without flags for interactive prompts. What it does:
  1. Rewrites the identity fields in book.yaml (comments preserved) and
     blanks the sample ISBNs so `make release` fails loudly until you
     supply real ones (drafting builds still work). Without
     --description, the description becomes a TODO that blocks all
     builds until written — deliberate, since it feeds the cover + OPF.
  2. Rewrites README.md to a short project readme for the new book.
  3. --fresh: replaces the three sample chapters with a single
     ch01-introduction.tex stub and updates editions.full.chapters.
  4. Prints the follow-up checklist (ISBNs, description, docs/research
     cleanup, CI strictness).
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOK_YAML = ROOT / "book.yaml"

CHAPTER_STUB = """\
\\chapter{Introduction}
\\label{ch:introduction}

Start here. Chapters use only the vocabulary in
docs/architecture/authoring-contract.md; see docs/guides/ for the
style system and latex/chapters history in git for worked examples.
"""


def set_scalar(text: str, key: str, value: str) -> str:
    """Replace `  key: ...` preserving indentation and trailing comments."""
    pattern = re.compile(rf'^(\s*{key}:)\s*(?:"[^"]*"|[^#\n]*?)(\s*(?:#.*)?)$',
                         re.MULTILINE)
    if not pattern.search(text):
        sys.exit(f"init_book: could not find key {key!r} in book.yaml")
    return pattern.sub(rf'\1 "{value}"\2', text, count=1)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--title")
    ap.add_argument("--subtitle", default=None)
    ap.add_argument("--author")
    ap.add_argument("--publisher")
    ap.add_argument("--description", default=None,
                    help="back-cover description; omit to leave a TODO that "
                         "blocks builds until written")
    ap.add_argument("--year", type=int, default=date.today().year)
    ap.add_argument("--fresh", action="store_true",
                    help="replace sample chapters with a single stub")
    args = ap.parse_args()

    def ask(prompt: str) -> str:
        if not sys.stdin.isatty():
            return ""
        return input(prompt).strip()

    title = args.title or ask("Title: ")
    subtitle = args.subtitle if args.subtitle is not None \
        else ask("Subtitle (empty for none): ")
    author = args.author or ask("Author: ")
    publisher = args.publisher or ask("Publisher: ")
    if not (title and author and publisher):
        sys.exit("init_book: title, author, and publisher are required "
                 "(pass --title/--author/--publisher when not at a terminal)")

    text = BOOK_YAML.read_text()
    text = set_scalar(text, "title", title)
    text = set_scalar(text, "subtitle", subtitle)
    text = set_scalar(text, "author", author)
    text = set_scalar(text, "author_short", author.split()[-1])
    text = set_scalar(text, "publisher", publisher)
    text = re.sub(r"^(\s*year:)\s*\d+", rf"\1 {args.year}", text, count=1,
                  flags=re.MULTILINE)
    # Blank the sample identifiers; release gate demands real ones.
    text = set_scalar(text, "isbn_print", "")
    text = set_scalar(text, "isbn_epub", "")
    # Description: user-provided, or a loud TODO placeholder that blocks
    # builds until written (intentional: it feeds the cover + OPF).
    desc = args.description or "TODO back-cover description for this book."
    desc_yaml = "".join(f"    {line}\n" for line in desc.split("\n"))
    text = re.sub(r"(^  description: >-\n)(?:    .*\n)+",
                  rf"\g<1>{desc_yaml}", text, count=1, flags=re.MULTILINE)

    if args.fresh:
        chapters_dir = ROOT / "latex" / "chapters"
        for old in chapters_dir.glob("ch*.tex"):
            old.unlink()
        (chapters_dir / "ch01-introduction.tex").write_text(CHAPTER_STUB)
        text = re.sub(r"^(\s*chapters:)\s*\[.*\]$", r"\1 [ch01]",
                      text, count=1, flags=re.MULTILINE)

    BOOK_YAML.write_text(text)

    (ROOT / "README.md").write_text(f"""\
# {title}

{subtitle or ""}

By {author} — {publisher}, {args.year}.

Built from [book-template](https://github.com/mjbommar/book-template).

```bash
make pdf     # print interior          make epub   # EPUB + epubcheck
make check   # style/prose gates       make help   # everything else
```

Start with `book.yaml` (all metadata), `latex/chapters/` (content),
and `docs/guides/WRITING-PROCESS.md` (workflow). Hard rules live in
`CLAUDE.md`; the authoring vocabulary in
`docs/architecture/authoring-contract.md`.
""")

    desc_step = ("1. Write the real description in book.yaml "
                 "(builds fail on the TODO)."
                 if not args.description else
                 "1. Review book.yaml (description set from --description).")
    print(f"""init_book: personalized for "{title}" by {author}.

Next steps:
  {desc_step}
  2. Add ISBNs to book.yaml before `make release` (drafting works without).
  3. Optionally prune template provenance: docs/research/, docs/PLAN.md,
     docs/ROADMAP.md (keep docs/decisions/ + architecture/ + guides/).
  4. make pdf && make check
""")


if __name__ == "__main__":
    main()
