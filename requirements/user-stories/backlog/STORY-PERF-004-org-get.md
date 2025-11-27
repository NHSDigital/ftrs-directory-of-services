---
story_id: STORY-PERF-004
jira_key:
title: crud-apis org-get Performance
role: API Consumer
goal: Receive response from org-get within performance targets
value: Simple primary key lookup; cached storage path
nfr_refs: [PERF-001]
status: draft
---

## Description
Implement and validate performance for crud-apis operation: org-get.

## Acceptance Criteria
1. p50 latency ≤40ms validated
2. p95 latency ≤100ms validated
3. Absolute max latency ≤300ms enforced
4. Load testing completed successfully

## Non-Functional Acceptance
- Operation ID: `org-get`
- Service: crud-apis
- p50: ≤40ms
- p95: ≤100ms
- Max: ≤300ms

## Test Strategy
| Test Type | Tooling | Focus |
|-----------|---------|-------|
| Compliance | Automated tooling | Policy enforcement |
| Integration | CI pipeline | Continuous validation |
| Audit | Manual review | Compliance assessment |

## Out of Scope
Implementation details to be refined during sprint planning

## Implementation Notes
- Simple primary key lookup; cached storage path
- Service: crud-apis
- Path: /Organization/{id}
- Method: GET
- Concurrency profile: burst-70 steady-25
- Status: draft

## Monitoring & Metrics
- `org_get_latency_ms` histogram (p50, p95, p99)
- `org_get_requests_total` counter
- `org_get_errors_total` counter

## Risks & Mitigation
| Risk | Impact | Mitigation |
|------|--------|-----------|
| Configuration drift | Non-compliance | Automated remediation |
| Tool failures | Missed violations | Redundant checks |

## Traceability
- NFR: PERF-001
- Registry: performance/expectations.yaml v1.6

## Open Questions
None
