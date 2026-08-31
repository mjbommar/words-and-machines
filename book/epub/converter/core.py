"""core.py — parse the constrained LaTeX dialect, dispatch handlers, package.

Pipeline (docs/architecture/epub-pipeline.md):

    build/epub-metadata.json ─┐
    latex/chapters/*.tex ─────┼─► preprocess ─► TexSoup ─► walker/handlers
    latex/bib/references.bib ─┘        │
                                       └─► XHTML pages ─► generators ─► zip

Verbatim environments (codelisting/promptcode/outputcode) and inline
\\code{...} are regex-extracted into placeholder commands *before*
TexSoup sees the source — listings bodies (#, &, $, unbalanced quotes)
break naive TexSoup parsing (lesson from the vibe-coding/datacenter
converters, docs/research/).  Environment bracket options are also
pre-extracted because TexSoup duplicates them into the environment's
contents.

Provenance: fresh rewrite per ADR 0007; walker/paragraph design from the
datacenter book's converter, packaging fix (mimetype first, stored) from
its package_epub.py, generators approach from the RFC book.
"""

from __future__ import annotations

import html
import json
import os
import re
import shutil
import subprocess
import time
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from TexSoup import TexSoup

from . import generators
from .latex_source import BRACED_CONTENT_PATTERN, VERBATIM_ENVS

MIMETYPE = "application/epub+zip"

# ---------------------------------------------------------------------------
# Pre-extraction (before TexSoup)
# ---------------------------------------------------------------------------

# One-level-balanced brace matcher for \code arguments.
_BRACED = BRACED_CONTENT_PATTERN
# Same, for [options]: top-level ']' must terminate the match (brackets
# are still fine inside {...} values, e.g. caption={see [sic]}).
_OPTS = r"(?:[^\[\]{}\\]|\\.|\{(?:[^{}\\]|\\.)*\})*"


@dataclass
class Extracted:
    """Placeholder stores filled during preprocessing."""
    code_blocks: list = field(default_factory=list)   # (env, opts, body)
    code_inline: list = field(default_factory=list)   # raw strings
    env_opts: list = field(default_factory=list)      # raw option strings


def preprocess(src: str, store: Extracted) -> str:
    """Return TexSoup-safe source with verbatim material stashed in *store*."""
    # 1. Verbatim environments -> \CODEBLOCK{n}. Runs first so nothing
    #    below ever touches listing bodies.
    def _env(m: re.Match) -> str:
        store.code_blocks.append(
            (m.group(1), (m.group(2) or "")[1:-1], m.group(3).strip("\n")))
        return "\\CODEBLOCK{%d}\n" % (len(store.code_blocks) - 1)

    src = re.sub(
        r"\\begin\{(%s)\}[ \t]*(\[.*?\])?\r?\n?(.*?)\\end\{\1\}"
        % "|".join(VERBATIM_ENVS),
        _env, src, flags=re.S)

    # 2. Inline \code{...} -> \CODEINLINE{n}. \code is \lstinline-backed
    #    (preamble/code.tex): its argument is verbatim, so \code{\code}
    #    and \code{dict['k']} must not reach TexSoup.
    def _inline(m: re.Match) -> str:
        store.code_inline.append(m.group(1))
        return "\\CODEINLINE{%d}" % (len(store.code_inline) - 1)

    src = re.sub(r"\\code\{(" + _BRACED + r")\}", _inline, src)

    # 3. Comments (unescaped %). After code extraction so listing
    #    comments survive.
    src = re.sub(r"(?<!\\)%[^\n]*", "", src)

    # 4. \begin{env}[opts] -> \begin{env}\ENVOPT{n}. TexSoup re-parses
    #    bracket options into the environment's contents, which would
    #    duplicate callout titles into the body text.
    def _opt(m: re.Match) -> str:
        store.env_opts.append(m.group(2))
        return "\\begin{%s}\\ENVOPT{%d}" % (m.group(1), len(store.env_opts) - 1)

    src = re.sub(r"\\begin\{(\w+)\}\s*\[(" + _OPTS + r")\]", _opt, src)
    return src


# ---------------------------------------------------------------------------
# Node introspection helpers (TexSoup ducks: TexNode wrappers at the top
# level, raw TexCmd/TexText inside argument groups)
# ---------------------------------------------------------------------------

def node_name(n) -> str | None:
    """Name of a command/environment node; None for text tokens."""
    if isinstance(n, str):
        return None
    cls = type(n).__name__
    if cls in ("TexText", "Token"):
        return None
    name = getattr(n, "name", None)
    if name is None or str(name) == "text":
        return None
    return str(name)


