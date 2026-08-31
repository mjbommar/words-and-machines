# isa-calculus -- the book, the paper, and the object ledger that binds them.
# `make check` is the gate: every object's checker must exit by the finding.
AXEYUM ?= $(HOME)/projects/personal/axeyum
export AXEYUM

.PHONY: help ledger artifact-check code-check axeyum-checkout-check machine-example-check check check-run reproduce book clean

help: ## list targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  %-14s %s\n",$$1,$$2}'

ledger: ## regenerate objects/LEDGER.md and the book's generated status macros from objects/*.json
	python3 scripts/gen_ledger.py

artifact-check: ## validate active evidence manifests, paths, and digests
	python3 -m unittest scripts.tests.test_evidence_manifest scripts.tests.test_check_axeyum_checkout
	python3 scripts/check_artifacts.py

code-check: ## parse A0 listings and assemble every RV64I and x86-64 listing
	python3 -m unittest scripts.test_check_code_listings
	python3 scripts/check_code_listings.py

axeyum-checkout-check: ## require a source-compatible and built Axeyum replay checkout
	python3 scripts/check_axeyum_checkout.py

machine-example-check: axeyum-checkout-check ## execute every published A0, RV64, and x86 machine listing
	@test -x "$(AXEYUM)/.venv/bin/python" || { printf '%s\n' "missing $(AXEYUM)/.venv/bin/python; build the Axeyum Python package first" >&2; exit 1; }
	"$(AXEYUM)/.venv/bin/python" -m unittest scripts.tests.test_axeyum_machine_examples

check: ledger artifact-check code-check ## validate every active object, manifest, and code listing
	python3 scripts/check_objects.py

check-run: check ## ALSO execute every checker_command and negative_control
	$(MAKE) machine-example-check
	python3 scripts/check_artifacts.py --run
	python3 scripts/check_objects.py --run

reproduce: check-run ## replay every active checker and negative control

book: ledger ## build the book PDF (delegates to book/Makefile; needs TeX Live + uv)
	$(MAKE) -C book pdf

clean:
	$(MAKE) -C book clean 2>/dev/null || true
