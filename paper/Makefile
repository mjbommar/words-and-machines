# ============================================================
# Paper build system. See docs/architecture/build-system.md.
#
#   make pdf          the paper PDF (engine/bib from paper.yaml)
#   make draft        DRAFT build: line numbers + banner
#   make anon         double-blind build (author identity stripped)
#   make figures      matplotlib + TikZ figures
#   make arxiv        hardened arXiv source bundle (ships .bbl)
#   make ssrn         SSRN PDF + paste-ready SSRN-METADATA.md
#   make check        style + reference/alt-text gates
#   make validate     everything a release must pass
#   make release      stamped release dir + SHA256SUMS
#
# The engine (pdflatex/xelatex/lualatex) and bibliography backend come
# from paper.yaml; the Makefile reads them via generate_metadata.py.
# ============================================================

ROOT   := $(CURDIR)
BUILD  := $(ROOT)/build
UV     := uv run --quiet
GEN    := $(UV) --with pyyaml scripts/generate_metadata.py

ENGINE := $(shell $(GEN) --print-engine 2>/dev/null || echo pdflatex)
VENUE  := $(shell $(GEN) --print-venue 2>/dev/null || echo preprint)

# Reproducible builds: pin SOURCE_DATE_EPOCH to the last commit so two
# builds of the same tree are byte-identical
# (reproducible-builds.org/docs/source-date-epoch/).
export SOURCE_DATE_EPOCH ?= $(shell git log -1 --format=%ct 2>/dev/null || date +%s)

# Map the engine to latexmk's flag.
ifeq ($(ENGINE),xelatex)
  LMK_ENGINE := -pdfxe
else ifeq ($(ENGINE),lualatex)
  LMK_ENGINE := -pdflua
else
  LMK_ENGINE := -pdf
endif

LATEXMK = latexmk $(LMK_ENGINE) -interaction=nonstopmode -halt-on-error \
          -output-directory=$(BUILD)/latex -cd

# ANSI status helper.
GREEN := \033[0;32m
NC    := \033[0m
define say
	@printf '$(GREEN)==> %s$(NC)\n' $(1)
endef

.PHONY: generated figures figures-tikz figures-mpl pdf draft anon grayscale \
        quick arxiv ssrn check lint wordcount repro doctor validate release watch \
        clean help

help: ## list targets
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-12s %s\n", $$1, $$2}'

# ---------------- metadata ----------------
generated: ## regenerate latex/generated/metadata.tex + build/arxiv-readme.json
	$(call say,"generating metadata (venue: $(VENUE), engine: $(ENGINE))")
	@$(GEN)

# ---------------- figures ----------------
figures: figures-mpl figures-tikz ## build all figures (matplotlib + TikZ)

figures-mpl: ## matplotlib figures from scripts/data/*.csv
	@$(UV) --with matplotlib scripts/build_figures.py

figures-tikz: ## standalone TikZ figures from latex/figures/src/*.tikz
	@$(UV) scripts/build_tikz.py

# ---------------- interiors ----------------
pdf: generated ## the paper PDF
	$(LATEXMK) -jobname=main latex/main.tex
	$(call say,"build/latex/main.pdf")

quick: generated ## fast single-pass draft (refs may be stale)
	@mkdir -p $(BUILD)/latex
	cd latex && $(ENGINE) -interaction=batchmode -output-directory=$(BUILD)/latex \
	  -jobname=main-quick main.tex || (tail -30 $(BUILD)/latex/main-quick.log; exit 1)
	$(call say,"build/latex/main-quick.pdf")

draft: generated ## DRAFT build: line numbers + banner
	$(LATEXMK) -usepretex='\def\DraftMode{1}' -jobname=main-draft latex/main.tex
	$(call say,"build/latex/main-draft.pdf")

anon: generated ## double-blind build (author identity stripped, incl. PDF metadata)
	$(LATEXMK) -usepretex='\def\AnonMode{1}' -jobname=main-anon latex/main.tex
	$(call say,"build/latex/main-anon.pdf")

grayscale: generated ## B&W-safe PDF (accent ramp collapses to gray)
	$(LATEXMK) -usepretex='\def\GrayscaleMode{1}' -jobname=main-grayscale latex/main.tex
	$(call say,"build/latex/main-grayscale.pdf")

# ---------------- submission ----------------
arxiv: figures pdf check ## hardened arXiv bundle + ARXIV-SUBMISSION.md
	@$(UV) --with pyyaml scripts/make_arxiv.py
	@$(UV) --with pyyaml scripts/export_arxiv_metadata.py
	$(call say,"build/arxiv/*.tar.gz + ARXIV-SUBMISSION.md")

ssrn: figures pdf ## SSRN PDF + paste-ready SSRN-METADATA.md
	@$(UV) --with pyyaml scripts/export_ssrn_metadata.py
	$(call say,"build/latex/main.pdf + SSRN-METADATA.md")

# ---------------- QA ----------------
check: ## style + reference/alt-text gates
	@$(UV) scripts/check_style.py
	@$(UV) scripts/check_refs.py

lint: ## chktex LaTeX lint on sections (advisory; skips if chktex absent)
	@$(UV) scripts/lint_latex.py

wordcount: ## per-section word counts (texcount)
	@$(UV) scripts/wordcount.py

# FORCE_SOURCE_DATE pins \today (and the \year/\month/\day primitives) to the
# epoch too, so two builds on DIFFERENT days are byte-identical — not just
# same-day. It is deliberately NOT exported for the normal build, where the
# title page should show the real \today (SSRN dates the paper as it appears).
repro: ## build twice at a fixed epoch; assert byte-identical PDFs (cross-day)
	@tmp=$$(mktemp); \
	 env SOURCE_DATE_EPOCH=1700000000 FORCE_SOURCE_DATE=1 \
	   $(MAKE) --no-print-directory clean pdf >/dev/null; \
	 cp $(BUILD)/latex/main.pdf $$tmp; \
	 env SOURCE_DATE_EPOCH=1700000000 FORCE_SOURCE_DATE=1 \
	   $(MAKE) --no-print-directory clean pdf >/dev/null; \
	 cmp -s $$tmp $(BUILD)/latex/main.pdf; res=$$?; \
	 rm -f $$tmp; \
	 $(MAKE) --no-print-directory clean >/dev/null; \
	 if [ $$res -eq 0 ]; then \
	   printf '$(GREEN)==> reproducible: two builds are byte-identical$(NC)\n'; \
	 else \
	   echo "repro: NOT byte-identical (fonts/timestamps?)"; exit 1; \
	 fi

doctor: ## toolchain, fonts, package, drift audit
	@$(UV) --with pyyaml scripts/doctor.py

validate: figures pdf check lint doctor ## everything a release must pass
	$(call say,"validate: all gates passed")

# ---------------- lifecycle ----------------
release: ## stamped release dir: slugged artifacts + SHA256SUMS
	@git diff --quiet || { echo "release: git tree is dirty"; exit 1; }
	@$(MAKE) validate
	@$(UV) --with pyyaml scripts/generate_metadata.py --strict
	@$(UV) --with pyyaml scripts/package_release.py

watch: generated ## continuous rebuild on save
	$(LATEXMK) $(LMK_ENGINE) -pvc -view=none -jobname=main latex/main.tex

clean: ## remove all build output and generated files
	rm -rf $(BUILD)
	rm -f latex/generated/*.tex
	$(call say,"clean")
