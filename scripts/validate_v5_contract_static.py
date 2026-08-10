#!/usr/bin/env python3
import json
import sys
from pathlib import Path

WORKFLOW_PATH = Path("workflows/version-intelligence-sync.v5.workflow.json")
DASHBOARD_PATH = Path(
    "field-asset-library/dashboards/platform/release-tracking-dashboard/release-tracking-dashboard.v5.json"
)

QUEUE_TILE_IDS = ["4", "9", "14", "19", "24"]
RISK_TILE_IDS = ["5", "10", "15", "20", "25"]

WORKFLOW_BUILD_REQUIRED = [
    "risk_priority",
    "highlight_focus",
    "action_hint",
    "deriveRiskPriority",
    "deriveHighlightFocus",
    "deriveActionHint",
]

WORKFLOW_UPLOAD_REQUIRED = [
    "risk_priority",
    "highlight_focus",
    "action_hint",
    "LD:risk_priority",
    "LD:highlight_focus",
    "LD:action_hint",
]

QUEUE_QUERY_REQUIRED = [
    "risk_priority",
    "breaking_now",
    "coming_next",
    "recommended_action",
    "admin_brief",
    "release_link",
    "release_notes_url",
    "action",
]

RISK_QUERY_REQUIRED = [
    "triage",
    "breaking_now",
    "coming_next",
    "risk_summary",
    "highlight_summary",
    "recommended_action",
    "admin_brief",
    "release_link",
    "release_notes_url",
]



def fail(msg: str) -> int:
    print(f"FAIL: {msg}")
    return 1



def load_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text())



def require_substrings(label: str, text: str, required):
    missing = [token for token in required if token not in text]
    if missing:
        return f"{label} missing tokens: {', '.join(missing)}"
    return ""



def validate_workflow_contract(workflow) -> list:
    errors = []
    tasks = workflow.get("tasks", {})

    build_script = (
        tasks.get("build_lookup_payloads", {})
        .get("input", {})
        .get("script", "")
    )
    upload_script = (
        tasks.get("upload_release_lookup", {})
        .get("input", {})
        .get("script", "")
    )

    if not build_script:
        errors.append("workflow task build_lookup_payloads.input.script is empty")
    else:
        err = require_substrings("build_lookup_payloads", build_script, WORKFLOW_BUILD_REQUIRED)
        if err:
            errors.append(err)

    if not upload_script:
        errors.append("workflow task upload_release_lookup.input.script is empty")
    else:
        err = require_substrings("upload_release_lookup", upload_script, WORKFLOW_UPLOAD_REQUIRED)
        if err:
            errors.append(err)

    return errors



def validate_dashboard_contract(dashboard) -> list:
    errors = []
    tiles = dashboard.get("content", {}).get("tiles", {})

    for tile_id in QUEUE_TILE_IDS:
        tile = tiles.get(tile_id)
        if not tile:
            errors.append(f"missing queue tile id {tile_id}")
            continue
        query = str(tile.get("query", ""))
        if not query:
            errors.append(f"queue tile {tile_id} has empty query")
            continue
        err = require_substrings(f"queue tile {tile_id}", query, QUEUE_QUERY_REQUIRED)
        if err:
            errors.append(err)

    for tile_id in RISK_TILE_IDS:
        tile = tiles.get(tile_id)
        if not tile:
            errors.append(f"missing risk tile id {tile_id}")
            continue
        query = str(tile.get("query", ""))
        if not query:
            errors.append(f"risk tile {tile_id} has empty query")
            continue
        err = require_substrings(f"risk tile {tile_id}", query, RISK_QUERY_REQUIRED)
        if err:
            errors.append(err)

    return errors



def main() -> int:
    try:
        workflow = load_json(WORKFLOW_PATH)
    except Exception as exc:
        return fail(f"unable to load workflow file: {exc}")

    try:
        dashboard = load_json(DASHBOARD_PATH)
    except Exception as exc:
        return fail(f"unable to load dashboard file: {exc}")

    errors = []
    errors.extend(validate_workflow_contract(workflow))
    errors.extend(validate_dashboard_contract(dashboard))

    if errors:
        print("FAIL: v5 static contract validation failed")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("PASS: v5 workflow/dashboard static contract tokens are present")
    print(
        "  checked workflow tasks: build_lookup_payloads, upload_release_lookup; "
        "dashboard queue tiles: 4,9,14,19,24; risk tiles: 5,10,15,20,25"
    )
    return 0



if __name__ == "__main__":
    sys.exit(main())
