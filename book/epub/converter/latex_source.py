"""Source-preserving LaTeX preparation and prose extraction.

TexSoup is the parser for the project's constrained authoring dialect.  A
small pre-pass is still required for verbatim bodies: their contents are not
LaTeX and can contain unmatched braces, dollars, comments, and backslashes.
All replacements in this module preserve length and newlines so diagnostics
continue to point at the original source line.

The EPUB converter imports the canonical verbatim vocabulary from here.  Text
analysis tools additionally use :func:`extract_prose`, which walks TexSoup's
source-positioned tree and retains only arguments that readers encounter as
prose.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from TexSoup import TexSoup


VERBATIM_ENVS = ("codelisting", "promptcode", "outputcode")

# Historical books can extend the contract. These constructors have verbatim
# semantics in LaTeX packages rather than merely visual box semantics.
_VERBATIM_DECL = re.compile(
    r"\\(?:newtcblisting|NewTCBListing|lstnewenvironment|"
    r"DefineVerbatimEnvironment)\*?\s*\{([A-Za-z@][A-Za-z0-9@*-]*)\}"
)

BRACED_CONTENT_PATTERN = r"(?:[^{}\\]|\\.|\{(?:[^{}\\]|\\.)*\})*"
_COMMENT = re.compile(r"(?<!\\)%[^\n]*")
_VERB = re.compile(r"\\verb\*?(.)(?:(?!\1).)*\1")
_INLINE_CODE = re.compile(r"\\code\{(" + BRACED_CONTENT_PATTERN + r")\}")
_MATH = re.compile(
    r"\$\$.*?\$\$|\\\[.*?\\\]|\\\(.*?\\\)|(?<!\\)\$[^$\n]*\$",
    re.DOTALL,
)
_URL = re.compile(r"https?://[^\s{}]+|www\.[^\s{}]+")
_ENV_EDGE = re.compile(
    r"\\(begin|end)\s*\{([A-Za-z@][A-Za-z0-9@*-]*)\}"
)
_OPTION_START = re.compile(
    r"(?:\\begin\s*\{[A-Za-z@][A-Za-z0-9@*-]*\}|"
    r"\\[A-Za-z@]+\*?)\s*(\[)"
)

# SBE policy: these bodies are not the author's running explanatory prose.
# `figure` and `table` remain traversable because their captions are prose;
# `tabular` is excluded separately.
NON_PROSE_ENVS = frozenset((
    *VERBATIM_ENVS,
    "verbatim", "Verbatim", "lstlisting", "minted",
    "tabular", "tabularx", "longtable",
    "equation", "align", "alignat", "gather", "multline",
    "displaymath", "math", "tikzpicture", "picture",
    "quotation", "quote", "verse", "parallelverse", "archive",
    "transcriptsrc",
))

# Commands whose arguments are metadata, identifiers, code, or layout rather
# than reader-visible prose. Commands not in this set are transparent semantic
# wrappers; TexSoup, not a regex, still determines their argument boundaries.
NON_PROSE_COMMANDS = frozenset((
    "autocite", "textcite", "parencite", "footcite", "citeauthor",
    "citeyear", "cite", "scite", "nocite", "label", "ref", "autoref",
    "pageref", "eqref", "Cref", "cref", "nameref", "chapref",
    "spineresumes", "url", "href", "includegraphics", "input",
    "include", "bibliography", "addbibresource", "code", "figalt", "index",
    "hypertarget", "hyperlink", "color", "textcolor", "definecolor", "rule",
    "setlength", "vspace", "hspace", "usepackage", "documentclass",
    "newcommand", "renewcommand", "glsadd", "addcontentsline", "markboth",
    "pagestyle", "epigraph", "chapterquote", "texttt", "num", "V", "Q",
    "K", "rowcolors", "cellcolor", "arrayrulecolor", "def", "arabic",
    "roman", "Roman", "alph", "Alph",
))

_ACCENT_COMMANDS = frozenset((
    "`", "'", '"', "^", "~", "=", ".", "u", "v", "H", "t", "c",
    "d", "b", "r",
))
_CHAR_COMMANDS = frozenset(("&", "%", "#", "$", "_"))


def blank(value: str) -> str:
    """Return same-length whitespace while retaining every newline."""
    return "".join("\n" if char == "\n" else " " for char in value)


def _blank_sub(pattern: re.Pattern, text: str) -> str:
    return pattern.sub(lambda match: blank(match.group(0)), text)


@lru_cache(maxsize=32)
def discover_verbatim_environments(root: Path) -> frozenset[str]:
    """Read verbatim environment declarations from a book's preambles.

    Current books need only :data:`VERBATIM_ENVS`. Older calibration projects
    define names such as ``terminalbox`` and ``vt100box`` with tcolorbox's
    listing constructor; discovering the declaration is safer than maintaining
    a cross-project name list in every prose tool.
    """
    names = set(VERBATIM_ENVS)
    candidates = (
        root / "latex" / "preamble",
        root / "preamble",
        root / "front-matter",
    )
    for directory in candidates:
        if not directory.is_dir():
            continue
        for path in directory.rglob("*.tex"):
            try:
                source = path.read_text(encoding="utf-8")
            except OSError:
                continue
            names.update(_VERBATIM_DECL.findall(source))
    return frozenset(names)


def _blank_environments(text: str, names: Iterable[str]) -> str:
    """Blank balanced named environments before TexSoup sees their bodies."""
    names = frozenset(name.rstrip("*") for name in names)
    stack: list[tuple[str, int]] = []
    spans: list[tuple[int, int]] = []
    for match in _ENV_EDGE.finditer(text):
        name = match.group(2).rstrip("*")
        if match.group(1) == "begin":
            stack.append((name, match.start()))
            continue
        for index in range(len(stack) - 1, -1, -1):
            if stack[index][0] != name:
                continue
            start = stack[index][1]
            nested = any(item[0] in names for item in stack[:index])
            del stack[index:]
            if name in names and not nested:
                spans.append((start, match.end()))
            break
    chars = list(text)
    for start, end in spans:
        chars[start:end] = blank(text[start:end])
    return "".join(chars)


def _blank_optional_arguments(text: str) -> str:
    """Blank balanced ``[...]`` options after commands/environments.

    TexSoup exposes environment options as body children. A small balanced
    scanner is required here because real titles contain nested brace groups
    such as ``title={\\textbf{...}}``; a regex with a fixed brace depth either
    leaks metadata or consumes body prose.
    """
    chars = list(text)
    for match in _OPTION_START.finditer(text):
        start = match.start(1)
        bracket_depth = 1
        brace_depth = 0
        index = start + 1
        while index < len(text):
            char = text[index]
            if char == "\\":
                index += 2
                continue
            if char == "{":
                brace_depth += 1
            elif char == "}" and brace_depth:
                brace_depth -= 1
            elif not brace_depth and char == "[":
                bracket_depth += 1
            elif not brace_depth and char == "]":
                bracket_depth -= 1
                if bracket_depth == 0:
                    chars[start:index + 1] = blank(text[start:index + 1])
                    break
            index += 1
    return "".join(chars)


def prepare_for_parse(raw: str, *, verbatim_envs: Iterable[str]) -> str:
    """Return same-length, TexSoup-safe source for analysis tools."""
    text = _blank_environments(raw, verbatim_envs)
    text = _blank_sub(_INLINE_CODE, text)
    text = _blank_sub(_VERB, text)
    text = _blank_sub(_COMMENT, text)
    text = _blank_sub(_MATH, text)
    text = _blank_sub(_URL, text)
    # TexSoup treats environment options as body children. Blank only the
    # brackets and their contents so titles/language names do not become prose.
    text = _blank_optional_arguments(text)
    return text


def _copy(chars: list[str], source: str, start: int, value: str) -> None:
    chars[start:start + len(value)] = source[start:start + len(value)]


def _write_compact(chars: list[str], start: int, end: int, value: str) -> None:
    """Write a rendered inline token without changing source length."""
    room = end - start
    rendered = value[:room]
    chars[start:start + len(rendered)] = rendered


def extract_prose(
    raw: str,
    *,
    root: Path,
    non_prose_envs: Iterable[str] = NON_PROSE_ENVS,
) -> str:
    """Extract reader-visible prose with source line positions preserved.

    Raises TexSoup's parse exception rather than silently falling back to a
    second parser. A malformed or undiscovered verbatim environment is a
    contract problem and must be made visible to callers and tests.
    """
    verbatim = discover_verbatim_environments(root)
    excluded = frozenset(non_prose_envs) | verbatim
    # Opaque math, quotation, table-data, and verbatim bodies are unnecessary
    # to the prose tree and can contain syntax TexSoup must not interpret.
    safe = prepare_for_parse(raw, verbatim_envs=excluded)
    output = list(blank(safe))

    def visit(node) -> None:
        position = getattr(node, "position", None)
        value = str(node)
        name = str(getattr(node, "name", ""))
        expression = type(getattr(node, "expr", None)).__name__

        if expression in ("TexText", "Token") or type(node).__name__ == "TexText":
            if position is not None:
                _copy(output, safe, position, value)
            return
        if name == "BraceGroup":
            for child in getattr(node, "contents", ()) or ():
                visit(child)
            return
        if expression in ("TexNamedEnv", "TexEnv"):
            if name.rstrip("*") in excluded:
                return
            for child in getattr(node, "contents", ()) or ():
                visit(child)
            return
        if name in _ACCENT_COMMANDS:
            match = re.search(r"[A-Za-z]", value[1:])
            if position is not None and match:
                _write_compact(output, position, position + len(value), match.group(0))
            return
        if name == "lettrine":
            letters = "".join(
                str(child) for child in getattr(node, "contents", ()) or ()
                if str(getattr(child, "name", "")) == "text"
            )
            if position is not None:
                _write_compact(output, position, position + len(value), letters)
            return
        if name in ("TeX", "LaTeX"):
            if position is not None:
                _write_compact(output, position, position + len(value), name)
            return
        if name in _CHAR_COMMANDS:
            if position is not None:
                _write_compact(output, position, position + len(value), name)
            return
        if name not in NON_PROSE_COMMANDS:
            # Unknown commands with arguments are normally presentation
            # wrappers in older books (drop caps, custom semantic spans,
            # callout labels). TexSoup still owns their boundaries. Known
            # opaque arguments are excluded above, and bare commands have no
            # children to leak.
            for child in getattr(node, "contents", ()) or ():
                visit(child)

    soup = TexSoup(safe)
    for node in soup.contents:
        visit(node)
    return "".join(output)
