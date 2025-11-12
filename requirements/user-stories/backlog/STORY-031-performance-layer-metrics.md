---
id: STORY-031
title: Performance metrics per layer
nfr_refs:
  - OBS-005
type: observability
status: draft
owner: performance-team
summary: Capture performance metrics (latency, throughput, resource usage) across all architecture layers.
---

## Description
Instrument application, database, cache, queue, and external dependency layers for latency and throughput plus resource utilisation to support capacity planning.

## Acceptance Criteria
- Metrics exported for latency & TPS per layer.
- Resource utilisation (CPU, memory, disk, IO) published for infra components.
- Dashboard panels show current & historical trends (≥7 days).
- Missing metric detection alert configured.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| metrics_export_presence | automated | Required metrics exist |
| dashboard_latency_panels | automated | Panels return data |
| missing_metric_simulation | automated | Alert fires |
| historical_window_check | automated | ≥7 days retained |

## Traceability
NFRs: OBS-005
