---
id: STORY-175
title: Standardise percentile calculation methodology
nfr_refs:
  - PERF-010
  - PERF-003
type: performance
status: draft
owner: performance-team
summary: Document and enforce standard percentile calculation methodology for latency metrics.
---

## Description
Produce methodology doc (definition, aggregation window, outlier handling, interpolation); align tooling configs (Prometheus/StatsD/k6) to ensure consistent P50/P95/P99 values.

## Acceptance Criteria
- Methodology document stored & versioned.
- Tooling config diff shows alignment (same window & quantile algorithm).
- Validation script compares two sources; variance ≤2%.
- Change to methodology triggers config update test.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| methodology_doc_presence | automated | File exists |
| tooling_config_alignment_scan | automated | Settings match spec |
| cross_source_variance_check | automated | ≤2% variance |
| methodology_change_trigger_test | automated | Config update job runs |

## Traceability
NFRs: PERF-010, PERF-003
