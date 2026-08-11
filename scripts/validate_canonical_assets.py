#!/usr/bin/env python3
import json
import sys
from pathlib import Path

CANONICAL_WORKFLOW_PATH = Path("workflows/version-intelligence-sync.v10.workflow.json")
CANONICAL_DASHBOARD_PATH = Path("dashboards/release-tracking-dashboard.v10.json")



def fail(msg: str) -> int:
    print(f"FAIL: {msg}")
    return 1



def load_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text())



def main() -> int:
    try:
        workflow = load_json(CANONICAL_WORKFLOW_PATH)
    except Exception as exc:
        return fail(f"unable to load canonical workflow: {exc}")

    try:
        dashboard = load_json(CANONICAL_DASHBOARD_PATH)
    except Exception as exc:
        return fail(f"unable to load canonical dashboard: {exc}")

    workflow_title = str(workflow.get("title", "")).strip()
    if "v10" not in workflow_title.lower():
        return fail(f"unexpected workflow title (expected v10 marker): {workflow_title}")

    if workflow.get("isDeployed") is not True:
        return fail("canonical workflow isDeployed is not true")

    trigger = workflow.get("trigger", {})
    if not isinstance(trigger, dict) or not trigger:
        return fail("canonical workflow trigger block is missing")

    dashboard_type = str(dashboard.get("type", "")).strip().lower()
    if dashboard_type != "dashboard":
        return fail(f"unexpected dashboard type: {dashboard.get('type')}")

    dashboard_name = str(dashboard.get("name", "")).strip()
    if "v10" not in dashboard_name.lower():
        return fail(f"unexpected dashboard name (expected v10 marker): {dashboard_name}")

    tiles = dashboard.get("content", {}).get("tiles", {})
    if not isinstance(tiles, dict) or not tiles:
        return fail("canonical dashboard has no tiles")

    print("PASS: canonical v10 assets are present and structurally valid")
    print(f"  workflow: {CANONICAL_WORKFLOW_PATH}")
    print(f"  dashboard: {CANONICAL_DASHBOARD_PATH}")
    print(f"  dashboard tiles: {len(tiles)}")
    return 0



if __name__ == "__main__":
    sys.exit(main())
