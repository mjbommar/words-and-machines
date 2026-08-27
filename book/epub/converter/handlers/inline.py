"""Inline semantics — the macro <-> class table in authoring-contract.md,
mirroring the print definitions in latex/preamble/commands.tex.

Also: TeX logo macros, LaTeX character escapes, and the metadata macros
(\\BookTitle, ...) that generate_metadata.py defines — those resolve to
values from build/epub-metadata.json, never to strings in this package
(ADR 0002).
"""

from . import inline_handler

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
}


def _make_semantic(tag: str, cls: str):
    def handler(node, ctx):
        inner = ctx.convert_inline(ctx.arg_nodes(node))
        attr = f' class="{cls}"' if cls else ""
        return f"<{tag}{attr}>{inner}</{tag}>"
    return handler


for _name, (_tag, _cls) in _SEMANTIC.items():
    inline_handler(_name)(_make_semantic(_tag, _cls))


# Math/logic callout icon macros (preamble/boxes.tex). Print-only: they
# draw a fontawesome glyph in the box title. In EPUB the icon is a
# class-based CSS ::before badge, so these strip to nothing here.
@inline_handler("iconProofKit", "iconTryIt", "iconGoingDeeper", "iconArchive")
def callout_icon(node, ctx):
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
