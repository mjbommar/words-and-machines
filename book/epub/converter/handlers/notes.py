"""Footnotes -> chapter endnotes with backlinks (ADR 0007; pipeline spec:
epub:type noteref/footnote pattern from the htsd book's night-mode-safe
endnote treatment).

Each \\footnote becomes a superscript noteref; the notes collect into a
per-chapter endnotes <section> that core appends after the body. Every
note carries a backlink to its reference mark.
"""

from . import inline_handler


@inline_handler("footnote")
def footnote(node, ctx):
    text = ctx.convert_inline(ctx.arg_nodes(node)).strip()
    n = len(ctx.footnotes) + 1
    note_id = f"fn-{ctx.chapter_index}-{n}"
    ref_id = f"fnref-{ctx.chapter_index}-{n}"
    ctx.footnotes.append((note_id, ref_id, text))
    return (
        f'<a class="noteref" id="{ref_id}" href="#{note_id}" '
        f'epub:type="noteref" role="doc-noteref"><sup>{n}</sup></a>'
    )


def render_endnotes(ctx) -> str:
    """Called by core after each chapter body; empty string when the
    chapter has no footnotes."""
    if not ctx.footnotes:
        return ""
    items = []
    for i, (note_id, ref_id, text) in enumerate(ctx.footnotes, 1):
        # Plain <li>: the doc-endnote role was deprecated in DPUB-ARIA
        # 1.1 (Ace flags it), and epub:type="footnote" on an <li> has no
        # non-deprecated role twin — the doc-endnotes container above
        # carries the semantics.
        items.append(
            f'<li id="{note_id}">'
            f'<p>{text} <a href="#{ref_id}" class="backlink" '
            f'epub:type="backlink" role="doc-backlink" '
            f'aria-label="Return to note {i} reference">&#8617;&#xFE0E;</a>'
            "</p></li>"
        )
    return (
        '<section class="endnotes" epub:type="footnotes" role="doc-endnotes">\n'
        '<h2 class="endnotes-title">Notes</h2>\n<ol>\n'
        + "\n".join(items) + "\n</ol>\n</section>"
    )
