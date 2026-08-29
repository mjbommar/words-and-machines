# Roadmap

Phases execute in order; each has an acceptance gate. Status: `[ ]` pending, `[x]` done.

## Phase 0 — Repo hygiene
- [x] Research reports for all 15 source projects (`docs/research/`)
- [x] `.gitignore` (LaTeX aux, `build/`, `latex/generated/`, `__pycache__`, `.texlive-cache`, EPUB output)
- [x] `README.md` (quickstart: instantiate → configure → build)
- [x] LICENSE decision (template code MIT; book content all-rights-reserved note)
- [x] Rename branch to `main`; first commit = docs + skeleton

**Gate:** clean `git status` after a full build (no artifacts tracked).

## Phase 1 — Config system
- [x] `book.yaml` schema: identity (title/subtitle/author/publisher/year), ISBNs per format, description, BISAC, keywords, trim + margins profile, font profile, citation style, editions, AI-disclosure text, price notes
- [x] `scripts/generate_metadata.py`: emits `latex/generated/metadata.tex` (all `\BookTitle`-style macros), validates against JSON Schema, **fails on `TODO`/placeholder values** unless `--allow-placeholders` (used by template CI)
- [x] `docs/architecture/config-schema.md` documenting every field

**Gate:** `uv run scripts/generate_metadata.py` produces valid metadata.tex; placeholder detection demonstrably fails.

## Phase 2 — LaTeX print/PDF pipeline
- [x] `latex/preamble/` modules: `main` (loader, documented order), `packages`, `fonts` (3 profiles, engine-conditional), `geometry` (trim presets 6×9 / 7×10 / 5.5×8.5 / 5×8, KDP-safe margins + gutter, bleed variants), `colors` (4-layer system), `styling` (chapter/section titles, fancyhdr per-matter styles, widow/orphan discipline, `\enable/\disablecleardoublepage`), `boxes` (semantic tcolorbox family with `importance=` keyval), `code` (listings + catcode-hash fix, per-language styles, print-safe wrapping), `verse` (optional paracol parallel-text module), `commands` (semantic inline macros ↔ EPUB CSS classes), `hyperref-last`
- [x] `latex/main.tex` with mode flags, front/main/back matter structure
- [x] `latex/frontmatter/`: halftitle, titlepage (from metadata macros), copyright w/ PCIP + AI-disclosure slot, and book-specific preface
- [x] `latex/backmatter/`: acknowledgments, about-the-author, colophon
- [x] `bib/references.bib` + house biblatex block (authoryear default; superscript-endnote preset selectable)
- [x] Sample chapters (3) exercising every environment: boxes, code, figures, tables, verse, citations, footnotes, cross-refs
- [x] Makefile targets: `pdf quick bleed ebook grayscale draft watch clean` — latexmk, out-of-tree `build/`

**Gate:** `make pdf bleed ebook` all succeed on sample content; PDFs open with correct trim; no aux files outside `build/`.

## Phase 3 — Cover system
- [x] `scripts/update_cover_vars.py`: pdfinfo page count → spine width (KDP white/cream formulas, Lulu paperback formula, Lulu hardcover lookup) → `latex/generated/cover-vars.tex`
- [x] `latex/cover/cover.tex`: one TikZ wrap template, `\ifdefined` switches for KDP/Lulu-paperback/Lulu-hardcover, front/spine/back layout from metadata macros
- [x] Front-cover raster export for EPUB (`make cover-image`), Ghostscript `/prepress` flatten
- [x] Makefile: `cover-vars kdp-cover lulu-cover cover-image` + dimension-check gate

**Gate:** `make kdp-cover` produces a correctly-dimensioned wrap PDF for the sample book's page count.

## Phase 4 — EPUB pipeline
- [x] `epub/converter/` package: TexSoup-based core, decorator-registered handlers (headings, semantic macros, boxes→`<aside>`, code, figures, tables, footnotes→endnotes, citations), `generators.py` (container/OPF/nav/front-matter from book.yaml + chapter structure)
- [x] CSS: house stylesheet (dark-mode safe, Kindle-safe subset — no flexbox/rgba), code-block overflow handling, box classes matching LaTeX environments
- [x] Accessibility metadata (schema.org block in generated OPF)
- [ ] Font embedding to match print profile — deferred; system-font CSS ships (TODO recorded in `epub/css/epub.css` header)
- [x] `make epub epub-check` — epubcheck 0-error gate + handler-coverage audit (unknown-command report)

