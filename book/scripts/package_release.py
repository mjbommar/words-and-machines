# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Package build artifacts into releases/<date>-<printing>/ (make release).

Implements the layout promised by docs/publishing/RELEASE-CHECKLIST.md §4:
slugged artifact names, a release README (printing statement, page count,
spine width, ISBNs, upload map, change-notes stub), and SHA256SUMS over
exactly the shipped files. Assumes `make validate-all` already passed —
this script only packages, it does not build.

    uv run scripts/package_release.py --printing first-printing [--edition NAME]
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"


def slugify(title: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", title.lower())).strip("-")


def pdf_pages(pdf: Path) -> int:
    out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True,
                         text=True, check=True).stdout
    return int(re.search(r"Pages:\s+(\d+)", out).group(1))


def spine_width() -> str:
    vars_tex = ROOT / "latex" / "generated" / "cover-vars.tex"
    if vars_tex.exists():
        m = re.search(r"\\setlength\{\\CoverSpineWidth\}\{([\d.]+)in\}",
                      vars_tex.read_text())
        if m:
            return f'{float(m.group(1)):.4f}"'
    return "unknown — rerun make cover-vars"


def tool_version(cmd: list[str]) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True)
        out = (r.stdout.strip() or r.stderr.strip())  # pdfinfo -v uses stderr
        return out.splitlines()[0] if out else "unknown"
    except OSError:
        return "not found"


def toolchain_report() -> str:
    sde = os.environ.get("SOURCE_DATE_EPOCH", "unset")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                            capture_output=True, text=True).stdout.strip()
    lines = [
        "# Toolchain that produced this release (reproducibility record)",
        f"commit: {commit}",
        f"SOURCE_DATE_EPOCH: {sde}",
        f"lualatex: {tool_version(['lualatex', '--version'])}",
        f"latexmk: {tool_version(['latexmk', '--version'])}",
        f"biber: {tool_version(['biber', '--version'])}",
        f"ghostscript: {tool_version(['gs', '--version'])}",
        f"poppler pdfinfo: {tool_version(['pdfinfo', '-v'])}",
        f"epubcheck: {tool_version(['epubcheck', '--version'])}",
        f"uv: {tool_version(['uv', '--version'])}",
        "",
        "Rebuild recipe: check out the commit above inside the pinned",
        "container from .github/workflows/build.yml, run `make release`,",
        "and compare SHA256SUMS.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--printing", default="first-printing")
    ap.add_argument("--edition", default=None)
    args = ap.parse_args()

    cfg = yaml.safe_load((ROOT / "book.yaml").read_text())
    slug = slugify(cfg["book"]["title"])
    suffix = f"-{args.edition}" if args.edition else ""
    today = date.today().isoformat()

    interior = BUILD / "latex" / f"book-print{suffix}.pdf"
    ebook_pdf = BUILD / "latex" / f"book-ebook{suffix}.pdf"
    epub = BUILD / "epub" / f"book{suffix}.epub"
    kdp_cover = BUILD / "cover" / "cover-kdp.pdf"
    kindle_jpg = BUILD / "cover" / "cover-kindle.jpg"
    pdfx = BUILD / "pdfx" / f"book-print{suffix}-x1a.pdf"
    onix = BUILD / "onix" / "onix-30.xml"

    # (source, slugged destination name, upload destination description)
    artifacts = [
        (interior, f"{slug}{suffix}-interior.pdf", "KDP paperback ‘manuscript’ upload"),
        (kdp_cover, f"{slug}{suffix}-cover-kdp.pdf", "KDP paperback cover upload"),
        (epub, f"{slug}{suffix}.epub", "KDP ebook ‘manuscript’ upload"),
        (kindle_jpg, f"{slug}{suffix}-cover-kindle.jpg", "KDP ebook cover upload"),
        (ebook_pdf, f"{slug}{suffix}-ebook.pdf", "direct-download / website PDF"),
        (pdfx, f"{slug}{suffix}-interior-x1a.pdf",
         "IngramSpark/Lulu interior (PDF/X-1a; cover comes from Ingram's template)"),
        (onix, f"{slug}{suffix}-onix-30.xml",
         "ONIX 3.0 feed (aggregators, libraries; carries the accessibility codes)"),
    ]
    missing = [str(src.relative_to(ROOT)) for src, _, _ in artifacts if not src.exists()]
    if missing:
        sys.exit("package_release: missing artifacts (run make validate-all "
                 "pdfx onix cover-image first): " + ", ".join(missing))

    out_dir = ROOT / "releases" / f"{today}-{args.printing}"
    if out_dir.exists():
        sys.exit(f"package_release: {out_dir.relative_to(ROOT)} already exists")
    out_dir.mkdir(parents=True)

    names = []
    for src, name, _ in artifacts:
        shutil.copy2(src, out_dir / name)
        names.append(name)

    pages = pdf_pages(interior)
    ids = cfg.get("identifiers", {})
    upload_rows = "\n".join(f"| `{name}` | {dest} |"
                            for _, name, dest in artifacts)
    (out_dir / "README.md").write_text(f"""\
# {cfg['book']['title']} — {args.printing} ({today})

- **Edition:** {args.edition or 'default'} · {cfg['book'].get('edition_statement', '')}
- **Interior:** {pages} pages, trim {cfg['trim']['preset']}, {cfg['trim'].get('paper', 'white')} paper
- **Spine width:** {spine_width()}
- **ISBN (print):** {ids.get('isbn_print') or '—'}
- **ISBN (ebook):** {ids.get('isbn_epub') or '—'}
- **Build date:** {today}

## What changed since the last printing

- TODO: fill in before uploading (or "initial release").

## Upload map

| File | Uploads to |
{upload_rows}

Verify from a clean shell before uploading: `sha256sum -c SHA256SUMS`.
Upload from THIS directory, never from `build/`.
""")

    # Toolchain record: what produced these bytes. With the Makefile's
    # SOURCE_DATE_EPOCH pin, a rebuild on this toolchain reproduces the
    # SHA256SUMS exactly; this file is how a future you re-creates it.
    (out_dir / "TOOLCHAIN.txt").write_text(toolchain_report())

    sums = out_dir / "SHA256SUMS"
    with sums.open("w") as f:
        for name in sorted(names):
            digest = hashlib.sha256((out_dir / name).read_bytes()).hexdigest()
            f.write(f"{digest}  {name}\n")

    print(f"package_release: {out_dir.relative_to(ROOT)} "
          f"({len(names)} artifacts, {pages}pp, spine {spine_width()})")
    print("package_release: edit the release README's change notes, then "
          f"commit and tag (printing/{today}).")


if __name__ == "__main__":
    main()
