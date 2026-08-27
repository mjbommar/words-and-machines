#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pydantic>=2.7",
#     "pydantic-ai-slim[openai,anthropic,google]>=1.0",
#     "pyyaml>=6.0",
# ]
# ///
"""Rewrite a LaTeX chapter through one or more LLMs, on raw pydantic-ai.

The prose problem this exists for: every style gate in this repo passed on a
draft the author called unpublishable. Gates catch tells; they cannot hear
voice. This runs a chapter through a model with the project's own guidance and
a named anchor-author set, so drafts can be compared side by side.

USAGE

    # one model
    uv run scripts/rewrite_chapter.py latex/chapters/ch01-getting-started.tex -m opus5

    # every configured model, into out/rewrites/<stamp>/
    uv run scripts/rewrite_chapter.py latex/chapters/ch01-getting-started.tex --all

    # swap the anchor authors (sets live in scripts/rewrite_chapter.yaml)
    uv run scripts/rewrite_chapter.py CH.tex --all --anchors my-bench

    # this book's own brief, with the subject statement kept out of it
    uv run scripts/rewrite_chapter.py CH.tex -m opus5 \
        --brief-file docs/guides/briefs/voice.md --direction "$(cat brief-subject.txt)"

    # see the exact prompt without spending a token
    uv run scripts/rewrite_chapter.py CH.tex --dry-run

CONFIGURATION

    scripts/rewrite_chapter.yaml, if present, overrides MODELS and ANCHOR_SETS.
    --config PATH points elsewhere. See --write-config for a starting file.

KEYS (from the environment; nothing is read from disk)

    OPENAI_API_KEY · ANTHROPIC_API_KEY · GEMINI_API_KEY / GOOGLE_API_KEY
    OPENROUTER_API_KEY   <- GLM and DeepSeek route through here

GUARDRAILS

    A rewrite pass is exactly where a fabrication gets into a sourced book, so
    the checks run INSIDE the retry loop: a failing sample is re-requested
    (twice), and a chapter that never passes keeps its original text. A chapter
    is never overwritten with itself.

    Blocking — invented \\autocite key; invented quotation (>=6 words inside
    quotes that are absent from the source); invented year or deep-time
    duration; an anchor author named in the prose; >=50% of paragraphs
    unchanged (a no-op dressed as a rewrite).

    Advisory — dropped source keys, and any quantity or <number><unit>
    measurement the source lacks. Both print; neither rejects.

    Every rejected sample is still written to <stem>.<model>.REJECTED.tex, with
    the offending sentence printed. This is not optional politeness: the year
    check cannot tell a fabricated date from correct arithmetic on the source's
    own "a hundred and thirty-eight years later", and discarding the text meant
    one false positive cost 3,497 words. A rejection is a claim to adjudicate,
    not a verdict.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

# --------------------------------------------------------------------------
# Models. provider drives which settings object is built; see build_settings.
# --------------------------------------------------------------------------

MODELS: dict[str, dict] = {
    "gpt56": {
        "model": "openai:gpt-5.6",
        "provider": "openai",
        "reasoning": "high",          # none|low|medium|high|xhigh|max
        "env": "OPENAI_API_KEY",
        "label": "OpenAI GPT-5.6",
    },
    "opus5": {
        "model": "anthropic:claude-opus-5",
        "provider": "anthropic",
        "effort": "high",             # adaptive thinking; Opus 5 rejects budgets
        "env": "ANTHROPIC_API_KEY",
        "label": "Anthropic Opus 5",
    },
    "gemini37": {
        "model": "google:gemini-3.7-flash",
        "provider": "google",
        "thinking_level": "high",     # low|medium|high  (3.7 rejects minimal)
        "max_tokens": 65536,          # Flash ceiling unconfirmed; kept conservative
        "env": "GEMINI_API_KEY",
        "env_alt": "GOOGLE_API_KEY",
        "label": "Google Gemini 3.7 Flash",
    },
    "glm52": {
        "model": "openrouter:z-ai/glm-5.2",
        "provider": "openrouter",
        "reasoning": "high",
        "env": "OPENROUTER_API_KEY",
        "label": "Z.ai GLM 5.2 (via OpenRouter)",
    },
    "deepseek": {
        "model": "openrouter:deepseek/deepseek-v4-pro",
        "provider": "openrouter",
        # V4 Pro's effective scale is high | xhigh (xhigh -> the native "max");
        # low and medium are aliased up to high, so "high" is the FLOOR of this
        # model's range, not the ceiling. At high it echoed the source verbatim
        # on 3 of 4 chapters, twice after spending real reasoning tokens.
        "reasoning": "xhigh",
        "env": "OPENROUTER_API_KEY",
        "label": "DeepSeek V4 Pro (via OpenRouter)",
    },
}

# Prose rewriting under hard factual constraints: enough looseness to actually
# rewrite, not so much that it drifts off the source. Inert on two of the five
# providers (see the quirks note below), so reasoning effort is the real dial.
DEFAULT_TEMPERATURE = 0.7
# 128k is the documented output ceiling on GPT-5.6 and Opus 5. This must be
# generous: reasoning tokens count against it, and a chapter rewrite is only
# ~4k tokens of prose. In the first five-model run GLM 5.2 spent 26k tokens
# thinking and came within 1,700 of a 32k cap — a near miss that would have
# silently truncated a longer chapter. Override per model where a provider's
# ceiling is lower.
DEFAULT_MAX_TOKENS = 128000

# A model that returns the source is not a rewrite. Retry instead of accepting.
# Calibrated on real runs: genuine rewrites land at 11-26% of paragraphs kept,
# no-ops at 70-100%. 90 was too lenient and let a 70% pass through as success.
NOOP_KEPT_PCT = 50.0
NOOP_RETRIES = 2

# Provider quirks worth knowing before you tune anything:
#   OpenAI   reasoning models ignore temperature and warn about it.
#   Anthropic requires temperature=1 while extended thinking is enabled.
#   Gemini 3.7 rejects thinking_level="minimal"; low|medium|high only.
# So temperature is close to a no-op on three of the five. Change reasoning
# effort, not temperature, when you want different output.

# --------------------------------------------------------------------------
# Anchor authors. Two sample sets ship, to show the shape; every book should
# define its own in scripts/rewrite_chapter.yaml (see --write-config).
# Keep each entry to take / do-not-take. Long descriptions dilute.
#
# THE BENCH SETS THE TEMPERATURE, and this is the choice that decides whether
# the output is usable. A bench of reticent writers produces a competent,
# inventorial report no matter what the brief asks for — measured on one
# chapter across four briefs and three providers, where the reticent bench came
# back flatter and more technical than the source it was given, and reached for
# invented connective colour to compensate. Prohibitions ("do not console the
# reader", "cut every summarising sentence") are obeyed hard and reliably, so a
# brief made of them yields prose with the warmth edited out. If the register
# you want is warm, defiant or proud, no rule will get you there: name authors
# who wrote that way and let the bench carry it.
# --------------------------------------------------------------------------

ANCHOR_SETS: dict[str, dict] = {
    "reportage": {
        "note": "SAMPLE. Technical or historical material carried by people "
                "rather than explained by a narrator. Cool register — read the "
                "note above before choosing it for a book that wants heat.",
        "authors": [
            ("John McPhee, *Annals of the Former World*",
             "Technical material carried by a person instead of explained by a "
             "narrator. TAKE the reportage. DO NOT take the affect — his "
             "reticence is affordable only because he reports first."),
            ("John Hanson Mitchell, *Ceremonial Time*",
             "A way of seeing installed before the deep time arrives, so the "
             "reader wants it rather than endures it. Keep the willingness to "
             "let a place be uncanny."),
            ("Adam Nicolson, *Sea Room*",
             "Seams hidden. Move from weather to a sixteenth-century chieftain "
             "inside two pages with no heading to notice."),
            ("Seamus Heaney, the bog poems",
             "Ground that keeps things, and names that hold them. He never "
             "explains what a name costs; he puts it in your hand."),
            ("Tim Robinson, *Stones of Aran*",
             "The charge — a word on stone as a human act. DO NOT take the "
             "completeness; his method is to record everything and readers "
             "call it penitential."),
            ("Barry Lopez, *Arctic Dreams*",
             "Awe with moral weight; landscape as an actor with its own "
             "indifference. Reverence and precision are the same discipline."),
            ("Annie Dillard",
             "No flinching at either terror or beauty."),
            ("Wallace Stegner, *Wolf Willow*",
             "Small in a big country, and staying. Survival as defiance, not "
             "consolation."),
        ],
    },
    "endurance": {
        "note": "SAMPLE, and the counterweight to 'reportage'. For a subject "
                "that was pushed around by larger forces and stayed: warm, "
                "unsentimental, proud. Measured against the reportage bench on "
                "the same chapter, this one was the only bench that kept the "
                "book's closing movement instead of trimming it to a tableau.",
        "authors": [
            ("Eduardo Galeano, *Memory of Fire*",
             "Short hot fragments, each one a transfer of power, dated and "
             "concrete, and he never tells you how to feel about it. TAKE the "
             "heat and the compression."),
            ("John Berger, *Pig Earth*",
             "The dignity of people the economy is grinding, carried entirely "
             "by their work. Pride is a thing done, never an adjective."),
            ("N. Scott Momaday, *The Way to Rainy Mountain*",
             "A people carried through dispossession by the names of the "
             "ground. Incantation earned by particulars, never asserted."),
            ("Wallace Stegner, *Wolf Willow*",
             "Small in a big country, and staying. Survival as defiance, not "
             "consolation."),
            ("Norman Maclean, *Young Men and Fire*",
             "Grief and technical precision inside one sentence, with no seam "
             "showing. DO NOT take the first-person memoir frame unless the "
             "book already has one."),
        ],
    },
}

DEFAULT_ANCHORS = "reportage"

# Project guidance pulled in verbatim, in this order, truncated per file.
GUIDE_FILES = [
    ("docs/VOICE.md", 22000),
    ("docs/guides/LEXICON.md", 14000),
]

# --------------------------------------------------------------------------
# Prompt
# --------------------------------------------------------------------------

# The brief. This is the whole stylistic instruction, and it is deliberately
# short.
#
# The first version of this script shipped a 39,000-character prompt: hard
# constraints, an eight-author anchor bench with take/do-not-take notes, and
# the full text of VOICE.md and LEXICON.md — declared to *outrank* the anchors.
# Five models ran it. On the one paragraph most open to reinterpretation (an
# 1849 survey plat converting an island into property) one model changed
# nothing, two changed an em-dash, and one changed "at Detroit" to "in
# Detroit". Twenty thousand words of guidance produced copyediting, because
# guidance that specific leaves nothing to decide, and because the constraints
# forbade the very moves the anchors are made of.
#
# So: say what the book is about, name the voices, and get out of the way. The
# mechanical floor below is four lines, and the citation/quantity guardrails in
# this script enforce the factual discipline the old prompt tried to argue for.

BRIEF = """\
Rewrite this chapter as if Harari and Graeber and Bryson coauthored it, with a
little García Márquez.