def children(n) -> list:
    return list(getattr(n, "contents", []) or [])


# ---------------------------------------------------------------------------
# Label pre-scan — chapter/section/figure/table numbering for \ref
# ---------------------------------------------------------------------------

_SCAN = re.compile(
    r"\\(chapter|section|subsection|label)\{([^{}]*)\}|\\begin\{(figure|table)\}")


def scan_labels(pre_sources: list[tuple[str, str]]) -> dict:
    """Map \\label keys -> (kind, display number, xhtml file, fragment id).

    Numbering mirrors the render pass exactly (same traversal order), so
    \\ref text always matches figure/table captions and section ids.
    """
    labels: dict[str, tuple] = {}
    for ci, (fname, src) in enumerate(pre_sources, 1):
        sec = sub = fig = tab = 0
        current: tuple | None = ("chapter", str(ci), fname, None)
        for m in _SCAN.finditer(src):
            cmd, arg, env = m.group(1), m.group(2), m.group(3)
            if cmd == "section":
                sec, sub = sec + 1, 0
                current = ("section", f"{ci}.{sec}", fname, f"sec-{ci}-{sec}")
            elif cmd == "subsection":
                sub += 1
                current = ("section", f"{ci}.{sec}.{sub}", fname,
                           f"sec-{ci}-{sec}-{sub}")
            elif cmd == "chapter":
                current = ("chapter", str(ci), fname, None)
            elif env == "figure":
                fig += 1
                current = ("figure", f"{ci}.{fig}", fname, None)
            elif env == "table":
                tab += 1
                current = ("table", f"{ci}.{tab}", fname, None)
            elif cmd == "label" and current:
                labels[arg] = current
    return labels


# ---------------------------------------------------------------------------
# Conversion context
# ---------------------------------------------------------------------------