**Gate:** `make epub` on sample book passes epubcheck with 0 errors, 0 warnings tolerated except known-benign list documented in `docs/architecture/epub-pipeline.md`.

## Phase 5 — Guides, AI workflow, publishing docs
- [x] `docs/guides/STYLE.md` (voice, quantified sentence targets, banned-word list), `STYLE-CRAFT.md` (burstiness, Kidder model, before/after), `STYLE-AI-TELLS.md` (rule-per-tell catalog — synthesized best-of from htsd/wiki/RFC/the-last-book), `SPIRIT-template.md`, `CODE-STYLE.md` (72-char code, line-breaking recipes), `WRITING-PROCESS.md` (7-phase), `REVIEW-QA.md` (review rounds, persona panels, counters), `CITATIONS.md` (claim classification, verify-before-cite, `verified=` bib fields), `RESEARCH.md` (per-chapter research folder contract)
- [x] `docs/publishing/`: `KDP-TEMPLATE.md` runbook (specs, spine math, CMYK recipe, listing metadata, proof checklist), `METADATA-TEMPLATE.md` (Bowker/PCIP dossier), `RELEASE-CHECKLIST.md`, `COVER-SPEC.md`
- [x] `CLAUDE.md` (canonical AI instructions; AGENTS.md → one-line pointer), `.claude/agents/` phased library (~12 curated from the 27-agent sets: researcher, outliner, drafter, content-editor, copy-editor, style-enforcer, fact-checker, citation-verifier, persona reviewers ×3, synthesizer)
- [x] QA scripts: `check_style.py`, `check_prose.py`, `book_stats.py`, `verify_citation.py`, `sample_text.py` (all PEP 723)

**Gate:** `make check` runs all checkers green on sample content; every Makefile target referenced in CLAUDE.md exists (checked by `make doctor`).

## Phase 6 — Init, CI, end-to-end
- [x] `scripts/init_book.py`: interactive/flagged personalization (slug, title, author…) → rewrites book.yaml, README, resets sample chapters (`--keep-samples` option), git-clean result
- [x] `.github/workflows/build.yml`: build PDF + EPUB + checks on push (TeX Live container), artifact upload
- [x] `make validate-all` meta-target; `make doctor` (toolchain + doc/build drift audit)
- [x] README quickstart verified by following it verbatim in a scratch dir
- [x] Commit history clean; push `main` to origin

**Gate (project complete):** in a scratch clone, `init_book.py` → `make validate-all` passes: print/bleed/ebook PDFs, EPUB (epubcheck 0), cover with computed spine, all checkers green, no tracked build artifacts.

---

## Phase 7 — 2026 platform & standards refresh

Added 2026-07-07 from a web-research review of KDP/Lulu specs, the European
Accessibility Act, EPUB accessibility tooling, and POD preflight practice.
Verified current before adding: the KDP paperback spine constants (white
0.002252"/page, cream 0.0025"/page) and the converter's existing schema.org
accessibility block, `epub:type`↔ARIA role pairing, and `xml:lang` emission.
Phases 7 → 8 → 9 are ordered by impact; items within a phase are independent.

- [x] **EPUB accessibility conformance claim + Ace gate** — EAA in force
      since 2025-06-28; target is EPUB Accessibility 1.1 + WCAG 2.2 Level AA
  - `epub/converter/generators.py`: add `dcterms:conformsTo` =
    `EPUB Accessibility 1.1 - WCAG 2.2 Level AA` and `a11y:certifiedBy`
    (publisher/author from `book.yaml`) to the existing schema.org block;
    keep the feature list derived from what the converter actually emits
  - new `make epub-a11y`: run Ace by DAISY (`@daisy/ace` ≥ 1.4.6; Node +
    headless Chromium); exit code alone is not a gate — parse `report.json`
    and fail on any serious/critical violation; wire into `validate-all`;
    `make doctor` reports whether ace is installed
  - alt text: add an explicit alt argument to the authoring contract's
    figure environment (none today — the converter falls back to caption
    text); fail `make epub` when an informative image lacks alt;
    decorative images get `alt=""` + `role="presentation"`; keep alt
    ≤ ~140 chars (KDP guidance)
  - mirror the accessibility answers in `docs/publishing/KDP-TEMPLATE.md` —
    Amazon's product-page display reads title-setup/ONIX 3.1, not the OPF
