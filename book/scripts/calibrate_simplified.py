#!/usr/bin/env python3
"""Run the held-out Simplified Book English calibration suite.

The nine projects are siblings in the author's workspace, not fixtures copied
into this repository. This runner makes the scorecard repeatable while keeping
their prose out of the template. It exits loudly when a project is absent
unless `--allow-missing` is requested for another machine.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import yaml

import check_simplified as sbe


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PROJECTS_ROOT = ROOT.parent
PROJECTS = (
    ("Foundations", "foundations-book", "latex"),
    ("AI Professional Services", "ai-professional-services-book", "latex"),
    ("History Through RFCs", "history-through-rfc-book", "latex"),
    ("Wiki History", "wiki-history-book", "latex"),
    ("Data Center 2026", "datacenter-2026-book", "latex"),
    ("HTSD", "htsd-book", "latex"),
    ("Legal Tech History", "legal-tech-history-book", "latex"),
    ("Agents in Law and Finance",
     "ai-law-finance-book/minibooks/agents-in-law-finance", "agents"),
    ("Complexity / Pop Science", "complexity-book/pop-sci-book", "latex"),
)


@dataclass
class Score:
    book: str
    path: str
    files: int
    words: int
    names: int
    core_percent: float
    recognized_percent: float
    unlisted_percent: float
    markers_per_1k: float
    errors: int
    warnings: int
    terms: int
    abbreviations: int
    substitutions: int
    other_findings: int


def finding_counts(findings: list[sbe.Finding]) -> dict[str, int]:
    """Group active findings into the three editorial work queues."""
    counts = {"terms": 0, "abbreviations": 0, "substitutions": 0,
              "other_findings": 0}
    for finding in findings:
        if finding.severity not in {"error", "warn"}:
            continue
        if finding.kind == "unintroduced term":
            counts["terms"] += 1
        elif finding.kind == "undefined abbreviation":
            counts["abbreviations"] += 1
        elif finding.kind in {"unapproved word", "unapproved phrase"}:
            counts["substitutions"] += 1
        else:
            counts["other_findings"] += 1
    return counts


def load_config(root: Path) -> dict:
    path = root / "book.yaml"
    if not path.is_file():
        return {}
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise SystemExit(f"calibrate_simplified: invalid YAML in {path}: {exc}")


def checked_book(root: Path, layout: str) -> tuple[sbe.Book, list[Path]]:
    """Load one calibration book through the same canonical-scope path."""
    latex = root / "latex"
    config = load_config(root)
    standard = sbe.Standard(config)
    if layout == "agents":
        files = sorted(
            path for path in (root / "chapters").rglob("*.tex")
            if "sections" in path.parts and "figures" not in path.parts
        )
        partial = True
    else:
        files = sbe.book_order(
            sbe.chapter_files(False, latex=latex), config, latex=latex
        )
        partial = False
    if not files:
        raise SystemExit(f"calibrate_simplified: no canonical prose in {root}")
    book = sbe.Book(files, standard, partial=partial, root=root)
    return book, files


def score_book(label: str, root: Path, layout: str) -> Score:
    book, files = checked_book(root, layout)
    counted = sum(book.counts[key]
                  for key in ("core", "open", "recognized", "declared",
                              "unlisted"))
    errors = sum(finding.severity == "error" for finding in book.findings)
    warnings = sum(finding.severity == "warn" for finding in book.findings)
    queues = finding_counts(book.findings)
    return Score(
        book=label,
        path=str(root),
        files=len(files),
        words=counted,
        names=book.counts["name"],
        core_percent=round(book.counts["core"] / counted * 100, 1),
        recognized_percent=round(
            book.counts["recognized"] / counted * 100, 2),
        unlisted_percent=round(book.counts["unlisted"] / counted * 100, 2),
        markers_per_1k=round(book.markers / counted * 1000, 2),
        errors=errors,
        warnings=warnings,
        **queues,
    )


def markdown(scores: list[Score]) -> str:
    lines = [
        "| Book | Words | Core | OpenGloss-recognized | Unlisted | Markers/1k | Errors / warnings |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for score in scores:
        lines.append(
            f"| {score.book} | {score.words:,} | {score.core_percent:.1f}% | "
            f"{score.recognized_percent:.2f}% | "
            f"{score.unlisted_percent:.2f}% | {score.markers_per_1k:.2f} | "
            f"{score.errors} / {score.warnings} |"
        )
    total_words = sum(score.words for score in scores)
    total_errors = sum(score.errors for score in scores)
    total_warnings = sum(score.warnings for score in scores)
    error_label = "error" if total_errors == 1 else "errors"
    warning_label = "warning" if total_warnings == 1 else "warnings"
    lines += ["", f"Total: {total_words:,} words; "
              f"{total_errors} {error_label}; "
              f"{total_warnings} {warning_label}."]
    lines += [
        "",
        "| Book | Terms | Abbreviations | Substitutions | Other |",
        "|---|---:|---:|---:|---:|",
    ]
    for score in scores:
        lines.append(
            f"| {score.book} | {score.terms} | {score.abbreviations} | "
            f"{score.substitutions} | {score.other_findings} |"
        )
    lines += [
        "",
        "Finding classes: "
        f"{sum(score.terms for score in scores)} terms; "
        f"{sum(score.abbreviations for score in scores)} abbreviations; "
        f"{sum(score.substitutions for score in scores)} substitutions; "
        f"{sum(score.other_findings for score in scores)} other.",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--projects-root", type=Path,
                        default=DEFAULT_PROJECTS_ROOT)
    parser.add_argument("--format", choices=("markdown", "json"),
                        default="markdown")
    parser.add_argument("--allow-missing", action="store_true")
    args = parser.parse_args()

    scores: list[Score] = []
    missing: list[Path] = []
    for label, relative, layout in PROJECTS:
        root = (args.projects_root / relative).resolve()
        if not root.is_dir():
            missing.append(root)
            continue
        scores.append(score_book(label, root, layout))
    if missing and not args.allow_missing:
        paths = "\n  ".join(str(path) for path in missing)
        sys.exit(f"calibrate_simplified: missing project(s):\n  {paths}")
    if args.format == "json":
        print(json.dumps({"scores": [asdict(score) for score in scores]},
                         indent=2))
    else:
        print(markdown(scores))


if __name__ == "__main__":
    main()
