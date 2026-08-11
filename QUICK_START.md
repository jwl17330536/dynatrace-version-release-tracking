# Quick Start

## Prerequisites

1. Dynatrace tenant with Workflows and Dashboards.
2. Credential Vault IDs for:
- `apiTokenVaultId` (`ReadConfig`)
- `rumTokenVaultId` (`ReadConfig`, `ReadSyntheticData`, `events.ingest`)
- `platformTokenVaultId` (platform document read/write rights)
3. Dashboard document ID for `releaseDashboardV10Id`.

## Install

Required artifacts only:

1. `workflows/version-intelligence-sync.v10.workflow.json`
2. `dashboards/release-tracking-dashboard.v10.json`

Older `v1`-`v9` assets are not needed for initial installation.

1. Import workflow artifact:
- `workflows/version-intelligence-sync.v10.workflow.json`
2. Import dashboard artifact:
- `dashboards/release-tracking-dashboard.v10.json`
3. Set required workflow trigger inputs in Dynatrace.
4. Enable the workflow schedule.

## Verify

1. Run the workflow once manually.
2. Confirm lookup updates and markdown tiles populate on dashboard v10.
3. Confirm exactly one Version Intelligence schedule is active.
