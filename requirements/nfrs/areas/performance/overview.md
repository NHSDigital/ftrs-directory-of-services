# Performance NFRs Overview

## Background
Performance covers end-to-end request handling time within FtRS owned architecture boundaries (ingress to egress) under representative average and peak loads. User experience for patients, professionals and Authority users is strongly tied to latency; delays degrade satisfaction, usage and conversion.

## Scope & Assumptions
- Production environment targets define user-visible SLAs; methodology applies in lower environments for early detection.
- Focus on ongoing operation (not one-off launch); includes regression detection & continuous profiling.
- Percentiles: P95 chosen for action expectations (table); P50/P95/P99 monitored; methodology standardised.
- Peak window: 8h rolling window used to flatten short-term spikes.

## Domain Goals
| Goal | Description |
|------|-------------|
| Defined Expectations | Explicit latency targets per significant user action (P95). |
| Realistic Testing | Load tests use anonymised live-like datasets. |
| Low Overhead | Telemetry & background processing impose minimal performance cost. |
| Fast Regression Detection | Automated alerts on significant degradation. |
| Consistent Methodology | Percentile calculations reproducible & documented. |

## Atomic Requirements
| Code | Title | Intent | Verification |
|------|-------|--------|-------------|
| PERF-002 | Adopt performance pillar lifecycle | Embed best practice | Pillar checklist & closure report |
| PERF-003 | Performance expectation specification | Define measurable targets | Versioned expectations table |
| PERF-004 | Live-like anonymised dataset | Realistic profiling without PID | Dataset review & anonymisation audit |
| PERF-005 | Automated tests for defined actions only | Focus testing scope | Manifest vs table diff |
| PERF-006 | Batch impact ≤5% p95 delta | Safeguard UX during background work | Comparative latency report |
| PERF-007 | Telemetry overhead thresholds | Balance observability & latency | Profiling overhead benchmark |
| PERF-008 | 8h window stability ≤10% variance | Predictable performance | Variance report & dashboard |
| PERF-009 | Regression alert >10% p95 increase | Early degradation detection | Alert simulation & ticket link |
| PERF-010 | Percentile methodology documented | Consistent metrics interpretation | Method doc & tool config scan |

## Metrics & Thresholds
| Metric | Target |
|--------|--------|
| P95 latency per defined action | As per expectations table |
| Batch window P95 delta vs baseline | ≤5% |
| Telemetry added latency (p95) | ≤50ms |
| Telemetry CPU overhead | ≤3% average |
| 8h rolling P95 variance | ≤10% |
| Regression alert trigger threshold | >10% P95 increase |
| Pre-live unresolved perf actions | 0 critical |

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
