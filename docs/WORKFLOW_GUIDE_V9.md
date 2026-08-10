# Version Intelligence Sync v9

## Overview

This workflow collects Dynatrace component release metadata and runtime version distributions, writes normalized lookup datasets, and updates markdown cards on dashboard v9.

## Workflow Links

- [Workflow Options](?options)
- [Trigger](?trigger)
- [Initialize Workflow Context](?task=initialize_workflow_context&tab=options)
- [Collect Release Indexes](?task=collect_release_indexes&tab=input)
- [Build Lookup Payloads](?task=build_lookup_payloads&tab=input)
- [Upload Release Lookup](?task=upload_release_lookup&tab=input)
- [Upload Runtime Lookup](?task=upload_runtime_lookup&tab=input)
- [Build Markdown Dashboard Payload](?task=build_markdown_dashboard_payload&tab=input)
- [Update Dashboard v9](?task=update_release_dashboard_v9_markdown&tab=input)

## Prerequisites

1. API token credential vault IDs for environment API and RUM/event tasks.
2. Platform bearer token (or platform JWT credential vault entry) for document updates.
3. Existing dashboard v9 document ID.
4. Permission to upload lookup files.

## Required Inputs

1. `apiTokenVaultId`
2. `rumTokenVaultId`
3. `platformBearerToken` or `platformTokenVaultId`
4. `releaseDashboardV9Id`
5. Optional:
   - `releaseLookupPath`
   - `runtimeLookupPath`
   - `docsSitemapUrl`
   - `releaseParserDepth`

## Setup Steps

1. Open Workflow options and configure all required inputs.
2. Confirm `releaseDashboardV9Id` points to the dashboard version v9 resource.
3. Save and run workflow manually once.
4. Verify:
   - lookup uploads succeed
   - markdown updater succeeds
   - dashboard top timestamp updates

## Outputs

- Lookup: `/lookups/dt_component_release_status`
- Lookup: `/lookups/dt_component_runtime_versions`
- Dashboard markdown cards for current and next planned releases

## AI Task Behavior

`ai_summarize_release_notes` is intentionally a deterministic no-op extension point.

- It does not gate downstream logic.
- It exists for future optional enrichment.

## Troubleshooting

1. `401 Could not parse JWT` during dashboard update:
   - Provide valid platform bearer token.
2. Missing tile updates:
   - Verify dashboard ID and markdown tile map alignment.
3. Empty runtime rows:
   - Validate token scope and telemetry source availability.
4. Lookup upload failure:
   - Validate parse pattern and file write permissions.

## Versioning

This workflow must only update dashboard v9. For behavior updates, create v10 workflow and v10 dashboard together, then disable v9 schedule.
