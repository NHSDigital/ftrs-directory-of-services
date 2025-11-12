---
id: STORY-184
title: Ensure batch/background processing does not degrade search latency
status: draft
type: functional
owner: gp-search-team
nfr_refs:
  - PERF-006
  - PERF-008
  - PERF-009
  - SCAL-005
summary: As a performance engineer I need confidence that secondary tasks keep user-facing latency stable.
---

### Acceptance Criteria
1. p95 latency delta during batch window ≤5% vs baseline (PERF-006).
2. 8h rolling window variance ≤10% (PERF-008).
3. Regression alert triggers if >10% p95 increase sustained (PERF-009).
4. Autoscaling policy guardrails prevent oscillation under mixed load (SCAL-005).

### Test Notes
| Scenario | Tool | Data | Expected |
|----------|------|------|----------|
| Batch impact test | k6 + batch simulator | Representative load | Delta ≤5% |
| Rolling variance | k6 prolonged | 8h synthetic | Variance ≤10% |
| Regression alert | injected slowdown | Batch window | Alert fired |

### Traceability
Batch impact & scaling governance.
