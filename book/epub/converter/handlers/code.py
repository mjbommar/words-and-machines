"""Code environments (latex/preamble/code.tex): codelisting, promptcode,
outputcode, and inline \\code.

The bodies never reach TexSoup — core.preprocess stashed them verbatim
and left \\CODEBLOCK{n}/\\CODEINLINE{n} placeholders. Here they come back
as HTML-escaped <pre><code>, so #, &, $, quotes and backslashes survive
exactly (the EPUB-side counterpart of code.tex's catcode fix). No
highlighting markup: CSS-only theming, per the pipeline spec.
"""

import html

from . import block_handler, inline_handler

# environment -> pre class (promptcode/outputcode are the AI-dialogue
# voices from vibe-coding-for-lawyers; codelisting is general-purpose).
_PRE_CLASS = {
    "codelisting": "listing",
    "promptcode": "prompt",
    "outputcode": "output",
}


@block_handler("CODEBLOCK")
def code_block(node, ctx):
    env, opts, body = ctx.extracted.code_blocks[int(ctx.arg_raw(node))]
    options = ctx.parse_options(opts)
    language = options.get("language", "").strip().lower()
    caption = options.get("caption", "").strip()

    lang_cls = f' class="language-{language}"' if language else ""
    pre = (f'<pre class="{_PRE_CLASS[env]}">'
           f"<code{lang_cls}>{html.escape(body)}</code></pre>")
    if not caption:
        return pre
    return (
        '<figure class="listing-figure">\n'
        f"{pre}\n"
        f"<figcaption>{ctx.inline_tex(caption)}</figcaption>\n"
        "</figure>"
    )


@inline_handler("CODEINLINE")
def code_inline(node, ctx):
    raw = ctx.extracted.code_inline[int(ctx.arg_raw(node))]
    return f"<code>{html.escape(raw)}</code>"


@inline_handler("code")
def code_direct(node, ctx):
    """\\code inside re-parsed fragments (captions, callout titles) that
    core.preprocess never saw; argument treated verbatim, as \\lstinline
    does."""
    return f"<code>{html.escape(ctx.arg_raw(node))}</code>"