class Context:
    """Everything handlers may touch. Handlers import nothing from core;
    they receive this object (keeps the registry modules dependency-free)."""

    def __init__(self, meta: dict, root: Path, workdir: Path,
                 labels: dict, bib: dict):
        self.meta = meta
        self.root = root                      # repo root
        self.workdir = workdir                # build/epub-work (PNG cache)
        self.labels = labels
        self.bib = bib                        # key -> field dict
        self.cited: dict[str, int] = {}       # key -> 1-based citation order
        self.images: dict[str, bytes] = {}    # epub href -> bytes
        self.warnings: list[str] = []
        self.a11y_errors: list[str] = []
        self.content_errors: list[str] = []
        self.unknowns: dict[str, int] = {}
        self.handled: set[str] = set()
        # per-chapter state (begin_chapter)
        self.chapter_index = 0
        self.chapter_file = ""
        self.chapter_title = ""
        self.document_kind = "chapter"
        self.sections: list[tuple[str, str]] = []
        self.footnotes: list[tuple[str, str, str]] = []
        self.extracted = Extracted()
        self._sec = self._sub = self._fig = self._tab = 0

    # -- chapter lifecycle -------------------------------------------------
    def begin_chapter(self, index: int, fname: str, extracted: Extracted,
                      kind: str = "chapter"):
        self.chapter_index = index
        self.chapter_file = fname
        self.chapter_title = ""
        self.document_kind = kind
        self.sections = []
        self.footnotes = []
        self.extracted = extracted
        self._sec = self._sub = self._fig = self._tab = 0

    def next_section(self, level: int) -> str:
        if level == 2:
            self._sec, self._sub = self._sec + 1, 0
            return f"sec-{self.chapter_index}-{self._sec}"
        self._sub += 1
        return f"sec-{self.chapter_index}-{self._sec}-{self._sub}"

    def next_figure(self) -> str:
        self._fig += 1
        return f"{self.chapter_index}.{self._fig}"

    def next_table(self) -> str:
        self._tab += 1
        return f"{self.chapter_index}.{self._tab}"

    # -- diagnostics ---------------------------------------------------------
    def warn(self, msg: str) -> None:
        self.warnings.append(f"{self.chapter_file}: {msg}")

    def a11y_error(self, msg: str) -> None:
        """Accessibility contract violation — fails the epub-check gate
        (the OPF claims EPUB Accessibility 1.1, so gaps are errors)."""
        self.a11y_errors.append(f"{self.chapter_file}: {msg}")

    def content_error(self, msg: str) -> None:
        """Record reader-visible conversion loss or malformed source."""
        self.content_errors.append(f"{self.chapter_file}: {msg}")

    def unknown(self, name: str) -> None:
        self.unknowns[name] = self.unknowns.get(name, 0) + 1

    # -- node helpers --------------------------------------------------------
    def arg_raw(self, node, index: int = 0) -> str:
        """Raw source text inside a command's Nth argument group."""
        args = list(getattr(node, "args", []) or [])
        if not args:
            return ""
        s = str(args[index])
        return s[1:-1] if s[:1] in "{[" else s

    def arg_nodes(self, node, index: int = 0) -> list:
        args = list(getattr(node, "args", []) or [])
        if not args:
            return []
        return children(args[index])

    def env_parts(self, node) -> tuple[str, list]:
        """(raw option string, body nodes) for an environment — consumes
        the \\ENVOPT marker injected by preprocess()."""
        opts, body = "", []
        for c in children(node):
            if node_name(c) == "ENVOPT" and not body:
                opts = self.extracted.env_opts[int(self.arg_raw(c))]
            else:
                body.append(c)
        return opts, body

    @staticmethod
    def parse_options(raw: str) -> dict[str, str]:
        """listings/tcolorbox-style keyval: title={...},importance=high."""
        out = {}
        for m in re.finditer(
                r"(\w+)\s*=\s*(\{" + _BRACED + r"\}|[^,\]]+)", raw):
            v = m.group(2).strip()
            if v[:1] == "{" and v[-1:] == "}":
                v = v[1:-1]
            out[m.group(1)] = v.strip()
        return out

    # -- text ---------------------------------------------------------------
    @staticmethod
    def text(s: str) -> str:
        """Plain text -> XHTML with typographic ligatures resolved."""
        s = html.escape(str(s), quote=False)
        s = s.replace("``", "“").replace("''", "”")
        s = s.replace("---", "—").replace("--", "–")
        s = s.replace("`", "‘").replace("'", "’")
        s = s.replace("~", " ")
        return s

    @staticmethod
    def plain(html_text: str) -> str:
        """Strip tags for alt text / nav labels (entities preserved)."""
        return re.sub(r"<[^>]+>", "", html_text).strip()

    @staticmethod
    def attr(value: str) -> str:
        return value.replace('"', "&quot;")

    def inline_tex(self, fragment: str) -> str:
        """Convert a small LaTeX fragment (option value, table cell)."""
        fragment = " ".join(fragment.split())
        if not fragment:
            return ""
        try:
            return self.convert_inline(TexSoup(fragment).contents).strip()
        except Exception:                                   # noqa: BLE001
            self.warn(f"unparseable fragment: {fragment[:60]!r}")
            return self.text(fragment)

    # -- walker ---------------------------------------------------------------
    def convert_inline(self, nodes) -> str:
        """Convert nodes in inline context (headings, captions, footnotes)."""
        from . import handlers  # late import: registry populated at package load
        out = []
        for n in nodes:
            name = node_name(n)
            if name is None:
                out.append(self.text(str(n)))
            elif name == "BraceGroup":                      # transparent {...}
                out.append(self.convert_inline(children(n)))
            elif name in handlers.INLINE:
                self.handled.add(name)
                out.append(handlers.INLINE[name](n, self))
            elif name in handlers.IGNORED:
                pass
            else:
                self.unknown(name)
        return "".join(out)

    def convert_blocks(self, nodes) -> list[str]:
        """Convert nodes in block context — builds <p> paragraphs from text
        runs (blank line = paragraph break) and flushes them around blocks."""
        from . import handlers
        blocks: list[str] = []
        para: list[str] = []

        def flush() -> None:
            content = "".join(para).strip()
            para.clear()
            if content:
                blocks.append(f"<p>{content}</p>")

        for n in nodes:
            name = node_name(n)
            if name is None:
                parts = re.split(r"\n[ \t]*\n+", str(n))
                for i, part in enumerate(parts):
                    if i:
                        flush()
                    para.append(self.text(part))
            elif name == "BraceGroup":
                para.append(self.convert_inline(children(n)))
            elif name in handlers.BLOCK:
                self.handled.add(name)
                flush()
                blocks.append(handlers.BLOCK[name](n, self))
            elif name in handlers.INLINE:
                self.handled.add(name)
                para.append(handlers.INLINE[name](n, self))
            elif name in handlers.IGNORED:
                pass
            else:
                self.unknown(name)
        flush()
        return blocks


