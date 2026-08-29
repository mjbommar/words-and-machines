"""Citations: \\autocite/\\textcite (authoryear) and \\scite (superscript),
resolved against latex/bib/references.bib, plus the generated
bibliography page (docs/decisions/0007-epub-converter.md).

authoryear renders biblatex-style inline labels — \\textcite ->
"Author (Year)", \\autocite -> "(Author Year)" — linked to the entry on
the bibliography page. The superscript preset (and \\scite regardless of
preset) falls back to endnote-style numbered noterefs, numbered in
first-citation order.

The .bib parser is deliberately tiny: brace-balanced field scanning
covers the house bibliography rules (guides/CITATIONS.md); it is not a
general BibTeX implementation.
"""

import html
import re
from pathlib import Path

from . import inline_handler

# ---------------------------------------------------------------------------
# BibTeX parsing
# ---------------------------------------------------------------------------


def load_bib(path: Path) -> dict[str, dict]:
    """Parse .bib into {key: {field: value, '_type': entrytype}}."""
    if not path.exists():
        return {}
    src = path.read_text()
    entries: dict[str, dict] = {}
    for m in re.finditer(r"@(\w+)\s*\{", src):
        etype = m.group(1).lower()
        if etype in ("comment", "preamble", "string"):
            continue
        body, _end = _balanced(src, m.end() - 1)
        key, _, rest = body.partition(",")
        fields = {"_type": etype}
        pos = 0
        for fm in re.finditer(r"(\w+)\s*=\s*", rest):
            if fm.start() < pos:  # inside a previous value
                continue
            value, pos = _field_value(rest, fm.end())
            fields[fm.group(1).lower()] = " ".join(value.split())
        entries[key.strip()] = fields
    return entries


