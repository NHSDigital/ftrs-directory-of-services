---
id: STORY-123
title: Operational event fields incl. transaction id
nfr_refs:
  - OBS-021
  - OBS-019
type: observability
status: draft
owner: platform-team
summary: Ensure operational events include required fields including transaction identifiers.
---

## Description
Enhance operational event schema with transaction_id, component, action, timestamp to support subject access and reconstruction.

## Acceptance Criteria
- Operational events contain mandatory fields.
- Schema validation fails if transaction_id missing.
- Subject access reconstruction uses events successfully.
- Tamper attempt on event fields detected & alerted.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| event_schema_validation | automated | Pass with fields |
| missing_transaction_id_test | automated | Build fails |
| sar_reconstruction_using_events | automated | Success |
| tamper_alert_simulation | automated | Alert fires |

## Traceability
NFRs: OBS-021, OBS-019
