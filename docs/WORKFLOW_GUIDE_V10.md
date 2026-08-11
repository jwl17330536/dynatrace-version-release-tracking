# Version Intelligence Sync v10

## Overview

This workflow collects Dynatrace component release and runtime version data, writes normalized lookups, and updates markdown cards on dashboard v10.

## Workflow Links

- [Workflow Options](?options)
- [Trigger](?trigger)
- [Initialize Workflow Context](?task=initialize_workflow_context&tab=options)
- [Collect Release Indexes](?task=collect_release_indexes&tab=input)
- [Build Lookup Payloads](?task=build_lookup_payloads&tab=input)
- [Build Markdown Dashboard Payload](?task=build_markdown_dashboard_payload&tab=input)
- [Update Dashboard v10](?task=update_release_dashboard_v10_markdown&tab=input)

## Required Inputs

1. `apiTokenVaultId`
2. `rumTokenVaultId`
3. `platformBearerToken` or `platformTokenVaultId`
4. `releaseDashboardV10Id`

## Where To Set Inputs

Set these in Dynatrace at:

1. `Workflows`
2. Open `Version Intelligence Sync v10 Markdown Dashboard`
3. `Workflow options`
4. `Trigger`
5. `Inputs`

For manual runs from `dtctl exec workflow`, pass the same values with `--params key=value` because manual execution does not inherit schedule static inputs.

## Input Matrix

### `apiTokenVaultId`

1. Where to set: `Workflow options -> Trigger -> Inputs -> apiTokenVaultId`
2. Expected format: `CREDENTIALS_VAULT-xxxxxxxxxxxxxxxx`
3. Where to get it:
   Create or open a `Token` credential in `Settings -> Credentials vault`, then copy the credential ID, not the token value.
4. What it stores:
   An Environment API token used for `/api/v1/config/clusterversion`.
5. Required rights:
   `ReadConfig`, plus workflow actor access to read the vault entry.

### `rumTokenVaultId`

1. Where to set: `Workflow options -> Trigger -> Inputs -> rumTokenVaultId`
2. Expected format: `CREDENTIALS_VAULT-xxxxxxxxxxxxxxxx`
3. Where to get it:
   Create or open a `Token` credential in `Settings -> Credentials vault`, then copy the credential ID, not the token value.
4. What it stores:
   The latest active Environment API token. Prefer rotating the token inside the existing vault entry instead of changing workflow JSON.
5. Required rights:
   `ReadConfig`, `ReadSyntheticData`, `events.ingest`, plus workflow actor access to read the vault entry.

### `platformTokenVaultId`

1. Where to set: `Workflow options -> Trigger -> Inputs -> platformTokenVaultId`
2. Expected format: `CREDENTIALS_VAULT-xxxxxxxxxxxxxxxx`
3. Where to get it:
   Create or open a `Token` credential in `Settings -> Credentials vault` that contains a platform bearer/JWT token, then copy the credential ID.
4. What it stores:
   A platform token used for `/platform/document/v1/documents/*` dashboard reads and updates.
5. Required rights:
   Permission to read and update dashboard documents, plus workflow actor access to read the vault entry.

### `platformBearerToken`

1. Where to set: `Workflow options -> Trigger -> Inputs -> platformBearerToken`
2. Intended use:
   Temporary manual-run override only when vault-backed platform auth is unavailable.
3. Security rule:
   Do not commit or export live values. In v10, placeholder values such as `<SET_PLATFORM_BEARER_TOKEN>` are ignored.

### `releaseDashboardV10Id`

1. Where to set: `Workflow options -> Trigger -> Inputs -> releaseDashboardV10Id`
2. Expected format: dashboard document UUID
3. Where to get it:
   Use `dtctl get dashboard <id-or-name> -o json --plain`, or copy the document ID from the dashboard URL/resource details.
4. Current v10 value in this repo:
   `20abcd0f-9f19-4545-9565-575bb7cd939d`

## Setup

1. Set `apiTokenVaultId` to a credential-vault token with `ReadConfig`.
2. Set `rumTokenVaultId` to a credential-vault token with `ReadConfig`, `ReadSyntheticData`, and `events.ingest`.
3. Set `platformTokenVaultId` to a credential-vault token that can read and update dashboard documents.
4. Only use `platformBearerToken` for temporary manual runs when vault-backed platform auth is unavailable.
5. Confirm `releaseDashboardV10Id` points to dashboard v10.
6. Save and run manually once.
7. Verify lookup uploads and dashboard markdown updates.

## Output

- Lookup file `/lookups/dt_component_release_status`
- Lookup file `/lookups/dt_component_runtime_versions`
- Markdown cards for current and next planned releases per component

## Visual Rules

1. Keep top title markdown iconized and text aligned to Dynatrace Component Release Tracking.
2. Keep Release Risk Legend markdown stable.
3. Keep section title markdown iconized:
   - ☁️ SaaS
   - 🖥️ OneAgent
   - 🛰️ ActiveGate
   - ☸️ Operator
   - 🌐 EdgeConnect

## Troubleshooting

1. Dashboard update 401 JWT parse error:
   set a valid platform bearer/JWT token in `platformTokenVaultId`, or pass `platformBearerToken` only for a temporary manual run.
2. Missing markdown tile updates:
   verify dashboard ID and tile mapping.
3. `Token Authentication failed` for `rum_collect_runtime_versions` or `oneagent_store_baseline_event`:
   rotate the token stored inside the existing credential-vault entry referenced by `rumTokenVaultId`.
4. `HTTP 403` from RUM or events APIs:
   verify the token is valid but missing required scopes.
5. Empty runtime rows:
   verify scopes and source telemetry.

## Versioning

Workflow v10 must update dashboard v10 only. For changes, create v11 pair and disable v10 schedule after enabling v11.
