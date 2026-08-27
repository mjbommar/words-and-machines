# KDP Publishing Runbook — Template

Fill-in runbook for publishing a book built from this template on Amazon KDP
(with Lulu paperback/hardcover notes where they differ). Copy-or-generate:
`uv run scripts/generate_metadata.py --emit-kdp` writes a `docs/publishing/KDP.md`
skeleton pre-filled from `book.yaml`; this file is the full genre it grows into.

House rule (ADR 0002): every identity value in this runbook — title, subtitle,
author, ISBNs, description, keywords, BISAC — must match `book.yaml` exactly.
If they disagree, fix `book.yaml` and rebuild; never fork the metadata here.

Account setup, tax interview, and banking are out of scope (one-time per
publisher account).

---

## 1. Files to upload

| Asset | Build | Upload to |
|---|---|---|
| Paperback interior | `make pdf` → `build/book-print.pdf` | KDP paperback (manuscript) |
| Paperback wrap cover | `make kdp-cover` (runs `make cover-vars` first) | KDP paperback (cover) |
| Kindle eBook | `make epub` (epubcheck must be 0 errors) | KDP Kindle |
| eBook cover raster | `make cover-image` | KDP Kindle (form upload; also embedded in EPUB) |
| Lulu covers | `make lulu-cover` | Lulu paperback / hardcover |

The interior PDF must **not** include the wrap cover — it starts at the
half-title. If any content runs to the page edge, upload the `make bleed`
build instead and tell KDP the manuscript has bleed.

**If the page count changes, the spine changes.** Rebuild in this order:
`make pdf` → `make cover-vars` → `make kdp-cover`. `make doctor` warns when
`latex/generated/cover-vars.tex` is older than the print PDF.

---

## 2. Interior specification

| Attribute | Value | Notes |
|---|---|---|
| Trim size | from `trim.preset` in `book.yaml` | 6×9 US Trade default; 7×10, 5.5×8.5, 5×8 presets |
| Page count | `pdfinfo build/book-print.pdf` | Drives spine width and printing cost |
| Paper | `trim.paper`: white or cream | White for figures/charts; affects spine formula |
| Ink | Black & white unless figures require color | Color multiplies printing cost |
| Bleed | None for standard interiors | Full-bleed art → `make bleed` + 0.125" bleed declared |
| Fonts | All embedded, vector, no Type 3 | Verify: `pdffonts build/book-print.pdf` |
| Rasters | ≥300 DPI | Body should be text + vector figures |

### KDP minimum margins (no-bleed; add 0.125" to outside/top/bottom with bleed)

| Page count | Gutter (inside) | Outside/top/bottom |
|---|---|---|
| 24–150 | 0.375" | 0.25" |
| 151–300 | 0.5" | 0.25" |
| 301–500 | 0.625" | 0.25" |
| 501–700 | 0.75" | 0.25" |
| 701–828 | 0.875" | 0.25" |

The template's geometry (roughly 0.875" gutter / 0.625" outside / 0.75"
top-bottom at 6×9) clears these comfortably for typical trade lengths.
Re-check this table against KDP Help if your page count crosses a band.

---

## 3. Spine width formulas

Computed automatically by `scripts/update_cover_vars.py` (via `make cover-vars`)
from the built print PDF's page count. For sanity checks:

| Platform / binding | Formula (inches) |
|---|---|
| KDP paperback, white paper | `pages × 0.002252` |
| KDP paperback, cream paper | `pages × 0.0025` |
| KDP paperback, standard color | `pages × 0.002252` (white stock) |
| KDP paperback, premium color | `pages × 0.002347` |
| Lulu paperback (perfect bound, standard) | `pages / 444 + 0.06` |
| Lulu paperback (magazine paper) | `pages / 460 + 0.06` |
| Lulu hardcover (case wrap) | Lookup table by page range — see `LULU_HARDCOVER_SPINE_TABLE` in `scripts/update_cover_vars.py` (24–84 pp → 0.25" … 751–799 pp → 2.063") |

KDP's spec (kdp.amazon.com help topic G201953020) has **no additive term**;
the `+ 0.06` belongs to Lulu's paperback formula only. Some earlier book
projects' scripts carried it into the KDP branch — verify against KDP's own
cover calculator when in doubt.

