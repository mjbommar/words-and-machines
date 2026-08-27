#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pydetex>=1.1.1",
#     "nupunkt>=0.6.0",
#     "pyyaml>=6.0",
#     "pronouncing>=0.2.0",
# ]
# ///
"""Prose-cadence audit: sentence-final stress patterns and length contour.

The rhythm sibling of `prose_metrics.py`. Where that script measures how
*long* sentences are, this one measures how they *land* — the stress
shape of the last few syllables — and how sentence lengths move inside a
paragraph. Both are craft dimensions the ontology's `sound_and_rhythm`
branch names (docs/architecture/writing-ontology.md); this script says
which of those moves the draft is actually using.

Stress comes from the CMU Pronouncing Dictionary via `pronouncing`, with
a regex syllable/stress fallback for out-of-vocabulary words. Only
primary stress (CMU digit 1) counts as an ictus; secondary stress (2) is
treated as unstressed, since English secondary stress is a half-beat,
not a word accent. Monosyllabic function words (articles, prepositions,
auxiliaries, pronouns, conjunctions) are forced unstressed — CMU marks
them 1 in isolation, but prose rhythm does not.

Cadence labels (the tail is the last 7 syllables, ' = ictus, x = slack):

  planus    ' x x ' x        cursus planus — the calm, closed fall
  tardus    ' x x ' x x      cursus tardus — slower, more formal drop
  velox     ' x x x x ' x    cursus velox — the long swinging close
  punch     final word is a stressed monosyllable ("...and it broke.")
  rising    final syllable stressed, polysyllabic word ("...the result.")
  falling   exactly one unstressed final syllable ("...a matter.")
  trailing  two or more unstressed final syllables ("...necessary.")

The cursus labels are approximations: classical cursus counts word
accents in Latin clausulae, and English stress-timing only rhymes with
it. Read them as "this ending has a cursus-like shape", not as a claim
about Latin prose rhythm.

Paragraph contour classifies each paragraph's sentence-length series:

  plateau     lengths barely move (cv < 0.20)
  sawtooth    lengths alternate direction nearly every sentence
  crescendo   lengths trend up across the paragraph
  diminuendo  lengths trend down
  mixed       none of the above

Paragraphs whose sentences all sit in one length band (<=10, 11-20,
21-30, >30 words) are flagged separately: same shape, every time.

Advisory thresholds (a genre profile's ```style-targets``` block may
override them with these keys):

  cadence_share_max     0.45   max share for the single most common cadence
  cadence_run_max       4      longest allowed run of identical cadences
  uniform_para_pct_max  25     max % of paragraphs stuck in one length band

If the ontology's `sound_and_rhythm` branch is present, each chapter gets
2-3 seeded suggestions drawn from it, biased toward entries that mention
a cadence the chapter underuses.

Usage:
    uv run scripts/rhythm_audit.py                     # per-chapter table
    uv run scripts/rhythm_audit.py --chapter ch02
    uv run scripts/rhythm_audit.py --text draft.txt
    uv run scripts/rhythm_audit.py --json
    uv run scripts/rhythm_audit.py --detail            # per-chapter breakdown
    uv run scripts/rhythm_audit.py --strict            # WARNs become failures

Advisory: exits 0 unless --strict.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import random
import re
import statistics
import sys
from contextlib import redirect_stdout
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

REPO_ROOT = SCRIPTS_DIR.parent
CHAPTER_SUBDIR = ("chapters",)
ONTOLOGY_BRANCH = "sound_and_rhythm"

# same corpus recipe as prose_metrics.py / length_distribution.py
DROP_ENVS = (
    "tikzpicture", "figure", "table", "tabular", "tabularx", "lstlisting",
    "verbatim", "Verbatim", "equation", "align", "alignat", "gather",
    "definitionbox", "tryitbox", "examplebox", "codelisting", "promptcode",
    "outputcode", "timeline", "timelinetitled",
)

DEFAULTS = {
    "cadence_share_max": 0.45,
    "cadence_run_max": 4.0,
    "uniform_para_pct_max": 25.0,
}

CADENCES = ("planus", "tardus", "velox", "punch", "rising", "falling",
            "trailing")
CURSUS = ("planus", "tardus", "velox")

# Cursus tails as ictus/slack strings, longest first so velox wins.
CURSUS_TAILS = (
    ("velox", "1000010"),
    ("tardus", "100100"),
    ("planus", "10010"),
)

LENGTH_BANDS = ((10, "<=10"), (20, "11-20"), (30, "21-30"), (10 ** 6, ">30"))

# Monosyllables that carry no prose accent. CMU marks most of these "1";
# in running prose they are slack.
FUNCTION_WORDS = {
    "a", "an", "the", "and", "or", "but", "nor", "for", "yet", "so", "as",
    "at", "by", "in", "of", "off", "on", "out", "up", "to", "with", "from",
    "into", "onto", "over", "than", "that", "then", "though", "till", "if",
    "is", "am", "are", "was", "were", "be", "been", "being", "do", "does",
    "did", "done", "has", "have", "had", "can", "could", "may", "might",
    "must", "shall", "should", "will", "would", "he", "she", "it", "we",
    "they", "you", "i", "me", "him", "her", "us", "them", "my", "your",
    "his", "its", "our", "their", "this", "these", "those", "who", "whom",
    "whose", "which", "what", "when", "where", "while", "not", "no",
    "there", "here", "some", "any", "all", "each", "such", "own", "one",
    "per", "via", "upon", "about", "after", "before", "between", "through",
    "under", "until", "since", "unless", "because", "however",
}

VOWEL_GROUP_RE = re.compile(r"[aeiouy]+")
WORD_CLEAN_RE = re.compile(r"[^a-z'\-]+")

# Latinate endings whose stress is not word-initial; used only by the
# out-of-vocabulary fallback.
PENULT_SUFFIXES = ("tion", "sion", "cian", "tional", "ical", "ially")
ANTEPENULT_SUFFIXES = ("ity", "ify", "ogy", "ular", "ative", "itude", "omy")


# ------------------------------------------------------------------ corpus


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


def paragraphs_of(source: str, is_latex: bool) -> list[str]:
    """Blank-line-separated prose blocks. Matches prose_metrics.py: lone
    commands and sub-15-word blocks are fragments, not paragraphs."""
    paras = []
    for block in re.split(r"\n\s*\n", source):
        block = block.strip()
        if not block:
            continue
        if is_latex:
            if block.startswith("\\") and "\n" not in block:
                continue
            prose = light_detex(block)
        else:
            prose = re.sub(r"\s+", " ", block)
        if len(prose.split()) >= 15:
            paras.append(prose)
    return paras


def discover(root: Path) -> list[Path]:
    """Chapters under <root>/latex/chapters, or *.tex directly in root."""
    files: list[Path] = []
    for name in CHAPTER_SUBDIR:
        d = root / "latex" / name
        if d.is_dir():
            files += sorted(d.glob("*.tex"))
    if not files and root.is_dir():
        files += sorted(root.glob("*.tex"))
    return files


def load_targets(root: Path) -> dict[str, float]:
    """DEFAULTS overlaid with the active genre profile's style-targets."""
    import yaml
    targets = dict(DEFAULTS)
    book_yaml = root / "book.yaml"
    if not book_yaml.exists():
        return targets
    try:
        cfg = yaml.safe_load(book_yaml.read_text()) or {}
        profile = (cfg.get("style") or {}).get("profile")
    except (yaml.YAMLError, OSError):
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
            with contextlib.suppress(TypeError, ValueError):
                targets[key] = float(block[key])
    return targets


