# Version Alignment Policy

This policy governs Version Intelligence workflow and dashboard changes.

## Core policy

1. Workflow and dashboard versions move in lockstep.
2. Workflow `vN` updates dashboard `vN` only.
3. New behavior requires a new pair: workflow `vN+1` and dashboard `vN+1`.
4. Never overwrite prior versions for iterative feature changes.
5. Keep only one active scheduled Version Intelligence workflow.

## Required change sequence

1. Export live workflow `vN` and dashboard `vN`.
2. Create new dashboard `vN+1` from live `vN` layout.
3. Clone workflow to `vN+1` and retarget dashboard ID to `vN+1`.
4. Apply new workflow.
5. Enable `vN+1` schedule.
6. Disable `vN` schedule.
7. Verify only one active schedule remains.

## Verification checklist

1. Workflow title and file name match `vN+1`.
2. Dashboard name and file name match `vN+1`.
3. Workflow input key and resolved ID point to dashboard `vN+1`.
4. No stale references to earlier version names in update-task keys/messages.
5. Latest execution updates dashboard `vN+1` timestamp and key markdown headers.
6. For manual `dtctl exec`, pass required inputs using `--params` (manual execution does not inherit schedule static inputs).
7. Re-verify Workflow Guide after apply (guide may not round-trip in this tenant's export payloads).

## Security requirements

1. Do not commit runtime bearer token literals.
2. Use placeholders in committed workflow files.
3. Supply credentials at runtime (vault or secure environment injection).
4. Prefer credential-vault IDs over raw token inputs for scheduled workflows.
5. Verify placeholder token fields cannot override a configured vault-backed credential.
