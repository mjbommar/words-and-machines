# Release Checklist

Gate list for shipping a printing. Nothing uploads to a platform unless every
gate below is green. `make release` automates the mechanical parts: it refuses
to run on a dirty git tree or a failing `make validate-all`, then stages
artifacts into `releases/$(DATE)-$(PRINTING)/` with SHA256SUMS.

---

## 1. Build gates

- [ ] **`make validate-all` green.** This is the master gate: print PDF,
      bleed PDF, ebook PDF, EPUB (epubcheck 0 errors), Ace accessibility
      audit (`make epub-a11y`), KDP cover, preflight (`make preflight`),
      style checks (`make check`), and `make doctor`. No manual override.
- [ ] **`make doctor` clean** — toolchain present, fonts resolve, no
      placeholder values (`TODO`, `[...]`, `XXX`) surviving in `book.yaml`,
      CLAUDE.md target audit passes, cover-vars freshness check passes.
- [ ] **Cover vars fresh against the *final* page count.** The spine width is
      a function of the page count; any interior change can move it. If the
      print PDF was rebuilt after the last `make cover-vars`, rerun
      `make cover-vars && make kdp-cover` (and `make lulu-cover` if shipping
      Lulu). `make doctor` warns on staleness — treat the warning as a
      failure here.
- [ ] Fonts embedded, no Type 3, images ≥300 ppi: `make preflight`
      (interior + KDP cover; `scripts/preflight_pdf.py` for other PDFs).
- [ ] `make stats` run and recorded (word counts become the printing's
      baseline for the next revision round).

## 2. Metadata cross-checks (everything traces to `book.yaml`)

The design intent behind `make doctor`: **a claim printed in the book must be
generated from `book.yaml`, never hand-typed** — so checking the book against
the platform means checking both against `book.yaml`.

- [ ] Copyright page ISBN(s) == `identifiers.*` == Bowker record == KDP form.
- [ ] Title/subtitle/author identical (character for character) across title
      page, copyright page, cover, OPF, and the KDP listing.
- [ ] Edition statement and printing line correct for *this* printing.
- [ ] AI-disclosure text on the copyright page matches the KDP AI-content
      answer ([`KDP-TEMPLATE.md`](KDP-TEMPLATE.md) §6).
- [ ] EPUB `dc:identifier` carries the epub ISBN (not the print ISBN); Kindle
      ASIN is Amazon's concern.
- [ ] If this is a **reprint**: content changes are within KDP's in-place
      update threshold (~10% page-count movement; no new edition claims), so
      the same ISBNs stand. Otherwise it's a new edition → new ISBNs → back
      to [`METADATA-TEMPLATE.md`](METADATA-TEMPLATE.md) §1.

## 3. Proof review

Full procedure in [`KDP-TEMPLATE.md`](KDP-TEMPLATE.md) §8. Minimum points:

- [ ] KDP online previewer pass (spine centering, barcode quiet zone,
      live-area warnings all resolved).
- [ ] Physical proof ordered and inspected: cover color, spine text within
      fold tolerance, barcode scans, gutter, random 10+-page interior check.
- [ ] Physical fixes (spine/margins/color) → new proof. Metadata-only fixes →
      previewer suffices.

## 4. Cut the release

- [ ] `make release` → `releases/<YYYY-MM-DD>-<printing>/`, e.g.
      `releases/2026-06-14-second-printing/`, containing:
  - interior PDF (named for the book slug, `-interior.pdf`)
  - PDF/X-1a interior (`-interior-x1a.pdf`, IngramSpark/Lulu)
  - wrap cover PDF (`-cover.pdf`; per platform if multiple)
  - EPUB
  - ONIX 3.0 feed (`-onix-30.xml`)
  - `SHA256SUMS` over exactly those artifacts
  - `README.md`: edition + printing statement, what changed since the last
    printing, page count, spine width, ISBNs, build date, and which file
    uploads where
- [ ] Verify integrity from a clean shell: `sha256sum -c SHA256SUMS`.
- [ ] Commit the release directory; tag the commit
      (e.g. `printing/2026-06-14`). The uploaded bytes must be reproducible
      from the tag: the Makefile pins `SOURCE_DATE_EPOCH` to the commit and
      the release's `TOOLCHAIN.txt` records the toolchain — rebuilding on
      the pinned CI container must reproduce `SHA256SUMS` exactly.
- [ ] Upload to platform(s) **from the release directory**, not from
      `build/` — what shipped is what was checksummed.
- [ ] Batch publishing: KDP caps new titles at **3 per day** per account
      (exceptions by request) — plan multi-edition/multi-format launches
      accordingly.

## 5. Post-publish verification (after "Live")

- [ ] Buy-page metadata: title, subtitle, author, price, page count, pub
      date, formats linked to one listing.
- [ ] **Look Inside** shows the final interior (allow days–2 weeks to
      refresh; verify the copyright page and ISBN shown are this printing's).
- [ ] Kindle sample downloads and renders: TOC works, cover shows, first
      chapters clean on phone + tablet + e-ink previews.
- [ ] Order one retail copy of the paperback (not a proof) and spot-check —
      retail and proof runs can differ.
- [ ] Store metadata propagation: categories appear as chosen; search for
      each of the 7 keywords + title; Author Central page linked.
- [ ] Bowker record updated to "published" with final price/date; PCIP data
      matches the shipped copyright page.
- [ ] Record the printing in the project log/TODO with the release path and
      live date; note keyword/category review due date (+30–60 days).
