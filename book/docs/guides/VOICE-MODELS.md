# VOICE-MODELS — Local Author-Voice Rewrite Models for De-Slopping

How to choose, serve, and safely use a local "voice model" — a text→text
rewriter that takes AI-flavored or rough prose and returns it in the
author's voice — as the engine behind `scripts/deslop.py` (REVIEW-QA §7's
detector-guided de-slop pass). Everything here is machine-independent; the
reference deployment this was measured on is described at the end.

The role is fixed regardless of model: **ideation and fix briefs, never
auto-editing.** Rewrites are quarries; the faithfulness guards in
`deslop.py` exist because every model below fails in the ways §4 lists.

---

## 1. Choosing a model — measured findings

Two viable architectures, with a real trade-off (all numbers measured
2026-07 on real book paragraphs; "Pangram" = external AI-detector
fraction-AI, lower reads more human; "invention" = facts added that were
not in the original):

| approach | voice match | invention | notes |
|---|---|---|---|
| **LoRA fine-tune of a ~4B base** on the author's corpus | best | higher (≈15% on a deep eval; 0 flagged on an 8-paragraph spot bench) | A 4B base is enough — bigger bases and more epochs measured *no better*. Q4_K_M quant is quality-identical to f16 for tuned models. |
| **Prompt-only large instruct model** (no custom weights) | good | lowest at full precision | Fine-tuning on dense, fact-rich prose *reintroduces* invention (measured: SFT took a clean base from 0%→15%). Quantization erodes the faithfulness edge: bf16 0% → Q8_0 5% → Q4_K_M 10% — **serve prompt-only models at Q8_0 or better.** |

Head-to-head on the 8-paragraph bench (4 detector-flagged, 2 stylized,
2 raw-draft; typography confound controlled):

| model class | tok/s* | Pangram (originals 0.75) | outcome |
|---|---|---|---|
| 4B author fine-tune (Q4) | ~160 | **0.38** | led every axis at once |
| ~26B MoE instruct, prompt-only (Q5) | ~110 | **0.38** | best prompt-only option |
| ~31B dense instruct, prompt-only (Q5) | ~25 | 0.38 | same score, 6× slower, compresses hardest |
| ~12B instruct QAT (Q4) | ~58 | 0.62 | middle |
| ~5-8B instruct, prompt-only (Q8) | ~83 | 0.75 | did not move the detector |
| 20B reasoning-first MoE | ~150 | 0.88 | **anti-suited** — leaves slop, raises detector scores |

Rules of thumb from the table:
- A fine-tune on the actual author's corpus beats scale.
- Without a fine-tune, use the largest *instruct* model that fits at Q5+;
  below ~10B prompt-only doesn't move detector scores.
- Never use reasoning-tuned models (gpt-oss-class) as rewriters.
- **The candidate loop beats model choice**: sampling 3 variants and
  scoring them (`deslop.py --candidates 3`) surfaced 0.00-AI rewrites even
  from models whose single-shot average didn't move.

## 1a. Pangram 4 changed the target (2026-07)

