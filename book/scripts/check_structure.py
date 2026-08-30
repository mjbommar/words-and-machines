#!/usr/bin/env python3
"""Audit the book-scale spine and chapter heading hierarchy.

This checker deliberately covers structural facts that prose/style checkers do
not: the public Part/chapter/section spine, local subsection discipline, and
heading length.  It cannot decide whether a section belongs in the argument;
the editorial pass must still read every section in order.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CHAPTERS = ROOT / "latex" / "chapters"
HEADING = re.compile(r"^\\(chapter|section|subsection)(\*)?\{([^{}]*)\}")


def words(title: str) -> int:
    plain = re.sub(r"\\[A-Za-z]+|[{}$]", " ", title)
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*", plain))


def edition_spine() -> list[str]:
    cfg = yaml.safe_load((ROOT / "book.yaml").read_text())
    editions = cfg.get("editions") or {}
    default = next((e for e in editions.values() if (e or {}).get("default")), {})
    parts = default.get("parts") or []
    findings = []
    if len(parts) != 4:
        findings.append(f"default edition has {len(parts)} parts; expected 4")
    seen = []
    for i, part in enumerate(parts, 1):
        if not str(part.get("title") or "").strip():
            findings.append(f"part {i} has no title")
        if not part.get("chapters"):
            findings.append(f"part {i} has no chapters")
        seen.extend(part.get("chapters") or [])
    expected = [f"ch{i:02d}" for i in range(1, 17)]
    if seen != expected:
        findings.append(f"part chapter order is {seen}; expected {expected}")
    return findings


def glossary_index_contract() -> list[str]:
    findings = []
    glossary_path = ROOT / "glossary.yaml"
    data = yaml.safe_load(glossary_path.read_text()) or {}
    terms = [str(e.get("term") or "").strip()
             for e in data.get("entries", []) if isinstance(e, dict)]
    if len(terms) < 50:
        findings.append(
            f"glossary has {len(terms)} entries; whole-book pass requires at least 50")
    source = "\n".join(path.read_text() for path in sorted(CHAPTERS.glob("ch*.tex")))
    raw_entries = re.findall(r"\\indexentry\{([^{}|]+)(?:\|[^{}]+)?\}", source)
    heads = {entry.split("!", 1)[0].casefold() for entry in raw_entries}
    for term in terms:
        if term.casefold() not in heads:
            findings.append(f"glossary term has no print-index locator: {term}")
    return findings


def audit_file(path: Path) -> list[str]:
    findings = []
    headings = []
    for line_no, line in enumerate(path.read_text().splitlines(), 1):
        match = HEADING.match(line)
        if match:
            headings.append((match.group(1), bool(match.group(2)),
                             match.group(3), line_no))
    chapters = [h for h in headings if h[0] == "chapter"]
    if len(chapters) != 1 or chapters[0][3] != 1:
        findings.append(f"{path.name}: chapter heading must be the first line")
    current_section = None
    subsection_count = 0
    sections = []
    for kind, starred, title, line_no in headings:
        prefix = f"{path.name}:{line_no}"
        if starred:
            findings.append(f"{prefix}: starred structural heading")
        limit = {"chapter": 9, "section": 10, "subsection": 12}[kind]
        if words(title) > limit:
            findings.append(
                f"{prefix}: {kind} title has {words(title)} words (limit {limit}): {title}")
        if title.rstrip().endswith((".", ":", ";", "?", "!")):
            findings.append(f"{prefix}: heading ends with punctuation: {title}")
        if kind == "section":
            if current_section is not None and subsection_count > 6:
                findings.append(
                    f"{path.name}:{current_section}: section has {subsection_count} subsections (limit 6)")
            current_section, subsection_count = line_no, 0
            sections.append(title)
        elif kind == "subsection":
            if current_section is None:
                findings.append(f"{prefix}: subsection appears before any section")
            subsection_count += 1
    if current_section is not None and subsection_count > 6:
        findings.append(
            f"{path.name}:{current_section}: section has {subsection_count} subsections (limit 6)")
    if not sections or sections[-1] != "Exercises":
        findings.append(f"{path.name}: final section must be Exercises")
    if len(sections) < 6 or len(sections) > 16:
        findings.append(
            f"{path.name}: {len(sections)} sections outside working range 6..16")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true",
                        help="exit nonzero when findings remain")
    args = parser.parse_args()
    findings = edition_spine() + glossary_index_contract()
    files = sorted(CHAPTERS.glob("ch*.tex"))
    for path in files:
        findings.extend(audit_file(path))
    for finding in findings:
        print(f"structure: {finding}")
    print(f"check_structure: {len(files)} chapters, {len(findings)} finding(s)")
    return 1 if args.strict and findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
