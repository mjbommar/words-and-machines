"""Handler registry — decorator-registered converters per LaTeX name.

Two registries keyed by command/environment name (the authoring
contract's namespace has no command/environment collisions):

* INLINE  — fn(node, ctx) -> str of inline HTML, appended to the
            paragraph being built.
* BLOCK   — fn(node, ctx) -> str of block HTML; the walker flushes the
            open paragraph first.
* IGNORED — names the converter deliberately drops (print-only layout
            commands); each carries a reason so the coverage report can
            distinguish "handled by silence" from "unknown".

Books can extend the vocabulary by registering additional handlers
before calling build_book() — core never needs to change (ADR 0007).
"""

INLINE: dict = {}
BLOCK: dict = {}
IGNORED: dict = {}


def inline_handler(*names):
    """Register an inline handler for one or more command names."""
    def deco(fn):
        for name in names:
            INLINE[name] = fn
        return fn
    return deco


def block_handler(*names):
    """Register a block handler for one or more command/environment names."""
    def deco(fn):
        for name in names:
            BLOCK[name] = fn
        return fn
    return deco


def ignore(name: str, reason: str) -> None:
    """Declare a name as deliberately unconverted (kept out of coverage)."""
    IGNORED[name] = reason


# Importing the package registers the whole contract vocabulary.
from . import structure, inline, blocks, code, media, notes, citations  # noqa: E402,F401
