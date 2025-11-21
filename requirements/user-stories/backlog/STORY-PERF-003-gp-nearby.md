---
story_id: STORY-PERF-003
jira_key:
title: gp-search gp-nearby Performance
role: API Consumer
goal: Receive response from gp-nearby within performance targets
value: Geo filtering + limited enrichment
nfr_refs: [PERF-001]
status: draft
---

## Description
Implement and validate performance for gp-search operation: gp-nearby.

## Acceptance Criteria
1. p50 latency ≤150ms validated
2. p95 latency ≤300ms validated
3. Absolute max latency ≤500ms enforced
4. Performer class: FAST
5. Load testing completed successfully
6. Burst throughput: 150 TPS sustained
7. Sustained throughput: 150 TPS maintained

## Non-Functional Acceptance
- Operation ID: `gp-nearby`\n- Service: gp-search\n- p50: ≤150ms\n- p95: ≤300ms\n- Max: ≤500ms\n- Performer class: FAST

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
- Service: gp-search
- Path: /gp-search/nearby?lat={lat}&lon={lon}&radius={r}
- Method: GET
- Concurrency profile: burst-50 steady-15
- Status: draft

## Monitoring & Metrics
- `gp_nearby_latency_ms` histogram (p50, p95, p99)
- `gp_nearby_requests_total` counter
- `gp_nearby_errors_total` counter
- `gp_nearby_tps` gauge

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
