# Dynatrace Component Release Tracking

## Overview
Cross-component view for SaaS, OneAgent, ActiveGate, Operator, and EdgeConnect current versus published release status.

## Purpose
When administrators need one place to compare currently running Dynatrace component versions against current and upcoming published releases, this dashboard reduces manual release-note correlation and rollout planning effort.

## Setup
1. Import the dashboard JSON in this folder into your Dynatrace tenant.
2. Confirm companion workflow outputs are available.
3. Share the dashboard with your environment (read) and keep owner edit permissions.
4. Capture and add screenshot.png before contribution PR.

## Companion Workflow
- Title: Version Intelligence Sync v5
- File: workflows/version-intelligence-sync.v5.workflow.json

## Dashboard Variants
1. `release-tracking-dashboard.v2.json`: detailed engineering baseline with broad table coverage.
2. `release-tracking-dashboard.v3.json`: operations-first layout with stronger triage signal and reduced table density.
3. `release-tracking-dashboard.v4.json`: component-sectioned operations layout with per-component runtime/release/queue/risk views.

## v4 Focus Areas
1. One global action-required summary tile.
2. Dedicated sections for SaaS, ActiveGate, OneAgent, Operator, and Edge.
3. Per-section runtime source health and release status views.
4. Per-section upgrade queue with aligned/unknown/newer action state.
5. Per-section risk/highlights for latest published release.

## Reference Documentation
- docs/DASHBOARD_ARCHITECTURE.md
- docs/DASHBOARD_QUERY_CATALOG.md

## Notes
- Replace placeholder tenant_url in meta.yaml with the live shared dashboard URL.
- Do not include tokens, credentials, or customer-confidential values.
