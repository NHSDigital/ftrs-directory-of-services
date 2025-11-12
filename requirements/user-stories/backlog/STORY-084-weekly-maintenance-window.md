---
id: STORY-084
title: Weekly maintenance window operations
nfr_refs:
  - AVAIL-005
type: availability
status: draft
owner: platform-team
summary: Execute Tuesday 09:00-10:00 maintenance window with documented tasks and minimal user impact.
---

## Description
Establish runbook for weekly window; perform upgrades or preventive tasks; capture metrics for any impairment; run smoke tests before and after; communicate status to stakeholders.

## Acceptance Criteria
- Window runbook committed with task checklist.
- Pre/post smoke test results archived.
- Any functional impairment limited and documented.
- Stakeholder notification sent prior to window start.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| runbook_presence | manual | Runbook committed |
| smoke_test_pre_post | automated | Pass both phases |
| stakeholder_notification_test | manual | Notification log present |
| impairment_metrics_capture | manual | Metrics recorded if impairment |

## Traceability
NFRs: AVAIL-005
