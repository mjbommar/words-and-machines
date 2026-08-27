#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Pangram AI-detection check — external detector cross-check per chapter.

Sends detexed chapter prose to the Pangram bulk API
(https://www.pangram.com) — all sampled units in one submission
(chunked at 200 items), polled as a set, results paged back — and
reports, per unit and book-wide, the fraction classified AI /
AI-assisted / human, plus every non-human window with its confidence.
This is the outside-in complement to the house-signal tools
(`make metrics`, `make slop`), which explain *why* prose reads as
machine text while Pangram scores *whether* a production-grade
detector thinks it is.

Requires PANGRAM_API_KEY in the environment. Two API paths:
realtime ($0.05/1k words, seconds per unit) and bulk ($0.04/1k words,
one submission per run, but the queue can take many minutes even for
small jobs). Default --api auto uses realtime for runs of <= 10 units
and bulk above that; the estimated cost of a run is printed to stderr
before any text is sent, and the sampling flags below bound it.

Usage:
    export PANGRAM_API_KEY=...
    uv run scripts/pangram_check.py                      # every chapter
    uv run scripts/pangram_check.py --chapter ch03       # one chapter
    uv run scripts/pangram_check.py --unit paragraph --sample random --n 5
    uv run scripts/pangram_check.py --pct 10             # 10% of units
    uv run scripts/pangram_check.py --root ../other-book --format jsonl

READING THE NUMBERS (Pangram 4). `fraction_ai` is a word-weighted average
of hard per-segment labels: a one-window submission (a single paragraph)
can only return 0.0 or 1.0. Use it as a verdict, never as a score or a
ranking key — 97% of our single-paragraph verdicts saturate, and windows
scoring 0.56 and 0.64 both report 1.0 while 0.33 reports "Human". The
continuous signal is `windows[].ai_assistance_score` (surfaced per flagged
window below, and used for ranking by deslop.py): label boundary ~0.37,
saturating above ~0.98. `humanizer_max` is a negative control for
commercial-humanizer artifacts — log it, never optimize it.

Scores are also context-dependent: the same paragraph scores differently
alone than inside its chapter (VOICE-MODELS.md §1b).

Advisory only — never a CI gate. Detectors have false positives; treat
a high fraction_ai as a prompt to run `make slop` / `make metrics` and
edit, not as a verdict.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

API_BASE = "https://text.external-api.pangram.com"
# content-hash result cache, shared with deslop.py's candidate scorer —
# re-runs only pay for changed text
CACHE_PATH = Path.home() / ".cache" / "pangram-results.json"
# Pangram 3 is deprecated 2026-09-30; requests must name a model.
# GET /models lists what the key can use ("default", "pangram-4").
PANGRAM_MODEL = os.environ.get("PANGRAM_MODEL", "pangram-4")
COST_REALTIME = 0.05   # v4: $0.05/100 words on long-form; see docs
COST_BULK = 0.04
AUTO_BULK_THRESHOLD = 10
MIN_WORDS = 60          # Pangram windows need real text to classify
POLL_INTERVAL = 2.0
POLL_INTERVAL_MAX = 15.0
BULK_CHUNK = 200

SUBDIRS = ("chapters", "frontmatter", "front-matter", "backmatter", "back-matter")
DROP_ENVS = (
    "tikzpicture", "figure", "table", "tabular", "tabularx", "lstlisting",
    "verbatim", "Verbatim", "equation", "align", "alignat", "gather",
    "definitionbox", "tryitbox", "examplebox", "codelisting", "promptcode",
    "outputcode",
)


def light_detex(text: str) -> str:
    text = re.sub(r"(?<!\\)%.*", "", text)
    # published typography — Pangram verdicts flip on --- vs real em dash
    # (REVIEW-QA §2 calibration), so normalize before any scoring
    text = text.replace("---", "\u2014").replace("--", "\u2013")
    text = text.replace("``", "\u201c").replace("''", "\u201d")
    for env in DROP_ENVS:
        text = re.sub(rf"\\begin\{{{env}\*?\}}.*?\\end\{{{env}\*?\}}", " ",
                      text, flags=re.DOTALL)
    text = re.sub(r"\$[^$]*\$", " ", text)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", text)
    text = re.sub(r"[{}~]", " ", text)
    return re.sub(r"[ \t]+", " ", text).strip()


def discover(root: Path, chapter: str | None) -> list[Path]:
    files: list[Path] = []
    for name in SUBDIRS:
        d = root / "latex" / name
        if d.exists():
            files += sorted(d.glob("*.tex"))
    if chapter:
        files = [f for f in files if f.name.startswith(chapter)]
    return files


@dataclass
class Unit:
    file: str
    line: int
    text: str

    @property
    def words(self) -> int:
        return len(self.text.split())


def build_units(files: list[Path], kind: str) -> list[Unit]:
    units: list[Unit] = []
    for f in files:
        if kind == "file":
            prose = re.sub(r"\s+", " ", light_detex(f.read_text())).strip()
            alpha = sum(c.isalpha() or c.isspace() for c in prose)
            if (len(prose.split()) >= MIN_WORDS
                    and alpha / max(1, len(prose)) > 0.85):
                units.append(Unit(f.name, 1, prose))
            continue
        # paragraph units with line anchors
        buf: list[str] = []
        start = 1
        for i, line in enumerate(f.read_text().splitlines() + [""], 1):
            if line.strip():
                if not buf:
                    start = i
                buf.append(line)
                continue
            if buf:
                prose = re.sub(r"\s+", " ", light_detex("\n".join(buf))).strip()
                alpha = sum(c.isalpha() or c.isspace() for c in prose)
                if (len(prose.split()) >= MIN_WORDS
                        and alpha / max(1, len(prose)) > 0.85):
                    units.append(Unit(f.name, start, prose))
                buf = []
    return units


# ------------------------------------------------------------------- cache

def cache_load() -> dict:
    try:
        return json.loads(CACHE_PATH.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def cache_key(text: str) -> str:
    """Version-keyed: v3 and v4 verdicts must never share an entry."""
    import hashlib
    return PANGRAM_MODEL + ":" + hashlib.sha256(text.strip().encode()).hexdigest()


def cache_save(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache))


# ---------------------------------------------------------------- API client

def api_request(url: str, key: str, payload: dict | None = None) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Content-Type": "application/json", "x-api-key": key},
        method="POST" if payload is not None else "GET",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def classify_realtime(units: list[Unit], key: str,
                      wait: float) -> dict[int, dict]:
    """One task per unit, submitted and polled sequentially (seconds each).
    Content-hash cached: unchanged units cost nothing on re-runs."""
    results: dict[int, dict] = {}
    cache = cache_load()
    hits = 0
    for i, u in enumerate(units):
        ck = cache_key(u.text)
        if ck in cache:
            results[i] = cache[ck]
            hits += 1
            continue
        try:
            task = api_request(f"{API_BASE}/task", key,
                               {"text": u.text, "model": PANGRAM_MODEL,
                                "public_dashboard_link": False})
            task_id = task.get("task_id")
            if not task_id:
                raise RuntimeError(f"no task_id in response: {task}")
            deadline = time.time() + min(wait, 180.0)
            while True:
                r = api_request(f"{API_BASE}/task/{task_id}", key)
                stage = r.get("stage", "")
                if stage == "STAGE_SUCCESS":
                    results[i] = r
                    cache[ck] = r
                    break
                if stage == "STAGE_FAILED":
                    results[i] = {"_error": r.get("error", "STAGE_FAILED")}
                    break
                if time.time() > deadline:
                    results[i] = {"_error": f"task {task_id} timed out"}
                    break
                time.sleep(POLL_INTERVAL)
        except (urllib.error.URLError, OSError, RuntimeError) as e:
            results[i] = {"_error": str(e)}
    cache_save(cache)
    if hits:
        print(f"pangram_check: {hits}/{len(units)} unit(s) from cache",
              file=sys.stderr)
    return results


def classify_bulk(units: list[Unit], key: str, wait: float,
                  resume: str | None = None) -> dict[int, dict]:
    """Submit all units via the bulk API (chunked), poll each bulk to a
    terminal status, page results. Returns {unit_index: result-or-error}.
    The bulk queue is a batch product — jobs can take minutes; on timeout
    the bulk_id is printed so the run can be finished later with --resume
    (same flags and --seed, so unit indices line up)."""
    results: dict[int, dict] = {}
    cache = cache_load()
    pending: list[tuple[int, Unit]] = []
    for i, u in enumerate(units):
        r = cache.get(cache_key(u.text))
        if r is not None and not resume:
            results[i] = r
        else:
            pending.append((i, u))
    if len(results):
        print(f"pangram_check: {len(results)}/{len(units)} unit(s) from "
              "cache", file=sys.stderr)
    for lo in range(0, len(pending), BULK_CHUNK):
        chunk = pending[lo:lo + BULK_CHUNK]
        if resume and lo == 0:
            bulk_id = resume
            print(f"pangram_check: resuming {bulk_id}", file=sys.stderr)
        else:
            sub = api_request(f"{API_BASE}/bulk", key, {
                "model": PANGRAM_MODEL,
                "items": [{"id": str(i), "text": u.text} for i, u in chunk]})
            bulk_id = sub.get("bulk_id")
            if not bulk_id:
                raise RuntimeError(f"no bulk_id in response: {sub}")
            for bad in sub.get("failed_items") or []:
                print(f"pangram_check: item rejected at submit: {bad}",
                      file=sys.stderr)
        # poll the set (gentle backoff — bulk jobs can queue for minutes)
        deadline = time.time() + wait
        interval = POLL_INTERVAL
        while True:
            status = api_request(f"{API_BASE}/bulk/{bulk_id}", key)
            done = (status.get("succeeded", 0) + status.get("failed", 0)
                    >= status.get("total_items", len(chunk)))
            if status.get("status") in ("succeeded", "failed") or done:
                break
            if time.time() > deadline:
                raise RuntimeError(
                    f"bulk {bulk_id} still {status.get('status')!r} after "
                    f"{wait:.0f}s — finish later with --resume {bulk_id} "
                    "(same flags and --seed)")
            time.sleep(interval)
            interval = min(interval * 1.5, POLL_INTERVAL_MAX)
        # page results
        offset, total = 0, None
        while total is None or offset < total:
            page = api_request(
                f"{API_BASE}/bulk/{bulk_id}/results"
                f"?offset={offset}&limit=100", key)
            total = page.get("total_items", 0)
            items = page.get("items", [])
            if not items:
                break
            for item in items:
                idx = int(item.get("id", -1))
                if item.get("stage") == "STAGE_SUCCESS" and item.get("result"):
                    results[idx] = item["result"]
                    if 0 <= idx < len(units):
                        cache[cache_key(units[idx].text)] = item["result"]
                else:
                    results[idx] = {"_error": item.get("error")
                                    or item.get("stage", "unknown")}
            offset += len(items)
    cache_save(cache)
    return results


# ---------------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--unit", choices=("file", "paragraph"), default="file",
                    help="what each API call covers (default: file)")
    ap.add_argument("--sample", choices=("all", "random"), default="all")
    ap.add_argument("--n", type=int, default=None,
                    help="number of units (implies --sample random)")
    ap.add_argument("--pct", type=float, default=None,
                    help="percent of units (implies --sample random)")
    ap.add_argument("--limit", type=int, default=0,
                    help="hard cap on units sent (0 = uncapped)")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--chapter", help="restrict to files starting with this")
    ap.add_argument("--root", type=Path,
                    default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--format", choices=("pretty", "jsonl"), default="pretty")
    ap.add_argument("--api", choices=("auto", "realtime", "bulk"),
                    default="auto",
                    help="auto (default): realtime for <= 10 units "
                         "($0.05/1k, seconds), bulk above ($0.04/1k, "
                         "queued minutes)")
    ap.add_argument("--wait", type=float, default=900.0,
                    help="seconds to wait for the bulk job (default 900)")
    ap.add_argument("--resume", default=None, metavar="BULK_ID",
                    help="fetch results of an already-submitted bulk instead "
                         "of resubmitting (rerun with identical flags/--seed)")
    args = ap.parse_args()

    key = os.environ.get("PANGRAM_API_KEY")
    if not key:
        raise SystemExit("pangram_check: set PANGRAM_API_KEY in the "
                         "environment (never commit it)")

    files = discover(args.root, args.chapter)
    if not files:
        raise SystemExit(f"pangram_check: no .tex files under {args.root}/latex/")
    units = build_units(files, args.unit)
    if not units:
        raise SystemExit("pangram_check: no prose units found")

    rng = random.Random(args.seed)
    if args.n is not None or args.pct is not None or args.sample == "random":
        rng.shuffle(units)
    if args.pct is not None:
        units = units[:max(1, math.ceil(len(units) * args.pct / 100))]
    elif args.n is not None:
        units = units[:args.n]
    if args.limit > 0:
        units = units[:args.limit]

    api = args.api
    if api == "auto":
        api = "bulk" if (args.resume or len(units) > AUTO_BULK_THRESHOLD) \
            else "realtime"
    rate = COST_BULK if api == "bulk" else COST_REALTIME
    total_words = sum(u.words for u in units)
    print(f"pangram_check: {len(units)} {args.unit} unit(s), "
          f"{total_words:,} words via {api} API, estimated cost "
          f"${total_words / 1000 * rate:.2f}", file=sys.stderr)

    try:
        if api == "bulk":
            results = classify_bulk(units, key, args.wait, args.resume)
        else:
            results = classify_realtime(units, key, args.wait)
    except (RuntimeError, urllib.error.URLError, OSError) as e:
        raise SystemExit(f"pangram_check: {api} request failed: {e}") from e

    rows = []
    for i, u in enumerate(units):
        r = results.get(i)
        if r is None or "_error" in r:
            err = (r or {}).get("_error", "no result returned")
            print(f"  {u.file}:{u.line} ERROR {err}", file=sys.stderr)
            continue
        row = {
            "file": u.file, "line": u.line, "words": u.words,
            "prediction": r.get("prediction_short"),
            "fraction_ai": r.get("fraction_ai"),
            "fraction_ai_assisted": r.get("fraction_ai_assisted"),
            "fraction_human": r.get("fraction_human"),
            "humanizer_max": max(
                [w.get("humanizer_score") or 0
                 for w in (r.get("windows") or [])] or [0]),
            "flagged_windows": [
                {"label": w.get("label"),
                 "score": round(w.get("ai_assistance_score", 0), 3),
                 "confidence": w.get("confidence"),
                 "words": w.get("word_count"),
                 "text": (w.get("text") or "")[:120]}
                for w in r.get("windows", [])
                if not (w.get("label") or "").startswith("Human")
            ],
        }
        rows.append(row)
        if args.format == "jsonl":
            print(json.dumps(row))
        else:
            frac = row["fraction_ai"] or 0.0
            assisted = row["fraction_ai_assisted"] or 0.0
            flag = "!" * (3 if frac >= 0.5 else 2 if frac >= 0.2
                          else 1 if frac + assisted > 0 else 0)
            print(f"{u.file}:{u.line}  {row['prediction'] or '?':6s} "
                  f"ai={frac:.2f} assisted={assisted:.2f} "
                  f"human={row['fraction_human'] or 0.0:.2f} "
                  f"({u.words}w) {flag}")
            for w in row["flagged_windows"]:
                print(f"   {w['label']} ({w['confidence']}, {w['score']}): "
                      f"“{w['text']}…”")

    if rows and args.format == "pretty":
        tw = sum(r["words"] for r in rows)
        wavg = lambda k: sum((r[k] or 0.0) * r["words"] for r in rows) / tw  # noqa: E731
        print()
        print(f"book (word-weighted over {len(rows)} unit(s)): "
              f"ai={wavg('fraction_ai'):.2f} "
              f"assisted={wavg('fraction_ai_assisted'):.2f} "
              f"human={wavg('fraction_human'):.2f}")
    print(f"pangram_check: {len(rows)}/{len(units)} unit(s) classified",
          file=sys.stderr)


if __name__ == "__main__":
    main()
