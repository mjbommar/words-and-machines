# Build System

`make structure` is the fast manuscript-navigation gate. It validates the
four-part chapter order, heading depth and title limits, chapter endings, and
the glossary-to-index routing contract before a PDF or EPUB build.

## Makefile variables
```make
EDITION ?= full          # key into book.yaml editions
ENGINE  ?= (from book.yaml via generate_metadata.py --print-engine)
BUILD   := build
```

## Target graph
```
generated: latex/generated/metadata.tex latex/generated/edition.tex   (from book.yaml)
pdf:        generated → latexmk main.tex (jobname book-print)
quick:      pdf with -interaction=batchmode, single pass, no bib refresh
bleed:      generated → pretex \BleedMode → book-bleed.pdf
ebook:      generated → pretex \EbookMode → book-ebook.pdf
grayscale:  generated → pretex \GrayscaleMode → book-grayscale.pdf
draft:      generated → pretex \DraftMode → book-draft.pdf
cover-vars: pdf → update_cover_vars.py → latex/generated/cover-vars.tex
kdp-cover:  cover-vars → cover.tex (\KDPCover) → gs /prepress flatten → dim check
lulu-cover: cover-vars → cover.tex (\LuluPaperback / \LuluHardcover)
cover-image: cover front panel → PNG (2560×1600-safe for Kindle)
epub:       generated → build_epub.py --edition $(EDITION) → epubcheck
epub-check: epub with strict coverage audit
epub-a11y:  epub → check_epub_a11y.py (Ace by DAISY; fails on
            serious/critical violations — backs the OPF's
            "EPUB Accessibility 1.1 - WCAG 2.2 Level AA" claim)
check:      check_style.py + check_prose.py on latex/chapters/
preflight:  pdf + kdp-cover → preflight_pdf.py (pdffonts: everything
            embedded, no Type 3; pdfimages: >=300 ppi, --allow exempts)
cover-ink:  kdp-cover → check_ink_coverage.py (per-pixel C+M+Y+K <= 240%
            via gs tiffsep; KDP/SWOP total-area-coverage cap)
pdfx:       pdf → export_pdfx.py (Ghostscript -dPDFX re-distill to
            PDF/X-1a:2001, CMYK, annotations dropped, OutputIntent
            verified) → preflight on the result. IngramSpark/Lulu
            uploads; KDP keeps the plain `pdf` output
onix:       export_onix.py → build/onix/onix-30.xml (one Product per
            enabled format incl. List 196 accessibility codes;
            onixcheck-validated — structure only, codes hand-verified)
narration-export: epub → export_narration.py → build/narration/*.txt
            (per-chapter plain text for AI narration; see
            docs/publishing/NARRATION.md for channel economics)
verify-citations: verify_citation.py --require-stamps --require-archives
            (network; gates release. `--archive` pins each cited URL in
            the Wayback Machine and writes archived= into the bib)
stats:      book_stats.py (word counts, per-chapter, delta vs last run)
vocab:      vocab_variety.py (OpenGloss v1.3 knowledge graph: overused
            words vs Wikipedia base rates; synonym/antonym/hypernym
            ideation with per-sense definitions (--senses), usage
            examples and collocation-fit marks on fresh picks,
            --max-register reading-level cap, --suggest-bans style-
            profile candidates, optional OGBert --embed context
            re-ranking (GPU); cache v2 ~120 MB in ~/.cache/opengloss/;
            advisory, never a gate)
prose-report: prose_report.py (orchestrates metrics + slop + vocab into
            one markdown report with deltas vs the previous run, stored in
            build/prose-report-state.json; --pangram adds detector
            fractions, --deslop N appends a voice-model fix brief;
            advisory)
metrics:    prose_metrics.py (per-chapter burstiness cv, MTLD/MATTR
            lexical diversity, compression ratio, adverb density,
            paragraph uniformity, specificity; thresholds overridable
            per style profile; compares against the house percentile
            baseline scripts/data/prose-baseline.json — regenerate with
            --write-baseline across edited books; advisory)
slop:       slop_audit.py (quantitative slop signals at file/section/
            paragraph/sentence level + optional 54-tell LLM judge via
            pydantic-ai, --llm --unit ... --sample ...; needs
            ANTHROPIC_API_KEY or OPENAI_API_KEY for --llm; advisory)
pangram:    pangram_check.py (Pangram 4 detector cross-check: fraction
            AI / AI-assisted / human + humanizer_max per chapter or
            paragraph with flagged windows; sends model=pangram-4
            (PANGRAM_MODEL overrides; v3 deprecates 2026-09-30) and keys
            the result cache by model version; sampling via
            --n/--pct/--limit; --api auto picks realtime for <= 10 units
            and the bulk queue above that, --resume finishes a timed-out
            bulk; needs PANGRAM_API_KEY, cost estimate printed before
            sending; advisory. NOTE fraction_ai is a hard-label average
            and saturates to 0/1 on single paragraphs — rank on
            windows[].ai_assistance_score instead, as deslop.py does)
(no target)  phrase_check.py (provenance: samples n-word spans from the
            book and counts them in Ai2's infini-gram index — long spans
            with LOW nonzero counts are the review signal; --phrase looks
            up one string. Free public API, no key; serial with --delay
            by design, concurrency gets the IP 403'd. Guide:
            docs/guides/PROVENANCE.md)
doctor:     toolchain presence, font resolution, CLAUDE.md target audit,
            cover-vars freshness, placeholder scan
validate-all: pdf bleed ebook epub epub-a11y kdp-cover preflight cover-ink
              check doctor
release:    validate-all + pdfx + onix + verify-citations + metadata --strict
            → releases/$(DATE)-$(PRINTING)/ (slugged artifacts, README, SHA256SUMS)
watch:      latexmk -pvc quick loop
clean:      rm -rf build latex/generated/*
```

## Conventions
- **Reproducible builds:** the Makefile exports `SOURCE_DATE_EPOCH` from the
  last commit's timestamp; LuaTeX, Ghostscript, and the EPUB packager all
  honor it, so two builds of the same tree are byte-identical (verified on
  `make pdf` and `make epub`). CI pins `texlive/texlive:TL2025-historic` —
  the frozen toolchain that makes SHA256SUMS reproducible across machines;
  each release carries a `TOOLCHAIN.txt` recording versions + rebuild recipe.
  (Tectonic was evaluated and rejected: upstream stalled, XeTeX-only.)
- ANSI-colored `@echo` status lines (house style from hacking/vibe Makefiles)
- Every artifact lands under `build/`; `latex/generated/` holds only generated .tex
- `release` refuses to run on a dirty git tree or failing `validate-all`
- CI (`.github/workflows/build.yml`) runs `validate-all`; the template ships placeholder-free sample metadata so CI is strict from day one. `make release` additionally requires real ISBNs (`generate_metadata.py --strict`)
