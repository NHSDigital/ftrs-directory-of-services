---
id: STORY-059
title: Restrict system utility program access
nfr_refs:
  - SEC-022
type: security
status: draft
owner: platform-team
summary: Limit access to system utility programs to approved identities only.
---

## Description
Catalog system utilities; enforce role-based access; record execution logs; monitor for unauthorized usage attempts.

## Acceptance Criteria
- Utility catalog committed.
- IAM policies restrict execution to approved roles.
- Unauthorized utility execution attempt denied & logged.
- Weekly audit verifies no unauthorized executions.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| utility_catalog_presence | manual | Catalog committed |
| iam_policy_restriction_scan | automated | Only approved roles have perms |
| unauthorized_execution_attempt | automated | Denied & logged |
| weekly_audit_report | manual | No unauthorized events |

## Traceability
NFRs: SEC-022
