# ============================================================
# Book build system. See docs/architecture/build-system.md.
#
#   make pdf            print interior        make epub        EPUB + epubcheck
#   make bleed          POD wrap interior     make kdp-cover   wrap cover (KDP)
#   make ebook          digital PDF           make check       style/prose gates
#   make validate-all   everything            make release     stamped artifacts
#
# EDITION=name selects a book.yaml edition (default: the default: true one).
# PLATFORM=kdp|lulu BINDING=paperback|hardcover control cover targets.
# ============================================================

EDITION  ?=
PLATFORM ?= kdp
BINDING  ?= paperback

ROOT   := $(CURDIR)
BUILD  := $(ROOT)/build
UV     := uv run
SBE_UV := uv run --group sbe
COMPOSE_UV := uv run --group compose
SBE_BUILD_UV := uv run --group sbe-build
ENGINE := $(shell $(UV) scripts/generate_metadata.py --print-engine 2>/dev/null || echo lualatex)

# Reproducible builds: LuaTeX, Ghostscript, and the EPUB packager all
# honor SOURCE_DATE_EPOCH. Pinning it to the last commit's timestamp
# makes two builds of the same tree byte-identical
# (reproducible-builds.org/docs/source-date-epoch/). Override:
#   make pdf SOURCE_DATE_EPOCH=...
export SOURCE_DATE_EPOCH ?= $(shell git log -1 --format=%ct 2>/dev/null || date +%s)

EDITION_FLAG := $(if $(EDITION),--edition $(EDITION),)
JOB_SUFFIX   := $(if $(EDITION),-$(EDITION),)

LATEXMK = latexmk -$(ENGINE) -interaction=nonstopmode -halt-on-error \
          -output-directory=$(BUILD)/latex -cd

