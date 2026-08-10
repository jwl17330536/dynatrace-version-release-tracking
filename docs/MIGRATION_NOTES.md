# Migration Notes

## Source

This repository was initialized by migrating Version Intelligence assets from `dt-version-checker`.

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

Dynatrace UI supports a Workflow Guide markdown panel. Because dtctl workflow exports do not currently round-trip a guide field in this tenant, guide source is maintained in `docs/WORKFLOW_GUIDE_V9.md` and should be pasted into the UI Workflow Guide after apply.
