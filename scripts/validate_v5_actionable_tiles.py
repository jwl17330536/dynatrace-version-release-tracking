#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

DASHBOARD_PATH = Path(
    "field-asset-library/dashboards/platform/release-tracking-dashboard/release-tracking-dashboard.v5.json"
)

QUEUE_REQUIRED_FIELDS = [
    "action",
    "risk_priority",
    "breaking_now",
    "coming_next",
    "recommended_action",
    "release_link",
    "release_notes_url",
]

RISK_REQUIRED_FIELDS = [
    "triage",
    "breaking_now",
    "coming_next",
    "risk_summary",
    "highlight_summary",
    "recommended_action",
    "release_link",
    "release_notes_url",
]



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
        return False, payload.get("error", {}).get("message", "unknown query error"), None

    return True, "", payload.get("records", [])



def is_blank(value) -> bool:
    text = str(value if value is not None else "").strip()
    return text == "" or text == "-"



def main() -> int:
    if not DASHBOARD_PATH.exists():
        print(f"ERROR: missing dashboard file {DASHBOARD_PATH}")
        return 2

    dashboard = json.loads(DASHBOARD_PATH.read_text())
    tiles = dashboard.get("content", {}).get("tiles", {})

    queue_tiles = []
    risk_tiles = []

    for tile_id, tile in tiles.items():
        if tile.get("type") != "data":
            continue
        title = str(tile.get("title", "")).strip()
        query = str(tile.get("query", "")).strip()
        if not query:
            continue

        if "Upgrade Queue" in title:
            queue_tiles.append((tile_id, title, query))
        elif "Risk and Highlights" in title:
            risk_tiles.append((tile_id, title, query))

    queue_tiles = sorted(queue_tiles, key=lambda t: int(t[0]))
    risk_tiles = sorted(risk_tiles, key=lambda t: int(t[0]))

    if len(queue_tiles) != 5 or len(risk_tiles) != 5:
        print(
            "FAIL: expected 5 queue tiles and 5 risk tiles in v5 dashboard, "
            f"found queue={len(queue_tiles)} risk={len(risk_tiles)}"
        )
        return 1

    failures = []
    total_rows = 0

    for tile_id, title, query in queue_tiles:
        ok, err, records = run_query(query)
        if not ok:
            failures.append(f"queue tile {tile_id} ({title}) query failed: {err}")
            continue

        if not records:
            failures.append(f"queue tile {tile_id} ({title}) returned no records")
            continue

        total_rows += len(records)
        for idx, record in enumerate(records, start=1):
            for field in QUEUE_REQUIRED_FIELDS:
                if field not in record:
                    failures.append(
                        f"queue tile {tile_id} ({title}) row {idx} missing field '{field}'"
                    )
                elif is_blank(record.get(field)):
                    failures.append(
                        f"queue tile {tile_id} ({title}) row {idx} has blank field '{field}'"
                    )

    for tile_id, title, query in risk_tiles:
        ok, err, records = run_query(query)
        if not ok:
            failures.append(f"risk tile {tile_id} ({title}) query failed: {err}")
            continue

        if not records:
            failures.append(f"risk tile {tile_id} ({title}) returned no records")
            continue

        total_rows += len(records)
        for idx, record in enumerate(records, start=1):
            for field in RISK_REQUIRED_FIELDS:
                if field not in record:
                    failures.append(
                        f"risk tile {tile_id} ({title}) row {idx} missing field '{field}'"
                    )
                elif is_blank(record.get(field)):
                    failures.append(
                        f"risk tile {tile_id} ({title}) row {idx} has blank field '{field}'"
                    )

    print(
        "Checked v5 actionable tiles: "
        f"queue={len(queue_tiles)} risk={len(risk_tiles)} total_rows={total_rows}"
    )

    if failures:
        print("FAIL: v5 actionable tile validation failed")
        for item in failures:
            print(f"  - {item}")
        return 1

    print("PASS: v5 actionable queue/risk tiles include required populated fields")
    return 0


if __name__ == "__main__":
    sys.exit(main())
