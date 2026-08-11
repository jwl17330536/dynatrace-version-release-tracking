# Migration Inventory

## Migrated (Active Reuse)
- workflows/version-intelligence-sync.v1.workflow.json
  - Legacy source: dynatrace-private-ops/workflows/dt-version-checker.v9.workflow.json
  - Reason: current production baseline with OneAgent + RUM collection.
  - Compatibility note: migrated initially as `release-tracker.v1.workflow.json`, then normalized to canonical naming.

- dashboards/oneagent-version-dashboard.json
  - Source: dynatrace-private-ops/dashboards/oneagent-version-dashboard.json
  - Reason: stable OneAgent compliance view and query patterns.

- dashboards/rum-classic-js-version-dashboard.json
  - Source: dynatrace-private-ops/dashboards/rum-classic-js-version-dashboard.json
  - Reason: stable per-app RUM JS version visibility.

- dashboards/rum-version-compliance-dashboard.v3.json
  - Source: dynatrace-private-ops/dashboards/rum-version-compliance-dashboard.v3.json
  - Reason: policy-based RUM compliance model.

- docs/oneagent-baseline-rum-classic-sync.README.md
  - Source: dynatrace-private-ops/docs/oneagent-baseline-rum-classic-sync.README.md
  - Reason: event contracts, token scopes, version-domain explanation.

## Retained as Reference (Not Primary)
- references/workflows/dt-version-checker.v5.workflow.json
- references/workflows/dt-version-checker.v6.workflow.json
- references/workflows/dt-version-checker.v7.workflow.json
- references/workflows/dt-version-checker.v8.workflow.json
- references/workflows/oneagent-baseline-sync.workflow.json

Reason: superseded historical versions retained for traceability and rollback understanding only.

## Left in Other Repos
- Repo-specific release scripts and changelogs in netflow-observability, proxmox-observability, and unifi-observability.

Reason: these are component/repo release assets, not tenant-wide Dynatrace version-checking assets.

## Duplicate Prevention Rule
Before creating any new workflow/dashboard in this repository:
1. Check dashboards/ and workflows/ for a reusable base.
2. Check references/ for prior solved variants.
3. Document why new artifacts are required if no reusable baseline exists.

## Post-Migration Enhancements Applied
- ActiveGate runtime collection upgraded from placeholder rows to a live DQL parser over startup logs.
- Operator runtime collection upgraded from static placeholder rows to a live Kubernetes inventory signal.
- EdgeConnect runtime collection intentionally remains placeholder-based until a reliable version-bearing source is validated.
- AI release-note enrichment upgraded to parse and map distinct `BREAKING` and `HIGHLIGHTS` sections.

## Validation Snapshot (2026-08-05)
- Workflow applied and executed successfully after parser and upload fixes.
  - Workflow ID: `92ebd560-5632-49c1-8f81-0782b40ac4eb`
  - Verified execution ID: `4cb9636e-c4e4-47a6-b302-d8701bfb5e0d` (SUCCESS)
- Lookup upload verification from workflow run:
  - `/lookups/dt_component_release_status` rowCount: 10
  - `/lookups/dt_component_runtime_versions` rowCount: 7
- Dashboard deployed with corrected query contracts and runtime source-health tile.
  - Dashboard ID: `065fa647-132c-4c23-9895-a55d0710b88c`

## Validation Snapshot (2026-08-06)
- Workflow v2 applied and executed successfully with schedule UI inputs and vault-first config references.
  - Workflow ID: `298cd024-8813-4a48-b5af-057537b9945a`
  - Verified execution ID: `f09c5f8d-a32c-47b3-b5f6-dc3d169c0f9f` (SUCCESS)
- Lookup upload verification from workflow run:
  - `/lookups/dt_component_release_status` rowCount: 10
  - `/lookups/dt_component_runtime_versions` rowCount: 7
- Tenant deduplication completed for v2 title collisions:
  - Removed duplicate workflow IDs: `87e2c28d-9736-4c71-bdfc-185947e2764b`, `af7405a3-b48e-43bc-b1d6-a4ee787d97d6`, `1e896ac7-8e95-4a70-98aa-a4c83fe03c16`, `1501b8d2-0493-421f-94e4-2343e36b8fe3`
  - Retained canonical workflow ID: `298cd024-8813-4a48-b5af-057537b9945a`

