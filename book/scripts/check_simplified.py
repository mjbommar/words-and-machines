#!/usr/bin/env python3
"""Simplified Book English — the vocabulary layer of the house style.

Reads `scripts/data/simplified_english/lexicon.json` (built by
`scripts/build_simplified_lexicon.py`, documented in
`docs/guides/SIMPLIFIED-ENGLISH.md`) and checks chapter prose against it.

Advisory by design: NOT part of `make check`. Vocabulary is a judgement
call often enough that a lexical linter should not stand between an author
and a release. Use `--strict` in a book's own CI if you want a gate.

What it checks:

  unapproved word     bureaucratic/legal diction with a plain replacement
                      ("promulgate" -> issue, publish)          [error|warn]
  unapproved phrase   the same, for phrases ("pursuant to")     [error|warn]
  uncommon term       a recurring word outside the ordinary-corpus tiers whose
                      first authorial use has no recognized explanation [warn]
  undefined abbrev    an abbreviation not expanded at first use       [warn]
  term drift          a declared term written some other way         [error]

Escape hatches, because every one of these can be wrong:
  * `% sbe-ok: <reason>` on the line above (or at the end of) a line
    silences SBE findings on it; `--suppressions` audits what was excused.
  * quoted spans (``...'') and dropped environments (quotation, archive,
    codelisting, ...) are never checked for diction — a quoted statute is
    not the author's word choice.
  * a match inside a capitalized phrase ("Payment in Lieu of Taxes") reads
    as a proper name and is skipped.
  * `ignore:`, `allow:`, `abbreviations:`, `names:`, `terms:` in book.yaml.

Deliberately NOT checked here — one fault, one gate:
  sentence and paragraph length  -> check_style.py (`style-targets`)
  Latinate share, nominalization, hedges -> register_report.py
  AI tells, banned slop words    -> check_style.py (STYLE.md)
  repetition, duplicate sentences -> check_prose.py

Usage:
    uv run --group sbe scripts/check_simplified.py                # whole book
    uv run --group sbe scripts/check_simplified.py --strict       # fail warnings
    uv run --group sbe scripts/check_simplified.py --terms        # term work list
    uv run --group sbe scripts/check_simplified.py --emit-config  # YAML block
    uv run --group sbe scripts/check_simplified.py --stats        # tier coverage
    uv run --group sbe scripts/check_simplified.py --markers      # score sources
    uv run --group sbe scripts/check_simplified.py --advisory     # + ideas
    uv run --group sbe scripts/check_simplified.py --suppressions # audit escapes
    uv run --group sbe scripts/check_simplified.py --explain gigawatt
    uv run --group sbe scripts/check_simplified.py --format grep|jsonl
    uv run --group sbe scripts/check_simplified.py --root ../other-book
    uv run --group sbe scripts/check_simplified.py FILES...
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from bisect import bisect_right
from collections import Counter
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path

import inflect
import simplemma
import yaml
from converter.latex_source import blank, extract_prose
from simplemma.tokenizer import TOKREGEX

ROOT = Path(__file__).resolve().parent.parent
LEXICON = ROOT / "scripts" / "data" / "simplified_english" / "lexicon.json"
BOOK_YAML = ROOT / "book.yaml"
LATEX = ROOT / "latex"
SUBDIRS = ("chapters", "frontmatter", "front-matter", "backmatter",
           "back-matter")

# --------------------------------------------------------------- LaTeX layer
_COMMENT = re.compile(r"(?<!\\)%.*")
_SBE_OK = re.compile(r"(?<!\\)%\s*sbe-ok\b:?[ \t]*(.*)")
_ACCENT_BRACED = re.compile(r"\\[`'\"^~=.uvHtcdbr]\{([A-Za-z])\}")
_ACCENT_BARE = re.compile(r"\\[`'\"^~=.](?=[A-Za-z])")
_BRACE_JUNK = re.compile(r"[{}$&~^_]")
_QUOTE_LIG = re.compile(r"``|''")
_DASH_LIG = re.compile(r"-{2,}")
_QUOTED = re.compile(r"``.*?''|\u201c.*?\u201d|\"[^\"\n]+\"", re.DOTALL)

# A word: unicode letters, so "Angstrom" with diacritics is one token.
_INFLECT = inflect.engine()


def words(text: str):
    """Yield Simplemma tokens that contain natural-language letters.

    Simplemma owns token boundaries (including Unicode, apostrophes, and
    hyphens). Filtering happens here because its tokenizer also returns
    punctuation and numeric tokens, which are useful to a general NLP
    pipeline but are not words in the SBE coverage denominator.
    """
    return (match for match in TOKREGEX.finditer(text)
            if match.group(0) and match.group(0)[0].isalpha())


def word_values(text: str) -> list[str]:
    return [match.group(0) for match in words(text)]


ROMAN = re.compile(r"^[IVXLCDM]+$")
# Initialisms and acronyms, not product/model codes.  The guide promises
# "3--7 capital letters"; accepting digits made H100, FP16 and Y2K look like
# abbreviations that could be expanded into a full name.
ABBREV_OK = re.compile(r"^[A-Z]{3,7}$")
# The token may carry ordinary English number or possession, but the policy
# decision belongs to its base form: APIs -> API; NATO's -> NATO. Requiring a
# lowercase plural/possessive suffix avoids shaving a real final S from CHIPS.
ABBREV_TOKEN = re.compile(r"^([A-Z]{3,7})(?:s|['\u2019]s)?$")
SENT_END = re.compile(r"[.!?][\"'\u201d)]*\s")
PARA_BREAK = re.compile(r"\n[ \t]*\n")
TITLE_WORD = re.compile(r"^[A-Z][a-z\u00c0-\u024f']+$")
# A name-shaped neighbour: starts capital, contains a lowercase somewhere.
# Matches "The", "Act", "GeForce"; not "GTX".
NAME_WORD = re.compile(r"^[A-Z][A-Za-z\u00c0-\u024f']*[a-z][A-Za-z\u00c0-\u024f']*$")

# Cues bound to the term: an em dash, paren or colon that OPENS an
# explanation, not one that happens to fall two sentences later.
# Strong cues say "a definition follows" on their own, wherever they fall
# in the window. Weak cues are only punctuation shapes — an em dash, a
# parenthesis, a copula — and ordinary apposition wears the same clothes
# ("He carried the theodolite up the ridge, a long walk in bad light"), so
# they only count when they sit right against the term.
GLOSS_STRONG = re.compile(
    r"\bcalled\b|\bknown as\b|\bstands for\b|\bwhat we call\b"
    r"|\bmeans\b|\bmeaning\b|\bwhich means\b|\bnamely\b|\bthat is\b"
    r"|\bthis is\b|\bi\.e\.", re.IGNORECASE)
# Within reach of the term, a dash / paren / colon opens an explanation
# whatever word follows it — STYLE.md §6 mandates "1.4 gigawatts --- enough
# to power 800,000 homes", where no article follows the dash. The reach is
# what keeps this honest; STYLE.md also caps em dashes at one per paragraph.
GLOSS_WEAK = re.compile(
    r"(?:\u2014|\(|:)\s*\w"
    r"|\bis\s+(?:a|an|the|zero|one|two|three|four|five|six|seven|eight|"
    r"nine|ten|\d+)\b|\bare\s+(?:the|a|an|zero|one|two|three|four|five|"
    r"six|seven|eight|nine|ten|\d+)\b", re.IGNORECASE)
GLOSS_WEAK_REACH = 90    # characters after the term
# A dash, paren or colon within a few characters of the term opens an
# apposition. That is a gloss regardless of what word follows it.
GLOSS_APPOSITIVE = re.compile(r"^[^\w\n]{0,3}(?:\u2014|\(|:)\s*\w")
GLOSS_BEFORE = re.compile(
    r"\b(?:called|known as|what we call|the term|that is|this is|meaning|"
    r"namely|so-called)\b"
    r"[^.!?]{0,60}$", re.IGNORECASE)
# A compact definition can precede the term: "no common measure—
# incommensurable". A dash directly before the word is much stronger than a
# generic comma and does not turn ordinary list items into false glosses.
GLOSS_REVERSE_APPOSITIVE = re.compile(r"\u2014\s*$")
GLOSS_REVERSE_NOUN = re.compile(
    r"\b(?:algorithm|class|function|language|measure|method|number|process|"
    r"system|term|word)\s*,\s*$", re.IGNORECASE)


def flatten(raw: str, *, root: Path = ROOT) -> tuple[str, list[tuple[int, int]]]:
    """Parsed LaTeX -> prose and the spans of inline quoted material.

    TexSoup and the shared EPUB pre-parser own structure. Newlines remain in
    place, so result line numbers are source line numbers. Accent commands can
    shorten a line; ordering compares line-local occurrences, not columns.
    """
    text = extract_prose(raw, root=root)
    text = _ACCENT_BRACED.sub(lambda m: m.group(1), text)
    text = _ACCENT_BARE.sub("", text)
    quoted = [(m.start(), m.end()) for m in _QUOTED.finditer(text)]
    text = _DASH_LIG.sub(lambda m: "\u2014" + " " * (len(m.group(0)) - 1), text)
    text = _QUOTE_LIG.sub(lambda m: blank(m.group(0)), text)
    text = _BRACE_JUNK.sub(" ", text)
    return text, quoted


class LineMap:
    def __init__(self, text: str) -> None:
        self.starts = [0]
        for i, c in enumerate(text):
            if c == "\n":
                self.starts.append(i + 1)

    def line(self, offset: int) -> int:
        return bisect_right(self.starts, offset)


@dataclass
class Finding:
    file: str
    line: int
    severity: str          # error | warn | idea
    kind: str
    message: str
    subject: str | None = None

    def render(self, fmt: str) -> str:
        if fmt == "jsonl":
            row = asdict(self)
            if self.subject is None:
                row.pop("subject")
            return json.dumps(row)
        tag = {"error": "ERROR ", "warn": "WARN ", "idea": "IDEA "}.get(
            self.severity, "WARN ")
        return f"{self.file}:{self.line}: {tag}{self.kind}: {self.message}"


# ------------------------------------------------------------------ lexicon

SEVERITIES = ("error", "warn", "off")

# Productive prefixes that can stand before an otherwise familiar component
# in a hyphenated compound. This is an SBE policy list, not a stemmer.
HYPHEN_PREFIX = frozenset((
    "un", "re", "non", "over", "under", "out", "pre", "post", "anti",
    "counter", "co", "mis", "sub", "inter", "multi", "semi", "self",
    "de", "mid", "ex", "pro", "micro", "macro", "mini",
))


def _as_list(value, key: str) -> list:
    if value is None:
        return []
    if isinstance(value, str) or not isinstance(value, (list, tuple)):
        sys.exit(f"check_simplified: book.yaml simplified_english.{key} must "
                 f"be a list, got {type(value).__name__} ({value!r})")
    return list(value)


def normalize(token: str) -> str:
    w = token.lower().replace("’", "'")
    w = w.strip("'-")
    w = re.sub(r"'s$", "", w)
    return w.strip("-")


def fold(word: str) -> str:
    """Strip diacritics for lookup, so an accented word finds its entry."""
    return "".join(c for c in unicodedata.normalize("NFKD", word)
                   if not unicodedata.combining(c))


@lru_cache(maxsize=None)
def stem_key(word: str) -> str:
    """Return an inflectional family key without erasing derivation.

    Simplemma handles known English inflections. For an unknown technical
    plural (for example, ``tokenizers``), inflect supplies grammatical-number
    handling. The known-word guard prevents inflect's noun heuristic from
    damaging singular words such as ``analysis`` and ``business``.
    """
    word = normalize(word)
    lemma = simplemma.lemmatize(word, lang="en")
    if lemma != word:
        # Simplemma occasionally truncates an imported plural (for example,
        # tranches -> tranch). Prefer inflect when its candidate round-trips
        # to the observed plural and preserves more of the source word.
        singular = _INFLECT.singular_noun(word)
        if (isinstance(singular, str)
                and _INFLECT.plural_noun(singular) == word
                and len(singular) > len(lemma)):
            return singular
        return lemma
    if simplemma.is_known(word, lang="en"):
        return word
    # An unknown adjective ending in -less/-ness is not a plural noun. The
    # round-trip check below catches most false analyses; this cheap semantic
    # guard catches the productive cases where inflect itself round-trips.
    if word.endswith("ss"):
        return word
    singular = _INFLECT.singular_noun(word)
    if (isinstance(singular, str) and singular
            and _INFLECT.plural_noun(singular) == word):
        return singular
    return word


class Standard:
    """The lexicon plus this book's overrides from book.yaml."""

    def __init__(self, book_cfg: dict, advisory: bool = False,
                 *, lexicon: Path = LEXICON) -> None:
        if not lexicon.exists():
            sys.exit(f"check_simplified: no lexicon at {lexicon}\n"
                     "build it: uv run --group sbe-build "
                     "scripts/build_simplified_lexicon.py")
        try:
            data = json.loads(lexicon.read_text())
        except json.JSONDecodeError as e:
            sys.exit(f"check_simplified: {lexicon} is not valid JSON ({e})")
        self.core: set[str] = set(data["core"])
        self.open: set[str] = set(data["open"])
        self.recognized: set[str] = set(data.get("recognized") or ())
        self.opengloss_phrases: set[str] = set(
            data.get("opengloss_phrases") or ())
        self.marked_sensitive: set[str] = set(data.get("sensitive") or ())
        self.thresholds = dict(data["thresholds"])
        self.abbrev_exempt = set(data["abbreviation_exempt"])
        self.version = data["version"]
        self.built = data["built"]
        self.advisory = advisory

        cfg = book_cfg.get("simplified_english") or {}
        if not isinstance(cfg, dict):
            sys.exit("check_simplified: book.yaml simplified_english: must be "
                     f"a mapping, got {type(cfg).__name__}")
        allowed_cfg = {"enabled", "terms", "abbreviations", "names", "ignore",
                       "allow", "deny", "thresholds"}
        if unknown := sorted(set(cfg) - allowed_cfg):
            sys.exit("check_simplified: unknown book.yaml simplified_english "
                     "key(s): " + ", ".join(unknown))
        enabled = cfg.get("enabled", True)
        if not isinstance(enabled, bool):
            sys.exit("check_simplified: book.yaml simplified_english.enabled "
                     f"must be true or false, got {enabled!r}")
        self.enabled = enabled

        overrides = cfg.get("thresholds") or {}
        if not isinstance(overrides, dict):
            sys.exit("check_simplified: book.yaml "
                     "simplified_english.thresholds must be a mapping")
        if unknown := sorted(set(overrides) - set(self.thresholds)):
            sys.exit("check_simplified: unknown book.yaml "
                     "simplified_english.thresholds key(s): "
                     + ", ".join(unknown))
        self.thresholds.update(overrides)
        for key in ("unintroduced", "undefined_abbreviation"):
            if self.thresholds.get(key) not in SEVERITIES:
                sys.exit(f"check_simplified: book.yaml thresholds.{key} must "
                         f"be one of {', '.join(SEVERITIES)}, got "
                         f"{self.thresholds.get(key)!r}")
        for key in ("gloss_window", "max_findings_per_file",
                    "unintroduced_min_uses"):
            try:
                self.thresholds[key] = max(1, int(self.thresholds[key]))
            except (TypeError, ValueError):
                sys.exit(f"check_simplified: book.yaml thresholds.{key} must "
                         f"be a positive integer, got "
                         f"{self.thresholds.get(key)!r}")

        self.abbrev_exempt |= {str(a) for a in
                               _as_list(cfg.get("abbreviations"),
                                        "abbreviations")}
        # Some brands and system names deliberately use an all-cap spelling
        # (LEXIS, WESTLAW, RANDU). They are not abbreviations an author can
        # expand, so configuration records that decision separately.
        self.name_exempt = {str(a) for a in
                            _as_list(cfg.get("names"), "names")}
        self.core |= {str(w).lower() for w in
                      _as_list(cfg.get("allow"), "allow")}

        # Declared terms: admitted vocabulary, plus spellings it must not take.
        self.declared: dict[str, dict] = {}
        self.drift: dict[str, str] = {}
        for entry in _as_list(cfg.get("terms"), "terms"):
            if isinstance(entry, str):
                entry = {"term": entry}
            if not isinstance(entry, dict) or "term" not in entry:
                sys.exit("check_simplified: book.yaml simplified_english."
                         f"terms entries need a `term:` key, got {entry!r}")
            term = str(entry["term"])
            parts = [p.lower() for p in word_values(term)]
            self.declared[term.lower()] = entry
            for part in parts:
                self.declared.setdefault(part, entry)
            for wrong in _as_list(entry.get("not"), "terms[].not"):
                wrong = str(wrong)
                if wrong.lower() != term.lower() and wrong.lower() not in parts:
                    self.drift[wrong] = term

        ignore = {str(w).lower() for w in _as_list(cfg.get("ignore"), "ignore")}
        # `ignore` means "this book deliberately keeps this word", which has
        # to cover the uncommon-term review too; otherwise an explicit
        # editorial decision returns every round and the list never converges.
        self.core |= {w for w in ignore if " " not in w}
        self.words: dict[str, tuple[str, str]] = {}
        for sub in data["substitutions"]:
            if sub["from"].lower() not in ignore:
                self.words[sub["from"].lower()] = (sub["grade"], sub["to"])
        for w in _as_list(cfg.get("deny"), "deny"):
            self.words[str(w).lower()] = ("error", "(banned in book.yaml)")
        self.phrases = {
            s["from"].lower(): (s["grade"], s["to"])
            for s in data["phrase_substitutions"]
            if s["from"].lower() not in ignore
        }
        if not advisory:     # `idea` grade is revision ideation, not a finding
            self.words = {k: v for k, v in self.words.items()
                          if v[0] != "idea"}
            self.phrases = {k: v for k, v in self.phrases.items()
                            if v[0] != "idea"}

        # The register-marker rate has to mean the same thing from book to
        # book, so it is not filtered by per-book policy. Most idea-grade
        # entries are ordinary words and would swamp the signal; `marker_only`
        # retains the narrower set that predicts register without making each
        # technically correct occurrence a default revision warning.
        # The builder owns this list so reference-corpus measurement and book
        # scoring cannot drift. `such` is deliberately absent: it is common
        # prose and failed the two-legislature replication test.
        all_markers = data.get("register_markers") or [
            s["from"].lower()
            for s in data["substitutions"] + data["phrase_substitutions"]
            if s["grade"] in ("error", "warn")
        ] + ["shall", "thereto", "hereunder", "said party",
             "provided that", "deemed", "aforementioned"]
        self.marker_re = self._alt(dict.fromkeys(all_markers),
                                   flexible_space=True)
        self.word_re = self._alt(self.words)
        self.phrase_re = self._alt(self.phrases, flexible_space=True)
        self.drift_re = self._alt(self.drift, flexible_space=True)

    @staticmethod
    def _alt(keys, flexible_space: bool = False):
        if not keys:
            return None
        parts = []
        for k in sorted(keys, key=len, reverse=True):
            pat = re.escape(k)
            if flexible_space:
                pat = pat.replace(r"\ ", r"\s+")
            parts.append(pat)
        return re.compile(rf"\b(?:{'|'.join(parts)})\b", re.IGNORECASE)

    # -- tier decisions ----------------------------------------------------

    def listed(self, word: str) -> str | None:
        if word in self.marked_sensitive:
            return None            # never quietly free, however it is spelled
        for w in (word, fold(word)):
            if w in self.core:
                return "core"
            if w in self.declared:
                return "declared"
            if w in self.open:
                return "open"
            if w in self.recognized:
                return "recognized"
        return None

    def tier(self, word: str) -> str:
        hit = self.listed(word)
        if hit:
            return hit
        if word in self.marked_sensitive:
            return "sensitive"
        lemma = stem_key(word)
        if lemma != word and (hit := self.listed(lemma)):
            return hit
        parts = [p for p in word.split("-") if p]
        if len(parts) > 1 and all(
                self.tier(p) not in ("recognized", "unlisted") or p.isdigit()
                or p in HYPHEN_PREFIX for p in parts):
            return "open"
        return "unlisted"


