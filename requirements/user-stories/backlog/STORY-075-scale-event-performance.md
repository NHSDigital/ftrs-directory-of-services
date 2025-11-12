---
id: STORY-075
title: Preserve performance during scaling events
nfr_refs:
  - SCAL-006
  - PERF-001
type: scalability
status: draft
owner: performance-team
summary: Verify scaling actions do not cause latency or error spikes beyond SLA limits.
---

## Description
Run continuous load while triggering autoscaling events to ensure latency percentiles and error rates remain within SLA boundaries before, during, and after scaling.

## Acceptance Criteria
- p50/p95 latency stays within defined SLA thresholds during scale-out/in.
- Error rate does not exceed baseline by >2% absolute.
- No failed requests due to in-flight instance termination.
- Report visualising metrics timeline stored.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| continuous_load_with_scale_out | automated | Latency stable; errors stable |
| continuous_load_with_scale_in | automated | Latency stable; errors stable |
| in_flight_termination_test | automated | No failed requests |
| metrics_timeline_report | manual | Report committed |

## Traceability
NFRs: SCAL-006, PERF-001