## Validation Snapshot (2026-08-06, Dashboard Repair)
- Incident: dashboard tiles failed with `FIELD_DOES_NOT_EXIST` for `component` due to lookup tables being overwritten with zero records and zero columns.
- Root cause: upload parser accepted only header rows when empty fields were present, resulting in successful HTTP status with `records: 0`.
- Workflow remediation applied to `version-intelligence-sync.v2.workflow.json`:
  - Upload CSV serialization now emits `-` for empty values so every LD parse field is populated.
  - Upload tasks now return API response payload for diagnostics.
  - Lookup dedupe key switched from `component` to synthetic `lookup_key` so latest+next release rows and runtime distributions are retained.
- Verification evidence:
  - Workflow ID: `298cd024-8813-4a48-b5af-057537b9945a`
  - Verified execution IDs: `d6249419-d366-4ce7-93a6-5c60e14cdc84` and `26f71710-56ac-4ddd-8602-2dae0097125b` (SUCCESS)
  - Release lookup query count: 10 rows
  - Runtime lookup query count: 7 rows
  - Tile-equivalent DQL queries now execute successfully without field errors.
  - Canonical dashboard retained: `065fa647-132c-4c23-9895-a55d0710b88c` (temporary duplicate removed).

## Validation Snapshot (2026-08-06, v3 Candidate)
- Created v3 workflow from the validated v2 artifact with schedule intentionally disabled for controlled cutover.
  - Workflow ID: `786ad6e6-cf90-4e1d-a67e-6544f2d5be8d`
  - Title: `Version Intelligence Sync v3`
  - Schedule state: `isActive=false`
  - Layout preservation check: `position_diffs=0` against live v2 export.
- Manual validation run:
  - Execution ID: `41e9077f-f11c-4889-ac8e-d688c3fc6161` (SUCCESS)
  - Post-run lookup counts: release=10, runtime=7

## Validation Snapshot (2026-08-06, v3 Hardening Complete)
- Hardened `version-intelligence-sync.v3.workflow.json` to remove unsupported Run JavaScript Jinja interpolation and rely on `execution().input` / `execution().params`.
- Verified v3 execution success with strict config values provided via run parameters.
  - Workflow ID: `786ad6e6-cf90-4e1d-a67e-6544f2d5be8d`
  - Verified execution ID: `e53c0cdb-81b0-4987-9692-017943568667` (SUCCESS)
  - Verified execution ID: `f96342ad-2f01-4505-9ba8-d37ac88bf45f` (ERROR before final RUM fix)
- Verified no-params manual execution currently fails as expected when required values are not supplied at run time.
  - Verified execution ID: `b7ddb101-c06c-4ae3-9d42-eb078611673b` (ERROR)
  - Missing keys during manual no-params run: `docsSitemapUrl`, `apiTokenVaultId`, `rumTokenVaultId`
  - Operational guidance: execute manually with `--params` for required keys, or run from a trigger path that provides input values.
- Dashboard v2 query contract revalidated after DQL conditional fix (`if(..., else: ...)`).
  - Validation script: `scripts/validate_dashboard_v2_queries.py`
  - Result: all 17 data tiles PASS
- Dashboard v2 redeployed after query fix:
  - Dashboard ID: `4832f8d0-49a8-4b43-8f61-d03b480fd766`

## Platform Constraint Note (Workflow Guide)
- Although `guide` is present in local JSON, `dtctl get workflow` returns `guide: null` after apply for v3.
- Current operating workaround: maintain canonical markdown in `docs/WORKFLOW_GUIDE_V3.md` and apply in UI when guide persistence is required.

## Implementation Snapshot (2026-08-05, v4/v3 Start)
- Started v4/v3 implementation track in repository artifacts.
  - New workflow artifact staged: `workflows/version-intelligence-sync.v4.workflow.json`
  - Workflow ID assigned for v4: `f82e7c9e-403a-4b77-9e3b-ef086279e4b0`
  - New dashboard artifact staged: `field-asset-library/dashboards/platform/release-tracking-dashboard/release-tracking-dashboard.v3.json`
- Dashboard v3 direction:
  - Reduced table density versus v2.
  - Added explicit triage-oriented status language and icon badges.
  - Added upgrade queue view and source-health-first operating layout.
- Validation utility added for v3 query smoke tests:
  - `scripts/validate_dashboard_v3_queries.py`

## Validation Snapshot (2026-08-06, v5 Parser + Deterministic Fallback)
- v5 workflow applied and updated to deployed state.
  - Workflow artifact: `workflows/version-intelligence-sync.v5.workflow.json`
  - Workflow ID: `827008e7-f74d-455a-8324-72629ff6225f`
