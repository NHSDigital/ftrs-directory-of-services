---
id: STORY-113
title: Performance telemetry near-real-time (<=60s)
nfr_refs:
  - OBS-007
  - OBS-005
type: observability
status: draft
owner: performance-team
summary: Ensure performance telemetry updates appear within 60 seconds of event.
---

## Description
Optimize pipeline delivering performance metrics (latency, TPS, resource utilisation) to dashboards with near-real-time ingestion.

## Acceptance Criteria
- Metric update latency ≤60s measured end-to-end.
- Alert fires if latency >60s for critical metrics.
- Burst of 100 metrics processed without backlog growth >15s.
- Latency metric recorded & visible.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| metric_latency_measurement | automated | ≤60s |
| latency_breach_alert_test | automated | Alert emitted |
| burst_processing_stress_test | automated | Backlog within limit |
| latency_metric_dashboard_presence | automated | Panel visible |

## Traceability
NFRs: OBS-007, OBS-005