# ------------------------------------------------------------ stress model


def syllable_estimate(word: str) -> int:
    """Regex syllable count for OOV words: vowel groups, silent-e removed."""
    w = word.lower()
    groups = VOWEL_GROUP_RE.findall(w)
    n = len(groups)
    if n > 1 and w.endswith("e") and not w.endswith(("le", "ee", "ye")):
        n -= 1
    if w.endswith(("ed",)) and n > 1 and not re.search(r"[td]ed$", w):
        n -= 1
    return max(1, n)


def fallback_stresses(word: str) -> str:
    """Stress guess for a word CMU does not know."""
    n = syllable_estimate(word)
    if n == 1:
        return "0" if word in FUNCTION_WORDS else "1"
    idx = 0  # English default: initial stress
    if word.endswith(PENULT_SUFFIXES) and n >= 2:
        idx = n - 2
    elif word.endswith(ANTEPENULT_SUFFIXES) and n >= 3:
        idx = n - 3
    return "".join("1" if i == idx else "0" for i in range(n))


def word_stresses(raw: str, cache: dict[str, str]) -> str:
    """Ictus/slack string for one word: '1' primary stress, '0' otherwise."""
    word = WORD_CLEAN_RE.sub("", raw.lower()).strip("'-")
    if not word:
        return ""
    if word in cache:
        return cache[word]
    if "-" in word:
        out = "".join(word_stresses(part, cache) for part in word.split("-")
                      if part)
        cache[word] = out
        return out
    import pronouncing
    phones = pronouncing.phones_for_word(word)
    if phones:
        raw_stress = pronouncing.stresses(phones[0])
        # secondary stress (2) is a half-beat, not a word accent
        out = "".join("1" if ch == "1" else "0" for ch in raw_stress)
        if not out:
            out = fallback_stresses(word)
    else:
        out = fallback_stresses(word)
    if word in FUNCTION_WORDS and len(out) == 1:
        out = "0"
    cache[word] = out
    return out


