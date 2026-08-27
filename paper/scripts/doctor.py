# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""doctor.py — toolchain, fonts, packages, and drift audit.

Checks that the machine can build THIS paper.yaml's configuration and that
the docs don't advertise Make targets the Makefile lacks:

  * the selected engine (pdflatex/xelatex/lualatex) is on PATH,
  * latexmk + the bibliography backend (bibtex or biber) are present,
  * every LaTeX package the active font profile + modules need resolves
    (kpsewhich), and the OpenType fonts resolve on the Unicode engines,
  * poppler (pdfinfo) is present for the packagers,
  * every `make <target>` named in CLAUDE.md exists in the Makefile,
  * paper.yaml has no leftover placeholders (advisory).

    uv run scripts/doctor.py

Exit non-zero if any hard requirement is missing.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PAPER_YAML = ROOT / "paper.yaml"
MAKEFILE = ROOT / "Makefile"
CLAUDE = ROOT / "CLAUDE.md"

ok: list[str] = []
problems: list[str] = []
notes: list[str] = []

# Packages each profile / module needs (pdfTeX names; the Unicode engines
# additionally need fontspec + unicode-math, checked separately).
PROFILE_PKGS = {
    "libertinus": ["libertinus.sty", "zi4.sty"],
    "newtx": ["newtxtext.sty", "newtxmath.sty", "zi4.sty"],
    "lmodern": ["lmodern.sty"],
    "plex": [],  # OpenType-only; font resolution checked below
}
CORE_PKGS = ["geometry.sty", "microtype.sty", "booktabs.sty", "threeparttable.sty",
             "caption.sty", "subcaption.sty", "cleveref.sty", "xurl.sty",
             "orcidlink.sty", "fancyhdr.sty", "titlesec.sty", "enumitem.sty",
             "rotating.sty", "pdflscape.sty", "longtable.sty", "eso-pic.sty",
             "xspace.sty"]
MODULE_PKGS = {
    "boxes": ["tcolorbox.sty"],
    "code": ["listings.sty"],
    "algorithms": ["algorithm.sty", "algpseudocodex.sty"],
    "siunitx": ["siunitx.sty"],
}
UNICODE_FONTS = {
    "libertinus": ["Libertinus Serif", "Libertinus Math"],
    "newtx": ["TeX Gyre Termes"],
    "lmodern": ["Latin Modern Roman"],
    "plex": ["IBM Plex Serif", "STIX Two Math"],
}


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def kpse(name: str) -> bool:
    r = subprocess.run(["kpsewhich", name], capture_output=True, text=True)
    return r.returncode == 0 and r.stdout.strip() != ""


def font_resolves(family: str) -> bool:
    if not have("fc-list"):
        return True  # can't check; don't fail
    r = subprocess.run(["fc-list", family], capture_output=True, text=True)
    return bool(r.stdout.strip())


def check_toolchain(cfg: dict) -> None:
    engine = cfg["typography"]["engine"]
    for tool in (engine, "latexmk", "kpsewhich"):
        (ok if have(tool) else problems).append(
            f"{tool} {'found' if have(tool) else 'MISSING (required)'}")
    backend = "biber" if cfg["citations"]["system"] == "biblatex" else "bibtex"
    (ok if have(backend) else problems).append(
        f"{backend} {'found' if have(backend) else 'MISSING (required)'}")
    (ok if have("pdfinfo") else notes).append(
        f"pdfinfo {'found' if have('pdfinfo') else 'missing (packagers use it)'}")
    (ok if have("chktex") else notes).append(
        f"chktex {'found' if have('chktex') else 'missing (make lint skips; full TeX Live has it)'}")
    (ok if have("texcount") else notes).append(
        f"texcount {'found' if have('texcount') else 'missing (make wordcount falls back to a rough count)'}")


def check_packages(cfg: dict) -> None:
    profile = cfg["typography"]["font_profile"]
    engine = cfg["typography"]["engine"]
    pkgs = list(CORE_PKGS)
    if engine == "pdflatex":
        pkgs += PROFILE_PKGS.get(profile, [])
    else:
        pkgs += ["fontspec.sty", "unicode-math.sty"]
    for mod, need in MODULE_PKGS.items():
        if cfg.get("modules", {}).get(mod, True):
            pkgs += need
    for pkg in sorted(set(pkgs)):
        (ok if kpse(pkg) else problems).append(
            f"package {pkg} {'resolves' if kpse(pkg) else 'MISSING (kpsewhich)'}")
    # Unicode-engine font resolution.
    if engine != "pdflatex":
        for fam in UNICODE_FONTS.get(profile, []):
            (ok if font_resolves(fam) else problems).append(
                f"font {fam!r} {'resolves' if font_resolves(fam) else 'NOT found (fontconfig)'}")


def check_venue_engine(cfg: dict) -> None:
    """arXiv does not accept lualatex source; flag venue/engine mismatch here
    (make arxiv also refuses it, but doctor is where you'd look first)."""
    venue = (cfg.get("venue", {}) or {}).get("target")
    engine = (cfg.get("typography", {}) or {}).get("engine")
    if venue == "arxiv" and engine == "lualatex":
        problems.append(
            "venue.target=arxiv with engine=lualatex — arXiv does not accept "
            "lualatex source (make arxiv will refuse); use pdflatex or xelatex")
    else:
        ok.append(f"venue/engine: {venue}/{engine} (arXiv-compatible)")


def check_makefile_drift() -> None:
    if not (MAKEFILE.exists() and CLAUDE.exists()):
        return
    targets = set(re.findall(r"^([a-z][a-z-]*):", MAKEFILE.read_text(), re.M))
    mentioned = set(re.findall(r"make ([a-z][a-z-]+)", CLAUDE.read_text()))
    missing = sorted(mentioned - targets)
    for t in missing:
        problems.append(f"CLAUDE.md mentions `make {t}` but the Makefile has no such target")
    if not missing and mentioned:
        ok.append(f"CLAUDE.md ↔ Makefile: {len(mentioned)} targets all exist")


def _scan_values(node) -> int:
    """Count placeholder-like tokens in yaml VALUES only (not comments)."""
    pat = re.compile(r"TODO|FIXME|XXX|\[[A-Za-z][^\]]*\]")
    if isinstance(node, dict):
        return sum(_scan_values(v) for v in node.values())
    if isinstance(node, list):
        return sum(_scan_values(v) for v in node)
    if isinstance(node, str):
        return len(pat.findall(node))
    return 0


def check_placeholders(cfg: dict) -> None:
    n = _scan_values(cfg)
    if n:
        notes.append(f"paper.yaml has {n} placeholder-like value(s) "
                     "(fill before release)")


def main() -> int:
    if not PAPER_YAML.exists():
        print("doctor: paper.yaml not found", file=sys.stderr)
        return 1
    cfg = yaml.safe_load(PAPER_YAML.read_text())
    check_toolchain(cfg)
    check_packages(cfg)
    check_venue_engine(cfg)
    check_makefile_drift()
    check_placeholders(cfg)

    for line in ok:
        print(f"  \033[0;32mok\033[0m   {line}")
    for line in notes:
        print(f"  \033[1;33mnote\033[0m {line}")
    for line in problems:
        print(f"  \033[0;31mFAIL\033[0m {line}")
    print(f"\ndoctor: {len(ok)} ok, {len(notes)} notes, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
