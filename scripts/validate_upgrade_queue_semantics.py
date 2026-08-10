#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

DASHBOARD_PATH = Path("field-asset-library/dashboards/platform/release-tracking-dashboard/release-tracking-dashboard.v4.json")

EXPECTED_QUERY = (
    'load "/lookups/dt_component_release_status" '
    '| filter is_latest == "true" and released_version != "" and released_version != "Not yet published" '
    '| fields component, running_version, is_newer_than_running '
    '| fieldsAdd expected_action = if(is_newer_than_running == "true", "newer", else: if(running_version == "" or running_version == "-", "unknown", else: "aligned")) '
    '| fields component, expected_action '
    '| sort component asc'
)


def run_query(query: str):
    cmd = ["dtctl", "query", query, "-o", "json", "--plain"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return False, proc.stderr.strip() or proc.stdout.strip(), None

    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return False, f"Non-JSON response: {proc.stdout[:200]}", None

    if payload.get("ok") is False:
        return False, payload.get("error", {}).get("message", "unknown query error"), payload

    return True, "", payload.get("records", [])


def action_to_code(action: str):
    text = str(action or "").lower()
    if "newer available" in text:
        return "newer"
    if "runtime unknown" in text:
        return "unknown"
    if "aligned" in text:
        return "aligned"
    return "unknown_action_text"


def title_to_component(title: str):
    key = str(title or "").split(" ", 1)[0].strip().lower()
    mapping = {
        "saas": "saas",
        "activegate": "activegate",
        "oneagent": "oneagent",
        "operator": "operator",
        "edge": "edgeconnect",
    }
    return mapping.get(key, "")


def load_queue_tiles():
    if not DASHBOARD_PATH.exists():
        raise FileNotFoundError(f"missing dashboard file: {DASHBOARD_PATH}")

    dashboard = json.loads(DASHBOARD_PATH.read_text())
    tiles = dashboard.get("content", {}).get("tiles", {})
    out = []
    for tile_id, tile in tiles.items():
        title = str(tile.get("title", "")).strip()
        if tile.get("type") != "data" or "Upgrade Queue" not in title:
            continue

        query = str(tile.get("query", "")).strip()
        component = title_to_component(title)
        if not query:
            raise ValueError(f"missing query for tile {tile_id}")
        if not component:
            raise ValueError(f"unable to infer component from tile title: {title}")
        out.append((tile_id, title, component, query))

    if not out:
        raise ValueError("no Upgrade Queue tiles found")
    return sorted(out, key=lambda x: int(x[0]))


def to_component_map(records, field_name: str):
    out = {}
    for row in records:
        component = str(row.get("component", "")).strip()
        value = str(row.get(field_name, "")).strip()
        if component:
            out[component] = value
    return out


def main() -> int:
    try:
        queue_tiles = load_queue_tiles()
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 2

    tile_action_map = {}
    total_rows = 0
    for tile_id, title, component, tile_query in queue_tiles:
        ok, err, tile_records = run_query(tile_query)
        if not ok:
            print(f"ERROR: tile query failed for tile {tile_id} ({title})")
            print(f"  {err}")
            return 2

        total_rows += len(tile_records)
        if not tile_records:
            tile_action_map[component] = "missing"
            continue

        first = tile_records[0]
        tile_action_map[component] = action_to_code(first.get("action", ""))

    ok, err, expected_records = run_query(EXPECTED_QUERY)
    if not ok:
        print("ERROR: expected semantics query failed")
        print(f"  {err}")
        return 2

    expected_action_map = to_component_map(expected_records, "expected_action")

    components = sorted(set(tile_action_map.keys()) | set(expected_action_map.keys()))
    mismatches = []

    for component in components:
        tile_action = tile_action_map.get(component, "missing")
        expected_action = expected_action_map.get(component, "missing")
        if tile_action != expected_action:
            mismatches.append((component, expected_action, tile_action))

    print(f"Queue tiles: {len(queue_tiles)} | Tile rows: {total_rows} | Expected rows: {len(expected_records)} | Components compared: {len(components)}")

    if mismatches:
        print("FAIL: v4 queue semantics drift detected")
        for component, expected_action, tile_action in mismatches:
            print(f"  - {component}: expected={expected_action}, tile={tile_action}")
        return 1

    counts = {"newer": 0, "unknown": 0, "aligned": 0}
    for action in tile_action_map.values():
        if action in counts:
            counts[action] += 1

    print("PASS: v4 queue semantics match lookup-derived expectations.")
    print(f"  newer={counts['newer']} unknown={counts['unknown']} aligned={counts['aligned']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