- [x] **Print-PDF preflight gates: font embedding + image DPI**
  - new `scripts/preflight_pdf.py` (PEP 723, poppler): `pdffonts` — every
    font `emb=yes` and zero Type 3 rows (the classic LuaLaTeX/TikZ/listings
    failure); `pdfimages -list` — every image ≥ 300 x/y-ppi, with a
    whitelist flag for intentional exceptions
  - run on interior and cover PDFs; new `make preflight` wired into
    `validate-all`; referenced from `docs/publishing/RELEASE-CHECKLIST.md`
- [x] **Kindle DRM flag + KDP pricing/policy notes**
  - `book.yaml` + config schema: explicit `publishing.kindle_drm` — since
    2026-01-20 buyers can download the EPUB/PDF of DRM-free Kindle titles,
    and the choice is effectively per-title permanent; surface the tradeoff
    in `KDP-TEMPLATE.md` (replaces the bare "DRM — house precedent: off")
  - runbook pricing note: print royalty dropped 60% → 50% for list prices
    under $9.99 (2025-06-10) — flag the cliff next to `price_usd_print`
  - note the 3-new-titles/day publishing cap; drop transparency-code
    references if any remain (retired ~2025-11)
- [x] **Structured AI disclosure matching KDP's questionnaire**
  - restructure `publishing.ai_disclosure` from one prose blob to KDP's
    actual form: per content type (text / images / translations) ×
    AI-generated vs AI-assisted (assisted = no disclosure required;
    generated = disclosure even after substantial edits)
  - `generate_metadata.py` renders the Content-page answers into the KDP
    runbook artifacts; keep a human-readable summary for the copyright page
