# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""init_paper.py — personalize a fresh clone of paper-template.

Rewrites paper.yaml's identity block (title, author, abstract) from CLI
flags and, with --fresh, replaces the sample sections with a single empty
starter so you can begin writing immediately. Preserves the engine / font /
bib / venue choices unless you pass them.

    uv run scripts/init_paper.py \\
      --title "My Paper" --author "A. Name <a@x.org> @ My Lab" \\
      --venue arxiv --fresh

--author may be repeated; the form is "Name <email> @ Affiliation" (email
and affiliation optional). The first author is corresponding.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PAPER_YAML = ROOT / "paper.yaml"
SECTIONS = ROOT / "latex" / "sections"

STARTER = """\\section{Introduction}
\\label{sec:intro}

Start writing here. See docs/guides/STYLE-PAPER.md for the authoring
contract and the available macros and environments.
"""


def parse_author(spec: str) -> dict:
    a: dict = {}
    m = re.match(r"\s*([^<@]+?)\s*(?:<([^>]+)>)?\s*(?:@\s*(.+))?\s*$", spec)
    if not m or not m.group(1):
        sys.exit(f"init_paper: cannot parse --author {spec!r} "
                 "(use 'Name <email> @ Affiliation')")
    a["name"] = m.group(1).strip()
    if m.group(2):
        a["email"] = m.group(2).strip()
    if m.group(3):
        a["affiliation"] = m.group(3).strip()
    return a


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--title")
    ap.add_argument("--subtitle")
    ap.add_argument("--author", action="append", default=[],
                    help="'Name <email> @ Affiliation' (repeatable)")
    ap.add_argument("--abstract")
    ap.add_argument("--venue", choices=["preprint", "arxiv", "ssrn"])
    ap.add_argument("--engine", choices=["pdflatex", "xelatex", "lualatex"])
    ap.add_argument("--font", dest="font_profile",
                    choices=["libertinus", "newtx", "lmodern", "plex"])
    ap.add_argument("--bib", dest="bib_system", choices=["natbib", "biblatex"])
    ap.add_argument("--fresh", action="store_true",
                    help="replace sample sections with an empty starter")
    args = ap.parse_args()

    cfg = yaml.safe_load(PAPER_YAML.read_text())
    if args.title:
        cfg["paper"]["title"] = args.title
    if args.subtitle is not None:
        cfg["paper"]["subtitle"] = args.subtitle
    if args.abstract:
        cfg["abstract"] = args.abstract
    if args.author:
        authors = [parse_author(s) for s in args.author]
        authors[0]["corresponding"] = True
        cfg["authors"] = authors
    if args.venue:
        cfg["venue"]["target"] = args.venue
    if args.engine:
        cfg["typography"]["engine"] = args.engine
    if args.font_profile:
        cfg["typography"]["font_profile"] = args.font_profile
    if args.bib_system:
        cfg["citations"]["system"] = args.bib_system

    PAPER_YAML.write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True,
                                         width=100))
    print("init_paper: rewrote paper.yaml")

    if args.fresh:
        for tex in SECTIONS.glob("*.tex"):
            tex.unlink()
        (SECTIONS / "01_introduction.tex").write_text(STARTER)
        # Trim main.tex to the single starter section AND drop the sample
        # appendix machinery (\appendix + its input), which would otherwise
        # reference the now-deleted A_appendix.tex and break `make pdf`.
        main_tex = ROOT / "latex" / "main.tex"
        src = main_tex.read_text()
        # 1. collapse the contiguous body inputs to the starter.
        src = re.sub(
            r"(\\input\{sections/01_introduction\})\n(?:\\input\{sections/[^}]+\}\n)*",
            r"\1\n", src)
        # 2. remove the appendix block (comment banner + \appendix + inputs).
        src = re.sub(
            r"\n% -+ Appendix -+\n\\appendix\n(?:\\input\{sections/[A-Z]_[^}]+\}\n)+",
            "\n", src)
        # 3. belt-and-suspenders: drop any remaining appendix-section input.
        src = re.sub(r"\\input\{sections/[A-Z]_[^}]+\}\n", "", src)
        main_tex.write_text(src)
        print("init_paper: --fresh: reset to a single starter section and "
              "removed the sample appendix (review latex/main.tex)")


if __name__ == "__main__":
    main()
