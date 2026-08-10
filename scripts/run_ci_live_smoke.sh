#!/usr/bin/env bash
set -euo pipefail

# Mirrors the manual GitHub Actions live-v5 job locally.
# Required environment variables:
#   DT_ENVIRONMENT
#   DT_API_TOKEN

if [[ -z "${DT_ENVIRONMENT:-}" || -z "${DT_API_TOKEN:-}" ]]; then
  echo "ERROR: Missing required environment variables DT_ENVIRONMENT and/or DT_API_TOKEN" >&2
  echo "Hint: export DT_ENVIRONMENT and DT_API_TOKEN, then retry." >&2
  exit 1
fi

mkdir -p reports/validation

report_path="reports/validation/ci-v5-live.latest.json"
summary_path="reports/validation/ci-v5-live.step-summary.md"

: > "$summary_path"

dtctl config set-credentials ci-token --token "$DT_API_TOKEN"
dtctl config set-context ci \
  --environment "$DT_ENVIRONMENT" \
  --token-ref ci-token \
  --safety-level readonly

dtctl config use-context ci
dtctl doctor --plain

exit_code=0
if ! python3 scripts/run_validation_suite.py --profile v5 --json | tee "$report_path"; then
  exit_code=$?
fi

python3 scripts/write_validation_summary.py \
  --report-path "$report_path" \
  --title "Live V5 Validation Summary" \
  --summary-path "$summary_path"

echo "Live validation report: $report_path"
echo "Live validation summary: $summary_path"

exit "$exit_code"
