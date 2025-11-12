---
id: STORY-160
title: Clinical Safety assurance approval
nfr_refs:
  - GOV-010
type: governance
status: draft
owner: clinical-safety
summary: Obtain Clinical Safety assurance approval including safety case and hazard mitigation.
---

## Description
Prepare clinical safety case with hazard log and mitigation measures; review and approve with relevant safety officer.

## Acceptance Criteria
- Safety case document stored & versioned.
- Hazard log items show mitigation status.
- Approval record includes safety officer signature/date.
- Unmitigated high-risk hazards count = 0.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| safety_case_artifact_presence | automated | File exists |
| hazard_log_scan | automated | All high hazards mitigated |
| approval_signature_presence | manual | Signature/date present |
| unmitigated_high_hazard_alert | automated | Alert if >0 |

## Traceability
NFRs: GOV-010
