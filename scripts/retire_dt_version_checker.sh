#!/bin/bash
set -euo pipefail

# Retire the legacy dt-version-checker folder/repo with safety gates.
# Default mode is dry-run. Use --execute to perform archival/removal actions.

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd "${SCRIPT_PATH%/*}" && pwd)"
CANONICAL_REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DEV_ROOT_DEFAULT="$(cd "$CANONICAL_REPO_DIR/.." && pwd)"

DEV_ROOT="${DEV_ROOT:-$DEV_ROOT_DEFAULT}"
LEGACY_DIR="${LEGACY_DIR:-$DEV_ROOT/dt-version-checker}"
RETIRE_ON_DATE="${RETIRE_ON_DATE:-2026-09-10}"

EXECUTE=false
REMOVE_LOCAL=false
ARCHIVE_REMOTE=false
FORCE_DATE=false
GITHUB_REPO="${GITHUB_REPO:-}"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/retire_dt_version_checker.sh [options]

Options:
  --execute               Perform archive/removal actions (default is dry-run)
  --remove-local          Remove local legacy folder after checks pass (requires --execute)
  --archive-remote        Archive GitHub repository if one is detected/provided (requires --execute)
  --github-repo OWNER/REPO
                          Explicit remote to archive (for example jwl17330536/dt-version-checker)
  --dev-root PATH         Override workspace dev root (default: parent of canonical repo)
  --legacy-dir PATH       Override local legacy path (default: <dev-root>/dt-version-checker)
  --retire-on-date YYYY-MM-DD
                          Earliest date for retirement actions (default: 2026-09-10)
  --force-date            Bypass retirement date gate
  -h, --help              Show this help

Examples:
  bash scripts/retire_dt_version_checker.sh
  bash scripts/retire_dt_version_checker.sh --execute --archive-remote --github-repo jwl17330536/dt-version-checker
  bash scripts/retire_dt_version_checker.sh --execute --remove-local --archive-remote --github-repo jwl17330536/dt-version-checker
EOF
}

GREP_BIN="/usr/bin/grep"
GIT_BIN="/usr/bin/git"
SED_BIN="/usr/bin/sed"
DATE_BIN="/bin/date"
CAT_BIN="/bin/cat"
RM_BIN="/bin/rm"

if [[ ! -x "$GREP_BIN" ]]; then
  GREP_BIN="$(command -v grep || true)"
fi
if [[ ! -x "$GIT_BIN" ]]; then
  GIT_BIN="$(command -v git || true)"
fi
if [[ ! -x "$SED_BIN" ]]; then
  SED_BIN="$(command -v sed || true)"
fi
if [[ ! -x "$DATE_BIN" ]]; then
  DATE_BIN="$(command -v date || true)"
fi
if [[ ! -x "$CAT_BIN" ]]; then
  CAT_BIN="$(command -v cat || true)"
fi
if [[ ! -x "$RM_BIN" ]]; then
  RM_BIN="$(command -v rm || true)"
fi

log() {
  printf '[retire] %s\n' "$*"
}

err() {
  printf '[retire][error] %s\n' "$*" >&2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --execute)
      EXECUTE=true
      ;;
    --remove-local)
      REMOVE_LOCAL=true
      ;;
    --archive-remote)
      ARCHIVE_REMOTE=true
      ;;
    --github-repo)
      shift
      GITHUB_REPO="${1:-}"
      ;;
    --dev-root)
      shift
      DEV_ROOT="${1:-}"
      ;;
    --legacy-dir)
      shift
      LEGACY_DIR="${1:-}"
      ;;
    --retire-on-date)
      shift
      RETIRE_ON_DATE="${1:-}"
      ;;
    --force-date)
      FORCE_DATE=true
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      err "Unknown option: $1"
      usage
      exit 2
      ;;
  esac
  shift
done

if [[ "$REMOVE_LOCAL" == true || "$ARCHIVE_REMOTE" == true ]] && [[ "$EXECUTE" != true ]]; then
  err "--remove-local and --archive-remote require --execute"
  exit 2
fi

if [[ -z "$GREP_BIN" ]] || [[ ! -x "$GREP_BIN" ]]; then
  err "grep is required"
  exit 1
fi

if [[ -z "$GIT_BIN" ]] || [[ ! -x "$GIT_BIN" ]]; then
  err "git is required"
  exit 1
fi

if [[ -z "$SED_BIN" ]] || [[ ! -x "$SED_BIN" ]]; then
  err "sed is required"
  exit 1
