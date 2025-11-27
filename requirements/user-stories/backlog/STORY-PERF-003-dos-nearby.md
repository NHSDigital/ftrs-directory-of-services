---
story_id: STORY-PERF-003
jira_key:
title: dos-search nearby query Performance
role: API Consumer
goal: Receive response from nearby search query within performance targets
value: Geo filtering + limited enrichment
nfr_refs: [PERF-001]
status: draft
---

## Description
Implement and validate performance for nearby search. Service renamed from gp-search to dos-search (legacy operation_id `gp-nearby` retained until registry update).

## Acceptance Criteria
1. p50 latency ≤150ms validated
2. p95 latency ≤300ms validated
3. Absolute max latency ≤500ms enforced
4. Load testing completed successfully
5. Burst throughput: 150 TPS sustained
6. Sustained throughput: 150 TPS maintained

## Non-Functional Acceptance
- Operation ID: `gp-nearby` (pending rename -> `dos-nearby` in registry v1.5)
- Service: dos-search
- p50: ≤150ms
- p95: ≤300ms
- Max: ≤500ms

## Test Strategy
| Test Type | Tooling | Focus |
|-----------|---------|-------|
| Compliance | Automated tooling | Policy enforcement |
| Integration | CI pipeline | Continuous validation |
| Audit | Manual review | Compliance assessment |

## Out of Scope
Implementation details to be refined during sprint planning

## Implementation Notes
- Geo filtering + limited enrichment
- Service: dos-search
- Path: /dos-search/nearby?lat={lat}&lon={lon}&radius={r}
- Method: GET
- Concurrency profile: burst-50 steady-15
- Status: draft
- Rename plan: update expectations.yaml operations in next registry version (perf v1.5)

## Monitoring & Metrics
- `dos_nearby_latency_ms` histogram (p50, p95, p99)
- `dos_nearby_requests_total` counter
- `dos_nearby_errors_total` counter
- `dos_nearby_tps` gauge

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
