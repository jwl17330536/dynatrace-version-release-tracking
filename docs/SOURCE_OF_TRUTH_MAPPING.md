# Source of Truth Mapping

This document maps each requirement to its data source and fallback behavior.

## Version Intelligence Requirements Map

| Requirement | Primary Source | Workflow Task | Lookup Target | Fallback Behavior |
|---|---|---|---|---|
| SaaS current tenant version | Cluster Version API `/api/v1/config/clusterversion` | `collect_saas_current_version` | `dt_component_runtime_versions` | Row with `source_status=unavailable` and diagnostic message |
| OneAgent running versions + counts | Host telemetry (`installerVersion`) via DQL | `collect_oneagent_runtime_distribution` | `dt_component_runtime_versions` | Row with `source_status=unavailable` if no rows returned |
| ActiveGate running versions + counts | Host logs containing `Dynatrace ActiveGate started.` | `collect_activegate_runtime_distribution` + `build_lookup_payloads` | `dt_component_runtime_versions` | Explicit unavailable row when no parseable records |
| Operator running versions + counts | Kubernetes cluster inventory via DQL (`dt.entity.kubernetes_cluster`) | `collect_operator_runtime_distribution` + `build_lookup_payloads` | `dt_component_runtime_versions` | `source_status=not_configured` when no clusters; `source_status=partial` when clusters exist but version source is not yet implemented |
| EdgeConnect running versions + counts | Pending tenant-specific source validation | `build_lookup_payloads` (placeholder row) | `dt_component_runtime_versions` | Explicit unavailable row |
| Current/latest released version for each component | Dynatrace docs release pages | `collect_release_indexes` | `dt_component_release_status` | `release_status=unavailable` if parse fails |
| Next planned version for each component | Dynatrace docs release pages | `collect_release_indexes` | `dt_component_release_status` | `released_version=Not yet published` |
| Planned rollout date | Dynatrace docs release pages (rollout text parse) | `collect_release_indexes` | `dt_component_release_status` | Empty date if not provided |
| Longform release links | Dynatrace docs release pages | `collect_release_indexes` | `dt_component_release_status` | Use index page URL |
| Breaking changes summary (AI bonus) | Davis Copilot workflow action | `ai_summarize_release_notes` + `build_lookup_payloads` | `dt_component_release_status` | Empty summary fields if AI task unavailable |
| Highlights summary (AI bonus) | Davis Copilot workflow action | `ai_summarize_release_notes` + `build_lookup_payloads` | `dt_component_release_status` | Empty summary fields if AI task unavailable |

## Notes
- Runtime and release lookups are uploaded by `upload_runtime_lookup` and `upload_release_lookup`.
- `collect_release_indexes` currently creates two rows per component: latest and next-planned (or Not yet published).
- ActiveGate runtime collection is implemented from logs with explicit unavailable fallback when no parseable records are found.
- Operator runtime collection is implemented as a live inventory signal (cluster presence) with explicit `not_configured`/`partial` statuses.
- EdgeConnect runtime collection remains placeholder-based with explicit unavailable rows to avoid silent omissions until validated tenant sources are implemented.
