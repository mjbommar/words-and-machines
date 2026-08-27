#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pydetex>=1.1.1",
#     "nupunkt>=0.6.0",
#     "pyyaml>=6.0",
# ]
# ///
"""Per-chapter valence and tension curve, optionally vs. a target arc shape.

Slices each chapter into 10-20 equal-weight windows and scores every
window twice:

  valence   lexicon sentiment, -1 (dark) .. +1 (bright). A compact
            curated positive/negative word list lives in this file —
            the approach is the one AFINN (Nielsen 2011) and VADER
            (Hutto & Gilbert 2014) popularized, reimplemented small and
            dependency-free rather than vendored, with simple negation
            flipping (a negator within three tokens inverts polarity).
  tension   0 .. 1 proxy built from negation density, question density,
            and a conflict-word list — the "something is at stake here"
            signal that valence alone misses (a calm disaster and a
            cheerful fight both read flat on valence).

Both are printed as sparklines plus numbers, so a chapter's shape is
visible at a glance: does it fall, rise, sag in the middle, or sit flat?
Flat is the finding worth acting on — a chapter with no movement in
either row is a chapter with no arc.

With the ontology's `arc_shapes` branch present, a named shape's `curve`
extra becomes a target:

    uv run scripts/arc_profiler.py --list-targets
    uv run scripts/arc_profiler.py --target "man in a hole"

Measured and target curves are resampled onto a common x grid (21
points, positions normalized to 0..1) and compared by Pearson
correlation, mean absolute deviation, and the position where they
diverge most — the place to look first when a chapter is not doing the
shape it was outlined for. Without the branch the script profiles only
and says so.

Read the correlation first: lexicon valence rarely reaches the rails a
hand-drawn target curve uses, so the deviation numbers carry an
amplitude penalty the correlation does not.

Caveats worth keeping in mind: lexicon valence is coarse on ironic,
technical, or dialogue-heavy prose; the tension proxy counts markers,
not stakes. Read the curve as a prompt to reread the flagged window,
never as a verdict.

Usage:
    uv run scripts/arc_profiler.py                     # all chapters
    uv run scripts/arc_profiler.py --chapter ch02 --windows 16
    uv run scripts/arc_profiler.py --text draft.txt
    uv run scripts/arc_profiler.py --target "tragedy" --strict
    uv run scripts/arc_profiler.py --json

Advisory: exits 0 unless --strict.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import math
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
ONTOLOGY_BRANCH = "arc_shapes"

DROP_ENVS = (
    "tikzpicture", "figure", "table", "tabular", "tabularx", "lstlisting",
    "verbatim", "Verbatim", "equation", "align", "alignat", "gather",
    "definitionbox", "tryitbox", "examplebox", "codelisting", "promptcode",
    "outputcode", "timeline", "timelinetitled",
)

WORD_RE = re.compile(r"[a-z][a-z'\u2019-]*[a-z]|[a-z]")
SPARK = "\u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588"
GRID = 21  # resample points for target comparison
VALENCE_SHRINKAGE = 4.0  # additive smoothing on (pos-neg)/(pos+neg)
SMOOTH_KERNEL = (0.25, 0.5, 0.25)  # 3-point taper over the window series

DEFAULTS = {
    "valence_range_min": 0.25,   # peak-to-trough movement expected
    "tension_range_min": 0.15,
    "arc_correlation_min": 0.30,  # only applies with --target
}

POSITIVE = """
abundant admire advance affection agree amazing applause appreciate approve
assure beautiful benefit best better bless bloom bold bonus boost brave
breakthrough bright brilliant calm capable care celebrate charm cheer clarity
clear clever comfort commend compassion competent confidence confident content
cooperate courage cure dear dedicated delight deserve devoted dignity diligent
eager earnest ease easy efficient elegant encourage endorse energy enjoy
enthusiasm excel excellent excited exquisite fair faith fascinating favor
festive fine flourish fond forgive fortune free freedom fresh friend friendly
fulfil fun gain generous gentle genuine gift glad glory good grace graceful
gracious grateful gratitude great growth happy harmony heal health help honest
honor hope humane humor ideal improve innovative inspire integrity intelligent
invaluable inviting joy just keen kind kindness laugh liberty light lively
love lovely loyal lucky marvelous meaningful merit mercy noble nurture
open opportunity optimism patient peace perfect playful pleasant pleased
pleasure plenty polished popular positive praise precious pride productive
progress promise prosper proud prudent quick quiet radiant reassure recover
relief reliable remedy rescue resilient resolve respect restore reward rich
right robust safe satisfaction satisfy save secure sensible serene sincere
skilled smile smooth solid soothing sparkle splendid stable steady strength
strong sturdy succeed success sunny superb support sure surge sustain sweet
tender thankful thrive thrilling tidy tranquil treasure triumph tranquility
trust truth uplifting useful valiant valuable vibrant victory vigor virtue
vital vivid warm warmth wealth welcome well whole wholesome willing win
wisdom wise wonder wonderful worth worthy zeal
"""

NEGATIVE = """
afraid alarm anger angry angst anxious attack awful bad betray bitter blame
bleak blunder breach broken burden chaos cheat collapse complain confuse
corrupt crisis cruel crush curse damage damn danger dangerous dark dead death
decay decline defeat defect deficient degrade delay demolish deny depress
deprive desperate despair destroy deteriorate difficult diminish dirty
disappoint disaster discourage disgust dismay disorder dispute disrupt
distort distress disturb doom doubt drain dread dreary dull dying embarrass
empty enemy erode error evil exhaust fail failure fake false fatal fault fear
fierce fight flaw fool forbid fragile frantic fraud fright frustrate gloom
grief grim guilt harass hard harm harsh hate hazard heavy helpless hinder
hollow hopeless hostile humiliate hurt ignore ill illness impair impossible
inadequate inept inferior inflame injury injustice insecure insult
intolerable irritate isolate jealous lack lag lapse lie loathe lonely loss
lost mad malice menace miserable mistake mock murder neglect nervous
nightmare noise nonsense obscure obstacle offend oppress outrage overwhelm
pain panic paralyze pathetic penalty peril perish plague poison pointless
poor precarious prejudice pressure problem protest punish quarrel reckless
refuse regret reject relentless reluctant repress resent restless ridicule
risk rot rude ruin sabotage sad savage scandal scarce scare scream setback
severe shame shatter shock shrink sick sin sinister slow slump sorrow sting
strain stress struggle stubborn stupid suffer suspect suspicion tense terror
threat threaten tired torment tough toxic tragedy trap trouble turmoil ugly
unable uncertain uneasy unfair unhappy unrest unstable useless vain vanish
victim vicious violate violence volatile vulnerable war wary waste weak weary
weep wither worn worry worse worst wound wreck wrong
"""

CONFLICT = """
although argue attack battle betray blame breach challenge clash collide
combat compete conflict confront contest contradict controversy counter
crisis critic criticize deadline debate defend defy deny despite dilemma
disagree dispute dissent doubt enemy fight friction hostile impasse
insist litigate object objection oppose opponent pressure protest push
rebut refuse resist retaliate rival showdown stake stakes stalemate
standoff strike struggle sue tension threat threaten trap ultimatum
versus warn warning
"""

NEGATORS = {
    "not", "no", "never", "none", "nothing", "nobody", "nowhere", "neither",
    "nor", "cannot", "without", "hardly", "scarcely", "barely", "lack",
    "lacks", "lacked", "fails", "fail", "failed", "refuse", "refuses",
    "cant", "dont", "didnt", "wont", "isnt", "wasnt", "arent", "werent",
    "doesnt", "couldnt", "wouldnt", "shouldnt", "hasnt", "havent", "aint",
}
NEG_SUFFIX_RE = re.compile(r"n[\u2019']t$")
SUFFIXES = ("s", "es", "ed", "d", "ing", "ly", "er", "est", "ness", "ful")


def build_set(blob: str) -> set[str]:
    return {w for w in blob.split() if w}


POSITIVE_SET = build_set(POSITIVE)
NEGATIVE_SET = build_set(NEGATIVE)
CONFLICT_SET = build_set(CONFLICT)


def lex_lookup(word: str, lexicon: set[str]) -> bool:
    """Exact match, then a cheap suffix strip for inflected forms."""
    if word in lexicon:
        return True
    for suf in SUFFIXES:
        if word.endswith(suf) and len(word) - len(suf) >= 3:
            stem = word[: -len(suf)]
            if stem in lexicon:
                return True
            if suf in ("ed", "ing", "es") and stem + "e" in lexicon:
                return True
            if len(stem) > 3 and stem[-1] == stem[-2] and stem[:-1] in lexicon:
                return True
    return False


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


def discover(root: Path) -> list[Path]:
    files: list[Path] = []
    for name in CHAPTER_SUBDIR:
        d = root / "latex" / name
        if d.is_dir():
            files += sorted(d.glob("*.tex"))
    if not files and root.is_dir():
        files += sorted(root.glob("*.tex"))
    return files


def load_targets(root: Path) -> dict[str, float]:
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


def shapes_with_curves(branch) -> list[dict]:
    """Every record in the branch that carries a usable `curve` extra."""
    out = []
    if not branch:
        return out
    for entries in branch.get("categories", {}).values():
        for e in entries:
            if not isinstance(e, dict):
                continue
            curve = e.get("curve")
            if not isinstance(curve, list) or len(curve) < 2:
                continue
            pts = []
            for p in curve:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    try:
                        pts.append((float(p[0]), float(p[1])))
                    except (TypeError, ValueError):
                        continue
            if len(pts) >= 2:
                out.append({"name": str(e.get("name", "")),
                            "aka": e.get("aka"),
                            "definition": str(e.get("definition", "")),
                            "points": sorted(pts)})
    return out


def find_shape(shapes: list[dict], name: str) -> dict | None:
    want = name.strip().lower()
    for s in shapes:
        if s["name"].strip().lower() == want:
            return s
    for s in shapes:
        aka = s.get("aka")
        akas = aka if isinstance(aka, list) else ([aka] if aka else [])
        if any(str(a).strip().lower() == want for a in akas):
            return s
    for s in shapes:
        if want in s["name"].strip().lower():
            return s
    return None


# ------------------------------------------------------------------ scoring


def windows_of(sents: list[str], n_windows: int) -> list[list[str]]:
    """Contiguous windows of roughly equal word count."""
    lens = [len(s.split()) for s in sents]
    total = sum(lens)
    if total == 0 or n_windows < 1:
        return []
    per = total / n_windows
    out: list[list[str]] = []
    cur: list[str] = []
    acc = 0
    for s, ln in zip(sents, lens, strict=True):
        cur.append(s)
        acc += ln
        if acc >= per * (len(out) + 1) and len(out) < n_windows - 1:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    while len(out) < n_windows and any(len(w) > 1 for w in out):
        # split the widest window so the grid stays the requested size
        i = max(range(len(out)), key=lambda k: len(out[k]))
        w = out.pop(i)
        half = max(1, len(w) // 2)
        out[i:i] = [w[:half], w[half:]]
    return out


def score_window(text: str) -> dict:
    lower = text.lower()
    words = WORD_RE.findall(lower)
    n = len(words) or 1
    pos = neg = 0
    for i, w in enumerate(words):
        polarity = 0
        if lex_lookup(w, POSITIVE_SET):
            polarity = 1
        elif lex_lookup(w, NEGATIVE_SET):
            polarity = -1
        if polarity == 0:
            continue
        window = words[max(0, i - 3):i]
        if any(t in NEGATORS or NEG_SUFFIX_RE.search(t) for t in window):
            polarity = -polarity
        if polarity > 0:
            pos += 1
        else:
            neg += 1
    # additive shrinkage: a window with one lexicon hit must not read as a
    # full-scale +1. k=4 keeps sparse windows near zero and lets dense ones
    # approach the rails.
    valence = (pos - neg) / (pos + neg + VALENCE_SHRINKAGE)

    negations = sum(1 for w in words
                    if w in NEGATORS or NEG_SUFFIX_RE.search(w))
    questions = text.count("?")
    conflict = sum(1 for w in words if lex_lookup(w, CONFLICT_SET))
    raw = 100 * (negations + conflict + 2 * questions) / n
    tension = min(1.0, raw / 8.0)  # 8 markers per 100 words saturates
    return {
        "words": len(words),
        "valence": round(valence, 3),
        "pos": pos,
        "neg": neg,
        "tension": round(tension, 3),
        "tension_raw": round(raw, 2),
        "conflict": conflict,
        "negations": negations,
        "questions": questions,
    }


def smooth(values: list[float]) -> list[float]:
    """3-point taper; edges reflect. Window scores are noisy on their own —
    the shape lives in the trend, not in a single window."""
    if len(values) < 3:
        return list(values)
    a, b, c = SMOOTH_KERNEL
    out = []
    for i, v in enumerate(values):
        prev = values[i - 1] if i > 0 else v
        nxt = values[i + 1] if i < len(values) - 1 else v
        out.append(a * prev + b * v + c * nxt)
    return out


def sparkline(values: list[float], lo: float, hi: float) -> str:
    if hi <= lo:
        return SPARK[len(SPARK) // 2] * len(values)
    out = []
    for v in values:
        frac = (v - lo) / (hi - lo)
        idx = int(round(frac * (len(SPARK) - 1)))
        out.append(SPARK[max(0, min(len(SPARK) - 1, idx))])
    return "".join(out)


# --------------------------------------------------------------- comparison


def resample(points: list[tuple[float, float]], grid: int = GRID) -> list[float]:
    """Linear interpolation onto `grid` evenly spaced x in [0, 1]."""
    xs = [p[0] for p in points]
    lo, hi = min(xs), max(xs)
    span = (hi - lo) or 1.0
    norm = sorted(((x - lo) / span, y) for x, y in points)
    out = []
    for i in range(grid):
        x = i / (grid - 1)
        if x <= norm[0][0]:
            out.append(norm[0][1])
            continue
        if x >= norm[-1][0]:
            out.append(norm[-1][1])
            continue
        for (x0, y0), (x1, y1) in zip(norm, norm[1:], strict=False):
            if x0 <= x <= x1:
                t = (x - x0) / (x1 - x0) if x1 > x0 else 0.0
                out.append(y0 + t * (y1 - y0))
                break
    return out


def pearson(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or len(a) < 3:
        return 0.0
    ma, mb = statistics.mean(a), statistics.mean(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b, strict=True))
    da = math.sqrt(sum((x - ma) ** 2 for x in a))
    db = math.sqrt(sum((y - mb) ** 2 for y in b))
    if da == 0 or db == 0:
        return 0.0
    return num / (da * db)


def scale_unit(values: list[float]) -> list[float]:
    """Scale into [-1, 1] without shifting the zero point, so a curve given
    on a 0..100 or 0..10 scale compares against measured valence."""
    peak = max(abs(v) for v in values) or 1.0
    if peak <= 1.0:
        return list(values)
    return [v / peak for v in values]


def compare_to_shape(valences: list[float], shape: dict) -> dict:
    measured = resample([(i / max(1, len(valences) - 1), v)
                         for i, v in enumerate(valences)])
    target = scale_unit(resample(shape["points"]))
    measured_s = scale_unit(measured)
    devs = [abs(m - t) for m, t in zip(measured_s, target, strict=True)]
    worst = max(range(len(devs)), key=lambda i: devs[i])
    return {
        "target": shape["name"],
        "correlation": round(pearson(measured_s, target), 3),
        "mean_abs_dev": round(statistics.mean(devs), 3),
        "max_dev": round(devs[worst], 3),
        "max_dev_position": round(worst / (len(devs) - 1), 2),
        "target_curve": [round(v, 3) for v in target],
        "measured_curve": [round(v, 3) for v in measured_s],
    }


# ------------------------------------------------------------------ analyze


def analyze(name: str, source: str, is_latex: bool, tok, n_windows: int,
            min_words: int, rng: random.Random) -> dict | None:
    prose = strip_latex(source) if is_latex else source
    prose = re.sub(r"[ \t]+", " ", prose).strip()
    words = WORD_RE.findall(prose.lower())
    if len(words) < min_words:
        return None
    sents = [s.strip() for s in tok.tokenize(prose) if len(s.split()) >= 3]
    if len(sents) < n_windows:
        n_windows = max(3, len(sents))
    wins = windows_of(sents, n_windows)
    if not wins:
        return None

    scored = []
    for i, w in enumerate(wins):
        text = " ".join(w)
        s = score_window(text)
        s["window"] = i + 1
        s["position"] = round(i / max(1, len(wins) - 1), 2)
        s["opening"] = " ".join(text.split()[:10])
        scored.append(s)

    raw_vals = [s["valence"] for s in scored]
    raw_tens = [s["tension"] for s in scored]
    vals = [round(v, 3) for v in smooth(raw_vals)]
    tens = [round(v, 3) for v in smooth(raw_tens)]
    for s, v, t in zip(scored, vals, tens, strict=True):
        s["valence_smoothed"] = v
        s["tension_smoothed"] = t
    peak = max(range(len(vals)), key=lambda i: vals[i])
    trough = min(range(len(vals)), key=lambda i: vals[i])
    hot = max(range(len(tens)), key=lambda i: tens[i])
    # seeded jitter only breaks ties between identical windows
    if vals.count(vals[peak]) > 1:
        peak = rng.choice([i for i, v in enumerate(vals) if v == vals[peak]])
    if tens.count(tens[hot]) > 1:
        hot = rng.choice([i for i, t in enumerate(tens) if t == tens[hot]])

    return {
        "file": name,
        "words": len(words),
        "windows": len(wins),
        "valence": vals,
        "tension": tens,
        "valence_unsmoothed": [round(v, 3) for v in raw_vals],
        "tension_unsmoothed": [round(v, 3) for v in raw_tens],
        "valence_mean": round(statistics.mean(vals), 3),
        "valence_range": round(max(vals) - min(vals), 3),
        "tension_mean": round(statistics.mean(tens), 3),
        "tension_range": round(max(tens) - min(tens), 3),
        "slope": round(
            (statistics.mean(vals[len(vals) // 2:])
             - statistics.mean(vals[:max(1, len(vals) // 2)])), 3),
        "peak": scored[peak],
        "trough": scored[trough],
        "hottest": scored[hot],
        "detail": scored,
    }


def warnings_for(m: dict, t: dict[str, float]) -> list[str]:
    w = []
    if m["valence_range"] < t["valence_range_min"]:
        w.append(f"valence range {m['valence_range']} < "
                 f"{t['valence_range_min']:g} — the chapter's emotional line "
                 "never moves")
    if m["tension_range"] < t["tension_range_min"]:
        w.append(f"tension range {m['tension_range']} < "
                 f"{t['tension_range_min']:g} — nothing tightens or releases")
    cmp_ = m.get("comparison")
    if cmp_ and cmp_["correlation"] < t["arc_correlation_min"]:
        w.append(f"correlation {cmp_['correlation']} with "
                 f"\u201c{cmp_['target']}\u201d < {t['arc_correlation_min']:g} "
                 f"— biggest divergence at position "
                 f"{cmp_['max_dev_position']}")
    return w


# -------------------------------------------------------------------- output


def print_chapter(m: dict) -> None:
    print(f"\n{m['file']} — {m['words']} words, {m['windows']} windows")
    print(f"  valence {sparkline(m['valence'], -1.0, 1.0)}  "
          f"mean {m['valence_mean']:+.2f} range {m['valence_range']:.2f} "
          f"drift {m['slope']:+.2f}")
    print(f"  tension {sparkline(m['tension'], 0.0, 1.0)}  "
          f"mean {m['tension_mean']:.2f} range {m['tension_range']:.2f}")
    print("  values  " + " ".join(f"{v:+.2f}" for v in m["valence"]))
    for label, key in (("peak", "peak"), ("trough", "trough"),
                       ("tightest", "hottest")):
        s = m[key]
        metric = (f"valence {s['valence_smoothed']:+.2f}" if key != "hottest"
                  else f"tension {s['tension_smoothed']:.2f}")
        print(f"  {label:8s} w{s['window']:<2d} ({s['position']:.2f}) "
              f"{metric}  \u201c{s['opening']}...\u201d")
    cmp_ = m.get("comparison")
    if cmp_:
        print(f"  vs \u201c{cmp_['target']}\u201d: r={cmp_['correlation']:+.2f} "
              f"mad={cmp_['mean_abs_dev']:.2f} "
              f"max dev {cmp_['max_dev']:.2f} at position "
              f"{cmp_['max_dev_position']}")
        print("    target  " + sparkline(cmp_["target_curve"], -1.0, 1.0))
        print("    chapter " + sparkline(cmp_["measured_curve"], -1.0, 1.0))


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, action="append", default=None,
                    help="book root (chapters at <root>/latex/chapters); "
                         "repeatable (default: this repo)")
    ap.add_argument("--text", type=Path, action="append", default=None,
                    help="analyze a plain-text file instead of the corpus")
    ap.add_argument("--chapter", help="restrict to files starting with this")
    ap.add_argument("--windows", type=int, default=12,
                    help="windows per chapter, 10-20 (default 12)")
    ap.add_argument("--target", help="ontology arc-shape name to compare against")
    ap.add_argument("--list-targets", action="store_true",
                    help="list arc shapes that carry a curve")
    ap.add_argument("--json", action="store_true", help="JSON lines")
    ap.add_argument("--seed", type=int, default=None,
                    help="seed for tie-breaking window picks")
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero if any chapter has warnings")
    args = ap.parse_args()

    branch = load_ontology_branch(ONTOLOGY_BRANCH)
    shapes = shapes_with_curves(branch)

    if args.list_targets:
        if not shapes:
            print(f"arc_profiler: no arc shapes with curves "
                  f"(ontology branch {ONTOLOGY_BRANCH!r} missing or "
                  "curve-free) — comparison unavailable")
            return
        width = max(len(s["name"]) for s in shapes)
        for s in shapes:
            print(f"{s['name']:<{width}}  [{len(s['points'])} pts]  "
                  f"{s['definition']}")
        print(f"arc_profiler: {len(shapes)} target shape(s)")
        return

    n_windows = max(10, min(20, args.windows))
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
            raise SystemExit(f"arc_profiler: no .tex files under {roots}")
        inputs = [(f.name, f.read_text(encoding="utf-8"), True) for f in files]

    shape = None
    if args.target:
        shape = find_shape(shapes, args.target)
        if shape is None:
            names = ", ".join(s["name"] for s in shapes) or "(none available)"
            print(f"arc_profiler: no arc shape named {args.target!r}; "
                  f"have: {names}", file=sys.stderr)

    from nupunkt import PunktSentenceTokenizer
    tok = PunktSentenceTokenizer()

    targets = load_targets(roots[0])
    rng = random.Random(args.seed)
    min_words = 60 if args.text else 200

    rows, all_warns = [], []
    for name, source, is_latex in inputs:
        m = analyze(name, source, is_latex, tok, n_windows, min_words, rng)
        if m is None:
            print(f"note: {name} skipped (< {min_words} words)",
                  file=sys.stderr)
            continue
        if shape:
            m["comparison"] = compare_to_shape(m["valence"], shape)
        m["warnings"] = warnings_for(m, targets)
        rows.append(m)
        all_warns += [(m["file"], w) for w in m["warnings"]]

    if not rows:
        print(f"arc_profiler: nothing long enough to analyze "
              f"(need {min_words}+ words)")
        return

    if args.json:
        for m in rows:
            print(json.dumps(m))
    else:
        for m in rows:
            print_chapter(m)
        print()
        for fname, w in all_warns:
            print(f"WARN {fname}: {w}")
        if branch is None:
            print(f"note: ontology branch {ONTOLOGY_BRANCH!r} not found — "
                  "profile only, no target comparison")
        print(f"arc_profiler: {len(rows)} chapter(s), "
              f"{len(all_warns)} warning(s)")

    if args.strict and all_warns:
        sys.exit(1)


if __name__ == "__main__":
    main()
