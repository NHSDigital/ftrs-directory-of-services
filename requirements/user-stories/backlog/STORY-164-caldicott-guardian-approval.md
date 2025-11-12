---
id: STORY-164
title: Caldicott Guardian approval
nfr_refs:
  - GOV-014
  - GOV-005
type: governance
status: draft
owner: data-governance
summary: Obtain Caldicott Guardian approval ensuring ethical handling of confidential data.
---

## Description
Provide data confidentiality practices, access control summary, and anonymisation/pseudonymisation approach for review.

## Acceptance Criteria
- Confidentiality practices document stored.
- Access control summary lists roles & permissions.
- Anonymisation approach reviewed & accepted.
- Approval record (signature/date) archived.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| confidentiality_doc_presence | automated | File exists |
| access_control_summary_scan | automated | Roles/permissions present |
| anonymisation_approach_review | manual | Accepted status |
| approval_record_metadata_check | automated | Signature/date present |

## Traceability
NFRs: GOV-014, GOV-005
