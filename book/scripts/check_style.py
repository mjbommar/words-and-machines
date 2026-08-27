# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Style gate for chapters (docs/guides/STYLE.md + STYLE-AI-TELLS.md).

Doc-as-lint-config: banned words/phrases are parsed from the fenced
```banned-words / ```banned-phrases blocks in STYLE.md, and mechanical
AI-tell regexes from the ```tell-patterns block in STYLE-AI-TELLS.md —
the guides and this checker cannot drift apart.

Style profiles (docs/guides/styles/<name>.md, selected by book.yaml's
`style.profile`) layer register-specific deltas on that base: fenced
```banned-words-add / ```banned-words-remove (and -phrases- twins)
adjust the lists, and a ```style-targets YAML block can override
`tell_budget` and set `sentence_hard_max` (long-sentence warnings).
No profile selected = base STYLE.md behavior, unchanged.

Also enforces the authoring contract's "forbidden in chapters" list
(docs/architecture/authoring-contract.md) and the no-literal-metadata
rule (ADR 0002).

Banned words/phrases and forbidden constructs are errors. AI-tell
pattern matches are budgeted per STYLE-AI-TELLS.md's linter notes:
each match is reported, but the run fails only when a chapter exceeds
the tell budget (or immediately with --strict-tells). Long-sentence
findings are warnings, never errors — sentence extraction from LaTeX
is approximate. Code-listing bodies are excluded from prose checks.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

TELL_BUDGET = 3  # default tell matches allowed per chapter before failing

ROOT = Path(__file__).resolve().parent.parent
# Every prose file in latex/chapters/, not just chNN-*.tex. The original glob
# was "ch*.tex", which silently skipped interchapters (ib-*.tex, ic-*.tex …),
# prologues and epilogues. An unchecked chapter is worse than an unwritten one:
# it reads as gated when nothing gated it.
CHAPTERS = sorted(
    p for p in (ROOT / "latex" / "chapters").glob("*.tex") if not p.name.startswith("_")
)
STYLE_MD = ROOT / "docs" / "guides" / "STYLE.md"
TELLS_MD = ROOT / "docs" / "guides" / "STYLE-AI-TELLS.md"
STYLES_DIR = ROOT / "docs" / "guides" / "styles"

FORBIDDEN_CONSTRUCTS = [
    (r"\\vspace\b", "manual spacing (\\vspace) — adjust styling.tex instead"),
    (r"\\newcommand\b", "\\newcommand in chapter — define in preamble/commands.tex"),
    (r"\\renewcommand\b", "\\renewcommand in chapter"),
    (r"\\bfseries\b", "\\bfseries — use \\keyterm or semantic markup"),
    (r"\\begin\{tikzpicture\}", "raw TikZ in chapter — put figures in latex/figures/"),
    (r"\\definecolor\b", "hard-coded color in chapter"),
    (r"\\(?:small|large|Large|footnotesize|scriptsize|huge|Huge)\b",
     "manual font sizing in chapter"),
]

CODE_ENVS = ("codelisting", "promptcode", "outputcode", "verbatim", "lstlisting")


def fenced_block(path: Path, tag: str) -> list[str]:
    if not path.exists():
        return []
    m = re.search(rf"```{tag}\n(.*?)```", path.read_text(), re.DOTALL)
    if not m:
        return []
    return [ln.strip() for ln in m.group(1).splitlines()
            if ln.strip() and not ln.strip().startswith("#")]


def strip_for_prose(text: str) -> str:
    """Remove comments and code-environment bodies before prose checks."""
    text = re.sub(r"(?<!\\)%.*", "", text)
    for env in CODE_ENVS:
        text = re.sub(rf"\\begin\{{{env}\}}.*?\\end\{{{env}\}}", " ",
                      text, flags=re.DOTALL)
    return text


def load_profile(cfg: dict) -> tuple[str | None, Path | None]:
    """(profile name, profile path) from book.yaml `style.profile`."""
    name = (cfg.get("style") or {}).get("profile")
    if not name:
        return None, None
    path = STYLES_DIR / f"{name}.md"
    if not path.exists():
        available = sorted(p.stem for p in STYLES_DIR.glob("*.md")
                           if p.stem != "README")
        sys.exit(f"check_style: style.profile {name!r} has no profile file "
                 f"docs/guides/styles/{name}.md "
                 f"(available: {', '.join(available) or 'none'})")
    return name, path


