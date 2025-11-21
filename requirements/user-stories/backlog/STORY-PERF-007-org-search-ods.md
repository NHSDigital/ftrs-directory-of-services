---
story_id: STORY-PERF-007
jira_key:
title: crud-apis org-search-ods Performance
role: API Consumer
goal: Receive response from org-search-ods within performance targets
value: ODS code normalization + single index scan
nfr_refs: [PERF-001]
status: draft
---

## Description
Implement and validate performance for crud-apis operation: org-search-ods.

## Acceptance Criteria
1. p50 latency ≤60ms validated
2. p95 latency ≤140ms validated
3. Absolute max latency ≤400ms enforced
4. Performer class: FAST
5. Load testing completed successfully

## Non-Functional Acceptance
- Operation ID: `org-search-ods`\n- Service: crud-apis\n- p50: ≤60ms\n- p95: ≤140ms\n- Max: ≤400ms\n- Performer class: FAST

## Test Strategy
| Test Type | Tooling | Focus |
|-----------|---------|-------|
| Compliance | Automated tooling | Policy enforcement |
| Integration | CI pipeline | Continuous validation |
| Audit | Manual review | Compliance assessment |

## Out of Scope
Implementation details to be refined during sprint planning

## Implementation Notes
- ODS code normalization + single index scan
- Service: crud-apis
- Path: /Organization?identifier=odsOrganisationCode|{code}
- Method: GET
- Concurrency profile: burst-50 steady-15
- Status: draft

## Monitoring & Metrics
- `org_search_ods_latency_ms` histogram (p50, p95, p99)
- `org_search_ods_requests_total` counter
- `org_search_ods_errors_total` counter

## Risks & Mitigation
| Risk | Impact | Mitigation |
|------|--------|-----------|
| Configuration drift | Non-compliance | Automated remediation |
| Tool failures | Missed violations | Redundant checks |

## Traceability
- NFR: PERF-001
- Registry: performance/expectations.yaml v1.4

## Open Questions
None
