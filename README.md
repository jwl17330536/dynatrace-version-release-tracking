# dynatrace-version-release-tracking

Canonical repository for the Dynatrace Version Intelligence release-tracking package.

## Purpose
- Collect release metadata and runtime version telemetry for key Dynatrace components.
- Normalize data into reusable lookup files.
- Update a markdown-card dashboard for operational release review.
- Provide a portable workflow + dashboard template other teams can reuse.

## Canonical Assets
- Workflow: `workflows/version-intelligence-sync.v9.workflow.json`
- Dashboard source artifact: `dashboards/release-tracking-dashboard.v9.json`
- Dashboard live export snapshot: `dashboards/release-tracking-dashboard.v9.live.export.json`

## Mandatory Version Alignment Policy
This repo enforces a strict lockstep versioning policy:

1. Workflow `vN` must update dashboard `vN` only.
2. Never edit prior versions in place for behavior changes.
3. Every iteration creates a new `vN+1` workflow and `vN+1` dashboard pair.
4. After enabling new workflow `vN+1`, disable workflow `vN` schedule.
5. Keep one active Version Intelligence schedule at any time.

See `docs/VERSION_ALIGNMENT_POLICY.md` for full rules and operational checks.

## Workflow Guide
Dynatrace Workflow Guide content for v9 is maintained in:

- `docs/WORKFLOW_GUIDE_V9.md`

Note: current `dtctl` export payloads do not include a `guide` property. After importing/applying in a tenant, paste the markdown from `docs/WORKFLOW_GUIDE_V9.md` into **Workflow guide** in the UI (Workflow options).

## Tenant Portability
Before enabling schedule in a new tenant, update workflow inputs:

1. `releaseDashboardV9Id`
2. `apiTokenVaultId`
3. `rumTokenVaultId`
4. `platformBearerToken` or `platformTokenVaultId` (platform JWT credential)
5. Optional lookup paths and parser depth

Do not commit live bearer token values.

## Repository Layout
- `workflows/`: versioned workflow JSON artifacts and live exports.
- `dashboards/`: versioned dashboard JSON artifacts and live exports.
- `docs/`: runbooks, architecture notes, guide templates, version policy.
- `scripts/`: validation and CI helper scripts.
- `field-asset-library/`: contribution-ready dashboard packaging.
- `references/`: historical snapshots for traceability.

## Validation
- `make help`
- `make self-check`
- `make static`
- `make ci-check`

For local CI smoke:
- `bash scripts/run_ci_smoke.sh static`

## Security
- Never commit secrets, tokens, or tenant-private IDs unless intentionally public.
- Use placeholders in committed artifacts (`<...>` format).
- Supply runtime credentials via environment variables, secret stores, or vault IDs.

## Cross-Repo Consumers
Some dashboards in `dynatrace-private-ops` consume events produced by this workflow (for example OneAgent baseline annotations). Those dashboards remain in their own repo and are documented as consumers, not source assets.
