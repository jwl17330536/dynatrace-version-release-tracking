#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

DASHBOARD_PATH = Path("field-asset-library/dashboards/platform/release-tracking-dashboard/release-tracking-dashboard.v2.json")


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

    records = payload.get("records", [])
    return True, "", len(records)


def main() -> int:
    if not DASHBOARD_PATH.exists():
        print(f"ERROR: missing dashboard file {DASHBOARD_PATH}")
        return 2

    dashboard = json.loads(DASHBOARD_PATH.read_text())
    tiles = dashboard.get("content", {}).get("tiles", {})

    data_tiles = []
    for tile_id, tile in tiles.items():
        if tile.get("type") == "data":
            data_tiles.append((tile_id, tile.get("title", ""), tile.get("query", "")))

    if not data_tiles:
        print("ERROR: no data tiles found")
        return 2

    failures = 0
    print(f"Validating {len(data_tiles)} data tile queries from {DASHBOARD_PATH}")
    for tile_id, title, query in sorted(data_tiles, key=lambda x: int(x[0])):
        ok, err, rec_count = run_query(query)
        if ok:
            print(f"PASS tile {tile_id:>2} | records={rec_count:<4} | {title}")
        else:
            failures += 1
            print(f"FAIL tile {tile_id:>2} | {title}")
            print(f"  {err}")

    if failures:
        print(f"\nValidation completed with {failures} failing tile query(ies).")
        return 1

    print("\nValidation completed successfully. All tile queries passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
