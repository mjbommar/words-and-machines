# /// script
# requires-python = ">=3.11"
# ///
"""PDF/X-1a derivative for IngramSpark/Lulu (`make pdfx`).

IngramSpark requires PDF/X-1a:2001 or X-3:2002 interiors and covers;
Lulu recommends the same. KDP does not need PDF/X — its uploads stay on
the untouched LuaLaTeX output. Ghostscript re-distills the whole file
(it can re-encode images), which is why this is a *derivative* target:
the canonical build artifacts are never modified.

Pipeline: write a PDFX_def.ps declaring the CMYK OutputIntent, then
    gs -dPDFX -dPDFXCompatibilityPolicy=1 -sColorConversionStrategy=CMYK
       -dCompatibilityLevel=1.3 ...
and verify the result actually carries /GTS_PDFXVersion + /OutputIntents
(veraPDF validates PDF/A and PDF/UA, not PDF/X, so this smoke check plus
Ghostscript's own conformance pass is the practical CI gate).

ICC profile resolution: $PDFX_ICC, then a system SWOP-compatible
profile (CGATS TR 001), then Ghostscript's default_cmyk.icc (declared
with identifier "Custom"). Ship the real profile you prove with.
"""

from __future__ import annotations

import argparse
import glob
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SWOP_CANDIDATES = [
    "/usr/share/color/icc/USWebCoatedSWOP.icc",
    "/usr/share/color/icc/adobe/USWebCoatedSWOP.icc",
    "/usr/share/color/icc/CGATS001Compat-v2-micro.icc",
]


def find_icc() -> tuple[Path, str]:
    """(profile path, OutputConditionIdentifier)."""
    env = os.environ.get("PDFX_ICC")
    if env:
        p = Path(env)
        if not p.exists():
            sys.exit(f"export_pdfx: $PDFX_ICC={env} does not exist")
        return p, "Custom"
    for cand in SWOP_CANDIDATES:
        if Path(cand).exists():
            return Path(cand), "CGATS TR 001"
    gs_icc = sorted(glob.glob(
        "/usr/share/ghostscript/*/iccprofiles/default_cmyk.icc"))
    if gs_icc:
        return Path(gs_icc[-1]), "Custom"
    sys.exit("export_pdfx: no CMYK ICC profile found — set $PDFX_ICC "
             "(install icc-profiles-free for a SWOP-compatible one)")


def pdfx_def(icc: Path, identifier: str, title: str) -> str:
    """Canonical Ghostscript PDFX_def.ps shape (doc/pdfwrite docs),
    with our OutputIntent values substituted."""
    escaped = str(icc).replace("\\", "/").replace("(", r"\(").replace(")", r"\)")
    safe_title = title.replace("(", r"\(").replace(")", r"\)")
    return f"""%!
% PDFX_def.ps — OutputIntent prefix for the PDF/X distill (generated).
/ICCProfile ({escaped}) def

[ /Title ({safe_title})
  /Trapped /False
  /DOCINFO pdfmark

[ /GTS_PDFXVersion (PDF/X-1a:2001)
  /GTS_PDFXConformance (PDF/X-1a:2001)
  /DOCINFO pdfmark

[ /_objdef {{icc_PDFX}} /type /stream /OBJ pdfmark
[ {{icc_PDFX}} << /N 4 >> /PUT pdfmark
[ {{icc_PDFX}} ICCProfile (r) file /PUT pdfmark

[ /_objdef {{OutputIntent_PDFX}} /type /dict /OBJ pdfmark
[ {{OutputIntent_PDFX}} <<
  /Type /OutputIntent
  /S /GTS_PDFX
  /OutputCondition (Commercial and specialty printing)
  /OutputConditionIdentifier ({identifier})
  /RegistryName (http://www.color.org)
  /DestOutputProfile {{icc_PDFX}}
>> /PUT pdfmark
[ {{Catalog}} << /OutputIntents [ {{OutputIntent_PDFX}} ] >> /PUT pdfmark
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--pdf", type=Path,
                    default=ROOT / "build" / "latex" / "book-print.pdf")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--title", default="",
                    help="document title for the PDF/X Info dict")
    args = ap.parse_args()

    if not args.pdf.exists():
        sys.exit(f"export_pdfx: {args.pdf} not found — build it first")
    icc, identifier = find_icc()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    # Ghostscript -dSAFER can't read system color dirs; use a local copy.
    icc_local = args.out.parent / icc.name
    icc_local.write_bytes(icc.read_bytes())
    def_ps = args.out.parent / "PDFX_def.ps"
    def_ps.write_text(pdfx_def(icc_local, identifier,
                               args.title or args.pdf.stem))

    cmd = ["gs", "-dPDFX", "-dBATCH", "-dNOPAUSE", "-dNOOUTERSAVE", "-q",
           # -dSAFER (default) blocks file reads; the def file must open
           # the ICC profile we just copied beside it.
           f"--permit-file-read={args.out.parent}/",
           "-sDEVICE=pdfwrite", "-dPDFXCompatibilityPolicy=1",
           "-dCompatibilityLevel=1.3",
           "-sColorConversionStrategy=CMYK",
           "-dProcessColorModel=/DeviceCMYK",
           # hyperref's link annotations are forbidden in PDF/X-1a and
           # meaningless on paper — drop them in the distill.
           "-dPreserveAnnots=false",
           "-dEmbedAllFonts=true", "-dSubsetFonts=true",
           f"-sOutputFile={args.out}", str(def_ps), str(args.pdf)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    chatter = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode or not args.out.exists():
        print(chatter[-1500:], file=sys.stderr)
        sys.exit(f"export_pdfx: ghostscript failed (exit {proc.returncode})")
    if "reverting to normal PDF output" in chatter:
        offending = [ln for ln in chatter.splitlines()
                     if "not permitted" in ln or "reverting" in ln]
        print("\n".join(offending), file=sys.stderr)
        sys.exit("export_pdfx: input has PDF/X-incompatible content — "
                 "Ghostscript reverted to plain PDF (see above)")

    raw = args.out.read_bytes()
    missing = [m for m in ("/GTS_PDFXVersion", "/OutputIntents")
               if m.encode() not in raw]
    if missing:
        sys.exit(f"export_pdfx: output lacks {', '.join(missing)} — "
                 "not a PDF/X file; inspect the Ghostscript output")

    print(f"export_pdfx: wrote {args.out} "
          f"(PDF/X-1a:2001, OutputIntent {identifier}: {icc.name})")
    if identifier == "Custom":
        print("export_pdfx: NOTE using a generic CMYK profile — set "
              "$PDFX_ICC to your press profile before uploading",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
