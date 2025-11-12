---
id: STORY-047
title: Annual external penetration testing
nfr_refs:
  - SEC-010
type: security
status: draft
owner: security-team
summary: Conduct independent penetration test annually and after major perimeter changes.
---

## Description
Schedule external accredited testers to perform comprehensive penetration test; track findings and remediation; repeat after significant architecture changes.

## Acceptance Criteria
- Pen test statement of work approved.
- Report stored with classification of findings.
- Critical/high findings have remediation tickets.
- Follow-up verification retest shows closure of critical issues.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| sow_approval_check | manual | Approved SOW document |
| report_storage_presence | manual | Report artifact committed |
| remediation_ticket_audit | automated | Tickets for each high/critical |
| retest_verification | manual | Critical issues resolved |

## Traceability
NFRs: SEC-010
