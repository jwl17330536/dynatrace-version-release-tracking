# AGENTS

This repository contains the canonical Version Intelligence release-tracking assets for Dynatrace workflows and dashboards.

## Non-negotiable rules

1. Always version workflow and dashboard together.
2. Workflow `vN` must update dashboard `vN` only.
3. Never modify previous versions in place for behavior changes.
4. Every behavior iteration must create a new `vN+1` pair.
5. Keep exactly one active Version Intelligence workflow schedule.
6. After enabling `vN+1`, disable `vN`.
7. Keep committed assets secret-safe (no live token literals).

## Workflow guide requirement

Every workflow version must include an operator guide in Dynatrace UI Workflow Guide.

Source markdown for guide content is maintained in:

- `docs/WORKFLOW_GUIDE_V10.md`

If tooling cannot serialize guide content, add it manually in Workflow options after apply.

In this tenant, `dtctl get workflow` currently does not round-trip `guide`; always verify and re-paste guide markdown after apply.

## Publishing expectations

This repository is intended for public reuse and iteration.

1. Keep tenant-specific values as placeholders.
2. Keep setup and troubleshooting instructions current.
3. Preserve previous version files for rollback traceability.

## Public Standards Alignment

1. Keep one canonical end-user install path in `README.md` and `QUICK_START.md`.
2. Keep contributor-only workflows in `CONTRIBUTING.md`.
3. Keep local/private scaffolding untracked (`.local.*`, `local-only/`, private notes).
4. Keep this repository standalone with no required dependency on private/internal sibling repos.
5. Keep strict PII/secret checks and required branch protections green before release.
