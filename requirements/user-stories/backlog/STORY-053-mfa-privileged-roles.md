---
id: STORY-053
title: Enforce MFA for privileged infra roles
nfr_refs:
  - SEC-016
type: security
status: draft
owner: platform-team
summary: Require multi-factor authentication for all privileged infrastructure human roles.
---

## Description
Identify privileged roles; configure IAM and IdP integration to mandate MFA; test enforcement and logging.

## Acceptance Criteria
- List of privileged roles documented.
- MFA policy attached to each role.
- Attempted login without MFA denied & logged.
- Monthly report shows 100% MFA compliance.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| privileged_role_list_presence | manual | Document committed |
| mfa_policy_attachment_scan | automated | All roles have MFA policy |
| no_mfa_login_attempt | automated | Denied & audit log |
| monthly_mfa_compliance_report | manual | 100% compliance |

## Traceability
NFRs: SEC-016
