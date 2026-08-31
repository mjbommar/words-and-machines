"""Block environments: quotation (+\\attribution) and the callout family
(keyidea/example/warning/sidebar/definition — latex/preamble/boxes.tex).

Callouts become <aside class="callout callout-KIND" role="note"> with a
heading; default titles mirror the tcolorbox definitions 1:1, and the
importance= key becomes a class the CSS maps to left-border weight, just
as boxes.tex scales the leftrule (provenance: complexity-book's callout
family, docs/research/complexity-book.md).
"""

import json

from ..core import node_name
from . import block_handler, inline_handler

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
    title_html = ctx.inline_tex(title)
    title_text = ctx.plain(title_html)
    return (
        f'<aside class="{classes}" role="note" aria-label="{ctx.attr(title_text)}">\n'
        f'<p class="callout-title">{title_html}</p>\n'
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


def _item_parts(item, ctx):
    """Return an optional item label and the remaining body nodes."""
    args = list(getattr(item, "args", ()) or ())
    label_nodes = ctx.arg_nodes(item) if args and str(args[0]).startswith("[") else []
    body = list(getattr(item, "contents", ()) or ())
    if label_nodes:
        body = body[len(label_nodes):]
    label = ctx.convert_inline(label_nodes).strip() if label_nodes else ""
    return label, body


def _list_items(node, ctx):
    items = []
    for child in getattr(node, "contents", ()) or ():
        name = node_name(child)
        if name == "item":
            items.append(_item_parts(child, ctx))
        elif name is None and not str(child).strip():
            continue
        else:
            ctx.content_error(f"unexpected content outside \\item in {node.name}")
    return items


@block_handler("enumerate", "itemize")
def ordinary_list(node, ctx):
    tag = "ol" if str(node.name) == "enumerate" else "ul"
    rendered = []
    for label, body in _list_items(node, ctx):
        content = "\n".join(ctx.convert_blocks(body))
        marker = f'<span class="item-label">{label}</span> ' if label else ""
        rendered.append(f"<li>{marker}{content}</li>")
    return f"<{tag}>\n" + "\n".join(rendered) + f"\n</{tag}>"


@block_handler("description")
def description_list(node, ctx):
    rendered = []
    for label, body in _list_items(node, ctx):
        if not label:
            ctx.content_error("description item has no label")
            label = "Item"
        content = "\n".join(ctx.convert_blocks(body))
        rendered.append(f"<dt>{label}</dt><dd>{content}</dd>")
    return "<dl>\n" + "\n".join(rendered) + "\n</dl>"


@block_handler("center")
def center(node, ctx):
    """Preserve legacy centered content; alignment is presentational CSS."""
    inner = "\n".join(ctx.convert_blocks(node.contents))
    return f'<div class="center">\n{inner}\n</div>'


def _object_record(ctx, object_id: str) -> dict:
    path = ctx.root.parent / "objects" / f"{object_id}.json"
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        ctx.content_error(f"cannot load object {object_id!r}: {exc}")
        return {"id": object_id, "title": object_id,
                "epistemic_status": "unknown",
                "scope": "Object record unavailable.", "evidence": []}


def _evidence_summary(record: dict) -> str:
    rows = record.get("evidence", [])
    return "; ".join(
        f"{row['kind']} / {row['trust_class']} ({row['check_status']})"
        for row in rows
    ) or "no evidence recorded"


@inline_handler("obj")
def object_id(node, ctx):
    return f"<code>{ctx.text(ctx.arg_raw(node))}</code>"


def _object_field(field: str):
    def handler(node, ctx):
        record = _object_record(ctx, ctx.arg_raw(node))
        value = {
            "ObjStatus": record.get("epistemic_status", "unknown"),
            "ObjScope": record.get("scope") or "--",
            "ObjEvidence": _evidence_summary(record),
            "ObjTitle": record.get("title", record.get("id", "unknown")),
        }[field]
        return ctx.text(value)
    return handler


for _field in ("ObjStatus", "ObjScope", "ObjEvidence", "ObjTitle"):
    inline_handler(_field)(_object_field(_field))


@block_handler("ArtifactScope")
def artifact_scope(node, ctx):
    record = _object_record(ctx, ctx.arg_raw(node))
    values = (
        ("Status", record.get("epistemic_status", "unknown")),
        ("Scope", record.get("scope") or "--"),
        ("Evidence", _evidence_summary(record)),
    )
    return '<dl class="artifact-scope">' + "".join(
        f"<dt>{label}</dt><dd>{ctx.text(value)}</dd>" for label, value in values
    ) + "</dl>"


@block_handler("artifact")
def artifact(node, ctx):
    object_id_value = ctx.arg_raw(node)
    record = _object_record(ctx, object_id_value)
    # TexSoup duplicates a mandatory environment argument into ``contents``.
    arg_nodes = ctx.arg_nodes(node)
    body = list(node.contents)[len(arg_nodes):]
    inner = "\n".join(ctx.convert_blocks(body))
    title = f"Object {object_id_value}: {record.get('title', object_id_value)}"
    return (
        f'<aside class="artifact" role="note" aria-label="{ctx.attr(title)}">\n'
        f'<p class="artifact-title">Object <code>{ctx.text(object_id_value)}</code>: '
        f'{ctx.text(record.get("title", object_id_value))}</p>\n'
        f"{inner}\n</aside>"
    )
