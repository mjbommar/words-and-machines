"""Inline semantics — the macro <-> class table in authoring-contract.md,
mirroring the print definitions in latex/preamble/commands.tex.

Also: TeX logo macros, LaTeX character escapes, and the metadata macros
(\\BookTitle, ...) that generate_metadata.py defines — those resolve to
values from build/epub-metadata.json, never to strings in this package
(ADR 0002).
"""

from xml.etree import ElementTree

from latex2mathml import converter as mathml_converter

from . import block_handler, inline_handler

# macro -> (tag, class) — the contract's table, verbatim.
_SEMANTIC = {
    "emph": ("em", ""),
    "term": ("i", "term"),
    "work": ("i", "work"),
    "person": ("span", "person"),
    # `keyterm` marks the defining occurrence, not merely bold text. The
    # surrounding sentence supplies the definition; <dfn> exposes that
    # relationship to assistive technology and reading tools.
    "keyterm": ("dfn", "keyterm"),
    "foreignphrase": ("i", "foreign"),
    "textbf": ("b", ""),        # allowed by the contract ("\textbf allowed")
    "textit": ("i", ""),
    "texttt": ("code", ""),
}


def _make_semantic(tag: str, cls: str):
    def handler(node, ctx):
        inner = ctx.convert_inline(ctx.arg_nodes(node))
        attr = f' class="{cls}"' if cls else ""
        return f"<{tag}{attr}>{inner}</{tag}>"
    return handler


for _name, (_tag, _cls) in _SEMANTIC.items():
    inline_handler(_name)(_make_semantic(_tag, _cls))


def _math_source(node) -> str:
    """Recover the TeX inside a TexSoup math node without its delimiters."""
    return "".join(str(child) for child in getattr(node, "contents", ()) or ())


_MATHML = "http://www.w3.org/1998/Math/MathML"
_TOKEN_TAGS = {f"{{{_MATHML}}}{name}" for name in ("mi", "mn", "mo", "mtext", "ms")}


def _normalize_mathml(rendered: str) -> str:
    """Repair token wrappers emitted for commands such as ``\\mathbin``.

    MathML token elements cannot contain an ``mrow``. latex2mathml currently
    emits such wrappers for ``\\mathbin`` and a few styled identifiers. Keep
    the outer token and its spacing attributes while flattening its illegal
    child subtree to the same visible text.
    """
    ElementTree.register_namespace("", _MATHML)
    root = ElementTree.fromstring(rendered)
    for token in root.iter():
        if token.tag not in _TOKEN_TAGS or not list(token):
            continue
        # Token elements admit text, not arbitrary MathML children. Commands
        # such as ``\mathbin{\mathsf{xor}}`` produce a styled mrow inside an
        # outer ``mo``. Preserve the visible operator and the outer spacing
        # attributes by flattening only the illegal token subtree to text.
        value = "".join(token.itertext())
        for child in list(token):
            token.remove(child)
        token.text = value
    return ElementTree.tostring(root, encoding="unicode")


@inline_handler("math")
def inline_math(node, ctx):
    """LaTeX inline math becomes native EPUB MathML."""
    source = _math_source(node)
    try:
        return _normalize_mathml(mathml_converter.convert(source, display="inline"))
    except Exception as exc:
        ctx.content_error(f"cannot convert inline math {source[:80]!r}: {exc}")
        return f'<code class="math-fallback">{ctx.text(source)}</code>'


@block_handler("displaymath")
def display_math(node, ctx):
    """LaTeX display math becomes native block MathML."""
    source = _math_source(node)
    try:
        return _normalize_mathml(mathml_converter.convert(source, display="block"))
    except Exception as exc:
        ctx.content_error(f"cannot convert display math {source[:80]!r}: {exc}")
        return f'<pre class="math-fallback">{ctx.text(source)}</pre>'


# Math/logic callout icon macros (preamble/boxes.tex). Print-only: they
# draw a fontawesome glyph in the box title. In EPUB the icon is a
# class-based CSS ::before badge, so these strip to nothing here.
@inline_handler("iconProofKit", "iconTryIt", "iconGoingDeeper", "iconArchive")
def callout_icon(node, ctx):
    return ""


@inline_handler("index", "indexentry")
def index_marker(node, ctx):
    """Print page locators have no stable meaning in a reflowable EPUB."""
    return ""


@inline_handler("TeX")
def tex_logo(node, ctx):
    return "TeX"


@inline_handler("LaTeX")
def latex_logo(node, ctx):
    return "LaTeX"


# LaTeX character escapes (\& \% \# \$ \_) -> the literal character.
@inline_handler("&", "%", "#", "$", "_")
def char_escape(node, ctx):
    ch = str(node.name)
    return "&amp;" if ch == "&" else ch


# Metadata macros: name -> key in build/epub-metadata.json. Only macros
# whose values the json carries are mapped; anything else stays a
# coverage miss (better loud than silently wrong).
_META_MACROS = {
    "BookTitle": "title",
    "BookSubtitle": "subtitle",
    "BookAuthor": "author",
    "BookPublisher": "publisher",
    "BookYear": "year",
    "BookEditionStatement": "edition_statement",
    "BookCopyrightHolder": "copyright_holder",
    "BookEditionName": "edition",
    "BookISBNEpub": "isbn",
    "BookBibTitle": "bibliography_title",
}


def _make_meta(key: str):
    def handler(node, ctx):
        return ctx.text(str(ctx.meta.get(key, "")))
    return handler


for _macro, _key in _META_MACROS.items():
    inline_handler(_macro)(_make_meta(_key))
