# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""make_arxiv.py — build a self-contained arXiv source bundle.

Ships the pre-generated ``.bbl`` (so arXiv need not run the bibliography
backend), the ``00README.json`` from generate_metadata.py, only the LaTeX
source + final figure PDFs, and — crucially — VERIFIES the bundle compiles
standalone in a temp dir with zero undefined references before packaging.
Modeled on ioctl-census/paper/scripts/make_arxiv.sh, generalized to read
paper.yaml (engine, bib backend) and to inline generated/metadata.tex so
the bundle needs no build step.

    uv run scripts/make_arxiv.py [--keep-comments]

Notes
-----
* biblatex/biber bundles: the ``.bbl`` format must match arXiv's TeX Live
  version (3.3 on TL2025). This script warns if it can detect a mismatch;
  select the matching TeX Live in the 00README when in doubt.
* No shell-escape is used anywhere (the code module is pure listings), so
  the bundle compiles under arXiv's non-shell-escape AutoTeX.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
LATEX = ROOT / "latex"
BUILD = ROOT / "build"
PAPER_YAML = ROOT / "paper.yaml"
ARXIV_OUT = BUILD / "arxiv"

ENGINE_CMD = {"pdflatex": "pdflatex", "xelatex": "xelatex", "lualatex": "lualatex"}


