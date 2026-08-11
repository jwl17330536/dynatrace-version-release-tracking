# Historical Assets

This repository keeps historical workflow and dashboard versions for traceability, rollback analysis, and contributor validation.

## Not Required for Initial Install

You do not need historical `v1`-`v9` assets to install and run this package.

For first-time setup, use only:

1. `workflows/version-intelligence-sync.v10.workflow.json`
2. `dashboards/release-tracking-dashboard.v10.json`

## Why Historical Assets Remain

1. Validation scripts and architecture comparisons reference prior versions.
2. Contributors use previous versions to verify behavior deltas.
3. Historical artifacts support auditability and rollback context.

## Future Direction

Historical assets may be reduced in future iterations once validation tooling is migrated to canonical-only baselines.
