#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pydetex>=1.1.1",
#     "nupunkt>=0.6.0",
#     "pyyaml>=6.0",
# ]
# ///
"""Per-chapter prose-quality metrics: burstiness, lexical diversity, density.

Quantifies the "AI flatness" signals that STYLE-AI-TELLS.md Part 6 only
eyeballs. Every metric is grounded in the detection/homogenization
literature (GPTZero-style burstiness; MTLD/MATTR from McCarthy & Jarvis
2010, used by the LLM-homogenization studies; compression ratio per
Shaib et al. 2024 "Standardizing the Measurement of Text Diversity",
arXiv:2403.00553 — one of the most robust diversity scores):

  sents   sentences               mean/sd  sentence length (words)
  cv      sd/mean — burstiness. Uniform machine prose sits low.
  mtld    Measure of Textual Lexical Diversity (length-robust TTR)
  mattr   Moving-Average TTR, window 50
  comp    zlib compression ratio of the prose (lower = more repetitive)
  adv%    -ly adverb share of words
  para-cv paragraph-length variation (uniform paragraphs = AI tell 2.1)
  spec    specificity: digits + mid-sentence proper nouns per 100 words
          (human prose is dense in checkable particulars; see the
          humanization moves in STYLE-CRAFT.md section 11)

Default thresholds (advisory WARNs, tuned so the template's edited books
pass with margin: their chapters score cv .55-.68, mtld 100-175):

  cv >= 0.45   mtld >= 80   mattr >= 0.78   adv% <= 2.5   para-cv >= 0.30

A genre profile (docs/guides/styles/<name>.md via book.yaml `style.profile`)
can override with keys in its ```style-targets block: burstiness_cv_min,
mtld_min, mattr_min, adverb_pct_max, para_cv_min.

Advisory by default — exits 0 unless --strict (then chapter WARNs fail).

If scripts/data/prose-baseline.json exists (or --baseline FILE is given),
chapters are also compared against the house corpus percentile bands and
values outside p10..p90 get an informational note (never a failure).
Regenerate the baseline from a set of edited books with:

    uv run scripts/prose_metrics.py --write-baseline scripts/data/prose-baseline.json \
        --root ../book-a --root ../book-b --root ../book-c

Usage:
    uv run scripts/prose_metrics.py                 # per-chapter table
    uv run scripts/prose_metrics.py --strict        # WARNs become failures
    uv run scripts/prose_metrics.py --root ../other-book
    uv run scripts/prose_metrics.py --format jsonl  # machine-readable
"""

from __future__ import annotations

import argparse
import io
import json
import re
import statistics
import sys
import zlib
from contextlib import redirect_stdout
from pathlib import Path

# same corpus recipe as check_prose.py / vocab_variety.py
SUBDIRS = ("chapters", "frontmatter", "front-matter", "backmatter", "back-matter")
DROP_ENVS = (
    "tikzpicture", "figure", "table", "tabular", "tabularx", "lstlisting",
    "verbatim", "Verbatim", "equation", "align", "alignat", "gather",
    "definitionbox", "tryitbox", "examplebox", "codelisting", "promptcode",
    "outputcode",
)
WORD_RE = re.compile(r"[a-z][a-z'-]*[a-z]|[a-z]")

