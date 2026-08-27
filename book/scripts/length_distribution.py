#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pydetex>=1.1.1",
#     "nupunkt>=0.6.0",
#     "pyyaml>=6.0",
# ]
# ///
"""Sentence- and paragraph-length DISTRIBUTION, with per-style targets.

prose_metrics.py summarizes length with a mean and a cv (burstiness). This
shows the actual *shape* — percentiles and a histogram — so you can see whether
the variance comes from a healthy mix of short and long sentences or from a few
outliers dragging the mean around. Sentence segmentation and paragraph
detection match prose_metrics.py, so the mean/cv columns reconcile.

Length targets are style-dependent, so this reads the SAME genre profile the
rest of the toolchain uses: book.yaml `style.profile` ->
docs/guides/styles/<profile>.md's ```style-targets``` block. Narrative
nonfiction wants 15-20-word sentences with wide, deliberate variance; a
practical guide or young-readers book wants shorter and flatter. Override the
profile per-run with --style; with no profile set, base STYLE.md defaults apply.

    uv run scripts/length_distribution.py                 # whole book, active profile
    uv run scripts/length_distribution.py --chapter 03
    uv run scripts/length_distribution.py --style young-readers
    uv run scripts/length_distribution.py --by-chapter
    uv run scripts/length_distribution.py --format jsonl

Advisory only — never a CI gate.
"""
from __future__ import annotations
import argparse
import io
import json
import re
import statistics
from contextlib import redirect_stdout
from pathlib import Path

# same corpus recipe as prose_metrics.py / check_prose.py
SUBDIRS = ("chapters", "frontmatter", "front-matter", "backmatter", "back-matter")
DROP_ENVS = (
    "tikzpicture", "figure", "table", "tabular", "tabularx", "lstlisting",
    "verbatim", "Verbatim", "equation", "align", "alignat", "gather",
    "definitionbox", "tryitbox", "examplebox", "codelisting", "promptcode",
    "outputcode", "timeline", "timelinetitled",
)

# Base STYLE.md defaults; a genre profile's ```style-targets``` overrides these.
LENGTH_DEFAULTS = {
    "sentence_avg_lo": 14.0,
    "sentence_avg_hi": 20.0,
    "sentence_hard_max": 35.0,
    "paragraph_sents_lo": 3.0,
    "paragraph_sents_hi": 7.0,
}
LENGTH_KEYS = tuple(LENGTH_DEFAULTS)

# Fallback bands for --style when a book does not vendor docs/guides/styles/.
# Kept in sync with the ```style-targets``` blocks in those profiles.
PROFILE_FALLBACK = {
    "narrative-nonfiction": {"sentence_avg_lo": 15, "sentence_avg_hi": 20,
                             "sentence_hard_max": 35,
                             "paragraph_sents_lo": 3, "paragraph_sents_hi": 7},
    "technical-handson":    {"sentence_avg_lo": 12, "sentence_avg_hi": 20,
                             "sentence_hard_max": 35,
                             "paragraph_sents_lo": 2, "paragraph_sents_hi": 6},
    "practical-guide":      {"sentence_avg_lo": 12, "sentence_avg_hi": 18,
                             "sentence_hard_max": 30,
                             "paragraph_sents_lo": 2, "paragraph_sents_hi": 5},
    "young-readers":        {"sentence_avg_lo": 12, "sentence_avg_hi": 18,
                             "sentence_hard_max": 30,
                             "paragraph_sents_lo": 2, "paragraph_sents_hi": 5},
    "verse-translation":    {"sentence_avg_lo": 6, "sentence_avg_hi": 16,
                             "sentence_hard_max": 40,
                             "paragraph_sents_lo": 1, "paragraph_sents_hi": 8},
}


def strip_latex(text: str) -> str:
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        from pydetex import pipelines
    text = re.sub(r"(?m)^%.*$", "", text)
    for env in DROP_ENVS:
        text = re.sub(rf"\\begin\{{{env}\*?\}}.*?\\end\{{{env}\*?\}}", " ",
                      text, flags=re.DOTALL)
    text = re.sub(r"\\\[.*?\\\]", " ", text, flags=re.DOTALL)
    text = re.sub(r"\$[^$]*\$", " ", text)
    text = re.sub(r"\\(?:input|include|includegraphics)(?:\[[^\]]*\])?\{[^}]*\}",
                  " ", text)
    with redirect_stdout(io.StringIO()):
        cleaned = pipelines.strict(text)
    return cleaned


