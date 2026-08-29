# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""export_ssrn_metadata.py — paste-ready SSRN submission dossier.

Writes SSRN-METADATA.md at the repo root: every field the SSRN submission
form wants, each on a single unwrapped line so it pastes cleanly (the
convention from journalists/us-data-center-opposition/SSRN-METADATA.md).
Reads paper.yaml so the dossier can never drift from the built PDF.

    uv run scripts/export_ssrn_metadata.py

SSRN (guidelines updated 2026-06-15) takes a PDF, wants title + authors +
affiliations + emails on the page, keywords, optional JEL codes, and — when
AI was used — an explicit AI-disclosure statement. This dossier collects all
of that; the built PDF (make ssrn) supplies the rest.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PAPER_YAML = ROOT / "paper.yaml"
OUT = ROOT / "SSRN-METADATA.md"


def one_line(text: str) -> str:
    return " ".join((text or "").split())


def main() -> None:
    if not PAPER_YAML.exists():
        print("export_ssrn_metadata: paper.yaml not found", file=sys.stderr)
        sys.exit(1)
    cfg = yaml.safe_load(PAPER_YAML.read_text())
    p = cfg["paper"]
    ssrn = (cfg.get("venue", {}) or {}).get("ssrn", {}) or {}
    title = p["title"]
    if p.get("subtitle"):
        title = f"{title}: {p['subtitle']}"

    authors = cfg["authors"]
    author_lines = []
    for a in authors:
        bits = [a["name"]]
        if a.get("affiliation"):
            bits.append(a["affiliation"])
        if a.get("email"):
            bits.append(a["email"])
        if a.get("orcid"):
            bits.append(f"ORCID {a['orcid']}")
        author_lines.append(" — ".join(bits))

    kws = ", ".join(cfg.get("classification", {}).get("keywords", []) or [])
    jel = cfg.get("classification", {}).get("jel", []) or []
    date = p.get("date") or "(build date — rebuild the PDF the day you upload; "\
        "the title page is dated \\today)"

    disc = cfg.get("disclosure", {}) or {}
    lines = [
        f"# SSRN Submission Metadata — {p['title']}",
        "",
        "Paste-ready fields for the SSRN submission form. Every field is a "
        "single unwrapped line/paragraph so it pastes cleanly. Generated from "
        "`paper.yaml` by `scripts/export_ssrn_metadata.py` — regenerate after "
        "any edit so this never drifts from the built PDF.",
        "",
        "## Title",
        "",
        one_line(title),
        "",
    ]
    if ssrn.get("prior_subtitle"):
        lines += [
            f"(Prior working subtitle, reversible in one edit: "
            f"\"{one_line(ssrn['prior_subtitle'])}\". SSRN's 2026-06-15 "
            "guidelines disfavor \"framework\"-style subtitles among content "
            "not typically accepted; the contribution remains inside.)",
            "",
        ]
    lines += [
        "## Authors",
        "",
        *[f"- {ln}" for ln in author_lines],
        "",
        "## Date written",
        "",
        one_line(date),
        "",
        "## Abstract",
        "",
        one_line(cfg["abstract"]),
        "",
        "## Keywords",
        "",
        kws or "(none set)",
        "",
    ]
    if jel:
        lines += ["## JEL classification codes", "",
                  *[f"- {c}" for c in jel], ""]
    lines += [
        "## Declarations",
        "",
        f"- Funding: {one_line(disc.get('funding', 'none to declare'))}.",
        f"- Competing interests: {one_line(disc.get('competing_interests', 'none to declare'))}.",
        f"- Data availability: {one_line(disc.get('data_availability', ''))}",
    ]
    if disc.get("ai_used"):
        lines.append(
            f"- AI disclosure (REQUIRED by SSRN when AI was used; also a "
            f"first-page footnote in the PDF): {one_line(disc.get('ai_statement', ''))}")
    else:
        lines.append("- AI disclosure: no AI used in preparation.")

    related = ssrn.get("related") or []
    if related:
        lines += ["", "## Related SSRN papers (link on the submission)", ""]
        for r in related:
            bits = [one_line(r.get("title", ""))]
            if r.get("abstract_id"):
                bits.append(f"SSRN abstract {r['abstract_id']}")
            if r.get("note"):
                bits.append(one_line(r["note"]))
            lines.append("- " + " — ".join(b for b in bits if b))
    networks = ssrn.get("networks") or []
    if networks:
        lines += ["", "## Suggested SSRN networks / eJournals", ""]
        lines += [f"- {one_line(n)}" for n in networks]

    lines += [
        "",
        "## Submission notes",
        "",
        "- Upload `build/latex/main.pdf` (PDF only; SSRN does not take LaTeX).",
        "- Paper type: working paper.",
        "- If `paper.date` is empty in `paper.yaml`, the title page uses "
        "`\\today` — rebuild (`make ssrn`) the day you upload so the page "
        "date matches SSRN's metadata.",
    ]
    OUT.write_text("\n".join(lines) + "\n")
    print(f"export_ssrn_metadata: wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
