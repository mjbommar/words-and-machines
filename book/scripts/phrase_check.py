#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pydetex>=1.1.1"]
# ///
"""Provenance spot-check: do long spans of the book appear verbatim elsewhere?

Queries Ai2's infini-gram engine (https://infini-gram.io), which indexes
trillion-token corpora and counts how often an n-gram of any length occurs.
Long spans are the signal: an 8-word span that appears verbatim in a
web-scale corpus is either functional grammar ("to doubt that it would turn
into the", 81 hits) or borrowed phrasing (distinctive words, low count).
The second kind is what you want to see before publishing.

This answers PROVENANCE ("does my text contain someone else's words?"), not
DETECTABILITY ("does a detector call this AI?" — that's pangram_check.py).
Provenance is the risk with legal and ethical teeth; treat it separately.

    uv run scripts/phrase_check.py                      # sample the book
    uv run scripts/phrase_check.py --chapter ch03 -n 60
    uv run scripts/phrase_check.py --phrase "the sour tang of fermenting"
    uv run scripts/phrase_check.py --gram 10 --root ../other-book

BE POLITE. This is a free public research API with no key and no published
rate limit. Hammering it with concurrency gets your IP 403'd (we did this;
it cleared after a few minutes). This script is deliberately SERIAL with a
--delay between calls, and it will not accept a concurrency flag. Budget
~3 queries/sec, i.e. about a minute per 150 sampled spans.

Reading the output:
  count 0            span appears nowhere in the index — normal for
                     unpublished prose, and the overwhelming majority
  count high (100+)  generic connective grammar; ignore
  count low (1-20)   REVIEW: distinctive wording attested elsewhere
Advisory only — a match is a prompt to look, never a verdict. The index is
web-derived, so a phrase lifted from a book that was never quoted online
will not appear here.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.infini-gram.io/"
# 4.3T tokens, the largest index that answers without credentials.
# Full list: https://infini-gram.readthedocs.io/en/latest/api.html
DEFAULT_INDEX = "v4_dclm-baseline_llama"

SUBDIRS = ("chapters", "frontmatter", "front-matter", "backmatter", "back-matter")
DROP_ENVS = (
    "tikzpicture", "figure", "table", "tabular", "tabularx", "lstlisting",
    "verbatim", "Verbatim", "equation", "align", "alignat", "gather",
    "definitionbox", "tryitbox", "examplebox", "codelisting", "promptcode",
    "outputcode",
)


def detex(text: str) -> str:
    text = re.sub(r"(?<!\\)%.*", "", text)
    for env in DROP_ENVS:
        text = re.sub(rf"\\begin\{{{env}\*?\}}.*?\\end\{{{env}\*?\}}", " ",
                      text, flags=re.DOTALL)
    text = re.sub(r"\$[^$]*\$", " ", text)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", text)
    text = re.sub(r"[{}~]", " ", text)
    text = text.replace("---", " ").replace("--", " ")
    return re.sub(r"\s+", " ", text).strip()


def discover(root: Path, chapter: str | None) -> list[Path]:
    files: list[Path] = []
    for name in SUBDIRS:
        d = root / "latex" / name
        if d.exists():
            files += sorted(d.glob("*.tex"))
    if chapter:
        files = [f for f in files if f.name.startswith(chapter)]
    return files


def count(query: str, index: str, delay: float,
          retries: int = 2) -> int | None:
    """One serial count query. Sleeps `delay` after every call — do not
    remove, and do not wrap this in a thread pool."""
    body = json.dumps({"index": index, "query_type": "count",
                       "query": query}).encode()
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(
                API, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.load(r)
            time.sleep(delay)
            if "count" in data:
                return data["count"]
            print(f"phrase_check: API said {data}", file=sys.stderr)
            return None
        except urllib.error.HTTPError as e:
            if e.code == 403:
                print("phrase_check: 403 Forbidden — the API has rate-limited "
                      "this IP. Stop, wait a few minutes, and raise --delay.",
                      file=sys.stderr)
                raise SystemExit(1) from None
            time.sleep(2.0 * (attempt + 1))
        except (urllib.error.URLError, OSError, ValueError):
            time.sleep(2.0 * (attempt + 1))
    return None


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phrase", help="look up one exact phrase and exit")
    ap.add_argument("--gram", type=int, default=8,
                    help="span length in words (default 8; 5 is the study's "
                         "floor, longer = stronger evidence)")
    ap.add_argument("-n", "--samples", type=int, default=32,
                    help="spans sampled per file (default 32)")
    ap.add_argument("--delay", type=float, default=0.35,
                    help="seconds between queries (default 0.35 — raise it, "
                         "never lower it)")
    ap.add_argument("--index", default=DEFAULT_INDEX)
    ap.add_argument("--max-count", type=int, default=50,
                    help="report matches at or below this count; above it a "
                         "span is generic grammar (default 50)")
    ap.add_argument("--chapter", help="restrict to files starting with this")
    ap.add_argument("--root", type=Path,
                    default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--format", choices=("pretty", "jsonl"), default="pretty")
    args = ap.parse_args()

    if args.phrase:
        c = count(args.phrase, args.index, args.delay)
        print(f"{c if c is not None else '?'}  \u201c{args.phrase}\u201d")
        return

    files = discover(args.root, args.chapter)
    if not files:
        raise SystemExit(f"phrase_check: no .tex under {args.root}/latex/")
    rng = random.Random(args.seed)
    hits, queried = [], 0
    for f in files:
        words = detex(f.read_text()).split()
        grams = [" ".join(words[i:i + args.gram])
                 for i in range(len(words) - args.gram + 1)]
        if len(grams) < 10:
            continue
        picks = rng.sample(grams, min(args.samples, len(grams)))
        found = 0
        for p in picks:
            c = count(p, args.index, args.delay)
            queried += 1
            if c:
                found += 1
                hits.append({"file": f.name, "span": p, "count": c})
        if args.format == "pretty":
            print(f"{f.name:34s} {found}/{len(picks)} spans attested",
                  file=sys.stderr)

    flagged = sorted((h for h in hits if h["count"] <= args.max_count),
                     key=lambda h: h["count"])
    if args.format == "jsonl":
        for h in hits:
            print(json.dumps(h))
        return
    print(f"\n{queried} spans of {args.gram} words queried; {len(hits)} "
          f"attested anywhere; {len(flagged)} at count <= {args.max_count}")
    if flagged:
        print("\nREVIEW (distinctive wording attested elsewhere):")
        for h in flagged:
            print(f"  [{h['count']:>6,}x] {h['file']}: \u201c{h['span']}\u201d")
    else:
        print("No distinctive span matched — nothing to review.")


if __name__ == "__main__":
    main()
