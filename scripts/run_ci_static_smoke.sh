#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports/validation

report_path="reports/validation/ci-static.latest.json"
summary_path="reports/validation/ci-static.step-summary.md"

: > "$summary_path"

exit_code=0
if ! python3 scripts/run_validation_suite.py --profile ci-static --json | tee "$report_path"; then
  exit_code=$?
fi

python3 scripts/write_validation_summary.py \
  --report-path "$report_path" \
  --title "Static Validation Summary" \
  --summary-path "$summary_path"

echo "Static validation report: $report_path"
echo "Static validation summary: $summary_path"

exit "$exit_code"
