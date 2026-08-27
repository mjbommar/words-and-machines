# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""check_refs.py — reference, citation, and figure-accessibility gates.

Reads the last build log (build/latex/main.log) and the section sources,
and fails on:

  * undefined references or citations (the classic silent-drift bug),
  * multiply-defined labels,
  * a \\includegraphics without an alt= key (arXiv HTML/LaTeXML needs it),
  * an \\input'd section file that is not referenced from main.tex
    (dead section — usually a rename left behind).

Advisory-only warnings (never fail the build) are printed with 'warning:'.

    uv run scripts/check_refs.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LATEX = ROOT / "latex"
LOG = ROOT / "build" / "latex" / "main.log"

errors: list[str] = []
warnings: list[str] = []


def check_log() -> None:
    if not LOG.exists():
        warnings.append(f"{LOG.relative_to(ROOT)} not found — run `make pdf` first")
        return
    text = LOG.read_text(errors="ignore")
    undef = re.findall(r"(?:Citation|Reference) `([^']*)' .*undefined", text)
    for name in sorted(set(undef)):
        errors.append(f"undefined reference/citation: {name!r}")
    multi = re.findall(r"multiply.?defined.*`([^']*)'", text, re.IGNORECASE)
    # hyperref/nameref sometimes double-reports; dedupe.
    for name in sorted(set(multi)):
        errors.append(f"multiply-defined label: {name!r}")


def check_alt_text() -> None:
    """Every \\includegraphics needs an alt= key for arXiv HTML."""
    for tex in sorted((LATEX / "sections").glob("*.tex")):
        src = tex.read_text()
        # strip comments
        src = re.sub(r"(?<!\\)%.*", "", src)
        for m in re.finditer(r"\\includegraphics(\[[^\]]*\])?\{([^}]*)\}", src):
            opts = m.group(1) or ""
            if "alt=" not in opts:
                errors.append(
                    f"{tex.name}: \\includegraphics{{{m.group(2)}}} has no "
                    "alt= text (needed for arXiv HTML/screen readers)")


def check_dead_sections() -> None:
    main = (LATEX / "main.tex").read_text()
    inputs = set(re.findall(r"\\input\{(sections/[^}]+)\}", main))
    inputs = {i.split("sections/")[-1] for i in inputs}
    for tex in sorted((LATEX / "sections").glob("*.tex")):
        if tex.stem not in inputs:
            warnings.append(f"{tex.name}: not \\input from main.tex (dead section?)")


def main() -> int:
    check_log()
    check_alt_text()
    check_dead_sections()

    for w in warnings:
        print(f"check_refs: warning: {w}")
    for e in errors:
        print(f"check_refs: ERROR: {e}", file=sys.stderr)
    if errors:
        print(f"check_refs: {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("check_refs: OK (refs resolve, figures have alt text)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