# -------------------------------------------------------------------- check

def is_sentence_start(text: str, pos: int) -> bool:
    i = pos - 1
    while i >= 0 and text[i] in " \t\n\"'\u201c(\u2014-":
        if text[i] == "\n" and i > 0 and text[i - 1] == "\n":
            return True
        i -= 1
    return i < 0 or text[i] in ".!?:;\u2022"


def gloss_span(text: str, off: int, window: int) -> str:
    """The term plus the rest of its sentence and the next one.

    Bounded by the paragraph, because an explanation two paragraphs later
    is not an explanation the reader met in time.
    """
    span = text[off:off + window]
    if (para := PARA_BREAK.search(span)):
        span = span[: para.start()]
    ends = [m.end() for m in SENT_END.finditer(span)]
    return span[: ends[1]] if len(ends) > 1 else span


class Book:
    """Every chapter, flattened once, with book-wide first-use bookkeeping.

    First use is a property of the BOOK, not of a file: a term introduced
    in chapter 3 is introduced for chapter 9 too. So the scan is two
    passes — collect, then judge.
    """

    def __init__(self, files: list[Path], std: Standard,
                 partial: bool = False, *, root: Path = ROOT) -> None:
        self.std = std
        self.partial = partial
        self.root = root
        self.findings: list[Finding] = []
        self.counts = {"core": 0, "open": 0, "recognized": 0,
                       "declared": 0, "unlisted": 0, "name": 0}
        self.per_file: list[tuple[str, dict]] = []
        self.text: dict[str, str] = {}
        self.lines: dict[str, LineMap] = {}
        self.suppressed: dict[str, dict[int, str]] = {}
        # First-use rules are ordered. An acronym expanded later in the book
        # must not excuse its first occurrence.
        self.file_rank: dict[str, int] = {}
        self.expansion_at: dict[str, list[tuple[int, int]]] = {}
        self.first_term: dict[str, tuple[str, int, str]] = {}
        self.term_uses: Counter[str] = Counter()
        self.first_sensitive: dict[str, tuple[str, int, str]] = {}
        self.sensitive_uses: Counter[str] = Counter()
        self.first_abbrev: dict[str, tuple[str, int]] = {}
        self.abbrev_uses: Counter[str] = Counter()
        self.abbrev_where: dict[str, list[tuple[str, int]]] = {}
        self.initialisms: dict[str, dict[str, list[int]]] = {}
        self.suppression_log: list[tuple[str, int, str]] = []
        self.markers = 0
        self.marker_uses: Counter[str] = Counter()
        for path in files:
            self._collect(path)
        self._judge()

    def add(self, rel: str, off: int, severity: str, kind: str,
            msg: str, *, subject: str | None = None) -> None:
        line = self.lines[rel].line(off)
        if kind != "suppression" and (mark := self.suppressed.get(rel,
                                                                 {}).get(line)):
            _, scope = mark
            quoted = {w.lower() for w in re.findall(r"'([^']+)'", msg)}
            if subject:
                quoted.add(subject.lower())
            if not scope or (quoted & scope) or any(s in msg.lower()
                                                    for s in scope):
                return
        self.findings.append(
            Finding(rel, line, severity, kind, msg, subject=subject))

    # -- pass 1 ------------------------------------------------------------

    def _collect(self, path: Path) -> None:
        std = self.std
        try:
            raw = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            sys.exit(f"check_simplified: cannot read {path}: {e}")
        text, quoted = flatten(raw, root=self.root)
        try:
            rel = str(path.relative_to(self.root))
        except ValueError:
            rel = str(path)
        self.text[rel] = text
        self.lines[rel] = LineMap(text)
        rank = len(self.file_rank)
        self.file_rank[rel] = rank

        # `% sbe-ok: word[, word] — reason` silences findings that quote one
        # of those words, on this line and the next. Naming nothing silences
        # everything on those lines, which is what the audit exists for.
        raw_lines = LineMap(raw)
        marks: dict[int, tuple[str, frozenset[str]]] = {}
        pending: list[tuple[int, str]] = []
        for m in _SBE_OK.finditer(raw):
            line = raw_lines.line(m.start())
            body = m.group(1).strip()
            targets, sep, reason = body.partition("\u2014")
            if not sep:
                targets, sep, reason = body.partition(" - ")
            if not sep:
                targets, reason = "", body
            scope = frozenset(w.strip().lower()
                              for w in re.split(r"[,;]", targets) if w.strip())
            reason = reason.strip()
            if not reason:
                pending.append((m.start(), "`% sbe-ok` with no reason — say "
                                "why, so a reviewer can audit what was "
                                "excused"))
                reason = "(no reason given)"
            for ln in (line, line + 1):
                marks[ln] = (reason, scope)
            self.suppression_log.append(
                (rel, line,
                 f"{', '.join(sorted(scope)) or 'everything on the line'}"
                 f" — {reason}"))
        self.suppressed[rel] = marks
        for off, msg in pending:
            self.add(rel, off, "warn", "suppression", msg)

        counts = {"core": 0, "open": 0, "recognized": 0,
                  "declared": 0, "unlisted": 0, "name": 0}

        def in_quote(pos: int) -> bool:
            return any(a <= pos < b for a, b in quoted)

        # unapproved words and phrases
        for rx, table, kind in ((std.phrase_re, std.phrases,
                                 "unapproved phrase"),
                                (std.word_re, std.words, "unapproved word")):
            if rx is None:
                continue
            for m in rx.finditer(text):
                if in_quote(m.start()) or in_proper_name(text, m):
                    continue
                key = re.sub(r"\s+", " ", m.group(0).lower())
                grade, better = table.get(key, ("warn", ""))
                found = re.sub(r"\s+", " ", m.group(0))
                self.add(rel, m.start(), grade, kind,
                         f"{found!r} -> {better}" if better else repr(found))

        if std.marker_re is not None:
            for m in std.marker_re.finditer(text):
                if in_quote(m.start()):
                    continue
                marker = re.sub(r"\s+", " ", m.group(0).lower())
                self.marker_uses[marker] += 1
                self.markers += 1

        # a declared term written some other way
        if std.drift_re is not None:
            for m in std.drift_re.finditer(text):
                if in_quote(m.start()):
                    continue
                found = re.sub(r"\s+", " ", m.group(0))
                target = next((v for k, v in std.drift.items()
                               if k.lower() == found.lower()), None)
                if target is None or found.lower() == target.lower():
                    continue
                self.add(rel, m.start(), "error", "term drift",
                         f"{found!r} — the book's declared term is {target!r}")

        # abbreviation expansions, in every shape an author writes them
        explicit, initialisms = collect_expansions(text)
        for abbr, positions in explicit.items():
            self.expansion_at.setdefault(abbr, []).extend(
                (rank, pos) for pos in positions)
        self.initialisms.setdefault(rel, initialisms)

        # word tiers and first uses
        for m in words(text):
            token = m.group(0)
            word = normalize(token)
            if not word or SKIP.match(word):
                continue
            # Quotation is evidence, not the author's diction. Exclude it
            # from tiers, term prompts, and abbreviation first-use history,
            # just as we already exclude it from substitutions and markers.
            if in_quote(m.start()):
                continue
            # Identifier-like alphanumeric tokens are not prose vocabulary.
            if any(c.isdigit() for c in token):
                counts["name"] += 1
                continue
            # Plural and possessive endings do not change abbreviation
            # identity: APIs and NATO's are checked as API and NATO.
            if (abbr_match := ABBREV_TOKEN.fullmatch(token)):
                abbr = abbr_match.group(1)
                if abbr in std.name_exempt:
                    counts["name"] += 1
                    continue
                if is_abbreviation(std, text, m, abbr):
                    self.abbrev_uses[abbr] += 1
                    self.abbrev_where.setdefault(abbr, []).append(
                        (rel, m.start()))
                    self.first_abbrev.setdefault(abbr, (rel, m.start()))
                continue
            # xAI, arXiv, eCourts, al-Khwarizm: internal capitals are a strong
            # proper-name/identifier signal. Frequency tiers are lowercase
            # and cannot usefully judge these spellings.
            if (any(c.isupper() for c in token[1:])
                    and any(c.islower() for c in token)):
                counts["name"] += 1
                continue
            # Two-letter forms (AI, US) and long all-cap identifiers fall
            # outside the deliberately narrow 3--7-letter check. Preserve the
            # counting contract: they are metadata-like tokens, not prose
            # words in the coverage denominator.
            if token.isupper() and len(token) > 1:
                continue
            if word in std.marked_sensitive:
                self.sensitive_uses[word] += 1
                self.first_sensitive.setdefault(word, (rel, m.start(), token))
                counts["unlisted"] += 1
                continue
            if token[0].isupper():
                tier = std.tier(word)
                # A capitalized word the lexicon doesn't know is a name, not
                # a new term — including at the start of a sentence, where
                # the capital carries no information.
                if tier == "unlisted" or not is_sentence_start(text, m.start()):
                    counts["name"] += 1
                    continue
                counts[tier] += 1
                continue
            tier = std.tier(word)
            counts[tier] += 1
            if tier in ("recognized", "unlisted"):
                key = stem_key(word)
                self.term_uses[key] += 1
                self.first_term.setdefault(key, (rel, m.start(), token))

        for k, v in counts.items():
            self.counts[k] += v
        self.per_file.append((rel, counts))

    # -- pass 2 ------------------------------------------------------------

    def _judge(self) -> None:
        std = self.std
        window = int(std.thresholds.get("gloss_window", 400))
        cap = int(std.thresholds.get("max_findings_per_file", 40))
        scope = ("first use in the files checked" if self.partial
                 else "first use in the book")

        sev = std.thresholds.get("unintroduced", "warn")
        min_uses = int(std.thresholds.get("unintroduced_min_uses", 2))
        if sev != "off":
            shown: Counter[str] = Counter()
            hidden: Counter[str] = Counter()
            for stem, (rel, off, surface) in sorted(
                    self.first_term.items(), key=lambda kv: kv[1][:2]):
                if self.introduced(stem, rel, off, window):
                    continue
                uses = self.term_uses[stem]
                if uses < min_uses and not std.advisory:
                    continue
                finding_sev = "idea" if uses < min_uses else sev
                if shown[rel] >= cap:
                    hidden[rel] += 1
                    continue
                shown[rel] += 1
                tier = std.tier(normalize(surface))
                origin = ("is an OpenGloss headword but falls outside the "
                          "ordinary-corpus tiers" if tier == "recognized"
                          else "is not found in OpenGloss or the corpus tiers")
                self.add(rel, off, finding_sev, "unintroduced term",
                         f"{surface!r} ({uses}x) {origin}; its {scope} carries no "
                         "recognized inline explanation. Review whether this "
                         "use is jargon, restricted, or already clear in "
                         "context.",
                         subject=surface)
            for rel, n in hidden.items():
                self.add(rel, 0, "warn", "unintroduced term",
                         f"{n} more first use(s) in this file not shown "
                         "(raise max_findings_per_file)")

        for word, (rel, off, surface) in sorted(
                self.first_sensitive.items(), key=lambda kv: kv[1][:2]):
            self.add(rel, off, "warn", "sensitive term",
                     f"{surface!r} ({self.sensitive_uses[word]}x) is a slur or "
                     "an outdated ethnonym or clinical term. A frequency list "
                     "blesses it; a book should quote it, frame it, or replace "
                     "it — never use it unmarked")

        sev = std.thresholds.get("undefined_abbreviation", "warn")
        if sev != "off":
            for abbr, (rel, off) in sorted(self.first_abbrev.items(),
                                           key=lambda kv: kv[1]):
                if (abbr in std.abbrev_exempt
                        or self.expanded_by_first_use(abbr, rel, off)
                        or abbr.lower() in std.declared
                        or self.spelled_out_nearby(abbr)):
                    continue
                self.add(rel, off, sev, "undefined abbreviation",
                         f"{abbr!r} ({self.abbrev_uses[abbr]}x) is not expanded "
                         'at first use — write it once as "Full Name (ABBR)", '
                         "or list it under simplified_english.abbreviations "
                         "in book.yaml; if it is an all-cap proper name, list "
                         "it under simplified_english.names instead",
                         subject=abbr)

    def expanded_by_first_use(self, abbr: str, rel: str, off: int) -> bool:
        """Was the abbreviation explicitly expanded no later than first use?"""
        first = (self.file_rank[rel], off)
        return any(where <= first for where in self.expansion_at.get(abbr, ()))

    def spelled_out_nearby(self, abbr: str) -> bool:
        """A phrase whose initials spell the abbreviation, near a use of it.

        "community benefit agreements ... CBAs target specific needs" is an
        expansion; requiring proximity keeps three accidental initials in
        an unrelated sentence from silencing the check.
        """
        first_rel, first_off = self.first_abbrev.get(abbr, (None, None))
        if first_rel is not None:
            for pos in self.initialisms.get(first_rel, {}).get(abbr, ()):
                # Visible-word distance is stable across LaTeX comments and
                # citation keys, whose same-length blanking can add hundreds
                # of meaningless characters between adjacent prose lines.
                if pos <= first_off:
                    between = self.text[first_rel][pos:first_off]
                    if len(word_values(between)) > 80:
                        continue
                else:
                    between = self.text[first_rel][first_off:pos]
                    if len(word_values(between)) > 25:
                        continue
                # A reverse expansion can follow the acronym in the same
                # sentence ("XYZ, the Xylophone Yield Zone"). Once a sentence
                # has ended, however, it is a later definition and cannot
                # rewrite the first-use history.
                if (pos > first_off
                        and SENT_END.search(between)):
                    continue
                return True
        return False

    def word_position(self, stem: str, rel: str, off: int) -> tuple[int, int, int]:
        """Comparable first-use position independent of TeX column shifts."""
        line = self.lines[rel].line(off)
        line_start = self.lines[rel].starts[line - 1]
        prior = sum(
            stem_key(normalize(hit.group(0))) == stem
            for hit in words(self.text[rel][line_start:off])
        )
        return self.file_rank[rel], line, prior + 1

    def introduced_before(self, stem: str, position: tuple[int, int, int],
                          window: int, seen: frozenset[str]) -> bool:
        """Was a component term introduced before a later compound use?"""
        first = self.first_term.get(stem)
        if first is None or stem in seen:
            return False
        rel, off, _ = first
        if self.word_position(stem, rel, off) > position:
            return False
        return self.introduced(stem, rel, off, window, seen=seen)

    def introduced(self, stem: str, rel: str, off: int, window: int,
                   *, seen: frozenset[str] = frozenset()) -> bool:
        """Does the first authorial use carry a recognizable explanation?"""
        position = self.word_position(stem, rel, off)
        seen = seen | {stem}
        # a hyphenated compound of an introduced term is introduced
        parts = [stem_key(p) for p in stem.split("-") if p]
        if len(parts) > 1 and all(
                self.introduced_before(p, position, window, seen)
                or self.std.tier(p) not in ("recognized", "unlisted")
                or p in HYPHEN_PREFIX for p in parts):
            return True
        text = self.text[rel]
        before = text[max(0, off - 140):off]
        if GLOSS_BEFORE.search(before):
            return True
        if (GLOSS_REVERSE_APPOSITIVE.search(before)
                or GLOSS_REVERSE_NOUN.search(before)):
            return True
        span = gloss_span(text, off, window)
        token = next(words(span), None)
        after = span[token.end():] if token else span
        first_end = (match.end() if (match := SENT_END.search(span))
                     else len(span))
        first_sentence = span[:first_end]
        current_cue = bool(
            GLOSS_STRONG.search(first_sentence)
            or GLOSS_APPOSITIVE.match(after)
            or re.match(r"^\s*,\s+(?:a|an|the)\b", after, re.IGNORECASE)
            or GLOSS_WEAK.search(
                first_sentence[:len(stem) + GLOSS_WEAK_REACH])
        )
        if not current_cue and not GLOSS_STRONG.search(span):
            return False
        # A gloss built from words the reader also lacks has moved the
        # problem, not solved it (Wycliffe EasyEnglish, Ericsson English).
        # Once the first sentence itself contains a definition cue, later
        # sentences are subsequent prose, not part of the definition. Counting
        # repeated uses there used to invalidate a perfectly good gloss.
        definition = first_sentence if current_cue else span
        fresh = 0
        for m in words(definition[len(stem):]):
            w = normalize(m.group(0))
            if (w and not m.group(0)[0].isupper()
                    and self.std.tier(w) in ("recognized", "unlisted")
                    and stem_key(w) != stem):
                fresh += 1
        return fresh <= 1

    # -- reporting helpers -------------------------------------------------

    def glossary(self) -> list[dict]:
        """Every candidate term, with its first-use sentence and status.

        A draft, not shippable copy: the definition is the introducing
        sentence, which for an in-place gloss is sometimes a fragment.
        Emit, curate, then render.
        """
        window = int(self.std.thresholds.get("gloss_window", 400))
        out: list[dict] = []
        for stem, (rel, off, surface) in self.first_term.items():
            explained = self.introduced(stem, rel, off, window)
            door = "gloss" if explained else "unglossed"
            out.append({
                "term": surface, "kind": "term", "uses": self.term_uses[stem],
                "door": door, "file": rel, "line": self.lines[rel].line(off),
                "definition": " ".join(
                    gloss_span(self.text[rel], off, window).split()),
            })
        for abbr, (rel, off) in self.first_abbrev.items():
            out.append({
                "term": abbr, "kind": "abbreviation",
                "uses": self.abbrev_uses[abbr],
                "door": ("expanded" if self.expanded_by_first_use(
                              abbr, rel, off)
                         else "declared" if abbr in self.std.abbrev_exempt
                         else "unexpanded"),
                "file": rel, "line": self.lines[rel].line(off),
                "definition": " ".join(
                    gloss_span(self.text[rel], off, window).split()),
            })
        return sorted(out, key=lambda e: e["term"].lower())

    @staticmethod
    def guide_blocks() -> str:
        """The parts of the guide that are really data, regenerated.

        The guide quotes the graded word lists so an author can read them
        in one place; those lists live in the artifact. Delimited regions
        plus a doctor check are what keep the two from drifting, which they
        already had once.
        """
        data = json.loads(LEXICON.read_text())

        def names(kind: str, grade: str) -> list[str]:
            return sorted(s["from"] for s in data[kind]
                          if s["grade"] == grade)

        out = ["<!-- sbe:generated:lists — regenerate with "
               "`uv run --group sbe scripts/check_simplified.py "
               "--emit-guide-blocks` -->"]
        for grade, gloss in (
                ("error", "fails `--strict`; no defensible use in trade prose"),
                ("warn", "usually the wrong word, sometimes exactly right"),
                ("idea", "shown only with `--advisory`")):
            words = names("substitutions", grade)
            phrases = names("phrase_substitutions", grade)
            out.append(f"\n**`{grade}`** — {gloss}.\n")
            if words:
                out.append(f"- {len(words)} words: "
                           + ", ".join(f"*{w}*" for w in words))
            if phrases:
                out.append(f"- {len(phrases)} phrases: "
                           + ", ".join(f"*{p}*" for p in phrases))
        c = data["counts"]
        out.append(f"\nTiers: **{c['core']:,}** core forms, "
                   f"**{c['open']:,}** open, "
                   f"**{c.get('recognized', 0):,}** OpenGloss-recognized, "
                   f"**{c['sensitive']}** sensitive; "
                   f"**{c['substitutions']}** word and "
                   f"**{c['phrase_substitutions']}** phrase substitutions "
                   f"(lexicon v{data['version']}, built {data['built']}).")
        out.append("<!-- /sbe:generated -->")
        return "\n".join(out)

    def emit_config(self) -> str:
        terms = [(self.term_uses[s], self.first_term[s][2])
                 for s in self.first_term
                 if any(f.kind == "unintroduced term" for f in self.findings)]
        flagged = {f.subject for f in self.findings
                   if f.kind == "unintroduced term" and f.subject}
        abbrevs = sorted({f.subject for f in self.findings
                          if f.kind == "undefined abbreviation" and f.subject})
        lines = ["simplified_english:", "  terms:"]
        for _, surface in sorted(terms, reverse=True):
            if surface in flagged:
                lines.append(f'    - term: "{surface}"')
        lines.append("  abbreviations: ["
                     + ", ".join(f'"{a}"' for a in abbrevs) + "]")
        return "\n".join(lines)


