# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Generate build metadata from book.yaml (the single source of truth).

Outputs
-------
latex/generated/metadata.tex   LaTeX macros consumed by preamble, front matter, cover
latex/generated/edition.tex    ordered \\input list for the selected edition
build/epub-metadata.json       normalized metadata for the EPUB converter

Usage
-----
    uv run scripts/generate_metadata.py [--edition NAME] [--allow-placeholders]
    uv run scripts/generate_metadata.py --print-engine     # for Makefile
    uv run scripts/generate_metadata.py --emit-kdp         # KDP.md skeleton

Any string value containing TODO/FIXME/XXX or [bracketed placeholder] fails
generation unless --allow-placeholders is given (ADR 0002).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
BOOK_YAML = ROOT / "book.yaml"
GENERATED = ROOT / "latex" / "generated"
BUILD = ROOT / "build"

TRIM_PRESETS = {
    "6x9": (6.0, 9.0),
    "7x10": (7.0, 10.0),
    "5.5x8.5": (5.5, 8.5),
    "5x8": (5.0, 8.0),
    "8.5x11": (8.5, 11.0),  # textbook/workbook; KDP "large trim" pricing tier
}
FONT_PROFILES = ("libertinus", "garamond", "plex")
ENGINES = ("lualatex", "xelatex")
CITATION_STYLES = ("authoryear", "superscript")
AUDIENCES = ("trade", "academic", "young-readers")
PAPERS = ("white", "cream", "standard-color", "premium-color")

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


SAMPLE_ISBN_PREFIX = "9798000000"  # the template's shipped sample block


def isbn13_valid(isbn: str) -> bool:
    digits = re.sub(r"[-\s]", "", isbn)
    if not re.fullmatch(r"97[89]\d{10}", digits):
        return False
    total = sum(int(d) * (1 if i % 2 == 0 else 3)
                for i, d in enumerate(digits[:12]))
    return int(digits[12]) == (10 - total % 10) % 10


def validate_isbns(cfg: dict) -> None:
    """Any non-empty ISBN must be a well-formed ISBN-13 (always enforced)."""
    for field in ("isbn_print", "isbn_epub", "isbn_hardcover"):
        val = get(cfg, f"identifiers.{field}", "")
        if val and not isbn13_valid(val):
            fail(f"identifiers.{field}: {val!r} is not a valid ISBN-13 "
                 "(13 digits starting 978/979 with correct check digit)")
    for name, ed in cfg.get("editions", {}).items():
        for field in ("isbn_print", "isbn_epub"):
            val = (ed or {}).get(field, "")
            if val and not isbn13_valid(val):
                fail(f"editions.{name}.{field}: {val!r} is not a valid ISBN-13")


def validate_strict(cfg: dict) -> None:
    """Release-gate checks: real ISBNs must exist for every enabled format."""
    if get(cfg, "formats.print", False) and not get(cfg, "identifiers.isbn_print"):
        fail("[strict] formats.print is true but identifiers.isbn_print is empty")
    if get(cfg, "formats.epub", False) and not get(cfg, "identifiers.isbn_epub"):
        fail("[strict] formats.epub is true but identifiers.isbn_epub is empty")
    if get(cfg, "formats.hardcover", False) and not get(cfg, "identifiers.isbn_hardcover"):
        fail("[strict] formats.hardcover is true but identifiers.isbn_hardcover is empty")
    for field in ("isbn_print", "isbn_epub", "isbn_hardcover"):
        val = re.sub(r"[-\s]", "", get(cfg, f"identifiers.{field}", "") or "")
        if val.startswith(SAMPLE_ISBN_PREFIX):
            fail(f"[strict] identifiers.{field} still carries the template's "
                 "sample ISBN block — assign a real ISBN before release")


