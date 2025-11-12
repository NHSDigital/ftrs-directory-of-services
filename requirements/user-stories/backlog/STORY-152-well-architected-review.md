---
id: STORY-152
title: Well-Architected Framework review completion
nfr_refs:
  - GOV-002
  - GOV-004
type: governance
status: draft
owner: cloud-architecture
summary: Complete formal Well-Architected review and close remediation actions.
---

## Description
Run AWS/Azure Well-Architected tool or manual checklist; capture risks; assign remediation tasks; confirm closure before release.

## Acceptance Criteria
- Review report stored with date & reviewer certification ID.
- All high & medium remediation actions closed or risk accepted.
- Action tracker shows owner & due date for each item.
- Follow-up review scheduled if open risks remain.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| report_artifact_presence | automated | File exists & metadata present |
| action_tracker_scan | automated | All actions resolved or accepted |
| unclosed_action_alert_test | automated | Alert if high open |
| reviewer_cert_id_validation | automated | Certification ID format valid |

## Traceability
NFRs: GOV-002, GOV-004
