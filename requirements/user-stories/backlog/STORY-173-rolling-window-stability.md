---
id: STORY-173
title: 8h rolling window performance stability
nfr_refs:
  - PERF-008
  - PERF-009
type: performance
status: draft
owner: performance-team
summary: Monitor and maintain ≤10% variance in P95 latency across rolling 8h windows.
---

## Description
Compute rolling 8h window P95 for each action; track variance vs previous window; ensure predictable performance and trigger alert beyond threshold.

## Acceptance Criteria
- Dashboard panel shows rolling 8h P95 per action.
- Variance calculation job stored & scheduled.
- Variance ≤10% for all monitored windows.
- Breach creates incident ticket automatically.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| variance_job_execution_test | automated | Job success & metrics |
| dashboard_panel_presence | automated | Panel renders data |
| variance_threshold_assertion | automated | ≤10% |
| breach_ticket_creation_simulation | automated | Ticket created |

## Traceability
NFRs: PERF-008, PERF-009