def light_detex(text: str) -> str:
    text = re.sub(r"(?<!\\)%.*", "", text)
    for env in DROP_ENVS:
        text = re.sub(rf"\\begin\{{{env}\*?\}}.*?\\end\{{{env}\*?\}}", " ",
                      text, flags=re.DOTALL)
    text = re.sub(r"\$[^$]*\$", " ", text)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", text)
    text = re.sub(r"[{}~]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def paragraphs_of(source: str) -> list[str]:
    """Blank-line-separated prose blocks, detexed individually. Matches
    prose_metrics.py: lone commands and sub-15-word blocks are fragments,
    not paragraphs."""
    paras = []
    for block in re.split(r"\n\s*\n", source):
        block = block.strip()
        if not block or (block.startswith("\\") and "\n" not in block):
            continue
        prose = light_detex(block)
        if len(prose.split()) >= 15:
            paras.append(prose)
    return paras


def load_targets(root: Path, style: str | None) -> tuple[dict, str]:
    """LENGTH_DEFAULTS overlaid with the active genre profile's style-targets.

    Profile resolution: --style arg, else book.yaml `style.profile`. Reads the
    profile's ```style-targets``` block when the .md is vendored, else the
    baked-in PROFILE_FALLBACK, else defaults.
    """
    import yaml
    targets = dict(LENGTH_DEFAULTS)
    profile = style
    if profile is None:
        book_yaml = root / "book.yaml"
        if book_yaml.exists():
            try:
                cfg = yaml.safe_load(book_yaml.read_text()) or {}
                profile = (cfg.get("style") or {}).get("profile") or None
            except yaml.YAMLError:
                profile = None
    if not profile:
        return targets, "base STYLE.md"

    prof_md = root / "docs" / "guides" / "styles" / f"{profile}.md"
    block = {}
    if prof_md.exists():
        m = re.search(r"```style-targets\n(.*?)```", prof_md.read_text(), re.DOTALL)
        if m:
            try:
                block = yaml.safe_load(m.group(1)) or {}
            except yaml.YAMLError:
                block = {}
    if not block:
        block = PROFILE_FALLBACK.get(profile, {})
    for key in LENGTH_KEYS:
        if key in block:
            targets[key] = float(block[key])
    return targets, profile


def discover(root: Path) -> list[Path]:
    files: list[Path] = []
    for name in SUBDIRS:
        d = root / "latex" / name
        if d.exists():
            files += sorted(d.glob("*.tex"))
    return files


def pctl(vals: list[float], q: float) -> float:
    if not vals:
        return 0.0
    s = sorted(vals)
    i = q * (len(s) - 1)
    lo, hi = int(i), min(int(i) + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (i - lo)


def summarize(vals: list[int]) -> dict:
    if not vals:
        return {"n": 0}
    m = statistics.mean(vals)
    sd = statistics.pstdev(vals) if len(vals) > 1 else 0.0
    return {"n": len(vals), "mean": m, "median": statistics.median(vals),
            "sd": sd, "cv": (sd / m if m else 0.0), "min": min(vals),
            "p10": pctl(vals, .10), "p25": pctl(vals, .25), "p75": pctl(vals, .75),
            "p90": pctl(vals, .90), "p95": pctl(vals, .95), "max": max(vals)}


def histogram(vals: list[int], edges: list[int], width: int = 34) -> list[str]:
    labels, counts, prev = [], [], 0
    for e in edges:
        labels.append(f"{prev}-{e}")
        counts.append(sum(1 for v in vals if prev < v <= e))
        prev = e
    labels.append(f"{prev}+")
    counts.append(sum(1 for v in vals if v > prev))
    top = max(counts) or 1
    rows = []
    for lab, c in zip(labels, counts):
        bar = "#" * round(width * c / top)
        share = 100 * c / len(vals) if vals else 0
        rows.append(f"    {lab:>6}  {bar:<{width}} {c:>5} ({share:4.1f}%)")
    return rows


def collect(files, tok):
    sent_lens, para_sent_lens, para_word_lens, per_chapter = [], [], [], []
    for f in files:
        source = f.read_text(encoding="utf-8")
        prose = re.sub(r"\s+", " ", strip_latex(source)).strip()
        ch = [len(s.split()) for s in tok.tokenize(prose) if len(s.split()) >= 2]
        sent_lens += ch
        for para in paragraphs_of(source):
            para_word_lens.append(len(para.split()))
            para_sent_lens.append(sum(1 for s in tok.tokenize(para) if s.strip()))
        if ch:
            per_chapter.append((f.name, ch))
    return sent_lens, para_sent_lens, para_word_lens, per_chapter


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--chapter", help="restrict to files whose name starts with this")
    ap.add_argument("--style", choices=sorted(PROFILE_FALLBACK),
                    help="override the genre profile for this run")
    ap.add_argument("--by-chapter", action="store_true",
                    help="per-chapter mean/cv table instead of the full distribution")
    ap.add_argument("--format", choices=("table", "jsonl"), default="table")
    args = ap.parse_args()

    from nupunkt import PunktSentenceTokenizer
    tok = PunktSentenceTokenizer()

    files = discover(args.root)
    if args.chapter:
        files = [f for f in files if f.name.startswith(args.chapter)]
    if not files:
        raise SystemExit(f"length_distribution: no .tex files under {args.root}")

    tgt, profile = load_targets(args.root, args.style)
    avg_lo, avg_hi = tgt["sentence_avg_lo"], tgt["sentence_avg_hi"]
    hard_max = tgt["sentence_hard_max"]
    para_lo, para_hi = tgt["paragraph_sents_lo"], tgt["paragraph_sents_hi"]

    sent_lens, para_sent_lens, para_word_lens, per_chapter = collect(files, tok)

    if args.format == "jsonl":
        print(json.dumps({"profile": profile, "targets": tgt, "files": len(files),
                          "sentence_words": summarize(sent_lens),
                          "paragraph_sentences": summarize(para_sent_lens),
                          "paragraph_words": summarize(para_word_lens)}))
        return

    if args.by_chapter:
        print(f"\nprofile={profile}  sentence avg target "
              f"{avg_lo:g}-{avg_hi:g}, hard max {hard_max:g}\n")
        print(f"  {'chapter':<26}{'sents':>6}{'mean':>7}{'cv':>6}{'max':>5}{'>max':>6}")
        print("  " + "-" * 56)
        for name, ch in per_chapter:
            m = statistics.mean(ch)
            sd = statistics.pstdev(ch) if len(ch) > 1 else 0.0
            cv = sd / m if m else 0.0
            over = sum(1 for x in ch if x > hard_max)
            flag = "" if avg_lo <= m <= avg_hi and over == 0 else "  <-"
            print(f"  {name:<26}{len(ch):>6}{m:>7.1f}{cv:>6.2f}{max(ch):>5}{over:>6}{flag}")
        return

    s, ps, pw = summarize(sent_lens), summarize(para_sent_lens), summarize(para_word_lens)
    over = sum(1 for x in sent_lens if x > hard_max)
    short = sum(1 for x in sent_lens if x <= 8)
    para_in = sum(1 for x in para_sent_lens if para_lo <= x <= para_hi)

    scope = "/".join(f.name for f in files) if args.chapter else "whole book"
    print(f"\n=== {scope} | profile: {profile} ===")
    print(f"\nSENTENCE LENGTH (words)   n={s['n']}   "
          f"target mean {avg_lo:g}-{avg_hi:g}, hard max {hard_max:g}")
    print(f"  mean {s['mean']:.1f}  median {s['median']:.0f}  sd {s['sd']:.1f}  "
          f"cv {s['cv']:.2f} (burstiness)")
    print(f"  min {s['min']}  p10 {s['p10']:.0f}  p25 {s['p25']:.0f}  "
          f"p75 {s['p75']:.0f}  p90 {s['p90']:.0f}  p95 {s['p95']:.0f}  max {s['max']}")
    print(f"  short (<=8w): {100*short/s['n']:.1f}%   "
          f"over hard-max (>{hard_max:g}w): {over} ({100*over/s['n']:.1f}%)")
    print(f"  mean-in-target: {'OK' if avg_lo <= s['mean'] <= avg_hi else 'OUT OF BAND'}"
          f"   burstiness: {'healthy (cv>=0.5)' if s['cv'] >= 0.5 else 'flat (cv<0.5)'}")
    print("  histogram:")
    for row in histogram(sent_lens, [5, 10, 15, 20, 25, 30, 35]):
        print(row)

    print(f"\nPARAGRAPH LENGTH   n={ps['n']}   target {para_lo:g}-{para_hi:g} sentences")
    print(f"  sentences/para: mean {ps['mean']:.1f}  median {ps['median']:.0f}  "
          f"min {ps['min']}  p90 {ps['p90']:.0f}  max {ps['max']}")
    print(f"  words/para:     mean {pw['mean']:.0f}  median {pw['median']:.0f}  "
          f"p90 {pw['p90']:.0f}  max {pw['max']}")
    print(f"  in-target ({para_lo:g}-{para_hi:g} sents): {100*para_in/ps['n']:.1f}%")
    print("  histogram (sentences per paragraph):")
    for row in histogram(para_sent_lens, [1, 2, 3, 4, 5, 6, 7]):
        print(row)
    print()


if __name__ == "__main__":
    main()
