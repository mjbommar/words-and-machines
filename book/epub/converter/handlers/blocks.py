"""Block environments: quotation (+\\attribution) and the callout family
(keyidea/example/warning/sidebar/definition — latex/preamble/boxes.tex).

Callouts become <aside class="callout callout-KIND" role="note"> with a
heading; default titles mirror the tcolorbox definitions 1:1, and the
importance= key becomes a class the CSS maps to left-border weight, just
as boxes.tex scales the leftrule (provenance: complexity-book's callout
family, docs/research/complexity-book.md).
"""

from . import block_handler
from ..core import node_name

# environment -> default title, exactly as defined in preamble/boxes.tex.
# The math/logic set (proofkit/tryit/goingdeeper/archive) carries a
# distinct hue AND a leading icon; in EPUB the icon is a class-based CSS
# ::before glyph (epub/css/epub.css), independent of this title text.
CALLOUT_TITLES = {
    "keyidea": "Key Idea",
    "example": "Example",
    "warning": "Warning",
    "sidebar": "Aside",
    "definition": "Definition",
    "proofkit": "Proof Kit",
    "tryit": "Try It",
    "goingdeeper": "Going Deeper",
    "archive": "From the Archive",
}


@block_handler(*CALLOUT_TITLES)
def callout(node, ctx):
    kind = str(node.name)
    opts, body = ctx.env_parts(node)
    options = ctx.parse_options(opts)
    title = options.get("title", CALLOUT_TITLES[kind])
    importance = options.get("importance", "medium")
    if importance not in ("low", "medium", "high"):
        ctx.warn(f"{kind}: unknown importance={importance!r}")
        importance = "medium"
    classes = f"callout callout-{kind}"
    if importance != "medium":
        classes += f" callout-{importance}"
    inner = "\n".join(ctx.convert_blocks(body))
    return (
        f'<aside class="{classes}" role="note">\n'
        f'<h3 class="callout-title">{ctx.inline_tex(title)}</h3>\n'
        f"{inner}\n</aside>"
    )


@block_handler("quotation")
def quotation(node, ctx):
    """quotation env -> <blockquote>; a trailing \\attribution{...} becomes
    a <footer> credit line (em dash supplied here, as in commands.tex)."""
    attribution = None
    body = []
    for child in node.contents:
        if node_name(child) == "attribution":
            attribution = child
        else:
            body.append(child)
    parts = ctx.convert_blocks(body)
    if attribution is not None:
        credit = ctx.convert_inline(ctx.arg_nodes(attribution)).strip()
        parts.append(f'<footer class="attribution">— {credit}</footer>')
    inner = "\n".join(parts)
    return f'<blockquote class="quotation">\n{inner}\n</blockquote>'