SKIP = re.compile(r"^\w$")


def in_proper_name(text: str, m: re.Match) -> bool:
    """Is this match inside a capitalized phrase — a name, not diction?

    "Payment in Lieu of Taxes (PILOT)" is an instrument, not a way of
    saying "instead of".
    """
    if any(TITLE_WORD.match(w) for w in m.group(0).split()):
        before = text[max(0, m.start() - 40):m.start()].split()
        after = text[m.end():m.end() + 40].split()
        if (before and TITLE_WORD.match(before[-1])) or (
                after and TITLE_WORD.match(after[0])):
            return True
    return False


def is_abbreviation(std: Standard, text: str, m: re.Match, abbr: str) -> bool:
    """Distinguish an acronym from a name, a numeral, or a shouted word."""
    if not ABBREV_OK.match(abbr) or len(abbr) < 3:
        return False
    if ROMAN.match(abbr):                     # Louis XIV, Book XIII
        return False
    # A bare all-cap spelling of an ordinary word is often emphasis or a
    # protocol command (NEVER, AND, POWER, GET). A lowercase plural or
    # possessive suffix is different evidence: APIs, SATs, RAND's. Do not let
    # the lowercase frequency entry erase those abbreviation/name decisions.
    if std.listed(abbr.lower()) and m.group(0) == abbr:
        return False
    # Domain names and product model designators are proper names, not forms
    # that can be expanded: LWN.net, GTX 580. The exact spelling still belongs
    # in `names:` when it appears bare elsewhere.
    if re.match(r"\.[a-z]{2,}\b", text[m.end():m.end() + 12]):
        return False
    # HOSTS.TXT, report.PDF: an all-cap filename suffix is a code component,
    # not an abbreviation the author can expand in prose.
    if m.start() > 0 and text[m.start() - 1] == ".":
        return False
    if re.match(r"\s+\d{2,}\b", text[m.end():m.end() + 12]):
        return False
    after = text[m.end():m.end() + 30].split()
    # "GeForce GTX", "POWER Act" are names — but not "The QRST rule", where
    # the capital belongs to the sentence, not to a name.
    prev = None
    for w in words(text[max(0, m.start() - 40):m.start()]):
        prev = (w.group(0), max(0, m.start() - 40) + w.start())
    prev_is_name = bool(prev and NAME_WORD.match(prev[0])
                        and not is_sentence_start(text, prev[1]))
    if prev_is_name or (after and NAME_WORD.match(after[0])):
        return False
    return True


