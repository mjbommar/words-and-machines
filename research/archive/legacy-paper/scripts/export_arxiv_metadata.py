# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""export_arxiv_metadata.py — paste-ready arXiv submission form sheet.

Writes ARXIV-SUBMISSION.md at the repo root: the fields the arXiv submission
form wants (title, authors, abstract as plain text, primary + cross-list
categories, the "Comments" line, license), plus a pre-submit checklist and a
note on what the bundle deliberately excludes. Modeled on
needles-at-scale/ARXIV-SUBMISSION.md. Derives the page/figure/table counts
from the last build so the Comments line is never hand-maintained.

    uv run scripts/export_arxiv_metadata.py

Run after `make pdf`/`make arxiv` so the counts reflect the current build.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PAPER_YAML = ROOT / "paper.yaml"
BUILD = ROOT / "build"
OUT = ROOT / "ARXIV-SUBMISSION.md"

LICENSES = {
    "cc-by-4.0": "CC BY 4.0", "cc-by-sa-4.0": "CC BY-SA 4.0",
    "cc-by-nc-sa-4.0": "CC BY-NC-SA 4.0", "cc-by-nc-nd-4.0": "CC BY-NC-ND 4.0",
    "arxiv-nonexclusive": "arXiv.org perpetual, non-exclusive license",
    "cc0": "CC0 1.0",
}


def one_line(text: str) -> str:
    return " ".join((text or "").split())


def pdf_pages() -> int | None:
    pdf = BUILD / "latex" / "main.pdf"
    if not pdf.exists():
        return None
    r = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True)
    m = re.search(r"Pages:\s*(\d+)", r.stdout)
    return int(m.group(1)) if m else None


def count_floats() -> tuple[int, int]:
    """Count figures and tables across the section sources (env begins)."""
    figs = tabs = 0
    for tex in sorted((ROOT / "latex" / "sections").glob("*.tex")):
        src = re.sub(r"(?<!\\)%.*", "", tex.read_text())
        figs += len(re.findall(r"\\begin\{figure\*?\}", src))
        figs += len(re.findall(r"\\begin\{sidewaysfigure\}", src))
        tabs += len(re.findall(r"\\begin\{table\*?\}", src))
        tabs += len(re.findall(r"\\begin\{sidewaystable\}", src))
        tabs += len(re.findall(r"\\begin\{longtable\}", src))
    return figs, tabs


def comments_line(pages: int | None, figs: int, tabs: int) -> str:
    parts = []
    if pages:
        parts.append(f"{pages} pages")
    if figs:
        parts.append(f"{figs} figure" + ("s" if figs != 1 else ""))
    if tabs:
        parts.append(f"{tabs} table" + ("s" if tabs != 1 else ""))
    return ", ".join(parts) if parts else "(run make pdf to derive counts)"


def main() -> None:
    if not PAPER_YAML.exists():
        print("export_arxiv_metadata: paper.yaml not found", file=sys.stderr)
        sys.exit(1)
    cfg = yaml.safe_load(PAPER_YAML.read_text())
    p = cfg["paper"]
    title = p["title"] + (f": {p['subtitle']}" if p.get("subtitle") else "")
    authors = "; ".join(
        a["name"] + (f" ({a['affiliation']})" if a.get("affiliation") else "")
        for a in cfg["authors"])
    cls = cfg.get("classification", {})
    primary = cls.get("arxiv_primary", "") or "(set classification.arxiv_primary)"
    cross = ", ".join(cls.get("arxiv_cross", []) or []) or "(none)"
    lic = LICENSES.get(cfg.get("venue", {}).get("license", ""), "(set venue.license)")
    pages = pdf_pages()
    figs, tabs = count_floats()

    lines = [
        f"# arXiv Submission — {p['title']}",
        "",
        "Paste-ready fields for the arXiv submission form. Generated from "
        "`paper.yaml` + the last build by `scripts/export_arxiv_metadata.py`.",
        "",
        "## Form fields",
        "",
        f"- **Title:** {one_line(title)}",
        f"- **Authors:** {authors}",
        f"- **Primary category:** {primary}",
        f"- **Cross-list:** {cross}",
        f"- **Comments:** {comments_line(pages, figs, tabs)}",
        f"- **License:** {lic}",
        "",
        "## Abstract (plain text — arXiv strips LaTeX)",
        "",
        one_line(cfg["abstract"]),
        "",
        "## Pre-submit checklist",
        "",
        "- [ ] `make arxiv` is green (standalone compile verified, 0 undefined refs).",
        "- [ ] The engine is pdflatex or xelatex (arXiv does not name lualatex).",
        "- [ ] `main.bbl` is in the bundle and matches the engine's bib program.",
        "- [ ] Every figure has `alt=` text (arXiv HTML/LaTeXML).",
        "- [ ] No `\\shell-escape`/`minted`; figures are pre-built PDFs.",
        "- [ ] `00README.json` names the intended compiler + TeX Live 2025.",
        "",
        "## Deliberately NOT in the bundle",
        "",
        "- Python scripts, CSVs, and figure sources (only final figure PDFs ship).",
        "- `generated/metadata.tex` (inlined into `main.tex`).",
        "- Build byproducts (`.aux/.log/.bcf/.run.xml/...`).",
    ]
    OUT.write_text("\n".join(lines) + "\n")
    print(f"export_arxiv_metadata: wrote {OUT.relative_to(ROOT)} "
          f"({comments_line(pages, figs, tabs)})")


if __name__ == "__main__":
    main()