def tail_pattern(sentence: str, cache: dict[str, str],
                 max_syll: int = 7) -> tuple[str, list[str]]:
    """Stress string of the final <=7 syllables plus the words it covers."""
    words = [w for w in re.findall(r"[A-Za-z][A-Za-z'\-]*", sentence) if w]
    pattern, used = "", []
    for w in reversed(words):
        s = word_stresses(w, cache)
        if not s:
            continue
        pattern = s + pattern
        used.insert(0, w)
        if len(pattern) >= max_syll:
            break
    if len(pattern) > max_syll:
        cut = len(pattern) - max_syll
        pattern = pattern[cut:]
    return pattern, used


def classify_cadence(sentence: str, cache: dict[str, str]) -> dict | None:
    pattern, used = tail_pattern(sentence, cache)
    if not pattern or not used:
        return None
    label = None
    for name, tail in CURSUS_TAILS:
        if pattern.endswith(tail):
            label = name
            break
    if label is None:
        last_word = used[-1]
        last_stress = word_stresses(last_word, cache)
        trailing_slack = len(pattern) - len(pattern.rstrip("0"))
        if trailing_slack == 0:
            label = "punch" if len(last_stress) == 1 else "rising"
        elif trailing_slack == 1:
            label = "falling"
        else:
            label = "trailing"
    return {
        "label": label,
        "pattern": pattern,
        "tail": " ".join(used[-3:]),
    }


# --------------------------------------------------------- length contour


def band_of(n: int) -> str:
    for edge, name in LENGTH_BANDS:
        if n <= edge:
            return name
    return ">30"


def slope(values: list[float]) -> float:
    n = len(values)
    xs = list(range(n))
    mx, my = statistics.mean(xs), statistics.mean(values)
    denom = sum((x - mx) ** 2 for x in xs)
    if denom == 0:
        return 0.0
    return sum((x - mx) * (y - my)
               for x, y in zip(xs, values, strict=True)) / denom


def contour_of(lens: list[int]) -> str:
    if len(lens) < 3:
        return "unscored"  # fewer than three sentences: no contour to read
    vals = [float(v) for v in lens]
    mean = statistics.mean(vals)
    sd = statistics.pstdev(vals)
    cv = sd / mean if mean else 0.0
    diffs = [b - a for a, b in zip(vals, vals[1:], strict=False)]
    signs = [1 if d > 0 else (-1 if d < 0 else 0) for d in diffs]
    changes = sum(1 for a, b in zip(signs, signs[1:], strict=False)
                  if a and b and a != b)
    rel_slope = slope(vals) * (len(vals) - 1) / mean if mean else 0.0
    if cv < 0.20:
        return "plateau"
    if len(vals) >= 4 and changes >= len(vals) - 2 and cv >= 0.25:
        return "sawtooth"
    if rel_slope >= 0.5:
        return "crescendo"
    if rel_slope <= -0.5:
        return "diminuendo"
    return "mixed"


# ----------------------------------------------------------------- ontology


def load_ontology_branch(name: str):
    try:
        import writing_ontology
    except ImportError:
        return None
    try:
        if name not in writing_ontology.available_branches():
            return None
        return writing_ontology.load_branch(name)
    except (OSError, ValueError):
        return None


def entry_text(entry) -> str:
    if not isinstance(entry, dict):
        return str(entry)
    parts = [str(entry.get(k, "")) for k in
             ("name", "aka", "definition", "effect", "example", "register")]
    tags = entry.get("tags")
    if isinstance(tags, list):
        parts += [str(t) for t in tags]
    return " ".join(parts).lower()


