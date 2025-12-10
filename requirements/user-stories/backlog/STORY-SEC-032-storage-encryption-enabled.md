---
story_id: STORY-SEC-032
title: Storage services show encryption enabled
role: Security Engineer
goal: Deliver: Storage services show encryption enabled
value: Every storage service (S3, RDS, etc.) shows encryption enabled with managed or customer keys.
nfr_refs: [SEC-004]
status: draft
---

## Description

Implement and validate NFR `SEC-004` for domain `security`.

## Acceptance Criteria

- 100% storage resources encrypted at rest
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `SEC-004`
- Domain: security
- Control ID: `storage-encryption-enabled`
- Measure: Storage services show encryption enabled
- Threshold: 100% storage resources encrypted at rest
- Tooling: AWS Config rules + Terraform policy checks
- Cadence: Continuous + CI enforcement
- Environments: dev, int, ref, prod


## Traceability

- Domain registry: requirements/nfrs/security/nfrs.yaml
