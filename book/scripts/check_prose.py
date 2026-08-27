#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pydetex>=1.1.1",
#     "nupunkt>=0.6.0",
# ]
# ///
"""Prose-repetition gate — pydetex LaTeX stripping + nupunkt segmentation.

Catches the failure modes that recur when parallel agents rewrite prose:
  - duplicate sentences (normalized, >= min-words)          [ERROR if cross-file]
  - repeated long n-grams across files (converging phrasing) [WARN; ERROR --strict]
  - adjacent sentences opening with the same word           [WARN]
  - monotonous sentence starts book-wide                    [WARN]

Why pydetex + nupunkt rather than a stdlib heuristic detexer:
  * pydetex understands LaTeX, so inline/display math ($61 \\cdot 53$,
    \\[ 1 + 1/4 + 1/9 \\]) and commands are removed properly instead of
    surfacing as phantom "repeated n-grams".
  * nupunkt does real sentence-boundary detection, so "Altdorf in 1667."
    or "Mr. Boole" don't split mid-sentence and manufacture false dups.

Severity model (so the gate is usable in CI): only the highest-confidence
signal — a duplicate SENTENCE repeated across two different files — fails
the build by default. Everything else is reported as a warning. `--strict`
also fails on cross-file n-gram echoes. A running motif or a twice-quoted
source will show as a warning, not a red build.

Layout-agnostic: scans latex/{chapters, frontmatter|front-matter,
backmatter|back-matter}/*.tex, so the same file works in book-template and
its downstream books. Override with explicit file args.

Usage:
    uv run scripts/check_prose.py                 # whole book, default gate
    uv run scripts/check_prose.py --strict        # n-gram echoes fail too
    uv run scripts/check_prose.py --format grep   # one finding per line
    uv run scripts/check_prose.py --format jsonl  # machine-readable
    uv run scripts/check_prose.py FILES...        # scan specific files
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from dataclasses import dataclass, asdict
from pathlib import Path

from pydetex import pipelines
from nupunkt import PunktSentenceTokenizer

ROOT = Path(__file__).resolve().parent.parent
LATEX = ROOT / "latex"
# both hyphenations, so this script is identical across books
SUBDIRS = ("chapters", "frontmatter", "front-matter", "backmatter", "back-matter")

# Non-prose environments dropped before pydetex (figures/code/math blocks
# and the house Proof-Kit boxes) so their contents never enter the corpus.
DROP_ENVS = (
    "tikzpicture", "figure", "table", "tabular", "tabularx", "lstlisting",
    "verbatim", "Verbatim", "equation", "align", "alignat", "gather",
    "definitionbox", "tryitbox", "examplebox", "codelisting", "promptcode",
    "outputcode",
)


def discover(root: Path) -> list[Path]:
    files: list[Path] = []
    for name in SUBDIRS:
        d = root / "latex" / name
        if d.exists():
            files += sorted(d.glob("*.tex"))
    return files


def strip_latex(text: str) -> str:
    """LaTeX -> plain prose. Pre-strip the things pydetex mishandles, then
    hand the rest to pydetex's strict pipeline (stdout muted: pydetex chatters
    about \\input resolution)."""
    text = re.sub(r"(?m)^%.*$", "", text)                    # line comments
    for env in DROP_ENVS:
        text = re.sub(rf"\\begin\{{{env}\*?\}}.*?\\end\{{{env}\*?\}}", " ",
                      text, flags=re.DOTALL)
    text = re.sub(r"\\\[.*?\\\]", " ", text, flags=re.DOTALL)  # display math
    text = re.sub(r"\$[^$]*\$", " ", text)                     # inline math
    # don't let pydetex load included figures/chapters into the prose
    text = re.sub(r"\\(?:input|include|includegraphics)(?:\[[^\]]*\])?\{[^}]*\}",
                  " ", text)
    with redirect_stdout(io.StringIO()):
        cleaned = pipelines.strict(text)
    return re.sub(r"\s+", " ", cleaned).strip()


def normalize(sentence: str) -> str:
    s = re.sub(r"[^a-z0-9\s]", "", sentence.lower())
    return re.sub(r"\s+", " ", s).strip()


@dataclass
class Finding:
    severity: str            # "error" | "warn"
    kind: str                # "dup-sentence" | "ngram-echo" | "opener-run" | "monotonous-start"
    message: str
    files: list[str]


def analyze(paths: list[Path], *, ngram: int, min_words: int,
            opener_run: int, strict: bool) -> list[Finding]:
    tok = PunktSentenceTokenizer()
    findings: list[Finding] = []

    sent_locations: dict[str, set[str]] = defaultdict(set)
    sent_display: dict[str, str] = {}
    ngram_files: dict[str, set[str]] = defaultdict(set)
    ngram_counts: Counter[str] = Counter()
    all_starts: Counter[tuple[str, ...]] = Counter()

    for path in paths:
        rel = str(path.relative_to(ROOT)) if ROOT in path.parents else path.name
        prose = strip_latex(path.read_text())
        sents = [s.strip() for s in tok.tokenize(prose)]

        seen_in_file: Counter[str] = Counter()
        for s in sents:
            norm = normalize(s)
            if len(norm.split()) < min_words:
                continue
            seen_in_file[norm] += 1
            sent_locations[norm].add(rel)
            sent_display.setdefault(norm, s)

        # within-file duplicate sentence -> warn (quoting-then-discussing is common)
        for norm, n in seen_in_file.items():
            if n > 1:
                findings.append(Finding(
                    "warn", "dup-sentence",
                    f"sentence repeated {n}x within file: "
                    f"\"{sent_display[norm][:90]}\"", [rel]))

        # adjacent same-opener runs -> warn (burstiness signal)
        openers = [normalize(s).split()[0] for s in sents
                   if len(normalize(s).split()) >= 4]
        run = 1
        for i in range(1, len(openers)):
            run = run + 1 if openers[i] == openers[i - 1] else 1
            if run == opener_run:
                findings.append(Finding(
                    "warn", "opener-run",
                    f"{opener_run} consecutive sentences open with "
                    f"{openers[i]!r}", [rel]))

        # collect cross-file n-grams and sentence starts
        words = normalize(prose).split()
        for i in range(len(words) - ngram + 1):
            g = " ".join(words[i:i + ngram])
            ngram_counts[g] += 1
            ngram_files[g].add(rel)
        for s in sents:
            w = normalize(s).split()
            if len(w) >= 4:
                all_starts[tuple(w[:4])] += 1

    # cross-file duplicate SENTENCE -> ERROR (the strong signal)
    for norm, files in sent_locations.items():
        if len(files) > 1:
            findings.append(Finding(
                "error", "dup-sentence",
                f"identical sentence in {len(files)} files: "
                f"\"{sent_display[norm][:90]}\"", sorted(files)))

    # cross-file n-gram echo -> WARN (ERROR under --strict)
    sev = "error" if strict else "warn"
    for gram, n in ngram_counts.items():
        files = ngram_files[gram]
        if len(files) > 1:
            findings.append(Finding(
                sev, "ngram-echo",
                f"{ngram}-gram echoed across {len(files)} files: \"{gram}\"",
                sorted(files)))

    # monotonous book-wide sentence starts -> WARN (top offenders only)
    for start, n in all_starts.most_common(8):
        if n >= 6:
            findings.append(Finding(
                "warn", "monotonous-start",
                f"{n} sentences open \"{' '.join(start)} ...\"", []))

    return findings


def emit(findings: list[Finding], fmt: str, n_files: int) -> None:
    errors = [f for f in findings if f.severity == "error"]
    warns = [f for f in findings if f.severity == "warn"]

    if fmt == "jsonl":
        for f in findings:
            print(json.dumps(asdict(f)))
        return
    if fmt == "grep":
        for f in findings:
            where = f.files[0] if f.files else "book"
            print(f"{where}:{f.severity}:{f.kind}: {f.message}")
        return

    # console
    order = {"dup-sentence": 0, "ngram-echo": 1, "opener-run": 2,
             "monotonous-start": 3}
    for f in sorted(findings, key=lambda x: (x.severity != "error",
                                             order.get(x.kind, 9))):
        tag = "ERROR" if f.severity == "error" else "warn "
        where = f" [{', '.join(f.files)}]" if f.files else ""
        print(f"  {tag}  {f.message}{where}")
    print()
    print(f"check_prose: {len(errors)} error(s), {len(warns)} warning(s) "
          f"across {n_files} files")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", help="tex files to scan (default: whole book)")
    ap.add_argument("--ngram", type=int, default=8, help="n-gram length (default 8)")
    ap.add_argument("--min-words", type=int, default=8,
                    help="min words for a sentence to count (default 8)")
    ap.add_argument("--opener-run", type=int, default=4,
                    help="flag N consecutive same-opener sentences (default 4)")
    ap.add_argument("--strict", action="store_true",
                    help="cross-file n-gram echoes fail the build too")
    ap.add_argument("--format", choices=("console", "grep", "jsonl"),
                    default="console")
    args = ap.parse_args()

    if args.files:
        paths = [Path(f) for f in args.files]
    else:
        paths = discover(ROOT)
    paths = [p for p in paths if p.exists()]
    if not paths:
        sys.exit("check_prose: no prose sources found")

    findings = analyze(paths, ngram=args.ngram, min_words=args.min_words,
                       opener_run=args.opener_run, strict=args.strict)
    emit(findings, args.format, len(paths))

    if any(f.severity == "error" for f in findings):
        sys.exit(1)


if __name__ == "__main__":
    main()
