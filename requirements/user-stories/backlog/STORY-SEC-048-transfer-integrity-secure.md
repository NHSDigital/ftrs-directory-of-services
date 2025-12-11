---
story_id: STORY-SEC-048
title: Code/data transfer logs show integrity & secure channels
role: Security Engineer
goal: Deliver: Code/data transfer logs show integrity & secure channels
value: Transfer of code or data maintains integrity and uses secure channels; events are logged.
nfr_refs: [SEC-024]
status: draft
---

## Description

Implement and validate NFR `SEC-024` for domain `security`.

## Acceptance Criteria

- 100% transfers logged; integrity and secure channel verified
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `SEC-024`
- Domain: security
- Control ID: `transfer-integrity-secure`
- Measure: Code/data transfer logs show integrity & secure channels
- Threshold: 100% transfers logged; integrity and secure channel verified
- Tooling: Checksums/signatures + TLS enforcement + audit logs
- Cadence: CI per change + weekly reviews
- Environments: dev, int, ref, prod

## Traceability

- Domain registry: requirements/nfrs/security/nfrs.yaml