- Initial manual executions failed due missing runtime parameters (expected with empty manual input on this workflow model).
  - Failed execution IDs: `b541aeab-4a31-47ef-a92f-cf1368450b51`, `3cb2d9a0-d1c6-4e11-96bf-f48b7908d209`
  - Missing values reported: `apiTokenVaultId`, `rumTokenVaultId`
- Parameterized validation execution succeeded end-to-end.
  - Success execution ID: `5451dbbf-233e-4738-9dbf-cc4595dccac1`
  - Final state: `SUCCESS`
- Lookup upload verification from successful v5 run:
  - `/lookups/dt_component_release_status` statusCode: `200`, rowCount: `10`
  - `/lookups/dt_component_runtime_versions` statusCode: `200`, rowCount: `7`
- Parser propagation and fallback behavior verified from task results:
  - `build_lookup_payloads` totals: release rows `10`, runtime rows `7`, parser success rows `10`
  - Deterministic fallback observed on OneAgent latest row (`oneagent|1.343`) where AI breaking summary was empty:
    - `breaking_changes_summary` populated as `AI unavailable, review release_url: ... (parser_status=success)`
  - Feature updates parsing verified on SaaS latest row (`saas|1.345`) with both
    `parsed_feature_updates` and `parsed_feature_sections` populated.
- Dashboard smoke validation completed after v5 execution.
  - Validation script: `scripts/validate_dashboard_v3_queries.py`
  - Result: all 7 data tiles PASS

## Validation Snapshot (2026-08-06, v5 No-Params Hardening)
- Implemented default fallback handling for manual no-params execution in v5 runtime scripts:
  - `collect_saas_current_version` now defaults `apiTokenVaultId` when omitted.
  - `oneagent_store_baseline_event` now defaults `rumTokenVaultId` when omitted.
  - `rum_collect_runtime_versions` now defaults `rumTokenVaultId` when omitted.
  - `upload_runtime_lookup` now defaults `releaseLookupPath`, `runtimeLookupPath`, `lookupLocale`, and `lookupTimezone` when omitted.
- Validation sequence:
  - First no-params run failed on strict upload-runtime config gate before final patch.
    - Execution ID: `a137279f-e985-4a08-9d8a-aa3ba6ec3a59` (ERROR)
  - Re-applied workflow after runtime upload defaults patch and re-ran with no params.
    - Execution ID: `4d422c91-ad8d-4b19-8f6a-8ab59450d366` (SUCCESS)
- No-params success verification from task outputs:
  - `/lookups/dt_component_release_status` statusCode: `200`, rowCount: `10`
  - `/lookups/dt_component_runtime_versions` statusCode: `200`, rowCount: `7`
  - `build_lookup_payloads`: release rows `10`, runtime rows `7`, parser success rows `10`
  - `build_lookup_payloads`: `is_newer_than_running=true` rows `0` (current tenant runtime sprint/build levels are already at or above published docs baselines for checked components).

## Validation Snapshot (2026-08-06, v3 Upgrade Queue Semantic Reconciliation)
- Root cause of mismatch closed: tile 6 previously compared full runtime build strings to published sprint baseline strings (`running_version == latest_published`), which produced false `🔴 newer available` rows.
- Tile 6 query now uses canonical workflow output from `/lookups/dt_component_release_status`:
  - `is_newer_than_running == "true"` => `🔴 newer available`
  - otherwise => `🟢 aligned`
- Revalidation evidence:
  - Dashboard query smoke tests: `python3 scripts/validate_dashboard_v3_queries.py` => all 7 data tiles PASS.
  - Live tile 6 DQL result after patch: `record_count=5`, `newer_available=0`, `aligned=5`.
  - Dashboard applied with patched query semantics: `152d125f-a3cc-470b-a612-ba4e83fd0016`.

## Validation Snapshot (2026-08-06, v3 Upgrade Queue Tri-State Status)
- Refined tile 6 action semantics to avoid false-positive `aligned` when runtime version is unknown.
  - `is_newer_than_running == "true"` => `🔴 newer available`
  - `running_version == "" or "-"` => `🟠 runtime unknown`
  - otherwise => `🟢 aligned`
