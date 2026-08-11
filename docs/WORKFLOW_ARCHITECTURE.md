# Workflow Architecture

## Workflow
- Title: Version Intelligence Sync v2
- File: workflows/version-intelligence-sync.v2.workflow.json
- Canonical workflow ID: 298cd024-8813-4a48-b5af-057537b9945a
- Schedule: Daily cron (single active scheduler policy)

## Current Task Graph
1. oneagent_collect_release_baseline
2. oneagent_store_baseline_event (depends on oneagent_collect_release_baseline)
3. rum_collect_runtime_versions
4. collect_release_indexes
5. collect_saas_current_version
6. collect_oneagent_runtime_distribution
7. collect_activegate_runtime_distribution
8. collect_operator_runtime_distribution
9. collect_edgeconnect_runtime_distribution
10. ai_summarize_release_notes (depends on collect_release_indexes)
11. build_lookup_payloads (depends on release/runtime collectors)
12. upload_release_lookup (depends on build_lookup_payloads)
13. upload_runtime_lookup (depends on build_lookup_payloads)

## Task Purpose Table
- oneagent_collect_release_baseline:
  Collects latest OneAgent release baseline from Dynatrace docs and returns latest release, oldest supported ESS version, source URL, and fetch timestamp.
- oneagent_store_baseline_event:
  Ingests baseline results as custom annotation events for downstream dashboards and compliance checks.
- rum_collect_runtime_versions:
  Collects RUM classic JavaScript runtime versions by app and writes policy and summary events.
- collect_release_indexes:
  Parses Dynatrace docs release pages and produces latest and next-planned release rows for all tracked components.
- collect_saas_current_version:
  Calls the cluster version API and returns SaaS runtime version rows.
- collect_oneagent_runtime_distribution:
  Runs DQL aggregation for OneAgent installerVersion distribution.
- collect_activegate_runtime_distribution:
  Collects ActiveGate runtime version distribution from log events by parsing `Dynatrace ActiveGate started.` lines.
- collect_operator_runtime_distribution:
  Collects Kubernetes inventory presence signal used to classify Operator runtime status as `not_configured` or `partial`.
- collect_edgeconnect_runtime_distribution:
  Current placeholder collector with explicit unavailable status until source validation is complete.
- ai_summarize_release_notes:
  Uses Davis Copilot workflow action to produce compact risk/highlight narrative from latest release rows.
- build_lookup_payloads:
  Normalizes release/runtime data, merges AI summaries, and enforces per-component row presence.
- upload_release_lookup and upload_runtime_lookup:
  Upload normalized rows into lookup tables used by the release-tracking dashboard.

## Data Contracts
- Input contracts:
  - Credential Vault token IDs are provided via schedule trigger inputs.
  - Lookup path and locale/timezone values are provided via schedule trigger inputs.
  - Dynatrace docs pages and API endpoints must be reachable.
- Output contracts:
  - Event stream includes OneAgent baseline and RUM runtime/policy events.
  - Lookup rows for release intelligence and runtime counts per component.

## Failure Behavior
- Any token resolution failure is treated as hard-fail.
- Event ingest API failures are hard-fail for affected task.
- Docs parsing failures are hard-fail for baseline collection.

## Planned Expansion Tasks
- operator_collect_runtime_distribution: replace cluster-presence signal with true operator version distribution source.
- edgeconnect_collect_runtime_distribution: replace placeholder with validated source implementation.

## Implemented in v2 Baseline
- collect_release_indexes
- collect_saas_current_version
- collect_oneagent_runtime_distribution
- collect_activegate_runtime_distribution
- collect_operator_runtime_distribution (inventory signal)
- build_lookup_payloads
- upload_release_lookup
- upload_runtime_lookup

## AI Summary Status
- `ai_summarize_release_notes` is wired and feeds summary text into release lookup rows.
- Current implementation parses `BREAKING:` and `HIGHLIGHTS:` sections and maps them into distinct summary fields for latest release rows.
- If section parsing fails, the compact AI output is used as a fallback to avoid empty enrichment.

## Ownership
- Repository owner: dynatrace-version-release-tracking
- Operational owner: platform observability workflow maintainers
- Change policy: vN+1 for workflow revisions; one active scheduled workflow only.
