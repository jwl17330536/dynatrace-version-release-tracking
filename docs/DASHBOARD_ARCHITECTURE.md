# Dashboard Architecture

## Dashboard
- Name: Dynatrace Component Release Tracking v4
- File: field-asset-library/dashboards/platform/release-tracking-dashboard/release-tracking-dashboard.v4.json

## Audience
- Platform administrators
- Observability engineers
- Upgrade and rollout coordinators

## Sections and Questions
1. Global summary:
   One executive tile shows how many components currently require action.
2. SaaS section:
   Runtime health, release status, upgrade queue, and risk/highlights.
3. ActiveGate section:
   Runtime health, release status, upgrade queue, and risk/highlights.
4. OneAgent section:
   Runtime health, release status, upgrade queue, and risk/highlights.
5. Operator section:
   Runtime health, release status, upgrade queue, and risk/highlights.
6. Edge section:
   Runtime health, release status, upgrade queue, and risk/highlights.

## Data Sources
- Primary: lookup tables (release and runtime).
- Secondary: migrated event streams for OneAgent and RUM during transition.

## Fallback Semantics
- If next planned release is unavailable: show Not yet published.
- If runtime source is unavailable: keep row with source_status and collection_message.
- If runtime source is not configured in tenant prerequisites: surface source_status=not_configured.

## Naming Convention
Use consistent tile names for each component:
- <Component> Runtime Source Health
- <Component> Release Status
- <Component> Upgrade Queue
- <Component> Risk and Highlights