INITIAL_SKIP = frozenset((
    "a", "an", "the", "of", "in", "on", "at", "to", "for", "and", "or", "but",
    "is", "are", "was", "were", "be", "by", "it", "its", "as", "that", "this",
))


def collect_expansions(
        text: str) -> tuple[dict[str, list[int]], dict[str, list[int]]]:
    """Every shape of "this is what the letters stand for" we can detect.

    Both forms carry their position so the caller can enforce expansion at
    first use instead of letting a later definition rewrite book history.
    """
    explicit: dict[str, list[int]] = {}
    patterns = (
        r"\(([A-Z]{3,7})s?\)",
        r"\b([A-Z]{3,7})\s*\((?=[A-Za-z])",
        r",\s*or\s+([A-Z]{3,7})s?\s*,",
        r"\b(?:often\s+)?abbreviated\s+(?:as\s+)?([A-Z]{3,7})\b",
    )
    for pattern in patterns:
        for m in re.finditer(pattern, text):
            explicit.setdefault(m.group(1), []).append(m.start(1))

    spans = [(m.group(0), m.start(), m.end()) for m in words(text)]
    initialisms: dict[str, list[int]] = {}
    for i, (word, pos, _end) in enumerate(spans):
        if len(word) < 3 or word.lower() in INITIAL_SKIP:
            continue

        # Writers build initials in several legitimate ways. FERC drops "of";
        # NPOV keeps it; ENIAC keeps "and"; INUS capitalizes only the four
        # defined components in a longer explanatory phrase. Generate all
        # three readings, but only within one sentence and a short window.
        all_letters: list[str] = []
        content_letters: list[str] = []
        capital_letters: list[str] = []
        whole_all: list[str] = []
        whole_content: list[str] = []
        whole_capital: list[str] = []
        previous_end = pos
        for j in range(i, min(i + 12, len(spans))):
            nxt, nxt_pos, nxt_end = spans[j]
            if j > i and re.search(r"[.!?]", text[previous_end:nxt_pos]):
                break
            previous_end = nxt_end
            parts = [part for part in nxt.split("-") if part]
            whole_letter = nxt[0].upper()
            whole_all.append(whole_letter)
            if nxt.lower() not in INITIAL_SKIP:
                whole_content.append(whole_letter)
            if nxt[0].isupper():
                whole_capital.append(whole_letter)
            for part in parts:
                if not part or not part[0].isalpha():
                    continue
                letter = part[0].upper()
                all_letters.append(letter)
                if part.lower() not in INITIAL_SKIP:
                    content_letters.append(letter)
                if part[0].isupper():
                    capital_letters.append(letter)
            for letters in (all_letters, content_letters, capital_letters,
                            whole_all, whole_content, whole_capital):
                if 2 <= len(letters) <= 7:
                    initialisms.setdefault("".join(letters), []).append(pos)
    return explicit, initialisms


