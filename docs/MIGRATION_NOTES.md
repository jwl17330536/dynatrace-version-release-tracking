# Migration Notes

## Source

This repository was initialized by migrating Version Intelligence assets from the legacy repository `dt-version-checker` (now deprecated).

## Cutover Result

- New dashboard created: `Dynatrace Component Release Tracking v9`
- Dashboard ID: `71ce9cf7-4736-46bf-ae51-b9977d2bf19a`
- New workflow created: `Version Intelligence Sync v9 Markdown Dashboard`
- Workflow ID: `c446519c-e8fe-430d-8473-a29086986254`
- Previous workflow v8 (`2ed34b17-dff8-46d8-aeea-2310f8b3796c`) disabled

## Corrective Changes in v9

1. Removed stale v7 naming from dashboard updater paths and input keys.
2. Updated workflow to target `releaseDashboardV9Id`.
3. Preserved markdown header-tile tolerance in dashboard patch logic.
4. Kept AI summarization as explicit no-op extension point.
5. Fixed rollout propagation bug in newer-release branch (`row.rollout_start_date`).

## Workflow Guide

Dynatrace UI supports a Workflow Guide markdown panel. Because dtctl workflow exports do not currently round-trip a guide field in this tenant, guide source is maintained in `docs/WORKFLOW_GUIDE_V9.md` and `docs/WORKFLOW_GUIDE_V10.md` and should be pasted into the UI Workflow Guide after apply.

## v10 Iteration and Cutover

- New dashboard created: `Dynatrace Component Release Tracking v10`
- Dashboard ID: `20abcd0f-9f19-4545-9565-575bb7cd939d`
- New workflow created: `Version Intelligence Sync v10 Markdown Dashboard`
- Workflow ID: `748a7500-1486-4829-8739-54558d7bf123`
- Previous workflow v9 (`c446519c-e8fe-430d-8473-a29086986254`) disabled

### v10 UX/content updates

1. Preserved separate top title and Release Risk Legend behavior.
2. Added emoji section headers and emoji main title in markdown tiles.
3. Kept deterministic markdown-only update pattern and v10 dashboard targeting.

### Validation notes

1. Manual runs require explicit `--params` for workflow inputs; scheduled static inputs are not auto-injected into manual executions.
2. Dashboard markdown updates validated on v10 tiles (`0`, `12`-`17`).
3. In this tenant, guide markdown still does not persist in workflow export payloads; source remains in `docs/WORKFLOW_GUIDE_V10.md` for UI paste.
4. A later auth remediation hardened v10 token handling so placeholder platform bearer inputs do not override a configured vault-backed platform token.
5. Runtime auth failures on `rum_collect_runtime_versions` and `oneagent_store_baseline_event` are remediated by rotating the token value inside the referenced credential-vault entry rather than committing raw token changes.
