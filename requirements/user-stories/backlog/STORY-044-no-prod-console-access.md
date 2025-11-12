---
id: STORY-044
title: Eliminate direct prod console data access
nfr_refs:
  - SEC-006
type: security
status: draft
owner: platform-team
summary: Prevent and monitor for any direct interactive console queries against production data stores.
---

## Description
Restrict production data access to application/API pathways; implement alerting for interactive console attempts; enforce break-glass procedure for urgent cases.

## Acceptance Criteria
- IAM policies prohibit direct query permissions.
- Break-glass role requires MFA and approval ticket.
- Simulated console query attempt denied and alert raised.
- Monthly audit shows zero unauthorized direct queries.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| iam_policy_scan | automated | No direct query perms |
| break_glass_access_test | manual | MFA + approval required |
| unauthorized_console_attempt | automated | Denied + alert logged |
| monthly_audit_report | manual | Zero unauthorized events |

## Traceability
NFRs: SEC-006