> EXAMPLE: a 434-page white-paper KDP paperback → `434 × 0.002252 =
> 0.9774"` spine; full wrap `2 × 6" + 0.9774" + 2 × 0.125" = 13.227"` wide ×
> `9" + 2 × 0.125" = 9.25"` tall.

Spine **text** is only allowed at ≥79 pages (KDP; Lulu ~80), and must stay
≥0.0625" from the spine folds (fold tolerance is ±0.0625"). The cover
template enforces this automatically: `cover-vars.tex` carries an
`\ifCoverSpineText` flag derived from the real page count, so a too-thin
book renders a blank spine rather than an invalid one.

Full wrap-cover anatomy, safe zones, and the render pipeline:
[`COVER-SPEC.md`](COVER-SPEC.md).

---

## 4. Cover upload specs

- **One PDF, one page**: back + spine + front as a single full wrap.
- Dimensions: `(2 × trim width) + spine + (2 × 0.125" bleed)` wide ×
  `trim height + (2 × 0.125")` tall. `make kdp-cover` prints the final
  dimensions and fails the build if they don't match the computed wrap.
- All fonts embedded; raster elements ≥300 DPI; file ≤650 MB.
- Cover finish (matte vs glossy) is chosen in the KDP form, not the file.
  House precedent: matte.
- Lulu hardcover case wrap uses **0.875" bleed** (0.75" board wrap + 0.125");
  `update_cover_vars.py --platform lulu --binding hardcover` handles it.

### CMYK / PDF/X-1a conversion (recommended for predictable print color)

`make kdp-cover` already flattens transparency with Ghostscript `/prepress`.
KDP accepts that RGB PDF and converts it internally; for predictable color,
convert the flattened wrap to CMYK PDF/X-1a:2001 with a SWOP output intent
and upload the converted file:

```bash
# one-time: create a PDF/X output-intent definition (pdfx-def.ps) that
# declares GTS_PDFXVersion (PDF/X-1a:2001) and a CMYK SWOP ICC profile,
# e.g. /usr/share/color/icc/colord/SWOP_TR005_coated_5.icc
gs -dNOSAFER -dPDFX -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -dCompatibilityLevel=1.3 -sColorConversionStrategy=CMYK \
   -sOutputFile=build/kdp-cover-cmyk.pdf pdfx-def.ps build/kdp-cover.pdf
```

Expectations after conversion: transparency flattens to a single CMYK raster
(normal for covers); deepest blacks lift slightly (CMYK cannot reach pure RGB
black) — this matches how KDP actually prints. Verify dimensions again with
`pdfinfo` after converting. *(No Makefile target exists for this step yet;
run the recipe manually.)*

### Barcode and quiet zone

- KDP auto-places an ISBN barcode in the **lower-right of the back cover**
  (nominal 2" × 1.2" zone, ≥0.25" inside the trim edges). On dark covers,
  reserve a **white quiet-zone box** there so the barcode scans.
- Alternatively embed your own EAN-13 (≥300 DPI, **white background**) in that
  zone; KDP detects it and will not overprint. Never do both.
- Lulu always requires you to leave its barcode area clear per its current
  template.

---

## 5. Listing metadata (KDP form, in order)

Work from the generated `docs/publishing/KDP.md` skeleton; the values below
describe the rules, not your book.

| Field | Rule |
|---|---|
| Language | From `book.language`. |
| Title / Subtitle | Must match the title page and copyright page **character for character** (all derive from `book.yaml`). |
| Series / Edition | Series usually blank; edition number from `book.edition_statement`. |
| Author | Real or pen name; split first/last as you want it displayed. |
| Contributors | Human contributors only (translator, illustrator, foreword). **Never list AI tools here** — that's what the AI-content questions are for. |
| Description | ≤4,000 characters *including* HTML. Supported tags only: `<b>`, `<em>`, `<br>`, `<h4>`–`<h6>`, `<ul>`, `<ol>`, `<li>`. Structure that works: bold hook line → 2–3 short narrative paragraphs → `<b>What's inside:</b>` bullet list → who-it's-for line → italic provenance/credibility line. Keep a plain-text variant for Bowker (see [`METADATA-TEMPLATE.md`](METADATA-TEMPLATE.md)). |
| Publishing rights | "I own the copyright…" (note any public-domain source texts in the description/copyright page). |
| Primary audience / sexually explicit | Standard adult content; No. Reading age: leave blank unless children's. |
| Primary marketplace | Amazon.com unless you have a reason otherwise. |
| Categories | Up to 3 in KDP's browse picker. Choose from your BISAC worksheet: one broad for visibility + two niche for ranking. You can request more via KDP Support post-publication. |
| Keywords | **7 slots, ≤50 characters each** (`classification.keywords`). Target reader search phrases; do not repeat words already in the title, subtitle, or category names. Record the character count for each. |
| AI content | See §6. |
| ISBN | "I have my own ISBN" with the Bowker-assigned print ISBN from `identifiers.isbn_print`; or take KDP's free ISBN (then Bowker/PCIP options narrow). Kindle uses an ASIN; the epub ISBN still goes in the EPUB `dc:identifier`. |

Full BISAC/keyword worksheets, PCIP block, and comp research:
[`METADATA-TEMPLATE.md`](METADATA-TEMPLATE.md).

### Accessibility questions (title setup)

Amazon's product-page accessibility panel ("Visual adjustments",
"Nonvisual reading", "Hazards") is driven by the answers you give at
title setup (or ONIX 3.1 for feed publishers) — it does **not** read the
EPUB's own OPF metadata. Answer from what the pipeline actually
guarantees; `make epub-a11y` (Ace by DAISY) must be green before you
claim any of this:

