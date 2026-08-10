# Dashboard Query Catalog

## Dashboard File
- field-asset-library/dashboards/platform/release-tracking-dashboard/release-tracking-dashboard.v4.json

## Tile Catalog
- Tile 0: Global Action Required Components
  - Source: /lookups/dt_component_runtime_versions + /lookups/dt_component_release_status
  - Purpose: global count of components needing action now

- Component section tiles (SaaS, ActiveGate, OneAgent, Operator, Edge)
  - Runtime Source Health
    - Source: /lookups/dt_component_runtime_versions filtered by component
    - Expected columns: source_status, source_type, observed_version, rows
  - Release Status
    - Source: /lookups/dt_component_release_status filtered by component
    - Expected columns: released_version, release_status, is_latest, is_next_planned, running_version, release_url, fetched_at
  - Upgrade Queue
    - Source: /lookups/dt_component_release_status filtered by component and latest row
    - Expected columns: running_version, latest_published, action, release_url, fetched_at
  - Risk and Highlights
    - Source: /lookups/dt_component_release_status filtered by component and latest row
    - Expected columns: released_version, risk, highlights, release_url, fetched_at

## Validation Rules
1. Every tile query must run without errors.
2. Every component section must include the 4 expected data tiles (runtime, release, queue, risk).
3. Queue action state per component must align with lookup-derived expectations.
4. Missing data must be explicit through status fields, not silent omissions.

## Lookup Upload Contract Notes
- Release lookup keeps both latest and next rows per component via workflow-generated `lookup_key` dedupe field.
- Runtime lookup keeps multi-version distributions via workflow-generated `lookup_key` dedupe field.
- Empty string values are serialized as `-` during lookup upload to avoid parser row drops.
