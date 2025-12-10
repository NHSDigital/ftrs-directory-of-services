---
story_id: STORY-SEC-049
title: API responses contain no unencrypted PID fields
role: Security Engineer
goal: Deliver: API responses contain no unencrypted PID fields
value: API responses never include unencrypted patient identifiable data (PID) fields.
nfr_refs: [SEC-026]
status: draft
---

## Description

Implement and validate NFR `SEC-026` for domain `security`.

## Acceptance Criteria

- 0 occurrences of unencrypted PID in responses
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `SEC-026`
- Domain: security
- Control ID: `pid-no-plaintext-response`
- Measure: API responses contain no unencrypted PID fields
- Threshold: 0 occurrences of unencrypted PID in responses
- Tooling: Integration tests + response scanners
- Cadence: CI per build + periodic production sampling
- Environments: int, ref, prod

## Traceability

- Domain registry: requirements/nfrs/security/nfrs.yaml
