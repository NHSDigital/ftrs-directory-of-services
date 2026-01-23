# Performance NFRs Overview

## Background

Performance covers end-to-end request handling time within FtRS owned architecture boundaries (ingress to egress) under representative average and peak loads. User experience for patients, professionals and Authority users is strongly tied to latency; delays degrade satisfaction, usage and conversion.

## Scope & Assumptions

- Production environment targets define user-visible SLAs; methodology applies in lower environments for early detection.
- Focus on ongoing operation (not one-off launch); includes regression detection & continuous profiling.
- Percentiles: P95 chosen for action expectations (table); P50/P95/P99 monitored; methodology standardised.
- Peak window: 8h rolling window used to flatten short-term spikes.

## Domain Goals

| Goal                      | Description                                                        |
| ------------------------- | ------------------------------------------------------------------ |
| Defined Expectations      | Explicit latency targets per significant user action (P95).        |
| Realistic Testing         | Load tests use anonymised live-like datasets.                      |
| Low Overhead              | Telemetry & background processing impose minimal performance cost. |
| Fast Regression Detection | Automated alerts on significant degradation.                       |
| Consistent Methodology    | Percentile calculations reproducible & documented.                 |

## Atomic Requirements

| Code     | Title                                      | Intent                                                                                                                                     | Verification                                                                           |
| -------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------- |
| PERF-001 | Percentile latency adherence per operation | Each registry operation (expectations.yaml) meets p50/p95 thresholds defined in current version; targets may evolve via refinement stories | Automated validator compares live metrics to registry; dashboards overlay targets      |
| PERF-002 | Adopt performance pillar lifecycle         | Lifecycle activities (profiling, review, optimisation) tracked per refinement story affecting quantitative targets                         | Pillar checklist with story links; closure report references changed registry version  |
| PERF-003 | Performance expectation specification      | Maintain a versioned registry of per-operation quantitative targets decoupled from NFR wording                                             | Registry file version + changelog entries; diff review on PR                           |
| PERF-004 | Live-like anonymised dataset               | Provide representative anonymised samples enabling realistic percentile validation without exposing PID                                    | Dataset review log + anonymisation audit artefact tied to stories updating coverage    |
| PERF-005 | Automated tests for defined actions only   | Test manifest derived from registry operation_id list; excludes deprecated/undocumented actions                                            | Manifest vs expectations.yaml operation_id diff gate in CI                             |
| PERF-006 | Batch impact ≤5% p95 delta                 | Background ETL / batch operations do not increase affected endpoint p95 by >5% vs baseline window                                          | Comparative latency report referencing registry version + time window                  |
| PERF-007 | Telemetry overhead thresholds              | Observability instrumentation overhead kept within documented CPU / latency budgets; adjustments tracked via stories                       | Profiling benchmark run; overhead metrics ≤ thresholds; story links for changes        |
| PERF-008 | 8h window stability ≤10% variance          | Rolling 8h p95 for each operation remains within ±10% of target unless exception story approved                                            | Variance dashboard & validator summary; exception_story field in registry for SLOW ops |
| PERF-009 | Regression alert >10% p95 increase         | Automatic alert/story creation when p95 exceeds target +10% sustained for configured window                                                | Alert simulation test + ticket referencing operation_id & registry version             |
| PERF-010 | Percentile methodology documented          | Single authoritative methodology doc and tool configuration; any change triggers registry version bump if targets recalculated                    | Doc presence + configuration scan; story referencing methodology and registry version         |
| PERF-011 | Burst throughput capacity per operation    | Each dos-search endpoint supports ≥150 TPS burst without breaching latency targets                                                         | Load test report (burst phase) vs registry burst_tps_target                            |
| PERF-012 | Sustained throughput baseline              | Each dos-search endpoint sustains ≥150 TPS steady state for defined window meeting latency targets                                         | Load test steady phase metrics vs sustained_tps_target                                 |
| PERF-013 | Request payload size constraint            | Maximum inbound request payload ≤1MB; larger payloads rejected early                                                                       | Test suite boundary cases; registry max_request_payload_bytes field                    |

## Metrics & Thresholds

| Metric                             | Target                    |
| ---------------------------------- | ------------------------- |
| P95 latency per defined action     | As per expectations table |
| Batch window P95 delta vs baseline | ≤5%                       |
| Telemetry added latency (p95)      | ≤50ms                     |
| Telemetry CPU overhead             | ≤3% average               |
| 8h rolling P95 variance            | ≤10%                      |
| Regression alert trigger threshold | >10% P95 increase         |
| Pre-live unresolved performance actions   | 0 critical                |

## Workflow

1. Maintain expectations table (actions, endpoints, P95 targets, notes) in versioned file.
2. Update automated load test manifest when table changes; enforce diff gate.
3. Generate anonymised dataset refresh pre-major test cycle with audit evidence.
4. Run comparative tests for batch windows vs baseline; record delta metrics.
5. Continuous telemetry overhead profiling; adjust sampling/levels to stay within thresholds.
6. Alerting rule monitors P95 deltas; creates incident ticket when breached.
7. Review percentile methodology doc quarterly; update tooling configs if needed.

## Maturity

All PERF codes draft. Move to review after first complete cycle (table, tests, profiling, alerting). Approve after two consecutive releases meeting thresholds with no unaddressed critical regressions.