| Question | Answer (this pipeline) |
|---|---|
| Visual adjustments | Yes — reflowable text; font, size, and layout adjustable. |
| Nonvisual reading | Supported — logical reading order, structural navigation, alt text on informative images (`\figalt`). |
| Alt text present | Yes, if `make epub-check` passes (alt-text gate). Keep alt ≤140 characters. |
| Hazards | None (no flashing, motion, or sound content). |
| Conformance | EPUB Accessibility 1.1 — WCAG 2.2 Level AA, self-certified (`a11y:certifiedBy` = publisher from `book.yaml`). |

Don't answer "I don't know" — since the EAA came into force (2025-06-28)
that renders as "accessibility unknown" on EU storefronts.

---

## 6. AI-content disclosure — answer honestly

KDP asks whether the book contains AI-generated **text**, **images**, or
**translations**, and distinguishes:

- **AI-generated** — "content created by an AI-based tool, even if you applied
  substantial edits afterwards."
- **AI-assisted** — "you created the content yourself, and used AI-based tools
  to edit, refine, error-check, or otherwise improve that content."

Policy for books from this template:

1. **Decide from the actual workflow, per content type.** AI-drafted prose
   with heavy human editing is still "AI-generated (text) — with extensive
   editing" under KDP's definition. Human-authored prose that AI edited or
   checked is "AI-assisted" and requires no disclosure. Judge text, cover
   art, interior images, and translations separately. When in doubt, the
   disclosing option is the safe one.
2. **The selection is internal to Amazon** (not shown on the product page),
   and disclosed AI-generated books are permitted. There is no advantage to
   shading the answer.
3. **Mirror the disclosure in the book itself.** Record the per-type answers
   in `book.yaml` (`publishing.ai_disclosure.text/images/translations`, each
   `none | assisted | generated`, plus an optional `detail` note) — they land
   in the generated `KDP.md` dossier ready to transcribe into the Content
   page. The `statement` field prints on the copyright page (and flows into
   the EPUB); the KDP answers, the copyright page, and any Author's Note must
   tell the same story.
4. **US Copyright Office filings must match too.** Unlike KDP's private
   checkbox, USCO *requires* disclosing AI-generated material and limits the
   claim to the human contribution (2023 AI guidance). If you register,
   describe the human authorship consistently with the KDP answer.
5. Algorithmically rendered art (TikZ, matplotlib "cover-as-code") is
   author-created code output, not AI image generation — but art made with a
   generative image model is AI-generated and should be disclosed as such.

---

## 7. Pricing and royalty math

**Paperback royalty = 60% × list price − printing cost** (Amazon marketplaces;
Expanded Distribution pays 40%). List price must clear the printing cost with
margin.

> **Sub-$9.99 cliff (since 2025-06-10):** print books listed under $9.99 USD
> (and the equivalent thresholds in other marketplaces) earn only **50%**.
> If a short book prices near the line, $9.99 usually nets more than $8.99 —
> do the math at both rates before dipping below the threshold.

