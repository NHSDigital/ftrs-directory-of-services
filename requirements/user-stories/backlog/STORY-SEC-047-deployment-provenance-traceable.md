---
story_id: STORY-SEC-047
title: Deployment provenance shows unique traceable accounts
role: Security Engineer
goal: Deliver: Deployment provenance shows unique traceable accounts
value: Deployment provenance shows traceable unique accounts per automated pipeline stage.
nfr_refs: [SEC-023]
status: draft
---

## Description

Implement and validate NFR `SEC-023` for domain `security`.

## Acceptance Criteria

- All deployments traceable to unique accounts
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `SEC-023`
- Domain: security
- Control ID: `deployment-provenance-traceable`
- Measure: Deployment provenance shows unique traceable accounts
- Threshold: All deployments traceable to unique accounts
- Tooling: CI/CD audit trails + commit signing
- Cadence: Continuous
- Environments: dev, int, ref, prod

## Traceability

- Domain registry: requirements/nfrs/security/nfrs.yaml
