#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash scripts/run_ci_smoke.sh <mode> [options]

Modes:
  static
    Runs local static CI smoke flow.

  live
    Runs local live-v5 CI smoke flow (requires DT_ENVIRONMENT and DT_API_TOKEN).

  preflight
    Runs v5 preflight with optional arguments passed through.

Examples:
  bash scripts/run_ci_smoke.sh static
  bash scripts/run_ci_smoke.sh live
  bash scripts/run_ci_smoke.sh preflight --profile ci-static
  bash scripts/run_ci_smoke.sh preflight --profile v5 --execute-workflow
EOF
}

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

mode="$1"
shift || true

case "$mode" in
  static)
    if [[ $# -gt 0 ]]; then
      echo "ERROR: static mode does not accept extra arguments" >&2
      usage
      exit 2
    fi
    exec bash scripts/run_ci_static_smoke.sh
    ;;

  live)
    if [[ $# -gt 0 ]]; then
      echo "ERROR: live mode does not accept extra arguments" >&2
      usage
      exit 2
    fi
    exec bash scripts/run_ci_live_smoke.sh
    ;;

  preflight)
    exec python3 scripts/run_v5_preflight.py "$@"
    ;;

  -h|--help|help)
    usage
    exit 0
    ;;

  *)
    echo "ERROR: unknown mode '$mode'" >&2
    usage
    exit 2
    ;;
esac