# ---------------------------------------------------------------------------
# Build orchestration
# ---------------------------------------------------------------------------

@dataclass
class Report:
    epub_path: Path
    unknowns: dict
    warnings: list
    link_errors: list
    a11y_errors: list
    content_errors: list
    handled: set

    @property
    def ok(self) -> bool:
        return (not self.unknowns and not self.link_errors
                and not self.a11y_errors and not self.content_errors)


class BuildError(RuntimeError):
    pass


def build_book(root: Path, cover: Path, edition: str | None = None) -> Report:
    """Convert the book under *root* into build/epub/book[-EDITION].epub.

    Always writes the EPUB and returns a Report; the caller decides how
    strictly to treat report.unknowns / report.link_errors (the CLI's
    --strict maps report.ok to the exit code — the `epub-check` gate).
    """
    root = Path(root).resolve()
    meta_path = root / "build" / "epub-metadata.json"
    if not meta_path.exists():
        raise BuildError(
            "build/epub-metadata.json missing — run "
            "`uv run scripts/generate_metadata.py` first")
    meta = json.loads(meta_path.read_text())
    if edition and edition != meta.get("edition"):
        raise BuildError(
            f"--edition {edition!r} but metadata was generated for "
            f"{meta.get('edition')!r}; re-run scripts/generate_metadata.py "
            f"--edition {edition}")
    cover = Path(cover)
    if not cover.is_file():
        raise BuildError(f"cover image not found: {cover}")

    workdir = root / "build" / "epub-work"
    workdir.mkdir(parents=True, exist_ok=True)

    # Preprocess authored front matter and every chapter. Order comes from the
    # metadata json, which is generated from the selected edition.
    pre: list[tuple[str, str, Extracted, str]] = []
    for tex_name in meta.get("frontmatter", []):
        tex_path = root / "latex" / "frontmatter" / tex_name
        if not tex_path.exists():
            raise BuildError(f"front-matter file not found: {tex_path}")
        store = Extracted()
        src = preprocess(tex_path.read_text(), store)
        pre.append((Path(tex_name).stem + ".xhtml", src, store, "preface"))
    for tex_name in meta["chapters"]:
        tex_path = root / "latex" / "chapters" / tex_name
        if not tex_path.exists():
            raise BuildError(f"chapter not found: {tex_path}")
        store = Extracted()
        src = preprocess(tex_path.read_text(), store)
        kind = "introduction" if tex_name.startswith("ch00-") else "chapter"
        pre.append((Path(tex_name).stem + ".xhtml", src, store, kind))

    labels = scan_labels([(f, s) for f, s, _, _ in pre])

    from .handlers import citations, notes  # registry side effects + helpers
    bib = citations.load_bib(root / "latex" / "bib" / "references.bib")
    ctx = Context(meta, root, workdir, labels, bib)

    # Convert chapters.
    chapters: list[dict] = []
    chapter_number = 0
    for fname, src, store, kind in pre:
        if kind == "chapter":
            chapter_number += 1
        ctx.begin_chapter(chapter_number, fname, store, kind)
        body = ctx.convert_blocks(TexSoup(src).contents)
        body.append(notes.render_endnotes(ctx))
        chapters.append({
            "file": fname,
            "title": ctx.plain(ctx.chapter_title) or kind.title(),
            "number": chapter_number if kind == "chapter" else None,
            "kind": kind,
            "sections": list(ctx.sections),
            "body": "\n".join(b for b in body if b),
        })

    # Assemble the container file map (path inside zip -> bytes/str).
    lang = meta.get("language", "en")
    css = (root / "epub" / "css" / "epub.css").read_text()
    cover_ext = cover.suffix.lower().lstrip(".") or "png"
    cover_href = f"images/cover.{'jpeg' if cover_ext in ('jpg', 'jpeg') else cover_ext}"

    files: dict[str, bytes | str] = {
        "META-INF/container.xml": generators.container_xml(),
        "OEBPS/epub.css": css,
        f"OEBPS/{cover_href}": cover.read_bytes(),
    }
    for href, data in ctx.images.items():
        files[f"OEBPS/{href}"] = data

    bibliography = citations.bibliography_page(ctx) if ctx.cited else None
    pages = generators.generate(meta, chapters, cover_href,
                                bibliography=bibliography, lang=lang,
                                images=list(ctx.images))
    for name, content in pages.items():
        files[f"OEBPS/{name}"] = content

    link_errors = check_links(files)

    suffix = f"-{edition}" if edition else ""
    epub_path = root / "build" / "epub" / f"book{suffix}.epub"
    package_epub(epub_path, files)

    return Report(epub_path=epub_path, unknowns=dict(ctx.unknowns),
                  warnings=list(ctx.warnings), link_errors=link_errors,
                  a11y_errors=list(ctx.a11y_errors),
                  content_errors=list(ctx.content_errors),
                  handled=set(ctx.handled))


