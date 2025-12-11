---
story_id: STORY-SEC-044
title: Remote connections present valid Authority certs
role: Security Engineer
goal: Deliver: Remote connections present valid Authority certs
value: Remote connections present valid certificates from trusted authorities.
nfr_refs: [SEC-020]
status: draft
---

## Description

Implement and validate NFR `SEC-020` for domain `security`.

## Acceptance Criteria

- 100% validation events pass; 0 successful connections with invalid certs
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `SEC-020`
- Domain: security
- Control ID: `authority-cert-validation`
- Measure: Remote connections present valid Authority certs; invalid certs rejected
- Threshold: 100% validation events pass; 0 successful connections with invalid certs
- Tooling: TLS config tests + runtime observation in logs
- Cadence: CI policy validation + runtime checks
- Environments: int, ref, prod

## Traceability

- Domain registry: requirements/nfrs/security/nfrs.yaml
