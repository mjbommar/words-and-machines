"""generators.py — every packaged document that is not converted chapter
prose: container.xml, content.opf, nav.xhtml, toc.ncx, cover/title/
copyright pages, and the XHTML skeleton the chapters share.

Everything here is generated from build/epub-metadata.json — no static
templates with baked-in book strings (ADR 0002; the drift this rewrite
exists to eliminate). Provenance: the RFC book's generators.py had the
best OPF/nav approach of the four ancestor converters (ADR 0007).
"""

from __future__ import annotations

import html
import os
import re
import time
import uuid

_E = lambda s: html.escape(str(s), quote=True)  # noqa: E731


# ---------------------------------------------------------------------------
# Shared XHTML skeleton
# ---------------------------------------------------------------------------

def xhtml_page(title: str, body: str, lang: str, css: str = "epub.css") -> str:
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        "<!DOCTYPE html>\n"
        '<html xmlns="http://www.w3.org/1999/xhtml" '
        'xmlns:epub="http://www.idpf.org/2007/ops" '
        f'xml:lang="{_E(lang)}" lang="{_E(lang)}">\n'
        f"<head>\n<title>{_E(title)}</title>\n"
        f'<link rel="stylesheet" type="text/css" href="{css}"/>\n'
        f"</head>\n<body>\n{body}\n</body>\n</html>\n"
    )


# ---------------------------------------------------------------------------
# Identifier — ISBN when present (urn:isbn only if the checksum is real,
# so epubcheck's OPF-085 never fires on placeholder ISBNs)
# ---------------------------------------------------------------------------

def _isbn13_valid(digits: str) -> bool:
    if len(digits) != 13 or not digits.isdigit():
        return False
    total = sum(int(d) * (1 if i % 2 == 0 else 3)
                for i, d in enumerate(digits))
    return total % 10 == 0


def unique_identifier(meta: dict) -> str:
    isbn = (meta.get("isbn") or "").strip()
    digits = re.sub(r"[^0-9Xx]", "", isbn)
    if _isbn13_valid(digits):
        return f"urn:isbn:{digits}"
    if isbn:
        return isbn  # keep the ISBN visible even when not checksum-clean
    seed = f"{meta.get('title', '')}|{meta.get('author', '')}"
    return f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, seed)}"


# ---------------------------------------------------------------------------
# Static container pieces
# ---------------------------------------------------------------------------

def container_xml() -> str:
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<container version="1.0" '
        'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
        "  <rootfiles>\n"
        '    <rootfile full-path="OEBPS/content.opf" '
        'media-type="application/oebps-package+xml"/>\n'
        "  </rootfiles>\n</container>\n"
    )


# ---------------------------------------------------------------------------
# Front matter pages (all values from the metadata json)
# ---------------------------------------------------------------------------

def cover_page(meta: dict, cover_href: str, lang: str) -> str:
    body = (
        '<section epub:type="cover" class="cover-page">\n'
        f'<img class="cover-image" src="{cover_href}" '
        f'alt="Cover of {_E(meta["full_title"])}"/>\n</section>'
    )
    return xhtml_page("Cover", body, lang)


def titlepage(meta: dict, lang: str) -> str:
    lines = [f'<h1 class="book-title">{_E(meta["title"])}</h1>']
    if meta.get("subtitle"):
        lines.append(f'<p class="book-subtitle">{_E(meta["subtitle"])}</p>')
    lines.append(f'<p class="book-author">{_E(meta["author"])}</p>')
    if meta.get("publisher"):
        lines.append(f'<p class="book-publisher">{_E(meta["publisher"])}</p>')
    body = ('<section epub:type="titlepage" class="titlepage">\n'
            + "\n".join(lines) + "\n</section>")
    return xhtml_page(meta["title"], body, lang)


def copyright_page(meta: dict, lang: str) -> str:
    paras = [
        f'<p class="cp-title">{_E(meta["full_title"])}</p>',
        f'<p>Copyright &#169; {_E(meta["year"])} '
        f'{_E(meta["copyright_holder"])}. All rights reserved.</p>',
    ]
    statement = _E(meta.get("edition_statement", ""))
    publisher = _E(meta.get("publisher", ""))
    if statement and publisher:
        paras.append(f"<p>{statement}. Published by {publisher}.</p>")
    elif statement or publisher:
        paras.append(f"<p>{statement or publisher}</p>")
    if meta.get("isbn"):
        paras.append(f'<p>ISBN {_E(meta["isbn"])} (EPUB)</p>')
    # AI-disclosure paragraph, only when book.yaml declares one (ADR 0012).
    if (meta.get("ai_disclosure") or "").strip():
        paras.append(f'<p class="ai-disclosure">{_E(meta["ai_disclosure"])}</p>')
    body = ('<section epub:type="copyright-page" class="copyright">\n'
            + "\n".join(paras) + "\n</section>")
    return xhtml_page("Copyright", body, lang)


# ---------------------------------------------------------------------------
# Navigation: nav.xhtml (EPUB 3) + toc.ncx (legacy readers)
# ---------------------------------------------------------------------------