def apply_deltas(base: list[str], adds: list[str],
                 removes: list[str]) -> list[str]:
    """Base list + profile adds, minus profile removes (case-insensitive)."""
    gone = {r.lower() for r in removes}
    merged = [w for w in base if w.lower() not in gone]
    have = {w.lower() for w in merged}
    merged += [w for w in adds if w.lower() not in have]
    return merged


def profile_targets(path: Path) -> dict:
    """The ```style-targets YAML block of a profile (may be absent)."""
    m = re.search(r"```style-targets\n(.*?)```", path.read_text(), re.DOTALL)
    if not m:
        return {}
    data = yaml.safe_load(m.group(1)) or {}
    if not isinstance(data, dict):
        sys.exit(f"check_style: {path.name} style-targets block must be a "
                 "YAML mapping")
    return data


# Inline commands whose argument is prose; used when flattening LaTeX
# for the approximate sentence-length check.
_INLINE_CMD = re.compile(
    r"\\(?:emph|term|work|person|keyterm|foreignphrase|code|textbf|texttt)"
    r"\{([^{}]*)\}")


def long_sentences(prose: str, limit: int) -> list[tuple[int, int, str]]:
    """(approx line, word count, head) for sentences over *limit* words.
    Approximate by design — LaTeX flattening and sentence splitting are
    both heuristic, which is why findings are warnings, not errors."""
    hits = []
    lines = prose.splitlines()
    para: list[str] = []
    para_start = 1
    for i, line in enumerate(lines + [""], 1):
        if line.strip():
            if not para:
                para_start = i
            para.append(line.strip())
            continue
        if para:
            flat = " ".join(para)
            for _ in range(3):
                flat = _INLINE_CMD.sub(r"\1", flat)
            flat = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})*",
                          " ", flat)
            flat = re.sub(r"[{}~]", " ", flat)
            for sent in re.split(r"(?<=[.!?])\s+(?=[A-Z“\"])", flat):
                words = len(sent.split())
                if words > limit:
                    hits.append((para_start, words,
                                 " ".join(sent.split()[:8]) + "…"))
            para = []
    return hits


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--strict-tells", action="store_true",
                    help="any AI-tell match fails (default: budgeted)")
    args = ap.parse_args()

    if not CHAPTERS:
        sys.exit("check_style: no chapters found in latex/chapters/")

    banned_words = fenced_block(STYLE_MD, "banned-words")
    banned_phrases = fenced_block(STYLE_MD, "banned-phrases")
    tell_patterns = fenced_block(TELLS_MD, "tell-patterns")
    artifact_patterns = fenced_block(TELLS_MD, "artifact-patterns")
    if not banned_words:
        print("check_style: WARNING no banned-words block found in "
              "docs/guides/STYLE.md — banned-word checks skipped",
              file=sys.stderr)

    cfg = yaml.safe_load((ROOT / "book.yaml").read_text())

    # Style profile (docs/guides/styles/): register deltas over the base.
    profile_name, profile_path = load_profile(cfg)
    tell_budget = TELL_BUDGET
    sentence_hard_max = None
    if profile_path:
        banned_words = apply_deltas(
            banned_words,
            fenced_block(profile_path, "banned-words-add"),
            fenced_block(profile_path, "banned-words-remove"))
        banned_phrases = apply_deltas(
            banned_phrases,
            fenced_block(profile_path, "banned-phrases-add"),
            fenced_block(profile_path, "banned-phrases-remove"))
        targets = profile_targets(profile_path)
        tell_budget = int(targets.get("tell_budget", TELL_BUDGET))
        if targets.get("sentence_hard_max"):
            sentence_hard_max = int(targets["sentence_hard_max"])

    # Literal metadata strings (ADR 0002): title/author belong in macros.
    #
    # Exception, opt-in per book: when the title is also the name of the book's
    # subject — a place, a person, a ship — running prose cannot avoid it, and
    # \BookTitle in a sentence would be wrong the moment the book is retitled.
    # Set `style.title_is_subject: true` in book.yaml to drop the title (never
    # the author) from this check. ADR 0002's own wording is "literal
    # occurrences … in places that should use macros"; running prose is not one
    # of those places.
    literals = [cfg["book"]["title"], cfg["book"]["author"]]
    if (cfg.get("style") or {}).get("title_is_subject"):
        literals = [cfg["book"]["author"]]

    word_res = [(w, re.compile(rf"\b{re.escape(w)}\b", re.IGNORECASE))
                for w in banned_words]
    phrase_res = [(p, re.compile(re.escape(p), re.IGNORECASE))
                  for p in banned_phrases]
    tell_res = []
    for pat in tell_patterns:
        try:
            tell_res.append((pat, re.compile(pat, re.IGNORECASE)))
        except re.error as e:
            print(f"check_style: WARNING bad tell-pattern {pat!r}: {e}",
                  file=sys.stderr)
    # Machine artifacts (STYLE-AI-TELLS.md "zero tolerance" block): chatbot
    # residue — markdown leaks, oaicite/turn0search tokens, curly quotes,
    # emoji. Never budgeted: any match is an error.
    artifact_res = []
    for pat in artifact_patterns:
        try:
            artifact_res.append((pat,
                re.compile(pat, re.IGNORECASE | re.MULTILINE)))
        except re.error as e:
            print(f"check_style: WARNING bad artifact-pattern {pat!r}: {e}",
                  file=sys.stderr)

    violations = 0
    tell_total = 0
    for chapter in CHAPTERS:
        raw = chapter.read_text()
        prose = strip_for_prose(raw)
        rel = chapter.relative_to(ROOT)
        tells_here = 0

        def report(line_no: int, msg: str, rel: Path = rel) -> None:
            nonlocal violations
            violations += 1
            print(f"{rel}:{line_no}: {msg}")

        for i, line in enumerate(raw.splitlines(), 1):
            if line.lstrip().startswith("%"):
                continue
            for pat, why in FORBIDDEN_CONSTRUCTS:
                if re.search(pat, line):
                    report(i, f"forbidden construct: {why}")

        for i, line in enumerate(prose.splitlines(), 1):
            for word, rx in word_res:
                if rx.search(line):
                    report(i, f"banned word: {word!r}")
            for phrase, rx in phrase_res:
                if rx.search(line):
                    report(i, f"banned phrase: {phrase!r}")
            for pat, rx in tell_res:
                if rx.search(line):
                    tells_here += 1
                    print(f"{rel}:{i}: AI-tell (budgeted): /{pat[:60]}/")
            for pat, rx in artifact_res:
                if rx.search(line):
                    report(i, f"machine artifact: /{pat[:60]}/")
            for lit in literals:
                if lit and lit in line:
                    report(i, f"literal metadata string {lit!r} — "
                              "use \\BookTitle/\\BookAuthor macros")

        tell_total += tells_here
        if tells_here and (args.strict_tells or tells_here > tell_budget):
            violations += tells_here
            print(f"{rel}: {tells_here} AI-tell match(es) "
                  f"{'(strict mode)' if args.strict_tells else f'(budget {tell_budget})'}")

        if sentence_hard_max:
            for line_no, words, head in long_sentences(prose,
                                                       sentence_hard_max):
                print(f"{rel}:{line_no}: WARN sentence ~{words} words "
                      f"(profile ceiling {sentence_hard_max}): {head}")

    if violations:
        sys.exit(f"check_style: {violations} violation(s)")
    profile_note = f", profile {profile_name!r}" if profile_name else ""
    print(f"check_style: OK ({len(CHAPTERS)} chapters, "
          f"{len(banned_words)} banned words, {len(banned_phrases)} banned "
          f"phrases, {len(tell_res)} tell patterns, "
          f"{len(artifact_res)} artifact patterns, "
          f"{tell_total} budgeted tell match(es){profile_note})")


if __name__ == "__main__":
    main()
