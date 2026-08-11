# dynatrace-version-release-tracking

Canonical repository for the Dynatrace Version Intelligence release-tracking package.

## Purpose
- Collect release metadata and runtime version telemetry for key Dynatrace components.
- Normalize data into reusable lookup files.
- Update a markdown-card dashboard for operational release review.
- Provide a portable workflow + dashboard template other teams can reuse.

## Repository Standards

1. Canonical user install path: `README.md` + `QUICK_START.md`.
2. Contributor workflow: `CONTRIBUTING.md`.
3. Release history: `CHANGELOG.md`.
4. This repository is standalone and does not require `dynatrace-infrastructure-observability-framework`.

## Start Here

1. Fast install path: `QUICK_START.md`.
2. Canonical runtime and setup details: this `README.md`.
3. Developer iteration and validation workflow: `CONTRIBUTING.md`.

## Canonical Assets
- Workflow: `workflows/version-intelligence-sync.v10.workflow.json`
- Workflow live export snapshot: `workflows/version-intelligence-sync.v10.live.export.workflow.json`
- Dashboard source artifact: `dashboards/release-tracking-dashboard.v10.json`
- Dashboard live export snapshot: `dashboards/release-tracking-dashboard.v10.live.export.json`

Only these v10 assets are required for first-time install.

## Install Boundary

For install and runtime setup, ignore older version files (`v1`-`v9`) unless you are doing historical comparison or rollback analysis.

Historical assets remain in this repository for traceability and contributor validation workflows.

See `docs/HISTORICAL_ASSETS.md` for details.

## Mandatory Version Alignment Policy
This repo enforces a strict lockstep versioning policy:

1. Workflow `vN` must update dashboard `vN` only.
2. Never edit prior versions in place for behavior changes.
3. Every iteration creates a new `vN+1` workflow and `vN+1` dashboard pair.
4. After enabling new workflow `vN+1`, disable workflow `vN` schedule.
5. Keep one active Version Intelligence schedule at any time.

See `docs/VERSION_ALIGNMENT_POLICY.md` for full rules and operational checks.

## Workflow Guide
Dynatrace Workflow Guide content for v10 is maintained in:

- `docs/WORKFLOW_GUIDE_V10.md`

Note: current `dtctl` export payloads do not include a `guide` property in this tenant. After importing/applying in a tenant, paste the markdown from `docs/WORKFLOW_GUIDE_V10.md` into **Workflow guide** in the UI (Workflow options).

## Tenant Portability
Before enabling schedule in a new tenant, update workflow inputs:

1. `releaseDashboardV10Id`
2. `apiTokenVaultId`
3. `rumTokenVaultId`
4. `platformBearerToken` or `platformTokenVaultId` (platform JWT credential)
5. Optional lookup paths and parser depth

Do not commit live bearer token values.

Set these in Dynatrace under `Workflow options -> Trigger -> Inputs`.

Minimum input requirements:

1. `apiTokenVaultId`
	Credential-vault ID for an Environment API token used by `/api/v1/config/clusterversion`.
	Required scope: `ReadConfig`.
2. `rumTokenVaultId`
	Credential-vault ID for an Environment API token used by `/api/v1/rum/manualApps` and `/api/v2/events/ingest`.
	Required scopes: `ReadConfig`, `ReadSyntheticData`, `events.ingest`.
3. `platformTokenVaultId`
	Credential-vault ID for a platform bearer/JWT token used by `/platform/document/v1/documents/*`.
	Required rights: ability to read and update dashboard documents.
4. `platformBearerToken`
	Temporary manual-run override only when vault-backed platform auth is unavailable.
5. `releaseDashboardV10Id`
	Dashboard document UUID from the dashboard URL or `dtctl get dashboard <id-or-name> -o json --plain`.

In v10, placeholder values like `<SET_PLATFORM_BEARER_TOKEN>` are ignored and a configured `platformTokenVaultId` takes precedence.

## Repository Layout
- `workflows/`: canonical v10 install artifact plus historical versioned workflow JSON artifacts.
- `dashboards/`: canonical v10 install artifact plus historical versioned dashboard JSON artifacts.
- `docs/`: runbooks, architecture notes, guide templates, version policy.
- `scripts/`: validation and CI helper scripts.
- `field-asset-library/`: contribution-ready dashboard packaging.
- `references/`: historical snapshots for traceability.

## Validation
- `make help`
- `make self-check`
- `make static`
- `make ci-check`
- `python3 scripts/run_validation_suite.py --profile canonical` (canonical v10 assets)
- `python3 scripts/run_validation_suite.py --profile v5` (legacy compatibility checks)

For local CI smoke:
- `bash scripts/run_ci_smoke.sh static`

## Security
- Never commit secrets, tokens, or tenant-private IDs unless intentionally public.
- Use placeholders in committed artifacts (`<...>` format).
- Supply runtime credentials via environment variables, secret stores, or vault IDs.

## Cross-Repo Consumers
Some dashboards in `dynatrace-private-ops` consume events produced by this workflow (for example OneAgent baseline annotations). Those dashboards remain in their own repo and are documented as consumers, not source assets.
