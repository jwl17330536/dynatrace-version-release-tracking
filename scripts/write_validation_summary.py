#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Optional


def build_summary_lines(title: str, report_path: Path) -> List[str]:
    lines = [f"## {title}", ""]

    if not report_path.exists():
        lines.append("- Result: report file missing (validation step likely failed before report generation)")
        return lines

    try:
        payload = json.loads(report_path.read_text())
    except Exception as exc:
        lines.append(f"- Result: unable to parse report JSON ({exc})")
        lines.append(f"- Report path: {report_path}")
        return lines

    summary = payload.get("summary", {})
    lines.extend(
        [
            f"- Profile: {payload.get('profile')}",
            f"- OK: {payload.get('ok')}",
            f"- Pass: {summary.get('pass', 0)}",
            f"- Skip: {summary.get('skip', 0)}",
            f"- Fail: {summary.get('fail', 0)}",
            "",
            "### Checks",
        ]
    )

    for check in payload.get("checks", []):
        status = str(check.get("status", "unknown")).upper()
        name = str(check.get("name", "unknown check"))
        lines.append(f"- {status}: {name}")

    return lines


def resolve_summary_target(summary_path_arg: str) -> Optional[Path]:
    if summary_path_arg:
        return Path(summary_path_arg)

    env_summary = os.environ.get("GITHUB_STEP_SUMMARY", "").strip()
    if env_summary:
        return Path(env_summary)

    return None


def parse_args():
    parser = argparse.ArgumentParser(description="Write markdown summary from validation JSON report")
    parser.add_argument("--report-path", required=True, help="path to validation JSON report")
    parser.add_argument("--title", required=True, help="markdown heading text")
    parser.add_argument("--summary-path", default="", help="optional output markdown path (defaults to GITHUB_STEP_SUMMARY when available)")
    parser.add_argument("--strict", action="store_true", help="exit non-zero on summary write errors")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report_path = Path(args.report_path)
    lines = build_summary_lines(args.title, report_path)
    body = "\n".join(lines) + "\n"

    target = resolve_summary_target(args.summary_path)
    if target is None:
        print(body, end="")
        return 0

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as handle:
            handle.write(body)
    except Exception as exc:
        print(f"WARN: failed to write summary: {exc}", file=sys.stderr)
        return 1 if args.strict else 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
