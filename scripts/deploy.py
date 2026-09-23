#!/usr/bin/env python3
"""
Deploy a versioned workflow and/or dashboard to a Dynatrace tenant.

Merges personal config from local-only/my-config.json into the canonical
templates, then applies via dtctl. Config values are never committed —
only the sanitized templates are tracked in git.

Usage:
  python3 scripts/deploy.py [--dry-run] [--dashboard] [--context CONTEXT] [--version VERSION]

Options:
  --dry-run           Print merged JSON without deploying (safe to run anytime)
  --dashboard         Also deploy the dashboard before the workflow
  --context CONTEXT   dtctl context to use (default: current dtctl context)
  --version VERSION   Version to deploy, e.g. v11 (default: v11)

Config keys recognized in local-only/my-config.json:
  releaseDashboardV11Id   Dashboard UUID — injected into workflow trigger inputs
  dashboardId             Dashboard UUID — injected as 'id' field when deploying dashboard
                          (if set, updates the existing dashboard; if absent, creates new)
  apiTokenVaultId         CREDENTIALS_VAULT-... for ReadConfig token
  rumTokenVaultId         CREDENTIALS_VAULT-... for RUM token
  platformTokenVaultId    CREDENTIALS_VAULT-... for platform JWT token
  platformBearerToken     Temporary override only (use platformTokenVaultId instead)
"""

import argparse
import copy
import json
import os
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_VERSION = "v11"
WORKFLOW_TEMPLATE = "workflows/version-intelligence-sync.{version}.workflow.json"
DASHBOARD_TEMPLATE = "dashboards/release-tracking-dashboard.{version}.json"
CONFIG_FILE = "local-only/my-config.json"
CONFIG_EXAMPLE = "local-only/my-config.example.json"


def load_json(path: str):
    full = os.path.join(REPO_ROOT, path)
    if not os.path.exists(full):
        return None
    with open(full) as f:
        return json.load(f)


def apply_config_to_workflow(workflow: dict, config: dict) -> dict:
    merged = copy.deepcopy(workflow)
    trigger = merged.setdefault("trigger", {})
    inputs = trigger.setdefault("inputs", {})

    # Inject any config key that already exists as a trigger input (version-agnostic)
    for key, value in config.items():
        if key == "dashboardId":
            continue  # dashboardId is for dashboard deploy, not workflow inputs
        if key in inputs:
            entry = inputs[key]
            if isinstance(entry, dict):
                entry["value"] = value
            else:
                inputs[key] = {"value": value}
        elif key in ("releaseDashboardV10Id", "releaseDashboardV11Id",
                     "apiTokenVaultId", "rumTokenVaultId",
                     "platformTokenVaultId", "platformBearerToken"):
            # Explicitly inject these even if not yet present as keys
            inputs[key] = {"value": value}

    return merged


def apply_config_to_dashboard(dashboard: dict, config: dict) -> dict:
    merged = copy.deepcopy(dashboard)
    dashboard_id = config.get("dashboardId", "").strip()
    if dashboard_id and not dashboard_id.startswith("<"):
        merged["id"] = dashboard_id
        print(f"  Updating existing dashboard: {dashboard_id}")
    else:
        merged.pop("id", None)
        print("  No dashboardId in config — dtctl will create a new dashboard")
    return merged


def run_dtctl(cmd):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False, text=True)
    return result.returncode, ""


def deploy_dashboard(version, config, context, dry_run):
    dashboard_path = DASHBOARD_TEMPLATE.format(version=version)
    dashboard = load_json(dashboard_path)
    if dashboard is None:
        print(f"ERROR: Dashboard template not found: {dashboard_path}", file=sys.stderr)
        return 1

    merged = apply_config_to_dashboard(dashboard, config)

    if dry_run:
        print(f"\n--- Dashboard JSON ({dashboard_path}) ---")
        print(json.dumps(merged, indent=2))
        return 0

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, dir="/tmp") as tmp:
        json.dump(merged, tmp, indent=2)
        tmp_path = tmp.name

    try:
        cmd = ["dtctl", "apply", "dashboard", "-f", tmp_path]
        if context:
            cmd += ["--context", context]
        rc, output = run_dtctl(cmd)
        if rc == 0 and not config.get("dashboardId"):
            print("\nNOTE: A new dashboard was created. Copy its UUID from the Dynatrace URL")
            print("      and add it to local-only/my-config.json as:")
            print('        "dashboardId": "<UUID>",')
            print(f'        "releaseDashboard{version.upper()}Id": "<UUID>"')
        return rc
    finally:
        os.unlink(tmp_path)


def deploy_workflow(version, config, context, dry_run):
    workflow_path = WORKFLOW_TEMPLATE.format(version=version)
    workflow = load_json(workflow_path)
    if workflow is None:
        print(f"ERROR: Workflow template not found: {workflow_path}", file=sys.stderr)
        return 1

    merged = apply_config_to_workflow(workflow, config)

    if dry_run:
        print(f"\n--- Workflow JSON ({workflow_path}) ---")
        print(json.dumps(merged, indent=2))
        return 0

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, dir="/tmp") as tmp:
        json.dump(merged, tmp, indent=2)
        tmp_path = tmp.name

    try:
        cmd = ["dtctl", "apply", "workflow", "-f", tmp_path]
        if context:
            cmd += ["--context", context]
        rc, _ = run_dtctl(cmd)
        return rc
    finally:
        os.unlink(tmp_path)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--dry-run", action="store_true", help="Print merged JSON without deploying")
    parser.add_argument("--dashboard", action="store_true", help="Also deploy the dashboard")
    parser.add_argument("--context", default=None, help="dtctl context (default: current context)")
    parser.add_argument(
        "--version", default=DEFAULT_VERSION, help=f"Version to deploy (default: {DEFAULT_VERSION})"
    )
    args = parser.parse_args()

    config = load_json(CONFIG_FILE)
    if config is None:
        print(f"ERROR: Config file not found: {CONFIG_FILE}", file=sys.stderr)
        print(f"       Copy the example and fill in your values:", file=sys.stderr)
        print(f"         cp {CONFIG_EXAMPLE} {CONFIG_FILE}", file=sys.stderr)
        sys.exit(1)

    for k, v in config.items():
        if isinstance(v, str) and ("<YOUR_" in v or "xxxxxxxx" in v):
            print(f"WARNING: {k} still contains a placeholder value", file=sys.stderr)

    if args.dashboard:
        print(f"\n=== Deploying dashboard ({args.version}) ===")
        rc = deploy_dashboard(args.version, config, args.context, args.dry_run)
        if rc != 0:
            print(f"ERROR: Dashboard deploy failed (exit {rc})", file=sys.stderr)
            sys.exit(rc)

    print(f"\n=== Deploying workflow ({args.version}) ===")
    rc = deploy_workflow(args.version, config, args.context, args.dry_run)
    sys.exit(rc)


if __name__ == "__main__":
    main()