def nav_doc(meta: dict, entries: list[dict], first_chapter: str,
            lang: str) -> str:
    items = []
    for e in entries:
        sub = ""
        if e.get("children"):
            sub = ("\n<ol>\n" + "\n".join(
                f'<li><a href="{c["href"]}">{_E(c["label"])}</a></li>'
                for c in e["children"]) + "\n</ol>")
        items.append(f'<li><a href="{e["href"]}">{_E(e["label"])}</a>{sub}</li>')
    body = (
        '<nav epub:type="toc" role="doc-toc" id="toc">\n'
        "<h1>Contents</h1>\n<ol>\n" + "\n".join(items) + "\n</ol>\n</nav>\n"
        '<nav epub:type="landmarks" hidden="hidden">\n<h2>Landmarks</h2>\n<ol>\n'
        '<li><a epub:type="cover" href="cover.xhtml">Cover</a></li>\n'
        '<li><a epub:type="toc" href="nav.xhtml">Table of Contents</a></li>\n'
        f'<li><a epub:type="bodymatter" href="{first_chapter}">Begin Reading'
        "</a></li>\n</ol>\n</nav>"
    )
    return xhtml_page("Contents", body, lang)


def ncx_doc(meta: dict, uid: str, entries: list[dict]) -> str:
    points = []
    for i, e in enumerate(entries, 1):
        points.append(
            f'<navPoint id="np-{i}" playOrder="{i}">\n'
            f"<navLabel><text>{_E(e['label'])}</text></navLabel>\n"
            f'<content src="{e["href"]}"/>\n</navPoint>')
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">\n'
        "<head>\n"
        f'<meta name="dtb:uid" content="{_E(uid)}"/>\n'
        '<meta name="dtb:depth" content="1"/>\n'
        '<meta name="dtb:totalPageCount" content="0"/>\n'
        '<meta name="dtb:maxPageNumber" content="0"/>\n'
        "</head>\n"
        f"<docTitle><text>{_E(meta['full_title'])}</text></docTitle>\n"
        "<navMap>\n" + "\n".join(points) + "\n</navMap>\n</ncx>\n"
    )


# ---------------------------------------------------------------------------
# content.opf
# ---------------------------------------------------------------------------

_MEDIA_TYPES = {
    ".xhtml": "application/xhtml+xml",
    ".css": "text/css",
    ".ncx": "application/x-dtbncx+xml",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
}


def _item_id(href: str) -> str:
    return "item-" + re.sub(r"[^A-Za-z0-9.-]+", "-", href).strip("-")


