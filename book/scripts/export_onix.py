# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0", "onixcheck>=0.9"]
# ///
"""ONIX 3.0 metadata export (`make onix`).

Generates one ONIX message from book.yaml — a Product record per
enabled format (print/epub/hardcover) — and validates it against the
official EDItEUR XSD via onixcheck before writing. This is the
machine-readable companion to the KDP/Bowker dossier: IngramSpark,
library channels (OverDrive etc.), and aggregators consume ONIX, Amazon
accepts ONIX 3.0/3.1 for Kindle since April 2025, and ONIX is the only
supply-chain channel for the EAA accessibility metadata (List 196) that
mirrors the EPUB's own conformance claim.

Codelist values used (verified against ns.editeur.org/onix/en/196 on
2026-07-07 — onixcheck validates XSD structure but NOT codelist
values, so re-verify these when EDItEUR revises the lists):
  List 196 (accessibility): 04 EPUB Accessibility 1.1 · 82 WCAG 2.2 ·
    85 WCAG level AA · 11 TOC navigation · 13 single logical reading
    order · 14 short alternative descriptions · 22 language tagging ·
    36 text-appearance modifiable
  List 150 (form): BC paperback · BB hardback · EB digital download
  List 175 (form detail): E101 EPUB

    uv run scripts/export_onix.py [--edition NAME] [--out build/onix/onix-30.xml]
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path
from xml.etree import ElementTree as ET

import yaml

ROOT = Path(__file__).resolve().parent.parent

LANG_639_2 = {"en": "eng", "es": "spa", "fr": "fre", "de": "ger",
              "it": "ita", "pt": "por", "nl": "dut", "ja": "jpn",
              "zh": "chi", "la": "lat", "ru": "rus", "ar": "ara"}
AUDIENCE_CODES = {"trade": "01", "academic": "06", "young-readers": "02"}

# EPUB accessibility (List 196) — must mirror what the EPUB's OPF
# claims (epub/converter/generators.py; the Ace gate backs both).
A11Y_CONFORMANCE = ["04", "82", "85"]   # EPUB a11y 1.1, WCAG 2.2, level AA
A11Y_FEATURES = ["11", "13", "14", "22", "36"]


def sub(parent, tag: str, text: str | None = None):
    el = ET.SubElement(parent, tag)
    if text is not None:
        el.text = text
    return el


def print_page_count() -> int | None:
    prints = sorted((ROOT / "build" / "latex").glob("book-print*.pdf"))
    if not prints:
        return None
    try:
        out = subprocess.run(["pdfinfo", str(prints[0])],
                             capture_output=True, text=True,
                             check=True).stdout
        return int(re.search(r"Pages:\s+(\d+)", out).group(1))
    except (OSError, subprocess.CalledProcessError, AttributeError):
        return None


def product(cfg: dict, form: str, isbn: str, pages: int | None) -> ET.Element:
    b = cfg["book"]
    digits = re.sub(r"[^0-9]", "", isbn)
    p = ET.Element("Product")
    sub(p, "RecordReference", f"{digits}-{form}")
    sub(p, "NotificationType", "03")  # confirmed record
    pid = sub(p, "ProductIdentifier")
    sub(pid, "ProductIDType", "15")   # ISBN-13
    sub(pid, "IDValue", digits)

    dd = sub(p, "DescriptiveDetail")
    sub(dd, "ProductComposition", "00")
    sub(dd, "ProductForm", form)
    if form == "EB":
        sub(dd, "ProductFormDetail", "E101")  # EPUB
        for code in A11Y_CONFORMANCE + A11Y_FEATURES:
            pff = sub(dd, "ProductFormFeature")
            sub(pff, "ProductFormFeatureType", "09")  # accessibility
            sub(pff, "ProductFormFeatureValue", code)

    td = sub(dd, "TitleDetail")
    sub(td, "TitleType", "01")
    te = sub(td, "TitleElement")
    sub(te, "TitleElementLevel", "01")
    sub(te, "TitleText", b["title"])
    if b.get("subtitle"):
        sub(te, "Subtitle", b["subtitle"])

    c = sub(dd, "Contributor")
    sub(c, "SequenceNumber", "1")
    sub(c, "ContributorRole", "A01")  # author
    sub(c, "PersonName", b["author"])

    lang = sub(dd, "Language")
    sub(lang, "LanguageRole", "01")
    primary = (b.get("language") or "en").split("-")[0].lower()
    sub(lang, "LanguageCode", LANG_639_2.get(primary, "eng"))

    if form in ("BC", "BB") and pages:
        ext = sub(dd, "Extent")
        sub(ext, "ExtentType", "00")   # main content page count
        sub(ext, "ExtentValue", str(pages))
        sub(ext, "ExtentUnit", "03")   # pages

    for code in cfg.get("classification", {}).get("bisac", []):
        s = sub(dd, "Subject")
        sub(s, "SubjectSchemeIdentifier", "10")  # BISAC
        sub(s, "SubjectCode", code)
    kws = cfg.get("classification", {}).get("keywords", [])
    if kws:
        s = sub(dd, "Subject")
        sub(s, "SubjectSchemeIdentifier", "20")  # keywords
        sub(s, "SubjectHeadingText", "; ".join(kws))
    aud = sub(dd, "Audience")
    sub(aud, "AudienceCodeType", "01")
    sub(aud, "AudienceCodeValue", AUDIENCE_CODES.get(
        cfg.get("classification", {}).get("audience", "trade"), "01"))

    cd = sub(p, "CollateralDetail")
    tc = sub(cd, "TextContent")
    sub(tc, "TextType", "03")          # description
    sub(tc, "ContentAudience", "00")   # unrestricted
    sub(tc, "Text", b["description"].strip())

    pd = sub(p, "PublishingDetail")
    if b.get("imprint"):
        imp = sub(pd, "Imprint")
        sub(imp, "ImprintName", b["imprint"])
    pub = sub(pd, "Publisher")
    sub(pub, "PublishingRole", "01")
    sub(pub, "PublisherName", b["publisher"])
    sub(pd, "PublishingStatus", "04")  # active
    pdate = sub(pd, "PublishingDate")
    sub(pdate, "PublishingDateRole", "01")
    d = sub(pdate, "Date", str(b["year"]))
    d.set("dateformat", "05")          # year only
    return p


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path,
                    default=ROOT / "build" / "onix" / "onix-30.xml")
    args = ap.parse_args()

    cfg = yaml.safe_load((ROOT / "book.yaml").read_text())
    ids = cfg.get("identifiers", {})
    formats = cfg.get("formats", {})
    pages = print_page_count()

    msg = ET.Element("ONIXMessage")
    msg.set("xmlns", "http://ns.editeur.org/onix/3.0/reference")
    msg.set("release", "3.0")
    header = sub(msg, "Header")
    sender = sub(header, "Sender")
    sub(sender, "SenderName", cfg["book"]["publisher"])
    sub(header, "SentDateTime", time.strftime("%Y%m%dT%H%M%S", time.gmtime()))

    n = 0
    plan = [("print", "BC", ids.get("isbn_print")),
            ("epub", "EB", ids.get("isbn_epub")),
            ("hardcover", "BB", ids.get("isbn_hardcover"))]
    for fmt, form, isbn in plan:
        if formats.get(fmt) and isbn:
            msg.append(product(cfg, form, isbn, pages))
            n += 1
    if n == 0:
        sys.exit("export_onix: no enabled format has an ISBN in book.yaml — "
                 "nothing to export")

    ET.indent(msg)
    xml = ET.tostring(msg, encoding="unicode", xml_declaration=True) + "\n"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(xml)

    import onixcheck
    errors = onixcheck.validate(str(args.out))
    for e in errors:
        print(f"export_onix: onixcheck: {e.short}", file=sys.stderr)
    if errors:
        sys.exit(f"export_onix: {len(errors)} validation error(s) — "
                 f"{args.out} does not conform to the ONIX 3.0 schema")
    print(f"export_onix: wrote {args.out.relative_to(ROOT)} "
          f"({n} product record(s), onixcheck valid)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