Printing cost model (US, B&W paperback, ≥110 pages — verify KDP's current
table at upload; KDP shows the exact figure in the pricing form):

```
printing ≈ $0.85 + $0.012 × pages        # B&W
color is roughly 3–5× — check the calculator
```

> EXAMPLE: 260-page B&W paperback at $24.99 list →
> printing ≈ $0.85 + 3.12 = $3.97; royalty ≈ 0.60 × 24.99 − 3.97 ≈ **$11.02**.

**Kindle:** 70% royalty only inside the $2.99–$9.99 band, minus a delivery fee
(~$0.15/MB); 35% outside the band, no delivery fee. A $9.99 ebook frequently
nets *more* than $14.99 — do the math both ways before pricing above the band.

Pricing procedure:

1. Build the comp-title pricing table ([`METADATA-TEMPLATE.md`](METADATA-TEMPLATE.md) §5)
   within ~30 days of launch — Amazon prices move.
2. Position by format: trade paperback typically $16.99–$24.99 depending on
   page count; large/parallel-text formats justify more; hardcover ≈ paperback
   + $10–15.
3. Record the final prices in `book.yaml` (`publishing.price_usd_print`,
   `publishing.price_usd_ebook`) so the dossier stays the source of truth.
4. KDP Select/KU requires ebook *exclusivity* — house precedent: not enrolled.
5. **DRM** — set from `book.yaml` `publishing.kindle_drm` (house precedent:
   off/false). Choose deliberately: since **2026-01-20** buyers can download
   the actual EPUB/PDF of DRM-free Kindle titles from Manage Your Content
   and Devices, and the choice is effectively **permanent per title** — it
   cannot be meaningfully changed after publication. DRM-free is
   reader-friendly and consistent with selling the same EPUB on other
   storefronts; DRM-on trades that away for (weak) copy protection.

---

## 8. Proof order → approval checklist

Before ordering the proof, `make validate-all` must be green and the
[`RELEASE-CHECKLIST.md`](RELEASE-CHECKLIST.md) gates must pass. Then:

- [ ] Upload interior + cover; run KDP's **online previewer** end-to-end
      (every flagged page, spine centering, barcode quiet zone, live-area
      violations).
- [ ] **Order a physical proof.** Never publish from the previewer alone.
- [ ] On the proof: cover color/contrast, spine text centered (±0.0625"
      tolerance), barcode scans with a phone, gutter comfortable at the
      thickest signature, front-matter page sequence, running heads, a
      10+-page random interior spot-check, paper/ink match with intent.
- [ ] Cross-check title page, copyright page (ISBN, edition statement, AI
      disclosure), and cover text against `book.yaml` one final time.
- [ ] Fix → rebuild (`make pdf && make cover-vars && make kdp-cover`) →
      re-proof if the fixes were physical (spine, margins, color); previewer
      alone is acceptable only for pure metadata changes.
- [ ] Approve and publish. Then complete the post-publish checks in
      [`RELEASE-CHECKLIST.md`](RELEASE-CHECKLIST.md).

---

## 9. Timeline expectations

| Step | Typical time |
|---|---|
| KDP file processing + automated checks | minutes–hours |
| Proof print + shipping | ~1 week (expedited options vary) |
| Publish review after approval | 24–72 h (paperback and Kindle reviewed separately) |
| Listing fully live, formats linked | up to a few days after "Live" |
| Look Inside reflects the final files | days–2 weeks after going live |
| A+ Content / Author Central | after publication; A+ review takes days |
| Category adjustments via KDP Support | days |
| Sales-rank/keyword data worth reading | 30–60 days |

Plan launch dates backwards from the proof loop: at least **two weeks** from
"files final" to "confidently live," longer if the proof forces a spine or
color fix.

---

## 10. Sources (verify before each publication — KDP specs drift)

- KDP Help: Paperback Submission Guidelines; Set Trim/Bleed/Margins; Cover
  Guidelines; Book Description, Metadata, and Keywords guidelines; AI-content
  policy (Content Guidelines); Printing cost & royalty calculator.
- Lulu Book Creation Guide (spine tables, hardcover wrap):
  https://help.api.lulu.com/ and https://www.lulu.com/publishing-toolkit
- BISG BISAC subject headings: https://www.bisg.org/complete-bisac-subject-headings-list
- Bowker MyIdentifiers: https://www.myidentifiers.com/
