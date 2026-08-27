# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""wordcount.py — per-section and total word counts.

Uses texcount if available (accurate LaTeX-aware counting); otherwise falls
back to a rough whitespace count with LaTeX commands stripped. Advisory —
never a gate.

    uv run scripts/wordcount.py
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECTIONS = ROOT / "latex" / "sections"


def texcount_total(path: Path) -> int | None:
    if shutil.which("texcount") is None:
        return None
    r = subprocess.run(["texcount", "-1", "-sum", "-merge", str(path)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    m = re.search(r"(\d+)", r.stdout)
    return int(m.group(1)) if m else None


def rough_count(path: Path) -> int:
    src = path.read_text()
    src = re.sub(r"(?<!\\)%.*", "", src)
    src = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^}]*\})?", " ", src)
    src = re.sub(r"[{}$&~^_\\]", " ", src)
    return len([w for w in src.split() if any(c.isalnum() for c in w)])


def main() -> int:
    files = sorted(SECTIONS.glob("*.tex"))
    if not files:
        print("wordcount: no sections found")
        return 0
    have_texcount = shutil.which("texcount") is not None
    total = 0
    print(f"wordcount: {'texcount' if have_texcount else 'rough (install texcount for accuracy)'}")
    for tex in files:
        n = texcount_total(tex) if have_texcount else None
        if n is None:
            n = rough_count(tex)
        total += n
        print(f"  {tex.name:<28} {n:>6}")
    print(f"  {'TOTAL':<28} {total:>6}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