def die(msg: str) -> None:
    print(f"make_arxiv: ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def slug(cfg: dict) -> str:
    title = cfg["paper"].get("short_title") or cfg["paper"]["title"]
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s or "paper"


def collect_sources() -> list[Path]:
    """Every .tex the build \\inputs, plus the bib and final figure PDFs.

    We inline generated/metadata.tex into main.tex (below), so the bundle
    carries no generated/ dir. Figure PDFs are the only binary assets.
    """
    files: list[Path] = []
    files += sorted(LATEX.glob("*.tex"))
    for sub in ("preamble", "frontmatter", "backmatter", "sections"):
        files += sorted((LATEX / sub).glob("*.tex"))
    files += sorted((LATEX / "bib").glob("*.bib"))
    files += sorted((LATEX / "figures").glob("*.pdf"))
    files += [LATEX / "figures" / "figure-preamble.tex"]
    return [f for f in files if f.exists()]


def rel_to_latex(p: Path) -> Path:
    return p.relative_to(LATEX)


def inline_metadata(main_tex: str, metadata_tex: str) -> str:
    """Replace the \\IfFileExists{generated/metadata.tex}{...}{...} guard in
    main.tex with the literal contents of the generated file, so the arXiv
    bundle needs no metadata generation step."""
    # Consume the WHOLE guard: from \IfFileExists through the final `}` on
    # its own line (the block ends with "...py}%\n}\n"). An earlier lazy
    # `.*?}{%.*?}` stopped at \errmessage's closing brace and left a stray
    # `}` — which shipped a bundle that failed with "! Too many }'s".
    pattern = re.compile(
        r"\\IfFileExists\{generated/metadata\.tex\}.*?\n\}\n",
        re.DOTALL,
    )
    block = "% --- inlined generated/metadata.tex (make_arxiv) ---\n" + metadata_tex + "\n"
    new, n = pattern.subn(lambda _m: block, main_tex, count=1)
    if n == 0:
        # Fall back to a simpler \input replacement.
        new = main_tex.replace(r"\input{generated/metadata}", block)
    return new


def main() -> None:
    keep_comments = "--keep-comments" in sys.argv[1:]
    if not PAPER_YAML.exists():
        die("paper.yaml not found")
    cfg = yaml.safe_load(PAPER_YAML.read_text())
    engine = cfg["typography"]["engine"]
    # arXiv's 00README accepts tex/pdftex/latex/pdflatex/xelatex — NOT
    # lualatex. Shipping a bundle arXiv can't process is worse than
    # refusing here; switch to pdflatex/xelatex (or keep lualatex for the
    # local/SSRN PDF only).
    if engine == "lualatex":
        die("engine 'lualatex' is not an accepted arXiv compiler; set "
            "typography.engine to pdflatex or xelatex for the arXiv bundle "
            "(lualatex is fine for make pdf / make ssrn).")
    compiler = ENGINE_CMD[engine]

    # 1. fresh build to refresh main.bbl / main.pdf.
    print("make_arxiv: refreshing build (make pdf)...")
    subprocess.run(["make", "pdf"], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL)
    bbl = BUILD / "latex" / "main.bbl"
    metadata = LATEX / "generated" / "metadata.tex"
    readme = BUILD / "arxiv-readme.json"
    if not metadata.exists():
        die("latex/generated/metadata.tex missing (run make generated)")
    biblatex = cfg["citations"]["system"] == "biblatex"
    if not bbl.exists():
        # biblatex uses .bbl too; if truly absent, bibliography is inline.
        print("make_arxiv: note: no main.bbl (inline bibliography?)")

    # 2. stage sources into a temp dir, inlining metadata.
    stage = Path(tempfile.mkdtemp(prefix="arxiv-stage-"))
    try:
        for f in collect_sources():
            dest = stage / rel_to_latex(f)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(f, dest)

        # Inline generated metadata into main.tex.
        main_src = (LATEX / "main.tex").read_text()
        (stage / "main.tex").write_text(
            inline_metadata(main_src, metadata.read_text()))

        # Ship the .bbl next to main.tex.
        if bbl.exists():
            shutil.copyfile(bbl, stage / "main.bbl")

        # 00README.json (arXiv compiler + TeX Live version).
        if readme.exists():
            shutil.copyfile(readme, stage / "00README.json")

        # 3. verify a clean standalone compile (no metadata gen, no backend).
        print(f"make_arxiv: verifying standalone {compiler} build...")
        for _ in range(2):
            r = subprocess.run(
                [compiler, "-interaction=nonstopmode", "main.tex"],
                cwd=stage, capture_output=True, text=True)
        log = (stage / "main.log")
        if not (stage / "main.pdf").exists():
            tail = "\n".join(r.stdout.splitlines()[-25:])
            die(f"standalone build produced no PDF:\n{tail}")
        # A nonstopmode build can recover from a hard TeX error and still
        # emit a PDF — so PDF-exists is NOT enough. Assert a clean exit and
        # no error lines, or the "verified standalone compile" is hollow.
        logtext = log.read_text(errors="ignore") if log.exists() else ""
        tex_errors = [ln for ln in logtext.splitlines() if ln.startswith("!")]
        if r.returncode != 0 or tex_errors:
            sample = "\n".join(tex_errors[:5]) or "\n".join(r.stdout.splitlines()[-15:])
            die(f"standalone build reported TeX errors (exit {r.returncode}):\n{sample}")
        undef = len(re.findall(r"(?:Citation|Reference) `[^']*' .*undefined",
                               logtext))
        if undef:
            die(f"standalone build has {undef} undefined reference(s)/citation(s)")
        pages = 0
        m = re.search(r"Output written on main\.pdf \((\d+) page", logtext)
        if m:
            pages = int(m.group(1))
        # biblatex .bbl-format sanity note. The version marker is a comment
        # on line 2 of a biber .bbl: "% $ biblatex bbl format version 3.3 $".
        if biblatex and bbl.exists():
            head = bbl.read_text(errors="ignore")[:400]
            fm = re.search(r"bbl format version ([\d.]+)", head)
            if fm:
                warn = "" if fm.group(1) == "3.3" else \
                    "  WARNING: arXiv TL2025 expects 3.3 — select a matching " \
                    "TeX Live on submission or switch to natbib."
                print(f"make_arxiv: biblatex .bbl format {fm.group(1)}{warn}")

        # 4. package the verified stage (drop compile byproducts, incl. the
        # biber control files a standalone run leaves behind).
        for junk in ("main.pdf", "main.log", "main.aux", "main.out",
                     "main.fls", "main.fdb_latexmk", "main.bcf",
                     "main.run.xml", "main.blg"):
            (stage / junk).unlink(missing_ok=True)
        if not keep_comments:
            pass  # arxiv-latex-cleaner is the recommended comment stripper;
                  # we ship source verbatim so the bundle is auditable.

        ARXIV_OUT.mkdir(parents=True, exist_ok=True)
        tarball = ARXIV_OUT / f"{slug(cfg)}-arxiv.tar.gz"
        with tarfile.open(tarball, "w:gz") as tar:
            for f in sorted(stage.rglob("*")):
                if f.is_file():
                    tar.add(f, arcname=str(f.relative_to(stage)))

        size = tarball.stat().st_size / 1024
        print(f"make_arxiv: standalone build OK — {pages} pages, 0 undefined refs")
        print(f"make_arxiv: wrote {tarball.relative_to(ROOT)} ({size:.0f} KB)")
        with tarfile.open(tarball) as tar:
            for n in tar.getnames():
                print(f"  {n}")
    finally:
        shutil.rmtree(stage, ignore_errors=True)


if __name__ == "__main__":
    main()