def validate(cfg: dict) -> None:
    for field in ("book.title", "book.author", "book.publisher", "book.year",
                  "book.description", "book.language", "trim.preset",
                  "typography.font_profile", "typography.engine",
                  "citations.style", "editions"):
        get(cfg, field, required=True)

    checks = [
        ("trim.preset", TRIM_PRESETS, None),
        ("typography.font_profile", FONT_PROFILES, None),
        ("typography.engine", ENGINES, None),
        ("citations.style", CITATION_STYLES, None),
        ("trim.paper", PAPERS, "white"),
        ("classification.audience", AUDIENCES, "trade"),
    ]
    for field, allowed, default in checks:
        val = get(cfg, field, default)
        if val not in allowed:
            fail(f"{field} must be one of {sorted(allowed)}, got {val!r}")

    if get(cfg, "typography.base_size", 11) not in (10, 11, 12):
        fail("typography.base_size must be 10, 11, or 12")
    if get(cfg, "modules.verse", False) and get(cfg, "typography.engine") != "xelatex":
        fail("modules.verse requires typography.engine: xelatex (polyglossia)")

    kws = get(cfg, "classification.keywords", [])
    if len(kws) > 7:
        fail("classification.keywords: KDP allows at most 7")
    for kw in kws:
        if len(kw) > 50:
            fail(f"keyword exceeds KDP 50-char limit: {kw!r}")
    if len(get(cfg, "classification.bisac", [])) > 3:
        fail("classification.bisac: at most 3 codes")

    if not isinstance(get(cfg, "publishing.kindle_drm", False), bool):
        fail("publishing.kindle_drm must be true or false")
    validate_ai_disclosure(get(cfg, "publishing.ai_disclosure", None))

    profile = get(cfg, "style.profile", None)
    if profile:
        styles = ROOT / "docs" / "guides" / "styles"
        if not (styles / f"{profile}.md").exists():
            available = sorted(p.stem for p in styles.glob("*.md")
                               if p.stem != "README")
            fail(f"style.profile {profile!r} has no profile file "
                 f"docs/guides/styles/{profile}.md "
                 f"(available: {', '.join(available) or 'none'})")


AI_LEVELS = ("none", "assisted", "generated")
AI_TYPES = ("text", "images", "translations")


def validate_ai_disclosure(decl) -> None:
    """Structured form mirrors KDP's questionnaire (per content type,
    generated-vs-assisted). A bare string (legacy) is accepted as the
    copyright-page statement with the per-type answers left open."""
    if decl is None or isinstance(decl, str):
        return
    if not isinstance(decl, dict):
        fail("publishing.ai_disclosure must be a string or a mapping")
    allowed = set(AI_TYPES) | {"detail", "statement"}
    for key in decl:
        if key not in allowed:
            fail(f"publishing.ai_disclosure.{key}: unknown key "
                 f"(allowed: {sorted(allowed)})")
    for t in AI_TYPES:
        val = decl.get(t, "none")
        if val not in AI_LEVELS:
            fail(f"publishing.ai_disclosure.{t} must be one of "
                 f"{AI_LEVELS}, got {val!r}")


def ai_disclosure_parts(cfg: dict) -> tuple[str, dict | None]:
    """(copyright-page statement, per-type answers or None-if-legacy)."""
    decl = get(cfg, "publishing.ai_disclosure", None)
    if decl is None:
        return "", None
    if isinstance(decl, str):
        return decl.strip(), None
    types = {t: decl.get(t, "none") for t in AI_TYPES}
    types["detail"] = (decl.get("detail") or "").strip()
    return (decl.get("statement") or "").strip(), types

    editions = cfg["editions"]
    defaults = [name for name, e in editions.items() if (e or {}).get("default")]
    if len(defaults) != 1:
        fail(f"exactly one edition must set default: true (found {len(defaults)})")
    chapter_re = re.compile(r"^ch\d{2}$")
    for name, ed in editions.items():
        chapters = (ed or {}).get("chapters") or []
        if not chapters:
            fail(f"edition {name!r} has no chapters")
        for ch in chapters:
            if not chapter_re.match(ch):
                fail(f"edition {name!r}: chapter id {ch!r} must match chNN")


def resolve_chapter_file(ch_id: str) -> Path:
    matches = sorted((ROOT / "latex" / "chapters").glob(f"{ch_id}-*.tex"))
    if not matches:
        fail(f"no chapter file latex/chapters/{ch_id}-*.tex")
    if len(matches) > 1:
        fail(f"ambiguous chapter id {ch_id}: {[m.name for m in matches]}")
    return matches[0]


def edition_config(cfg: dict, name: str | None) -> tuple[str, dict]:
    editions = cfg["editions"]
    if name is None:
        name = next(n for n, e in editions.items() if (e or {}).get("default"))
    if name not in editions:
        fail(f"unknown edition {name!r} (available: {', '.join(editions)})")
    return name, editions[name] or {}


