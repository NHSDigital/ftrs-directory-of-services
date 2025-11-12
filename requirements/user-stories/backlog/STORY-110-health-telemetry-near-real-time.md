---
id: STORY-110
title: Health telemetry near-real-time (<=60s)
nfr_refs:
  - OBS-003
  - OBS-001
type: observability
status: draft
owner: operations-team
summary: Achieve near-real-time health telemetry with visibility latency ≤60s.
---

## Description
Ensure health events (component up/down, degradation) propagate to dashboards within one minute for rapid incident response.

## Acceptance Criteria
- Event-to-visibility latency ≤60s for simulated component failure.
- Latency measurement recorded & reported.
- Alert triggers if latency >60s.
- System handles burst of 50 simultaneous health events without backlog >10s.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| failure_event_latency_test | automated | ≤60s |
| latency_threshold_alert_test | automated | Alert fires on breach |
| burst_event_stress_test | automated | Backlog ≤10s |
| latency_metric_presence | automated | Metric recorded |

## Traceability
NFRs: OBS-003, OBS-001