- [x] **Spine/cover math coverage + page-count gates**
  - `scripts/update_cover_vars.py`: add KDP premium color (0.002347"/page)
    and standard color (0.002252"/page) paper types, selectable via
    `trim.paper`; keep the no-+constant-for-KDP regression comment
  - gates: fail when the cover carries spine text and the interior is
    under 79 pages (KDP minimum); enforce the KDP hardcover range
    75–550 pages when `formats.hardcover` is on

**Gate:** `make validate-all` additionally passes `epub-a11y` (0
serious/critical Ace violations) and `preflight` (all fonts embedded, no
Type 3, images ≥ 300 ppi); `generate_metadata.py` round-trips the DRM flag
and structured AI disclosure into the KDP runbook artifacts.

## Phase 8 — Distribution beyond KDP

- [x] **PDF/X-1a derivative target + cover ink gate** (`make pdfx`) —
      IngramSpark hard-requires PDF/X-1a:2001 or X-3:2002; Lulu recommends it
  - Ghostscript re-distill of the print PDF (`-dPDFX`, `PDFX_def.ps` with a
    SWOP OutputIntent, `-dPDFXCompatibilityPolicy=1`,
    `-sColorConversionStrategy=CMYK`); verify `/GTS_PDFX` + OutputIntent
    post-hoc (veraPDF validates PDF/A and PDF/UA, not PDF/X)
  - KDP keeps the untouched LuaLaTeX PDF; IngramSpark covers must come from
    Ingram's per-ISBN template generator, not the KDP spine formula —
    document in `COVER-SPEC.md`
  - cover ink-coverage (TAC) gate: `gs -sDEVICE=inkcov` on CMYK cover
    output; fail above the vendor limit (default 240%, a named constant
    beside the spine formulas)
- [x] **ONIX 3.1 export** (`make onix`) — shipped as ONIX 3.0 (widest
      tooling support; 3.1 is a superset direction, upgrade when a
      channel demands it)
  - template (Jinja2 or lxml) from `book.yaml` → ONIX 3.0/3.1 message
    including List 196 accessibility codes; validate with
    `uv run onixcheck`; land it in the release folder
  - context: Amazon accepts ONIX 3.0/3.1 for Kindle since 2025-04, and ONIX
    is the only supply-chain channel for EAA accessibility metadata

**Gate:** `make pdfx onix` produce a `/GTS_PDFX`-stamped interior and an
onixcheck-valid ONIX message, both packaged by `make release`.

## Phase 9 — Release hardening + optional lanes

- [x] **Citation archiving** — `verify_citation.py --archive`
  - Wayback SPN2 via the `savepagenow` lib: CDX lookup for an existing
    snapshot first, `if_not_archived_within` dedupe, ~6 req/min
    authenticated throttle, creds via env vars
  - write `archived = {snapshot URL}` beside `verified =` in
    `references.bib`; `--strict` requires both on every url entry;
    document in `docs/guides/CITATIONS.md` (a prior book measured 57% URL
    rot — verification without archiving doesn't survive publication)
- [x] **Reproducible release builds**
  - Makefile sets `SOURCE_DATE_EPOCH` from the git commit date (LuaTeX
    honors it); pin CI and docs to a dated `texlive/texlive` image tag;
    record toolchain versions in the release folder beside SHA256SUMS
  - Tectonic ruled out: upstream stalled, XeTeX-only
- [x] **Narration export** (`make narration-export`, optional)
  - per-chapter plain text stripped of LaTeX artifacts, suitable for
    AI-narration pipelines; document channel economics in
    `docs/publishing/`: Google Play auto-narration (52%, audio files
    downloadable and portable), KDP Virtual Voice (40%, Amazon-locked),
    ElevenLabs + Findaway (premium, everywhere except Audible)

**Gate:** two cold `make release` runs under the pinned toolchain produce
byte-identical SHA256SUMS; every url bib entry carries `verified =` and
`archived =`; narration export round-trips a sample chapter with no LaTeX
markup remaining.

---

## Completion record — Phases 7–9 (2026-07-07)

All ten items implemented and verified on this machine:
- `make validate-all` green end-to-end with the new gates wired in:
  `epub-a11y` (Ace 1.4.6, **0 violations of any severity** — fixing the
  claim surfaced real template defects: link-only-by-color citations,
  4.47:1 callout-title contrast, deprecated `doc-endnote` role),
  `preflight` (fonts/DPI; negative-tested with a 30-ppi fixture),
  `cover-ink` (found the sample cover at 274% TAC from RGB→CMYK
  conversion; `cover-field` now ink-safe CMYK at 230%).
- `make pdfx` produces a `/GTS_PDFX`-stamped PDF/X-1a:2001 interior
  (annotations dropped, CGATS TR 001 OutputIntent, gate refuses
  Ghostscript's silent revert-to-plain-PDF); `make onix` emits an
  onixcheck-valid ONIX 3.0 message — List 196 codes hand-verified
  against ns.editeur.org (onixcheck checks structure, not code values).
- Reproducibility verified locally: `make pdf` and `make epub` twice →
  identical SHA256 (SOURCE_DATE_EPOCH from the last commit). Pending
  external verification: a full `make release` rebuild inside the
  pinned `TL2025-historic` container (CI config updated but not yet
  exercised), and `make release` itself still — by design — refuses
  the sample ISBNs.
- Sample bib fully `verified =` + `archived =` stamped (3 Wayback
  snapshots; SPN undated-URL responses are detected and retried).
- Spine formulas extended (premium/standard color), spine text now
  page-count-gated via `\ifCoverSpineText`, KDP hardcover 75–550 gate
  in doctor; DRM + structured AI disclosure round-trip from book.yaml
  into the generated KDP dossier.

## Completion record — Phases 0–6 (2026-07-06)

All gates verified on this machine:
- `make validate-all` cold-passes: print (6×9 exact), bleed (6.25×9.25 exact),
  ebook, EPUB (epubcheck 0 fatals/errors/warnings/infos), KDP wrap cover with
  dimension gate, style/prose/doctor green.
- Scratch-clone test: `init_book.py --fresh` → placeholder gate blocks the build
  until the description is written → fresh book builds PDF + EPUB + cover with
  its own metadata and **no template leakage in the OPF**.
- Deferred as documented (not blocking): EPUB font embedding (TODO in
  epub/css/epub.css header), `kdp-cover-cmyk` make target (manual Ghostscript
  recipe in docs/publishing/KDP-TEMPLATE.md), ISBN barcode script (KDP/Lulu
  auto-generate; quiet zone reserved on the cover).
