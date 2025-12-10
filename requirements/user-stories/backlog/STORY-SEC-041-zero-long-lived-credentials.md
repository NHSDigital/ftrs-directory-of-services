---
story_id: STORY-SEC-041
title: Scan reports zero unmanaged long-lived credentials
role: Security Engineer
goal: Deliver: Scan reports zero unmanaged long-lived credentials
value: No long-lived unmanaged credentials; periodic scans confirm only managed secrets exist.
nfr_refs: [SEC-017]
status: draft
---

## Description

Implement and validate NFR `SEC-017` for domain `security`.

## Acceptance Criteria

- 0 unmanaged long-lived credentials
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `SEC-017`
- Domain: security
- Control ID: `zero-long-lived-credentials`
- Measure: Scan reports zero unmanaged long-lived credentials
- Threshold: 0 unmanaged long-lived credentials
- Tooling: Secret scanners + IAM credential report audit
- Cadence: CI per build + weekly audit
- Environments: dev, int, ref, prod


## Traceability

- Domain registry: requirements/nfrs/security/nfrs.yaml