Always remember that the theme of the book is the web of relationship among
natural forces, human forces, and between them. The symbolism of change and
erosion, of smallness relative to a larger force, yet of a strong solitude and
permanence despite it all must remain.
"""

MECHANICS = """\
Return the complete chapter as LaTeX and nothing else — no preamble, no
commentary, no code fence. Keep \\chapter and \\label. Use only commands the
source already uses.

Keep every \\autocite key exactly as it appears; move a key with the claim it
supports, never invent one. Do not invent facts, dates, numbers or quotations,
and do not reword text inside quotation marks — everything else is yours.

Never name the authors above, or any writer, in the prose. They are models for
how to write, not people this book mentions.
"""

# The old apparatus, kept for --guidance full.
TASK_RULES = MECHANICS + """
You may restructure, reorder, cut, compress and rewrite freely within those
constraints. Cutting is welcome — the argument sets the length, not a target.
"""


def read_guide(root: Path) -> str:
    parts = []
    for rel, limit in GUIDE_FILES:
        p = root / rel
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        if len(text) > limit:
            text = text[:limit] + "\n\n[…truncated…]\n"
        parts.append(f"===== {rel} =====\n{text}")
    return "\n\n".join(parts)


def render_anchors(name: str, sets: dict) -> str:
    spec = sets.get(name)
    if not spec:
        raise SystemExit(f"unknown anchor set {name!r}; have {sorted(sets)}")
    lines = [f"ANCHOR AUTHORS — {name}", spec.get("note", ""), ""]
    for who, how in spec["authors"]:
        lines.append(f"* {who}\n    {how}")
    lines.append(
        "\nThese are models for a MOVE, not lines to imitate. Do not write a "
        "sentence that sounds like a pastiche of any of them, and never name "
        "them in the prose."
    )
    return "\n".join(lines)


def build_system_prompt(root: Path, anchors: str, sets: dict,
                        extra: str | None, guidance: str = "brief",
                        brief: str | None = None) -> str:
    """brief (default) = the direction and a four-line mechanical floor.
    full = the original apparatus: anchors + VOICE.md + LEXICON.md."""
    if guidance == "brief":
        blocks = [brief or BRIEF, MECHANICS]
        if extra:
            blocks.append(extra)
        return "\n\n".join(blocks)

    blocks = [TASK_RULES, render_anchors(anchors, sets)]
    guide = read_guide(root)
    if guide:
        blocks.append(
            "PROJECT STYLE GUIDANCE — this governs, and outranks the anchor "
            "authors where they conflict.\n\n" + guide
        )
    if extra:
        blocks.append("ADDITIONAL DIRECTION FROM THE AUTHOR\n\n" + extra)
    return "\n\n" + ("\n\n" + "-" * 70 + "\n\n").join(blocks)


# --------------------------------------------------------------------------
# Citation guardrail
# --------------------------------------------------------------------------

CITE_RE = re.compile(r"\\(?:auto|paren|foot|text)?cite[a-z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}")


def cite_keys(tex: str) -> set[str]:
    out: set[str] = set()
    for m in CITE_RE.finditer(tex):
        for k in m.group(1).split(","):
            k = k.strip()
            if k:
                out.add(k)
    return out


# Quantities. A rewrite must not introduce a measurement the source lacks.
# Caught in testing: a model turned "the water beside it" into "the water
# thirty paces out". No citation key was invented, so the key check passed.
NUMWORDS = {
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
    "sixty", "seventy", "eighty", "ninety", "hundred", "thousand", "million",
    "billion", "dozen", "half", "quarter", "third",
}
NUM_RE = re.compile(r"\d[\d,]*(?:\.\d+)?")
WORD_RE = re.compile(r"[A-Za-z]+")


def quantities(tex: str) -> set[str]:
    body = re.sub(r"\\autocite[^}]*\}", " ", tex)      # keys carry digits
    found = {n.replace(",", "") for n in NUM_RE.findall(body)}
    found |= {w.lower() for w in WORD_RE.findall(body) if w.lower() in NUMWORDS}
    return found


# A bare-number check is not enough. Two different models turned "the water
# beside it" into "the water thirty paces out", and "thirty" was already in the
# source ("thirty-four feet high"), so the number-set diff stayed silent. What
# changed was the UNIT the number was attached to. Compare measurement pairs.
UNITS = (r"paces?|steps?|feet|foot|yards?|miles?|inch(?:es)?|metres?|meters?|"
         r"km|kilometres?|kilometers?|acres?|fathoms?|cords?|tons?|pounds?|lbs?|"
         r"minutes?|hours?|days?|weeks?|months?|years?|decades?|centuries?")
MEASURE_RE = re.compile(
    r"\b((?:\d[\d,]*(?:\.\d+)?|" + "|".join(sorted(NUMWORDS, key=len, reverse=True)) +
    r")(?:[- ](?:and[- ])?(?:" + "|".join(sorted(NUMWORDS, key=len, reverse=True)) +
    r"))*)[\s-]+(" + UNITS + r")\b", re.IGNORECASE)


# Naming the anchors in the prose is the loudest tell there is, and it happened:
# DeepSeek V4 Pro produced "Stories, as Harari would note…", "Graeber would
# recognize this…", and "like a García Márquez novel…" — the model citing its
# own style instruction inside the book. Telling it not to is necessary but not
# sufficient, so the check lives here too and derives the names from whatever
# brief is in use rather than a hardcoded list.
BRIEF_STOP = {"rewrite", "always", "the", "this", "a", "an", "and", "with",
              "chapter", "return", "keep", "never", "do", "use", "it", "they"}

# A bench entry: a bullet whose line opens with the author's name, then a comma.
#   * Wallace Stegner, Wolf Willow. Small in a big country, and staying.
BENCH_LINE = re.compile(r"^\s*[*\-•]\s*([A-ZÀ-Þ][^,.\n]*)", re.M)


def anchor_names(brief: str, source: str) -> set[str]:
    """Author surnames the brief benches, which the prose must never name.

    Scoped to bench-entry lines when the brief has them, and only then falling
    back to bare capitalised words. That scoping is the whole point: the old
    behaviour was "every capitalised word in the brief the source lacks", which
    silently made the book's own subject matter contraband. A tone brief reading
    "the Ojibwa, the French, the Mormons and the Irish" banned *Mormons* — a word
    chapter 1 happens never to use — and rejected three consecutive samples,
    discarding 3,497 words of output for a rule nobody had written.

    A brief that describes the book is the normal case, not the exotic one. Only
    a name the brief actually puts on the bench can leak from the bench.
    """
    src_words = {w.lower() for w in re.findall(r"[A-Za-zÀ-ÿ]+", source)}

    bench = BENCH_LINE.findall(brief)
    if bench:
        candidates = [w for entry in bench
                      for w in re.findall(r"\b([A-ZÀ-Þ][a-zà-ÿ]{3,})\b", entry)]
    else:
        # No bench lines: fall back to capitalised words, minus the ones that
        # are capitalised only because a sentence started there. That alone
        # clears Erosion, Pride, Whatever, Write and Assign out of two briefs
        # written for this book. The fallback is still best-effort and cannot
        # tell a benched author from a named people mid-sentence — so put the
        # bench in bullets, which is what the shipped anchor sets do.
        candidates = re.findall(r"(?<![.!?]\s)(?<!^)\b([A-ZÀ-Þ][a-zà-ÿ]{3,})\b",
                                brief, re.M)

    return {w for w in candidates
            if w.lower() not in BRIEF_STOP and w.lower() not in src_words}


def name_leaks(brief: str, source: str, out: str) -> set[str]:
    names = anchor_names(brief, source)
    if not names:
        return set()
    pat = re.compile(r"\b(" + "|".join(re.escape(n) for n in names) + r")\b")
    return set(pat.findall(out))


# The worst failure this tool can produce, and it happened — on a history book
# built from this template, DeepSeek attributed to a real 1854 pamphlet a
# sentence dating an event to 1611 that appears nowhere in it. The citation-key
# check passed, because the model reused a legitimate key and invented the
# claim around it. A key check verifies the label, never the claim, so
# quotations are checked directly against the source.
QUOTE_RE = re.compile(r"``(.+?)''", re.S)


def _norm(t: str) -> str:
    """LaTeX-insensitive comparison form. Collapse whitespace LAST: replacing
    punctuation with spaces creates new runs, and a needle joined on single
    spaces never matches a haystack that still has doubles."""
    t = re.sub(r"\\[a-zA-Z]+\*?", " ", t)      # LaTeX commands
    t = t.lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)          # everything else -> space
    return t.strip()


def invented_quotes(source: str, out: str, min_words: int = 6) -> list[str]:
    """Quoted passages in the output whose wording is not in the source."""
    src = _norm(source)
    bad = []
    for q in QUOTE_RE.findall(out):
        words = _norm(q).split()
        if len(words) < min_words:
            continue                      # short quotes get reworded legitimately
        # look for any 6-word run of the quote in the source
        if not any(" ".join(words[i:i + 6]) in src
                   for i in range(len(words) - 5)):
            bad.append(q.strip()[:110])
    return bad


def kept_percent(source: str, out: str) -> float:
    """Share of output paragraphs byte-identical to a source paragraph.

    The most useful single number here. In the first five-model run, DeepSeek
    V4 Pro returned 98% of the source unchanged after 263 seconds and 24,644
    output tokens, and GLM 5.2 returned 83%. Both reported success. A model
    that hands the input back is not a rewrite, and nothing else in this
    script's output distinguishes that case from a good one.
    """
    src = {p.strip() for p in source.split("\n\n") if p.strip()}
    paras = [p.strip() for p in out.split("\n\n") if p.strip()]
    if not paras:
        return 0.0
    return 100.0 * sum(1 for p in paras if p in src) / len(paras)


def measures(tex: str) -> set[str]:
    body = re.sub(r"\\autocite[^}]*\}", " ", tex)
    out = set()
    for m in MEASURE_RE.finditer(body):
        num = re.sub(r"\s+", " ", m.group(1).lower().replace("-", " ")).strip()
        out.add(f"{num} {m.group(2).lower().rstrip('s')}")
    return out


@dataclass
class Result:
    key: str
    label: str
    ok: bool
    text: str = ""
    error: str = ""
    seconds: float = 0.0
    in_tokens: int = 0
    out_tokens: int = 0
    invented: set[str] = field(default_factory=set)
    dropped: set[str] = field(default_factory=set)
    leaked: set[str] = field(default_factory=set)
    fake_quotes: list[str] = field(default_factory=list)
    new_quantities: set[str] = field(default_factory=set)
    kept_pct: float = 0.0        # % of output paragraphs identical to source


# --------------------------------------------------------------------------
# Model settings per provider
# --------------------------------------------------------------------------

def build_settings(spec: dict, temperature: float, max_tokens: int):
    """Return a provider-appropriate settings object.

    Falls back to plain ModelSettings when a provider-specific class or field
    is unavailable in the installed pydantic-ai, so a version bump degrades to
    working-without-reasoning rather than crashing.
    """
    from pydantic_ai.settings import ModelSettings

    max_tokens = int(spec.get("max_tokens", max_tokens))
    base = {"temperature": temperature, "max_tokens": max_tokens}
    provider = spec["provider"]

    try:
        if provider == "openai":
            from pydantic_ai.models.openai import OpenAIResponsesModelSettings
            return OpenAIResponsesModelSettings(
                openai_reasoning_effort=spec.get("reasoning", "high"), **base)

        if provider == "anthropic":
            from pydantic_ai.models.anthropic import AnthropicModelSettings
            # Opus 5 rejects {'type':'enabled','budget_tokens':N} and requires
            # adaptive thinking plus an effort level. Older Claude models take
            # the budget form, so honour thinking_budget when it is set.
            # Anthropic also requires temperature=1 while thinking is enabled.
            if spec.get("thinking_budget"):
                return AnthropicModelSettings(
                    anthropic_thinking={"type": "enabled",
                                        "budget_tokens": int(spec["thinking_budget"])},
                    temperature=1.0, max_tokens=max_tokens)
            return AnthropicModelSettings(
                anthropic_thinking={"type": "adaptive"},
                anthropic_effort=spec.get("effort", "high"),
                temperature=1.0, max_tokens=max_tokens)

        if provider == "google":
            from pydantic_ai.models.google import GoogleModelSettings
            return GoogleModelSettings(
                google_thinking_config={
                    "thinking_level": spec.get("thinking_level", "high")},
                **base)

        if provider == "openrouter":
            from pydantic_ai.models.openrouter import OpenRouterModelSettings
            return OpenRouterModelSettings(
                openrouter_reasoning={"effort": spec.get("reasoning", "high")},
                **base)
    except Exception as e:  # noqa: BLE001 - degrade, do not abort
        print(f"  note: provider settings unavailable ({e}); using plain "
              f"ModelSettings", file=sys.stderr)

    return ModelSettings(**base)


def have_key(spec: dict) -> str | None:
    for name in (spec.get("env"), spec.get("env_alt")):
        if name and os.environ.get(name):
            return name
    return None


def run_model(key: str, spec: dict, system: str, source: str,
              temperature: float, max_tokens: int,
              brief_text: str = "") -> Result:
    from pydantic_ai import Agent

    label = spec.get("label", key)
    env = have_key(spec)
    if not env:
        return Result(key, label, False,
                      error=f"no API key ({spec.get('env')})")

    settings = build_settings(spec, temperature, max_tokens)
    agent = Agent(spec["model"], instructions=system, model_settings=settings)

    # DeepSeek V4 Pro will spend 15,000 reasoning tokens and then emit the
    # source verbatim. It is not deterministic: the same chapter no-opped on one
    # run and rewrote properly on the next. So a near-identical return is
    # treated as a failed attempt and retried, not accepted.
    t0 = time.monotonic()
    text, secs, run = "", 0.0, None
    for attempt in range(1, NOOP_RETRIES + 2):
        try:
            run = agent.run_sync(
                "Rewrite the chapter below. Return only the LaTeX.\n\n" + source)
        except Exception as e:  # noqa: BLE001
            return Result(key, label, False, error=f"{type(e).__name__}: {e}",
                          seconds=time.monotonic() - t0)
        text = (run.output or "").strip()
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z]*\n", "", text)
            text = re.sub(r"\n```\s*$", "", text).strip()
        # Validate inside the loop: a fabricated key, quotation or date is a
        # failed sample, not a verdict on the model. ch06 no-opped once and
        # then invented 11 citation keys; with validation outside the loop
        # that chapter had no third chance and kept its original text.
        kept = kept_percent(source, text)
        bad = []
        if kept >= NOOP_KEPT_PCT:
            bad.append(f"no-op ({kept:.0f}% unchanged)")
        if cite_keys(text) - cite_keys(source):
            bad.append(f"{len(cite_keys(text) - cite_keys(source))} invented key(s)")
        if invented_quotes(source, text):
            bad.append(f"{len(invented_quotes(source, text))} invented quote(s)")
        _y = {q for q in (quantities(text) - quantities(source))
              if re.fullmatch(r"1[5-9]\d{2}|20[0-2]\d", q)}
        # Deep-time durations are a DeepSeek tic: it produced the identical
        # unsourced phrase "ten thousand years ago" in two separate chapters,
        # neither of which mentions a glacial timescale at all. Blocking.
        _d = {m for m in (measures(text) - measures(source))
              if re.search(r"(thousand|million|billion|hundred)\s+year", m)}
        if _y or _d:
            bad.append(f"invented date/duration {sorted(_y | _d)}")
        if brief_text and name_leaks(brief_text, source, text):
            bad.append("named an anchor author")
        if not bad:
            break
        if attempt <= NOOP_RETRIES:
            print(f"   rejected: {'; '.join(bad)} — retry {attempt}"
                  f"/{NOOP_RETRIES}", flush=True)
    secs = time.monotonic() - t0

    src_keys, out_keys = cite_keys(source), cite_keys(text)
    invented = out_keys - src_keys
    dropped = src_keys - out_keys

    usage = getattr(run, "usage", None)
    if callable(usage):          # <=1.x exposed usage() as a method
        usage = usage()
    in_tok = getattr(usage, "input_tokens", 0) or 0
    out_tok = getattr(usage, "output_tokens", 0) or 0

    leaked = name_leaks(brief_text, source, text) if brief_text else set()
    newq = (quantities(text) - quantities(source)) | (measures(text) - measures(source))
    # A year the source does not contain is a fabricated date. Blocking.
    new_years = {q for q in newq if re.fullmatch(r"1[5-9]\d{2}|20[0-2]\d", q)}
    fakeq = invented_quotes(source, text)
    ok = (not invented and not leaked and not new_years and not fakeq
          and bool(text))
    res = Result(key, label, ok, text=text,
                 seconds=secs, in_tokens=in_tok, out_tokens=out_tok,
                 invented=invented, dropped=dropped,
                 kept_pct=kept_percent(source, text), leaked=leaked,
                 fake_quotes=fakeq)
    res.new_quantities = newq
    if invented:
        res.error = f"invented {len(invented)} citation key(s)"
    elif fakeq:
        res.error = f"invented {len(fakeq)} quotation(s) not in the source"
    elif new_years:
        res.error = f"invented date(s) not in the source: {sorted(new_years)}"
    elif leaked:
        res.error = f"named the anchor author(s) in the prose: {sorted(leaked)}"
    elif not text:
        res.error = "empty output"
    elif res.kept_pct >= NOOP_KEPT_PCT:
        res.ok = False
        res.error = f"no-op: returned {res.kept_pct:.0f}% of the source unchanged"
    return res


# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------

SAMPLE_CONFIG = """\
# rewrite_chapter.yaml — overrides the script's built-in defaults.
# Only the keys you set are replaced; everything else keeps its default.

