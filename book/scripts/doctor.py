# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Drift and toolchain audit (`make doctor`).

Checks the failure modes found across prior book projects:
  - missing toolchain pieces / unresolvable fonts (hard-coded path era)
  - CLAUDE.md advertising make targets that don't exist
  - stale cover-vars relative to the print interior
  - committed build artifacts
  - guides missing their machine-readable lint blocks
  - the Simplified Book English lexicon drifting from its policy sources
Warnings don't fail; errors do.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml
from trim_catalog import (
    KDP_HARDCOVER_MAX_PAGES,
    KDP_HARDCOVER_MIN_PAGES,
    TRIM_CATALOG,
)

ROOT = Path(__file__).resolve().parent.parent
errors, warnings = [], []

FONT_FAMILIES = {
    "libertinus": ["Libertinus Serif", "Libertinus Sans", "Libertinus Mono"],
    "garamond": ["EB Garamond"],
    "plex": ["IBM Plex Serif", "IBM Plex Sans", "IBM Plex Mono"],
}


def check_toolchain(engine: str) -> None:
    needed = [engine, "latexmk", "biber", "gs", "pdfinfo", "pdftoppm",
              "magick", "epubcheck", "uv"]
    for tool in needed:
        if not shutil.which(tool):
            errors.append(f"toolchain: {tool} not found on PATH")
    # Ace (make epub-a11y): a global install is optional — npx fetches
    # it on first run — but some Node runtime must exist.
    if not shutil.which("ace"):
        if shutil.which("npx"):
            warnings.append("toolchain: ace (DAISY) not installed globally; "
                            "`make epub-a11y` fetches its Puppeteer runner via "
                            "npx on first run (network + headless-Chromium "
                            "download)")
        else:
            errors.append("toolchain: neither ace nor npx found — "
                          "`make epub-a11y` needs Node.js")


