# OneAgent Baseline Sync v2 (with RUM Classic JS Versions)

Workflow file:
- `local-notes/dynatrace-version-release-tracking.workflow.json`

Dashboard file:
- `local-notes/rum-version-compliance-dashboard.json`

## What this workflow does

- Keeps the original OneAgent baseline sync behavior.
- Collects RUM classic JavaScript library version per app.
- Writes one custom event per app (`RUMJSVersion|...`) for dashboard queries.
- Writes a run summary event (`RUMJSVersionSyncSummary|...`).
- Writes a baseline event (`RUMJSBaseline|...`) with latest, oldest supported, and effective target RUM classic JS versions.
- Writes per-app policy events (`RUMJSPolicyApp|...`) with status: `on_target`, `below_target`, `unsupported`, `above_target`, `unknown`.
- Writes a policy summary event (`RUMJSPolicySummary|...`) with counts by status.

## Version format clarification

The workflow tracks two different version domains:

- OneAgent baseline values (`latest_release`, `oldest_supported_ess`) are OneAgent versions like `1.339`.
- RUM classic values (`js_library_version`, `latest_version`, `oldest_supported_version`) come from RUM JavaScript APIs and are numeric revision IDs.

Important:

- RUM numeric values are not OneAgent version numbers.
- Dynatrace documents these RUM values as natural numbers where a higher value means a newer RUM JavaScript build.
- The Dynatrace UI may display a friendlier RUM label (for example `1.339.4.20260508-173628`), but the API endpoints used by this workflow return numeric revision IDs.
- Compare RUM values numerically only; do not compare them to OneAgent `1.xxx` versions.
- When available, the workflow also extracts a best-effort human-readable target label from the manual insertion tag response and surfaces it separately from the numeric version IDs.

This workflow is on the same track as the Dynatrace guidance you quoted:

- `GET /api/v1/rum/appRevision/{entity}` is the per-application current version.
- `GET /api/v1/rum/jsLatestVersion` is the tenant-wide latest available version.
- `GET /api/v1/rum/jsConfiguredVersions` is the tenant-wide configured version set shown in the UI.
- The dashboard should treat those values as RUM JavaScript compliance inputs, not as OneAgent release numbers.

## Required updates before import/run

Update placeholders in the workflow JSON:

1. In both JavaScript tasks (`store_baseline_event` and `sync_rum_classic_js_versions`), set:
- `RUM_TOKEN_VAULT_ID = "..."`

2. `RUM_TOKEN_VAULT_ID` must be a credential vault entry ID:
- `CREDENTIALS_VAULT-xxxxxxxxxxxxxxxx`

3. Do not use Access Tokens **Token ID** values (for example `dt0c01.xxxxx`) as `RUM_TOKEN_VAULT_ID`.
- Token IDs are not credential vault IDs and will fail authentication.

4. Do not set tenant URL.
- The script resolves the environment URL via `@dynatrace-sdk/app-environment` and converts `.apps.` hosts to classic API domain automatically.

## Token scopes needed

For token used by `RUM_TOKEN_VAULT_ID`:
- RUM JavaScript tag management read scope (to call `/api/v1/rum/manualApps` and `/api/v1/rum/appRevision/{entity}`).
- Events ingest permission (to call `/api/v2/events/ingest`).
- Optional: `rumManualInsertionTags.read` if you want best-effort human-readable target labels from the manual insertion tag APIs.

## Import order

1. Import workflow JSON.
2. Set `RUM_TOKEN_VAULT_ID` in both JavaScript tasks.
3. Run workflow once manually and confirm success.
4. Import dashboard JSON.
5. Validate dashboard tiles populate.

## Quick validation queries

Latest per-app JS library versions:

```dql
fetch events
| filter source == "rum_classic_api" and isNotNull(application_id) and isNotNull(js_library_version)
| fields ts = timestamp, app_id = application_id, app_name = application_name, js_version = js_library_version
| sort ts desc
| dedup app_id
| fields app_name, app_id, js_version, last_seen = ts
| sort app_name asc
```

Latest run summary:

```dql
fetch events
| filter source == "rum_classic_api" and isNotNull(app_count) and isNotNull(versions_found)
| sort timestamp desc
| limit 1
| fields app_count = toLong(app_count), versions_found = toLong(versions_found), fetched_at
```

Latest and oldest-supported RUM classic baseline:

```dql
fetch events
| filter source == "rum_classic_baseline" and isNotNull(latest_version) and isNotNull(oldest_supported_version)
| sort timestamp desc
| limit 1
| fields latest_version, oldest_supported_version, effective_target_version, effective_target_policy, effective_target_label, latest_stable, previous_stable, latest_ie_supported, latest_ie11_supported, fetched_at
```

Latest policy summary:

```dql
fetch events
| filter source == "rum_classic_policy_summary"
| sort timestamp desc
| limit 1
| fields apps_on_target = toLong(apps_on_target), apps_below_target = toLong(apps_below_target), apps_unsupported = toLong(apps_unsupported), apps_above_target = toLong(apps_above_target), apps_unknown = toLong(apps_unknown), effective_target_version, effective_target_policy, effective_target_label, oldest_supported_version, latest_version, fetched_at
```

Latest per-app policy status:

```dql
fetch events
| filter source == "rum_classic_policy_app" and isNotNull(application_id)
| fields ts = timestamp, app_id = application_id, app_name = application_name, js_version = js_library_version, human_readable_target_label, status = policy_status, effective_target_version, effective_target_policy, oldest_supported_version, latest_version, fetched_at
| fieldsAdd app_name = coalesce(app_name, app_id)
| sort ts desc
| dedup app_id
| fields app_name, app_id, status, js_version, human_readable_target_label, effective_target_version, effective_target_policy, oldest_supported_version, latest_version, fetched_at, last_seen = ts
| sort status asc, app_name asc
```