DEFAULTS = {
    "burstiness_cv_min": 0.45,
    "mtld_min": 80.0,
    "mattr_min": 0.78,
    "adverb_pct_max": 2.5,
    "para_cv_min": 0.30,
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
    """Cheap regex detex — good enough for paragraph word counts, and safe
    on tiny blocks that crash pydetex."""
    text = re.sub(r"(?<!\\)%.*", "", text)
    for env in DROP_ENVS:
        text = re.sub(rf"\\begin\{{{env}\*?\}}.*?\\end\{{{env}\*?\}}", " ",
                      text, flags=re.DOTALL)
    text = re.sub(r"\$[^$]*\$", " ", text)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", text)
    text = re.sub(r"[{}~]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def paragraphs_of(source: str) -> list[str]:
    """Paragraph word counts from the raw LaTeX (blank-line separated),
    stripped individually so structure survives."""
    paras = []
    for block in re.split(r"\n\s*\n", source):
        block = block.strip()
        if not block or (block.startswith("\\") and "\n" not in block):
            continue  # lone commands (\chapter{...}, \input) aren't paragraphs
        prose = light_detex(block)
        if len(prose.split()) >= 15:
            paras.append(prose)
    return paras


def mtld(tokens: list[str], ttr_threshold: float = 0.72) -> float:
    def one_pass(toks: list[str]) -> float:
        factors, types, count = 0.0, set(), 0
        for t in toks:
            count += 1
            types.add(t)
            if len(types) / count <= ttr_threshold:
                factors += 1
                types, count = set(), 0
        if count:
            factors += (1 - len(types) / count) / (1 - ttr_threshold)
        return len(toks) / factors if factors else 0.0
    if not tokens:
        return 0.0
    return (one_pass(tokens) + one_pass(tokens[::-1])) / 2


def mattr(tokens: list[str], window: int = 50) -> float:
    if not tokens:
        return 0.0
    if len(tokens) < window:
        return len(set(tokens)) / len(tokens)
    vals = [len(set(tokens[i:i + window])) / window
            for i in range(len(tokens) - window + 1)]
    return sum(vals) / len(vals)


def cv(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = statistics.mean(values)
    return statistics.stdev(values) / m if m else 0.0


def discover(root: Path) -> list[Path]:
    files: list[Path] = []
    for name in SUBDIRS:
        d = root / "latex" / name
        if d.exists():
            files += sorted(d.glob("*.tex"))
    return files


def load_targets(root: Path) -> dict[str, float]:
    """DEFAULTS overlaid with the selected genre profile's style-targets."""
    import yaml
    targets = dict(DEFAULTS)
    book_yaml = root / "book.yaml"
    if not book_yaml.exists():
        return targets
    try:
        cfg = yaml.safe_load(book_yaml.read_text()) or {}
        profile = (cfg.get("style") or {}).get("profile")
    except yaml.YAMLError:
        return targets
    if not profile:
        return targets
    prof_md = root / "docs" / "guides" / "styles" / f"{profile}.md"
    if not prof_md.exists():
        return targets
    m = re.search(r"```style-targets\n(.*?)```", prof_md.read_text(), re.DOTALL)
    if not m:
        return targets
    try:
        block = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return targets
    for key in DEFAULTS:
        if key in block:
            targets[key] = float(block[key])
    return targets


def analyze(path: Path, tok) -> dict | None:
    source = path.read_text()
    prose = re.sub(r"\s+", " ", strip_latex(source)).strip()
    words = WORD_RE.findall(prose.lower())
    if len(words) < 200:  # too short for stable diversity metrics
        return None
    sents = [s for s in tok.tokenize(prose) if len(s.split()) >= 2]
    lens = [float(len(s.split())) for s in sents]
    para_lens = [float(len(p.split())) for p in paragraphs_of(source)]
    adv = sum(1 for w in words if w.endswith("ly") and len(w) > 4)
    # specificity: checkable particulars — digit tokens plus capitalized
    # tokens that are not sentence-initial (proper-noun heuristic)
    particulars = 0
    for s in sents:
        toks = s.split()
        particulars += sum(1 for t_ in toks if any(c.isdigit() for c in t_))
        particulars += sum(1 for t_ in toks[1:]
                           if t_[:1].isupper() and t_[1:2].islower())
    return {
        "file": path.name,
        "words": len(words),
        "sents": len(sents),
        "mean_len": round(statistics.mean(lens), 1) if lens else 0.0,
        "cv": round(cv(lens), 2),
        "mtld": round(mtld(words), 1),
        "mattr": round(mattr(words), 3),
        "comp": round(len(zlib.compress(prose.encode(), 9))
                      / max(1, len(prose.encode())), 3),
        "adv_pct": round(100 * adv / len(words), 1),
        "para_cv": round(cv(para_lens), 2),
        "spec": round(100 * particulars / len(words), 1),
    }


def warnings_for(m: dict, t: dict[str, float]) -> list[str]:
    w = []
    if m["cv"] < t["burstiness_cv_min"]:
        w.append(f"cv {m['cv']} < {t['burstiness_cv_min']} — uniform sentence "
                 "lengths (burstiness; STYLE-AI-TELLS Part 6)")
    if m["mtld"] < t["mtld_min"]:
        w.append(f"mtld {m['mtld']} < {t['mtld_min']:g} — low lexical "
                 "diversity (try `make vocab`)")
    if m["mattr"] < t["mattr_min"]:
        w.append(f"mattr {m['mattr']} < {t['mattr_min']} — low moving-window "
                 "diversity")
    if m["adv_pct"] > t["adverb_pct_max"]:
        w.append(f"adverbs {m['adv_pct']}% > {t['adverb_pct_max']}% — trim -ly "
                 "adverbs (adverb budget)")
    if m["para_cv"] > 0 and m["para_cv"] < t["para_cv_min"]:
        w.append(f"para-cv {m['para_cv']} < {t['para_cv_min']} — uniform "
                 "paragraph sizes (tell 2.1)")
    return w


# ------------------------------------------------------------- house baseline

BASELINE_DEFAULT = Path(__file__).resolve().parent / "data" / "prose-baseline.json"
# direction of badness for house-band notes: -1 = low is suspect, +1 = high
# is, 0 = both tails. mtld/mattr flag both ways: below p10 = repetitive
# draft; above p90 = the raw-LLM "elegant variation" signature (validated
# against a raw claude-sonnet-5 draft, which scored mtld 222 vs house p90 161
# while sitting at cv 0.39 vs house p10 0.52).
BAND_DIRECTION = {"cv": -1, "mtld": 0, "mattr": 0, "comp": -1,
                  "para_cv": -1, "spec": -1, "adv_pct": +1}


def percentile(sorted_vals: list[float], q: float) -> float:
    if not sorted_vals:
        return 0.0
    idx = (len(sorted_vals) - 1) * q
    lo, hi = int(idx), min(int(idx) + 1, len(sorted_vals) - 1)
    frac = idx - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def write_baseline(rows: list[dict], roots: list[Path], out: Path) -> None:
    metrics = {}
    for key in ("cv", "mtld", "mattr", "comp", "adv_pct", "para_cv", "spec",
                "mean_len"):
        vals = sorted(r[key] for r in rows if key in r)
        metrics[key] = {"p10": round(percentile(vals, 0.10), 3),
                        "p50": round(percentile(vals, 0.50), 3),
                        "p90": round(percentile(vals, 0.90), 3)}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "_generated_by": "scripts/prose_metrics.py --write-baseline",
        "_note": "house percentile bands from edited books; regenerate per "
                 "the prose_metrics.py docstring, never hand-edit",
        "source_roots": [r.name for r in roots],
        "chapters": len(rows),
        "metrics": metrics,
    }, indent=2) + "\n")
    print(f"prose_metrics: baseline from {len(rows)} chapters "
          f"({len(roots)} book(s)) -> {out}", file=sys.stderr)


