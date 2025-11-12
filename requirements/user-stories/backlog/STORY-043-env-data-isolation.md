---
id: STORY-043
title: Enforce environment data isolation
nfr_refs:
  - SEC-005
type: security
status: draft
owner: platform-team
summary: Prevent cross-environment data access ensuring dev/test cannot read prod datasets and vice versa.
---

## Description
Implement access controls and naming conventions guaranteeing that resources in each environment only access data scoped to that environment. Validate with negative tests.

## Acceptance Criteria
- Distinct KMS keys / policies per environment.
- IAM roles scoped to environment resources only.
- Negative test: dev role access to prod data denied.
- Audit report enumerates zero cross-env success attempts.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| iam_policy_scope_scan | automated | No cross-env ARNs referenced |
| kms_key_segregation | manual | Separate keys per env |
| negative_access_test | automated | Access denied & logged |
| audit_cross_env_report | manual | Zero successful events |

## Traceability
NFRs: SEC-005
