# Version Intelligence Sync v3

## Purpose
Collect and normalize component release and runtime version intelligence for SaaS, OneAgent, ActiveGate, Operator, and EdgeConnect.

## Prerequisites
- Credential Vault token for platform/environment API calls.
- Credential Vault token with RUM JavaScript tag read access (if RUM checks are enabled).
- Workflow permission to read the selected vault entries.
- Lookup upload permission for target lookup paths.

## Configuration
1. Open Workflow Options: [?options](?options)
2. Open Trigger setup: [?trigger](?trigger)
3. Configure these trigger inputs:
- `apiTokenVaultId` (required)
- `rumTokenVaultId` (required)
- `docsSitemapUrl` (required)
- `releaseLookupPath` (required)
- `runtimeLookupPath` (required)
- `lookupLocale` (required)
- `lookupTimezone` (required)

## Task Navigation
- [Release metadata collection](?task=collect_release_indexes&tab=options)
- [SaaS runtime collector](?task=collect_saas_current_version&tab=options)
- [Payload normalization](?task=build_lookup_payloads&tab=options)
- [Release lookup upload](?task=upload_release_lookup&tab=options)
- [Runtime lookup upload](?task=upload_runtime_lookup&tab=options)

## Validation
1. Run workflow manually.
2. Confirm both upload tasks succeed.
3. Confirm lookup row counts:
- `/lookups/dt_component_release_status` -> 10 rows expected
- `/lookups/dt_component_runtime_versions` -> 7 rows expected
4. Confirm dashboard tiles render without missing-field errors.

## Troubleshooting
- If upload tasks return HTTP 200 but records are zero, inspect upload task response payload in execution task result.
- If `component` field is missing in dashboard queries, inspect lookup metadata and confirm columns are populated.
- If operator shows `not_configured`, this is expected when no Kubernetes clusters are present.

## Scheduling
Keep only one active scheduled version at a time. Enable v3 schedule only after validation and disable superseded schedules.
