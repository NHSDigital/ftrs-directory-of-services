---
id: STORY-174
title: Performance regression alerting
nfr_refs:
  - PERF-009
  - PERF-002
type: performance
status: draft
owner: operations-team
summary: Alert on >10% increase in P95 latency for any defined action.
---

## Description
Implement monitoring rule comparing current P95 vs baseline; trigger alert & incident workflow when threshold exceeded; include diagnostic snapshot.

## Acceptance Criteria
- Alert rule configured for each action threshold (>10% increase).
- Simulated regression triggers alert & incident ticket.
- Alert payload includes action name, previous P95, current P95, delta%.
- Runbook link embedded in ticket.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| regression_simulation_test | automated | Alert + ticket |
| alert_payload_field_validation | automated | Required fields present |
| runbook_link_presence_test | automated | Link accessible |
| false_positive_filter_check | automated | No alert under normal variance |

## Traceability
NFRs: PERF-009, PERF-002