# --------------------------------------------------------------------- main

_INPUT = re.compile(r"\\(?:input|include)\s*\{([^{}]+)\}")


def included_tex_files(main: Path, include_matter: bool,
                       *, latex: Path = LATEX) -> list[Path]:
    """Return included prose files in reading order, following LaTeX inputs.

    Legacy books do not have book.yaml edition manifests. Their `main.tex` is
    the authoritative table of contents, and a directory glob silently pulls
    in commented-out specimens and abandoned drafts. Follow the actual input
    graph when it is available; keep the glob fallback for partial projects.
    """
    allowed = set(SUBDIRS if include_matter else ("chapters",))
    seen: set[Path] = set()
    ordered: list[Path] = []

    def visit(path: Path) -> None:
        path = path.resolve()
        if path in seen or not path.is_file():
            return
        seen.add(path)
        try:
            rel = path.relative_to(latex.resolve())
        except ValueError:
            rel = None
        if rel is not None and rel.parts and rel.parts[0] in allowed:
            ordered.append(path)
        try:
            raw = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return
        raw = _COMMENT.sub("", raw)
        for match in _INPUT.finditer(raw):
            target = match.group(1).strip()
            if not target or "\\" in target:
                continue
            child = Path(target)
            if child.suffix != ".tex":
                child = child.with_suffix(".tex")
            candidates = (latex / child, path.parent / child)
            visit(next((candidate for candidate in candidates
                        if candidate.is_file()), candidates[0]))

    visit(main)
    return ordered