def _balanced(src: str, open_brace: int) -> tuple[str, int]:
    """Content of the brace group starting at src[open_brace] == '{'."""
    depth = 0
    for i in range(open_brace, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[open_brace + 1:i], i
    return src[open_brace + 1:], len(src)


def _field_value(src: str, start: int) -> tuple[str, int]:
    """Field value at src[start:]: {braced}, "quoted", or bare token."""
    if start < len(src) and src[start] == "{":
        value, end = _balanced(src, start)
        return value, end + 1
    if start < len(src) and src[start] == '"':
        end = src.index('"', start + 1)
        return src[start + 1:end], end + 1
    m = re.match(r"[^,}]*", src[start:])
    return m.group(0).strip(), start + m.end()


# ---------------------------------------------------------------------------
# Entry -> label / formatted reference
# ---------------------------------------------------------------------------


def _detex(s: str) -> str:
    """LaTeX field text -> plain text (logos, escapes, braces)."""
    s = re.sub(r"\\(TeX|LaTeX)(\{\})?", r"\1", s)
    s = s.replace(r"\&", "&").replace(r"\%", "%").replace(r"\_", "_")
    s = re.sub(r"\\\w+\s*", "", s)          # any other command: drop
    s = s.replace("{", "").replace("}", "")
    s = s.replace("---", "—").replace("--", "–")
    return " ".join(s.split())


def _split_names(author_field: str) -> list[str]:
    """Split on ' and ' outside braces (corporate authors stay whole)."""
    names, depth, token = [], 0, []
    i = 0
    while i < len(author_field):
        ch = author_field[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        if depth == 0 and author_field[i:i + 5] == " and ":
            names.append("".join(token))
            token, i = [], i + 5
            continue
        token.append(ch)
        i += 1
    names.append("".join(token))
    return [n.strip() for n in names if n.strip()]


def _family(name: str) -> str:
    if name.startswith("{"):                 # corporate: {W3C}
        return _detex(name)
    if "," in name:                          # Last, First
        return _detex(name.split(",", 1)[0])
    return _detex(name.split()[-1])          # First Last


def author_label(entry: dict) -> str:
    field = entry.get("author") or entry.get("editor") or \
        entry.get("organization") or "Anonymous"
    families = [_family(n) for n in _split_names(field)]
    if len(families) == 1:
        return families[0]
    if len(families) == 2:
        return f"{families[0]} and {families[1]}"
    return f"{families[0]} et al."


def entry_year(entry: dict) -> str:
    for f in ("date", "year", "urldate"):
        m = re.match(r"(\d{4})", entry.get(f, ""))
        if m:
            return m.group(1)
    return "n.d."


def _ordinal(edition: str) -> str:
    if edition.isdigit():
        n = int(edition)
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(
            n % 10 if n % 100 not in (11, 12, 13) else 0, "th")
        return f"{n}{suffix} ed."
    return f"{edition} ed."


def format_entry(entry: dict) -> str:
    """One bibliography line — simple authoryear reference style."""
    esc = lambda s: html.escape(_detex(s), quote=False)  # noqa: E731
    authors = esc(entry.get("author") or entry.get("editor")
                  or entry.get("organization") or "Anonymous")
    year = entry_year(entry)
    title = esc(entry.get("title", "Untitled"))
    if entry.get("subtitle"):
        title += f": {esc(entry['subtitle'])}"
    parts = [f"{authors} ({year})."]

    if entry["_type"] == "article":
        parts.append(f"“{title}.”")
        if entry.get("journaltitle"):
            ref = f"<i>{esc(entry['journaltitle'])}</i>"
            if entry.get("volume"):
                ref += f" {esc(entry['volume'])}"
                if entry.get("number"):
                    ref += f"({esc(entry['number'])})"
            if entry.get("pages"):
                ref += f": {esc(entry['pages'])}"
            parts.append(ref + ".")
    else:
        parts.append(f"<i>{title}</i>.")
        if entry.get("edition"):
            parts.append(_ordinal(entry["edition"]))
        if entry.get("publisher"):
            parts.append(f"{esc(entry['publisher'])}.")
        elif entry.get("organization"):
            parts.append(f"{esc(entry['organization'])}.")

    if entry.get("doi"):
        url = f"https://doi.org/{entry['doi']}"
        parts.append(f'<a href="{url}">{html.escape(url)}</a>.')
    elif entry.get("url"):
        url = entry["url"]
        parts.append(f'<a href="{html.escape(url, quote=True)}">'
                     f"{html.escape(url)}</a>.")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


@inline_handler("autocite", "textcite", "scite")
def cite(node, ctx):
    # BibLaTeX accepts comma-separated keys in one command.  Treating the
    # whole argument as one key dropped valid references from the EPUB.
    keys = [key.strip() for key in ctx.arg_raw(node, -1).split(",")
            if key.strip()]
    name = str(node.name)
    superscript = (name == "scite"
                   or ctx.meta.get("citation_style") == "superscript")
    rendered = []
    for key in keys:
        entry = ctx.bib.get(key)
        if entry is None:
            ctx.warn(f"citation key not in references.bib: {key}")
            rendered.append("?")
            continue
        index = ctx.cited.setdefault(key, len(ctx.cited) + 1)
        href = f"bibliography.xhtml#bib-{key}"
        if superscript:  # endnote-style noteref fallback (pipeline spec)
            rendered.append(
                f'<a class="citation-sup" href="{href}" '
                f'epub:type="noteref" role="doc-noteref">'
                f'<sup>{index}</sup></a>')
            continue
        label = ctx.text(author_label(entry))
        year = entry_year(entry)
        if name == "textcite":
            rendered.append(
                f'{label} (<a class="citation" href="{href}">{year}</a>)')
        else:
            rendered.append(
                f'<a class="citation" href="{href}">{label} {year}</a>')

    if superscript:
        return ",".join(rendered)
    if name == "textcite":
        return "; ".join(rendered)
    return "(" + "; ".join(rendered) + ")"


# ---------------------------------------------------------------------------
# Bibliography page body (core wraps it in the XHTML skeleton)
# ---------------------------------------------------------------------------


def bibliography_page(ctx) -> dict:
    """Return {"title", "body"} for the generated bibliography page,
    listing only cited entries. authoryear sorts alphabetically;
    superscript keeps first-citation (noteref) order."""
    title = ctx.meta.get("bibliography_title", "Bibliography")
    superscript = ctx.meta.get("citation_style") == "superscript"
    keys = list(ctx.cited)
    if not superscript:
        keys.sort(key=lambda k: (author_label(ctx.bib[k]).lower(),
                                 entry_year(ctx.bib[k])))
    tag = "ol" if superscript else "ul"
    items = "\n".join(
        f'<li id="bib-{k}">{format_entry(ctx.bib[k])}</li>' for k in keys)
    body = (
        '<section epub:type="bibliography" role="doc-bibliography">\n'
        f"<h1>{ctx.text(title)}</h1>\n"
        f'<{tag} class="bibliography">\n{items}\n</{tag}>\n</section>'
    )
    return {"title": title, "body": body}
