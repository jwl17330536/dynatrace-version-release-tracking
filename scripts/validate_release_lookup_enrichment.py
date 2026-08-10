#!/usr/bin/env python3
import json
import subprocess
import sys

QUERY = (
    'load "/lookups/dt_component_release_status" '
    '| filter is_latest == "true" '
    '| fields component, released_version, risk_priority, highlight_focus, action_hint, release_url '
    '| summarize '
    'rows = count(), '
    'components = countDistinct(component), '
    'missing_risk_priority = countIf(risk_priority == "" or risk_priority == "-"), '
    'missing_highlight_focus = countIf(highlight_focus == "" or highlight_focus == "-"), '
    'missing_action_hint = countIf(action_hint == "" or action_hint == "-"), '
    'missing_release_url = countIf(release_url == "" or release_url == "-")'
)

EXPECTED_COMPONENTS_MIN = 5


def fail(message: str) -> int:
    print(f"FAIL: {message}")
    return 1


def main() -> int:
    cmd = ["dtctl", "query", QUERY, "-o", "json", "--plain"]
    proc = subprocess.run(cmd, capture_output=True, text=True)

    if proc.returncode != 0:
        out = (proc.stderr or proc.stdout or "").strip()
        return fail(f"dtctl query failed: {out}")

    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return fail(f"non-JSON response from dtctl: {(proc.stdout or '')[:220]}")

    if payload.get("ok") is False:
        message = payload.get("error", {}).get("message", "unknown query error")
        return fail(f"lookup query returned error: {message}")

    records = payload.get("records", [])
    if not records:
        return fail("lookup query returned zero records for latest releases")

    row = records[0]
    rows = int(str(row.get("rows", "0")))
    components = int(str(row.get("components", "0")))
    missing_risk = int(str(row.get("missing_risk_priority", "0")))
    missing_highlight = int(str(row.get("missing_highlight_focus", "0")))
    missing_action = int(str(row.get("missing_action_hint", "0")))
    missing_url = int(str(row.get("missing_release_url", "0")))

    print(
        "Latest rows="
        f"{rows} components={components} missing_risk_priority={missing_risk} "
        f"missing_highlight_focus={missing_highlight} missing_action_hint={missing_action} "
        f"missing_release_url={missing_url}"
    )

    if rows <= 0:
        return fail("no latest release rows available")

    if components < EXPECTED_COMPONENTS_MIN:
        return fail(
            f"expected at least {EXPECTED_COMPONENTS_MIN} components in latest rows, found {components}"
        )

    if missing_risk > 0 or missing_highlight > 0 or missing_action > 0 or missing_url > 0:
        return fail("enriched lookup fields are missing values in latest rows")

    print("PASS: release lookup enrichment fields are populated for latest rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