fi

if [[ -z "$DATE_BIN" ]] || [[ ! -x "$DATE_BIN" ]]; then
  err "date is required"
  exit 1
fi

if [[ -z "$CAT_BIN" ]] || [[ ! -x "$CAT_BIN" ]]; then
  err "cat is required"
  exit 1
fi

if [[ -z "$RM_BIN" ]] || [[ ! -x "$RM_BIN" ]]; then
  err "rm is required"
  exit 1
fi

if [[ ! -d "$DEV_ROOT" ]]; then
  err "DEV_ROOT does not exist: $DEV_ROOT"
  exit 1
fi

if [[ ! -d "$LEGACY_DIR" ]]; then
  log "Legacy directory not found (already removed?): $LEGACY_DIR"
fi

TODAY="$($DATE_BIN +%F)"
if [[ "$TODAY" < "$RETIRE_ON_DATE" ]]; then
  if [[ "$EXECUTE" == true && "$FORCE_DATE" != true ]]; then
    err "Date gate blocked: today=$TODAY retire_on_date=$RETIRE_ON_DATE (use --force-date to bypass)"
    exit 1
  fi
  if [[ "$EXECUTE" != true ]]; then
    log "Dry-run before retirement date: today=$TODAY retire_on_date=$RETIRE_ON_DATE"
  fi
fi

log "Scanning for blocking dt-version-checker references outside historical allowlist"
ref_file="/tmp/retire_dt_version_checker_refs.out"
filtered_file="/tmp/retire_dt_version_checker_refs_filtered.out"

(
  cd "$DEV_ROOT"
  "$GREP_BIN" -RIn "dt-version-checker" . \
    --exclude-dir=.git \
    --exclude-dir=.workspace-reorg \
    --exclude-dir=dt-version-checker \
    > "$ref_file" || true
)

# Allowed historical references in canonical migration-history docs.
# Anything else is considered a blocker.
"$GREP_BIN" -Ev '^\./dynatrace-version-release-tracking/docs/MIGRATION_NOTES\.md:' "$ref_file" | \
  "$GREP_BIN" -Ev '^\./dynatrace-version-release-tracking/docs/MIGRATION_INVENTORY\.md:' \
  | "$GREP_BIN" -Ev '^\./dynatrace-version-release-tracking/scripts/retire_dt_version_checker\.sh:' \
  > "$filtered_file" || true

if [[ -s "$filtered_file" ]]; then
  err "Blocking references found. Update these before retirement:"
  "$CAT_BIN" "$filtered_file"
  exit 1
fi

log "Reference gate passed"

if [[ -z "$GITHUB_REPO" && -d "$LEGACY_DIR/.git" ]]; then
  origin_url="$(cd "$LEGACY_DIR" && git remote get-url origin 2>/dev/null || true)"
  if [[ -n "$origin_url" ]]; then
    # Supports git@github.com:owner/repo.git and https://github.com/owner/repo.git
    repo_guess="$(printf '%s' "$origin_url" | "$SED_BIN" -E 's#^git@github.com:##; s#^https://github.com/##; s#\.git$##')"
    if [[ "$repo_guess" == */* ]]; then
      GITHUB_REPO="$repo_guess"
    fi
  fi
fi

if [[ "$EXECUTE" != true ]]; then
  log "Dry-run complete"
  log "Would archive remote: ${GITHUB_REPO:-<none detected>}"
  log "Would remove local dir: $LEGACY_DIR"
  exit 0
fi

if [[ "$ARCHIVE_REMOTE" == true ]]; then
  if [[ -z "$GITHUB_REPO" ]]; then
    err "--archive-remote requested but no GitHub repo could be determined. Provide --github-repo OWNER/REPO"
    exit 1
  fi
  if ! command -v gh >/dev/null 2>&1; then
    err "gh CLI is required for remote archive"
    exit 1
  fi
  log "Archiving GitHub repository: $GITHUB_REPO"
  gh api -X PATCH "repos/$GITHUB_REPO" -f archived=true >/dev/null
  log "Remote archived: $GITHUB_REPO"
fi

if [[ "$REMOVE_LOCAL" == true ]]; then
  if [[ -d "$LEGACY_DIR" ]]; then
    log "Removing local directory: $LEGACY_DIR"
    "$RM_BIN" -rf "$LEGACY_DIR"
    log "Local directory removed"
  else
    log "Local directory already absent: $LEGACY_DIR"
  fi
fi

log "Retirement execution completed"
