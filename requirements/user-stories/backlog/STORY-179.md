---
id: STORY-179
title: Emit structured logs and distributed traces with minimal overhead
status: draft
type: functional
owner: gp-search-team
nfr_refs:
  - OBS-017
  - OBS-019
  - OBS-030
  - OBS-021
  - PERF-007
summary: As an operator I need correlated logs and traces to diagnose issues rapidly without degrading performance.
---

### Acceptance Criteria
1. Logs include transaction id, ods_code, organization_id, status_code.
2. Log levels adjustable at runtime and propagate <2 minutes (OBS-017 synergy with OBS-018 though not directly referenced).
3. Trace spans show handler -> validation -> repository -> mapper -> response.
4. Operational events include transaction id per schema (OBS-021).
5. Observability overhead CPU ≤3% and p95 added latency ≤50ms vs baseline (PERF-007).

### Test Notes
| Scenario | Tool | Data | Expected |
|----------|------|------|----------|
| Log content | pytest + caplog | Valid request | Required fields present |
| Trace chain | local exec + X-Ray | Valid request | All spans visible |
| Overhead benchmark | load test | 100 RPS | CPU & latency deltas within threshold |

### Traceability
Logging/tracing NFRs with overhead constraints.
