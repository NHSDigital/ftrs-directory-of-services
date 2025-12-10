---
story_id: STORY-SEC-040
title: Key rotation events logged; unauthorized access denied
role: Security Engineer
goal: Deliver: Key rotation events logged; unauthorized access denied
value: Cryptographic keys rotate on schedule and unauthorized access attempts are rejected and logged.
nfr_refs: [SEC-013]
status: draft
---

## Description

Implement and validate NFR `SEC-013` for domain `security`.

## Acceptance Criteria

- 100% rotation events logged; 0 unauthorized key access
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `SEC-013`
- Domain: security
- Control ID: `key-rotation-logging`
- Measure: Key rotation events logged; unauthorized access denied
- Threshold: 100% rotation events logged; 0 unauthorized key access
- Tooling: KMS/AWS logs + SIEM correlation
- Cadence: Quarterly audit + CI checks on policy
- Environments: dev, int, ref, prod


## Traceability

- Domain registry: requirements/nfrs/security/nfrs.yaml
