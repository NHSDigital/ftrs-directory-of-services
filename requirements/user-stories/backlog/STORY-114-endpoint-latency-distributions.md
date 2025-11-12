---
id: STORY-114
title: Endpoint latency distributions recorded
nfr_refs:
  - OBS-009
  - OBS-008
type: observability
status: draft
owner: api-team
summary: Record histogram latency distributions per endpoint for user experience assurance.
---

## Description
Implement histogram metrics capturing p50, p95, p99 for each API endpoint and expose panels for historical trend analysis.

## Acceptance Criteria
- Histogram buckets collected for all endpoints.
- Dashboard shows p50/p95/p99 per endpoint.
- Missing bucket triggers alert.
- Historical trend (7d) available for each percentile.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| histogram_metric_presence | automated | Buckets exist |
| percentile_panel_presence | automated | p50/p95/p99 visible |
| missing_bucket_alert_test | automated | Alert fires |
| historical_trend_query | automated | 7d data returned |

## Traceability
NFRs: OBS-009, OBS-008
