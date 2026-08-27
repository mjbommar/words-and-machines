# isa-calculus -- the book, the paper, and the object ledger that binds them.
# `make check` is the gate: every object's checker must exit by the finding.
AXEYUM ?= $(HOME)/projects/personal/axeyum
export AXEYUM

.PHONY: help ledger check check-run reproduce book paper clean

help: ## list targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  %-14s %s\n",$$1,$$2}'

ledger: ## regenerate objects/LEDGER.md and the book's generated status macros from objects/*.json
	python3 scripts/gen_ledger.py

check: ledger ## structural + semantic validation of every object record
	python3 scripts/check_objects.py

check-run: ledger ## ALSO execute every checker_command and negative_control (needs $$AXEYUM prebuilt examples)
	python3 scripts/check_objects.py --run

reproduce: ## re-run the pure-Python exhaustive reproductions (no axeyum needed)
	python3 scripts/bitlogic_bfs.py
	python3 scripts/byte_perm_bfs.py

book: ledger ## build the book PDF (delegates to book/Makefile; needs TeX Live + uv)
	$(MAKE) -C book pdf

paper: ## build the paper PDF (delegates to paper/Makefile)
	$(MAKE) -C paper pdf

clean:
	$(MAKE) -C book clean 2>/dev/null || true
	$(MAKE) -C paper clean 2>/dev/null || true
