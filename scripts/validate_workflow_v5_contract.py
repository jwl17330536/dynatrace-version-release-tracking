#!/usr/bin/env python3
import json
import sys
from pathlib import Path

WORKFLOW_PATH = Path("workflows/version-intelligence-sync.v5.workflow.json")


def fail(msg: str) -> int:
    print(f"FAIL: {msg}")
    return 1


def warn(msg: str) -> None:
    print(f"WARN: {msg}")


def main() -> int:
    if not WORKFLOW_PATH.exists():
        return fail(f"missing file {WORKFLOW_PATH}")

    try:
        workflow = json.loads(WORKFLOW_PATH.read_text())
    except json.JSONDecodeError as exc:
        return fail(f"invalid JSON: {exc}")

    title = str(workflow.get("title", "")).strip()
    if title != "Version Intelligence Sync v5":
        return fail(f"unexpected title: {title}")

    if workflow.get("isDeployed") is not True:
        return fail("workflow isDeployed is not true")

    tasks = workflow.get("tasks", {})

    init_script = (
        tasks
        .get("initialize_workflow_context", {})
        .get("input", {})
        .get("script", "")
    )
    if not init_script:
        return fail("missing initialize_workflow_context task or script")

    init_required = [
        'credentialVaultClient.getCredentialsDetails',
        'const apiTokenVaultId = readInput(ex, "apiTokenVaultId"',
        'const rumTokenVaultId = readInput(ex, "rumTokenVaultId"',
        'api_token: apiToken',
        'rum_token: rumToken'
    ]
    for marker in init_required:
        if marker not in init_script:
            return fail(f"missing expected marker in initialize script: {marker}")

    rum_task = (
        tasks
        .get("rum_collect_runtime_versions", {})
        .get("input", {})
        .get("script", "")
    )
    rum_script = str(rum_task)

    required = [
        'let RUM_TOKEN_VAULT_ID = "";',
        'const ctx = await result("initialize_workflow_context");',
        'loadTokenFromContext(ctx?.rum_token, ctx?.rum_token_vault_id);',
        'RUM_TOKEN_VAULT_ID = String(vaultId || "").trim() || "unknown_vault_id";',
        '${RUM_TOKEN_VAULT_ID || "unknown_vault_id"}'
    ]
    for marker in required:
        if marker not in rum_script:
            return fail(f"missing expected marker in rum script: {marker}")

    if 'resolveRumTokenVaultId' in rum_script:
        return fail("legacy local rumTokenVaultId resolver still present in RUM script")

    for task_name in [
        "collect_saas_current_version",
        "collect_release_indexes",
        "rum_collect_runtime_versions",
        "collect_oneagent_runtime_distribution",
        "collect_activegate_runtime_distribution",
        "collect_operator_runtime_distribution",
        "collect_edgeconnect_runtime_distribution"
    ]:
        predecessors = tasks.get(task_name, {}).get("predecessors", [])
        if "initialize_workflow_context" not in predecessors:
            return fail(f"task {task_name} is missing initialize_workflow_context predecessor")

    schedule = workflow.get("trigger", {}).get("schedule", {})
    if schedule.get("isActive") is not True:
        warn("schedule.isActive is false (manual/control mode)")

    inputs = schedule.get("inputs", {})
    api_vault = str(inputs.get("apiTokenVaultId", {}).get("value", "")).strip()
    rum_vault = str(inputs.get("rumTokenVaultId", {}).get("value", "")).strip()
    if api_vault and rum_vault and api_vault == rum_vault:
        warn("apiTokenVaultId and rumTokenVaultId use same vault value; verify least-privilege intent")

    print("PASS: workflow v5 contract checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
