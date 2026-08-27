#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pydetex>=1.1.1",
#     "nupunkt>=0.6.0",
# ]
# ///
"""
Find NEAR-duplicate sentences across chapters via stem-normalized Jaccard.

Method (per the house recipe):
  1. strip LaTeX (pydetex), segment sentences (nupunkt)
  2. normalize: lowercase, strip punctuation, tokenize
  3. stem cheaply: keep the first N characters of each token (default 4)
  4. pairwise Jaccard similarity on stem SETS; report pairs >= threshold
  5. also print a sorted-adjacent pass (sort all normalized sentences,
     flag neighbors sharing a long common prefix) as a fast second signal

Complements check_repetition.py (exact dups, n-grams) — this catches
paraphrased restatements the exact-match pass misses.

Usage:
    uv run scripts/find_near_duplicates.py latex/chapters/ch-1[7-9]*.tex latex/chapters/ch-2*.tex
    uv run scripts/find_near_duplicates.py --threshold 0.6 --stem 4 --min-words 8 FILES...
    uv run scripts/find_near_duplicates.py --all          # whole book incl. prologue/epilogue
"""

import argparse
import itertools
import re
import sys
from pathlib import Path

from pydetex import pipelines
from nupunkt import PunktSentenceTokenizer

ROOT = Path(__file__).resolve().parent.parent
CHAPTERS = ROOT / "latex" / "chapters"
BACKMATTER = ROOT / "latex" / "back-matter"

STOP = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "for",
    "with", "was", "were", "is", "are", "it", "its", "that", "this", "had",
    "has", "have", "not", "no", "as", "at", "by", "be", "been", "from",
}


def strip_latex(text: str) -> str:
    # drop comments and known non-prose blocks before pydetex
    text = re.sub(r"(?m)^%.*$", "", text)
    text = re.sub(r"\\begin\{table\}.*?\\end\{table\}", " ", text, flags=re.S)
    text = re.sub(r"\\begin\{tabular.?\}.*?\\end\{tabular.?\}", " ", text, flags=re.S)
    text = re.sub(r"\\chapterquote\{.*?\}\{.*?\}", " ", text, flags=re.S)
    cleaned = pipelines.strict(text)
    return re.sub(r"\s+", " ", cleaned).strip()


def stems(sentence: str, n: int) -> frozenset:
    toks = re.findall(r"[a-z0-9]+", sentence.lower())
    return frozenset(t[:n] for t in toks if t not in STOP and len(t) > 2)


def jaccard(a: frozenset, b: frozenset) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files", nargs="*", help="tex files (globs ok)")
    ap.add_argument("--all", action="store_true", help="all chapters + prologue/epilogue")
    ap.add_argument("--threshold", type=float, default=0.55)
    ap.add_argument("--stem", type=int, default=4, help="first-N-chars token stem")
    ap.add_argument("--min-words", type=int, default=8)
    ap.add_argument("--same-chapter", action="store_true",
                    help="also report pairs within the same chapter (default: cross-chapter only... "
                         "actually both are reported; this flag restricts to same-chapter)")
    args = ap.parse_args()

    if args.all:
        paths = sorted(CHAPTERS.glob("*.tex"))
    else:
        paths = [Path(f) for f in args.files]
    paths = [p for p in paths if p.exists()]
    if not paths:
        sys.exit("no input files")

    tok = PunktSentenceTokenizer()
    sentences = []  # (file, idx, text, stems)
    for p in paths:
        prose = strip_latex(p.read_text())
        for i, s in enumerate(tok.tokenize(prose)):
            s = s.strip()
            if len(s.split()) < args.min_words:
                continue
            sentences.append((p.stem, i, s, stems(s, args.stem)))

    print(f"# {len(sentences)} sentences from {len(paths)} files "
          f"(stem={args.stem}, jaccard>={args.threshold}, min_words={args.min_words})\n")

    # ---- pairwise jaccard ----
    pairs = []
    for (f1, i1, s1, t1), (f2, i2, s2, t2) in itertools.combinations(sentences, 2):
        if f1 == f2 and abs(i1 - i2) <= 1:
            continue  # adjacent in-source sentences legitimately share terms
        j = jaccard(t1, t2)
        if j >= args.threshold:
            pairs.append((j, f1, s1, f2, s2))
    pairs.sort(reverse=True)

    print(f"## Near-duplicate pairs: {len(pairs)}\n")
    for j, f1, s1, f2, s2 in pairs:
        scope = "SAME-CH" if f1 == f2 else "CROSS  "
        print(f"[{j:.2f}] {scope}")
        print(f"   {f1}: {s1}")
        print(f"   {f2}: {s2}\n")

    # ---- sorted-adjacent pass (long shared prefixes) ----
    norm = sorted((re.sub(r"[^a-z0-9 ]", "", s.lower()), f, s) for f, _, s, _ in sentences)
    print("## Sorted-adjacent shared prefixes (>=40 chars)\n")
    seen = set()
    for (n1, f1, s1), (n2, f2, s2) in zip(norm, norm[1:]):
        common = 0
        for a, b in zip(n1, n2):
            if a != b:
                break
            common += 1
        if common >= 40 and (f1, s1[:60]) not in seen:
            seen.add((f1, s1[:60]))
            print(f"[{common}ch] {f1}: {s1}")
            print(f"       {f2}: {s2}\n")


if __name__ == "__main__":
    main()