def build_macros(cfg: dict, ed_name: str, ed: dict) -> dict[str, str]:
    b = cfg["book"]
    tw, th = TRIM_PRESETS[cfg["trim"]["preset"]]
    isbn_print = ed.get("isbn_print") or get(cfg, "identifiers.isbn_print", "")
    isbn_epub = ed.get("isbn_epub") or get(cfg, "identifiers.isbn_epub", "")
    return {
        "BookTitle": b["title"],
        "BookSubtitle": b.get("subtitle", ""),
        "BookAuthor": b["author"],
        "BookAuthorShort": b.get("author_short") or b["author"],
        "BookPublisher": b["publisher"],
        "BookImprint": b.get("imprint", ""),
        "BookYear": str(b["year"]),
        "BookEditionStatement": b.get("edition_statement", "First Edition"),
        "BookCopyrightHolder": b.get("copyright_holder") or b["author"],
        "BookDescription": b["description"].strip(),
        "BookLanguage": b.get("language", "en-US"),
        "BookISBNPrint": isbn_print,
        "BookISBNEpub": isbn_epub,
        "BookISBNHardcover": get(cfg, "identifiers.isbn_hardcover", ""),
        "BookLCCN": get(cfg, "identifiers.lccn", ""),
        "BookAIDisclosure": ai_disclosure_parts(cfg)[0],
        "BookEditionName": ed_name,
        "BookEditionSuffix": ed.get("title_suffix", ""),
        "BookFontProfile": cfg["typography"]["font_profile"],
        "BookCitationStyle": cfg["citations"]["style"],
        "BookBibTitle": get(cfg, "citations.bibliography_title", "Bibliography"),
        "BookTrimWidth": f"{tw}in",
        "BookTrimHeight": f"{th}in",
        "BookBleed": f"{get(cfg, 'trim.bleed', 0.125)}in",
        "BookPaper": get(cfg, "trim.paper", "white"),
        "BookBaseSize": f"{get(cfg, 'typography.base_size', 11)}pt",
    }


def write_metadata_tex(cfg: dict, macros: dict[str, str]) -> None:
    lines = [
        "% ------------------------------------------------------------",
        "% GENERATED by scripts/generate_metadata.py from book.yaml.",
        "% Do not edit; do not commit. Regenerate with `make generated`.",
        "% ------------------------------------------------------------",
    ]
    for name, value in macros.items():
        lines.append(f"\\newcommand{{\\{name}}}{{{tex_escape(value)}}}")
    # boolean flags
    flags = {
        "BookHasSubtitle": bool(macros["BookSubtitle"]),
        "BookHasImprint": bool(macros["BookImprint"]),
        "BookHasEditionSuffix": bool(macros["BookEditionSuffix"]),
        "BookHasAIDisclosure": bool(macros["BookAIDisclosure"]),
        "BookHasISBNPrint": bool(macros["BookISBNPrint"]),
        "BookHasLCCN": bool(macros["BookLCCN"]),
        "BookModuleCode": bool(get(cfg, "modules.code", False)),
        "BookModuleVerse": bool(get(cfg, "modules.verse", False)),
        "BookModuleBoxes": bool(get(cfg, "modules.boxes", True)),
    }
    for name, on in flags.items():
        lines.append(f"\\newif\\if{name}\\{name}{'true' if on else 'false'}")
    GENERATED.mkdir(parents=True, exist_ok=True)
    (GENERATED / "metadata.tex").write_text("\n".join(lines) + "\n")


def write_edition_tex(ed_name: str, ed: dict) -> list[str]:
    files = [resolve_chapter_file(ch) for ch in ed["chapters"]]
    lines = [
        f"% GENERATED edition '{ed_name}' — do not edit (see book.yaml editions).",
    ] + [f"\\input{{chapters/{f.stem}}}" for f in files]
    (GENERATED / "edition.tex").write_text("\n".join(lines) + "\n")
    return [f.name for f in files]


def write_epub_json(cfg: dict, macros: dict[str, str], ed_name: str,
                    chapter_files: list[str]) -> None:
    BUILD.mkdir(parents=True, exist_ok=True)
    data = {
        "title": macros["BookTitle"],
        "subtitle": macros["BookSubtitle"],
        "full_title": macros["BookTitle"]
        + (f": {macros['BookSubtitle']}" if macros["BookSubtitle"] else "")
        + (f" ({macros['BookEditionSuffix']})" if macros["BookEditionSuffix"] else ""),
        "author": macros["BookAuthor"],
        "publisher": macros["BookPublisher"],
        "year": int(macros["BookYear"]),
        "language": macros["BookLanguage"].lower(),
        "isbn": macros["BookISBNEpub"],
        "description": macros["BookDescription"],
        "ai_disclosure": macros["BookAIDisclosure"],
        "edition": ed_name,
        "edition_statement": macros["BookEditionStatement"],
        "copyright_holder": macros["BookCopyrightHolder"],
        "font_profile": macros["BookFontProfile"],
        "citation_style": macros["BookCitationStyle"],
        "bibliography_title": macros["BookBibTitle"],
        "keywords": get(cfg, "classification.keywords", []),
        "bisac": get(cfg, "classification.bisac", []),
        "chapters": chapter_files,
        "modules": {
            "code": bool(get(cfg, "modules.code", False)),
            "verse": bool(get(cfg, "modules.verse", False)),
            "boxes": bool(get(cfg, "modules.boxes", True)),
        },
    }
    (BUILD / "epub-metadata.json").write_text(json.dumps(data, indent=2) + "\n")