def rhythm_suggestions(branch, dist: dict[str, int], seed, n: int = 3) -> list[str]:
    """Seeded picks from the ontology branch, biased toward entries that
    mention a cadence this chapter underuses. Category names are never
    hardcoded — only our own measured labels are matched against entry text."""
    if not branch:
        return []
    pool = [e for entries in branch.get("categories", {}).values()
            for e in entries]
    if not pool:
        return []
    total = sum(dist.values()) or 1
    underused = [c for c in CADENCES if dist.get(c, 0) / total < 0.05]
    rng = random.Random(seed)
    scored = []
    for e in pool:
        text = entry_text(e)
        hits = sum(1 for c in underused if c in text)
        scored.append((hits, rng.random(), e))
    scored.sort(key=lambda t: (-t[0], t[1]))
    out = []
    for _hits, _r, e in scored[:n]:
        if isinstance(e, dict):
            line = f"{e.get('name')} — {e.get('definition', '')}".strip(" —")
            if e.get("example"):
                line += f"  e.g. {e['example']}"
        else:
            line = str(e)
        out.append(line)
    return out


# ------------------------------------------------------------------ analyze


def analyze(name: str, source: str, is_latex: bool, tok,
            cache: dict[str, str]) -> dict | None:
    prose = strip_latex(source) if is_latex else source
    prose = re.sub(r"\s+", " ", prose).strip()
    sents = [s for s in tok.tokenize(prose) if len(s.split()) >= 3]
    if len(sents) < 5:
        return None

    cadences, labels, examples = [], [], {}
    for s in sents:
        c = classify_cadence(s, cache)
        if c is None:
            continue
        cadences.append(c)
        labels.append(c["label"])
        examples.setdefault(c["label"], c["tail"])
    if not labels:
        return None

    dist = {c: labels.count(c) for c in CADENCES}
    total = len(labels)

    runs, longest_runs = [], []
    start = 0
    for i in range(1, len(labels) + 1):
        if i == len(labels) or labels[i] != labels[start]:
            runs.append((labels[start], i - start, start))
            start = i
    max_run = max((r[1] for r in runs), default=0)
    for label, length, at in sorted(runs, key=lambda r: -r[1])[:3]:
        if length >= 3:
            longest_runs.append({
                "cadence": label, "length": length, "at_sentence": at + 1,
                "sample": cadences[at]["tail"],
            })

    contours: dict[str, int] = {}
    uniform_paras = []
    para_details = []
    paras = paragraphs_of(source, is_latex)
    for i, p in enumerate(paras, 1):
        p_sents = [s for s in tok.tokenize(p) if len(s.split()) >= 3]
        lens = [len(s.split()) for s in p_sents]
        shape = contour_of(lens)
        contours[shape] = contours.get(shape, 0) + 1
        bands = {band_of(n) for n in lens}
        uniform = len(lens) >= 3 and len(bands) == 1
        if uniform:
            uniform_paras.append({"paragraph": i, "band": bands.pop(),
                                  "lengths": lens,
                                  "opening": " ".join(p.split()[:8])})
        para_details.append({"paragraph": i, "shape": shape, "lengths": lens})

    n_paras = len([p for p in para_details if len(p["lengths"]) >= 3])
    top_label, top_n = max(dist.items(), key=lambda kv: kv[1])
    return {
        "file": name,
        "sents": total,
        "mean_len": round(statistics.mean([len(s.split()) for s in sents]), 1),
        "cadence_counts": dist,
        "cadence_pct": {k: round(100 * v / total, 1) for k, v in dist.items()},
        "cursus_pct": round(100 * sum(dist[c] for c in CURSUS) / total, 1),
        "top_cadence": top_label,
        "top_share": round(top_n / total, 3),
        "max_run": max_run,
        "runs": longest_runs,
        "examples": examples,
        "paragraphs": len(para_details),
        "paragraphs_scored": n_paras,
        "contours": contours,
        "uniform_band_paras": uniform_paras,
        "uniform_band_pct": round(100 * len(uniform_paras) / n_paras, 1)
        if n_paras else 0.0,
        "para_details": para_details,
    }


def warnings_for(m: dict, t: dict[str, float]) -> list[str]:
    w = []
    if m["top_share"] > t["cadence_share_max"]:
        w.append(f"{m['top_cadence']} cadence is {100 * m['top_share']:.0f}% of "
                 f"endings (> {100 * t['cadence_share_max']:.0f}%) — every "
                 "sentence lands the same way")
    if m["max_run"] > t["cadence_run_max"]:
        w.append(f"run of {m['max_run']} identical cadences "
                 f"(> {t['cadence_run_max']:g}) — vary one ending in the run")
    if m["uniform_band_pct"] > t["uniform_para_pct_max"]:
        w.append(f"{m['uniform_band_pct']}% of paragraphs keep every sentence "
                 f"in one length band (> {t['uniform_para_pct_max']:g}%)")
    return w


# -------------------------------------------------------------------- output


