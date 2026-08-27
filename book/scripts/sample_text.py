# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Random prose spans for spot review (docs/guides/REVIEW-QA.md).

Prints N random spans of consecutive sentences drawn across chapters,
with source locations, so a reviewer (human or agent) can audit register
and quality without reading in book order — the datacenter book's
random-span sampling recipe.

    uv run scripts/sample_text.py [--spans 5] [--sentences 4] [--seed 7]
                                  [--chapter ch02]
"""

from __future__ import annotations

import argparse
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHAPTERS = sorted((ROOT / "latex" / "chapters").glob("ch*.tex"))


def detex(text: str) -> str:
    text = re.sub(r"(?<!\\)%.*", "", text)
    for env in ("codelisting", "promptcode", "outputcode", "verbatim",
                "lstlisting", "tabular"):
        text = re.sub(rf"\\begin\{{{env}\}}.*?\\end\{{{env}\}}", " ",
                      text, flags=re.DOTALL)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", text)
    text = re.sub(r"[{}~]", " ", text)
    return re.sub(r"\s+", " ", text)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spans", type=int, default=5)
    ap.add_argument("--sentences", type=int, default=4)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--chapter", default=None,
                    help="restrict to chapters whose filename starts with this "
                         "(e.g. ch02)")
    args = ap.parse_args()
    rng = random.Random(args.seed)

    chapters = [c for c in CHAPTERS
                if not args.chapter or c.name.startswith(args.chapter)]
    if not chapters:
        raise SystemExit(f"sample_text: no chapter matches {args.chapter!r}")

    pool = []
    for chapter in chapters:
        sents = [s.strip() for s in
                 re.split(r"(?<=[.!?])\s+", detex(chapter.read_text()))
                 if len(s.split()) >= 4]
        for i in range(0, max(0, len(sents) - args.sentences)):
            pool.append((chapter.name, sents[i:i + args.sentences]))

    if not pool:
        raise SystemExit("sample_text: no prose found")
    for n, (name, span) in enumerate(rng.sample(pool, min(args.spans, len(pool))), 1):
        print(f"--- span {n} ({name}) ---")
        print(" ".join(span))
        print()


if __name__ == "__main__":
    main()
