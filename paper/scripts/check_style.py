# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""check_style.py — house-style lint for section sources.

Enforces the authoring rules in docs/guides/STYLE-PAPER.md so that sections
stay convertible and consistent:

  ERRORS (fail the build):
    * raw \\color / \\textcolor in a section (use semantic macros/boxes)
    * \\vspace / \\hspace with a hard-coded length in a section
    * a \\newcommand / \\def in a section (macros live in the preamble)
    * TODO / FIXME / XXX left in prose
    * minted / \\shellescape usage (breaks arXiv)

  WARNINGS (advisory):
    * a banned filler word ("very", "really", "clearly", "obviously")
    * a bare URL in prose (use \\url{} / a citation)

    uv run scripts/check_style.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Lint only author content. frontmatter/ and backmatter/ are template
# internals (title block, disclosures) where low-level spacing/color is
# legitimate — the authoring contract governs sections/ only.
SECTIONS = [ROOT / "latex" / "sections"]

ERROR_PATTERNS = [
    (re.compile(r"\\(text)?color\b"), "raw color (use a semantic macro or box)"),
    (re.compile(r"\\[vh]space\*?\{"), "manual spacing (belongs in the preamble)"),
    (re.compile(r"\\newcommand|\\renewcommand|\\def\b"), "macro definition (preamble only)"),
    (re.compile(r"\b(TODO|FIXME|XXX)\b"), "unfinished marker in prose"),
    # Actual minted USAGE breaks arXiv (needs --shell-escape). A prose
    # mention inside \code{} is fine, so match the package/env, not the word.
    (re.compile(r"\\usepackage(\[[^\]]*\])?\{minted\}|\\begin\{minted\}"),
     "minted usage (needs --shell-escape; breaks arXiv)"),
]
WARN_WORDS = re.compile(r"\b(very|really|clearly|obviously|simply|just)\b",
                        re.IGNORECASE)
BARE_URL = re.compile(r"(?<!\{)(?<!//)\bhttps?://\S+")


def strip_comments(src: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", src)


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    files: list[Path] = []
    for d in SECTIONS:
        if d.is_dir():
            files += sorted(d.glob("*.tex"))

    for tex in files:
        raw = tex.read_text()
        src = strip_comments(raw)
        for i, line in enumerate(src.splitlines(), 1):
            for pat, msg in ERROR_PATTERNS:
                if pat.search(line):
                    errors.append(f"{tex.name}:{i}: {msg}")
            for m in WARN_WORDS.finditer(line):
                warnings.append(f"{tex.name}:{i}: filler word {m.group(0)!r}")
            if BARE_URL.search(line) and "\\code" not in line and "\\url" not in line:
                warnings.append(f"{tex.name}:{i}: bare URL (wrap in \\url or cite)")

    for w in warnings:
        print(f"check_style: warning: {w}")
    for e in errors:
        print(f"check_style: ERROR: {e}", file=sys.stderr)
    if errors:
        print(f"check_style: {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(f"check_style: OK ({len(files)} files; {len(warnings)} advisory)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