def print_table(rows: list[dict]) -> None:
    hdr = (f"{'chapter':32s} {'sents':>5s} {'mean':>5s} {'punch':>6s} "
           f"{'rise':>6s} {'fall':>6s} {'trail':>6s} {'cursus':>6s} "
           f"{'run':>4s} {'uni%':>5s}")
    print(hdr)
    print("-" * len(hdr))
    for m in rows:
        p = m["cadence_pct"]
        flag = " !" if m["warnings"] else ""
        print(f"{m['file']:32s} {m['sents']:5d} {m['mean_len']:5.1f} "
              f"{p['punch']:6.1f} {p['rising']:6.1f} {p['falling']:6.1f} "
              f"{p['trailing']:6.1f} {m['cursus_pct']:6.1f} "
              f"{m['max_run']:4d} {m['uniform_band_pct']:5.1f}{flag}")


def print_detail(m: dict) -> None:
    print(f"\n{m['file']} — {m['sents']} sentence endings")
    parts = []
    for c in CADENCES:
        parts.append(f"{c} {m['cadence_pct'][c]:.1f}%")
    print("  cadence: " + ", ".join(parts))
    for c in CADENCES:
        ex = m["examples"].get(c)
        if ex:
            print(f"    {c:9s} e.g. \u201c...{ex}\u201d")
    if m["runs"]:
        for r in m["runs"]:
            print(f"  run: {r['length']}x {r['cadence']} from sentence "
                  f"{r['at_sentence']} (\u201c...{r['sample']}\u201d)")
    if m["contours"]:
        shape_str = ", ".join(f"{k} {v}" for k, v in
                              sorted(m["contours"].items(), key=lambda kv: -kv[1]))
        print(f"  paragraph contour ({m['paragraphs']} paras): {shape_str}")
    for u in m["uniform_band_paras"][:5]:
        print(f"  uniform band: para {u['paragraph']} all {u['band']} words "
              f"{u['lengths']} — \u201c{u['opening']}...\u201d")
    for s in m.get("suggestions", []):
        print(f"  try: {s}")


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, action="append", default=None,
                    help="book root (chapters at <root>/latex/chapters); "
                         "repeatable (default: this repo)")
    ap.add_argument("--text", type=Path, action="append", default=None,
                    help="analyze a plain-text file instead of the corpus; "
                         "repeatable")
    ap.add_argument("--chapter", help="restrict to files starting with this")
    ap.add_argument("--detail", action="store_true",
                    help="per-chapter cadence breakdown and examples")
    ap.add_argument("--json", action="store_true",
                    help="machine-readable JSON lines")
    ap.add_argument("--seed", type=int, default=None,
                    help="seed for ontology suggestion sampling")
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero if any chapter has warnings")
    args = ap.parse_args()

    roots = args.root or [REPO_ROOT]
    inputs: list[tuple[str, str, bool]] = []
    if args.text:
        for p in args.text:
            inputs.append((p.name, p.read_text(encoding="utf-8"), False))
    else:
        files: list[Path] = []
        for root in roots:
            files += discover(root)
        if args.chapter:
            files = [f for f in files if f.name.startswith(args.chapter)]
        if not files:
            raise SystemExit(f"rhythm_audit: no .tex files under {roots}")
        inputs = [(f.name, f.read_text(encoding="utf-8"), True) for f in files]

    from nupunkt import PunktSentenceTokenizer
    tok = PunktSentenceTokenizer()

    targets = load_targets(roots[0])
    branch = load_ontology_branch(ONTOLOGY_BRANCH)
    cache: dict[str, str] = {}

    rows, all_warns = [], []
    for name, source, is_latex in inputs:
        m = analyze(name, source, is_latex, tok, cache)
        if m is None:
            continue
        m["warnings"] = warnings_for(m, targets)
        m["suggestions"] = rhythm_suggestions(
            branch, m["cadence_counts"], args.seed)
        rows.append(m)
        all_warns += [(m["file"], w) for w in m["warnings"]]

    if not rows:
        print("rhythm_audit: nothing long enough to analyze (need 5+ sentences)")
        return

    if args.json:
        for m in rows:
            print(json.dumps(m))
    else:
        print_table(rows)
        if args.detail:
            for m in rows:
                print_detail(m)
        print()
        for fname, w in all_warns:
            print(f"WARN {fname}: {w}")
        if branch is None:
            print(f"note: ontology branch {ONTOLOGY_BRANCH!r} not found — "
                  "no craft suggestions (profile only)")
        print(f"rhythm_audit: {len(rows)} chapter(s), "
              f"{len(all_warns)} warning(s)")

    if args.strict and all_warns:
        sys.exit(1)


if __name__ == "__main__":
    main()
