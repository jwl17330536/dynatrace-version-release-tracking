# Dynatrace Component Release Tracking

## Overview
Cross-component view for SaaS, OneAgent, ActiveGate, Operator, and EdgeConnect current versus published release status.

## Purpose
When administrators need one place to compare currently running Dynatrace component versions against current and upcoming published releases, this dashboard reduces manual release-note correlation and rollout planning effort.

## Current Version
**v12** — see `dashboards/release-tracking-dashboard.v12.json` in the repo root.

## Setup
1. Follow the operator install guide: [QUICK_START.md](../../../../QUICK_START.md)
2. Import the latest dashboard JSON from `dashboards/` in the repo root.
3. Deploy the companion workflow using `make deploy-all` (see [docs/DEPLOYING.md](../../../../docs/DEPLOYING.md)).
4. Share the dashboard with your environment (read) and keep owner edit permissions.

## Companion Workflow
- Title: Version Intelligence Sync v12
- File: `workflows/version-intelligence-sync.v12.workflow.json`

## Notes
- Dashboard version history (v1–v12) is preserved in git. All canonical versions are in the `dashboards/` folder at the repo root.
- Replace placeholder tenant_url in meta.yaml with the live shared dashboard URL.
- Do not include tokens, credentials, or customer-confidential values.
