---
id: STORY-183
title: Maintain observability freshness and overhead limits
status: draft
type: functional
owner: gp-search-team
nfr_refs:
  - PERF-007
  - OBS-007
  - OBS-009
  - OBS-024
summary: As an operator I need timely metrics and alerts without excessive resource overhead.
---

### Acceptance Criteria
1. Telemetry overhead CPU ≤3% / p95 added latency ≤50ms (PERF-007).
2. Metrics freshness ≤60s from event to dashboard (OBS-007).
3. Latency histograms include p50/p95/p99 buckets (OBS-009).
4. Alert rule fires when overhead thresholds breached (OBS-024).

### Test Notes
| Scenario | Tool | Data | Expected |
|----------|------|------|----------|
| Freshness test | load + timing | 50 RPS | Dashboard shows events <60s old |
| Overhead benchmark | load test | 100 RPS | Within CPU & latency limits |
| Alert simulation | injected overhead | 100 RPS | Alert triggers |

### Traceability
Observability performance alignment.