def check_fonts(profile: str) -> None:
    try:
        listing = subprocess.run(["fc-list"], capture_output=True,
                                 text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        warnings.append("fonts: fc-list unavailable; skipped font check")
        return
    for family in FONT_FAMILIES.get(profile, []):
        if family.lower() in listing.lower():
            continue
        # TeX Live ships fonts outside fontconfig; probe kpsewhich database.
        probe = family.split()[0].lower()
        tex = subprocess.run(["kpsewhich", "--all", f"{probe}-regular.otf"],
                             capture_output=True, text=True)
        found = bool(tex.stdout.strip()) or bool(subprocess.run(
            ["bash", "-c",
             f"find /usr/share/tex* -iname '*{probe}*.otf' -print -quit 2>/dev/null"],
            capture_output=True, text=True).stdout.strip())
        if not found:
            errors.append(f"fonts: {family!r} (profile {profile}) not resolvable")


def make_targets(makefile: Path) -> set[str]:
    """Return concrete targets declared by one Makefile."""
    if not makefile.is_file():
        return set()
    return set(re.findall(r"^([a-z][a-z0-9-]*):", makefile.read_text(), re.M))


def missing_make_targets(claude_text: str, makefiles: tuple[Path, ...]) -> set[str]:
    """Find documented targets absent from both book and repository scopes."""
    real: set[str] = set()
    for makefile in makefiles:
        real.update(make_targets(makefile))
    mentioned = set(re.findall(r"make ([a-z][a-z0-9-]*)", claude_text))
    return mentioned - real


def check_claude_md_targets() -> None:
    claude = ROOT / "CLAUDE.md"
    if not claude.exists():
        warnings.append("CLAUDE.md missing")
        return
    makefiles = (ROOT / "Makefile", ROOT.parent / "Makefile")
    for target in sorted(missing_make_targets(claude.read_text(), makefiles)):
        errors.append(f"drift: CLAUDE.md mentions `make {target}` "
                      "but neither the book nor repository Makefile has such a target")


# KDP minimum gutter (inside margin) by page count, no-bleed interiors.
# Source: KDP "Set Trim Size, Bleed, and Margins" (GVBQ3CMEQW3W2VL6).
KDP_GUTTER_MIN = [(150, 0.375), (300, 0.5), (500, 0.625),
                  (700, 0.75), (828, 0.875)]
INNER_FRACTION = 0.145833  # keep in sync with preamble/geometry.tex


def print_page_count() -> int | None:
    prints = sorted((ROOT / "build" / "latex").glob("book-print*.pdf"))
    if not prints:
        return None
    try:
        out = subprocess.run(["pdfinfo", str(prints[0])], capture_output=True,
                             text=True, check=True).stdout
        return int(re.search(r"Pages:\s+(\d+)", out).group(1))
    except (OSError, subprocess.CalledProcessError, AttributeError):
        return None


def check_gutter_vs_pages(cfg: dict) -> None:
    pages = print_page_count()
    if pages is None:
        return
    preset = cfg["trim"]["preset"]
    paper = cfg["trim"].get("paper", "white")
    maximum = TRIM_CATALOG[preset].paperback_max[paper]
    if pages > maximum:
        errors.append(f"interior is {pages} pages — beyond KDP's "
                      f"{maximum}-page maximum for {preset} on {paper}; "
                      "split or reformat")
        return
    gutter = INNER_FRACTION * TRIM_CATALOG[preset].width
    required = next(g for cap, g in KDP_GUTTER_MIN if pages <= cap)
    if gutter < required:
        errors.append(f"gutter {gutter:.3f}in is below KDP's minimum "
                      f"{required}in for a {pages}-page interior")


def check_hardcover_pages(cfg: dict) -> None:
    """KDP case-laminate hardcover accepts selected trims and 75-550 pages.
    Lulu's 24-799 hardcover range is enforced by update_cover_vars.py."""
    if not cfg.get("formats", {}).get("hardcover"):
        return
    platforms = cfg.get("publishing", {}).get("platforms", []) or []
    if "kdp" not in platforms:
        return
    preset = cfg["trim"]["preset"]
    if not TRIM_CATALOG[preset].kdp_hardcover:
        errors.append(f"hardcover: KDP does not accept trim {preset}")
    pages = print_page_count()
    if pages is not None and not (
            KDP_HARDCOVER_MIN_PAGES <= pages <= KDP_HARDCOVER_MAX_PAGES):
        errors.append(f"hardcover: interior is {pages} pages — KDP hardcover "
                      f"accepts {KDP_HARDCOVER_MIN_PAGES}-"
                      f"{KDP_HARDCOVER_MAX_PAGES}; drop the format or fix "
                      "the interior")


def check_large_trim_type_size(cfg: dict) -> None:
    preset = cfg["trim"]["preset"]
    recommended = TRIM_CATALOG[preset].recommended_base_size
    if cfg["typography"]["base_size"] < recommended:
        warnings.append(f"{preset} with base_size "
                        f"{cfg['typography']['base_size']}: use at least "
                        f"{recommended}pt for this trim")


def check_cover_vars_freshness() -> None:
    vars_tex = ROOT / "latex" / "generated" / "cover-vars.tex"
    prints = sorted((ROOT / "build" / "latex").glob("book-print*.pdf"))
    if vars_tex.exists() and prints:
        newest = max(p.stat().st_mtime for p in prints)
        if vars_tex.stat().st_mtime < newest:
            warnings.append("cover-vars.tex older than the print PDF — "
                            "rerun `make cover-vars` before uploading a cover")


def check_committed_artifacts() -> None:
    try:
        tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, check=True,
                                 capture_output=True, text=True).stdout.split()
    except (OSError, subprocess.CalledProcessError):
        return
    bad = [f for f in tracked
           if re.search(r"\.(pdf|aux|log|bbl|epub|synctex\.gz)$", f)
           and not f.startswith(("releases/", "latex/figures/", "docs/"))]
    for f in bad:
        errors.append(f"committed artifact: {f}")