- Added explicit `action_priority` sort order for stable triage ordering (`newer` -> `unknown` -> `aligned`).
- Revalidation evidence:
  - Dashboard query smoke tests: `python3 scripts/validate_dashboard_v3_queries.py` => all 7 data tiles PASS.
  - Live tile 6 DQL result after tri-state patch: `record_count=5`, `newer_available=0`, `runtime_unknown=2`, `aligned=3`.
  - Dashboard updated in place: `152d125f-a3cc-470b-a612-ba4e83fd0016`.

## Validation Snapshot (2026-08-06, Automated Red-Path Ranking Check)
- Added targeted backlog validator: `scripts/validate_upgrade_queue_red_path.py`.
  - Query scope: `/lookups/dt_component_release_status` where `is_newer_than_running=true`.
  - Assertions:
    - `newer_than_running_rank` is numeric and >= 1.
    - `running_version` is present for backlog rows.
    - Rank sequence is contiguous per component (1..N).
- Current execution result: `SKIP` (no backlog rows currently present in tenant), which is expected for current aligned state.

## Validation Snapshot (2026-08-06, Tile 6 Semantic Alignment Guard)
- Added semantic drift validator: `scripts/validate_upgrade_queue_semantics.py`.
  - Reads tile 6 query directly from dashboard artifact.
  - Executes an independent expected-action query from `/lookups/dt_component_release_status`.
  - Compares per-component classification (`newer` / `unknown` / `aligned`) between tile output and expected output.
- Current execution result: `PASS`.
  - Evidence summary: `newer=0`, `unknown=2`, `aligned=3`.

## Validation Snapshot (2026-08-06, One-Shot Validation Suite)
- Added orchestrator script: `scripts/run_validation_suite.py`.
  - Runs `validate_dashboard_v3_queries.py`.
  - Runs `validate_upgrade_queue_semantics.py`.
  - Runs `validate_upgrade_queue_red_path.py`.
  - Produces consolidated PASS/SKIP/FAIL summary.
- Current suite run result:
  - `PASS=2`, `SKIP=1`, `FAIL=0`
  - `SKIP` corresponds to expected no-backlog state for red-path ranking validation.

## Implementation Snapshot (2026-08-05, Dashboard + Workflow Gap Fixes)
- Dashboard v3 semantics updated and deployed in place (`152d125f-a3cc-470b-a612-ba4e83fd0016`):
  - Tile 1 (`Action Required Components`) now includes both runtime source issues and upgrade backlog signal (`is_newer_than_running=true`).
  - Tile 2 (`Components In Watch State`) now reflects runtime watch states (`partial`, `not_configured`) plus release watch indicators (`release_status != current` or `is_next_planned=true`).
- Workflow v5 reliability fix deployed (`827008e7-f74d-455a-8324-72629ff6225f`):
  - `rum_collect_runtime_versions` no longer references out-of-scope `rumTokenVaultId` in helper function auth-error paths.
  - Added explicit script-level tracking variable for vault ID context in 401 diagnostics.
- Post-implementation validation evidence:
  - `python3 scripts/run_validation_suite.py` => `PASS=2`, `SKIP=1`, `FAIL=0`.
  - Dashboard query smoke tests: all 7 tiles PASS.
  - Tile 6 semantic alignment guard: PASS (`newer=0`, `unknown=2`, `aligned=3`).

## Validation Snapshot (2026-08-06, Workflow Runtime Fix Verification)
- Repaired `rum_collect_runtime_versions` script text integrity after deployment edit:
  - Removed literal `\\n` code artifacts in embedded script source.
  - Preserved explicit `RUM_TOKEN_VAULT_ID` assignment and usage for 401 diagnostics.
- Deployed updated v5 workflow and executed manual no-params run:
  - Workflow ID: `827008e7-f74d-455a-8324-72629ff6225f`
  - Execution ID: `360987f2-3514-4c8c-8f10-8badf7f0604d` (`SUCCESS`)
  - Runtime: 23 seconds

## Validation Snapshot (2026-08-06, Workflow Contract Guard)
- Added contract validator: `scripts/validate_workflow_v5_contract.py`.
  - Validates v5 title and deployed state.
  - Validates RUM collector auth-diagnostic variable scoping markers.
  - Fails if out-of-scope `${rumTokenVaultId}` reference exists in RUM script.
  - Emits warnings (non-fatal) for schedule disabled state and shared vault defaults.
- Added to one-shot suite: `scripts/run_validation_suite.py`.

## Outstanding Items (Post-v5)
- Execute `python3 scripts/run_validation_suite.py` after next observed backlog condition (`is_newer_than_running=true`) to capture first non-SKIP PASS evidence for live red-path ranking behavior.
