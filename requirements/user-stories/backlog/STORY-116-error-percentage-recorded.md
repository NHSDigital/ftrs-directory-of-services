---
id: STORY-116
title: Error percentage vs total responses recorded
nfr_refs:
  - OBS-012
  - OBS-011
type: observability
status: draft
owner: api-team
summary: Record and display error percentage across API responses supporting error budget tracking.
---

## Description
Implement metric capturing error_rate = errors/total_requests per time window with dashboard visualisation and alerting.

## Acceptance Criteria
- Error percentage panel visible with current & historical trend.
- Alert triggers when error rate exceeds configured threshold.
- Metric segmentation by error_type available.
- Calculation validated against sampled logs (≤1% variance).

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| error_rate_panel_presence | automated | Panel visible |
| threshold_alert_simulation | automated | Alert fires |
| segmentation_query_test | automated | Types separated |
| variance_validation_test | automated | ≤1% difference |

## Traceability
NFRs: OBS-012, OBS-011
