# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Generate build metadata from paper.yaml (the single source of truth).

Outputs
-------
latex/generated/metadata.tex   LaTeX macros + \\ifPaper... flags consumed by
                               the preamble, title block, and back matter.
build/arxiv-readme.json        arXiv 00README.json (compiler + texlive version).

Usage
-----
    uv run scripts/generate_metadata.py
    uv run scripts/generate_metadata.py --print-engine      # for the Makefile
    uv run scripts/generate_metadata.py --print-bibengine   # bibtex|biber
    uv run scripts/generate_metadata.py --print-venue       # preprint|arxiv|ssrn
    uv run scripts/generate_metadata.py --allow-placeholders
    uv run scripts/generate_metadata.py --strict            # release gate

Any string value containing TODO/FIXME/XXX or [bracketed placeholder] fails
generation unless --allow-placeholders is given (the ADR-0002 rule, adapted).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PAPER_YAML = ROOT / "paper.yaml"
GENERATED = ROOT / "latex" / "generated"
BUILD = ROOT / "build"

ENGINES = ("pdflatex", "xelatex", "lualatex")
FONT_PROFILES = ("libertinus", "newtx", "lmodern", "plex")
BIB_SYSTEMS = ("natbib", "biblatex")
BIB_STYLES = ("numeric", "authoryear")
VENUES = ("preprint", "arxiv", "ssrn")
LINESPACING = ("single", "onehalf", "double")
BASE_SIZES = (10, 11, 12)
PAPER_SIZES = {"letter": "letterpaper", "a4": "a4paper"}
LICENSES = {
    "cc-by-4.0": "CC BY 4.0",
    "cc-by-sa-4.0": "CC BY-SA 4.0",
    "cc-by-nc-sa-4.0": "CC BY-NC-SA 4.0",
    "cc-by-nc-nd-4.0": "CC BY-NC-ND 4.0",
    "arxiv-nonexclusive": "arXiv.org perpetual, non-exclusive license",
    "cc0": "CC0 1.0 (public domain)",
}
# Font profiles that need an OpenType engine (not pdflatex).
OPENTYPE_ONLY = ("plex",)
# arXiv TeX Live version the toolchain targets (see docs/guides/SUBMISSION.md).
TEXLIVE_VERSION = 2025

PLACEHOLDER_RE = re.compile(r"TODO|FIXME|XXX|\[[A-Za-z][^\]]*\]")

TEX_SPECIALS = {
    "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
    "_": r"\_", "{": r"\{", "}": r"\}",
    "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    "\\": r"\textbackslash{}",
}


def tex_escape(value: str) -> str:
    return "".join(TEX_SPECIALS.get(ch, ch) for ch in str(value))


