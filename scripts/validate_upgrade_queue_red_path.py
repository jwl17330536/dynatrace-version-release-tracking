#!/usr/bin/env python3
import json
import subprocess
import sys
from collections import defaultdict

QUERY = (
    'load "/lookups/dt_component_release_status" '
    '| filter is_newer_than_running == "true" '
    '| fields component, released_version, newer_than_running_rank, running_version, release_url, fetched_at '
    '| sort component asc, newer_than_running_rank asc'
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


def to_rank(value: str):
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def validate(records):
    if not records:
        print("SKIP: no is_newer_than_running=true rows found in release lookup.")
        print("      Red-path ranking will be validated automatically once backlog rows appear.")
        return 0

    errors = []
    by_component = defaultdict(list)

    for row in records:
        component = str(row.get("component", "")).strip() or "unknown"
        rank = to_rank(row.get("newer_than_running_rank", ""))
        running_version = str(row.get("running_version", "")).strip()
        released_version = str(row.get("released_version", "")).strip()

        if rank is None or rank < 1:
            errors.append(
                f"{component} {released_version}: invalid newer_than_running_rank={row.get('newer_than_running_rank')}"
            )
            continue

        if running_version in ("", "-"):
            errors.append(
                f"{component} {released_version}: missing running_version for backlog row"
            )

        by_component[component].append(rank)

    for component, ranks in by_component.items():
        ordered = sorted(ranks)
        expected = list(range(1, len(ordered) + 1))
        if ordered != expected:
            errors.append(f"{component}: non-contiguous ranks {ordered}, expected {expected}")

    if errors:
        print("FAIL: red-path ranking validation failed")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("PASS: red-path rows present and ranking is contiguous per component.")
    for component in sorted(by_component.keys()):
        print(f"  - {component}: ranks {sorted(by_component[component])}")
    return 0


def main() -> int:
    ok, err, records = run_query(QUERY)
    if not ok:
        print("ERROR: unable to query release lookup")
        print(f"  {err}")
        return 2

    print(f"Found {len(records)} red-path row(s) (is_newer_than_running=true).")
    return validate(records)


if __name__ == "__main__":
    sys.exit(main())
