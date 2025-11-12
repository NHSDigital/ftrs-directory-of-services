---
id: STORY-010
title: Maintain ongoing cryptographic policy compliance
nfr_refs:
  - SEC-001
type: security
status: draft
owner: security-team
summary: Embed continuous monitoring ensuring future changes retain approved algorithms.
---

## Description
Integrate cryptographic policy checks into CI/CD so any new service or configuration change is validated against approved algorithm list before deployment.

## Acceptance Criteria
- Pre-deploy step fails on unapproved algorithms.
- Change introducing new cipher triggers automatic review ticket.
- Alert raised if runtime config drifts from approved set.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| ci_policy_gate_test | automated | Build fails on disallowed config |
| new_cipher_change_detection | automated | Ticket created & linked |
| runtime_drift_alert_simulation | automated | Alert delivered to channel |

## Traceability
NFRs: SEC-001
