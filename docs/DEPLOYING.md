# Deploying — Iterate Without Touching the Dynatrace UI

The deploy pattern in this repo lets you make changes and push them to Dynatrace with a single command. Your personal configuration (vault IDs, dashboard UUID) lives in a gitignored local file — never committed. The public workflow template stays clean.

---

## How it works

```
local-only/my-config.json      ← your real values (gitignored, never committed)
         +
workflows/version-intelligence-sync.v10.workflow.json   ← the public template
         ↓
scripts/deploy.py              ← merges them together
         ↓
dtctl apply workflow           ← pushes to your Dynatrace tenant
```

Your config values are injected at deploy time. You never manually edit the Dynatrace workflow inputs through the UI again.

---

## One-time setup

**1. Create your personal config file**

```bash
cp local-only/my-config.example.json local-only/my-config.json
```

Edit `local-only/my-config.json` with your actual values:

```json
{
  "releaseDashboardV10Id": "paste-your-dashboard-uuid-here",
  "apiTokenVaultId": "CREDENTIALS_VAULT-your-actual-id",
  "rumTokenVaultId": "CREDENTIALS_VAULT-your-actual-id",
  "platformTokenVaultId": "CREDENTIALS_VAULT-your-actual-id"
}
```

This file is in `.gitignore` — it will never be committed.

**2. Confirm dtctl is authenticated**

```bash
dtctl config current-context
dtctl auth whoami --plain
```

---

## Iteration cycle

```bash
# 1. Edit the workflow or dashboard template
vim workflows/version-intelligence-sync.v10.workflow.json

# 2. Preview what will be deployed
make deploy-dry

# 3. Deploy to your tenant
make deploy

# 4. Verify in Dynatrace — run the workflow once manually and check the dashboard
```

---

## Deploy to a specific context

```bash
make deploy DEPLOY_CONTEXT=sprint
make deploy DEPLOY_CONTEXT=prod
```

Or directly:

```bash
python3 scripts/deploy.py --context sprint
python3 scripts/deploy.py --dry-run --context sprint
```

---

## Workflow guide

dtctl does not round-trip the Workflow Guide field. After deploying, re-paste the guide manually:

1. Open the workflow in Dynatrace
2. Click **Workflow options** → **Guide**
3. Paste the contents of `docs/WORKFLOW_GUIDE_V10.md`

---

## Creating a new version (vN+1)

When you're ready to publish a new workflow version:

1. Copy the v10 workflow template: `cp workflows/version-intelligence-sync.v10.workflow.json workflows/version-intelligence-sync.v11.workflow.json`
2. Copy the v10 dashboard: `cp dashboards/release-tracking-dashboard.v10.json dashboards/release-tracking-dashboard.v11.json`
3. Make your changes to the v11 files
4. Deploy the new version: `make deploy DEPLOY_VERSION=v11`
5. Enable the v11 workflow schedule in Dynatrace, then disable the v10 schedule
6. Open a PR with your new v11 pair

---

## Security

`local-only/my-config.json` is gitignored. The deploy script will warn you if your config still contains placeholder values. Never commit your config file, and never hardcode real values into the workflow template.
