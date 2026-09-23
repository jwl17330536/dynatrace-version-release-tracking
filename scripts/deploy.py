#!/usr/bin/env python3
"""
Deploy the v10 workflow to a Dynatrace tenant.

Merges personal config from local-only/my-config.json into the canonical
workflow template, then applies it via dtctl. Config values are never
committed — only the sanitized template is tracked in git.

Usage:
  python3 scripts/deploy.py [--dry-run] [--context CONTEXT] [--version VERSION]

Options:
  --dry-run           Print the merged workflow JSON without deploying
  --context CONTEXT   dtctl context to use (default: current dtctl context)
  --version VERSION   Workflow version to deploy (default: v10)
"""

import argparse
import copy
import json
import os
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_VERSION = "v10"
WORKFLOW_TEMPLATE = "workflows/version-intelligence-sync.{version}.workflow.json"
CONFIG_FILE = "local-only/my-config.json"
CONFIG_EXAMPLE = "local-only/my-config.example.json"


def load_json(path: str) -> dict:
    full = os.path.join(REPO_ROOT, path)
    if not os.path.exists(full):
        return None
    with open(full) as f:
        return json.load(f)


def deep_merge(base: dict, overlay: dict) -> dict:
    result = copy.deepcopy(base)
    for key, value in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def apply_config_to_workflow(workflow: dict, config: dict) -> dict:
    merged = copy.deepcopy(workflow)
    trigger = merged.setdefault("trigger", {})
    inputs = trigger.setdefault("inputs", {})

    input_keys = [
        "releaseDashboardV10Id",
        "apiTokenVaultId",
        "rumTokenVaultId",
        "platformTokenVaultId",
        "platformBearerToken",
    ]
    for key in input_keys:
        if key in config:
            if isinstance(inputs.get(key), dict):
                inputs[key]["value"] = config[key]
            else:
                inputs[key] = {"value": config[key]}

    return merged


def run_dtctl(workflow_path: str, context: str | None) -> int:
    cmd = ["dtctl", "apply", "workflow", "-f", workflow_path]
    if context:
        cmd += ["--context", context]
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="Print merged JSON without deploying")
    parser.add_argument("--context", default=None, help="dtctl context (default: current context)")
    parser.add_argument("--version", default=DEFAULT_VERSION, help=f"Workflow version (default: {DEFAULT_VERSION})")
    args = parser.parse_args()

    workflow_path = WORKFLOW_TEMPLATE.format(version=args.version)
    workflow = load_json(workflow_path)
    if workflow is None:
        print(f"ERROR: Workflow template not found: {workflow_path}", file=sys.stderr)
        sys.exit(1)

    config = load_json(CONFIG_FILE)
    if config is None:
        print(f"ERROR: Config file not found: {CONFIG_FILE}", file=sys.stderr)
        print(f"       Copy the example and fill in your values:", file=sys.stderr)
        print(f"         cp {CONFIG_EXAMPLE} {CONFIG_FILE}", file=sys.stderr)
        sys.exit(1)

    placeholder_check = ["<YOUR_DASHBOARD_UUID>", "xxxxxxxxxxxxxxxx"]
    for val in placeholder_check:
        for k, v in config.items():
            if isinstance(v, str) and val in v:
                print(f"WARNING: {k} still contains a placeholder value: {v}", file=sys.stderr)

    merged = apply_config_to_workflow(workflow, config)

    if args.dry_run:
        print(json.dumps(merged, indent=2))
        return

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        json.dump(merged, tmp, indent=2)
        tmp_path = tmp.name

    try:
        rc = run_dtctl(tmp_path, args.context)
        sys.exit(rc)
    finally:
        os.unlink(tmp_path)


if __name__ == "__main__":
    main()
