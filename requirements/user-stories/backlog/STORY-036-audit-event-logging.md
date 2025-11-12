---
id: STORY-036
title: Audit event logging for user-centric actions
nfr_refs:
  - OBS-022
type: observability
status: draft
owner: compliance-team
summary: Record audit events for user-centric actions supporting compliance & subject access requests.
---

## Description
Generate audit events for create/update/read sensitive operations including user identity and transaction metadata.

## Acceptance Criteria
- Audit log contains user identifier, action, resource, timestamp, transaction_id.
- Subject access request reconstruction succeeds.
- Tampered audit entry detection triggers alert.
- Access to audit logs restricted & monitored.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| sar_reconstruction_test | automated | Complete audit chain |
| audit_log_schema_validation | automated | Required fields present |
| tamper_detection_simulation | automated | Alert fires |
| access_control_audit_log | automated | Unauthorized denied |

## Traceability
NFRs: OBS-022