_AI_ANSWERS = {
    "none": "none",
    "assisted": "AI-assisted — no KDP disclosure required",
    "generated": "**AI-generated — disclose on the Content page**",
}


def ai_disclosure_lines(cfg: dict, macros: dict[str, str]) -> list[str]:
    statement, types = ai_disclosure_parts(cfg)
    if types is None:
        return [
            "- Per-type answers (text/images/translations) not declared —",
            "  classify per KDP-TEMPLATE.md section 6 before uploading",
            f"- Copyright-page statement: {statement or 'none declared'}",
        ]
    must = any(types[t] == "generated" for t in AI_TYPES)
    lines = [f"- Disclosure required: {'**yes**' if must else 'no'}"]
    lines += [f"- {t.capitalize()}: {_AI_ANSWERS[types[t]]}" for t in AI_TYPES]
    if types["detail"]:
        lines.append(f"- Extent (for the form's follow-ups): {types['detail']}")
    lines.append(f"- Copyright-page statement: {statement or 'none declared'}")
    return lines


def emit_kdp(cfg: dict, macros: dict[str, str]) -> None:
    target = ROOT / "docs" / "publishing" / "KDP.md"
    if target.exists():
        print(f"refusing to overwrite existing {target.relative_to(ROOT)}")
        return
    kws = get(cfg, "classification.keywords", [])
    lines = [
        f"# KDP Dossier — {macros['BookTitle']}",
        "",
        "Generated skeleton; edit freely (regenerating never overwrites).",
        "See docs/publishing/KDP-TEMPLATE.md for the full runbook.",
        "",
        "## Listing",
        f"- **Title:** {macros['BookTitle']}",
        f"- **Subtitle:** {macros['BookSubtitle'] or '—'}",
        f"- **Author:** {macros['BookAuthor']}",
        f"- **Description:** {macros['BookDescription']}",
        f"- **Language:** {macros['BookLanguage']}",
        f"- **ISBN (print):** {macros['BookISBNPrint'] or 'TBD'}",
        f"- **ISBN (ebook):** {macros['BookISBNEpub'] or 'TBD'}",
        "",
        "## Categories & keywords",
        f"- **BISAC:** {', '.join(get(cfg, 'classification.bisac', [])) or 'TBD'}",
        "- **Keywords (7 max, 50 chars each):**",
        *[f"  {i}. {kw} ({len(kw)} chars)" for i, kw in enumerate(kws, 1)],
        "",
        "## Print specs",
        f"- **Trim:** {get(cfg, 'trim.preset')} — {macros['BookPaper']} paper, "
        f"bleed {macros['BookBleed']}",
        "- **Spine width:** run `make cover-vars` after final page count",
        "",
        "## Kindle settings",
        f"- **DRM:** {'enabled' if get(cfg, 'publishing.kindle_drm', False) else 'disabled'}"
        " — effectively permanent per title; DRM-free titles are"
        " buyer-downloadable as EPUB/PDF (since 2026-01-20)",
        "",
        "## AI disclosure (KDP Content page)",
        *ai_disclosure_lines(cfg, macros),
        "",
        "## Pricing",
        f"- Print: {get(cfg, 'publishing.price_usd_print') or 'TBD'}",
        f"- Ebook: {get(cfg, 'publishing.price_usd_ebook') or 'TBD'}",
    ]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n")
    print(f"wrote {target.relative_to(ROOT)}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--edition", default=None)
    ap.add_argument("--allow-placeholders", action="store_true")
    ap.add_argument("--print-engine", action="store_true",
                    help="print the LaTeX engine and exit (for Makefile)")
    ap.add_argument("--emit-kdp", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="release gate: also require ISBNs for enabled formats")
    args = ap.parse_args()

    if not BOOK_YAML.exists():
        fail("book.yaml not found at repo root")
    cfg = yaml.safe_load(BOOK_YAML.read_text())
    validate(cfg)
    validate_isbns(cfg)
    if args.strict:
        validate_strict(cfg)

    if args.print_engine:
        print(cfg["typography"]["engine"])
        return

    hits = scan_placeholders(cfg)
    if hits and not args.allow_placeholders:
        for h in hits:
            print(f"  placeholder: {h}", file=sys.stderr)
        fail("book.yaml contains placeholder values (see above); "
             "fill them in or pass --allow-placeholders")

    ed_name, ed = edition_config(cfg, args.edition)
    macros = build_macros(cfg, ed_name, ed)
    write_metadata_tex(cfg, macros)
    chapter_files = write_edition_tex(ed_name, ed)
    write_epub_json(cfg, macros, ed_name, chapter_files)
    if args.emit_kdp:
        emit_kdp(cfg, macros)
    print(f"generated metadata for edition '{ed_name}' "
          f"({len(chapter_files)} chapters)")


if __name__ == "__main__":
    main()
