# Cover Specification

How the wrap cover works: anatomy, safe zones, the page-count → spine →
render pipeline, and the ebook cover raster. Decision record: ADR 0008.

---

## 1. Wrap-cover anatomy

One PDF, one page: back cover + spine + front cover, laid out left → right,
with bleed on all four outer edges.

```
        ◄────────────────────── total wrap width ──────────────────────►
        ┌─┬──────────────────────┬────────┬──────────────────────┬─┐ ▲
        │b│                      │        │                      │b│ │ bleed 0.125"
        │l│      BACK COVER      │ SPINE  │     FRONT COVER      │l│ │
        │e│                      │        │                      │e│ │
        │e│  description text    │ title  │   title / subtitle   │e│ │ trim
        │d│  author bio          │ author │   author             │d│ │ height
        │ │  ┌────────────┐      │        │                      │ │ │
        │ │  │  BARCODE   │      │        │                      │ │ │
        │ │  │ quiet zone │      │        │                      │ │ │
        │ │  └────────────┘      │        │                      │ │ ▼
        └─┴──────────────────────┴────────┴──────────────────────┴─┘
           ◄──── trim width ────► ◄spine─► ◄──── trim width ────►
```

- **Total wrap** = `2 × trim width + spine + 2 × bleed` wide ×
  `trim height + 2 × bleed` tall.
- **Bleed**: 0.125" (KDP and Lulu paperback). Background art must run to the
  bleed edge — never end at the trim line. **Lulu hardcover case wrap** uses
  0.875" (0.75" board wrap + 0.125" bleed) and larger board-driven panels;
  the script computes it.
- **Safe zone**: keep all text and critical art ≥0.25" inside the trim edges,
  and off the spine folds.
- **Spine**: width is computed from the page count
  ([`KDP-TEMPLATE.md`](KDP-TEMPLATE.md) §3 has the formulas). Spine text only
  at ≥80 pages; inset spine text ≥0.0625" from both folds — KDP's fold
  tolerance is ±0.0625", so text that touches a fold will sometimes wrap it.
- **Barcode zone**: lower-right of the back cover, nominal 2" × 1.2",
  ≥0.25" inside trim. On dark covers reserve a **white quiet-zone box** there
  (KDP's auto-placed barcode won't scan on dark ink). Either let KDP place
  its barcode in that box, or embed your own ≥300-DPI EAN-13 on a white
  background — never both.

All cover text (title, subtitle, author, description, ISBN) comes from the
metadata macros generated out of `book.yaml` — the TikZ file contains **no
literal book strings** (ADR 0002).

---

## 2. The pipeline: page count → spine → cover PDF

`latex/cover/cover.tex` is a standalone TikZ document that renders the full
wrap for three platforms via `\ifdefined` switches (`\KDPCover`,
`\LuluPaperback`, `\LuluHardcover`). It consumes two generated files:
`latex/generated/metadata.tex` (identity) and `latex/generated/cover-vars.tex`
(dimensions).

```
make pdf                     # interior must be built (and FINAL) first
   └─► build/book-print.pdf
make cover-vars              # scripts/update_cover_vars.py
   ├─ reads page count via pdfinfo on the print PDF
   ├─ computes spine width for the platform/binding
   │    (KDP white/cream/groundwood/color formulas, Lulu /444 formula,
   │     Lulu hardcover lookup table — all in the script)
   └─► latex/generated/cover-vars.tex
        (trim, bleed, spine, total wrap dimensions)
make kdp-cover               # or: make lulu-cover
   ├─ 3-pass TikZ render of cover.tex (passes stabilize
   │    overlay positioning; do not trust a 1-pass build)
   ├─ Ghostscript /prepress flatten:
   │    gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   │       -dPDFSETTINGS=/prepress -sOutputFile=out.pdf in.pdf
   │    (flattens transparency KDP's pipeline mishandles;
   │     embeds/normalizes fonts)
   └─ dimension check: pdfinfo page size must equal the
        computed wrap — mismatch fails the target
```

Rules that follow from the dependency chain:

1. **The interior drives the cover.** Any change to the interior page count
   invalidates `cover-vars.tex` and therefore the cover PDF. Rebuild order:
   `make pdf` → `make cover-vars` → `make kdp-cover`.
2. `make doctor` warns when `cover-vars.tex` is older than the print PDF;
   [`RELEASE-CHECKLIST.md`](RELEASE-CHECKLIST.md) treats that warning as a
   release blocker.
3. Raster assets placed on the cover must be ≥300 DPI **at wrap size** — a
   background image that was fine on a screen mock is usually not. Vector
   (TikZ/PDF) art is preferred; it is crisp at any size. `make preflight`
   gates both (fonts embedded, no Type 3, ≥300 ppi).
4. **Total ink coverage:** POD presses cap C+M+Y+K at ~240% per spot
   (KDP/SWOP). `make cover-ink` measures the true per-pixel maximum via
   Ghostscript separations and fails above the cap — which is why
   `cover-field` is defined directly in CMYK in `preamble/colors.tex`
   (an RGB near-black converts to ~274%). Runs in `make validate-all`.
5. For predictable print color, optionally convert the flattened wrap to
   CMYK PDF/X-1a:2001 before upload — recipe in
   [`KDP-TEMPLATE.md`](KDP-TEMPLATE.md) §4 (manual Ghostscript step; the
   interior equivalent is automated as `make pdfx`).
6. **IngramSpark covers are different:** Ingram requires its per-ISBN
   Cover Template Generator output (own spine math and bleed) — do not
   reuse the KDP wrap or these spine formulas for Ingram uploads. The
   `make pdfx` interior is the IngramSpark-ready piece.

---

## 3. Ebook / Kindle cover raster

`make cover-image` exports the **front panel only** of the wrap, as two
files for two different consumers:

| File | Spec | Use |
|---|---|---|
| `build/cover/cover-front.png` | PNG at the book's true trim ratio (e.g. 1707×2560 for 6×9), height 2560 px | Embedded in the EPUB by the converter — readers show the real cover proportions |
| `build/cover/cover-kindle.jpg` | JPEG, exactly 1600×2560 (KDP's "ideal" per spec G200645690; 1.6:1 height:width; minimum 1000 px long side) | **KDP ebook listing upload only** — do not embed this one |

The trim ratio (1.5:1 at 6×9) is not Kindle's 1.6:1, so the KDP JPEG is
letterboxed with the cover's own field color — check that nothing critical
reads badly against the extended edges. Keep the art identical between the
two so the store listing and the reader library show the same cover.

---

## 4. Optional pattern: cover-as-code

Art direction lives in `latex/cover/cover.tex` (layout, typography, color
from the preamble palette). For generative/algorithmic cover art, the proven
pattern is a standalone **matplotlib (or similar) generator script** that
renders the front-panel art to a vector PDF, which `cover.tex` then places
like any other asset:

- The generator is deterministic (seeded) and checked into `scripts/` or a
  book-specific `src/`, so the art is reproducible from code — same
  philosophy as the rest of the build.
- Output vector PDF where possible; if raster, render at ≥300 DPI at final
  panel size.
- Algorithmic art is author-created code output — relevant to the AI-content
  disclosure discussion in [`KDP-TEMPLATE.md`](KDP-TEMPLATE.md) §6.

This template ships the TikZ wrap only; a generator is a per-book addition.
