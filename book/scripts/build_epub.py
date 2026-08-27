"""Build the EPUB 3 edition from the converted LaTeX chapters.

Thin CLI over the epub/converter package (ADR 0007). Run from the repo
root under the project environment:

    uv run scripts/build_epub.py --cover build/cover/cover-front.png
    uv run scripts/build_epub.py --edition full --cover ... --strict

Requires build/epub-metadata.json (run scripts/generate_metadata.py
first — the Makefile's `generated` target does this).

Output: build/epub/book.epub, or build/epub/book-EDITION.epub when
--edition is given (matches the Makefile's JOB_SUFFIX convention).
--strict exits 1 on any unhandled LaTeX command/environment or broken
internal link (the `epub-check` gate).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

try:
    import converter  # installed by uv from [tool.hatch.build.targets.wheel]
except ImportError:  # fresh checkout before `uv sync`: import from source
    sys.path.insert(0, str(ROOT / "epub"))
    import converter

from converter.core import BuildError  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--edition", default=None,
                    help="edition name (must match the generated metadata)")
    ap.add_argument("--cover", required=True, type=Path,
                    help="front-cover raster image (PNG/JPEG)")
    ap.add_argument("--strict", action="store_true",
                    help="fail on unhandled commands or broken links")
    args = ap.parse_args()

    try:
        report = converter.build_book(ROOT, cover=args.cover,
                                      edition=args.edition)
    except BuildError as exc:
        print(f"build_epub: ERROR: {exc}", file=sys.stderr)
        return 1

    for w in report.warnings:
        print(f"build_epub: warning: {w}", file=sys.stderr)
    if report.unknowns:
        print("build_epub: unhandled LaTeX commands/environments "
              "(coverage report):", file=sys.stderr)
        for name, count in sorted(report.unknowns.items()):
            print(f"  \\{name}  x{count}", file=sys.stderr)
    for e in report.link_errors:
        print(f"build_epub: link error: {e}", file=sys.stderr)
    for e in report.a11y_errors:
        print(f"build_epub: accessibility error: {e}", file=sys.stderr)

    rel = report.epub_path.relative_to(ROOT)
    print(f"build_epub: wrote {rel} "
          f"({len(report.handled)} constructs handled)")

    if args.strict and not report.ok:
        print("build_epub: --strict: failing on the issues above",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
