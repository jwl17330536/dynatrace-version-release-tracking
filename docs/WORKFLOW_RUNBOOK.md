# Workflow Runbook

## Workflow Identity
- Title: Version Intelligence Sync v3
- File: workflows/version-intelligence-sync.v3.workflow.json
- Canonical workflow ID: 786ad6e6-cf90-4e1d-a67e-6544f2d5be8d

## Workflow Guide Source
- UI guide markdown source: docs/WORKFLOW_GUIDE_V3.md
- Apply in UI from Workflow Options -> Workflow guide -> Edit guide.
- Note: `dtctl apply` currently does not persist `guide` in this tenant for v3 (`dtctl get workflow` returns `guide: null`).

## Setup
1. Import or apply the workflow in Dynatrace.
2. Configure schedule trigger inputs for environment-specific values.
3. Ensure token scopes include required read APIs and events.ingest.
4. Run once manually and validate successful execution.
5. Enable schedule only after manual validation.
6. Keep the workflow `id` in the JSON file so apply updates in place.

## Required Inputs
- Dynatrace docs availability for release parsing.
- Dynatrace API connectivity for version and runtime collection.
- Valid vault token(s) with correct scopes.
- Schedule inputs configured in the trigger:
  - apiTokenVaultId
  - rumTokenVaultId
  - docsSitemapUrl
  - releaseLookupPath
  - runtimeLookupPath
  - lookupLocale
  - lookupTimezone
- Manual execution compatibility:
  - v3 Run JavaScript tasks resolve values from `execution().input` or `execution().params`.
  - `dtctl exec workflow --params key=value` is required for manual runs when the execution is not started from a trigger path that provides inputs.
  - Verified no-params manual run behavior: missing required config keys (`docsSitemapUrl`, `apiTokenVaultId`, `rumTokenVaultId`) and fails fast.

## Operating Model
- One active scheduled workflow in this sync path.
- All changes to workflow logic follow vN+1 naming.
- Keep older versions available for rollback.
- Keep a stable `id` in the local workflow file to avoid duplicate creation.

## Implemented Task Groups
1. Baseline compatibility tasks:
  - oneagent_collect_release_baseline
  - oneagent_store_baseline_event
  - rum_collect_runtime_versions
2. Cross-component release/runtime tasks:
  - collect_release_indexes
  - collect_saas_current_version
  - collect_oneagent_runtime_distribution
  - collect_activegate_runtime_distribution
  - collect_operator_runtime_distribution
  - collect_edgeconnect_runtime_distribution
  - build_lookup_payloads
  - upload_release_lookup
  - upload_runtime_lookup
3. AI enrichment task:
  - ai_summarize_release_notes

## Troubleshooting
- If baseline task fails:
  - Check docs endpoint accessibility.
  - Check parser assumptions for page format changes.
- If event ingest fails:
  - Check token scope and tenant API domain resolution.
- If RUM collection fails:
  - Validate RUM API permissions and API response shape.
- If release lookup upload fails:
  - Check resource-store lookup upload permissions and parse pattern compatibility.
  - Confirm CSV schema matches expected lookup fields.
- If AI summary task fails:
  - Check Davis Copilot workflow action availability and workflow permissions.
  - Verify `summary_prompt` is present from `collect_release_indexes`.
- If ActiveGate becomes unavailable:
  - Validate ActiveGate startup logs exist in the selected window and still contain parseable version text in parentheses.
  - Confirm `collect_activegate_runtime_distribution` DQL still returns `activegate_version` rows.
- If Operator is `not_configured`:
  - Confirm tenant has no Kubernetes clusters (`dt.entity.kubernetes_cluster` count is zero).
  - This status is expected in non-Kubernetes environments.
- If Operator is `partial`:
  - Kubernetes clusters are present, but operator version extraction is not yet implemented.
  - Prioritize implementing a cluster workload/log source for operator image tags or version fields.
- If EdgeConnect remains unavailable:
  - This is expected until runtime source validation is implemented.
  - Confirm placeholder collector task still produces explicit unavailable row.

## Rollback
1. Disable the new scheduled version.
2. Re-enable the last known good version.
3. Record rollback reason in migration inventory.

## Validation Checklist
- Manual run succeeded.
- Expected output events exist.
- Runtime lookup contains rows for saas, oneagent, activegate, operator, edgeconnect.
- Release lookup contains latest and next-planned rows per component.
- Dashboard queries return current run data.
- No secrets or tokens are embedded in workflow files.
