---
id: STORY-132
title: Accessibility defect parity enforcement
nfr_refs:
  - ACC-004
  - ACC-012
type: accessibility
status: draft
owner: product-team
summary: Ensure accessibility defects receive parity in prioritisation and SLA tracking.
---

## Description
Configure defect tracker workflows so accessibility issues have equivalent severity classification, SLAs, and reporting as functional defects.

## Acceptance Criteria
- Defect tracker shows matching SLA fields for accessibility issues.
- Weekly report includes accessibility defect counts.
- New critical accessibility defect auto-tags release blocker.
- Random audit shows no downgrading without justification.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| tracker_field_presence | automated | SLA fields populated |
| weekly_report_scan | automated | Accessibility section present |
| critical_defect_blocker_test | automated | Release blocked |
| downgrade_audit_review | manual | Justifications valid |

## Traceability
NFRs: ACC-004, ACC-012
