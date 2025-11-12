---
id: STORY-127
title: Dashboard data freshness <60s
nfr_refs:
  - OBS-029
  - OBS-007
type: observability
status: draft
owner: operations-team
summary: Maintain dashboard data freshness under 60 seconds for accurate operational decisions.
---

## Description
Measure and enforce end-to-end ingestion latency so dashboards reflect near-current state; implement freshness indicator.

## Acceptance Criteria
- Freshness indicator shows age ≤60s under nominal load.
- Alert fires if freshness age >60s for critical panels.
- Latency metrics recorded for ingestion pipeline steps.
- Burst scenario retains freshness ≤90s.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| freshness_indicator_measure | automated | Age ≤60s |
| freshness_breach_alert_test | automated | Alert fires |
| ingestion_step_latency_capture | automated | Metrics present |
| burst_freshness_degradation_test | automated | ≤90s age |

## Traceability
NFRs: OBS-029, OBS-007
