"""Media: figure environments (\\includegraphics + \\caption + \\label)
and booktabs tables (authoring-contract.md "Block environments").

Figures: PDF sources are rasterized to PNG via pdftoppm at build time
(cached in build/epub-work/ — see core.convert_figure_image).

Tables: the contract's subset — tabular with l/c/r columns, booktabs
rules only (\\toprule/\\midrule/\\bottomrule), & and \\\\. Rows before the
first \\midrule become <thead>.
"""

import re

from ..core import convert_figure_image, node_name
from . import block_handler


@block_handler("figure")
def figure(node, ctx):
    num = ctx.next_figure()
    graphic = width = caption_nodes = label = figalt = None
    _, body = ctx.env_parts(node)  # tolerate (and drop) [htbp]-style opts
    for child in body:
        name = node_name(child)
        if name == "includegraphics":
            for arg in getattr(child, "args", []):
                raw = str(arg)
                if raw.startswith("["):  # e.g. [width=0.82\textwidth]
                    m = re.search(r"width\s*=\s*([0-9.]+)\s*\\textwidth", raw)
                    width = float(m.group(1)) if m else None
                else:
                    graphic = raw[1:-1]
        elif name == "caption":
            caption_nodes = ctx.arg_nodes(child)
        elif name == "label":
            label = ctx.arg_raw(child)
        elif name == "figalt":
            figalt = ctx.plain(ctx.convert_inline(ctx.arg_nodes(child))).strip()
        elif name is None or name == "centering":
            continue
        else:
            ctx.unknown(name)

    if graphic is None:
        ctx.warn("figure without \\includegraphics")
        return ""
    href = convert_figure_image(ctx, graphic)
    if href is None:
        return ""

    caption_html = ctx.convert_inline(caption_nodes or []).strip()
    fig_id = label.replace(":", "-") if label else f"figure-{num.replace('.', '-')}"
    style = f' style="width:{width:.0%}"' if width else ""
    caption = (f'<figcaption><span class="caption-label">Figure {num}.</span> '
               f"{caption_html}</figcaption>") if caption_html else ""

    # Alt text (authoring contract): \figalt wins; \figalt{} marks the
    # image decorative; otherwise fall back to the caption. A figure
    # with neither violates the OPF's accessibility conformance claim.
    if figalt == "":
        img = f'<img src="{href}" alt="" role="presentation"{style}/>'
    else:
        alt = " ".join((figalt or ctx.plain(caption_html)).split())
        if not alt:
            ctx.a11y_error(f"figure {num} ({graphic}) has no \\figalt "
                           "and no \\caption to derive alt text from")
            alt = f"Figure {num}"
        elif len(alt) > 140:
            ctx.warn(f"figure {num} alt text is {len(alt)} chars "
                     "(KDP recommends 140 or fewer)")
        img = f'<img src="{href}" alt="{ctx.attr(alt)}"{style}/>'
    return (
        f'<figure class="figure" id="{fig_id}">\n'
        f"{img}\n{caption}\n</figure>"
    )


@block_handler("table")
def table(node, ctx):
    num = ctx.next_table()
    caption_nodes = label = tabular = None
    _, body = ctx.env_parts(node)
    for child in body:
        name = node_name(child)
        if name == "caption":
            caption_nodes = ctx.arg_nodes(child)
        elif name == "label":
            label = ctx.arg_raw(child)
        elif name == "tabular":
            tabular = child
        elif name is None or name == "centering":
            continue
        else:
            ctx.unknown(name)
    if tabular is None:
        ctx.warn("table without tabular")
        return ""

    table_html = _convert_tabular(tabular, ctx)
    caption_html = ctx.convert_inline(caption_nodes or []).strip()
    tab_id = label.replace(":", "-") if label else f"table-{num.replace('.', '-')}"
    caption = (f'<figcaption><span class="caption-label">Table {num}.</span> '
               f"{caption_html}</figcaption>") if caption_html else ""
    return (
        f'<figure class="table-figure" id="{tab_id}">\n{caption}\n'
        f'<div class="table-wrap">\n{table_html}\n</div>\n</figure>'
    )


def _convert_tabular(node, ctx) -> str:
    colspec = ctx.arg_raw(node)
    aligns = [c for c in colspec.replace("@{}", "") if c in "lcr"]

    # Reconstruct the raw body; TexSoup duplicates the colspec as the
    # first content token — drop it.
    parts = [str(c) for c in node.contents]
    if parts and parts[0].strip("{}") == colspec.strip("{}"):
        parts = parts[1:]
    body = "".join(parts).replace(r"\&", "\x00")  # protect escaped &
    body = body.replace(r"\tabularnewline", r"\\")

    rows_html: list[str] = []
    header_done = False
    thead: list[str] = []
    for segment in re.split(r"\\\\(?:\[[^\]]*\])?", body):
        if r"\midrule" in segment:
            header_done = True
        segment = re.sub(r"\\(toprule|midrule|bottomrule)", "", segment)
        if not segment.strip():
            continue
        cells = [ctx.inline_tex(c.strip().replace("\x00", r"\&"))
                 for c in segment.split("&")]
        tag = "td" if header_done or thead else "th"
        row = []
        for i, cell in enumerate(cells):
            align = aligns[i] if i < len(aligns) else "l"
            scope = ' scope="col"' if tag == "th" else ""
            accessible_name = ""
            screen_reader_text = ""
            if tag == "th" and "<math " in cell:
                label = ctx.plain(cell)
                accessible_name = f' aria-label="{ctx.attr(label)}"'
                screen_reader_text = (
                    f'<span class="screen-reader-only">{ctx.text(label)}</span>')
            row.append(f'<{tag} class="col-{align}"{scope}{accessible_name}>'
                       f'{screen_reader_text}{cell}</{tag}>')
        target = thead if tag == "th" else rows_html
        target.append("<tr>" + "".join(row) + "</tr>")

    head = f"<thead>\n{chr(10).join(thead)}\n</thead>\n" if thead else ""
    return (f"<table>\n{head}<tbody>\n" + "\n".join(rows_html)
            + "\n</tbody>\n</table>")


@block_handler("tabular")
def standalone_tabular(node, ctx):
    """Convert a tabular used directly inside a legacy center environment."""
    return '<div class="table-wrap">\n' + _convert_tabular(node, ctx) + "\n</div>"
