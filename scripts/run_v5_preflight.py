#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_WORKFLOW_ID = "827008e7-f74d-455a-8324-72629ff6225f"


def run_cmd(cmd):
    proc = subprocess.run(cmd, capture_output=True, text=True)
    out = (proc.stdout or "")
    err = (proc.stderr or "")
    return proc.returncode, out, err


def run_json_cmd(cmd, label):
    code, out, err = run_cmd(cmd)
    if code != 0:
        message = (err or out).strip()
        raise RuntimeError(f"{label} failed: {message}")
    try:
        return json.loads(out)
    except json.JSONDecodeError as exc:
        snippet = (out or "")[:280]
        raise RuntimeError(f"{label} returned non-JSON output: {snippet}") from exc


def start_workflow_execution(workflow_id: str) -> str:
    code, out, err = run_cmd(["dtctl", "exec", "workflow", workflow_id, "-o", "json", "--plain"])
    text = (out or "") + (err or "")
    if code != 0:
        raise RuntimeError(f"workflow execution start failed: {text.strip()}")

    for line in text.splitlines():
        line = line.strip()
        if line.lower().startswith("execution id:"):
            return line.split(":", 1)[1].strip()

    # fallback if output shape changes and is JSON
    try:
        payload = json.loads(out)
        exec_id = str(payload.get("id", "")).strip()
        if exec_id:
            return exec_id
    except Exception:
        pass

    raise RuntimeError(f"unable to parse execution id from output: {text.strip()}")


def wait_for_execution(execution_id: str, timeout_sec: int, poll_sec: int):
    deadline = time.time() + timeout_sec
    last_payload = None

    while time.time() < deadline:
        payload = run_json_cmd(
            ["dtctl", "get", "wfe", execution_id, "-o", "json", "--plain"],
            "dtctl get wfe",
        )
        last_payload = payload
        state = str(payload.get("state", "")).upper()
        if state in {"SUCCESS", "FAILED", "CANCELED", "TIMEOUT", "ERROR"}:
            return payload
        time.sleep(poll_sec)

    state = str((last_payload or {}).get("state", "unknown"))
    raise TimeoutError(
        f"workflow execution {execution_id} did not reach terminal state within {timeout_sec}s (last state={state})"
    )


def run_validation(profile: str):
    payload = run_json_cmd(
        ["python3", "scripts/run_validation_suite.py", "--profile", profile, "--json"],
        "validation suite",
    )
    return payload


def ensure_parent(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)


def build_markdown_report(started_at, finished_at, profile, execution, validation_payload):
    summary = validation_payload.get("summary", {})
    checks = validation_payload.get("checks", [])

    lines = []
    lines.append("# Release Tracking v5 Preflight Report")
    lines.append("")
    lines.append(f"- Started at: {started_at}")
    lines.append(f"- Finished at: {finished_at}")
    lines.append(f"- Validation profile: {profile}")
    if execution:
        lines.append(f"- Workflow execution ID: {execution.get('id', '-')}")
        lines.append(f"- Workflow state: {execution.get('state', '-')}")
        lines.append(f"- Workflow runtime: {execution.get('runtime', '-')}")
    else:
        lines.append("- Workflow execution: not requested")

    lines.append("")
    lines.append("## Summary")
    lines.append(f"- PASS: {summary.get('pass', 0)}")
    lines.append(f"- SKIP: {summary.get('skip', 0)}")
    lines.append(f"- FAIL: {summary.get('fail', 0)}")
    lines.append(f"- Overall OK: {validation_payload.get('ok', False)}")
    lines.append("")
    lines.append("## Checks")

    for check in checks:
        status = str(check.get("status", "unknown")).upper()
        name = str(check.get("name", "unnamed"))
        lines.append(f"- {status}: {name}")

    return "\n".join(lines) + "\n"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run release-tracking v5 preflight: optional workflow execution + validation profile + reports"
    )
    parser.add_argument("--profile", choices=["all", "v5", "ci-static"], default="v5", help="validation profile")
    parser.add_argument(
        "--execute-workflow",
        action="store_true",
        help="execute workflow v5 before running validation",
    )
    parser.add_argument("--workflow-id", default=DEFAULT_WORKFLOW_ID, help="workflow id used with --execute-workflow")
    parser.add_argument("--timeout-sec", type=int, default=240, help="workflow execution wait timeout seconds")
    parser.add_argument("--poll-sec", type=int, default=5, help="workflow execution polling interval seconds")
    parser.add_argument(
        "--out-json",
        default="reports/validation/v5-preflight.latest.json",
        help="output JSON report path",
    )
    parser.add_argument(
        "--out-md",
        default="reports/validation/v5-preflight.latest.md",
        help="output Markdown report path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started_at = dt.datetime.utcnow().isoformat() + "Z"

    execution_payload = None

    try:
        if args.execute_workflow:
            execution_id = start_workflow_execution(args.workflow_id)
            execution_payload = wait_for_execution(execution_id, args.timeout_sec, args.poll_sec)
            if str(execution_payload.get("state", "")).upper() != "SUCCESS":
                raise RuntimeError(
                    f"workflow execution {execution_id} ended in state {execution_payload.get('state')}"
                )

        validation_payload = run_validation(args.profile)

        finished_at = dt.datetime.utcnow().isoformat() + "Z"
        report_payload = {
            "ok": bool(validation_payload.get("ok", False)),
            "startedAt": started_at,
            "finishedAt": finished_at,
            "profile": args.profile,
            "workflowExecution": execution_payload,
            "validation": validation_payload,
        }

        out_json = Path(args.out_json)
        out_md = Path(args.out_md)
        ensure_parent(out_json)
        ensure_parent(out_md)

        out_json.write_text(json.dumps(report_payload, indent=2) + "\n")
        out_md.write_text(
            build_markdown_report(started_at, finished_at, args.profile, execution_payload, validation_payload)
        )

        print(f"Preflight JSON report: {out_json}")
        print(f"Preflight Markdown report: {out_md}")
        print(f"Preflight result: {'PASS' if report_payload['ok'] else 'FAIL'}")

        return 0 if report_payload["ok"] else 1
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
