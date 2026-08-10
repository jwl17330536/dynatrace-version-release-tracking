# Cross-Repo Reuse Audit

## Goal
Avoid duplicate version-checking assets by reusing existing work first.

## Reused from dynatrace-private-ops
- Workflow: dt-version-checker.v9
- Dashboards: oneagent-version-dashboard, rum-classic-js-version-dashboard, rum-version-compliance-dashboard.v3
- Docs: oneagent-baseline-rum-classic-sync.README

## Left in Place by Design
- Historical workflow versions v5-v8 and oneagent-baseline-sync remain as reference snapshots.
- Repo-specific release checklists/changelogs/scripts remain in their owning repos:
  - netflow-observability
  - proxmox-observability
  - unifi-observability
  - application-observability-hub

## Decision Criteria
- Migrate if asset is tenant-wide Dynatrace version checking and actively reusable.
- Keep in source repo if asset is component-specific, historical-only, or unrelated to tenant-wide version tracking.

## Duplicate Prevention
Before adding new workflow/dashboard logic:
1. Compare against `workflows/`, `dashboards/`, and `references/` in this repo.
2. Check whether the same capability already exists in migrated assets.
3. If new logic is required, document the gap in commit/PR notes.
