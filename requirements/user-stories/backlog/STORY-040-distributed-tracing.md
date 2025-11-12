---
id: STORY-040
title: Distributed tracing end-to-end
nfr_refs:
  - OBS-030
type: observability
status: draft
owner: platform-team
summary: Implement distributed tracing with spans & transaction IDs across request lifecycle.
---

## Description
Instrument ingress, service calls, data layer interactions, and external calls with trace context enabling end-to-end latency analysis.

## Acceptance Criteria
- Trace displays all spans for synthetic multi-tier request.
- Missing span injection triggers alert.
- P95 span latency panel present.
- Trace correlation ID searchable.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| synthetic_trace_chain | automated | All spans present |
| missing_span_alert_test | automated | Alert fires |
| latency_panel_presence | automated | Panel shows p95 |
| correlation_id_search_test | automated | Trace found |

## Traceability
NFRs: OBS-030