def house_notes(m: dict, baseline: dict) -> list[str]:
    notes = []
    for key, band in baseline.get("metrics", {}).items():
        if key not in m or key not in BAND_DIRECTION:
            continue
        d = BAND_DIRECTION[key]
        if d <= 0 and m[key] < band["p10"]:
            notes.append(f"{key} {m[key]} below house p10 ({band['p10']})")
        elif d >= 0 and m[key] > band["p90"]:
            notes.append(f"{key} {m[key]} above house p90 ({band['p90']})"
                         + (" — possible elegant variation"
                            if key in ("mtld", "mattr") else ""))
    return notes


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, action="append", default=None,
                    help="book root; repeatable (default: this repo)")
    ap.add_argument("--chapter", help="restrict to files starting with this")
    ap.add_argument("--format", choices=("table", "jsonl"), default="table")
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero if any chapter has warnings")
    ap.add_argument("--baseline", type=Path, default=None,
                    help="house-baseline JSON to compare against "
                         "(default: scripts/data/prose-baseline.json if present)")
    ap.add_argument("--write-baseline", type=Path, default=None,
                    help="compute percentile bands over all --root books and "
                         "write them to this JSON file")
    args = ap.parse_args()
    roots = args.root or [Path(__file__).resolve().parent.parent]

    from nupunkt import PunktSentenceTokenizer
    tok = PunktSentenceTokenizer()

    files = []
    for root in roots:
        files += discover(root)
    if args.chapter:
        files = [f for f in files if f.name.startswith(args.chapter)]
    if not files:
        raise SystemExit(f"prose_metrics: no .tex files under {roots}")

    targets = load_targets(roots[0])
    baseline = None
    if args.write_baseline is None:
        bl_path = args.baseline or (
            BASELINE_DEFAULT if BASELINE_DEFAULT.exists() else None)
        if bl_path:
            try:
                baseline = json.loads(Path(bl_path).read_text())
            except (OSError, json.JSONDecodeError) as e:
                print(f"prose_metrics: WARN unreadable baseline {bl_path}: {e}",
                      file=sys.stderr)
    rows, all_warns = [], []
    for f in files:
        m = analyze(f, tok)
        if m is None:
            continue
        m["warnings"] = warnings_for(m, targets)
        m["house_notes"] = house_notes(m, baseline) if baseline else []
        rows.append(m)
        all_warns += [(m["file"], w) for w in m["warnings"]]

    if args.write_baseline is not None:
        write_baseline(rows, roots, args.write_baseline)
        return

    if args.format == "jsonl":
        for m in rows:
            print(json.dumps(m))
    else:
        hdr = (f"{'chapter':32s} {'words':>6s} {'sents':>5s} {'mean':>5s} "
               f"{'cv':>5s} {'mtld':>6s} {'mattr':>6s} {'comp':>5s} "
               f"{'adv%':>5s} {'p-cv':>5s} {'spec':>5s}")
        print(hdr)
        print("-" * len(hdr))
        for m in rows:
            flag = " !" if m["warnings"] else ""
            print(f"{m['file']:32s} {m['words']:6d} {m['sents']:5d} "
                  f"{m['mean_len']:5.1f} {m['cv']:5.2f} {m['mtld']:6.1f} "
                  f"{m['mattr']:6.3f} {m['comp']:5.3f} {m['adv_pct']:5.1f} "
                  f"{m['para_cv']:5.2f} {m['spec']:5.1f}{flag}")
        if rows:
            print()
            for fname, w in all_warns:
                print(f"WARN {fname}: {w}")
            for m in rows:
                for note in m.get("house_notes", []):
                    print(f"note {m['file']}: {note} [house baseline]")
            n = len(all_warns)
            print(f"prose_metrics: {len(rows)} chapters, {n} warning(s)")

    if args.strict and all_warns:
        sys.exit(1)


if __name__ == "__main__":
    main()
