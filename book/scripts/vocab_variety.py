#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pydetex>=1.1.1",
#     "nupunkt>=0.6.0",
#     "polars>=1.0",
#     "pyarrow>=15",
#     "huggingface_hub>=0.23",
# ]
# ///
"""Vocabulary-variety ideation from the OpenGloss knowledge graph.

AI-assisted drafts converge on a flat vocabulary distribution — the same
content words ("crucial", "landscape", "framework") recur far above their
base rate in English. This tool measures that against OpenGloss
(https://arxiv.org/abs/2511.18622): each manuscript word's frequency is
compared to its Wikipedia-derived expectation, and the graph's synonyms /
antonyms / hypernyms / hyponyms / collocations are shown to ideate more
varied phrasing. Relation words are annotated with THEIR book counts, so
"fresh picks" separates synonyms you haven't touched from ones you've
also worn out.

Advisory only — never a CI gate. Data: mjbommar/opengloss-v1.3-dictionary
(CC-BY 4.0), fetched once via column projection (~14 of 39 columns) into
~/.cache/opengloss/, shared across books built from this template.

Usage:
    uv run scripts/vocab_variety.py                     # heaviest repeated words
    uv run scripts/vocab_variety.py --sort ratio --band mid --pos adj,adv,verb
                                        # sharpest style-word overuse
    uv run scripts/vocab_variety.py --word crucial ...  # explicit lookup
    uv run scripts/vocab_variety.py --word "net negative"   # phrase headwords too
    uv run scripts/vocab_variety.py --random 5          # sample from prose
    uv run scripts/vocab_variety.py --random 5 --band any   # no frequency bias
    uv run scripts/vocab_variety.py --sentence 3        # random sentences,
                                        # every word in each looked up
    uv run scripts/vocab_variety.py --ngrams            # stock collocations
    uv run scripts/vocab_variety.py --chapter ch03      # restrict corpus
    uv run scripts/vocab_variety.py --root ../other-book
    uv run scripts/vocab_variety.py --format jsonl      # machine-readable
    uv run scripts/vocab_variety.py --refresh           # re-fetch dataset
    uv run scripts/vocab_variety.py --word W --senses   # per-sense view
    uv run scripts/vocab_variety.py --suggest-bans      # style-profile ban
                                        # candidates (adj/adv/verb by default)
    uv run scripts/vocab_variety.py --max-register 8    # cap pick reading level
    uv run --with sentence-transformers scripts/vocab_variety.py \
        --word W --embed                # OGBert context re-rank (GPU auto)

Cache v2 (~120 MB, ~/.cache/opengloss/): adds per-sense definitions and
relations (sense examples trimmed) plus 2 usage examples per headword, so
fresh picks come with a real example sentence and a ✓ when the pick
collocates with the target's actual neighbours in the book.

Known limits (fine for ideation): plural headwords ("numbers") split counts
with their base ("number"); multi-POS words can't be disambiguated without
tagging; the Wikipedia baseline makes topic terms top the mass view — that
is honest, use --pos/--sort ratio to hunt style words instead; --embed
ranking is experimental (definition-vs-context similarity).
"""

from __future__ import annotations

import argparse
import io
import json
import random
import re
import sys
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from pathlib import Path

DATASET = "mjbommar/opengloss-v1.3-dictionary"
CACHE = Path.home() / ".cache" / "opengloss"
SLIM_COLS = [
    "word", "reading_level", "is_stopword", "parts_of_speech", "total_senses",
    "all_definitions", "all_synonyms", "all_antonyms", "all_hypernyms",
    "all_hyponyms", "all_collocations", "all_inflections",
    "wiki_frequency", "wiki_frequency_rank", "senses", "all_examples",
]

# same layout + non-prose envs as check_prose.py, so both tools see one corpus
SUBDIRS = ("chapters", "frontmatter", "front-matter", "backmatter", "back-matter")
DROP_ENVS = (
    "tikzpicture", "figure", "table", "tabular", "tabularx", "lstlisting",
    "verbatim", "Verbatim", "equation", "align", "alignat", "gather",
    "definitionbox", "tryitbox", "examplebox", "codelisting", "promptcode",
    "outputcode",
)

