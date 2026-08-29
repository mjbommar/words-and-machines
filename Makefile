# isa-calculus -- the book, the paper, and the object ledger that binds them.
# `make check` is the gate: every object's checker must exit by the finding.
AXEYUM ?= $(HOME)/projects/personal/axeyum
export AXEYUM

.PHONY: help ledger artifact-check check check-run reproduce book clean

help: ## list targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  %-14s %s\n",$$1,$$2}'

ledger: ## regenerate objects/LEDGER.md and the book's generated status macros from objects/*.json
	python3 scripts/gen_ledger.py

artifact-check: ## validate active evidence manifests, paths, and digests
	python3 scripts/check_artifacts.py

check: ledger artifact-check ## validate every active object and manifest
	python3 scripts/check_objects.py

check-run: check ## ALSO execute every checker_command and negative_control
	python3 scripts/check_objects.py --run

reproduce: check-run ## replay every active checker and negative control

book: ledger ## build the book PDF (delegates to book/Makefile; needs TeX Live + uv)
	$(MAKE) -C book pdf

clean:
	$(MAKE) -C book clean 2>/dev/null || true
