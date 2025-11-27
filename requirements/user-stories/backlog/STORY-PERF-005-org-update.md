---
story_id: STORY-PERF-005
jira_key:
title: crud-apis org-update Performance
role: API Consumer
goal: Receive response from org-update within performance targets
value: Validation + persistence + OperationOutcome classification
nfr_refs: [PERF-001]
status: draft
---

## Description
Implement and validate performance for crud-apis operation: org-update.

## Acceptance Criteria
1. p50 latency ≤70ms validated
2. p95 latency ≤150ms validated
3. Absolute max latency ≤400ms enforced
4. Load testing completed successfully

## Non-Functional Acceptance
- Operation ID: `org-update`
- Service: crud-apis
- p50: ≤70ms
- p95: ≤150ms
- Max: ≤400ms

## Test Strategy
| Test Type | Tooling | Focus |
|-----------|---------|-------|
| Compliance | Automated tooling | Policy enforcement |
| Integration | CI pipeline | Continuous validation |
| Audit | Manual review | Compliance assessment |

## Out of Scope
Implementation details to be refined during sprint planning

## Implementation Notes
- Validation + persistence + OperationOutcome classification
- Service: crud-apis
- Path: /Organization/{id}
- Method: PUT
- Concurrency profile: burst-40 steady-15
- Status: draft

## Monitoring & Metrics
- `org_update_latency_ms` histogram (p50, p95, p99)
- `org_update_requests_total` counter
- `org_update_errors_total` counter

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
