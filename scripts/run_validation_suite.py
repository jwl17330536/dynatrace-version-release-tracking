#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys

ALL_CHECKS = [
    ("Workflow v5 contract checks", ["python3", "scripts/validate_workflow_v5_contract.py"]),
    ("Workflow/dashboard v5 static contract checks", ["python3", "scripts/validate_v5_contract_static.py"]),
    ("Release tracking v5 end-to-end checks", ["python3", "scripts/validate_release_tracking_v5_e2e.py"]),
    ("Release lookup enrichment checks", ["python3", "scripts/validate_release_lookup_enrichment.py"]),
    (
        "Dashboard v4 query smoke tests",
        [
            "python3",
            "scripts/validate_dashboard_queries.py",
            "field-asset-library/dashboards/platform/release-tracking-dashboard/release-tracking-dashboard.v4.json",
        ],
    ),
    (
        "Dashboard v5 query smoke tests",
        [
            "python3",
            "scripts/validate_dashboard_queries.py",
            "field-asset-library/dashboards/platform/release-tracking-dashboard/release-tracking-dashboard.v5.json",
        ],
    ),
    ("Dashboard v5 actionable tile checks", ["python3", "scripts/validate_v5_actionable_tiles.py"]),
    ("Dashboard v5 narrative quality checks", ["python3", "scripts/validate_v5_narrative_quality.py"]),
    ("Dashboard layout parity checks", ["python3", "scripts/validate_dashboard_layout_parity.py"]),
    ("Upgrade queue semantic alignment", ["python3", "scripts/validate_upgrade_queue_semantics.py"]),
    ("Upgrade queue red-path ranking", ["python3", "scripts/validate_upgrade_queue_red_path.py"]),
]

V5_PROFILE_CHECKS = [
    ("Workflow v5 contract checks", ["python3", "scripts/validate_workflow_v5_contract.py"]),
    ("Workflow/dashboard v5 static contract checks", ["python3", "scripts/validate_v5_contract_static.py"]),
    ("Release tracking v5 end-to-end checks", ["python3", "scripts/validate_release_tracking_v5_e2e.py"]),
    ("Release lookup enrichment checks", ["python3", "scripts/validate_release_lookup_enrichment.py"]),
    (
        "Dashboard v5 query smoke tests",
        [
            "python3",
            "scripts/validate_dashboard_queries.py",
            "field-asset-library/dashboards/platform/release-tracking-dashboard/release-tracking-dashboard.v5.json",
        ],
    ),
    ("Dashboard v5 actionable tile checks", ["python3", "scripts/validate_v5_actionable_tiles.py"]),
    ("Dashboard v5 narrative quality checks", ["python3", "scripts/validate_v5_narrative_quality.py"]),
    ("Dashboard layout parity checks", ["python3", "scripts/validate_dashboard_layout_parity.py"]),
]

CI_STATIC_PROFILE_CHECKS = [
    ("Workflow v5 contract checks", ["python3", "scripts/validate_workflow_v5_contract.py"]),
    ("Workflow/dashboard v5 static contract checks", ["python3", "scripts/validate_v5_contract_static.py"]),
    ("Dashboard layout parity checks", ["python3", "scripts/validate_dashboard_layout_parity.py"]),
]


def run_check(name, cmd, quiet=False):
    if not quiet:
        print(f"\n=== {name} ===")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    output = (proc.stdout or "") + (proc.stderr or "")
    output = output.strip()
    if output and not quiet:
        print(output)

    status = "fail"
    if proc.returncode == 0:
        # red-path validator can return 0 with SKIP when no backlog rows exist yet
        if "SKIP:" in output:
            status = "skip"
        else:
            status = "pass"

    return {
        "name": name,
        "cmd": cmd,
        "status": status,
        "returncode": proc.returncode,
        "output": output,
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Run repository validation suite")
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON summary instead of formatted text",
    )
    parser.add_argument(
        "--profile",
        choices=["all", "v5", "ci-static"],
        default="all",
        help="validation profile to run (default: all)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = {"pass": 0, "skip": 0, "fail": 0}
    results = []
    if args.profile == "v5":
        checks = V5_PROFILE_CHECKS
    elif args.profile == "ci-static":
        checks = CI_STATIC_PROFILE_CHECKS
    else:
        checks = ALL_CHECKS

    for name, cmd in checks:
        result = run_check(name, cmd, quiet=args.json)
        results.append(result)
        summary[result["status"]] += 1

    if args.json:
        payload = {
            "ok": summary["fail"] == 0,
            "profile": args.profile,
            "summary": summary,
            "checks": results,
        }
        print(json.dumps(payload, indent=2))
    else:
        print("\n=== Validation Suite Summary ===")
        print(f"PASS: {summary['pass']}")
        print(f"SKIP: {summary['skip']}")
        print(f"FAIL: {summary['fail']}")

    if summary["fail"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