def check_guides_lint_blocks() -> None:
    style = ROOT / "docs" / "guides" / "STYLE.md"
    tells = ROOT / "docs" / "guides" / "STYLE-AI-TELLS.md"
    if style.exists() and "```banned-words" not in style.read_text():
        errors.append("STYLE.md lacks its ```banned-words block "
                      "(check_style.py reads lint config from the guide)")
    if tells.exists() and "```tell-patterns" not in tells.read_text():
        warnings.append("STYLE-AI-TELLS.md lacks its ```tell-patterns block")


def check_simplified_lexicon() -> None:
    """The SBE dictionary against the two files it is derived from.

    Its policy lives in curated.yaml and its exclusions are read out of
    STYLE.md at build time, so either can move without the committed
    artifact noticing. This is the check that makes that loud.
    """
    import json

    data_dir = ROOT / "scripts" / "data" / "simplified_english"
    lexicon = data_dir / "lexicon.json"
    curated = data_dir / "curated.yaml"
    if not lexicon.exists():
        if (ROOT / "scripts" / "check_simplified.py").exists():
            errors.append("scripts/data/simplified_english/lexicon.json is "
                          "missing — run `make simplified-lexicon`")
        return
    try:
        lex = json.loads(lexicon.read_text())
    except json.JSONDecodeError as e:
        errors.append(f"lexicon.json is not valid JSON ({e})")
        return

    counts = lex.get("counts", {})
    for tier in ("core", "open"):
        if counts.get(tier) != len(lex.get(tier, [])):
            errors.append(f"lexicon.json counts.{tier} ({counts.get(tier)}) "
                          f"disagrees with the {tier} list "
                          f"({len(lex.get(tier, []))}) — rebuild it")
    if set(lex.get("core", ())) & set(lex.get("open", ())):
        errors.append("lexicon.json has words in both core and open")

    if curated.exists():
        policy = yaml.safe_load(curated.read_text()) or {}
        dropped = set(lex.get("deduplicated_against_style_md", ()))
        for key in ("substitutions", "phrase_substitutions"):
            entries = [e for e in (policy.get(key) or [])
                       if isinstance(e, dict)]
            names = [str(e.get("from", "")).casefold() for e in entries]
            dupes = sorted({name for name in names if names.count(name) > 1})
            if dupes:
                errors.append(f"curated.yaml has duplicate {key}: "
                              + ", ".join(dupes))
            want = {
                str(e.get("from", "")).casefold(): (
                    str(e.get("to", "")), e.get("grade"), e.get("source"))
                for e in entries
                if str(e.get("from", "")).casefold() not in dropped
            }
            got = {
                str(e.get("from", "")).casefold(): (
                    str(e.get("to", "")), e.get("grade"), e.get("source"))
                for e in (lex.get(key) or []) if isinstance(e, dict)
            }
            if want != got:
                errors.append(f"lexicon.json {key} drifted from curated.yaml "
                              "— run `make simplified-lexicon`")

        exact_fields = {
            "thresholds": policy.get("thresholds") or {},
            "abbreviation_exempt": sorted(
                policy.get("abbreviation_exempt") or []),
            "marker_only": sorted(str(marker).lower()
                                  for marker in policy.get("marker_only") or []),
            "sensitive": sorted(str(w).lower()
                                for w in (policy.get("never_core") or [])),
        }
        for key, want in exact_fields.items():
            if lex.get(key) != want:
                errors.append(f"lexicon.json {key} drifted from curated.yaml "
                              "— run `make simplified-lexicon`")
        marker_only = {str(marker).lower()
                       for marker in policy.get("marker_only") or []}
        want_markers = [
            str(entry["from"]).lower()
            for key in ("substitutions", "phrase_substitutions")
            for entry in policy.get(key) or []
            if (entry.get("grade") in ("error", "warn")
                or str(entry["from"]).lower() in marker_only)
        ] + ["shall", "thereto", "hereunder", "said party",
             "provided that", "deemed", "aforementioned"]
        want_markers = list(dict.fromkeys(want_markers))
        if lex.get("register_markers") != want_markers:
            errors.append("lexicon.json register_markers drifted from "
                          "curated.yaml — run `make simplified-lexicon`")
        missing_core = sorted(
            set(str(w).lower() for w in (policy.get("always_core") or []))
            - set(lex.get("core", ())))
        if missing_core:
            errors.append("lexicon.json is missing curated always_core words: "
                          + ", ".join(missing_core[:5]))

    for corpus in lex.get("provenance", {}).get("corpora", ()):
        revision = str(corpus.get("revision", ""))
        if not re.fullmatch(r"[0-9a-f]{40}", revision):
            errors.append("lexicon.json corpus provenance lacks a full "
                          f"revision pin for {corpus.get('name', '?')}")
        if not isinstance(corpus.get("marker_rate_per_1k"), (int, float)):
            errors.append("lexicon.json corpus provenance lacks an exact "
                          f"marker rate for {corpus.get('name', '?')}")

    # STYLE.md's ban list is an input to the build: the builder drops any
    # substitution STYLE.md already covers, so one offence is not reported
    # twice. If STYLE.md has moved since, that dedupe is stale.
    # (A banned word staying in core/open is CORRECT — the tiers say a word
    # needs no introduction, which is true of "bedrock"; STYLE.md bans it on
    # a different axis.)
    style = ROOT / "docs" / "guides" / "STYLE.md"
    if style.exists():
        banned: set[str] = set()
        for tag in ("banned-words", "banned-phrases"):
            if (m := re.search(rf"```{tag}\n(.*?)```", style.read_text(),
                               re.DOTALL)):
                banned |= {ln.strip().lower() for ln in m.group(1).splitlines()
                           if ln.strip() and not ln.strip().startswith("#")}
        subs = {s["from"].lower() for s in lex.get("substitutions", ())}
        subs |= {s["from"].lower() for s in lex.get("phrase_substitutions", ())}
        if (dupes := sorted(banned & subs)[:5]):
            warnings.append(
                "STYLE.md and the SBE substitution list both ban "
                f"{', '.join(dupes)} — one offence would be reported twice; "
                "rerun `make simplified-lexicon`")

    # The guide quotes the graded word lists; that region is generated.
    guide = ROOT / "docs" / "guides" / "SIMPLIFIED-ENGLISH.md"
    if guide.exists() and "<!-- sbe:generated:lists" in guide.read_text():
        import subprocess
        want = subprocess.run(
            ["uv", "run", str(ROOT / "scripts" / "check_simplified.py"),
             "--emit-guide-blocks"], capture_output=True, text=True).stdout
        text = guide.read_text()
        a = text.index("<!-- sbe:generated:lists")
        b = text.index("<!-- /sbe:generated -->") + len("<!-- /sbe:generated -->")
        if text[a:b].strip() != want.strip():
            errors.append(
                "docs/guides/SIMPLIFIED-ENGLISH.md's generated word lists are "
                "stale — `uv run --group sbe scripts/check_simplified.py "
                "--emit-guide-blocks` and paste the region back")

    if curated.exists() and curated.stat().st_mtime > lexicon.stat().st_mtime:
        warnings.append("simplified_english/curated.yaml is newer than "
                        "lexicon.json — rerun `make simplified-lexicon`")


def main() -> None:
    cfg = yaml.safe_load((ROOT / "book.yaml").read_text())
    check_toolchain(cfg["typography"]["engine"])
    check_fonts(cfg["typography"]["font_profile"])
    check_claude_md_targets()
    check_gutter_vs_pages(cfg)
    check_hardcover_pages(cfg)
    check_large_trim_type_size(cfg)
    check_cover_vars_freshness()
    check_committed_artifacts()
    check_guides_lint_blocks()
    check_simplified_lexicon()

    for w in warnings:
        print(f"doctor: WARN  {w}")
    for e in errors:
        print(f"doctor: ERROR {e}")
    if errors:
        sys.exit(f"doctor: {len(errors)} error(s), {len(warnings)} warning(s)")
    print(f"doctor: OK ({len(warnings)} warning(s))")


if __name__ == "__main__":
    main()
