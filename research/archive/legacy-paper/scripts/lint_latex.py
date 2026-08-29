# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""lint_latex.py — run chktex on the section sources (advisory).

chktex ships with a full TeX Live and is the de-facto LaTeX linter; this
wrapper runs it over latex/sections/ with the project .chktexrc (which mutes
the heuristic warnings that misfire on math/tables). If chktex is not on PATH
(e.g. a minimal Debian texlive without the binary), it SKIPS with a note
rather than failing — CI runs the full TeX Live where chktex is present.

    uv run scripts/lint_latex.py            # advisory (never fails the build)
    uv run scripts/lint_latex.py --strict   # exit nonzero if chktex warns
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECTIONS = ROOT / "latex" / "sections"
CHKTEXRC = ROOT / ".chktexrc"


def main() -> int:
    strict = "--strict" in sys.argv[1:]
    if shutil.which("chktex") is None:
        print("lint_latex: chktex not found — skipping (install via TeX Live; "
              "CI runs it on the full distribution).")
        return 0
    files = sorted(SECTIONS.glob("*.tex"))
    if not files:
        print("lint_latex: no sections to lint")
        return 0
    total = 0
    for tex in files:
        r = subprocess.run(
            ["chktex", "-q", "-l", str(CHKTEXRC), str(tex)],
            capture_output=True, text=True)
        # chktex writes WARNINGS to stdout (rc=1 is normal for warnings) but
        # CONFIG/parse errors (e.g. a malformed .chktexrc) to stderr prefixed
        # "ERROR". Those are a hard failure — otherwise a broken .chktexrc
        # reads as "clean" and the lint silently does nothing (a CI false
        # green). Match the ERROR prefix, not any stderr, so benign chktex
        # chatter doesn't trip it.
        if "ERROR" in r.stderr:
            print(f"lint_latex: chktex config error (bad .chktexrc?):\n"
                  f"{r.stderr.strip()}", file=sys.stderr)
            return 1
        out = r.stdout.strip()
        if out:
            total += out.count("\n") + 1
            print(out)
    if total:
        print(f"lint_latex: {total} chktex message(s) "
              f"({'FAIL' if strict else 'advisory'})")
        return 1 if strict else 0
    print(f"lint_latex: clean ({len(files)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
