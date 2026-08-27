#!/usr/bin/env python3
"""Build the Simplified Book English dictionary from corpora + policy.

Produces scripts/data/simplified_english/lexicon.json — the artifact that
`scripts/check_simplified.py` reads and `docs/guides/SIMPLIFIED-ENGLISH.md`
documents. The word tiers come from corpus frequency and OpenGloss
morphology; the policy (what to ban, what to swap it for, what a frequency
list must never bless) is hand-written in curated.yaml next to it.

Seven prose corpora, because one register cannot define ordinary English —
and a book's English is not any single one of them:

  gutenberg   manu/project_gutenberg          book English, largely pre-1930
  books       lucadiliello/bookcorpusopen     modern published books
  fineweb     HuggingFaceFW/fineweb-edu       modern educational web prose
  web         HuggingFaceFW/fineweb           modern general web prose
  news        cnn_dailymail                   modern journalistic prose
  simplewiki  wikimedia/wikipedia 20231101.simple  plain English by design
  explain     sentence-transformers/eli5      lay explanation (ELI5)
  billsum     FiscalNote/billsum (fed + CA)   the register to avoid

Only aggregate counts are stored — never text. The cache holds a word and
a number, which is what makes this a statistical measurement of English
rather than a copy of anyone's corpus.

plus OpenGloss (mjbommar/opengloss-v1.3-dictionary, CC-BY 4.0) for direct
dictionary recognition, inflections, and a Wikipedia frequency rank.

Tiers:

  core    common in any modern register (>= 10/M), or common in book
          English and still current (gutenberg >= 10/M and modern >= 1/M);
          attested >= 1/M in two of the seven prose corpora, or ranked in
          Wikipedia's top 30,000; expanded with the OpenGloss inflections
          that are themselves attested. Free to use, never reported.
  open    any other real English word attested at >= 0.5/M in a prose
          corpus. Allowed; counted, not reported.
  known   an OpenGloss headword below the corpus threshold. It is a real
          dictionary entry, not proof that a general reader knows its use.
  (rest)  unlisted — not found in the corpus tiers or OpenGloss. It may be a
          domain term, a coined form, a name, or a mistake.

Why so many: measured on these caches, swapping the single "modern prose"
corpus changes about half the core list, and an educational-web corpus
alone treats `whispered`, `shrugged`, `doorway` and `sofa` as unusual
words. Breadth is the fix for that, not a different threshold.

The register statistics (lift over prose, and document spread across bills)
are reported for context only. They rank candidates for human review; they
did not decide any grade, and they should not. See the guide, "How the
substitution list was graded".

Usage:
    uv run --group sbe-build scripts/build_simplified_lexicon.py
    uv run --group sbe-build scripts/build_simplified_lexicon.py --refresh
    uv run --group sbe-build scripts/build_simplified_lexicon.py --report
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "scripts" / "data" / "simplified_english"
CURATED = DATA / "curated.yaml"
OUT = DATA / "lexicon.json"
STYLE_MD = ROOT / "docs" / "guides" / "STYLE.md"

CACHE = Path.home() / ".cache" / "book-template" / "sbe"
OPENGLOSS_CACHE = Path.home() / ".cache" / "opengloss"
OPENGLOSS_DATASET = "mjbommar/opengloss-v1.3-dictionary"

PROSE_WORD = re.compile(r"[a-z][a-z'-]*")   # prose: keep contractions
BILL_WORD = re.compile(r"[a-z]+")           # bills: drop drafting punctuation

# Corpus sampling. Enough tokens that a 1-per-million threshold rests on
# ~15 observations; small enough to re-stream in minutes.
CORPORA = {
    "gutenberg": {
        "dataset": "manu/project_gutenberg", "split": "en", "field": "text",
        "revision": "164853d214065df26a630ee1ab91a0c39e461caf",
        "docs": 2500, "strip_gutenberg_boilerplate": True, "kind": "prose",
        "register": "book English, largely pre-1930",
    },
    "fineweb": {
        "dataset": "HuggingFaceFW/fineweb-edu", "config": "sample-10BT",
        "revision": "87f09149ef4734204d70ed1d046ddc9ca3f2b8f9",
        "split": "train", "field": "text", "docs": 20000, "kind": "prose",
        "register": "modern educational web prose",
    },
    "news": {
        "dataset": "cnn_dailymail", "config": "1.0.0", "split": "train",
        "revision": "96df5e686bee6baa90b8bee7c28b81fa3fa6223d",
        "field": "article", "docs": 25557, "kind": "prose",
        "register": "modern journalistic prose",
    },
    "books": {
        "dataset": "lucadiliello/bookcorpusopen", "split": "train",
        "revision": "edb74e6c88abb38f0a0fc993a7068ab00a32db45",
        "field": "text", "tokens": 20_000_000, "kind": "prose",
        "register": "modern published books (narrative)",
    },
    "web": {
        "dataset": "HuggingFaceFW/fineweb", "config": "sample-10BT",
        "revision": "9bb295ddab0e05d785b879661af7260fed5140fc",
        "split": "train", "field": "text", "tokens": 15_000_000,
        "kind": "prose",
        "register": "modern general web prose (unfiltered)",
    },
    "simplewiki": {
        "dataset": "wikimedia/wikipedia", "config": "20231101.simple",
        "revision": "b04c8d1ceb2f5cd4588862100d08de323dccfbaa",
        "split": "train", "field": "text", "tokens": 12_000_000,
        "kind": "prose",
        "register": "Simple English Wikipedia — plain English by construction",
    },
    "explain": {
        "dataset": "sentence-transformers/eli5", "config": "pair",
        "revision": "6e3b20a7a427560845779f217c3ff71493374bc0",
        "split": "train", "field": "answer", "tokens": 12_000_000,
        "kind": "prose",
        "register": "plain explanation written for a lay reader (ELI5)",
    },
    "billsum": {
        "dataset": "FiscalNote/billsum", "split": "train", "field": "text",
        "revision": "3d8510441c06a3d9dfb32eb0d7f80151730bcc4f",
        "docs": 8000, "kind": "bills",
        "register": "US federal legislative text",
    },
    "billsum-ca": {
        "dataset": "FiscalNote/billsum", "split": "ca_test", "field": "text",
        "revision": "3d8510441c06a3d9dfb32eb0d7f80151730bcc4f",
        "docs": 1237, "kind": "bills",     # the entire ca_test split
        "register": "California legislative text (replication set)",
    },
}
PROSE = ("gutenberg", "books", "fineweb", "web", "news",
         "simplewiki", "explain")
# Everything except the historical corpus: "is this word current?"
MODERN = ("books", "fineweb", "web", "news", "simplewiki", "explain")

# Tier thresholds, per million tokens. Chosen, not discovered: coverage is
# smooth in the threshold (about -3.6 points per doubling), so no value here
# is a cliff. See the guide's sensitivity table.
CORE_MODERN_MIN = 10.0     # common in at least one modern register
CORE_BOOK_MIN = 10.0       # ...or common in book English
CORE_STILL_CURRENT = 1.0   #    and still in use today
CORE_ATTEST_MIN = 1.0      # attested this often in >= 2 prose corpora
CORE_ATTEST_CORPORA = 2
CORE_WIKI_RANK_MAX = 30000  # ...or in the modern reference dictionary
CORE_REAL_WORD_MIN = 50.0  # this common => a real word, dictionary or not
INFLECTION_MIN = 0.5       # an inflected form must itself be attested
OPEN_MIN = 0.5

PG_START = re.compile(r"\*\*\* ?START OF (?:THIS|THE) PROJECT GUTENBERG.*?\*\*\*",
                      re.DOTALL)
PG_END = re.compile(r"\*\*\* ?END OF (?:THIS|THE) PROJECT GUTENBERG", re.DOTALL)


# ------------------------------------------------------------------ corpora

def marker_pattern(markers: list[str]) -> re.Pattern:
    """The combined marker matcher used by both corpus measurement and SBE."""
    parts = [re.escape(m).replace(r"\ ", r"\s+")
             for m in sorted(set(markers), key=len, reverse=True)]
    return re.compile(rf"\b(?:{'|'.join(parts)})\b", re.IGNORECASE)


def measurement_markers(curated: dict) -> list[str]:
    """Default policy entries, marker-only terms, and statutory markers."""
    marker_only = {str(marker).lower()
                   for marker in curated.get("marker_only") or []}
    markers = [str(entry["from"]).lower()
               for key in ("substitutions", "phrase_substitutions")
               for entry in curated.get(key) or []
               if (entry.get("grade") in ("error", "warn")
                   or str(entry["from"]).lower() in marker_only)]
    markers += ["shall", "thereto", "hereunder", "said party",
                "provided that", "deemed", "aforementioned"]
    return list(dict.fromkeys(markers))


def stream_counts(name: str, spec: dict, markers: list[str]) -> dict:
    """Token counts for one corpus, cached under ~/.cache/book-template/sbe."""
    from datasets import load_dataset

    kwargs = {"split": spec["split"], "streaming": True,
              "revision": spec["revision"]}
    if spec.get("config"):
        kwargs["name"] = spec["config"]
    ds = load_dataset(spec["dataset"], **kwargs)
    word_re = BILL_WORD if spec["kind"] == "bills" else PROSE_WORD

    counts: Counter[str] = Counter()
    doc_freq: Counter[str] = Counter()
    marker_counts: Counter[str] = Counter()
    marker_doc_freq: Counter[str] = Counter()
    marker_re = marker_pattern(markers)
    tokens = docs = 0
    for row in ds:
        text = row[spec["field"]]
        if spec.get("strip_gutenberg_boilerplate"):
            if (m := PG_START.search(text)):
                text = text[m.end():]
            if (m := PG_END.search(text)):
                text = text[:m.start()]
        words = word_re.findall(text.lower())
        counts.update(words)
        doc_freq.update(set(words))
        doc_markers = [re.sub(r"\s+", " ", m.group(0).lower())
                       for m in marker_re.finditer(text)]
        marker_counts.update(doc_markers)
        marker_doc_freq.update(set(doc_markers))
        tokens += len(words)
        docs += 1
        if docs % 500 == 0:
            print(f"  {name}: {docs} docs, {tokens / 1e6:.1f}M tokens",
                  file=sys.stderr)
        if tokens >= spec.get("tokens", 10**18) or docs >= spec.get("docs",
                                                                   10**18):
            break
    return {"corpus": name, "dataset": spec["dataset"],
            "dataset_revision": spec["revision"], "docs": docs,
            "tokens": tokens, "counts": dict(counts.most_common(120000)),
            "df": dict(doc_freq.most_common(120000)),
            "marker_counts": dict(marker_counts.most_common()),
            "marker_df": dict(marker_doc_freq.most_common()),
            "marker_total": sum(marker_counts.values()),
            "marker_set_sha256_16": hashlib.sha256(
                "\n".join(markers).encode()).hexdigest()[:16]}


def corpus_counts(name: str, refresh: bool, markers: list[str]) -> dict:
    """The cached counts for one corpus, checked against the spec.

    A cache built to a different budget than the code now asks for is the
    quiet way a dictionary changes underneath its own provenance, so say so.
    """
    path = CACHE / f"counts-{name}.json"
    if path.exists() and not refresh:
        data = json.loads(path.read_text())
        spec = CORPORA[name]
        marker_hash = hashlib.sha256(
            "\n".join(markers).encode()).hexdigest()[:16]
        if (data.get("dataset_revision") != spec["revision"]
                or data.get("marker_set_sha256_16") != marker_hash):
            sys.exit(f"build_simplified_lexicon: cache {path.name} predates "
                     "the pinned-revision/exact-marker measurement. Rebuild "
                     "it with --refresh")
        want = spec.get("tokens") or spec.get("docs")
        got = data["tokens"] if "tokens" in spec else data["docs"]
        unit = "tokens" if "tokens" in spec else "docs"
        if want and abs(got - want) > max(want * 0.02, 1000):
            print(f"build_simplified_lexicon: WARNING cache {path.name} holds "
                  f"{got} {unit}, spec asks for {want} — the committed "
                  f"lexicon may not be reproducible from this code",
                  file=sys.stderr)
        return data
    print(f"streaming {name} (one-time; cached at {path})", file=sys.stderr)
    data = stream_counts(name, CORPORA[name], markers)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))
    return data


def per_million(data: dict) -> dict[str, float]:
    t = data["tokens"]
    return {w: c / t * 1e6 for w, c in data["counts"].items()}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


# --------------------------------------------------------------- opengloss

def opengloss() -> tuple[dict[str, list[str]], dict[str, int], set[str]]:
    """Inflections/ranks for words, plus exact multiword headwords.

    Reads the slim cache `scripts/vocab_variety.py` builds; if it is absent,
    says so rather than duplicating that script's fetch.
    """
    import polars as pl

    path = OPENGLOSS_CACHE / f"{OPENGLOSS_DATASET.split('/')[-1]}-slim2.parquet"
    if not path.exists():
        sys.exit(
            f"build_simplified_lexicon: no OpenGloss cache at {path}.\n"
            "Build it once with:  uv run scripts/vocab_variety.py --refresh\n"
            "(~5 minutes, ~120 MB, shared by every book from this template.)")
    df = pl.read_parquet(
        path, columns=["word", "wiki_frequency_rank", "all_inflections"])
    phrases = {
        " ".join(str(word).casefold().split())
        for word in df.filter(pl.col("word").str.contains(" "))["word"].to_list()
    }
    df = df.filter(~pl.col("word").str.contains(" "))
    words = df["word"].to_list()
    words = [str(w).casefold() for w in words]
    infl = {
        w: [str(x).casefold() for x in (lst or []) if x and " " not in x]
        for w, lst in zip(words, df["all_inflections"].to_list(), strict=True)
    }
    rank = {w: r for w, r in zip(words, df["wiki_frequency_rank"].to_list(),
                                 strict=True) if r is not None}
    return infl, rank, phrases


# ------------------------------------------------------------------- tiers

def build_tiers(rates: dict[str, dict[str, float]], infl: dict,
                rank: dict) -> tuple[set[str], set[str]]:
    prose = [rates[c] for c in PROSE if c in rates]
    modern_rates = [rates[c] for c in MODERN if c in rates]
    g = rates["gutenberg"]
    known = set(infl)
    inflected = {x for lst in infl.values() for x in lst}
    vocab = set().union(*(set(d) for d in prose))

    def attested(w: str) -> int:
        return sum(1 for d in prose if d.get(w, 0.0) >= CORE_ATTEST_MIN)

    def anywhere(w: str) -> float:
        return max((d.get(w, 0.0) for d in prose), default=0.0)

    core: set[str] = set()
    for w in vocab:
        modern = max((d.get(w, 0.0) for d in modern_rates), default=0.0)
        common_now = modern >= CORE_MODERN_MIN
        common_in_books = (g.get(w, 0.0) >= CORE_BOOK_MIN
                           and modern >= CORE_STILL_CURRENT)
        if not (common_now or common_in_books):
            continue
        if not (attested(w) >= CORE_ATTEST_CORPORA
                or rank.get(w, 10**9) <= CORE_WIKI_RANK_MAX):
            continue
        if w in known or w in inflected or modern >= CORE_REAL_WORD_MIN:
            core.add(w)
    # Word families — but only inflected forms the corpora have actually
    # seen. Unfiltered expansion invents words ("accompannies", "aboves").
    for w in list(core):
        for x in infl.get(w, ()):
            if anywhere(x) >= INFLECTION_MIN:
                core.add(x)

    open_tier: set[str] = set()
    for w in vocab:
        if w in core or not (w in known or w in inflected):
            continue                       # corpus noise, OCR, proper names
        if anywhere(w) >= OPEN_MIN:
            open_tier.add(w)
            open_tier.update(x for x in infl.get(w, ())
                             if anywhere(x) >= INFLECTION_MIN)
    open_tier -= core

    contractions = {stem + "n't" for stem in (
        "is", "are", "was", "were", "do", "does", "did", "have", "has", "had",
        "would", "should", "could", "will", "can", "must", "need", "ought",
        "might")}
    for pron in ("i", "you", "he", "she", "it", "we", "they", "that", "there",
                 "who", "what", "here", "this"):
        contractions |= {pron + s for s in ("'s", "'re", "'ve", "'ll", "'d")}
    core |= contractions
    open_tier -= core
    return core, open_tier


# ------------------------------------------------------------------ policy

def style_banned() -> set[str]:
    """Words/phrases STYLE.md already fails on, so SBE does not repeat them."""
    if not STYLE_MD.exists():
        return set()
    text = STYLE_MD.read_text()
    out: set[str] = set()
    for tag in ("banned-words", "banned-phrases"):
        if (m := re.search(rf"```{tag}\n(.*?)```", text, re.DOTALL)):
            out |= {ln.strip().lower() for ln in m.group(1).splitlines()
                    if ln.strip() and not ln.strip().startswith("#")}
    return out


def register_stats(word: str, fed: dict, ca: dict,
                   rates: dict[str, dict[str, float]], *, phrases: bool = False) -> dict:
    """Descriptive register statistics. Advisory: they grade nothing.

    lift        rate in legislative text over rate in prose, Jeffreys-
                smoothed and taken as the geometric mean of the federal and
                California estimates, so a word has to behave the same way
                in two legislatures to score high.
    doc_spread  share of federal bills that use the word at all. Real
                boilerplate is everywhere; a topic word is bursty.
    """
    count_key = "marker_counts" if phrases else "counts"
    spread_key = "marker_df" if phrases else "df"

    def smoothed(counts: dict, tokens: int) -> float:
        return (counts.get(word, 0) + 0.5) / (tokens + 1) * 1e6

    prose = sum((rates[c].get(word, 0.0) for c in PROSE), 0.0) / len(PROSE)
    prose = max(prose, (0.5 / 200e6) * 1e6)      # Jeffreys floor, stated
    lift_fed = smoothed(fed[count_key], fed["tokens"]) / prose
    lift_ca = smoothed(ca[count_key], ca["tokens"]) / prose
    return {
        "register_lift": round((lift_fed * lift_ca) ** 0.5, 1),
        "doc_spread": round(fed[spread_key].get(word, 0) / fed["docs"], 3),
    }


def annotate(entries: list[dict], fed: dict, ca: dict, rates: dict,
             already: set[str], *, phrase_entries: bool = False
             ) -> tuple[list[dict], list[str]]:
    """Attach the register statistics; drop what STYLE.md already bans."""
    kept, dropped = [], []
    for e in entries:
        src = e["from"].lower()
        if src in already:
            dropped.append(src)
            continue
        entry = {k: v for k, v in e.items() if k != "index"}
        entry.update(register_stats(src, fed, ca, rates,
                                    phrases=phrase_entries))
        kept.append(entry)
    return kept, dropped


def validate_curated(curated: dict) -> None:
    """Fail before an expensive build when the hand-written policy is invalid."""
    valid_grades = {"error", "warn", "idea"}
    for key in ("substitutions", "phrase_substitutions"):
        seen: set[str] = set()
        for i, entry in enumerate(curated.get(key) or [], start=1):
            if not isinstance(entry, dict) or not entry.get("from"):
                sys.exit(f"build_simplified_lexicon: {key}[{i}] needs a "
                         "non-empty `from` value")
            source = str(entry["from"]).casefold()
            if source in seen:
                sys.exit(f"build_simplified_lexicon: duplicate {key} entry: "
                         f"{entry['from']!r}")
            seen.add(source)
            if entry.get("grade") not in valid_grades:
                sys.exit(f"build_simplified_lexicon: {key} entry "
                         f"{entry['from']!r} has invalid grade "
                         f"{entry.get('grade')!r}")
    marker_only = [str(marker).casefold()
                   for marker in curated.get("marker_only") or []]
    if len(marker_only) != len(set(marker_only)):
        sys.exit("build_simplified_lexicon: duplicate marker_only entry")
    known = {
        str(entry["from"]).casefold()
        for key in ("substitutions", "phrase_substitutions")
        for entry in curated.get(key) or []
        if isinstance(entry, dict) and entry.get("from")
    }
    if unknown := sorted(set(marker_only) - known):
        sys.exit("build_simplified_lexicon: marker_only entries must also be "
                 "substitutions: " + ", ".join(unknown))


# -------------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--refresh", action="store_true",
                    help="re-stream the reference corpora (slow)")
    ap.add_argument("--report", action="store_true",
                    help="print tier sizes and sanity checks; write nothing")
    args = ap.parse_args()

    curated = yaml.safe_load(CURATED.read_text())
    validate_curated(curated)
    markers = measurement_markers(curated)
    counts = {n: corpus_counts(n, args.refresh, markers) for n in CORPORA}
    rates = {n: per_million(counts[n]) for n in CORPORA}
    marker_rates = {
        n: {marker: count / counts[n]["tokens"] * 1e6
            for marker, count in counts[n]["marker_counts"].items()}
        for n in CORPORA
    }
    combined_rates = {
        n: rates[n] | marker_rates[n]
        for n in CORPORA
    }

    infl, rank, opengloss_phrases = opengloss()
    core, open_tier = build_tiers(rates, infl, rank)
    core |= {w.lower() for w in curated.get("always_core") or []}

    # A frequency list will happily bless words no book should use without
    # marking them. Demote them to unlisted so a first use has to be a
    # deliberate authorial act, not a default.
    # No inflection expansion here: it would sweep in innocent forms
    # ("colours" from "coloured"). List the forms that matter explicitly.
    sensitive = {w.lower() for w in curated.get("never_core") or []}
    core -= sensitive
    open_tier -= sensitive
    open_tier -= core
    # OpenGloss membership answers a different question from corpus
    # frequency. Keep the remaining headwords so the checker can distinguish
    # a recognized but uncommon word from a form absent from the dictionary.
    # Recognition is not automatic admission: both classes remain candidates
    # for a first-use explanation when the usage is technical or restricted.
    recognized = set(infl) - core - open_tier - sensitive

    already = style_banned()
    subs, dropped = annotate(curated.get("substitutions") or [],
                             counts["billsum"], counts["billsum-ca"],
                             combined_rates,
                             already)
    phrases, dropped_p = annotate(curated.get("phrase_substitutions") or [],
                                  counts["billsum"], counts["billsum-ca"],
                                  combined_rates, already,
                                  phrase_entries=True)

    if args.report:
        print(f"core {len(core)}  open {len(open_tier)}  "
              f"sensitive {len(sensitive)}")
        for w in ("of", "the", "software", "whispered", "doorway", "yeah",
                  "gigawatt", "promulgate", "accompannies", "don't"):
            tier = ("core" if w in core else
                    "open" if w in open_tier else "-")
            print(f"  {w:<14} {tier}")
        for corpus in CORPORA:
            cov = sum(v for k, v in counts[corpus]["counts"].items()
                      if k in core) / counts[corpus]["tokens"] * 100
            print(f"  coverage {corpus:<11} {cov:5.2f}%")
        return

    payload = {
        "standard": curated["meta"]["standard"],
        "abbrev": curated["meta"]["abbrev"],
        "version": curated["meta"]["version"],
        "built": date.today().isoformat(),
        "built_by": "scripts/build_simplified_lexicon.py",
        "based_on": curated["meta"]["based_on"],
        "provenance": {
            "corpora": [
                {"name": n, "dataset": CORPORA[n]["dataset"],
                 "revision": CORPORA[n]["revision"],
                 "register": CORPORA[n]["register"],
                 "docs": counts[n]["docs"], "tokens": counts[n]["tokens"],
                 "marker_rate_per_1k": round(
                     counts[n]["marker_total"] / counts[n]["tokens"] * 1000,
                     3),
                 "cache_sha256_16": digest(CACHE / f"counts-{n}.json")}
                for n in CORPORA
            ],
            "dictionary": {
                "dataset": OPENGLOSS_DATASET, "license": "CC-BY 4.0",
                "used_for": ("direct headword recognition, inflections, and "
                             "Wikipedia frequency rank"),
            },
            "policy_source": "scripts/data/simplified_english/curated.yaml",
            "register_lift": (
                "geometric mean of (federal bill rate / prose rate) and "
                "(California bill rate / prose rate), Jeffreys-smoothed; "
                "prose = mean of all seven prose corpora"),
            "doc_spread": "share of federal bills containing the word",
            "grading": (
                "grades are editorial judgement, seeded from the "
                "plainlanguage.gov list. The register statistics rank "
                "candidates for review; they do not decide grades."),
            "caveat": (
                "Corpus samples are the first N documents or tokens of the "
                "revision-pinned streaming datasets above; cache digests "
                "identify the exact aggregate counts this build used."),
        },
        "tier_rules": {
            "core": (f"(any modern corpus >= {CORE_MODERN_MIN}/M) or "
                     f"(gutenberg >= {CORE_BOOK_MIN}/M and modern >= "
                     f"{CORE_STILL_CURRENT}/M); attested >= "
                     f"{CORE_ATTEST_MIN}/M in {CORE_ATTEST_CORPORA} of "
                     f"{len(PROSE)} "
                     f"prose corpora or wiki rank <= {CORE_WIKI_RANK_MAX}; "
                     f"plus attested inflections"),
            "open": (f"known to OpenGloss and >= {OPEN_MIN}/M in a prose "
                     "corpus"),
            "recognized": ("OpenGloss headword below the corpus thresholds; "
                           "review technical or restricted uses"),
            "recognized_phrase": ("exact multiword OpenGloss headword; "
                                  "available to --explain, not an approval"),
            "unlisted": ("not in the corpus tiers or OpenGloss; review as a "
                         "domain term, coined form, name, or possible error"),
            "sensitive": ("curated never_core list, demoted out of both "
                          "tiers so a first use is deliberate"),
        },
        "thresholds": curated["thresholds"],
        "abbreviation_exempt": sorted(curated.get("abbreviation_exempt") or []),
        # Canonical input for both corpus measurement and book scoring. This
        # intentionally retains entries whose finding is owned by STYLE.md;
        # deduplicating diagnostics must not change a comparison metric.
        "register_markers": markers,
        "marker_only": sorted(str(marker).lower()
                              for marker in curated.get("marker_only") or []),
        "substitutions": subs,
        "phrase_substitutions": phrases,
        "sensitive": sorted(sensitive),
        "deduplicated_against_style_md": sorted(dropped + dropped_p),
        "counts": {"core": len(core), "open": len(open_tier),
                   "recognized": len(recognized),
                   "sensitive": len(sensitive), "substitutions": len(subs),
                   "phrase_substitutions": len(phrases)},
        "core": sorted(core),
        "open": sorted(open_tier),
        "recognized": sorted(recognized),
        # Exact lookup support for `--explain "force majeure"`. These entries
        # are not inserted into the unigram tier counts and are not approval
        # evidence; OpenGloss contains both terms of art and ordinary phrases.
        "opengloss_phrases": sorted(opengloss_phrases),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(core)} core, "
          f"{len(open_tier)} open, {len(recognized)} recognized, "
          f"{len(sensitive)} sensitive, {len(subs)} "
          f"word + {len(phrases)} phrase substitutions, "
          f"{len(dropped) + len(dropped_p)} dropped as already banned by "
          f"STYLE.md ({OUT.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
