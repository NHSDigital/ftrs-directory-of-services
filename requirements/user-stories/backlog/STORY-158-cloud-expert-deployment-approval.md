---
id: STORY-158
title: Cloud Expert deployment approval
nfr_refs:
  - GOV-008
  - GOV-002
type: governance
status: draft
owner: cloud-architecture
summary: Secure Cloud Expert approval of deployed environment post-review.
---

## Description
Validate deployed infrastructure matches reviewed Well-Architected design; capture deviations & remediation closure.

## Acceptance Criteria
- Deployment checklist completed & stored.
- Deviations list empty or items remediated.
- Cloud Expert sign-off record includes certification ID.
- Drift detection report linked.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| deployment_checklist_presence | automated | Checklist file exists |
| deviation_list_scan | automated | No unresolved deviations |
| signoff_cert_id_validation | automated | ID format valid |
| drift_report_link_check | automated | Link accessible |

## Traceability
NFRs: GOV-008, GOV-002
