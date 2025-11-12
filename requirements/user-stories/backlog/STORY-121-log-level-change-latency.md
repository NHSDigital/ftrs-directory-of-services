---
id: STORY-121
title: Log level change latency <2min
nfr_refs:
  - OBS-018
  - OBS-017
type: observability
status: draft
owner: platform-team
summary: Ensure log level changes propagate within two minutes to all components.
---

## Description
Measure and ensure propagation speed for runtime log level adjustments across distributed components.

## Acceptance Criteria
- Level change visible in component logs within 2 minutes.
- Latency metric recorded per change.
- Alert triggers if propagation exceeds 2 minutes.
- No component restart required.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| propagation_latency_measure | automated | <2min |
| latency_breach_alert_test | automated | Alert fires |
| restart_requirement_check | automated | No restart |
| latency_metric_presence | automated | Metric logged |

## Traceability
NFRs: OBS-018, OBS-017
