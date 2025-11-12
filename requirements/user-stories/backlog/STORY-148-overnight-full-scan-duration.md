---
id: STORY-148
title: Overnight full accessibility scan duration
nfr_refs:
  - ACC-020
  - ACC-002
type: accessibility
status: draft
owner: qa-team
summary: Keep overnight full application accessibility scan duration under 2 hours.
---

## Description
Execute comprehensive nightly accessibility scan covering all pages/components; tune concurrency & scope to meet duration target while retaining completeness.

## Acceptance Criteria
- Scan completes <2h median across last 14 runs.
- Coverage report shows 100% critical pages scanned.
- Duration breach triggers alert & optimization ticket.
- Historical duration trend stored.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| nightly_scan_duration_series | automated | All <2h |
| coverage_report_validation | automated | 100% coverage |
| duration_breach_alert_test | automated | Alert fired |
| trend_history_presence | automated | Trend file present |

## Traceability
NFRs: ACC-020, ACC-002
