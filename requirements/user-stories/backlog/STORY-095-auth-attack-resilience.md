---
id: STORY-095
title: Authentication attack resilience
nfr_refs:
  - REL-007
  - SEC-016
type: reliability
status: draft
owner: security-team
summary: Detect and mitigate brute force, replay, and credential stuffing attempts while enforcing MFA.
---

## Description
Implement rate limiting, adaptive authentication, MFA enforcement, and anomaly detection; simulate various auth attacks to confirm mitigations and alert generation.

## Acceptance Criteria
- Brute force simulation triggers rate limiting & alert.
- Replay attempt invalidated by nonce/timestamp controls.
- Credential stuffing flagged by anomaly detection thresholds.
- MFA required for privileged role login attempts.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| brute_force_simulation | automated | Rate limiting + alert |
| replay_attack_test | automated | Attempt rejected |
| credential_stuffing_simulation | automated | Alert & block |
| mfa_privileged_login_test | automated | MFA enforced |

## Traceability
NFRs: REL-007, SEC-016
