SHELL := /bin/bash

PROFILE ?= v5
PREFLIGHT_ARGS ?=

.PHONY: help static live preflight preflight-static preflight-v5 preflight-exec self-check ci-check release-readiness

help:
	@echo "dt-version-checker automation targets"
	@echo ""
	@echo "Core smoke targets:"
	@echo "  make static            # Local static CI smoke flow"
	@echo "  make live              # Local live-v5 CI smoke flow (requires DT_ENVIRONMENT + DT_API_TOKEN)"
	@echo ""
	@echo "Preflight targets:"
	@echo "  make preflight PROFILE=v5"
	@echo "  make preflight PROFILE=ci-static"
	@echo "  make preflight-exec    # Preflight with workflow execution"
	@echo ""
	@echo "Quality gates:"
	@echo "  make self-check        # Shell syntax + Python compile + workflow YAML parse"
	@echo "  make ci-check          # self-check + static smoke"
	@echo "  make release-readiness # ci-check + ci-static preflight + timestamped readiness report"

static:
	bash scripts/run_ci_smoke.sh static

live:
	bash scripts/run_ci_smoke.sh live

preflight:
	bash scripts/run_ci_smoke.sh preflight --profile "$(PROFILE)" $(PREFLIGHT_ARGS)

preflight-static:
	$(MAKE) preflight PROFILE=ci-static

preflight-v5:
	$(MAKE) preflight PROFILE=v5

preflight-exec:
	$(MAKE) preflight PROFILE=v5 PREFLIGHT_ARGS="--execute-workflow"

self-check:
	bash -n scripts/run_ci_smoke.sh scripts/run_ci_static_smoke.sh scripts/run_ci_live_smoke.sh
	python3 -m py_compile scripts/run_validation_suite.py scripts/run_v5_preflight.py scripts/write_validation_summary.py scripts/run_release_readiness.py
	ruby -e 'require "yaml"; YAML.load_file(".github/workflows/release-tracking-validation.yml"); puts "YAML OK"'
	python3 scripts/write_validation_summary.py --report-path reports/validation/nonexistent.json --title "Self-check Summary Probe" > /dev/null
	@echo "Self-check passed"

ci-check: self-check static

release-readiness:
	python3 scripts/run_release_readiness.py
