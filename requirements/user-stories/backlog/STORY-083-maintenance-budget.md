---
id: STORY-083
title: Enforce maintenance duration budget
nfr_refs:
  - AVAIL-004
  - AVAIL-005
type: availability
status: draft
owner: platform-team
summary: Track and enforce monthly maintenance budget ≤150 minutes and ≤60 minutes per single activity.
---

## Description
Automate aggregation of planned change durations; alert when 75% of monthly maintenance budget consumed; ensure Tuesday 09:00-10:00 window used for standard tasks and smoke tests confirm minimal impairment.

## Acceptance Criteria
- Script aggregates maintenance durations; output artifact stored.
- Monthly total never exceeds 150 minutes.
- Single activity never exceeds 60 minutes.
- Smoke tests during maintenance window pass (core search functionality).
- Alert triggers at 112.5 minutes (75%) consumption.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| duration_aggregation_script_run | automated | Report generated |
| monthly_budget_threshold_check | automated | ≤150 minutes |
| single_activity_duration_check | automated | ≤60 minutes |
| smoke_tests_window | automated | All pass |
| budget_alert_simulation | automated | Alert at 75% threshold |

## Traceability
NFRs: AVAIL-004, AVAIL-005
