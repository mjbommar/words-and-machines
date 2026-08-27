# ADR 0008 — One TikZ wrap-cover template; spine width computed from page count

## Decision
`latex/cover/cover.tex` is a standalone TikZ document rendering the full wrap (back–spine–front) for three platforms via `\ifdefined` switches: **KDP paperback**, **Lulu paperback**, **Lulu hardcover** (wrap + board sizing). `scripts/update_cover_vars.py`:

1. Reads interior page count via `pdfinfo` on the built print PDF
2. Computes spine width — KDP white `pages × 0.002252 + 0.06 in` (cream variant included), Lulu paperback `pages / 444 + 0.06 in`, Lulu hardcover from the published lookup table
3. Emits `latex/generated/cover-vars.tex` (trim, bleed, spine, total wrap dimensions)

Cover text (title/subtitle/author/description/ISBN) comes from metadata macros (ADR 0002). `make kdp-cover` chains: interior build → cover-vars → 3-pass TikZ render → Ghostscript `/prepress` flatten → dimension-check gate. `make cover-image` exports the front panel as the EPUB/Kindle cover raster (1.6:1 padding for Kindle).

## Evidence
This machinery shipped real books on all three platforms (datacenter, htsd, iliad, ovid, ai-law-finance). The spine formulas and hardcover lookup are copied from `update_cover_vars.py` variants that match printed proofs.

## Consequences
- Page-count changes require re-running cover-vars before re-uploading a cover; `make doctor` warns when cover-vars.tex is older than the print PDF.
- Art direction stays in the TikZ file; an optional cover-as-code generator (RFC's matplotlib pattern) is documented in `docs/publishing/COVER-SPEC.md`, not shipped.
