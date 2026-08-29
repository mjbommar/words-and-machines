"""Document structure: \\chapter/\\section/\\subsection, \\scenebreak,
\\label/\\ref (authoring-contract.md "Document structure").

Numbering and section ids must mirror core.scan_labels exactly — both
walk the source in the same order, so a \\ref to a figure two chapters
away renders the same number its caption shows.
"""

from . import block_handler, ignore, inline_handler


@block_handler("chapter")
def chapter(node, ctx):
    """\\chapter{Title} -> chapter-opening <h1> (one per file)."""
    title = ctx.convert_inline(ctx.arg_nodes(node))
    ctx.chapter_title = title
    if ctx.document_kind != "chapter":
        return f'<h1 class="chapter-title" id="chapter-0">{title}</h1>'
    return (
        f'<h1 class="chapter-title" id="chapter-{ctx.chapter_index}">'
        f'<span class="chapter-number">Chapter {ctx.chapter_index}</span> '
        f"{title}</h1>"
    )


@block_handler("section")
def section(node, ctx):
    sid = ctx.next_section(2)
    title = ctx.convert_inline(ctx.arg_nodes(node))
    ctx.sections.append((sid, ctx.plain(title)))  # feeds nav.xhtml
    return f'<h2 id="{sid}">{title}</h2>'


@block_handler("subsection")
def subsection(node, ctx):
    sid = ctx.next_section(3)
    title = ctx.convert_inline(ctx.arg_nodes(node))
    return f'<h3 id="{sid}">{title}</h3>'


@block_handler("scenebreak")
def scenebreak(node, ctx):
    """Typographic break — contract: EPUB renders <hr class="scene"/>."""
    return '<hr class="scene"/>'


@inline_handler("label")
def label(node, ctx):
    """Labels were resolved in the pre-scan; nothing to emit here."""
    return ""


@inline_handler("ref")
def ref(node, ctx):
    """\\ref{key}: link when the target is a converted chapter/section,
    plain text number for figures/tables (matches their caption number)."""
    key = ctx.arg_raw(node)
    target = ctx.labels.get(key)
    if target is None:
        ctx.warn(f"unresolved \\ref{{{key}}}")
        return "?"
    kind, num, fname, frag = target
    if kind in ("chapter", "section"):
        href = f"{fname}#{frag}" if frag else fname
        if fname == ctx.chapter_file:  # same-file ref: fragment only
            href = f"#{frag}" if frag else fname
        return f'<a href="{href}">{num}</a>'
    return num


# Print-layout commands with no EPUB meaning (deliberate ignore-list).
ignore("centering", "print-only alignment inside figure/table floats")
ignore("ENVOPT", "internal marker injected by core.preprocess; consumed "
                 "by environment handlers via ctx.env_parts")
