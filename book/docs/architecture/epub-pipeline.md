# EPUB Pipeline

## Flow
```
book.yaml ─► generate_metadata.py ─► build/epub-metadata.json
latex/chapters/*.tex (edition-filtered) ─► converter core ─► XHTML per chapter
frontmatter (generated, not parsed) + nav + OPF ─► package ─► build/epub/<slug>.epub ─► epubcheck
```

## Converter design (`epub/converter/`)
- **core.py** — TexSoup parse of each chapter; walks nodes; dispatches to handlers; unknown command/environment → recorded in coverage report (build fails in `epub-check` mode, warns in `epub` mode)
- **handlers/** — decorator-registered:
  - `structure.py` — chapter/section/scenebreak/labels
  - `inline.py` — semantic macros → class-mapped spans (authoring contract table)
  - `blocks.py` — quotation/attribution, callout family → `<aside class="callout callout-warning" role="note">` with title heading
  - `code.py` — codelisting → `<pre><code class="language-...">`, HTML-escaped, no highlighting markup (CSS-only theming)
  - `media.py` — figures (convert PDF figures → PNG via pdftoppm at build), tables (booktabs → plain table classes)
  - `notes.py` — footnotes → chapter endnotes with backlinks (`epub:type="footnote"` + noteref)
  - `citations.py` — resolves keys against the .bib (authoryear inline or superscript noterefs; bibliography page generated)
- **generators.py** — mimetype, container.xml, `content.opf` (dcterms, ISBN from metadata json, schema.org accessibility metadata, cover-image item), `nav.xhtml` (+ NCX for legacy), titlepage/copyright XHTML from metadata — **no static templates containing book strings**
- **package** — zip with mimetype first & uncompressed (datacenter's `package_epub.py` fix)

## CSS (`epub/css/epub.css`)
- Kindle-safe subset: no flexbox, no rgba(), no CSS variables; `em`/`%` units only
- Dark-mode safety: `color: inherit` defaults, borders via `currentColor`, no hard-coded near-black text on transparent (htsd/legal-tech night-mode findings)
- `pre { overflow-x: auto; white-space: pre-wrap }` for code on narrow screens
- Callout classes mirror LaTeX box names 1:1; small-caps via `font-variant` with fallback letter-spacing (no fake `<span>` uppercasing)

## Fonts
Embed the book's font profile OTFs (obfuscation off, license-permitting — all three profiles are OFL). `epub/fonts/` populated at build time from system fonts; `make doctor` verifies availability.

## Gates
1. `epubcheck` — 0 errors, 0 warnings (documented allowlist only)
2. Handler coverage — no unknown commands
3. Internal link check — every noteref/backlink/toc target resolves
4. Alt-text check — every informative figure carries `\figalt` or a
   caption to derive alt from (`\figalt{}` = decorative); a figure with
   neither fails `--strict`, because of gate 5's conformance claim
5. `make epub-a11y` — Ace by DAISY via `scripts/check_epub_a11y.py`;
   0 serious/critical violations. The OPF claims
   `EPUB Accessibility 1.1 - WCAG 2.2 Level AA` (`dcterms:conformsTo`,
   with `a11y:certifiedBy` from book.yaml's publisher/author —
   self-certification is allowed by the spec), which the EAA has made
   commercially necessary in the EU since 2025-06-28. Amazon's
   storefront accessibility panel reads title-setup/ONIX answers, not
   this OPF block — mirror the answers per KDP-TEMPLATE.md §Accessibility
