---
id: STORY-155
title: GDPR compliance sign-off
nfr_refs:
  - GOV-005
  - GOV-011
type: governance
status: draft
owner: information-governance
summary: Obtain formal Information Governance sign-off for GDPR compliance.
---

## Description
Prepare DPIA, data flow diagrams, retention schedule, and security controls summary. Submit to IG for review and sign-off.

## Acceptance Criteria
- DPIA file present & approved.
- Data flow diagram stored with version.
- Retention schedule aligns with IG policy.
- Sign-off record includes reviewer & date.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| dpia_artifact_presence | automated | DPIA file exists |
| data_flow_diagram_version_check | automated | Version metadata present |
| retention_schedule_policy_diff | automated | No policy deviations |
| signoff_metadata_validation | automated | Reviewer/date present |

## Traceability
NFRs: GOV-005, GOV-011
