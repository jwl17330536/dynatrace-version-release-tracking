# Deploying — Iterate Without Touching the Dynatrace UI

The deploy pattern in this repo lets you push changes to Dynatrace with a single command. Your personal configuration (vault IDs, dashboard UUID) lives in a gitignored local file — never committed. The public templates stay clean.

---

## How it works

```
local-only/my-config.json                          ← your real values (gitignored)
         +
dashboards/release-tracking-dashboard.v11.json     ← public dashboard template
workflows/version-intelligence-sync.v11.workflow.json  ← public workflow template
         ↓
scripts/deploy.py                                  ← merges config into templates
         ↓
dtctl apply dashboard  →  dtctl apply workflow     ← pushes to your Dynatrace tenant
```

---

## One-time setup

**1. Create your personal config file**

```bash
cp local-only/my-config.example.json local-only/my-config.json
```

Edit `local-only/my-config.json` with your actual values:

```json
{
  "releaseDashboardV11Id": "paste-your-dashboard-uuid-here",
  "dashboardId": "paste-your-dashboard-uuid-here",
  "apiTokenVaultId": "CREDENTIALS_VAULT-your-actual-id",
  "rumTokenVaultId": "CREDENTIALS_VAULT-your-actual-id",
  "platformTokenVaultId": "CREDENTIALS_VAULT-your-actual-id"
}
```

- `dashboardId` — the UUID of the dashboard in your tenant. If set, the deploy script updates the existing dashboard. If absent, it creates a new one.
- `releaseDashboardV11Id` — the same UUID, injected into the workflow's trigger inputs so the workflow knows which dashboard to update.

This file is in `.gitignore` — it will never be committed.

**2. Confirm dtctl is authenticated**

```bash
dtctl config current-context
dtctl auth whoami --plain
```

---

## First-time deploy (dashboard + workflow)

If you don't have a dashboard UUID yet, omit `dashboardId` from your config. The deploy script will create a new dashboard and tell you the UUID to save.

```bash
# Deploy dashboard first (creates new), then workflow
make deploy-all

# After deploy-all, note the dashboard UUID printed in the output.
# Add it to local-only/my-config.json:
#   "dashboardId": "<the-uuid>",
#   "releaseDashboardV11Id": "<the-uuid>"
# Then redeploy the workflow so it knows the dashboard UUID:
make deploy
```

---

## Preview before deploying

```bash
make deploy-dry
```

Prints the merged dashboard and workflow JSON to stdout — no changes made to your tenant.

---

## Day-2 iteration cycle

```bash
# 1. Edit a template
vim workflows/version-intelligence-sync.v11.workflow.json

# 2. Preview the merged output
make deploy-dry

# 3. Deploy workflow only (dashboard unchanged)
make deploy

# 4. Or redeploy both if the dashboard template changed
make deploy-all
```

---

## Deploy to a specific context

```bash
make deploy-all DEPLOY_CONTEXT=sprint
make deploy DEPLOY_CONTEXT=prod
```

Or directly:

```bash
python3 scripts/deploy.py --dashboard --context sprint
python3 scripts/deploy.py --dry-run --dashboard --context sprint
```

---

## Workflow guide

dtctl does not round-trip the Workflow Guide field. After deploying, re-paste the guide manually:

1. Open the workflow in Dynatrace
2. Click **Workflow options** → **Guide**
3. Paste the contents of `docs/WORKFLOW_GUIDE_V11.md`

---

## Creating a vN+1

When you're ready to publish a new version:

1. `cp workflows/version-intelligence-sync.v11.workflow.json workflows/version-intelligence-sync.v12.workflow.json`
2. `cp dashboards/release-tracking-dashboard.v11.json dashboards/release-tracking-dashboard.v12.json`
3. Make your changes to the v12 files
4. `make deploy-all DEPLOY_VERSION=v12`
5. Enable the v12 workflow schedule in Dynatrace, then disable the v11 schedule
6. Open a PR with the v12 pair

---

## Security

`local-only/my-config.json` is gitignored. The deploy script warns if any config value still contains a placeholder. Never commit your config file, and never hardcode real values into the public templates.
