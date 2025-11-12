---
id: STORY-032
title: TPS per API endpoint recorded
nfr_refs:
  - OBS-008
type: observability
status: draft
owner: api-team
summary: Record and display throughput (TPS) per API endpoint for capacity & scaling decisions.
---

## Description
Add instrumentation to count requests per endpoint with aggregation by minute including success/error segmentation.

## Acceptance Criteria
- Dashboard panel lists TPS for all active endpoints.
- TPS differentiates success vs error requests.
- Data retention ≥30 days.
- Alert triggers when TPS exceeds configured threshold.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| tps_metric_presence | automated | All endpoints show TPS |
| success_error_segmentation_test | automated | Segmentation accurate |
| threshold_alert_simulation | automated | Alert fires on spike |
| retention_check | automated | Historical data 30 days |

## Traceability
NFRs: OBS-008
