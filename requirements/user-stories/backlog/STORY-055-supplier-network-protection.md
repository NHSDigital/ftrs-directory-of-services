---
id: STORY-055
title: Protect supplier networks and restrict access
nfr_refs:
  - SEC-018
type: security
status: draft
owner: supplier-team
summary: Ensure supplier-controlled networks/services are protected and only Authority-approved entities have access.
---

## Description
Validate supplier network security posture; ensure access lists align with approved entities; capture attestation and audit evidence.

## Acceptance Criteria
- Supplier security attestation document stored.
- Access list matches approved entities only.
- Unauthorized access attempt test denied & logged.
- Quarterly review updates attestation status.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| attestation_presence | manual | Document committed |
| access_list_validation | automated | Only approved entities |
| unauthorized_access_attempt | automated | Denied & logged |
| quarterly_review_log | manual | Review entry present |

## Traceability
NFRs: SEC-018