# ---------------------------------------------------------------------------
# Gates: internal link check + packaging
# ---------------------------------------------------------------------------

def check_links(files: dict[str, bytes | str]) -> list[str]:
    """Every internal href (noteref, backlink, toc, citation) must resolve
    to an existing file/fragment (epub-pipeline.md gate 3)."""
    ids: dict[str, set[str]] = {}
    for path, data in files.items():
        if isinstance(data, str) and path.endswith((".xhtml", ".opf", ".ncx")):
            name = path.rsplit("/", 1)[-1]
            ids[name] = set(re.findall(r'\bid="([^"]+)"', data))
    errors = []
    for path, data in files.items():
        if not (isinstance(data, str) and path.endswith(".xhtml")):
            continue
        self_name = path.rsplit("/", 1)[-1]
        for href in re.findall(r'href="([^"]+)"', data):
            if href.startswith(("http:", "https:", "mailto:")):
                continue
            target, _, frag = href.partition("#")
            target = target.rsplit("/", 1)[-1] or self_name
            if target.endswith(".css") or target.startswith("images/"):
                continue
            if target not in ids:
                errors.append(f"{self_name}: broken link {href!r}")
            elif frag and frag not in ids[target]:
                errors.append(f"{self_name}: missing fragment {href!r}")
    return errors


def package_epub(path: Path, files: dict[str, bytes | str]) -> None:
    """OCF zip: `mimetype` first and STORED (uncompressed) — the exact fix
    carried by the datacenter book's package_epub.py."""
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = time.gmtime(int(os.environ.get("SOURCE_DATE_EPOCH", time.time())))
    date_time = stamp[:6]

    def info(name: str) -> zipfile.ZipInfo:
        zi = zipfile.ZipInfo(name, date_time=date_time)
        zi.external_attr = 0o644 << 16
        return zi

    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr(info("mimetype"), MIMETYPE, zipfile.ZIP_STORED)
        for name in sorted(files):
            data = files[name]
            if isinstance(data, str):
                data = data.encode("utf-8")
            zf.writestr(info(name), data, zipfile.ZIP_DEFLATED)


# ---------------------------------------------------------------------------
# Figure image conversion (used by handlers/media.py via ctx)
# ---------------------------------------------------------------------------

def convert_figure_image(ctx: Context, name: str) -> str | None:
    """Resolve latex/figures/<name>, converting PDF -> PNG via pdftoppm
    (cached in build/epub-work/). Registers bytes; returns epub href."""
    figdir = ctx.root / "latex" / "figures"
    # Chapter sources use the print-facing path ``figures/name`` because
    # LaTeX runs from ``latex/``.  The EPUB resolver already starts inside
    # ``latex/figures``, so remove that one conventional prefix instead of
    # accidentally looking below ``latex/figures/figures``.
    parts = Path(name).parts
    if parts and parts[0] == "figures":
        name = str(Path(*parts[1:]))
    src = None
    for candidate in ([figdir / name] if Path(name).suffix else
                      [figdir / f"{name}{ext}" for ext in
                       (".pdf", ".png", ".jpg", ".jpeg", ".svg")]):
        if candidate.exists():
            src = candidate
            break
    if src is None:
        ctx.warn(f"figure source not found: {name}")
        return None
    stem = src.stem
    if src.suffix.lower() == ".pdf":
        out = ctx.workdir / f"{stem}.png"
        if not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
            if shutil.which("pdftoppm") is None:
                ctx.warn("pdftoppm not found; cannot convert PDF figures")
                return None
            # DPI: 200 is fine at print size; figure-heavy books can
            # raise it (crisper diagrams under reader zoom) via FIGURE_DPI.
            dpi = os.environ.get("FIGURE_DPI", "200")
            subprocess.run(
                ["pdftoppm", "-png", "-r", dpi, "-singlefile",
                 str(src), str(ctx.workdir / stem)],
                check=True, capture_output=True)
        data, href = out.read_bytes(), f"images/{stem}.png"
    else:
        data, href = src.read_bytes(), f"images/{src.name}"
    ctx.images[href] = data
    return href
