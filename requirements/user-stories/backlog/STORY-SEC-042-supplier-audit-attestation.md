---
story_id: STORY-SEC-042
title: Supplier audit attestation stored & verified
role: Security Engineer
goal: Deliver: Supplier audit attestation stored & verified
value: Third-party supplier security attestation is collected and stored for audit.
nfr_refs: [SEC-018]
status: draft
---

## Description

Implement and validate NFR `SEC-018` for domain `security`.

## Acceptance Criteria

- Attestations current; verification completed
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `SEC-018`
- Domain: security
- Control ID: `supplier-audit-attestation`
- Measure: Supplier audit attestation stored & verified
- Threshold: Attestations current; verification completed
- Tooling: Supplier management system + evidence repository
- Cadence: Annual + on contract change
- Environments: prod

## Traceability

- Domain registry: requirements/nfrs/security/nfrs.yaml