WORD_RE = re.compile(r"[a-z][a-z'-]*[a-z]|[a-z]")


# ---------------------------------------------------------------- data layer

def cache_path(dataset: str) -> Path:
    return CACHE / f"{dataset.split('/')[-1]}-slim2.parquet"


def fetch_slim(dataset: str, out: Path) -> None:
    """One-time build of the slim cache: read only SLIM_COLS from the HF
    auto-converted parquet shards (full shards total ~3.2 GB; the slim
    projection is ~10x smaller and ~5 minutes on a home connection)."""
    from concurrent.futures import ThreadPoolExecutor

    import pyarrow as pa
    import pyarrow.parquet as pq
    from huggingface_hub import HfFileSystem

    fs = HfFileSystem()
    pattern = f"datasets/{dataset}@refs%2Fconvert%2Fparquet/default/train/*.parquet"
    shards = sorted(fs.glob(pattern))
    if not shards:
        raise SystemExit(f"vocab_variety: no parquet shards at {pattern} "
                         "(is the dataset name right? are you logged in to HF?)")
    print(f"fetching {len(shards)} shards of {dataset} "
          f"(one-time, ~5 min; cached at {out})", file=sys.stderr)

    def grab(f: str):
        tbl = pq.read_table(f, filesystem=fs, columns=SLIM_COLS, use_threads=True)
        print(f"  {f.split('/')[-1]}: {tbl.num_rows} rows", file=sys.stderr)
        return tbl

    # 2 workers: fast enough, and polite to HF's per-IP rate limits
    with ThreadPoolExecutor(max_workers=2) as ex:
        tables = list(ex.map(grab, shards))
    import polars as pl
    df = pl.from_arrow(pa.concat_tables(tables))
    # trim the heavy tails: 2 usage examples per word; senses without
    # their per-sense example lists
    df = df.with_columns(
        pl.col("all_examples").list.head(2),
        pl.col("senses").list.eval(pl.struct(
            part_of_speech=pl.element().struct.field("part_of_speech"),
            definition=pl.element().struct.field("definition"),
            synonyms=pl.element().struct.field("synonyms"),
            antonyms=pl.element().struct.field("antonyms"),
            hypernyms=pl.element().struct.field("hypernyms"),
            hyponyms=pl.element().struct.field("hyponyms"),
        )),
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(out, compression="zstd")
    print(f"cached {df.height} entries -> {out} "
          f"({out.stat().st_size / 1e6:.0f} MB)", file=sys.stderr)


class Gloss:
    """Slim OpenGloss dictionary with lemma resolution."""

    def __init__(self, dataset: str, refresh: bool = False) -> None:
        import polars as pl
        path = cache_path(dataset)
        if refresh or not path.exists():
            fetch_slim(dataset, path)
        self.df = pl.read_parquet(path)
        words = self.df["word"].to_list()
        self.row_of: dict[str, int] = {w: i for i, w in enumerate(words)}
        # inflection -> headword (first writer wins; exact headwords override)
        self.lemma_of: dict[str, str] = {}
        for w, infl in zip(words, self.df["all_inflections"].to_list(),
                           strict=True):
            for form in infl or []:
                self.lemma_of.setdefault(form.lower(), w)
        for w in words:
            self.lemma_of[w] = w
        self.stop = set(
            self.df.filter(pl.col("is_stopword"))["word"].to_list())
        self.wiki_freq: dict[str, int] = dict(zip(
            words, self.df["wiki_frequency"].fill_null(0).to_list(),
            strict=True))
        self.rank: dict[str, int | None] = dict(zip(
            words, self.df["wiki_frequency_rank"].to_list(), strict=True))
        self.pos: dict[str, list[str]] = dict(zip(
            words, self.df["parts_of_speech"].to_list(), strict=True))
        self.total_wiki = sum(self.wiki_freq.values())

    def lemma(self, token: str) -> str | None:
        t = token.lower()
        if t in self.lemma_of:
            return self.lemma_of[t]
        # light suffix stripping for forms the graph doesn't list
        for suf, reps in (("ies", ("y",)), ("es", ("e", "")), ("s", ("",)),
                          ("ing", ("", "e")), ("ed", ("", "e")), ("ly", ("",))):
            if t.endswith(suf) and len(t) - len(suf) >= 3:
                for rep in reps:
                    cand = t[: len(t) - len(suf)] + rep
                    if cand in self.lemma_of:
                        return self.lemma_of[cand]
        return None

    def entry(self, headword: str) -> dict | None:
        i = self.row_of.get(headword)
        return self.df.row(i, named=True) if i is not None else None

    def example(self, headword: str) -> str | None:
        e = self.entry(headword)
        ex = (e or {}).get("all_examples") or []
        return ex[0] if ex else None

    def register(self, headword: str) -> int | None:
        e = self.entry(headword)
        lvl = (e or {}).get("reading_level")
        return REGISTER_ORDER.get(lvl) if lvl else None


REGISTER_ORDER = {**{"K": 0}, **{str(i): i for i in range(1, 13)},
                  "BS": 13, "PhD": 14}


# -------------------------------------------------------------- corpus layer

def strip_latex(text: str) -> str:
    """LaTeX -> plain prose (same recipe as check_prose.py)."""
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
    return re.sub(r"\s+", " ", cleaned).strip()


def discover(root: Path, chapter: str | None) -> list[Path]:
    files: list[Path] = []
    for name in SUBDIRS:
        d = root / "latex" / name
        if d.exists():
            files += sorted(d.glob("*.tex"))
    if chapter:
        files = [f for f in files if f.name.startswith(chapter)]
    return files


class Corpus:
    """Token/lemma frequencies for the manuscript."""

    def __init__(self, files: list[Path], gloss: Gloss) -> None:
        self.token_counts: Counter[str] = Counter()
        self.lemma_counts: Counter[str] = Counter()
        self.lemma_files: dict[str, Counter[str]] = defaultdict(Counter)
        self.bigrams: Counter[tuple[str, str]] = Counter()
        self.trigrams: Counter[tuple[str, str, str]] = Counter()
        self.sentences: list[tuple[str, str]] = []  # (file, sentence)
        self.total_tokens = 0
        for f in files:
            prose = strip_latex(f.read_text())
            toks = WORD_RE.findall(prose.lower())
            self.total_tokens += len(toks)
            self.token_counts.update(toks)
            for a, b in zip(toks, toks[1:], strict=False):
                self.bigrams[(a, b)] += 1
            for a, b, c in zip(toks, toks[1:], toks[2:], strict=False):
                self.trigrams[(a, b, c)] += 1
            for t in toks:
                lem = gloss.lemma(t)
                if lem:
                    self.lemma_counts[lem] += 1
                    self.lemma_files[lem][f.name] += 1
            for s in re.split(r"(?<=[.!?])\s+", prose):
                if len(s.split()) >= 6:
                    self.sentences.append((f.name, s))

    def count(self, headword: str) -> int:
        """Book occurrences of a headword — or of a 2-3 word phrase."""
        parts = headword.split()
        if len(parts) == 2:
            return self.bigrams.get(tuple(parts), 0)
        if len(parts) == 3:
            return self.trigrams.get(tuple(parts), 0)
        return self.lemma_counts.get(headword, 0)


# ------------------------------------------------------------ target pickers

BANDS = {"common": (1, 2000), "mid": (2001, 20000), "rare": (20001, 10**9),
         "any": (1, 10**9)}  # any: no frequency filtering at all


def overuse_score(corpus: Corpus, gloss: Gloss, headword: str) -> float | None:
    """log2(observed rate / expected rate from Wikipedia)."""
    import math
    wf = gloss.wiki_freq.get(headword, 0)
    n = corpus.count(headword)
    if not wf or not n or not corpus.total_tokens:
        return None
    expected = wf / gloss.total_wiki
    observed = n / corpus.total_tokens
    return math.log2(observed / expected)


def kl_contribution(corpus: Corpus, gloss: Gloss, headword: str) -> float | None:
    """Book-rate-weighted overuse: p_book * log2(p_book / p_expected).

    A pure log-ratio crowns one-off rare words (a deliberate 'flyspeck'
    beats a wearying 'crucial' x40); weighting by the word's share of the
    manuscript surfaces the words that carry repeated mass — the flat-
    vocabulary offenders this tool exists to find."""
    s = overuse_score(corpus, gloss, headword)
    if s is None or s <= 0:
        return None
    return corpus.count(headword) / corpus.total_tokens * s


def pick_overused(corpus: Corpus, gloss: Gloss, *, top: int, min_count: int,
                  band: str | None, min_rank: int = 500,
                  pos: set[str] | None = None,
                  sort: str = "mass") -> list[str]:
    """sort='mass': KL contribution — the words carrying the most repeated
    weight (topic terms will top this; that's honest). sort='ratio': pure
    overuse multiple — pair with --band mid to hunt style tells."""
    unfiltered = band == "any"
    lo, hi = BANDS[band] if band else (1, 10**9)
    if not unfiltered:
        lo = max(lo, min_rank)  # function words the stopword flag misses
    scored = []
    for w, n in corpus.lemma_counts.items():
        if n < min_count or w in gloss.stop:
            continue
        if pos and not pos & {p.lower() for p in gloss.pos.get(w) or []}:
            continue
        rank = gloss.rank.get(w)
        if not unfiltered and (rank is None or not (lo <= rank <= hi)):
            continue
        fn = kl_contribution if sort == "mass" else overuse_score
        s = fn(corpus, gloss, w)
        if s is not None and s > 0:
            scored.append((s, w))
    scored.sort(reverse=True)
    return [w for _, w in scored[:top]]


def pick_random(corpus: Corpus, gloss: Gloss, *, n: int, band: str | None,
                rng: random.Random,
                min_rank: int = 500) -> list[tuple[str, str, str]]:
    """(headword, file, sentence) sampled from random prose sentences.

    band='any' disables every frequency filter: any non-stopword dictionary
    word can be drawn, even ones with no Wikipedia rank."""
    unfiltered = band == "any"
    lo, hi = BANDS[band] if band else (1, 10**9)
    if not unfiltered:
        lo = max(lo, min_rank)
    picks: list[tuple[str, str, str]] = []
    seen: set[str] = set()
    order = list(range(len(corpus.sentences)))
    rng.shuffle(order)
    for i in order:
        if len(picks) >= n:
            break
        fname, sent = corpus.sentences[i]
        cands = []
        for t in WORD_RE.findall(sent.lower()):
            lem = gloss.lemma(t)
            if not lem or lem in gloss.stop or lem in seen:
                continue
            rank = gloss.rank.get(lem)
            if unfiltered or (rank is not None and lo <= rank <= hi):
                cands.append(lem)
        if cands:
            w = rng.choice(cands)
            seen.add(w)
            picks.append((w, fname, sent))
    return picks


def pick_sentences(corpus: Corpus, gloss: Gloss, *, n: int,
                   rng: random.Random) -> list[tuple[str, str, list[str]]]:
    """n uniformly random sentences, each with every dictionary word in it —
    the 'help me rephrase this exact sentence' view. No frequency bias."""
    if not corpus.sentences:
        return []
    idxs = rng.sample(range(len(corpus.sentences)),
                      min(n, len(corpus.sentences)))
    out = []
    for i in idxs:
        fname, sent = corpus.sentences[i]
        lems: list[str] = []
        for t in WORD_RE.findall(sent.lower()):
            lem = gloss.lemma(t)
            if lem and lem not in gloss.stop and lem not in lems:
                lems.append(lem)
        out.append((fname, sent, lems))
    return out


def pick_ngrams(corpus: Corpus, gloss: Gloss, *, top: int,
                min_count: int) -> list[tuple[str, int, str]]:
    """Book bi/trigrams that are OpenGloss collocations of one of their
    words -> (phrase, count, headword)."""
    colls: dict[str, list[str]] = {}

    def collocations_of(w: str) -> list[str]:
        if w not in colls:
            e = gloss.entry(w)
            colls[w] = [c.lower() for c in (e["all_collocations"] if e else []) or []]
        return colls[w]

    def functionish(tok: str) -> bool:
        lem = gloss.lemma(tok)
        rank = gloss.rank.get(lem) if lem else None
        return lem is None or lem in gloss.stop or (rank or 10**9) < 500

    hits: list[tuple[int, str, str]] = []
    for grams in (corpus.bigrams, corpus.trigrams):
        for gram, n in grams.items():
            if n < min_count:
                continue
            # "wikimedia foundation" is a finding; "the same" is noise
            if functionish(gram[0]) or functionish(gram[-1]):
                continue
            phrase = " ".join(gram)
            for tok in gram:
                lem = gloss.lemma(tok)
                if lem and lem not in gloss.stop and phrase in collocations_of(lem):
                    hits.append((n, phrase, lem))
                    break
    hits.sort(reverse=True)
    return [(p, n, w) for n, p, w in hits[:top]]


# -------------------------------------------------------------- report layer

def annotate(words: list[str], corpus: Corpus, limit: int = 12,
             skip: str | None = None) -> tuple[str, list[str]]:
    """'syn(count)' list sorted by book count ascending + fresh (unused) picks."""
    uniq = list(dict.fromkeys(w.lower() for w in words if w.lower() != skip))
    counted = sorted((corpus.count(w), w) for w in uniq)
    shown = "  ".join(f"{w}({n})" for n, w in counted[:limit])
    fresh = [w for n, w in counted if n == 0][:6]
    return shown, fresh


def colloc_partners(headword: str, corpus: Corpus) -> set[str]:
    """Book tokens that appear next to the headword (bigram neighbours)."""
    out = set()
    for (a, b), n in corpus.bigrams.items():
        if n >= 2:
            if a == headword:
                out.add(b)
            elif b == headword:
                out.add(a)
    return out


def report_word(headword: str, gloss: Gloss, corpus: Corpus,
                context: tuple[str, str] | None = None, *,
                senses: bool = False, max_register: int | None = None,
                embed_ranker=None) -> dict | None:
    e = gloss.entry(headword)
    if e is None:
        return None
    n = corpus.count(headword)
    files = corpus.lemma_files.get(headword, Counter())
    score = overuse_score(corpus, gloss, headword)
    syn, fresh_syn = annotate(e["all_synonyms"] or [], corpus, skip=headword)
    ant, _ = annotate(e["all_antonyms"] or [], corpus, limit=8, skip=headword)
    hyper, _ = annotate(e["all_hypernyms"] or [], corpus, limit=8, skip=headword)
    hypo, fresh_hypo = annotate(e["all_hyponyms"] or [], corpus, limit=10,
                                skip=headword)
    gloss_line = (e["all_definitions"] or [""])[0]
    picks = list(dict.fromkeys(fresh_syn + fresh_hypo))
    if max_register is not None:
        picks = [w for w in picks
                 if (gloss.register(w) is None
                     or gloss.register(w) <= max_register)]
    if embed_ranker is not None:
        picks = embed_ranker(headword, picks)
    picks = picks[:8]
    # enrich top picks: usage example + does it collocate with the words
    # the book already puts next to the target?
    partners = colloc_partners(headword, corpus)
    pick_info = []
    for wpick in picks[:3]:
        pe = gloss.entry(wpick)
        colls = {c.lower() for c in ((pe or {}).get("all_collocations") or [])}
        fit = any(f"{wpick} {x}" in colls or f"{x} {wpick}" in colls
                  for x in partners)
        pick_info.append({"word": wpick, "example": gloss.example(wpick),
                          "collocates": fit})
    rec = {
        "word": headword,
        "pos": e["parts_of_speech"] or [],
        "book_count": n,
        "files": dict(files.most_common()),
        "wiki_rank": e["wiki_frequency_rank"],
        "overuse_log2": None if score is None else round(score, 2),
        "definition": gloss_line,
        "synonyms": syn, "antonyms": ant, "hypernyms": hyper, "hyponyms": hypo,
        "collocations": (e["all_collocations"] or [])[:8],
        "fresh_picks": picks,
        "pick_info": pick_info,
        "context": context,
    }
    if senses and e.get("senses"):
        rec["senses"] = []
        for s in e["senses"]:
            s_syn, _ = annotate(s.get("synonyms") or [], corpus, limit=8,
                                skip=headword)
            rec["senses"].append({
                "pos": s.get("part_of_speech"),
                "definition": (s.get("definition") or "")[:120],
                "synonyms": s_syn,
            })
    return rec


def emit_pretty(rec: dict) -> None:
    pos = "/".join(rec["pos"])
    locs = ", ".join(f"{f.removesuffix('.tex')}:{c}"
                     for f, c in list(rec["files"].items())[:5])
    head = (f"── {rec['word']} ({pos}) ─ book: {rec['book_count']}x"
            + (f" [{locs}]" if locs else "")
            + (f" ─ wiki rank {rec['wiki_rank']:,}" if rec["wiki_rank"] else ""))
    print(head)
    if rec["overuse_log2"] is not None and rec["book_count"]:
        print(f"   overuse: {2 ** rec['overuse_log2']:.1f}x expected rate")
    if rec["definition"]:
        d = rec["definition"]
        print(f"   gloss: {d[:110]}{'…' if len(d) > 110 else ''}")
    for label, key in (("synonyms ", "synonyms"), ("antonyms ", "antonyms"),
                       ("hypernyms", "hypernyms"), ("hyponyms ", "hyponyms")):
        if rec[key]:
            print(f"   {label}  {rec[key]}")
    if rec["collocations"]:
        print(f"   collocs    {' · '.join(rec['collocations'])}")
    if rec["fresh_picks"]:
        marks = {p["word"]: p for p in rec.get("pick_info", [])}
        shown = [w + (" ✓" if marks.get(w, {}).get("collocates") else "")
                 for w in rec["fresh_picks"]]
        print(f"   fresh picks: {', '.join(shown)}  (✓ = collocates with "
              "this word's neighbours in the book)"
              if any(m.get("collocates") for m in marks.values())
              else f"   fresh picks: {', '.join(shown)}")
        for pinfo in rec.get("pick_info", []):
            if pinfo.get("example"):
                ex = pinfo["example"]
                print(f"      {pinfo['word']}: “{ex[:100]}"
                      f"{'…' if len(ex) > 100 else ''}”")
    for s in rec.get("senses") or []:
        print(f"   sense [{s['pos']}] {s['definition']}")
        if s["synonyms"]:
            print(f"      syn: {s['synonyms']}")
    if rec["context"]:
        f, s = rec["context"]
        print(f"   from {f}: “{s[:140]}{'…' if len(s) > 140 else ''}”")
    print()


# ------------------------------------------------------------- embed ranker

def make_embed_ranker(gloss: Gloss, corpus: Corpus):
    """OGBert (the OpenGloss sentence-embedding model) re-ranks fresh picks:
    similarity between each pick's first definition and the sentences where
    the target word actually appears in the book. GPU-automatic."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        raise SystemExit(
            "vocab_variety: --embed needs sentence-transformers; rerun as\n"
            "  uv run --with sentence-transformers "
            "scripts/vocab_variety.py --embed …") from None
    model = SentenceTransformer("mjbommar/ogbert-110m-sentence")
    print(f"embed: ogbert-110m-sentence on {model.device}", file=sys.stderr)

    def rank(headword: str, picks: list[str]) -> list[str]:
        ctx = [s for _f, s in corpus.sentences
               if headword in s.lower().split()][:3]
        if not ctx or not picks:
            return picks
        defs = []
        for w in picks:
            e = gloss.entry(w)
            d = ((e or {}).get("all_definitions") or [w])[0]
            defs.append(d)
        import numpy as np
        emb = model.encode(ctx + defs, normalize_embeddings=True)
        ctx_vec = emb[:len(ctx)].mean(axis=0)
        sims = emb[len(ctx):] @ ctx_vec
        order = np.argsort(-sims)
        return [picks[i] for i in order]

    return rank


# ---------------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--word", nargs="+", help="explicit word(s) to look up")
    ap.add_argument("--random", type=int, metavar="N",
                    help="sample N words from random prose sentences")
    ap.add_argument("--sentence", type=int, metavar="N",
                    help="sample N completely random sentences and report "
                         "every dictionary word in each (no frequency bias)")
    ap.add_argument("--ngrams", action="store_true",
                    help="flag book phrases that are stock OpenGloss collocations")
    ap.add_argument("--band", choices=sorted(BANDS),
                    help="restrict to a wiki-frequency band")
    ap.add_argument("--top", type=int, default=15,
                    help="how many overused words to report (default 15)")
    ap.add_argument("--min-count", type=int, default=5,
                    help="minimum book occurrences to consider (default 5)")
    ap.add_argument("--sort", choices=("mass", "ratio"), default="mass",
                    help="mass: most repeated weight (topic terms rise); "
                         "ratio: sharpest overuse multiple (style tells rise)")
    ap.add_argument("--pos", help="only report these parts of speech, comma-"
                    "separated (e.g. adjective,adverb,verb to isolate style "
                    "words from topic nouns)")
    ap.add_argument("--min-rank", type=int, default=500,
                    help="ignore words above this wiki-frequency rank — filters"
                         " function words the stopword flag misses (default 500)")
    ap.add_argument("--senses", action="store_true",
                    help="show per-sense definitions and synonyms (cache v2)")
    ap.add_argument("--max-register",
                    choices=list(REGISTER_ORDER), default=None,
                    help="drop fresh picks above this reading level "
                         "(e.g. 8 for middle grade, BS for trade)")
    ap.add_argument("--embed", action="store_true",
                    help="re-rank fresh picks by OGBert similarity between "
                         "each pick's definition and the word's sentences in "
                         "the book (GPU if available; needs "
                         "sentence-transformers — rerun as: uv run --with "
                         "sentence-transformers scripts/vocab_variety.py …)")
    ap.add_argument("--suggest-bans", action="store_true",
                    help="print overused-word candidates formatted for a "
                         "style profile's banned-words-add block")
    ap.add_argument("--chapter", help="restrict to files starting with this")
    ap.add_argument("--root", type=Path,
                    default=Path(__file__).resolve().parent.parent,
                    help="book root (default: this repo)")
    ap.add_argument("--dataset", default=DATASET)
    ap.add_argument("--format", choices=("pretty", "jsonl"), default="pretty")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--refresh", action="store_true",
                    help="re-fetch the OpenGloss cache")
    args = ap.parse_args()
    rng = random.Random(args.seed)

    files = discover(args.root, args.chapter)
    if not files:
        raise SystemExit(f"vocab_variety: no .tex files under {args.root}/latex/")

    gloss = Gloss(args.dataset, refresh=args.refresh)
    corpus = Corpus(files, gloss)
    print(f"corpus: {len(files)} files, {corpus.total_tokens:,} tokens, "
          f"{len(corpus.lemma_counts):,} distinct lemmas", file=sys.stderr)

    if args.suggest_bans:
        existing = set()
        style_md = args.root / "docs" / "guides" / "STYLE.md"
        if style_md.exists():
            m = re.search(r"```banned-words\n(.*?)```", style_md.read_text(),
                          re.DOTALL)
            if m:
                existing = {ln.strip().lower()
                            for ln in m.group(1).splitlines() if ln.strip()}
        # style words by default — topic nouns dominate otherwise;
        # override with --pos noun (or any list) deliberately
        expand = {"adj": "adjective", "adv": "adverb"}
        ban_pos = ({expand.get(x.strip().lower(), x.strip().lower())
                    for x in args.pos.split(",")} if args.pos
                   else {"adjective", "adverb", "verb"})
        cands = pick_overused(corpus, gloss, top=args.top * 3,
                              min_count=max(args.min_count, 8),
                              band=args.band, min_rank=args.min_rank,
                              pos=ban_pos, sort="ratio")
        print("# overuse candidates for a profile's banned-words-add block")
        print("# (review each — topic terms and deliberate refrains stay)")
        emitted = 0
        for w in cands:
            if w.lower() in existing or " " in w:
                continue
            s = overuse_score(corpus, gloss, w)
            print(f"{w:24s} # {corpus.count(w)}x, "
                  f"{2 ** s:.0f}x expected" if s else w)
            emitted += 1
            if emitted >= args.top:
                break
        if not emitted:
            print("# none above thresholds — vocabulary looks varied")
        return

    embed_ranker = None
    if args.embed:
        embed_ranker = make_embed_ranker(gloss, corpus)

    if args.ngrams:
        hits = pick_ngrams(corpus, gloss, top=args.top, min_count=args.min_count)
        if args.format == "jsonl":
            for phrase, n, w in hits:
                print(json.dumps({"phrase": phrase, "book_count": n,
                                  "headword": w}))
        else:
            if not hits:
                print("no stock collocations above threshold — good sign.")
            for phrase, n, w in hits:
                print(f"{n:4}x  “{phrase}”  (collocation of ‘{w}’)")
        return

    if args.sentence:
        for fname, sent, lems in pick_sentences(corpus, gloss,
                                                n=args.sentence, rng=rng):
            if args.format == "pretty":
                print(f"═══ {fname}: “{sent}”")
                print()
            for w in lems:
                rec = report_word(w, gloss, corpus,
                                  None if args.format == "pretty"
                                  else (fname, sent),
                                  senses=args.senses,
                                  max_register=REGISTER_ORDER.get(
                                      args.max_register),
                                  embed_ranker=embed_ranker)
                if rec is None:
                    continue
                if args.format == "jsonl":
                    print(json.dumps(rec))
                else:
                    emit_pretty(rec)
        return

    targets: list[tuple[str, tuple[str, str] | None]] = []
    if args.word:
        for w in args.word:
            lem = gloss.lemma(w) or w.lower()
            targets.append((lem, None))
    elif args.random:
        targets = [(w, (f, s)) for w, f, s in
                   pick_random(corpus, gloss, n=args.random, band=args.band,
                               rng=rng, min_rank=args.min_rank)]
    else:
        expand = {"adj": "adjective", "adv": "adverb"}
        pos = ({expand.get(p.strip().lower(), p.strip().lower())
                for p in args.pos.split(",")} if args.pos else None)
        targets = [(w, None) for w in
                   pick_overused(corpus, gloss, top=args.top,
                                 min_count=args.min_count, band=args.band,
                                 min_rank=args.min_rank, pos=pos,
                                 sort=args.sort)]

    misses = []
    for w, ctx in targets:
        rec = report_word(w, gloss, corpus, ctx, senses=args.senses,
                          max_register=REGISTER_ORDER.get(args.max_register),
                          embed_ranker=embed_ranker)
        if rec is None:
            misses.append(w)
            continue
        if args.format == "jsonl":
            print(json.dumps(rec))
        else:
            emit_pretty(rec)
    for w in misses:
        print(f"not in OpenGloss: {w}", file=sys.stderr)


if __name__ == "__main__":
    main()
