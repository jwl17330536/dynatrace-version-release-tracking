#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

WORKFLOW_PATH = Path("workflows/version-intelligence-sync.v5.workflow.json")
DASHBOARD_V5_PATH = Path(
    "field-asset-library/dashboards/platform/release-tracking-dashboard/release-tracking-dashboard.v5.json"
)
DASHBOARD_V4_LIVE_PATH = Path(
    "field-asset-library/dashboards/platform/release-tracking-dashboard/release-tracking-dashboard.v4.live.json"
)
DASHBOARD_V4_PATH = Path(
    "field-asset-library/dashboards/platform/release-tracking-dashboard/release-tracking-dashboard.v4.json"
)

QUEUE_TILE_IDS = ["4", "9", "14", "19", "24"]
RISK_TILE_IDS = ["5", "10", "15", "20", "25"]

QUEUE_REQUIRED = [
    "action",
    "risk_priority",
    "breaking_now",
    "coming_next",
    "recommended_action",
    "release_link",
    "release_notes_url",
]
RISK_REQUIRED = [
    "triage",
    "breaking_now",
    "coming_next",
    "risk_summary",
    "highlight_summary",
    "recommended_action",
    "release_link",
    "release_notes_url",
]

LOOKUP_SUMMARY_QUERY = (
    'load "/lookups/dt_component_release_status" '
    '| filter is_latest == "true" '
    '| summarize '
    'rows = count(), '
    'components = countDistinct(component), '
    'missing_risk_priority = countIf(risk_priority == "" or risk_priority == "-"), '
    'missing_highlight_focus = countIf(highlight_focus == "" or highlight_focus == "-"), '
    'missing_action_hint = countIf(action_hint == "" or action_hint == "-"), '
    'missing_release_url = countIf(release_url == "" or release_url == "-")'
)


def run_query(query: str):
    cmd = ["dtctl", "query", query, "-o", "json", "--plain"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return False, proc.stderr.strip() or proc.stdout.strip(), None

    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return False, f"non-JSON response: {proc.stdout[:220]}", None

    if payload.get("ok") is False:
        return False, payload.get("error", {}).get("message", "unknown query error"), None

    return True, "", payload.get("records", [])


def is_blank(value) -> bool:
    text = str(value if value is not None else "").strip()
    return text == "" or text == "-"


def load_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text())


def baseline_layout_path() -> Path:
    if DASHBOARD_V4_LIVE_PATH.exists():
        return DASHBOARD_V4_LIVE_PATH
    return DASHBOARD_V4_PATH


def validate_layout_parity(dashboard_v5, baseline_dashboard):
    v5_layouts = dashboard_v5.get("content", {}).get("layouts", {})
    baseline_layouts = baseline_dashboard.get("content", {}).get("layouts", {})

    if not v5_layouts:
        return False, "v5 dashboard layouts missing"
    if not baseline_layouts:
        return False, "baseline dashboard layouts missing"

    if v5_layouts != baseline_layouts:
        changed = []
        all_ids = sorted(set(v5_layouts.keys()) | set(baseline_layouts.keys()), key=lambda x: int(x))
        for tile_id in all_ids:
            if v5_layouts.get(tile_id) != baseline_layouts.get(tile_id):
                changed.append(tile_id)
        return False, f"layout mismatch for tile IDs: {', '.join(changed)}"

    return True, f"layout parity ok ({len(v5_layouts)} tiles)"


def validate_workflow_presence(workflow):
    tasks = workflow.get("tasks", {})
    required_tasks = ["build_lookup_payloads", "upload_release_lookup", "ai_summarize_release_notes"]
    missing = [t for t in required_tasks if t not in tasks]
    if missing:
        return False, f"missing workflow tasks: {', '.join(missing)}"

    build_script = tasks.get("build_lookup_payloads", {}).get("input", {}).get("script", "")
    upload_script = tasks.get("upload_release_lookup", {}).get("input", {}).get("script", "")

    required_tokens = [
        "risk_priority",
        "highlight_focus",
        "action_hint",
        "deriveRiskPriority",
        "deriveHighlightFocus",
        "deriveActionHint",
        "LD:risk_priority",
        "LD:highlight_focus",
        "LD:action_hint",
    ]

    missing_tokens = []
    for token in required_tokens:
        if token not in build_script and token not in upload_script:
            missing_tokens.append(token)

    if missing_tokens:
        return False, f"workflow scripts missing tokens: {', '.join(missing_tokens)}"

    return True, "workflow task/script contract present"