defaults:
  temperature: 1.0
  max_tokens: 32000
  anchors: reportage

models:
  gpt56:
    model: "openai:gpt-5.6"
    provider: openai
    reasoning: high
    env: OPENAI_API_KEY
    label: "OpenAI GPT-5.6"

# anchor_sets:
#   my-set:
#     note: "why this set"
#     authors:
#       - ["Author, *Work*", "TAKE this. DO NOT take that."]
"""


def load_config(path: Path | None, root: Path):
    cfg_path = path or (root / "scripts" / "rewrite_chapter.yaml")
    models, sets = dict(MODELS), dict(ANCHOR_SETS)
    defaults = {"temperature": DEFAULT_TEMPERATURE,
                "max_tokens": DEFAULT_MAX_TOKENS,
                "anchors": DEFAULT_ANCHORS}
    if not cfg_path.exists():
        return models, sets, defaults
    import yaml
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    defaults.update(data.get("defaults") or {})
    for k, v in (data.get("models") or {}).items():
        models[k] = {**models.get(k, {}), **v}
    for k, v in (data.get("anchor_sets") or {}).items():
        sets[k] = {"note": v.get("note", ""),
                   "authors": [tuple(a) for a in v.get("authors", [])]}
    print(f"config: {cfg_path}", file=sys.stderr)
    return models, sets, defaults


# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Rewrite a LaTeX chapter through one or more LLMs.")
    ap.add_argument("chapter", nargs="?", type=Path)
    ap.add_argument("--model", "-m", action="append", default=[],
                    help="model key; repeatable")
    ap.add_argument("--all", action="store_true", help="every configured model")
    ap.add_argument("--anchors", default=None, help="anchor set name")
    ap.add_argument("--outdir", type=Path, default=None)
    ap.add_argument("--temperature", type=float, default=None)
    ap.add_argument("--max-tokens", type=int, default=None)
    ap.add_argument("--direction", default=None,
                    help="extra author direction appended to the prompt")
    ap.add_argument("--guidance", choices=["brief", "full"], default="brief",
                    help="brief (default): the direction plus a four-line "
                         "mechanical floor. full: anchors + VOICE.md + "
                         "LEXICON.md, ~39k chars — see the note by BRIEF.")
    ap.add_argument("--brief-file", type=Path, default=None,
                    help="read the stylistic brief from a file instead of BRIEF")
    ap.add_argument("--config", type=Path, default=None)
    ap.add_argument("--write-config", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the prompt and exit without calling anything")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    root = Path(__file__).resolve().parent.parent  # book/
    models, sets, defaults = load_config(a.config, root)

    if a.write_config:
        dest = a.config or (root / "scripts" / "rewrite_chapter.yaml")
        if dest.exists():
            print(f"refusing to overwrite {dest}", file=sys.stderr)
            return 1
        dest.write_text(SAMPLE_CONFIG, encoding="utf-8")
        print(f"wrote {dest}")
        return 0

    if a.list:
        temperature = a.temperature if a.temperature is not None else defaults["temperature"]
        max_tokens = a.max_tokens or defaults["max_tokens"]
        print(f"{'key':<10} {'provider':<11} {'key set':<8} model")
        for k, s in models.items():
            print(f"{k:<10} {s['provider']:<11} "
                  f"{'yes' if have_key(s) else 'NO':<8} {s['model']}")
        print("\nresolved settings actually sent "
              f"(temperature={temperature}, max_tokens={max_tokens}):")
        for k, s in models.items():
            st = build_settings(s, temperature, max_tokens)
            print(f"  {k:<10} {type(st).__name__:<30} {dict(st)}")
        print("\nanchor sets: " + ", ".join(sorted(sets)))
        return 0

    if not a.chapter:
        ap.error("chapter path required (or use --list / --write-config)")
    if not a.chapter.exists():
        ap.error(f"no such file: {a.chapter}")

    anchors = a.anchors or defaults["anchors"]
    temperature = a.temperature if a.temperature is not None else defaults["temperature"]
    max_tokens = a.max_tokens or defaults["max_tokens"]

    source = a.chapter.read_text(encoding="utf-8")
    brief = (a.brief_file.read_text(encoding="utf-8")
             if a.brief_file else None)
    system = build_system_prompt(root, anchors, sets, a.direction,
                                 guidance=a.guidance, brief=brief)

    if a.dry_run:
        print(system)
        print("\n" + "=" * 70)
        print(f"chapter: {a.chapter}  ({len(source.split())} words, "
              f"{len(cite_keys(source))} distinct citation keys)")
        print(f"prompt: {len(system)} chars, anchors={anchors}")
        return 0

    chosen = list(models) if a.all else (a.model or ["opus5"])
    unknown = [k for k in chosen if k not in models]
    if unknown:
        ap.error(f"unknown model key(s): {unknown}; have {sorted(models)}")

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    outdir = a.outdir or (root / "out" / "rewrites" / f"{a.chapter.stem}-{anchors}-{stamp}")
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"source : {a.chapter} ({len(source.split())} words)")
    print(f"anchors: {anchors}   outdir: {outdir}\n")

    results: list[Result] = []
    for k in chosen:
        print(f"-> {models[k].get('label', k)} …", flush=True)
        r = run_model(k, models[k], system, source, temperature, max_tokens,
                      brief_text=(brief or BRIEF) if a.guidance == "brief" else "")
        results.append(r)
        if r.ok:
            dest = outdir / f"{a.chapter.stem}.{k}.tex"
            dest.write_text(r.text + "\n", encoding="utf-8")
            print(f"   ok  {len(r.text.split()):>5} words  {r.seconds:>6.1f}s  "
                  f"in={r.in_tokens} out={r.out_tokens}  -> {dest.name}")
            if r.dropped:
                print(f"   note: dropped {len(r.dropped)} source key(s): "
                      f"{sorted(r.dropped)[:6]}")
            if r.new_quantities:
                print(f"   WARN: {len(r.new_quantities)} quantit(y/ies) not in "
                      f"the source — check for invented measurements: "
                      f"{sorted(r.new_quantities)[:10]}")
        else:
            print(f"   FAIL {r.error}")
            if r.invented:
                print(f"   invented: {sorted(r.invented)[:8]}")
            if r.leaked:
                print(f"   leaked anchor names: {sorted(r.leaked)}")
            for q in r.fake_quotes[:3]:
                print(f"   INVENTED QUOTE: ``{q}...''")
            # Every rejected sample it produced, printed with the sentence the
            # guard tripped on. A rejection is a claim that wants adjudicating,
            # not a verdict: the year check blocks any year absent from the
            # source, which includes a model correctly adding the source's own
            # "a hundred and thirty-eight years later" to 1763. Discarding the
            # text meant a false positive cost the whole draft — 3,497 words,
            # once, because this write sat inside the invented-quote loop above
            # and never ran for any other failure.
            for y in sorted(re.findall(r"1[5-9]\d{2}|20[0-2]\d", r.error or "")):
                for m in re.finditer(r"[^.]*\b" + y + r"\b[^.]*\.", r.text):
                    print(f"   {y} in: …{m.group(0).strip()[:150]}…")
                    break
            if r.text:
                dest = outdir / f"{a.chapter.stem}.{k}.REJECTED.tex"
                dest.write_text(r.text + "\n", encoding="utf-8")
                print(f"   kept for review -> {dest.name} "
                      f"({len(r.text.split())} words)")

    print(f"\n{'model':<30} {'status':<7} {'words':>6} {'kept':>6} "
          f"{'secs':>7} {'out tok':>8}")
    for r in results:
        kept = f"{r.kept_pct:.0f}%" if r.ok else "-"
        flag = "  <- barely rewrote" if r.ok and r.kept_pct >= 60 else ""
        print(f"{r.label:<30} {'ok' if r.ok else 'FAIL':<7} "
              f"{len(r.text.split()):>6} {kept:>6} {r.seconds:>7.1f} "
              f"{r.out_tokens:>8}{flag}")
    print(f"\n{outdir}")
    return 0 if any(r.ok for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
