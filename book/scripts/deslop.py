#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""deslop.py -- Voice-model rewrites for revision: A/B variants + batch fix briefs.

Feeds paragraphs from the book to a locally served author-voice rewrite model.
Two modes:

  SINGLE PASSAGE (A/B ideation): pick one paragraph, print N sampled
  variations next to the original. The variants are IDEATION AIDS, not
  replacements -- read them for structure and rhythm, then hand-write the
  final line yourself. Zero edits is a valid outcome.

  BATCH (--batch): rank paragraphs by quantitative slop signals, rewrite the
  worst (or a random sample), and emit a FIX BRIEF -- original and rewrite
  side by side with file:line anchors. The brief feeds the revision
  workflow; this tool NEVER edits chapters.

Every rewrite carries a mechanical FAITHFULNESS VERDICT targeting the
measured failure modes of small voice models (invention ~5-15%;
over-compression of thin inputs):

  invented   numbers/proper nouns in the rewrite absent from the original
  dropped    numbers/proper nouns from the original missing in the rewrite
  length     under 50% or over 130% of the original word count
  slop       rewrite re-scored with the quant slop signals; non-improving
             rewrites are flagged

Setup (required -- no model ships with the template):
  1. A text->text rewrite model in the author's voice, as GGUF.
     Model selection, serving recipe, measured bench results, and failure
     modes: docs/guides/VOICE-MODELS.md (machine-independent). Short
     version: an author fine-tune on a ~4B base beats scale; without one,
     the largest instruct model that fits at Q5+; never reasoning-tuned
     models. (Reference deployment: /data0/models/voice-deslop/ on the
     author's workstation.)
  2. llama.cpp `llama-server` (CUDA build for hybrid-SSM/GDN bases).
  3. Serve it, e.g.:
       llama-server -m /path/to/your-voice-model.gguf \\
         --host 127.0.0.1 --port 8091 -ngl 99 -c 8192 --jinja --alias voice

Server discovery: --server-url, else DESLOP_SERVER_URL, else probe
127.0.0.1:8091 (Qwen voice) then :8092 (Gemma); model name from /v1/models. If nothing
is listening and DESLOP_LLAMA_SERVER/DESLOP_MODEL are set, the server is
auto-started. Decode with sampling (temperature 0.7-0.8, top_p 0.9) --
greedy over-compresses and reads MORE machine-like, not less.

Usage:
  uv run scripts/deslop.py latex/chapters/ch03.tex --line 27      # paragraph at line
  uv run scripts/deslop.py latex/chapters/ch03.tex --grep "lawn"  # paragraph by phrase
  uv run scripts/deslop.py latex/chapters/ch03.tex --lines 63-77  # explicit range
  echo "draft text" | uv run scripts/deslop.py                    # raw text
  uv run scripts/deslop.py --batch                                # worst 10 -> brief
  uv run scripts/deslop.py --batch --sample random --n 5 --seed 1
  uv run scripts/deslop.py --batch --chapter ch03 --out brief.md
  uv run scripts/deslop.py --batch --format jsonl                 # for agents
  # -n <count>   --temps 0.7,0.75,0.8   --max-tokens 400

--candidates N is the automated REVIEW-QA §7 candidate loop: N sampled
variants, each scored (faithfulness + quant slop + Pangram fraction_ai when
PANGRAM_API_KEY is set; scores content-hash cached in
~/.cache/pangram-scores.json), printed best-first. Measured on a
detector-flagged paragraph: one of three plain samples scored 0.00 AI where
the original scored 1.00 -- sampling variance plus scoring finds winners.

TIERS (compose freely; measured against Pangram 4 — VOICE-MODELS.md §1a):
  --candidates N   sample N variants, score each (faithfulness + quant slop
                   + Pangram), print best-first. The workhorse.
  --fewshot        prompt with the book's own most-human paragraphs as style
                   samples (exemplars chosen by detector verdict when
                   PANGRAM_API_KEY is set, else by quant slop)
  --notes          extract the passage's facts, then write fresh prose from
                   those notes. The only tier that moved paragraphs the
                   detector locked at 1.00; highest invention risk
  --servers U1,U2  pool candidates across several endpoints — model
                   diversity beats one model's wider pool
Purely deterministic edits (contractions, filler removal, rhythm surgery)
measured ZERO detector movement — keep them for craft, not for scores.

--diagnose (experimental) conditions the prompt on the passage's measured
problems. Measured result so far: Gemma over-obeys any added instruction --
outputs compress ~30% and stay 1.00 AI. The diagnosis lines are printed in
batch briefs for the HUMAN regardless; prefer plain prompts + --candidates
for the model.

Full workflow: docs/guides/REVIEW-QA.md ("Detector-guided de-slop pass").
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import zlib
from dataclasses import dataclass, field
from pathlib import Path

SERVER_URL = os.environ.get("DESLOP_SERVER_URL", "")
# fine-tune port first: the 2026-07-26 bench (8 real paragraphs) had the
# author fine-tune fastest AND tied-best on Pangram with zero invention —
# see docs/guides/VOICE-MODELS.md §1
PROBE_URLS = ("http://127.0.0.1:8091", "http://127.0.0.1:8092")
LLAMA_SERVER = os.environ.get("DESLOP_LLAMA_SERVER", "")
MODEL_GGUF = os.environ.get("DESLOP_MODEL", "")
CUDA_DEVICE = os.environ.get("DESLOP_CUDA_DEVICE", "0")
SERVER_LOG = os.environ.get("DESLOP_SERVER_LOG", "/tmp/deslop-server.log")

PROMPT = (
    "Rewrite the following passage in the author's voice: direct, understated, "
    "concrete, technically precise. Remove all AI-slop tells. Preserve the facts "
    "exactly -- add no fact, name, or number not in the original. "
    "Output only the rewrite.\n\n{passage}"
)

# Diagnosis-conditioned prompt: the calibration finding is that RHYTHM is
# what detectors read (a rewrite that strips every lexical tell but keeps
# uniform sentence lengths still scores 1.00 AI). Feeding the model its
# measured problems targets the axis the base prompt misses.
PROMPT_DIAGNOSED = (
    "Rewrite the following passage in the author's voice: direct, understated, "
    "concrete, technically precise. Keep roughly the original length. Preserve "
    "the facts exactly -- add no fact, name, or number not in the original. "
    "Above all, vary the rhythm: this passage reads metronomic ({diagnosis}); "
    "let one sentence run long and cut another short, the way a person "
    "writes when they mean it. Output only the rewrite.\n\n{passage}"
)

# Few-shot: real author paragraphs beat any adjective list. Measured on
# Pangram 4 (2026-07): unguided best-of-3 0.70 -> few-shot 0.63 weighted-AI.
PROMPT_FEWSHOT = """You are the author revising your own draft.

Below are STYLE SAMPLES of your published writing. They are for rhythm and \
diction only -- their subject matter is irrelevant and none of their facts, \
names, numbers, or dates may appear in your output. Study how the sentences \
run from 3 to 35 words with no metronome, how a plain word repeats instead of \
rotating through synonyms, how a paragraph can just stop.

--- STYLE SAMPLES (do not reuse any content) ---
{examples}
--- END STYLE SAMPLES ---

Now rewrite ONLY the passage below, as the same author. Every fact in your \
rewrite must come from this passage and nowhere else -- add no fact, name, \
number, or date that is not in it. Change the sentence architecture freely: \
different openings, different lengths, merge or split ideas, reorder if it \
reads better. Keep roughly the original length. Output only the rewrite.

--- PASSAGE TO REWRITE ---
{passage}"""

# Notes reconstruction: the only tier that moved paragraphs Pangram 4 locked
# at 1.00. Rewriting edits token lineage; writing from notes replaces it.
PROMPT_NOTES = """List the factual content of this passage as terse notes -- \
one fact per line, no prose, no commentary. Include every name, number, date, \
and claim.

{passage}"""

PROMPT_FROM_NOTES = """You are the author of these STYLE SAMPLES. They show \
rhythm and diction only -- none of their facts, names, or numbers may appear \
in your output.

--- STYLE SAMPLES (do not reuse any content) ---
{examples}
--- END STYLE SAMPLES ---

Write ONE paragraph of about {words} words from the notes below, in that same \
voice. Do not reuse phrasing from the notes -- they are raw material, not a \
draft. Vary sentence length hard: at least one sentence under 6 words and one \
over 25. State every fact in the notes; invent nothing. Output only the \
paragraph.

NOTES:
{notes}"""

SUBDIRS = ("chapters", "frontmatter", "front-matter", "backmatter", "back-matter")

# ---------------------------------------------------------------------------
# LaTeX -> plain text (good enough for prose paragraphs)
# ---------------------------------------------------------------------------

_UNWRAP = ("proto", "keyterm", "person", "org", "texttt", "textit", "textbf", "emph")


def detex(text: str) -> str:
    text = re.sub(r"(?<!\\)%.*$", "", text, flags=re.MULTILINE)  # comments (not \%)
    text = text.replace("\\%", "%")
    text = re.sub(r"\\cite\{[^}]*\}", "", text)
    text = re.sub(r"\\rfc\{(\d+)\}", r"RFC \1", text)
    text = re.sub(r"\\(?:label|ref|pageref)\{[^}]*\}", "", text)
    text = re.sub(r"Chapter~?\\ref\{[^}]*\}", "an earlier chapter", text)
    for cmd in _UNWRAP:
        text = re.sub(r"\\" + cmd + r"\{([^{}]*)\}", r"\1", text)
    # second pass for nesting like \texttt{\proto{X}}
    for cmd in _UNWRAP:
        text = re.sub(r"\\" + cmd + r"\{([^{}]*)\}", r"\1", text)
    text = text.replace("~", " ")
    text = text.replace("---", "\u2014").replace("--", "\u2013")
    text = text.replace("``", '"').replace("''", '"')
    text = re.sub(r"\\[a-zA-Z]+\*?(\{[^}]*\})?", "", text)  # leftover commands
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Quant slop signals + faithfulness verdict
# ---------------------------------------------------------------------------

# compact subset of slop_audit.py's signals, kept in sync by hand
CONSTRUCTIONS = [
    re.compile(r"\b(?:it|this|that)?'?s?\s*not\s+(?:just|only|merely|simply)?"
               r"\s*[^.;:!?]{2,60}[,;\u2014-]+\s*(?:but|it'?s)\b", re.IGNORECASE),
    re.compile(r"\bisn'?t\s+just\b", re.IGNORECASE),
    re.compile(r"\bnot\s+because\b[^.;:!?]{3,60}\bbut\s+because\b", re.IGNORECASE),
    re.compile(r",\s+(ensuring|showcasing|highlighting|underscoring|"
               r"emphasizing|cementing|solidifying|signaling|reflecting)\s+\w",
               re.IGNORECASE),
]
AI_VOCAB = {
    "delve", "delves", "delving", "tapestry", "intricate", "intricacies",
    "meticulous", "meticulously", "pivotal", "crucial", "underscore",
    "underscores", "underscoring", "testament", "vibrant", "boasts",
    "bolster", "bolstered", "garner", "garnered", "interplay", "enduring",
    "landscape", "showcase", "showcases", "showcasing", "fostering",
    "emphasizing", "highlighting", "enhancing", "encompassing",
    "multifaceted", "nuanced", "paramount", "renowned", "nestled",
    "seamlessly", "leverage", "leveraging", "myriad", "plethora",
}
_WORD_RE = re.compile(r"[a-z][a-z'-]*[a-z]|[a-z]")
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
# capitalized-but-not-proper: function words that start quotes/clauses
_FACT_STOP = {
    "the", "a", "an", "this", "that", "these", "those", "it", "its", "if",
    "you", "your", "yours", "we", "our", "ours", "i", "my", "he", "she",
    "his", "her", "they", "their", "them", "and", "but", "or", "not", "no",
    "in", "on", "at", "by", "for", "of", "to", "with", "what", "when",
    "where", "why", "how", "who", "there", "here", "then", "now", "so",
}


def slop_signals(text: str) -> tuple[float, list[str]]:
    words = _WORD_RE.findall(text.lower())
    hits: list[str] = []
    for rx in CONSTRUCTIONS:
        for m in rx.finditer(text):
            hits.append(f"construction \u201c{m.group(0)[:60]}\u201d")
    slop = sorted({w for w in words if w in AI_VOCAB})
    if slop:
        hits.append("slop words: " + ", ".join(slop))
    raw = text.encode()
    comp = len(zlib.compress(raw, 9)) / max(1, len(raw))
    score = (2.0 * sum(1 for h in hits if h.startswith("construction"))
             + sum(1 for w in words if w in AI_VOCAB)
             + max(0.0, (0.40 - comp) * 10))
    return score, hits


def diagnose(text: str) -> list[str]:
    """Measured, passage-specific problems for the diagnosis-conditioned
    prompt (and for the human reading the brief)."""
    probs: list[str] = []
    sents = [s for s in _SENT_SPLIT.split(text) if len(s.split()) >= 2]
    lens = [len(s.split()) for s in sents]
    if len(lens) >= 3:
        mean = sum(lens) / len(lens)
        var = sum((x - mean) ** 2 for x in lens) / (len(lens) - 1)
        cv = (var ** 0.5) / mean if mean else 0.0
        if cv < 0.45:
            probs.append(
                f"sentence lengths are uniform (~{mean:.0f} words each, "
                "cv {:.2f}) -- vary hard: mix a 5-word sentence with a "
                "30-word one; do not keep the metronome".format(cv))
    if lens and max(lens) > 40:
        probs.append(f"one sentence runs {max(lens)} words -- split it")
    openers = {}
    for s in sents:
        w = s.split()[0].lower().strip("\u201c\"'")
        openers[w] = openers.get(w, 0) + 1
    for w, n in openers.items():
        if n >= 3 or (n >= 2 and w in ("this", "it", "there")):
            probs.append(f"{n} sentences open with '{w}' -- break the "
                         "repeated opener")
    for rx in CONSTRUCTIONS:
        for m in rx.finditer(text):
            probs.append("remove the contrast/participle frame: "
                         f"\u201c{m.group(0)[:50]}\u201d")
    slop = sorted({w for w in _WORD_RE.findall(text.lower()) if w in AI_VOCAB})
    if slop:
        probs.append("replace the stock vocabulary: " + ", ".join(slop))
    return probs[:6]


def extract_facts(text: str) -> set[str]:
    """Checkable particulars: normalized numbers + mid-sentence proper nouns."""
    out: set[str] = set()
    for tok in re.findall(r"\d[\d,.]*", text):
        out.add(tok.rstrip(".,").replace(",", ""))
    # dotted identifiers are facts too: comp.lang.lisp, robots.txt, 10.0.0.1
    for tok in re.findall(r"\b[\w-]+(?:\.[\w-]+)+\b", text):
        if not tok.replace(".", "").isdigit():
            out.add(tok.lower())
    for sent in _SENT_SPLIT.split(text):
        for t in sent.split()[1:]:
            t_ = t.strip("\u201c\u201d\"'().,;:\u2014-")
            if (t_[:1].isupper() and t_[1:2].islower()
                    and t_.lower() not in _FACT_STOP):
                out.add(t_.lower())
    return out


def _same_fact(a: str, b: str) -> bool:
    """Inflection tolerance: Egypt/Egyptian, Bayes/Bayesian are one fact."""
    if len(a) > len(b):
        a, b = b, a
    return len(a) >= 4 and b.startswith(a)


def assess(orig: str, new: str) -> dict:
    """Faithfulness + improvement verdict for one rewrite."""
    o_facts, n_facts = extract_facts(orig), extract_facts(new)
    invented = sorted(f for f in n_facts - o_facts
                      if not any(_same_fact(f, o) for o in o_facts))
    dropped = sorted(f for f in o_facts - n_facts
                     if not any(_same_fact(f, n) for n in n_facts))
    ratio = len(new.split()) / max(1, len(orig.split()))
    o_score, _ = slop_signals(orig)
    n_score, n_hits = slop_signals(new)
    flags = []
    if invented:
        flags.append("invented")
    if dropped:
        flags.append("dropped")
    if ratio < 0.5:
        flags.append("compressed")
    elif ratio > 1.3:
        flags.append("expanded")
    if o_score > 0 and n_score >= o_score:
        flags.append("no-improvement")
    return {
        "flags": flags, "invented": invented, "dropped": dropped,
        "length_ratio": round(ratio, 2),
        "slop_before": round(o_score, 1), "slop_after": round(n_score, 1),
        "residual_signals": n_hits, "ok": not flags,
    }


def verdict_line(v: dict) -> str:
    if v["ok"]:
        return "OK"
    bits = []
    if v["invented"]:
        bits.append("invented: " + ", ".join(v["invented"][:5]))
    if v["dropped"]:
        bits.append("dropped: " + ", ".join(v["dropped"][:5]))
    if "compressed" in v["flags"] or "expanded" in v["flags"]:
        bits.append(f"length \u00d7{v['length_ratio']}")
    if "no-improvement" in v["flags"]:
        bits.append(f"slop {v['slop_before']}\u2192{v['slop_after']}")
    return "; ".join(bits)


# ---------------------------------------------------------------------------
# Cached Pangram scoring (candidate ranking)
# ---------------------------------------------------------------------------

# shared with pangram_check.py — full result dicts keyed by model+text hash
PANGRAM_CACHE = Path.home() / ".cache" / "pangram-results.json"
PANGRAM_MODEL = os.environ.get("PANGRAM_MODEL", "pangram-4")
# label boundary measured on our corpus; above SATURATED progress is
# unmeasurable (the scale compresses into 0.98-0.994)
PANGRAM_BOUNDARY = 0.37
PANGRAM_SATURATED = 0.98


def _window_score(res: dict) -> float | None:
    """Token-weighted mean of per-window ai_assistance_score."""
    wins = res.get("windows") or []
    if not wins:
        return None
    tw = sum(w.get("token_length") or 1 for w in wins) or 1
    return round(sum((w.get("ai_assistance_score") or 0.0)
                     * (w.get("token_length") or 1) for w in wins) / tw, 4)


def _pangram_cache_load() -> dict:
    try:
        return json.loads(PANGRAM_CACHE.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def pangram_score(text: str, cache: dict) -> float | None:
    """Token-weighted mean of window `ai_assistance_score` — the CONTINUOUS
    detector signal, content-hash cached.

    NOT fraction_ai: that is a word-weighted average of *hard* segment
    labels, so a single-paragraph submission (one window) can only return
    0.0 or 1.0. Measured on our own cache: 97% of single-paragraph verdicts
    saturate, and windows scoring 0.56 and 0.64 both report fraction_ai=1.0
    while 0.33 reports "Human". Ranking candidates on that is a coin flip.
    The continuous score has a label boundary near 0.35-0.41 and saturates
    above ~0.98 (where progress is unmeasurable).

    Returns None when PANGRAM_API_KEY is unset or the call fails."""
    import hashlib
    key = os.environ.get("PANGRAM_API_KEY")
    if not key:
        return None
    # published typography before scoring — Pangram verdicts flip on
    # --- vs a real em dash (REVIEW-QA §2 calibration)
    text = (text.replace("---", "\u2014").replace("--", "\u2013")
            .replace("``", "\u201c").replace("''", "\u201d"))
    h = PANGRAM_MODEL + ":" + hashlib.sha256(text.strip().encode()).hexdigest()
    if h in cache:
        try:
            return _window_score(cache[h])
        except (AttributeError, TypeError):
            return None
    try:
        req = urllib.request.Request(
            "https://text.external-api.pangram.com/task",
            data=json.dumps({"text": text, "model": PANGRAM_MODEL,
                             "public_dashboard_link": False}).encode(),
            headers={"Content-Type": "application/json", "x-api-key": key})
        with urllib.request.urlopen(req, timeout=30) as r:
            task_id = json.load(r)["task_id"]
        deadline = time.time() + 120
        while time.time() < deadline:
            req = urllib.request.Request(
                f"https://text.external-api.pangram.com/task/{task_id}",
                headers={"x-api-key": key})
            with urllib.request.urlopen(req, timeout=30) as r:
                res = json.load(r)
            if res.get("stage") == "STAGE_SUCCESS":
                cache[h] = res
                PANGRAM_CACHE.parent.mkdir(parents=True, exist_ok=True)
                PANGRAM_CACHE.write_text(json.dumps(cache))
                return _window_score(res)
            if res.get("stage") == "STAGE_FAILED":
                return None
            time.sleep(2)
    except (urllib.error.URLError, OSError, KeyError, ValueError):
        return None
    return None


# ---------------------------------------------------------------------------
# Passage selection
# ---------------------------------------------------------------------------


def paragraphs(lines: list[str]):
    """Yield (start_line_1idx, end_line_1idx, text) for blank-line-separated blocks."""
    start, buf = None, []
    for i, ln in enumerate(lines, 1):
        if ln.strip():
            if start is None:
                start = i
            buf.append(ln)
        elif start is not None:
            yield start, i - 1, "\n".join(buf)
            start, buf = None, []
    if start is not None:
        yield start, len(lines), "\n".join(buf)


def select_passage(path: str, line: int | None, grep: str | None, lines_range: str | None) -> tuple[str, str]:
    raw = Path(path).read_text().splitlines()
    if lines_range:
        a, _, b = lines_range.partition("-")
        lo, hi = int(a), int(b or a)
        block = "\n".join(raw[lo - 1 : hi])
        return block, f"{path}:{lo}-{hi}"
    for s, e, block in paragraphs(raw):
        if line is not None and s <= line <= e:
            return block, f"{path}:{s}-{e}"
        if grep and re.search(grep, block, re.IGNORECASE):
            return block, f"{path}:{s}-{e}"
    sys.exit(f"error: no paragraph matched in {path}")


@dataclass
class Unit:
    file: str
    line: int
    text: str
    score: float = 0.0
    signals: list[str] = field(default_factory=list)


def discover(root: Path, chapter: str | None) -> list[Path]:
    files: list[Path] = []
    for name in SUBDIRS:
        d = root / "latex" / name
        if d.exists():
            files += sorted(d.glob("*.tex"))
    if chapter:
        files = [f for f in files if f.name.startswith(chapter)]
    return files


def fewshot_block(root: Path, n: int = 3, pool: int = 12) -> str:
    """n style exemplars from the book itself.

    Selection matters more than the prompt wording: exemplars the DETECTOR
    already reads as human transfer; merely low-slop ones do not (measured
    2026-07 — same prompt, quant-picked exemplars moved nothing, while
    detector-picked ones drove the largest single-tier gain). With
    PANGRAM_API_KEY set, the lowest-slop `pool` candidates are scored
    (cached) and the most-human `n` win; otherwise fall back to quant."""
    units = batch_units(root, None, 45, 130)
    if not units:
        return ""
    units.sort(key=lambda u: u.score)
    picks = units[:n]
    if os.environ.get("PANGRAM_API_KEY"):
        cache = _pangram_cache_load()
        scored = []
        for u in units[:pool]:
            s = pangram_score(u.text, cache)
            if s is not None:
                scored.append((s, u))
        if scored:
            scored.sort(key=lambda x: x[0])
            picks = [u for _s, u in scored[:n]]
    return "\n\n".join(f"EXAMPLE {i + 1}: {u.text}"
                        for i, u in enumerate(picks))


def batch_units(root: Path, chapter: str | None,
                lo: int, hi: int) -> list[Unit]:
    units: list[Unit] = []
    for f in discover(root, chapter):
        for s, _e, block in paragraphs(f.read_text().splitlines()):
            prose = detex(block)
            n = len(prose.split())
            alpha = sum(c.isalpha() or c.isspace() for c in prose)
            if lo <= n <= hi and alpha / max(1, len(prose)) > 0.85:
                u = Unit(f.name, s, prose)
                u.score, u.signals = slop_signals(prose)
                units.append(u)
    return units


# ---------------------------------------------------------------------------
# Server management + generation
# ---------------------------------------------------------------------------


def probe(base: str, timeout: float = 2.0) -> str | None:
    """Model name if an OpenAI-compatible server answers at base, else None."""
    try:
        with urllib.request.urlopen(f"{base}/v1/models", timeout=timeout) as r:
            return json.load(r)["data"][0]["id"]
    except (urllib.error.URLError, OSError, KeyError, IndexError, ValueError):
        return None


def ensure_server(url_flag: str | None) -> tuple[str, str]:
    """(base_url, model). Probe flag/env/default ports; auto-start if configured."""
    candidates = [c for c in (url_flag, SERVER_URL) if c] or list(PROBE_URLS)
    for base in candidates:
        model = probe(base)
        if model:
            return base, model
    if not (LLAMA_SERVER and MODEL_GGUF):
        sys.exit(
            "error: no voice server on " + ", ".join(candidates)
            + " and DESLOP_LLAMA_SERVER/DESLOP_MODEL are not set -- see the "
            "docstring + docs/guides/VOICE-MODELS.md for setup)")
    base = candidates[0] if (url_flag or SERVER_URL) else PROBE_URLS[1]
    port = base.rsplit(":", 1)[-1]
    print(f"starting de-slop server on {base} (log: {SERVER_LOG}) ...",
          file=sys.stderr)
    with open(SERVER_LOG, "ab") as log:
        subprocess.Popen(
            [
                LLAMA_SERVER, "-m", MODEL_GGUF,
                "--host", "127.0.0.1", "--port", port,
                "-ngl", "99", "-c", "8192", "--jinja", "--alias", "voice",
            ],
            env={"CUDA_VISIBLE_DEVICES": CUDA_DEVICE, "PATH": "/usr/bin:/bin"},
            stdout=log, stderr=log, start_new_session=True,
        )
    for _ in range(60):
        time.sleep(2)
        model = probe(base)
        if model:
            return base, model
    sys.exit(f"error: server did not become ready; see {SERVER_LOG}")


def generate(base: str, model: str, passage: str, temp: float, seed: int,
             max_tokens: int, diagnosis: list[str] | None = None,
             examples: str = "", notes_mode: bool = False) -> str:
    """One rewrite. examples -> few-shot prompt; notes_mode -> two-step
    notes extraction then reconstruction (see PROMPT_NOTES)."""
    if notes_mode:
        notes = _complete(base, model,
                          PROMPT_NOTES.format(passage=passage), 0.3,
                          seed, max_tokens)
        content = PROMPT_FROM_NOTES.format(
            examples=examples or "(no exemplars available)",
            words=len(passage.split()), notes=notes)
    elif examples:
        content = PROMPT_FEWSHOT.format(examples=examples, passage=passage)
    elif diagnosis:
        content = PROMPT_DIAGNOSED.format(
            diagnosis="; ".join(diagnosis), passage=passage)
    else:
        content = PROMPT.format(passage=passage)
    return _complete(base, model, content, temp, seed, max_tokens)


def _complete(base: str, model: str, content: str, temp: float, seed: int,
              max_tokens: int) -> str:
    body = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": content}],
            "temperature": temp,
            "top_p": 0.9,
            "seed": seed,
            "max_tokens": max_tokens,
            "chat_template_kwargs": {"enable_thinking": False},
        }
    ).encode()
    req = urllib.request.Request(
        f"{base}/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)["choices"][0]["message"]["content"].strip()


# ---------------------------------------------------------------------------
# Batch mode -> fix brief
# ---------------------------------------------------------------------------


def run_batch(args, base: str, model: str) -> None:
    units = batch_units(args.root, args.chapter, args.min_words, args.max_words)
    if not units:
        sys.exit(f"deslop: no eligible paragraphs "
                 f"({args.min_words}-{args.max_words} words)")
    sample = args.sample or ("random" if (args.n or args.pct) else "worst")
    rng = random.Random(args.seed)
    if sample == "worst":
        units.sort(key=lambda u: u.score, reverse=True)
    elif sample == "random":
        rng.shuffle(units)
    if args.pct is not None:
        units = units[:max(1, math.ceil(len(units) * args.pct / 100))]
    elif args.n is not None:
        units = units[:args.n]
    if args.limit > 0:
        units = units[:args.limit]

    md: list[str] = []
    rows: list[dict] = []
    ok = 0
    for i, u in enumerate(units, 1):
        print(f"  [{i}/{len(units)}] {u.file}:{u.line} (slop {u.score:.1f})",
              file=sys.stderr)
        diagnosis = diagnose(u.text) if args.diagnose else None
        examples = (fewshot_block(args.root)
                    if (args.fewshot or args.notes) else "")
        cands = []
        try:
            for k in range(args.candidates or 1):
                temp = args.temps_list[k % len(args.temps_list)]
                out = generate(base, model, u.text, temp, seed=1000 + k,
                               max_tokens=args.max_tokens,
                               diagnosis=diagnosis, examples=examples,
                               notes_mode=args.notes)
                cands.append((out, assess(u.text, out)))
        except (urllib.error.URLError, OSError, KeyError) as e:
            print(f"    ERROR {e}", file=sys.stderr)
            continue
        if args.candidates and len(cands) > 1:
            cache = _pangram_cache_load()
            scored = [(pangram_score(o, cache), o, v) for o, v in cands]
            scored.sort(key=lambda x: (not x[2]["ok"],
                                       x[0] if x[0] is not None else 1.0,
                                       x[2]["slop_after"]))
            _pg, new, v = scored[0]
        else:
            new, v = cands[0]
        ok += v["ok"]
        rows.append({"file": u.file, "line": u.line, "model": model,
                     "original": u.text, "rewrite": new, **v})
        status = "OK" if v["ok"] else " / ".join(v["flags"])
        md += [f"## {u.file}:{u.line} \u2014 {status}",
               f"slop {v['slop_before']} \u2192 {v['slop_after']}, "
               f"length \u00d7{v['length_ratio']}"]
        for d in diagnose(u.text):
            md.append(f"- diagnosis: {d}")
        if v["invented"]:
            md.append(f"- **invented facts (verify!):** {', '.join(v['invented'])}")
        if v["dropped"]:
            md.append(f"- **dropped facts:** {', '.join(v['dropped'])}")
        if v["residual_signals"]:
            md.append("- residual: " + "; ".join(v["residual_signals"]))
        md += ["", "**Original:**", f"> {u.text}", "",
               "**Rewrite:**", f"> {new}", ""]

    if args.format == "jsonl":
        out_text = "\n".join(json.dumps(r) for r in rows) + "\n"
    else:
        out_text = "\n".join([
            "# De-slop fix brief", "",
            f"Model: `{model}` at `{base}` \u2014 {len(rows)} rewrite(s), "
            f"{ok} clean, {len(rows) - ok} flagged.", "",
            "Rewrites are PROPOSALS (see docstring: invention/compression "
            "risks). Verify flagged facts; apply via the revision workflow, "
            "never blindly.", "",
        ] + md)
    if args.out:
        args.out.write_text(out_text)
        print(f"deslop: brief -> {args.out}", file=sys.stderr)
    else:
        print(out_text)
    print(f"deslop: {len(rows)} rewrite(s), {ok} clean, "
          f"{len(rows) - ok} flagged", file=sys.stderr)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def wc(s: str) -> int:
    return len(s.split())


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?", help=".tex file (omit to read stdin or --batch)")
    ap.add_argument("--line", type=int, help="pick the paragraph containing this line")
    ap.add_argument("--grep", help="pick the first paragraph matching this regex")
    ap.add_argument("--lines", help="explicit range, e.g. 63-77")
    ap.add_argument("-n", type=int, default=None,
                    help="variations (single mode, default 3) / batch sample size")
    ap.add_argument("--temps", default="0.7,0.75,0.8", help="comma list, cycled per variation")
    ap.add_argument("--diagnose", action="store_true",
                    help="condition the rewrite on measured problems (rhythm, "
                         "openers, constructions) — targets what detectors "
                         "actually read")
    ap.add_argument("--servers", default=None,
                    help="comma-separated extra endpoints to pool candidates "
                         "from (model diversity is the largest single lever "
                         "on detector scores — see VOICE-MODELS.md)")
    ap.add_argument("--fewshot", action="store_true",
                    help="few-shot the prompt with the book's own cleanest "
                         "paragraphs (measured: best single-tier gain)")
    ap.add_argument("--notes", action="store_true",
                    help="notes reconstruction — extract facts, then write "
                         "fresh prose from them. The only tier that moved "
                         "paragraphs Pangram 4 locked at 1.00; highest "
                         "invention risk, so guards matter most here")
    ap.add_argument("--candidates", type=int, default=None, metavar="N",
                    help="REVIEW-QA §7 candidate loop: N variants, each "
                         "scored (quant + faithfulness, + Pangram when "
                         "PANGRAM_API_KEY is set, content-hash cached), "
                         "ranked best-first")
    ap.add_argument("--max-tokens", type=int, default=400)
    ap.add_argument("--server-url", default=None,
                    help="OpenAI-compatible server base (default: "
                         "DESLOP_SERVER_URL, else probe :8092 then :8091)")
    ap.add_argument("--model", default=None,
                    help="model name (default: first from /v1/models)")
    # batch mode
    ap.add_argument("--batch", action="store_true",
                    help="rank paragraphs by slop signals and emit a fix brief")
    ap.add_argument("--sample", choices=("worst", "random"), default=None,
                    help="batch: worst (default) or random (default with --n/--pct)")
    ap.add_argument("--pct", type=float, default=None, help="batch: percent of paragraphs")
    ap.add_argument("--limit", type=int, default=10,
                    help="batch: cap on rewrites (default 10; 0 = uncapped)")
    ap.add_argument("--min-words", type=int, default=40,
                    help="batch: paragraph floor (models over-compress thin inputs)")
    ap.add_argument("--max-words", type=int, default=200, help="batch: paragraph ceiling")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--chapter", help="batch: restrict to files starting with this")
    ap.add_argument("--root", type=Path,
                    default=Path(__file__).resolve().parent.parent,
                    help="batch: book root (default: this repo)")
    ap.add_argument("--out", type=Path, default=None, help="batch: write brief here")
    ap.add_argument("--format", choices=("markdown", "jsonl"), default="markdown")
    args = ap.parse_args()
    args.temps_list = [float(t) for t in args.temps.split(",")]

    base, auto_model = ensure_server(args.server_url)
    model = args.model or auto_model
    print(f"deslop: {base} model={model}", file=sys.stderr)

    if args.batch:
        run_batch(args, base, model)
        return

    if args.file:
        if not (args.line or args.grep or args.lines):
            sys.exit("error: with a file, give --line, --grep, or --lines")
        raw, where = select_passage(args.file, args.line, args.grep, args.lines)
        passage = detex(raw)
    else:
        passage, where = sys.stdin.read().strip(), "stdin"
        if not passage:
            sys.exit("error: empty stdin and no file given (or use --batch)")

    n_words = wc(passage)
    if not 40 <= n_words <= 180:
        print(
            f"note: passage is {n_words} words; model sweet spot is 40-180 "
            f"({'may inject filler' if n_words < 40 else 'may over-compress or truncate'})",
            file=sys.stderr,
        )
    if "\\begin{" in passage:
        print("note: passage contains a LaTeX environment; results may be poor", file=sys.stderr)

    diagnosis = diagnose(passage) if args.diagnose else None
    examples = (fewshot_block(args.root)
                if (args.fewshot or args.notes) else "")
    if diagnosis:
        print("diagnosis:", file=sys.stderr)
        for d in diagnosis:
            print(f"  - {d}", file=sys.stderr)

    n_var = args.candidates or args.n or 3
    cache = _pangram_cache_load()
    orig_pg = pangram_score(passage, cache) if args.candidates else None
    print(f"\n\u2500\u2500 ORIGINAL  [{where}]  ({n_words} words)"
          + (f"  pangram={orig_pg:.2f}" if orig_pg is not None else "")
          + " \u2500\u2500")
    print(passage)

    endpoints = [(base, model)]
    for extra in (args.servers or "").split(","):
        extra = extra.strip()
        if not extra:
            continue
        m = probe(extra)
        if m:
            endpoints.append((extra, m))
        else:
            print(f"deslop: WARN no server at {extra}", file=sys.stderr)

    variants = []
    idx = 0
    for ep_base, ep_model in endpoints:
        for i in range(n_var):
            temp = args.temps_list[i % len(args.temps_list)]
            try:
                out = generate(ep_base, ep_model, passage, temp,
                               seed=1000 + i, max_tokens=args.max_tokens,
                               diagnosis=diagnosis, examples=examples,
                               notes_mode=args.notes)
            except (urllib.error.URLError, OSError, KeyError) as e:
                print(f"deslop: {ep_model} error {e}", file=sys.stderr)
                continue
            v = assess(passage, out)
            pg = pangram_score(out, cache) if args.candidates else None
            variants.append((idx, temp, out, v, pg))
            idx += 1

    if args.candidates:
        # rank: faithful first, then detector score, then residual slop
        variants.sort(key=lambda x: (not x[3]["ok"],
                                     x[4] if x[4] is not None else 1.0,
                                     x[3]["slop_after"]))
    for rank, (i, temp, out, v, pg) in enumerate(variants):
        label = chr(ord("A") + (i % 26))
        head = (f"\n\u2500\u2500 #{rank + 1} {label}  (temp {temp}, "
                f"{wc(out)} words)"
                + (f"  pangram={pg:.2f}" if pg is not None else "")
                + f" \u2014 {verdict_line(v)} \u2500\u2500")
        print(head)
        print(out)
    print()


if __name__ == "__main__":
    main()