def fail(msg: str) -> None:
    print(f"generate_metadata: ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def get(cfg: dict, dotted: str, default=None, required=False):
    node = cfg
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            if required:
                fail(f"missing required field: {dotted}")
            return default
        node = node[part]
    return node


def scan_placeholders(node, path="") -> list[str]:
    hits = []
    if isinstance(node, dict):
        for k, v in node.items():
            hits += scan_placeholders(v, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            hits += scan_placeholders(v, f"{path}[{i}]")
    elif isinstance(node, str) and PLACEHOLDER_RE.search(node):
        hits.append(f"{path}: {node!r}")
    return hits


def validate(cfg: dict) -> None:
    for field in ("paper.title", "authors", "abstract",
                  "typography.engine", "typography.font_profile",
                  "citations.system", "venue.target"):
        get(cfg, field, required=True)

    authors = cfg.get("authors") or []
    if not isinstance(authors, list) or not authors:
        fail("authors must be a non-empty list")
    for i, a in enumerate(authors):
        if not isinstance(a, dict) or not a.get("name"):
            fail(f"authors[{i}] needs at least a name")

    checks = [
        ("typography.engine", ENGINES, None),
        ("typography.font_profile", FONT_PROFILES, None),
        ("typography.linespacing", LINESPACING, "single"),
        ("citations.system", BIB_SYSTEMS, None),
        ("citations.style", BIB_STYLES, "numeric"),
        ("venue.target", VENUES, None),
    ]
    for field, allowed, default in checks:
        val = get(cfg, field, default)
        if val not in allowed:
            fail(f"{field} must be one of {sorted(allowed)}, got {val!r}")

    if get(cfg, "typography.base_size", 11) not in BASE_SIZES:
        fail(f"typography.base_size must be one of {BASE_SIZES}")
    if get(cfg, "typography.paper_size", "letter") not in PAPER_SIZES:
        fail(f"typography.paper_size must be one of {sorted(PAPER_SIZES)}")

    engine = get(cfg, "typography.engine")
    profile = get(cfg, "typography.font_profile")
    if profile in OPENTYPE_ONLY and engine == "pdflatex":
        fail(f"font_profile {profile!r} is OpenType-only; set "
             "typography.engine to xelatex or lualatex")

    bg = get(cfg, "typography.title_background", "") or ""
    if bg:
        figs = ROOT / "latex" / "figures"
        if not any((figs / f"{bg}{ext}").exists()
                   for ext in (".pdf", ".png", ".jpg", ".jpeg")):
            fail(f"typography.title_background {bg!r} has no figure "
                 f"latex/figures/{bg}.(pdf|png|jpg) — run `make figures` "
                 "(the demo is figures/src/title-banner.tikz) or fix the name")

    venue = get(cfg, "venue.target")
    if venue == "arxiv":
        lic = get(cfg, "venue.license", "cc-by-4.0")
        if lic not in LICENSES:
            fail(f"venue.license must be one of {sorted(LICENSES)}, got {lic!r}")
        if engine == "lualatex":
            print("generate_metadata: WARNING: engine 'lualatex' is not named "
                  "in arXiv's supported-engines FAQ; pdflatex or xelatex are "
                  "the safe choices for arXiv source upload.", file=sys.stderr)

    for code in get(cfg, "classification.jel", []) or []:
        if not re.fullmatch(r"[A-Z]\d{2}", str(code)):
            fail(f"classification.jel entry {code!r} is not a JEL code (e.g. C88)")


def validate_strict(cfg: dict) -> None:
    """Release-gate checks: no placeholder identity, corresponding email set."""
    authors = cfg["authors"]
    corr = [a for a in authors if a.get("corresponding")] or [authors[0]]
    if not corr[0].get("email"):
        fail("[strict] the corresponding author needs an email")
    if get(cfg, "venue.target") == "ssrn":
        if get(cfg, "disclosure.ai_used") and not get(cfg, "disclosure.ai_statement"):
            fail("[strict] SSRN requires an AI-disclosure statement when "
                 "disclosure.ai_used is true (guidelines 2026-06-15)")


def bibengine(cfg: dict) -> str:
    """Which bibliography program the Makefile should run."""
    system = get(cfg, "citations.system")
    if system == "natbib":
        return "bibtex"
    # biblatex: SSRN cluster uses biber; arXiv-robust path could use bibtex,
    # but the house biblatex block below is biber-oriented.
    return "biber"


def author_macros(cfg: dict) -> dict[str, str]:
    """Build \\PaperAuthorPlain (comma-joined, for PDF metadata) and
    \\PaperAuthorFirst. The formatted title-block author list is
    \\PaperAuthorBlock, emitted by write_authors_block()."""
    authors = cfg["authors"]
    names = [a["name"] for a in authors]
    return {
        "PaperAuthorPlain": ", ".join(names),
        "PaperAuthorFirst": names[0],
    }


def build_macros(cfg: dict) -> dict[str, str]:
    p = cfg["paper"]
    title = p["title"]
    subtitle = p.get("subtitle", "")
    short = p.get("short_title") or title
    macros = {
        "PaperTitle": title,
        "PaperSubtitle": subtitle,
        "PaperShortTitle": short,
        "PaperDate": p.get("date", "") or r"\today",
        "PaperAbstract": cfg["abstract"].strip(),
        "PaperKeywords": ", ".join(get(cfg, "classification.keywords", []) or []),
        "PaperJEL": ", ".join(get(cfg, "classification.jel", []) or []),
        "PaperMSC": ", ".join(get(cfg, "classification.msc", []) or []),
        "PaperSeries": get(cfg, "venue.series", "") or "",
        "PaperEngine": get(cfg, "typography.engine"),
        "PaperFontProfile": get(cfg, "typography.font_profile"),
        "PaperLineSpacing": get(cfg, "typography.linespacing", "single"),
        "PaperBibSystem": get(cfg, "citations.system"),
        "PaperBibStyle": get(cfg, "citations.style", "numeric"),
        "PaperBibTitle": get(cfg, "citations.bibliography_title", "References"),
        "PaperVenue": get(cfg, "venue.target"),
        "PaperLicense": LICENSES.get(get(cfg, "venue.license", ""), ""),
        "PaperAIStatement": (get(cfg, "disclosure.ai_statement", "") or "").strip(),
        "PaperFunding": (get(cfg, "disclosure.funding", "") or "").strip(),
        "PaperCompeting": (get(cfg, "disclosure.competing_interests", "") or "").strip(),
        "PaperDataAvail": (get(cfg, "disclosure.data_availability", "") or "").strip(),
        "PaperBaseSize": f"{get(cfg, 'typography.base_size', 11)}pt",
        "PaperPaperOption": PAPER_SIZES[get(cfg, "typography.paper_size", "letter")],
        "PaperTitleBackground": get(cfg, "typography.title_background", "") or "",
    }
    macros.update(author_macros(cfg))
    return macros


def write_authors_block(cfg: dict, lines: list[str]) -> None:
    r"""Emit \PaperAuthorBlock, an authblk-independent title-block body.

    Renders each author's name, a superscript affiliation marker, and
    collects unique affiliations into a numbered list. The corresponding
    author's email + AI-disclosure footnote hang off the first \thanks.
    Emitted as a single macro so the title block stays engine-agnostic.
    """
    authors = cfg["authors"]
    # Deduplicate affiliations preserving order.
    affils: list[str] = []
    for a in authors:
        aff = a.get("affiliation", "")
        if aff and aff not in affils:
            affils.append(aff)

    def aff_index(a: dict) -> str:
        aff = a.get("affiliation", "")
        return str(affils.index(aff) + 1) if aff in affils and aff else ""

    corr_idx = next((i for i, a in enumerate(authors) if a.get("corresponding")), 0)
    ai_stmt = (get(cfg, "disclosure.ai_statement", "") or "").strip()
    ai_used = bool(get(cfg, "disclosure.ai_used"))

    name_parts = []
    for i, a in enumerate(authors):
        marker = aff_index(a)
        sup = f"\\textsuperscript{{{marker}}}" if len(affils) > 1 and marker else ""
        name = tex_escape(a["name"])
        orcid = a.get("orcid", "")
        orcid_tex = (f"\\,\\orcidlink{{{tex_escape(orcid)}}}" if orcid else "")
        thanks = ""
        if i == corr_idx:
            bits = []
            if a.get("email"):
                bits.append(f"Corresponding author: \\texttt{{{tex_escape(a['email'])}}}.")
            if ai_used and ai_stmt:
                bits.append(tex_escape(ai_stmt))
            if bits:
                thanks = f"\\thanks{{{' '.join(bits)}}}"
        name_parts.append(f"{name}{orcid_tex}{sup}{thanks}")

    body = [r"\newcommand{\PaperAuthorBlock}{%"]
    body.append(r"  {\large " + r" \quad ".join(name_parts) + r"\par}%")
    if affils:
        body.append(r"  \vspace{0.4em}{\small\color{text-muted}%")
        if len(affils) == 1:
            body.append("    " + tex_escape(affils[0]) + r"\par}%")
        else:
            items = [f"\\textsuperscript{{{i+1}}}{tex_escape(aff)}"
                     for i, aff in enumerate(affils)]
            body.append("    " + r"\quad ".join(items) + r"\par}%")
    body.append("}")
    lines.extend(body)


def write_metadata_tex(cfg: dict, macros: dict[str, str]) -> None:
    lines = [
        "% ------------------------------------------------------------",
        "% GENERATED by scripts/generate_metadata.py from paper.yaml.",
        "% Do not edit; do not commit. Regenerate with `make generated`.",
        "% ------------------------------------------------------------",
    ]
    for name, value in macros.items():
        # \today must not be escaped; emit it raw.
        if value == r"\today":
            lines.append(f"\\newcommand{{\\{name}}}{{\\today}}")
        else:
            lines.append(f"\\newcommand{{\\{name}}}{{{tex_escape(value)}}}")

    flags = {
        "PaperHasSubtitle": bool(macros["PaperSubtitle"]),
        "PaperHasKeywords": bool(macros["PaperKeywords"]),
        "PaperHasJEL": bool(macros["PaperJEL"]),
        "PaperHasMSC": bool(macros["PaperMSC"]),
        "PaperHasSeries": bool(macros["PaperSeries"]),
        "PaperVenueArxiv": macros["PaperVenue"] == "arxiv",
        "PaperVenueSSRN": macros["PaperVenue"] == "ssrn",
        "PaperVenuePreprint": macros["PaperVenue"] == "preprint",
        "PaperEnginePDF": macros["PaperEngine"] == "pdflatex",
        "PaperBibNatbib": macros["PaperBibSystem"] == "natbib",
        "PaperBibBiblatex": macros["PaperBibSystem"] == "biblatex",
        "PaperBibNumeric": macros["PaperBibStyle"] == "numeric",
        "PaperTwoColumn": bool(get(cfg, "typography.twocolumn", False)),
        "PaperHasTitleBackground": bool(macros["PaperTitleBackground"]),
        "PaperModuleBoxes": bool(get(cfg, "modules.boxes", True)),
        "PaperModuleCode": bool(get(cfg, "modules.code", True)),
        "PaperModuleAlgo": bool(get(cfg, "modules.algorithms", True)),
        "PaperModuleSI": bool(get(cfg, "modules.siunitx", True)),
        "PaperSortCites": bool(get(cfg, "citations.sort", True)),
        "PaperAIUsed": bool(get(cfg, "disclosure.ai_used", False)),
    }
    for name, on in flags.items():
        lines.append(f"\\newif\\if{name}\\{name}{'true' if on else 'false'}")

    write_authors_block(cfg, lines)

    GENERATED.mkdir(parents=True, exist_ok=True)
    (GENERATED / "metadata.tex").write_text("\n".join(lines) + "\n")


def write_arxiv_readme(cfg: dict) -> None:
    """Emit build/arxiv-readme.json (arXiv 00README.json, spec 1).

    make_arxiv.py copies this into the bundle as 00README.json so arXiv
    uses the intended compiler and TeX Live version.
    """
    engine = get(cfg, "typography.engine")
    compiler = {"pdflatex": "pdflatex", "xelatex": "xelatex",
                "lualatex": "lualatex"}[engine]
    data = {
        "spec_version": 1,
        "process": {"compiler": compiler},
        "sources": [{"filename": "main.tex", "usage": "toplevel"}],
        "texlive_version": TEXLIVE_VERSION,
        "stamp": True,
        "nohyperref": False,
    }
    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / "arxiv-readme.json").write_text(json.dumps(data, indent=2) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--allow-placeholders", action="store_true")
    ap.add_argument("--print-engine", action="store_true")
    ap.add_argument("--print-bibengine", action="store_true")
    ap.add_argument("--print-venue", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="release gate: identity + venue-required fields")
    args = ap.parse_args()

    if not PAPER_YAML.exists():
        fail("paper.yaml not found at repo root")
    cfg = yaml.safe_load(PAPER_YAML.read_text())
    validate(cfg)
    if args.strict:
        validate_strict(cfg)

    if args.print_engine:
        print(cfg["typography"]["engine"])
        return
    if args.print_bibengine:
        print(bibengine(cfg))
        return
    if args.print_venue:
        print(cfg["venue"]["target"])
        return

    hits = scan_placeholders(cfg)
    if hits and not args.allow_placeholders:
        for h in hits:
            print(f"  placeholder: {h}", file=sys.stderr)
        fail("paper.yaml contains placeholder values (see above); "
             "fill them in or pass --allow-placeholders")

    macros = build_macros(cfg)
    write_metadata_tex(cfg, macros)
    write_arxiv_readme(cfg)
    print(f"generated metadata: venue={macros['PaperVenue']} "
          f"engine={macros['PaperEngine']} font={macros['PaperFontProfile']} "
          f"bib={macros['PaperBibSystem']}/{macros['PaperBibStyle']}")


if __name__ == "__main__":
    main()