# ANSI status helpers (house style)
GREEN  := \033[0;32m
YELLOW := \033[1;33m
NC     := \033[0m
define say
	@printf '$(GREEN)==> %s$(NC)\n' $(1)
endef

.PHONY: generated figures pdf quick bleed ebook grayscale draft cover-vars \
        kdp-cover lulu-cover cover-image epub epub-check epub-a11y check \
        preflight cover-ink pdfx onix narration-export stats vocab metrics \
        prose-report \
        lengths \
        slop pangram verify-citations doctor validate-all release watch \
        ontology craft brief \
        simplified simplified-lexicon test-simplified calibrate-simplified \
        test-compose \
        clean help

help: ## list targets
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-14s %s\n", $$1, $$2}'

# ---------------- metadata ----------------
generated: ## regenerate latex/generated/ + build/epub-metadata.json from book.yaml
	$(call say,"generating metadata (edition: $(if $(EDITION),$(EDITION),default))")
	@$(UV) scripts/generate_metadata.py $(EDITION_FLAG)

# ---------------- figures ----------------
figures: ## compile latex/figures/src/*.tikz -> figure PDFs (GRAYSCALE=1, PNG=1)
	@$(UV) scripts/build_figures.py \
	  $(if $(GRAYSCALE),--grayscale,) $(if $(PNG),--png,)
	$(call say,"figures built from latex/figures/src/")

# ---------------- interiors ----------------
pdf: generated ## print interior PDF (trim size, black links)
	$(LATEXMK) -jobname=book-print$(JOB_SUFFIX) latex/main.tex
	$(call say,"build/latex/book-print$(JOB_SUFFIX).pdf")

quick: generated ## fast single-pass draft compile
	cd latex && $(ENGINE) -interaction=batchmode -output-directory=$(BUILD)/latex \
	  -jobname=book-quick main.tex || (tail -30 $(BUILD)/latex/book-quick.log; exit 1)
	$(call say,"build/latex/book-quick.pdf (single pass; refs may be stale)")

bleed: generated ## interior with bleed (POD full-bleed art)
	$(LATEXMK) -usepretex='\def\BleedMode{1}' -jobname=book-bleed$(JOB_SUFFIX) latex/main.tex
	$(call say,"build/latex/book-bleed$(JOB_SUFFIX).pdf")

ebook: generated ## digital PDF (colored links, symmetric margins)
	$(LATEXMK) -usepretex='\def\EbookMode{1}' -jobname=book-ebook$(JOB_SUFFIX) latex/main.tex
	$(call say,"build/latex/book-ebook$(JOB_SUFFIX).pdf")

grayscale: generated ## B&W-safe interior for standard POD ink
	$(LATEXMK) -usepretex='\def\GrayscaleMode{1}' -jobname=book-grayscale$(JOB_SUFFIX) latex/main.tex
	$(call say,"build/latex/book-grayscale$(JOB_SUFFIX).pdf")

draft: generated ## watermarked draft PDF
	$(LATEXMK) -usepretex='\def\DraftMode{1}' -jobname=book-draft$(JOB_SUFFIX) latex/main.tex
	$(call say,"build/latex/book-draft$(JOB_SUFFIX).pdf")

# ---------------- covers ----------------
cover-vars: ## compute spine/wrap dims from built interior (PLATFORM, BINDING)
	@$(UV) scripts/update_cover_vars.py --platform $(PLATFORM) --binding $(BINDING) \
	  --pdf $(BUILD)/latex/book-print$(JOB_SUFFIX).pdf

# Depends on cover-vars.tex so switching PLATFORM/BINDING re-renders
# (cover-vars always rewrites the file, bumping its timestamp).
$(BUILD)/cover/cover.pdf: latex/cover/cover.tex latex/generated/cover-vars.tex \
                          latex/generated/metadata.tex
	mkdir -p $(BUILD)/cover
	cd latex && lualatex -interaction=nonstopmode -output-directory=$(BUILD)/cover cover/cover.tex
	cd latex && lualatex -interaction=nonstopmode -output-directory=$(BUILD)/cover cover/cover.tex

kdp-cover: PLATFORM=kdp
kdp-cover: cover-vars $(BUILD)/cover/cover.pdf ## KDP wrap cover, flattened
	gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress \
	  -sOutputFile=$(BUILD)/cover/cover-kdp.pdf $(BUILD)/cover/cover.pdf
	@$(UV) scripts/check_cover_dims.py --pdf $(BUILD)/cover/cover-kdp.pdf
	$(call say,"build/cover/cover-kdp.pdf")

lulu-cover: PLATFORM=lulu
lulu-cover: cover-vars $(BUILD)/cover/cover.pdf ## Lulu wrap cover (BINDING=paperback|hardcover)
	gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress \
	  -sOutputFile=$(BUILD)/cover/cover-lulu-$(BINDING).pdf $(BUILD)/cover/cover.pdf
	@$(UV) scripts/check_cover_dims.py --pdf $(BUILD)/cover/cover-lulu-$(BINDING).pdf
	$(call say,"build/cover/cover-lulu-$(BINDING).pdf")

cover-image: cover-vars $(BUILD)/cover/cover.pdf ## EPUB PNG + KDP-listing JPEG (1600x2560)
	@$(UV) scripts/export_cover_image.py --pdf $(BUILD)/cover/cover.pdf \
	  --out $(BUILD)/cover/cover-front.png \
	  --kindle-out $(BUILD)/cover/cover-kindle.jpg
	$(call say,"build/cover/cover-front.png + cover-kindle.jpg")

# ---------------- EPUB ----------------
epub: generated cover-image ## build EPUB 3 and run epubcheck
	@$(UV) scripts/build_epub.py $(EDITION_FLAG) --cover $(BUILD)/cover/cover-front.png
	epubcheck $(BUILD)/epub/book$(JOB_SUFFIX).epub
	$(call say,"build/epub/book$(JOB_SUFFIX).epub (epubcheck passed)")

epub-check: generated cover-image ## EPUB with strict handler-coverage audit
	@$(UV) scripts/build_epub.py $(EDITION_FLAG) --cover $(BUILD)/cover/cover-front.png --strict
	epubcheck $(BUILD)/epub/book$(JOB_SUFFIX).epub

epub-a11y: epub ## Ace by DAISY audit (fails on serious/critical)
	@$(UV) scripts/check_epub_a11y.py --epub $(BUILD)/epub/book$(JOB_SUFFIX).epub
	$(call say,"build/a11y-report/report.html (Ace passed)")

# ---------------- QA ----------------
check: ## style + prose gates on chapters
	@$(UV) scripts/check_style.py
	@$(UV) scripts/check_prose.py

simplified: ## Simplified Book English vocabulary report (advisory; docs/guides/SIMPLIFIED-ENGLISH.md)
	@$(SBE_UV) scripts/check_simplified.py

simplified-lexicon: ## rebuild scripts/data/simplified_english/lexicon.json from the corpora
	@$(SBE_BUILD_UV) scripts/build_simplified_lexicon.py

test-simplified: ## SBE checker regression tests
	@$(SBE_UV) python -m unittest discover -s tests -p 'test_*simplified.py' -v
	@$(SBE_UV) python -m unittest tests.test_latex_source -v

test-compose: ## outline composer regression tests
	@$(COMPOSE_UV) python -m unittest tests.test_outline_composer -v

calibrate-simplified: ## score the nine held-out sibling book projects
	@$(SBE_UV) scripts/calibrate_simplified.py

preflight: pdf kdp-cover ## font embedding + image DPI gates (poppler)
	@$(UV) scripts/preflight_pdf.py $(BUILD)/latex/book-print$(JOB_SUFFIX).pdf \
	  $(BUILD)/cover/cover-kdp.pdf
	$(call say,"preflight passed (fonts embedded / no Type 3 / image DPI)")

cover-ink: kdp-cover ## cover TAC gate (C+M+Y+K <= 240% per pixel)
	@$(UV) scripts/check_ink_coverage.py --pdf $(BUILD)/cover/cover-kdp.pdf

narration-export: epub ## per-chapter plain text for AI narration pipelines
	@$(UV) scripts/export_narration.py --epub $(BUILD)/epub/book$(JOB_SUFFIX).epub
	$(call say,"build/narration/*.txt")

onix: ## ONIX 3.0 metadata export from book.yaml (onixcheck-validated)
	@$(UV) scripts/export_onix.py
	$(call say,"build/onix/onix-30.xml")

pdfx: pdf ## PDF/X-1a derivative interior (IngramSpark/Lulu; KDP uses pdf)
	@$(UV) scripts/export_pdfx.py \
	  --pdf $(BUILD)/latex/book-print$(JOB_SUFFIX).pdf \
	  --out $(BUILD)/pdfx/book-print$(JOB_SUFFIX)-x1a.pdf
	@$(UV) scripts/preflight_pdf.py $(BUILD)/pdfx/book-print$(JOB_SUFFIX)-x1a.pdf
	$(call say,"build/pdfx/book-print$(JOB_SUFFIX)-x1a.pdf")

stats: ## word counts + deltas
	@$(UV) scripts/book_stats.py

vocab: ## OpenGloss vocabulary-variety report (advisory, never a gate)
	@$(UV) scripts/vocab_variety.py

metrics: ## burstiness/lexical-diversity prose metrics (advisory)
	@$(UV) scripts/prose_metrics.py

prose-report: ## one-command prose-quality report with round deltas (advisory)
	@$(UV) scripts/prose_report.py

lengths: ## sentence/paragraph length distribution vs per-style targets (advisory)
	@$(UV) scripts/length_distribution.py

slop: ## multi-level slop audit; LLM judge via slop_audit.py --llm (advisory)
	@$(UV) scripts/slop_audit.py

pangram: ## Pangram AI-detector cross-check (needs PANGRAM_API_KEY; paid; advisory)
	@$(UV) scripts/pangram_check.py

ontology: ## writing-ontology stats + schema lint (advisory; docs/architecture/writing-ontology.md)
	@$(UV) scripts/writing_ontology.py stats
	@$(UV) scripts/writing_ontology.py lint

craft: ## macro-to-micro craft diagnostics: constructions, figures, rhythm, register, arcs, promises (advisory)
	@$(UV) scripts/construction_variety.py
	@$(UV) scripts/figure_detector.py
	@$(UV) scripts/rhythm_audit.py
	@$(UV) scripts/register_report.py
	@$(UV) scripts/arc_profiler.py
	@$(UV) scripts/setup_payoff.py
	@$(UV) scripts/move_annotator.py --no-sequence

brief: ## one-file craft brief per chapter: diagnosis + owed promises + what to reach for + paste-ready blocks (advisory; BRIEF args: CHAPTER=chNN OUT=dir)
	@$(UV) scripts/craft_brief.py $(if $(CHAPTER),--chapter $(CHAPTER)) $(if $(OUT),--out $(OUT))

verify-citations: ## URL reachability + verified= + archived= gates (network)
	@$(UV) scripts/verify_citation.py --require-stamps --require-archives

doctor: ## toolchain, fonts, drift audit
	@$(UV) scripts/doctor.py

validate-all: pdf bleed ebook epub epub-a11y kdp-cover preflight cover-ink check test-simplified test-sbe-study doctor ## full gate
	$(call say,"validate-all: all gates passed")

# ---------------- lifecycle ----------------
PRINTING ?= first-printing

release: ## stamped release dir: slugged artifacts + README + SHA256SUMS
	@git diff --quiet || { echo "release: git tree is dirty"; exit 1; }
	@$(MAKE) validate-all
	@$(MAKE) pdfx onix
	@$(MAKE) verify-citations
	@$(UV) scripts/generate_metadata.py $(EDITION_FLAG) --strict
	@$(UV) scripts/package_release.py --printing $(PRINTING) $(EDITION_FLAG)

watch: generated ## continuous rebuild on save
	$(LATEXMK) -pvc -view=none -jobname=book-print latex/main.tex

clean: ## remove all build output and generated files
	rm -rf $(BUILD)
	rm -f latex/generated/*.tex
	$(call say,"clean")
