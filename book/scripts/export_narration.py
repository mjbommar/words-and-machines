# /// script
# requires-python = ">=3.11"
# ///
"""Per-chapter narration text export (`make narration-export`).

Extracts clean plain text from the built EPUB's chapter XHTML — the
converter has already resolved every LaTeX construct, so this is a
tag-strip, not a second parser. Output feeds AI-narration pipelines
(Google Play auto-narration, KDP Virtual Voice, ElevenLabs);
docs/publishing/NARRATION.md compares the channels.

Narration-specific cleanup:
  - footnote reference markers (superscript numbers) are dropped;
    the chapter-end Notes section is kept as its own passage
  - images are dropped; figure captions are kept (they carry the
    figure's narration-worthy content)
  - code blocks are kept verbatim but fenced with blank lines; books
    where listings shouldn't be narrated can delete those passages

    uv run scripts/export_narration.py            # build/narration/*.txt
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BLOCK_TAGS = {"h1", "h2", "h3", "h4", "p", "li", "figcaption",
              "blockquote", "pre", "aside", "section"}


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.blocks: list[tuple[str, bool]] = []  # (text, is_code)
        self._buf: list[str] = []
        self._skip = 0      # inside noteref/img/backlink
        self._pre = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class", "")
        if tag in ("head", "title", "style"):
            self._skip += 1
        if tag == "a" and ("noteref" in cls or "backlink" in cls):
            self._skip += 1
        if tag in ("img", "nav"):
            pass  # img is void; nav content handled via endtag skip
        if tag == "pre":
            self._flush()
            self._pre += 1
        elif tag in BLOCK_TAGS:
            self._flush()

    def handle_endtag(self, tag):
        if tag in ("head", "title", "style") and self._skip:
            self._skip -= 1
        if tag == "a" and self._skip:
            self._skip -= 1
        if tag == "pre":
            self._flush()
            self._pre = max(0, self._pre - 1)
        elif tag in BLOCK_TAGS:
            self._flush()

    def handle_data(self, data):
        if not self._skip:
            self._buf.append(data)

    def _flush(self):
        text = "".join(self._buf)
        self._buf = []
        if self._pre:
            if text.strip("\n"):
                self.blocks.append((text.strip("\n"), True))
        else:
            text = " ".join(text.split())
            if text:
                self.blocks.append((text, False))

    def result(self) -> list[tuple[str, bool]]:
        self._flush()
        return self.blocks


def chapter_text(xhtml: str) -> tuple[str, int]:
    """(narration text, count of suspicious LaTeX-ish leftovers)."""
    ex = TextExtractor()
    ex.feed(xhtml)
    blocks = ex.result()
    leftovers = sum(
        len(re.findall(r"\\[a-zA-Z]+\{", text))
        for text, is_code in blocks if not is_code)
    return "\n\n".join(text for text, _ in blocks) + "\n", leftovers


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--epub", type=Path,
                    default=ROOT / "build" / "epub" / "book.epub")
    ap.add_argument("--outdir", type=Path,
                    default=ROOT / "build" / "narration")
    args = ap.parse_args()

    if not args.epub.exists():
        sys.exit(f"export_narration: {args.epub} not found — run `make epub`")
    args.outdir.mkdir(parents=True, exist_ok=True)

    total_leftovers = 0
    written = []
    with zipfile.ZipFile(args.epub) as zf:
        chapters = sorted(n for n in zf.namelist()
                          if re.fullmatch(r"OEBPS/ch\d+.*\.xhtml", n))
        for name in chapters:
            text, leftovers = chapter_text(zf.read(name).decode("utf-8"))
            total_leftovers += leftovers
            out = args.outdir / (Path(name).stem + ".txt")
            out.write_text(text)
            written.append(out.name)

    if not written:
        sys.exit("export_narration: no chapter XHTML found in the EPUB")
    if total_leftovers:
        print(f"export_narration: WARNING {total_leftovers} LaTeX-like "
              "fragment(s) in non-code prose — inspect before narration",
              file=sys.stderr)
        return 1
    print(f"export_narration: wrote {len(written)} chapter file(s) to "
          f"{args.outdir.relative_to(ROOT)} (no LaTeX residue in prose)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
