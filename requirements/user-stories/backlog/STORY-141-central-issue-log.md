---
id: STORY-141
title: Maintain central accessibility issue log
nfr_refs:
  - ACC-013
  - ACC-015
type: accessibility
status: draft
owner: accessibility-team
summary: Maintain an up-to-date central log of accessibility defects, exceptions, and remediation status.
---

## Description
Implement shared log (markdown or issue tracking board) aggregating accessibility-related items across applications with status, severity, target fix date.

## Acceptance Criteria
- Log includes fields: id, severity, description, status, target_fix_date, exception_flag.
- Updated at least weekly (timestamp recorded).
- Random audit finds no stale (>30d) critical issues without justification.
- Exportable snapshot generated monthly.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| log_schema_validation | automated | Required fields present |
| weekly_update_timestamp_check | automated | Recent timestamp |
| stale_issue_audit | manual | None stale without justification |
| monthly_snapshot_generation | automated | Snapshot file created |

## Traceability
NFRs: ACC-013, ACC-015
