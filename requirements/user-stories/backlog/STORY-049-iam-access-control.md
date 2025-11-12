---
id: STORY-049
title: Central IAM access control
nfr_refs:
  - SEC-012
type: security
status: draft
owner: platform-team
summary: Govern human and system access to application resources via defined IAM roles and policies.
---

## Description
Create least-privilege IAM roles and policies for all resource interactions; enforce separation of duties; implement periodic review.

## Acceptance Criteria
- Role & policy catalogue created.
- Least privilege evaluation shows no excessive permissions.
- Quarterly access review executed & logged.
- Attempted unauthorized access denied & audited.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| role_policy_catalog_presence | manual | Catalog committed |
| permission_excess_scan | automated | No excessive perms flagged |
| quarterly_review_execution | manual | Review log present |
| unauthorized_access_attempt | automated | Denied & audit entry |

## Traceability
NFRs: SEC-012
