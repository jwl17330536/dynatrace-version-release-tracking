#!/usr/bin/env python3
import json
import sys
from pathlib import Path

V5_PATH = Path(
    "field-asset-library/dashboards/platform/release-tracking-dashboard/release-tracking-dashboard.v5.json"
)
V4_LIVE_PATH = Path(
    "field-asset-library/dashboards/platform/release-tracking-dashboard/release-tracking-dashboard.v4.live.json"
)
V4_PATH = Path(
    "field-asset-library/dashboards/platform/release-tracking-dashboard/release-tracking-dashboard.v4.json"
)


def load_layouts(path: Path):
    payload = json.loads(path.read_text())
    return payload.get("content", {}).get("layouts", {})


def main() -> int:
    if not V5_PATH.exists():
        print(f"ERROR: missing dashboard file {V5_PATH}")
        return 2

    if V4_LIVE_PATH.exists():
        baseline = V4_LIVE_PATH
    elif V4_PATH.exists():
        baseline = V4_PATH
        print("SKIP: live v4 baseline file not found; using v4.json fallback for parity check")
    else:
        print("ERROR: no baseline dashboard file found for parity check")
        return 2

    v5_layouts = load_layouts(V5_PATH)
    baseline_layouts = load_layouts(baseline)

    if not v5_layouts:
        print("ERROR: v5 dashboard has no layouts")
        return 2
    if not baseline_layouts:
        print(f"ERROR: baseline dashboard {baseline} has no layouts")
        return 2

    if v5_layouts != baseline_layouts:
        changed = []
        all_ids = sorted(set(v5_layouts.keys()) | set(baseline_layouts.keys()), key=lambda x: int(x))
        for tile_id in all_ids:
            if v5_layouts.get(tile_id) != baseline_layouts.get(tile_id):
                changed.append(tile_id)

        print("FAIL: dashboard layout parity check failed")
        print(f"  Baseline: {baseline}")
        print(f"  Changed layout tile IDs: {', '.join(changed)}")
        return 1

    print("PASS: dashboard layout parity check succeeded")
    print(f"  Baseline: {baseline}")
    print(f"  Tile layouts compared: {len(v5_layouts)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