def chapter_files(include_matter: bool, *, latex: Path = LATEX) -> list[Path]:
    """Included chapters by default; optionally include front/back matter."""
    main = latex / "main.tex"
    if main.is_file() and (included := included_tex_files(
            main, include_matter, latex=latex)):
        return included
    subs = SUBDIRS if include_matter else ("chapters",)
    files: list[Path] = []
    for sub in subs:
        d = latex / sub
        if d.is_dir():
            files += sorted(d.glob("*.tex"))
    return files


def book_order(files: list[Path], cfg: dict, *, latex: Path = LATEX) -> list[Path]:
    """Reading order, so "first use in the book" means what it says.

    `main.tex` input traversal is already authoritative. If discovery had to
    fall back to a directory glob, book.yaml's default edition supplies the
    best available order.
    """
    main = latex / "main.tex"
    if main.is_file():
        included = included_tex_files(main, include_matter=False, latex=latex)
        if included and [p.resolve() for p in files] == included:
            return files
    editions = (cfg or {}).get("editions") or {}
    order: list[str] = []
    for ed in editions.values():
        if isinstance(ed, dict) and ed.get("default"):
            order = [str(c) for c in (ed.get("chapters") or [])]
            break
    if not order:
        return files
    rank = {name: i for i, name in enumerate(order)}
    return sorted(files, key=lambda p: (
        min((rank[k] for k in rank if p.name.startswith(k)), default=10**6),
        p.name))


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", type=Path)
    ap.add_argument("--strict", action="store_true",
                    help="warnings fail the run too")
    ap.add_argument("--advisory", action="store_true",
                    help="also report idea-grade swaps and single-use terms")
    ap.add_argument("--all", action="store_true", dest="all_matter",
                    help="include front matter and back matter")
    ap.add_argument("--stats", action="store_true",
                    help="tier coverage per file; no findings")
    ap.add_argument("--markers", action="store_true",
                    help="register-marker counts that produce the score")
    ap.add_argument("--terms", action="store_true",
                    help="the term work list, most-used first")
    ap.add_argument("--emit-config", action="store_true", dest="emit_config",
                    help="a book.yaml block seeded from the findings")
    ap.add_argument("--emit-guide-blocks", action="store_true",
                    dest="emit_guide",
                    help="regenerate the generated regions of "
                         "docs/guides/SIMPLIFIED-ENGLISH.md")
    ap.add_argument("--glossary", action="store_true",
                    help="JSON glossary worklist: every candidate term, its "
                         "first use, and its explanation status")
    ap.add_argument("--suppressions", action="store_true",
                    help="list every %% sbe-ok line and its reason")
    ap.add_argument("--explain", nargs="+", metavar="WORD",
                    help="which tier these words are in, and why")
    ap.add_argument("--format", choices=("human", "grep", "jsonl"),
                    default="human")
    ap.add_argument("--root", type=Path,
                    help="check another book built from this template")
    args = ap.parse_args()

    root = args.root.resolve() if args.root else ROOT
    latex = root / "latex"
    book_yaml = root / "book.yaml"

    cfg = {}
    if book_yaml.exists():
        try:
            cfg = yaml.safe_load(book_yaml.read_text()) or {}
        except yaml.YAMLError as e:
            sys.exit(f"check_simplified: {book_yaml} is not valid YAML: {e}")
    std = Standard(cfg, advisory=args.advisory)

    if args.emit_guide:
        print(Book.guide_blocks())
        return

    if args.explain:
        for supplied in args.explain:
            token = supplied.strip()
            phrase = " ".join(token.casefold().split())
            if " " in phrase and phrase in std.opengloss_phrases:
                print(f"{supplied:<24} {'recognized phrase':<16} exact "
                      "OpenGloss phrase entry — dictionary recognition, not "
                      "an audience-familiarity decision")
                continue
            abbr_match = ABBREV_TOKEN.fullmatch(token)
            if abbr_match:
                abbr = abbr_match.group(1)
                if abbr in std.name_exempt:
                    print(f"{supplied:<24} {'name':<16} official all-cap name "
                          "declared in book.yaml")
                    continue
                if (abbr in std.abbrev_exempt
                        or abbr.lower() in std.declared):
                    print(f"{supplied:<24} {'abbreviation':<16} allowed bare "
                          "by the shared or book vocabulary")
                    continue
                # A suffix makes abbreviation/name intent explicit even when
                # the lowercase base happens to be an ordinary lexicon word.
                # For a bare form, mirror is_abbreviation's lexical filters.
                if (not ROMAN.match(abbr)
                        and (token != abbr or not std.listed(abbr.lower()))):
                    print(f"{supplied:<24} {'abbreviation':<16} expand at first "
                          "use, or declare under abbreviations/names")
                    continue
            word = normalize(supplied)
            tier = std.tier(word)
            note = {
                "core": "core lexicon — free to use",
                "open": "ordinary English beyond the core — free to use",
                "recognized": ("OpenGloss headword outside the ordinary-"
                               "corpus tiers — review this use in context"),
                "declared": "declared in book.yaml — free after introduction",
                "unlisted": ("not found in OpenGloss or the corpus tiers — "
                             "review as a term, coined form, name, or error"),
                "sensitive": "slur or outdated term — quote, frame, or replace",
            }[tier]
            if word in std.words:
                grade, better = std.words[word]
                note = f"{grade}: replace with {better}"
                tier = f"{tier}/banned"
            print(f"{supplied:<24} {tier:<16} {note}")
        return

    whole_book = not args.files
    files = args.files or chapter_files(args.all_matter, latex=latex)
    for f in files:
        if not f.is_file():
            sys.exit(f"check_simplified: not a readable file: {f}")
    if not files:
        sys.exit("check_simplified: no chapter files found under latex/")
    if not std.enabled:
        print("check_simplified: disabled in book.yaml "
              "(simplified_english.enabled: false)")
        return
    files = book_order(files, cfg, latex=latex) if whole_book else files

    book = Book(files, std, partial=not whole_book, root=root)
    findings = book.findings
    totals = book.counts
    errors = [f for f in findings if f.severity == "error"]
    warns = [f for f in findings if f.severity == "warn"]

    def finish() -> None:
        if errors or (args.strict and warns):
            sys.exit(1)

    if args.suppressions:
        for rel, line, reason in book.suppression_log:
            print(f"{rel}:{line}: sbe-ok — {reason}")
        print(f"check_simplified: {len(book.suppression_log)} suppression(s)")
        return finish()

    if args.emit_config:
        print(book.emit_config())
        return finish()

    if args.glossary:
        print(json.dumps(book.glossary(), indent=1, ensure_ascii=False))
        return finish()

    if args.terms:
        rows = []
        for f in findings:
            if f.kind != "unintroduced term" or not f.subject:
                continue        # the "N more not shown" notice quotes nothing
            key = stem_key(normalize(f.subject))
            rows.append((book.term_uses.get(key, 0), f))
        for _, f in sorted(rows, key=lambda r: (-r[0], r[1].file, r[1].line)):
            print(f.render("jsonl" if args.format == "jsonl" else "grep"))
        return finish()

    if args.markers:
        counted = sum(totals[k] for k in
                      ("core", "open", "recognized", "declared",
                       "unlisted")) or 1
        print("check_simplified: register markers")
        for marker, count in book.marker_uses.most_common():
            print(f"  {marker:<28} {count:5d}  {count / counted * 1000:6.2f}/1k")
    elif args.stats:
        print("check_simplified: tier coverage")
        for name, c in book.per_file:
            total = sum(c[k] for k in ("core", "open", "recognized",
                                       "declared", "unlisted")) or 1
            print(f"  {name:<44} core {c['core'] / total:6.1%}  "
                  f"open {c['open'] / total:6.1%}  "
                  f"recognized {c['recognized'] / total:6.1%}  "
                  f"unlisted {c['unlisted'] / total:6.1%}  "
                  f"names {c['name']}")
    else:
        for f in sorted(findings, key=lambda f: (f.file, f.line)):
            print(f.render(args.format))

    counted = sum(totals[k] for k in
                  ("core", "open", "recognized", "declared", "unlisted"))
    if args.format != "jsonl":
        if findings:
            by_kind: Counter[tuple[str, str]] = Counter(
                (f.kind, f.severity) for f in findings)
            print("  " + ";  ".join(
                f"{n} {kind}{'' if sev == 'error' else f' ({sev})'}"
                for (kind, sev), n in by_kind.most_common()))
        if not counted:
            print(f"check_simplified: {len(files)} file(s), no prose found "
                  f"[lexicon v{std.version}, built {std.built}]")
            return finish()
        unlisted = totals["unlisted"] / counted
        markers = book.markers / counted * 1000
        print(f"check_simplified: {len(files)} file(s), {counted} words "
              f"(+{totals['name']} names), core {totals['core'] / counted:.1%}, "
              f"OpenGloss-recognized {totals['recognized'] / counted:.2%}, "
              f"unlisted {unlisted:.2%}, register markers {markers:.2f}/1k, "
              f"{len(errors)} error(s), "
              f"{len(warns)} warning(s), "
              f"{len(book.suppression_log)} suppressed "
              f"[lexicon v{std.version}, built {std.built}]")
    finish()


if __name__ == "__main__":
    main()
