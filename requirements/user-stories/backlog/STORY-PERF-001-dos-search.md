---
story_id: STORY-PERF-001
jira_key:
title: dos-search primary search Performance
role: API Consumer
goal: Receive response from primary dos-search query within performance targets
value: Primary user-facing query; critical perceived responsiveness
nfr_refs: [PERF-001]
status: draft
---

## Description
Implement and validate performance for primary search operation. Service renamed from gp-search to dos-search (legacy operation_id `gp-search` retained until performance registry update).

## Acceptance Criteria
1. p50 latency ≤150ms validated
2. p95 latency ≤300ms validated
3. Absolute max latency ≤500ms enforced
4. Load testing completed successfully
5. Burst throughput: 150 TPS sustained
6. Sustained throughput: 150 TPS maintained

## Non-Functional Acceptance
- Operation ID: `gp-search` (pending rename -> `dos-search` in registry v1.5)
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
- Primary user-facing query; critical perceived responsiveness
- Service: dos-search
- Path: /dos-search?query={q}
- Method: GET
- Concurrency profile: burst-80 steady-20
- Status: draft
- Rename plan: update expectations.yaml operations in next registry version (perf v1.5)

## Monitoring & Metrics
- `dos_search_latency_ms` histogram (p50, p95, p99)
- `dos_search_requests_total` counter
- `dos_search_errors_total` counter
- `dos_search_tps` gauge

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