def validate_lookup_enrichment():
    ok, err, records = run_query(LOOKUP_SUMMARY_QUERY)
    if not ok:
        return False, f"lookup summary query failed: {err}"

    if not records:
        return False, "lookup summary query returned no records"

    row = records[0]
    rows = int(str(row.get("rows", "0")))
    components = int(str(row.get("components", "0")))
    missing_risk = int(str(row.get("missing_risk_priority", "0")))
    missing_highlight = int(str(row.get("missing_highlight_focus", "0")))
    missing_action = int(str(row.get("missing_action_hint", "0")))
    missing_url = int(str(row.get("missing_release_url", "0")))

    if rows <= 0:
        return False, "no latest rows in release lookup"
    if components < 5:
        return False, f"expected >=5 components in latest rows, found {components}"
    if missing_risk or missing_highlight or missing_action or missing_url:
        return False, (
            "missing enriched lookup fields: "
            f"risk={missing_risk}, highlight={missing_highlight}, "
            f"action={missing_action}, url={missing_url}"
        )

    return True, f"lookup enrichment ok rows={rows} components={components}"


def validate_actionable_tiles(dashboard):
    tiles = dashboard.get("content", {}).get("tiles", {})

    failures = []
    row_count = 0

    for tile_id in QUEUE_TILE_IDS:
        tile = tiles.get(tile_id)
        if not tile:
            failures.append(f"missing queue tile id {tile_id}")
            continue

        query = str(tile.get("query", "")).strip()
        if not query:
            failures.append(f"queue tile {tile_id} query missing")
            continue

        ok, err, records = run_query(query)
        if not ok:
            failures.append(f"queue tile {tile_id} query failed: {err}")
            continue
        if not records:
            failures.append(f"queue tile {tile_id} returned no rows")
            continue

        row_count += len(records)
        for i, record in enumerate(records, start=1):
            for field in QUEUE_REQUIRED:
                if field not in record:
                    failures.append(f"queue tile {tile_id} row {i} missing field '{field}'")
                elif is_blank(record.get(field)):
                    failures.append(f"queue tile {tile_id} row {i} blank field '{field}'")

    for tile_id in RISK_TILE_IDS:
        tile = tiles.get(tile_id)
        if not tile:
            failures.append(f"missing risk tile id {tile_id}")
            continue

        query = str(tile.get("query", "")).strip()
        if not query:
            failures.append(f"risk tile {tile_id} query missing")
            continue

        ok, err, records = run_query(query)
        if not ok:
            failures.append(f"risk tile {tile_id} query failed: {err}")
            continue
        if not records:
            failures.append(f"risk tile {tile_id} returned no rows")
            continue

        row_count += len(records)
        for i, record in enumerate(records, start=1):
            for field in RISK_REQUIRED:
                if field not in record:
                    failures.append(f"risk tile {tile_id} row {i} missing field '{field}'")
                elif is_blank(record.get(field)):
                    failures.append(f"risk tile {tile_id} row {i} blank field '{field}'")

    if failures:
        return False, failures

    return True, f"actionable tile checks ok queue={len(QUEUE_TILE_IDS)} risk={len(RISK_TILE_IDS)} rows={row_count}"


def main() -> int:
    errors = []

    try:
        workflow = load_json(WORKFLOW_PATH)
    except Exception as exc:
        print(f"FAIL: unable to load workflow file: {exc}")
        return 2

    try:
        dashboard_v5 = load_json(DASHBOARD_V5_PATH)
    except Exception as exc:
        print(f"FAIL: unable to load v5 dashboard file: {exc}")
        return 2

    baseline_path = baseline_layout_path()
    try:
        baseline_dashboard = load_json(baseline_path)
    except Exception as exc:
        print(f"FAIL: unable to load baseline dashboard file: {exc}")
        return 2

    wf_ok, wf_msg = validate_workflow_presence(workflow)
    if wf_ok:
        print(f"PASS: {wf_msg}")
    else:
        errors.append(wf_msg)

    layout_ok, layout_msg = validate_layout_parity(dashboard_v5, baseline_dashboard)
    if layout_ok:
        print(f"PASS: {layout_msg}")
    else:
        errors.append(layout_msg)

    lookup_ok, lookup_msg = validate_lookup_enrichment()
    if lookup_ok:
        print(f"PASS: {lookup_msg}")
    else:
        errors.append(lookup_msg)

    actionable_ok, actionable_msg = validate_actionable_tiles(dashboard_v5)
    if actionable_ok:
        print(f"PASS: {actionable_msg}")
    else:
        if isinstance(actionable_msg, list):
            errors.extend(actionable_msg)
        else:
            errors.append(str(actionable_msg))

    if errors:
        print("FAIL: v5 end-to-end release tracking contract validation failed")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("PASS: v5 end-to-end release tracking contract validation succeeded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
