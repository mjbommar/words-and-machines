#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pydetex>=1.1.1",
#     "nupunkt>=0.6.0",
#     "pyyaml>=6.0",
# ]
# ///
"""Diction and register profile: hedges, boosters, stance, word stock.

The diction sibling of `prose_metrics.py`. That script measures variety;
this one measures *stance and word stock* — how certain the prose sounds,
how close it stands to the reader, and whether it runs on Latinate
abstractions or Germanic verbs. The categories follow Hyland's
metadiscourse model (hedges / boosters / attitude markers / self- and
reader-mention), which is the standard vocabulary for this dimension and
the same one the ontology's `diction_and_register` branch names.

Measured per chapter (or per --text file), all rates per 1000 words:

  hedge     tentative markers: perhaps, arguably, seems, may, roughly...
  boost     certainty markers: clearly, undoubtedly, of course, in fact...
  attn      attitude markers: unfortunately, strikingly, admittedly...
  1st/2nd   self-mention (I, we, our) and reader-mention (you, your)
  latin     Latinate share of content words. Heuristic: Latinate
            suffixes (-tion -ity -ize -ous -ment -ance -ive -ate...) or
            three-plus syllables count Latinate; monosyllables and
            Germanic affixes (-ness -hood -ship -ful -less, un- be-
            fore- over- under-) count Germanic. It is a proxy for the
            Anglo-Saxon/Latinate register axis, not an etymology.
  nomin     nominalizations (-tion -ment -ness -ance -ity -ism nouns) —
            the "buried verb" rate
  contr     contractions (n't, 'll, 're, 've, it's, that's...) — the
            single loudest formality signal in English prose

Advisory bands (defaults tuned for general nonfiction; a genre profile's
```style-targets``` block may override each with the key shown):

  hedge_per_1000_max           18.0
  booster_per_1000_max          9.0
  attitude_per_1000_max        10.0
  nominalization_per_1000_max  30.0
  latinate_ratio_max            0.45
  contraction_per_1000_min      0.0   (0 disables; raise it for informal
                                       registers that must sound spoken)

A verse or academic profile should move these: raise `latinate_ratio_max`
for a formal register, raise `contraction_per_1000_min` for a chatty one.

If the ontology's `diction_and_register` branch is present and its records
carry `cues` lists, those cues are merged into the built-in lexicons at
runtime (matched by what the record says it is — hedge / booster /
attitude — never by category name), deduplicated. Without the branch the
built-in lists are used unchanged.

Usage:
    uv run scripts/register_report.py                  # per-chapter table
    uv run scripts/register_report.py --chapter ch02
    uv run scripts/register_report.py --text draft.txt
    uv run scripts/register_report.py --detail         # top items + examples
    uv run scripts/register_report.py --json
    uv run scripts/register_report.py --strict         # WARNs become failures

Advisory: exits 0 unless --strict.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import random
import re
import sys
from contextlib import redirect_stdout
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

REPO_ROOT = SCRIPTS_DIR.parent
CHAPTER_SUBDIR = ("chapters",)
ONTOLOGY_BRANCH = "diction_and_register"

DROP_ENVS = (
    "tikzpicture", "figure", "table", "tabular", "tabularx", "lstlisting",
    "verbatim", "Verbatim", "equation", "align", "alignat", "gather",
    "definitionbox", "tryitbox", "examplebox", "codelisting", "promptcode",
    "outputcode", "timeline", "timelinetitled",
)

WORD_RE = re.compile(r"[a-z][a-z'\u2019-]*[a-z]|[a-z]")

DEFAULTS = {
    "hedge_per_1000_max": 18.0,
    "booster_per_1000_max": 9.0,
    "attitude_per_1000_max": 10.0,
    "nominalization_per_1000_max": 30.0,
    "latinate_ratio_max": 0.45,
    "contraction_per_1000_min": 0.0,
}

# ------------------------------------------------------------- lexicons
# Curated after Hyland's metadiscourse lists; kept deliberately small and
# unambiguous. WORDS blobs are whitespace-separated single tokens;
# PHRASES lists are matched as multi-word phrases (whitespace-flexible).

HEDGE_WORDS = """
perhaps maybe arguably seems seem seemed seeming appears appear appeared
suggests suggest suggested indicates indicate indicated may might could
possibly probably presumably apparently ostensibly allegedly reportedly
conceivably plausibly likely unlikely roughly approximately somewhat
relatively fairly rather generally typically usually often sometimes
occasionally tends tend tended assume assumed presume supposed
essentially broadly loosely nearly almost virtually practically partly
largely mostly potentially reputedly seemingly arguable
"""
HEDGE_PHRASES = [
    "in some sense", "to some extent", "more or less", "kind of", "sort of",
    "in most cases", "by and large", "on the whole", "in principle",
    "in a sense", "at least in part", "it is possible that",
    "one might argue", "we might say", "if anything", "my sense is",
    "i think", "i believe", "it seems that", "there is some evidence",
]

BOOSTER_WORDS = """
clearly obviously undoubtedly certainly definitely indeed surely plainly
unquestionably undeniably absolutely entirely completely utterly totally
extremely highly vastly enormously tremendously dramatically profoundly
radically fundamentally decisively precisely exactly truly really
incredibly remarkably strikingly crucially critically massively hugely
invariably inevitably categorically demonstrably evidently always never
overwhelmingly emphatically manifestly patently
"""
BOOSTER_PHRASES = [
    "of course", "in fact", "no doubt", "without doubt", "needless to say",
    "it is clear that", "everyone knows", "beyond question",
    "there is no question", "the fact is", "quite simply",
    "self-evident",
]

ATTITUDE_WORDS = """
unfortunately fortunately surprisingly curiously oddly sadly happily
hopefully regrettably thankfully admittedly frankly honestly
interestingly importantly notably tellingly disappointingly alarmingly
refreshingly amusingly ironically predictably understandably rightly
wrongly absurdly shockingly worryingly mercifully usefully helpfully
astonishingly bizarrely sensibly prudently wisely foolishly appallingly
depressingly gratifyingly preferably unhappily
"""
ATTITUDE_PHRASES = [
    "it is worth noting", "the striking thing is", "to my dismay",
    "sad to say", "to its credit",
]

FIRST_PERSON = {"i", "me", "my", "mine", "myself", "we", "us", "our",
                "ours", "ourselves"}
SECOND_PERSON = {"you", "your", "yours", "yourself", "yourselves"}

LATINATE_SUFFIXES = (
    "ation", "ition", "ution", "tion", "sion", "ity", "ize", "ise", "ous",
    "ment", "ance", "ence", "ative", "itive", "ive", "ical", "ial", "ual",
    "ate", "ify", "able", "ible", "ory", "ary", "ism", "ist", "ure",
    "esque", "escent", "ferous", "fication",
)
GERMANIC_SUFFIXES = ("ness", "hood", "ship", "dom", "ful", "less", "like",
                     "ward", "wards", "some", "th")
GERMANIC_PREFIXES = ("un", "be", "fore", "over", "under", "out", "with",
                     "up", "off", "mis")
NOMINAL_SUFFIXES = ("tion", "sion", "ment", "ness", "ance", "ence", "ity",
                    "ism")
NOMINAL_FALSE_FRIENDS = {
    "moment", "cement", "element", "fragment", "garment", "ornament",
    "parliament", "monument", "instrument", "regiment", "sediment",
    "condiment", "compliment", "witness", "harness", "business",
}
CONTRACTION_RE = re.compile(
    r"\b\w+n[\u2019']t\b|\b\w+[\u2019'](?:ll|re|ve|d|m)\b|"
    r"\b(?:it|that|there|here|what|who|let|he|she|one|"
    r"someone|nothing|everything)[\u2019']s\b",
    re.IGNORECASE,
)
VOWEL_GROUP_RE = re.compile(r"[aeiouy]+")

# Function/grammar words excluded from the Latinate/Germanic ratio.
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "nor", "for", "yet", "so", "as",
    "at", "by", "in", "of", "off", "on", "out", "up", "to", "with", "from",
    "into", "onto", "over", "than", "that", "then", "though", "if", "is",
    "am", "are", "was", "were", "be", "been", "being", "do", "does", "did",
    "done", "has", "have", "had", "can", "could", "may", "might", "must",
    "shall", "should", "will", "would", "he", "she", "it", "we", "they",
    "you", "i", "me", "him", "her", "us", "them", "my", "your", "his",
    "its", "our", "their", "this", "these", "those", "who", "whom",
    "whose", "which", "what", "when", "where", "while", "not", "no",
    "there", "here", "some", "any", "all", "each", "such", "own", "one",
    "per", "via", "upon", "about", "after", "before", "between", "through",
    "under", "until", "since", "unless", "because", "however", "also",
    "very", "just", "only", "more", "most", "other", "same", "both",
}


def build_lexicons() -> dict[str, tuple[set[str], list[str]]]:
    """Single words and phrases per category, made mutually disjoint so the
    three rates stay independently interpretable (earlier category wins)."""
    out: dict[str, tuple[set[str], list[str]]] = {}
    seen_words: set[str] = set()
    seen_phrases: set[str] = set()
    for name, blob, phrase_list in (
        ("hedge", HEDGE_WORDS, HEDGE_PHRASES),
        ("booster", BOOSTER_WORDS, BOOSTER_PHRASES),
        ("attitude", ATTITUDE_WORDS, ATTITUDE_PHRASES),
    ):
        words = {w for w in blob.split() if w not in seen_words}
        seen_words |= words
        phrases = [p for p in phrase_list if p not in seen_phrases]
        seen_phrases |= set(phrases)
        out[name] = (words, phrases)
    return out


LEXICONS = build_lexicons()


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


CATEGORY_KEYS = {
    "hedge": ("hedge", "hedging", "mitigat", "tentative", "downtone",
              "approximat", "qualifier"),
    "booster": ("booster", "boosting", "intensif", "emphatic", "amplif",
                "certainty marker"),
    "attitude": ("attitude", "attitudinal", "evaluative", "stance marker",
                 "affective"),
}


def merge_ontology_cues(branch, lexicons: dict) -> dict[str, int]:
    """Fold `cues` extras from record entries into the built-in lexicons.

    Which lexicon a record feeds is decided from what the record *says it
    is* (name / aka / tags / definition), never from its category name."""
    merged = dict.fromkeys(lexicons, 0)
    if not branch:
        return merged
    for entries in branch.get("categories", {}).values():
        for e in entries:
            if not isinstance(e, dict):
                continue
            cues = e.get("cues")
            if not isinstance(cues, list) or not cues:
                continue
            blob = " ".join(
                str(e.get(k, "")) for k in ("name", "aka", "definition")
            ).lower()
            tags = e.get("tags")
            if isinstance(tags, list):
                blob += " " + " ".join(str(t) for t in tags).lower()
            for cat, keys in CATEGORY_KEYS.items():
                if not any(k in blob for k in keys):
                    continue
                words, phrases = lexicons[cat]
                for cue in cues:
                    cue = str(cue).strip().lower()
                    if not cue or not re.fullmatch(r"[a-z'\- ]+", cue):
                        continue
                    if " " in cue:
                        if cue not in phrases:
                            phrases.append(cue)
                            merged[cat] += 1
                    elif cue not in words:
                        words.add(cue)
                        merged[cat] += 1
    return merged


# ------------------------------------------------------------------ metrics


def syllables(word: str) -> int:
    w = word.lower()
    n = len(VOWEL_GROUP_RE.findall(w))
    if n > 1 and w.endswith("e") and not w.endswith(("le", "ee", "ye")):
        n -= 1
    return max(1, n)


def word_stock(word: str) -> str | None:
    """'latinate' | 'germanic' | None (function word / too short)."""
    if word in STOPWORDS or len(word) < 3 or "'" in word:
        return None
    if word.endswith(GERMANIC_SUFFIXES) and len(word) >= 5:
        return "germanic"
    if word.startswith(GERMANIC_PREFIXES) and len(word) >= 6 and \
            not word.endswith(LATINATE_SUFFIXES):
        return "germanic"
    if word.endswith(LATINATE_SUFFIXES) and len(word) >= 6:
        return "latinate"
    if syllables(word) >= 3:
        return "latinate"
    return "germanic"


def is_nominalization(word: str) -> bool:
    return (len(word) >= 6 and word.endswith(NOMINAL_SUFFIXES)
            and word not in NOMINAL_FALSE_FRIENDS)


def count_lexicon(words: list[str], text: str, lex: tuple[set[str], list[str]]
                  ) -> dict[str, int]:
    hits: dict[str, int] = {}
    single, phrases = lex
    for w in words:
        if w in single:
            hits[w] = hits.get(w, 0) + 1
    for p in phrases:
        pat = re.compile(r"\b" + re.escape(p).replace(r"\ ", r"\s+") + r"\b")
        n = len(pat.findall(text))
        if n:
            hits[p] = hits.get(p, 0) + n
            # phrases whose head word is also a single-word marker were
            # already counted once; subtract that overlap
            head = p.split()[0]
            if head in single and head in hits:
                hits[head] = max(0, hits[head] - n)
                if hits[head] == 0:
                    del hits[head]
    return hits


def example_for(term: str, sents: list[str]) -> str:
    pat = re.compile(r"\b" + re.escape(term).replace(r"\ ", r"\s+") + r"\b",
                     re.IGNORECASE)
    for s in sents:
        if pat.search(s):
            s = re.sub(r"\s+", " ", s).strip()
            return s if len(s) <= 110 else s[:107] + "..."
    return ""


def analyze(name: str, source: str, is_latex: bool, tok, lexicons: dict,
            rng: random.Random, min_words: int) -> dict | None:
    prose = strip_latex(source) if is_latex else source
    prose = re.sub(r"\s+", " ", prose).strip()
    lower = prose.lower()
    words = WORD_RE.findall(lower)
    if len(words) < min_words:
        return None
    n = len(words)
    per_k = lambda c: round(1000 * c / n, 1)  # noqa: E731

    sents = [s for s in tok.tokenize(prose) if len(s.split()) >= 3]
    sents_copy = list(sents)  # seeded order so quoted examples are stable
    rng.shuffle(sents_copy)

    hits = {cat: count_lexicon(words, lower, lexicons[cat])
            for cat in lexicons}
    counts = {cat: sum(h.values()) for cat, h in hits.items()}

    first = sum(1 for w in words if w in FIRST_PERSON)
    second = sum(1 for w in words if w in SECOND_PERSON)

    lat = ger = 0
    for w in words:
        stock = word_stock(w)
        if stock == "latinate":
            lat += 1
        elif stock == "germanic":
            ger += 1
    ratio = lat / (lat + ger) if (lat + ger) else 0.0

    nominal = [w for w in words if is_nominalization(w)]
    contractions = CONTRACTION_RE.findall(prose)

    top = {}
    for cat, h in hits.items():
        ranked = sorted(h.items(), key=lambda kv: (-kv[1], kv[0]))[:6]
        top[cat] = [
            {"term": t, "n": c, "example": example_for(t, sents_copy)}
            for t, c in ranked
        ]

    return {
        "file": name,
        "words": n,
        "hedge": counts["hedge"],
        "hedge_per_1000": per_k(counts["hedge"]),
        "booster": counts["booster"],
        "booster_per_1000": per_k(counts["booster"]),
        "attitude": counts["attitude"],
        "attitude_per_1000": per_k(counts["attitude"]),
        "first_person_per_1000": per_k(first),
        "second_person_per_1000": per_k(second),
        "latinate": lat,
        "germanic": ger,
        "latinate_ratio": round(ratio, 3),
        "nominalization_per_1000": per_k(len(nominal)),
        "contraction_per_1000": per_k(len(contractions)),
        "top_terms": top,
    }


def warnings_for(m: dict, t: dict[str, float]) -> list[str]:
    w = []
    if m["hedge_per_1000"] > t["hedge_per_1000_max"]:
        w.append(f"hedges {m['hedge_per_1000']}/1k > "
                 f"{t['hedge_per_1000_max']:g} — the prose keeps apologizing "
                 "for its own claims")
    if m["booster_per_1000"] > t["booster_per_1000_max"]:
        w.append(f"boosters {m['booster_per_1000']}/1k > "
                 f"{t['booster_per_1000_max']:g} — asserted certainty is "
                 "doing work the evidence should do")
    if m["attitude_per_1000"] > t["attitude_per_1000_max"]:
        w.append(f"attitude markers {m['attitude_per_1000']}/1k > "
                 f"{t['attitude_per_1000_max']:g} — the narrator is telling "
                 "the reader how to feel")
    if m["nominalization_per_1000"] > t["nominalization_per_1000_max"]:
        w.append(f"nominalizations {m['nominalization_per_1000']}/1k > "
                 f"{t['nominalization_per_1000_max']:g} — verbs buried in "
                 "-tion/-ment nouns")
    if m["latinate_ratio"] > t["latinate_ratio_max"]:
        w.append(f"Latinate share {m['latinate_ratio']} > "
                 f"{t['latinate_ratio_max']:g} — abstract word stock; swap "
                 "some for short Germanic verbs")
    if t["contraction_per_1000_min"] > 0 and \
            m["contraction_per_1000"] < t["contraction_per_1000_min"]:
        w.append(f"contractions {m['contraction_per_1000']}/1k < "
                 f"{t['contraction_per_1000_min']:g} — register reads more "
                 "formal than the profile asks for")
    return w


def notes_for(m: dict) -> list[str]:
    notes = []
    h, b = m["hedge"], m["booster"]
    if h + b >= 8:
        if b > 1.5 * max(h, 1):
            notes.append("stance skews assertive (boosters outnumber hedges "
                         f"{b}:{h})")
        elif h > 2 * max(b, 1):
            notes.append("stance skews tentative (hedges outnumber boosters "
                         f"{h}:{b})")
    if m["second_person_per_1000"] > 20:
        notes.append(f"heavy reader address ({m['second_person_per_1000']}/1k "
                     "second person)")
    if m["first_person_per_1000"] < 0.5 and m["second_person_per_1000"] < 0.5:
        notes.append("no self- or reader-mention: fully impersonal register")
    return notes


# -------------------------------------------------------------------- output


def print_table(rows: list[dict]) -> None:
    hdr = (f"{'chapter':32s} {'words':>6s} {'hedge':>6s} {'boost':>6s} "
           f"{'attn':>5s} {'1st':>5s} {'2nd':>5s} {'latin':>6s} "
           f"{'nomin':>6s} {'contr':>6s}")
    print(hdr)
    print("-" * len(hdr))
    for m in rows:
        flag = " !" if m["warnings"] else ""
        print(f"{m['file']:32s} {m['words']:6d} {m['hedge_per_1000']:6.1f} "
              f"{m['booster_per_1000']:6.1f} {m['attitude_per_1000']:5.1f} "
              f"{m['first_person_per_1000']:5.1f} "
              f"{m['second_person_per_1000']:5.1f} {m['latinate_ratio']:6.3f} "
              f"{m['nominalization_per_1000']:6.1f} "
              f"{m['contraction_per_1000']:6.1f}{flag}")
    print("(rates per 1000 words; latin = Latinate share of content words)")


def print_detail(m: dict) -> None:
    print(f"\n{m['file']} — {m['words']} words")
    for cat in ("hedge", "booster", "attitude"):
        items = m["top_terms"].get(cat) or []
        if not items:
            continue
        listing = ", ".join(f"{i['term']} x{i['n']}" for i in items)
        print(f"  {cat}: {listing}")
        ex = next((i for i in items if i["example"]), None)
        if ex:
            print(f"    \u201c{ex['example']}\u201d")
    print(f"  word stock: {m['latinate']} Latinate / {m['germanic']} Germanic "
          f"= {m['latinate_ratio']}")
    for note in m.get("notes", []):
        print(f"  note: {note}")


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, action="append", default=None,
                    help="book root (chapters at <root>/latex/chapters); "
                         "repeatable (default: this repo)")
    ap.add_argument("--text", type=Path, action="append", default=None,
                    help="analyze a plain-text file instead of the corpus")
    ap.add_argument("--chapter", help="restrict to files starting with this")
    ap.add_argument("--detail", action="store_true",
                    help="top markers per category with an example line")
    ap.add_argument("--json", action="store_true", help="JSON lines")
    ap.add_argument("--seed", type=int, default=None,
                    help="seed for example-sentence sampling")
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
            raise SystemExit(f"register_report: no .tex files under {roots}")
        inputs = [(f.name, f.read_text(encoding="utf-8"), True) for f in files]

    from nupunkt import PunktSentenceTokenizer
    tok = PunktSentenceTokenizer()

    targets = load_targets(roots[0])
    branch = load_ontology_branch(ONTOLOGY_BRANCH)
    lexicons = {k: (set(v[0]), list(v[1])) for k, v in LEXICONS.items()}
    merged = merge_ontology_cues(branch, lexicons)

    rng = random.Random(args.seed)
    # rates are noisy on short samples; chapters must be substantial, but a
    # --text passage the writer hands over deliberately gets analyzed anyway
    min_words = 40 if args.text else 150
    rows, all_warns = [], []
    for name, source, is_latex in inputs:
        m = analyze(name, source, is_latex, tok, lexicons, rng, min_words)
        if m is None:
            print(f"note: {name} skipped (< {min_words} words)",
                  file=sys.stderr)
            continue
        m["warnings"] = warnings_for(m, targets)
        m["notes"] = notes_for(m)
        rows.append(m)
        all_warns += [(m["file"], w) for w in m["warnings"]]

    if not rows:
        print(f"register_report: nothing long enough to analyze "
              f"(need {min_words}+ words)")
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
        if not args.detail:
            for m in rows:
                for note in m["notes"]:
                    print(f"note {m['file']}: {note}")
        if branch is None:
            print(f"note: ontology branch {ONTOLOGY_BRANCH!r} not found — "
                  "built-in lexicons only")
        elif sum(merged.values()):
            print("note: merged ontology cues — " + ", ".join(
                f"{k} +{v}" for k, v in merged.items() if v))
        print(f"register_report: {len(rows)} chapter(s), "
              f"{len(all_warns)} warning(s)")

    if args.strict and all_warns:
        sys.exit(1)


if __name__ == "__main__":
    main()