Pangram 4 ([arXiv:2607.27183](https://arxiv.org/abs/2607.27183)) is ~6x
larger than v3, classifies at **clause resolution with full-document
context**, and adds humanizer detection (97.67% of commercially "humanized"
text still caught). API note: `GET /models` lists what your key may use and
requests must name one (`"model": "pangram-4"`); v3 is deprecated
2026-09-30. Cache detector verdicts **keyed by model version** — v3 and v4
disagree constantly.

Measured on 8 real paragraphs (weighted-AI = fraction_ai + 0.5x
fraction_ai_assisted; baseline 0.875):

| tier | what it does | weighted-AI |
|---|---|---|
| 1. deterministic | contractions, filler-transition removal | **0.875 (no change)** |
| 2. + trained models | nupunkt rhythm surgery, OpenGloss de-synonymization | **0.875 (no change)** |
| 3-4. sampling + detector selection | best-of-3, plain prompt | 0.697 |
| 5. + few-shot exemplars | real author paragraphs as style samples | 0.625 |
| + compound second pass | rewrite the winner again | 0.562 |
| + model diversity | pool candidates across 2-3 different models | 0.500 |
| 6. + notes reconstruction | extract facts, write fresh prose from notes | 0.417 |
| + wide pool (14 candidates x 2 rounds) | everything above, more samples | **0.312** |

Five findings that should shape any pipeline:

1. **Deterministic edits do nothing.** Contractions, transition removal,
   rhythm surgery, synonym flattening: zero movement on every paragraph.
   v4 reads clause structure with document context; surface edits don't
   touch it. Keep tiers 1-2 for *craft* reasons, not for detector scores.
2. **Sampling variance plus scoring is the workhorse.** The same prompt at
   three temperatures produces candidates spanning 0.00-1.00. The pipeline's
   job is to generate widely and let the detector pick.
3. **Exemplar selection beats prompt wording.** Few-shot with paragraphs the
   *detector already reads as human* transfers; few-shot with merely
   low-slop paragraphs does not. `deslop.py --fewshot` therefore scores
   candidate exemplars (cached) and picks the most-human.
4. **Notes reconstruction is the only tier that moves locked paragraphs.**
   Extract the facts deterministically, then write fresh prose from the
   notes. Rewriting edits token lineage; writing from notes replaces it.
   Highest invention risk — the faithfulness guards matter most here.
5. **Model diversity is a real lever.** Pooling candidates from two or three
   different models beats any single model's wider pool
   (`deslop.py --servers`).

What stays stubborn: heavily stylized prose (anaphora, direct address) and
dense factual narration, where guards reject most candidates because there
is no room to restructure without inventing or dropping. Humanizer scores
stayed ~0.00-0.11 throughout, i.e. none of this trips v4's
humanizer-detection head — it is rewriting, not evasion.

**Honest caveat:** these are best-of-N numbers on a small eval. The claim is
"the pipeline reliably finds a low-scoring faithful variant," not "any
single rewrite scores 0.31." A one-model, 9-candidate run on the five
hardest paragraphs reached 0.70; the full 14-candidate multi-model campaign
reached ~0.34 on those same five.

## 1b. Measurement is the hard part (2026-07-29, second study)

Four corrections to §1a, found by reading the technical report closely and
testing its architectural claims. Each invalidated something we believed.

**The score we ranked on was 1-bit.** `fraction_ai` is a word-weighted
average of *hard* segment labels, so a single-paragraph submission (one
window) can only return 0.0 or 1.0 — **97% of our cached single-paragraph
verdicts were saturated**, and windows scoring 0.56 and 0.64 both reported
`fraction_ai = 1.0` while 0.33 reported "Human". The continuous signal,
`windows[*].ai_assistance_score`, was sitting unused in the same response.
Rank on its token-weighted mean (`deslop.py` now does). Practical
constants on our corpus: **label boundary ≈ 0.37**, and the scale
**saturates above ~0.98** — a paragraph at 0.99 cannot be measured
improving until it moves a long way. Re-measured on the continuous signal,
the §1a campaign reads **0.878 → 0.410**, with 4 of 8 paragraphs crossing
the boundary. Much of the "sampling variance" reported in §1a was
quantization noise.

**Isolated wins do not survive context.** A rewrite scoring 0.00 alone
scored **1.00 when placed back between its original neighbours**. The
report describes a CRF over segment labels with a smoothness penalty:
same-label transitions are free, changes are charged. One human paragraph
inside an AI run pays the boundary toll twice and gets smoothed away. Score
candidates the way the book will be read, not in isolation.

**Wins do not aggregate either.** Three rewrites scoring 0.00 / 0.00 / 0.00
individually scored **1.00 concatenated** (0.54 as a pair). More text gives
the detector more evidence of a shared emitter. Per-paragraph optimization
overstates what a chapter will score.

**Rewriting the whole block at once does not fix it.** Ten block-level
candidates across two models and three prompt modes: all 1.00. The unit
mismatch is not solved by simply enlarging the unit.

**A free local proxy did not work.** Per-token surprisal from a small local
model (the DetectGPT/Binoculars idea — mean NLL, p95, shock rate, flat
rate, dull-clause rate) showed **|r| ≤ 0.20 against Pangram verdicts on 20
labelled texts**, with human and AI group means nearly identical. Known-human
Melville and raw slop scored the same. Cheap pre-filtering to lift the
candidate ceiling is therefore *not* available by this route; the detector
is supervised and is not keying on plain perplexity.

**Why notes-reconstruction works — and why to distrust it.** The detector's
AI training class is built by *topic-prompt regeneration*, with near-verbatim
copies discarded. That deliberately excavates a hole where *grounded,
particular-dense generation* lives — which is exactly what notes-reconstruction
produces. It is a distribution-shift exploit, not a quality result: it will
close if a future version adds grounded generation to the AI class. The
same lexical distance that moves the score is what causes invention, so the
gain and the risk are one variable. Idea quarry, never paste-in.

## 2. Serving (llama.cpp)

```bash
llama-server -m <model>.gguf --host 127.0.0.1 --port 8091 \
  -ngl 99 -c 8192 --jinja --alias voice
```

- `deslop.py` probes `127.0.0.1:8091` then `:8092` (override with
  `--server-url` / `DESLOP_SERVER_URL`); model name is read from
  `/v1/models`. Auto-start via `DESLOP_LLAMA_SERVER` + `DESLOP_MODEL`.
- Hybrid-SSM/GDN bases (e.g. Qwen3.5's Gated DeltaNet) need a **CUDA**
  llama.cpp build — they hang on Vulkan and some vLLM versions reject them.
  Standard architectures serve anywhere.
- Models larger than one GPU split automatically across cards
  (`CUDA_VISIBLE_DEVICES=0,1`, one server).
- Models with integrated thinking modes need it off per request:
  `"chat_template_kwargs": {"enable_thinking": false}` (deslop sends this).

## 3. Generation settings and the prompt

Sample, don't beam: **temperature 0.7–0.8, top_p 0.9** — greedy decoding
over-compresses and reads *more* machine-like. Feed **paragraphs of
40–180 words**; lone sentences and slogans are out-of-distribution (models
over-compress or go chatty). The canonical prompt (in `deslop.py`):

> Rewrite the following passage in the author's voice: direct, understated,
> concrete, technically precise. Remove all AI-slop tells. Preserve the
> facts exactly — add no fact, name, or number not in the original.
> Output only the rewrite.

Do **not** append instruction lists (measured problems, style checklists):
models over-obey any added instruction — outputs compress ~30% and
detector scores don't improve. Diagnosis belongs in the brief for the
human, not in the prompt (`deslop.py --diagnose` docstring records this
negative result).

## 4. Failure modes → guards

All observed on real manuscripts; this is why `deslop.py` scores every
rewrite before you see it:

| failure | example (real) | guard |
|---|---|---|
| Invention | "Edison" → "Thomas Edison" (benign) up to fabricated names | invented-facts diff (numbers + proper nouns + dotted identifiers) |
| Dropped content | `comp.lang.lisp` silently deleted, leaving a broken sentence | dropped-facts diff |
| Over-compression | 60-word paragraph → 10-word sentence | length-ratio bound (<0.5 flagged) |
| Meaning drift | "was about to swallow" → "had swallowed"; remembrance framing → "an apology" | not mechanically catchable — the §7 human safety net is mandatory |
| Lexical cleanup ≠ detectability | all slop words removed, detector still 1.00 (rhythm unchanged) | slop-delta + Pangram scoring in `--candidates` |
| Typography confound | `---` vs `—` flips detector verdicts on identical text | all scorers normalize to published typography first |

Yield is low on polished prose — zero edits is a valid outcome. On a
hand-polished prologue, 2 of 5 applied rewrites carried meaning changes:
run whole-file applies only under git and review the diff paragraph by
paragraph.

## 5. Training your own fine-tune (summary)

A LoRA SFT over ~15 years of the author's writing on a 4B base, trained on
a 2×16GB-consumer-GPU workstation, reached the numbers above. Bigger bases
and longer training measured no better on voice or slop; they did not fix
invention (that's inherent to tuning on fact-dense prose — budget for the
guards instead). Keep the adapters so you can re-merge/re-quant against
newer bases.

## 6. Reference deployment (example, not a dependency)

The setup these numbers come from: `/data0/models/voice-deslop/` on the
author's workstation — `Qwen3.5-4B-voice.Q4_K_M.gguf` (fine-tune, port
8091, the default) and `gemma-4-E4B-it-Q8_0.gguf` (prompt-only fallback,
port 8092), with LoRA adapters and a README carrying both bench
addenda (v3 model comparison, and the v4 measurement findings summarized in
§1b). Nothing in the template requires that machine: point
`DESLOP_SERVER_URL` at any OpenAI-compatible endpoint serving any model
that satisfies §1.
