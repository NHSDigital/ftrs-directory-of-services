---
id: STORY-034
title: Infrastructure log repository secure & queryable
nfr_refs:
  - OBS-013
type: observability
status: draft
owner: platform-team
summary: Provide secure, queryable repository for infrastructure logs supporting forensics & compliance.
---

## Description
Centralise infrastructure logs with role-based access and indexed fields to enable fast forensic queries.

## Acceptance Criteria
- Access restricted to authorised roles; unauthorised attempt denied.
- Query returns expected fields for sample event.
- Encryption at rest enabled for log storage.
- Retention policy applied per compliance standard.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| access_control_negative_test | automated | Access denied |
| sample_query_field_check | automated | Fields present |
| encryption_flag_check | automated | Encryption enabled |
| retention_policy_scan | automated | Policy matches config |

## Traceability
NFRs: OBS-013