def content_opf(meta: dict, uid: str, spine_hrefs: list[str],
                extra_hrefs: list[str], cover_href: str, lang: str) -> str:
    modified = time.strftime(
        "%Y-%m-%dT%H:%M:%SZ",
        time.gmtime(int(os.environ.get("SOURCE_DATE_EPOCH", time.time()))))

    md = [f'<dc:identifier id="pub-id">{_E(uid)}</dc:identifier>',
          f'<dc:title id="title">{_E(meta["title"])}</dc:title>',
          '<meta refines="#title" property="title-type">main</meta>']
    if meta.get("subtitle"):
        md += [f'<dc:title id="subtitle">{_E(meta["subtitle"])}</dc:title>',
               '<meta refines="#subtitle" property="title-type">subtitle</meta>']
    md += [f'<dc:creator id="creator">{_E(meta["author"])}</dc:creator>',
           '<meta refines="#creator" property="role" '
           'scheme="marc:relators">aut</meta>',
           f'<dc:language>{_E(lang)}</dc:language>',
           f'<dc:date>{_E(meta["year"])}</dc:date>']
    if meta.get("publisher"):
        md.append(f'<dc:publisher>{_E(meta["publisher"])}</dc:publisher>')
    if meta.get("description"):
        md.append(f'<dc:description>{_E(meta["description"])}</dc:description>')
    for kw in meta.get("keywords", []):
        md.append(f"<dc:subject>{_E(kw)}</dc:subject>")
    for i, code in enumerate(meta.get("bisac", []), 1):
        md += [f'<dc:subject id="subj-bisac-{i}">{_E(code)}</dc:subject>',
               f'<meta refines="#subj-bisac-{i}" property="authority">BISAC</meta>',
               f'<meta refines="#subj-bisac-{i}" property="term">{_E(code)}</meta>']
    md.append(f'<meta property="dcterms:modified">{modified}</meta>')
    # schema.org accessibility block (epub-pipeline.md; ADR 0007 gate).
    # Features listed here must describe what the converter actually
    # emits — the `make epub-a11y` Ace gate backs the conformance claim.
    has_images = any(h.startswith("images/") for h in extra_hrefs) or cover_href
    md += ['<meta property="schema:accessMode">textual</meta>']
    if has_images:
        md.append('<meta property="schema:accessMode">visual</meta>')
    md += ['<meta property="schema:accessModeSufficient">textual</meta>',
           '<meta property="schema:accessibilityFeature">tableOfContents</meta>',
           '<meta property="schema:accessibilityFeature">structuralNavigation</meta>',
           '<meta property="schema:accessibilityFeature">readingOrder</meta>',
           '<meta property="schema:accessibilityFeature">displayTransformability</meta>']
    if has_images:
        md.append('<meta property="schema:accessibilityFeature">alternativeText</meta>')
    md += ['<meta property="schema:accessibilityHazard">none</meta>',
           '<meta property="schema:accessibilitySummary">Reflowable text '
           "with structural navigation, chapter endnotes with backlinks, "
           "and described images.</meta>",
           # EPUB Accessibility 1.1 conformance claim (exact string form
           # from the spec); a11y/dcterms are reserved EPUB 3.3 prefixes.
           # A claim requires a certifier — self-certification is allowed.
           '<meta property="dcterms:conformsTo">'
           "EPUB Accessibility 1.1 - WCAG 2.2 Level AA</meta>",
           '<meta property="a11y:certifiedBy">'
           f'{_E(meta.get("publisher") or meta["author"])}</meta>',
           # EPUB2-reader cover hint (legacy meta is valid in EPUB 3).
           f'<meta name="cover" content="{_item_id(cover_href)}"/>']

    manifest = ['<item id="item-nav" href="nav.xhtml" '
                'media-type="application/xhtml+xml" properties="nav"/>',
                '<item id="ncx" href="toc.ncx" '
                'media-type="application/x-dtbncx+xml"/>',
                f'<item id="{_item_id(cover_href)}" href="{cover_href}" '
                f'media-type="{_MEDIA_TYPES[os.path.splitext(cover_href)[1]]}" '
                'properties="cover-image"/>']
    for href in spine_hrefs + [h for h in extra_hrefs if h != cover_href]:
        ext = os.path.splitext(href)[1].lower()
        manifest.append(f'<item id="{_item_id(href)}" href="{href}" '
                        f'media-type="{_MEDIA_TYPES[ext]}"/>')

    spine = [f'<itemref idref="{_item_id(h)}"/>' for h in spine_hrefs[:3]]
    spine.append('<itemref idref="item-nav"/>')  # visible Contents page
    spine += [f'<itemref idref="{_item_id(h)}"/>' for h in spine_hrefs[3:]]

    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" '
        f'unique-identifier="pub-id" xml:lang="{_E(lang)}">\n'
        '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
        + "\n".join(md) + "\n</metadata>\n<manifest>\n"
        + "\n".join(manifest) + "\n</manifest>\n"
        '<spine toc="ncx">\n' + "\n".join(spine) + "\n</spine>\n</package>\n"
    )


# ---------------------------------------------------------------------------
# Top-level: everything under OEBPS/ except images
# ---------------------------------------------------------------------------

def generate(meta: dict, chapters: list[dict], cover_href: str,
             bibliography: dict | None, lang: str,
             images: list[str] | None = None) -> dict[str, str]:
    """Return {filename under OEBPS/: content} for all XHTML/OPF/NCX."""
    pages: dict[str, str] = {}
    uid = unique_identifier(meta)

    pages["cover.xhtml"] = cover_page(meta, cover_href, lang)
    pages["titlepage.xhtml"] = titlepage(meta, lang)
    pages["copyright.xhtml"] = copyright_page(meta, lang)

    for ch in chapters:
        body = ('<section epub:type="chapter" role="doc-chapter">\n'
                + ch["body"] + "\n</section>")
        pages[ch["file"]] = xhtml_page(ch["title"], body, lang)

    if bibliography:
        pages["bibliography.xhtml"] = xhtml_page(
            bibliography["title"], bibliography["body"], lang)

    # Reading-order TOC: front matter, chapters (with section children),
    # bibliography. Labels derive from converted content, not book.yaml.
    entries: list[dict] = [
        {"href": "cover.xhtml", "label": "Cover"},
        {"href": "titlepage.xhtml", "label": "Title Page"},
        {"href": "copyright.xhtml", "label": "Copyright"},
    ]
    for ch in chapters:
        entries.append({
            "href": ch["file"],
            "label": f"{ch['number']}. {ch['title']}",
            "children": [{"href": f"{ch['file']}#{sid}", "label": label}
                         for sid, label in ch["sections"]],
        })
    if bibliography:
        entries.append({"href": "bibliography.xhtml",
                        "label": bibliography["title"]})

    first_chapter = chapters[0]["file"] if chapters else "titlepage.xhtml"
    pages["nav.xhtml"] = nav_doc(meta, entries, first_chapter, lang)
    pages["toc.ncx"] = ncx_doc(meta, uid, entries)

    spine = (["cover.xhtml", "titlepage.xhtml", "copyright.xhtml"]
             + [ch["file"] for ch in chapters]
             + (["bibliography.xhtml"] if bibliography else []))
    extra = ["epub.css"] + sorted(images or [])
    pages["content.opf"] = content_opf(meta, uid, spine, extra,
                                       cover_href, lang)
    return pages
