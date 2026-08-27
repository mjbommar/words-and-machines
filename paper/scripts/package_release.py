# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""package_release.py — stamped release directory with checksums.

Copies the build's shippable artifacts into releases/<date>-<slug>/ with a
SHA256SUMS file and a TOOLCHAIN.txt rebuild recipe, so a release is a
self-describing, verifiable snapshot. Called by `make release` after the
gates pass. The date comes from git (last commit) to stay reproducible.

    uv run scripts/package_release.py
"""
from __future__ import annotations

import hashlib
import shutil
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
PAPER_YAML = ROOT / "paper.yaml"


def slug(cfg: dict) -> str:
    import re
    title = cfg["paper"].get("short_title") or cfg["paper"]["title"]
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "paper"


def git(*args: str) -> str:
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main() -> None:
    cfg = yaml.safe_load(PAPER_YAML.read_text())
    date = git("log", "-1", "--format=%cd", "--date=short") or "unknown-date"
    commit = git("rev-parse", "--short", "HEAD") or "nogit"
    rel = ROOT / "releases" / f"{date}-{slug(cfg)}"
    rel.mkdir(parents=True, exist_ok=True)

    artifacts = [
        BUILD / "latex" / "main.pdf",
    ]
    for tar in (BUILD / "arxiv").glob("*.tar.gz"):
        artifacts.append(tar)
    if (ROOT / "SSRN-METADATA.md").exists():
        artifacts.append(ROOT / "SSRN-METADATA.md")

    copied = []
    for a in artifacts:
        if a.exists():
            dest = rel / a.name
            shutil.copyfile(a, dest)
            copied.append(dest)

    sums = "\n".join(f"{sha256(f)}  {f.name}" for f in copied) + "\n"
    (rel / "SHA256SUMS").write_text(sums)

    engine = cfg["typography"]["engine"]
    (rel / "TOOLCHAIN.txt").write_text(
        f"paper: {cfg['paper']['title']}\n"
        f"commit: {commit}\n"
        f"engine: {engine}\n"
        f"font_profile: {cfg['typography']['font_profile']}\n"
        f"bib: {cfg['citations']['system']}/{cfg['citations'].get('style','')}\n"
        f"venue: {cfg['venue']['target']}\n"
        f"rebuild: make validate && make {cfg['venue']['target']}\n"
        f"texlive: 2025 (target)\n")

    print(f"package_release: wrote {rel.relative_to(ROOT)} "
          f"({len(copied)} artifacts + SHA256SUMS + TOOLCHAIN.txt)")


if __name__ == "__main__":
    main()
