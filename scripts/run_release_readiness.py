#!/usr/bin/env python3
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path


def run_step(name, cmd):
    started = dt.datetime.utcnow().isoformat() + "Z"
    proc = subprocess.run(cmd, capture_output=True, text=True)
    finished = dt.datetime.utcnow().isoformat() + "Z"

    output = ((proc.stdout or "") + (proc.stderr or "")).strip()

    return {
        "name": name,
        "command": cmd,
        "startedAt": started,
        "finishedAt": finished,
        "exitCode": proc.returncode,
        "ok": proc.returncode == 0,
        "output": output,
    }


def render_markdown(report):
    lines = []
    lines.append("# Release Readiness Report")
    lines.append("")
    lines.append(f"- Generated at: {report.get('generatedAt')}")
    lines.append(f"- Overall OK: {report.get('ok')}")
    lines.append(f"- Steps Passed: {report.get('passedSteps')}")
    lines.append(f"- Steps Failed: {report.get('failedSteps')}")
    lines.append("")
    lines.append("## Steps")

    for step in report.get("steps", []):
        status = "PASS" if step.get("ok") else "FAIL"
        lines.append(f"- {status}: {step.get('name')}")
        lines.append(f"  - Command: {' '.join(step.get('command', []))}")
        lines.append(f"  - Exit Code: {step.get('exitCode')}")

    return "\n".join(lines) + "\n"


def write_report(report_dir, report):
    report_dir.mkdir(parents=True, exist_ok=True)

    stamp = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    json_path = report_dir / f"release-readiness.{stamp}.json"
    md_path = report_dir / f"release-readiness.{stamp}.md"

    latest_json = report_dir / "release-readiness.latest.json"
    latest_md = report_dir / "release-readiness.latest.md"

    json_path.write_text(json.dumps(report, indent=2) + "\n")
    md_path.write_text(render_markdown(report))

    latest_json.write_text(json.dumps(report, indent=2) + "\n")
    latest_md.write_text(render_markdown(report))

    return json_path, md_path, latest_json, latest_md


def main():
    steps = [
        ("Self and static smoke gate", ["make", "ci-check"]),
        ("CI-static preflight report", ["make", "preflight-static"]),
    ]

    results = []
    for name, cmd in steps:
        result = run_step(name, cmd)
        results.append(result)

    failed = [item for item in results if not item["ok"]]

    report = {
        "generatedAt": dt.datetime.utcnow().isoformat() + "Z",
        "ok": len(failed) == 0,
        "passedSteps": len(results) - len(failed),
        "failedSteps": len(failed),
        "steps": results,
    }

    report_dir = Path("reports/validation")
    json_path, md_path, latest_json, latest_md = write_report(report_dir, report)

    print(f"Release readiness JSON report: {json_path}")
    print(f"Release readiness Markdown report: {md_path}")
    print(f"Release readiness latest JSON: {latest_json}")
    print(f"Release readiness latest Markdown: {latest_md}")
    print(f"Release readiness result: {'PASS' if report['ok'] else 'FAIL'}")

    if failed:
        print("\nFailed steps:")
        for item in failed:
            print(f"- {item['name']} (exit={item['exitCode']})")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
