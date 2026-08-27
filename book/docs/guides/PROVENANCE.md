# PROVENANCE — Checking Whether the Book Contains Someone Else's Words

Two different risks get confused constantly. Keep them apart:

| | question | tool | what a bad result means |
|---|---|---|---|
| **Detectability** | does a classifier call this AI? | `make pangram` ([VOICE-MODELS.md](VOICE-MODELS.md)) | a style signal; no legal weight |
| **Provenance** | does my text contain phrasing from someone else's? | `scripts/phrase_check.py` (this guide) | a real publishing risk |

Provenance is the one with legal and ethical teeth. It is also the cheaper
check, and it comes back clean far more often — but when it doesn't, you
need to know before the book ships.

---

## 1. The tool: Ai2's infini-gram

[infini-gram](https://infini-gram.io) indexes trillion-token corpora in a
suffix array and counts how often an n-gram **of any length** occurs. No
API key, no cost, no published rate limit.

```bash
curl -X POST https://api.infini-gram.io/ -H "Content-Type: application/json" \
  -d '{"index":"v4_dclm-baseline_llama","query_type":"count",
       "query":"her heart skipped a beat"}'
# {"count": 35120, "latency": 18.4, ...}
```

Indexes worth knowing (full list:
[readthedocs](https://infini-gram.readthedocs.io/en/latest/api.html)):

| index | corpus | tokens |
|---|---|---|
| `v4_dclm-baseline_llama` | DCLM-baseline | 4.3T ← default here |
| `v4_olmo-mix-1124_llama` | OLMo-mix | 4.6T |
| `v4_rpj_llama_s4` | RedPajama | 1.4T |
| `v4_piletrain_llama` | Pile-train | 383B |

All are **web-derived**. A phrase lifted from a book that was never quoted
online will not appear — this check has a real blind spot for print-only
sources.

### Be polite — this is the operational rule, not a nicety

It is a free public research service. **Query serially with a delay.** We
ran 8–16 concurrent workers against it during development and were
`403 Forbidden`-ed within minutes (it cleared after a few). `phrase_check.py`
is deliberately serial, sleeps `--delay` (default 0.35 s) after every call,
exposes no concurrency flag, and aborts with an explanation on a 403.
Budget ~3 queries/sec: about a minute per 150 sampled spans.

Running a local index is not a realistic escape: DCLM is **33 TiB** on disk
(~$3,000 in S3 egress), RedPajama 8.9 TiB. The only credential-free download
is a 62 GiB Dolma sample — 500× smaller than the hosted index, which inverts
the metric's meaning, since in a tiny corpus everything looks unattested.

## 2. How to use it

**Spot-check a manuscript** — long spans are the signal:

```bash
uv run scripts/phrase_check.py                          # sample every file
uv run scripts/phrase_check.py --chapter ch03 -n 60     # deeper on one
uv run scripts/phrase_check.py --gram 10                # stronger evidence
```

**Look up one suspicious phrase** — the highest-value use, and the one that
broke the GrantaGate story open:

```bash
uv run scripts/phrase_check.py --phrase "the sour tang of fermenting"
```

Reading counts:

| count | reading |
|---|---|
| 0 | appears nowhere — normal, and the overwhelming majority of unpublished prose |
| 100+ | functional grammar (`"to doubt that it would turn into the"`, 81×) — ignore |
| 1–20 | **review**: distinctive wording attested elsewhere |

A low-count hit is a prompt to look, never a verdict. Real named things
legitimately recur: `"Wiki Wiki Shuttle bus at Honolulu International
Airport"` (12×) is the etymology of *wiki*, not borrowing.

## 3. What our books measured (2026-07-31)

128 sampled 8-word spans across four books (wiki-history, history-through-rfc,
legal-tech-history, ai-professional-services): **one** span attested anywhere,
and it was generic grammar at 81 hits. **No distinctive span matched — no
provenance concern found.** Caveats: a spot check, not an audit; one chapter
per book; verbatim reuse only, not paraphrase or structure.

## 4. Why we do NOT compute "rare-phrase coverage"

Ai2 and Stony Brook published a striking result
([blog](https://allenai.org/blog/infinigram-books),
[arXiv:2607.20349](https://arxiv.org/html/2607.20349)): among top-selling
Amazon self-published books, those with substantial detected AI text were
**43.2%** covered by "rare expressions" (≥5 words, in ≤5 Google Books
volumes **and** zero web hits) versus **37.6%** without, and award-winning
literature just **19.1%**.

We tried to reproduce it as a house metric and concluded it does not
transfer. Three reasons, all worth knowing before someone tries again:

1. **We cannot reproduce their definition.** Their "rare" requires ≤5 Google
   Books volumes *and* zero web hits — phrasing that exists in a *few books*,
   which is what makes it evidence of book-training-data regurgitation. We
   have no Google Books access, so the closest proxy is "zero hits anywhere,"
   which measures novel phrasing — nearly the opposite thing.
2. **It doesn't discriminate.** On that proxy our edited books (74–89%), a raw
   Claude draft (80%), and machine rewrites (79%) all landed in one band,
   within ~2 SE of each other.
3. **It's confounded by indexing exposure.** Moby Dick scored **0.0%** — it is
   *in* the corpus, so every phrase is attested. Any unpublished manuscript
   scores high for the same mechanical reason. Note this also plausibly
   inflates the paper's own headline gap: award-winning books are far more
   indexed and quoted online than recent self-published ones.

The direction of that metric is counterintuitive and easy to get backwards:
**more rare phrasing is not the human signal.** Award-winning literature had
the least of it.

What survives is the targeted check in §2 — long spans, low counts, human
review — which is the version worth keeping.
