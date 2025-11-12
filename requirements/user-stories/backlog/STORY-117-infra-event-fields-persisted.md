---
id: STORY-117
title: Infrastructure event fields persisted
nfr_refs:
  - OBS-014
  - OBS-013
type: observability
status: draft
owner: platform-team
summary: Persist required infrastructure event fields (params, response, changes, datetime, sequence) for tamper detection & replay.
---

## Description
Extend infra logging schema to include mandatory fields enabling reliable reconstruction and integrity checks.

## Acceptance Criteria
- Log entries contain all required fields.
- Schema validation fails build on missing field.
- Replay script reconstructs infra change sequence.
- Tamper (field removal) triggers integrity alert.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| schema_validation_test | automated | Pass with all fields |
| replay_sequence_test | automated | Sequence reconstructed |
| missing_field_build_fail | automated | Build fails |
| tamper_alert_simulation | automated | Alert fires |

## Traceability
NFRs: OBS-014, OBS-013
