---
story_id: STORY-SEC-033
title: Cross-environment data access attempts denied
role: Security Engineer
goal: Deliver: Cross-environment data access attempts denied
value: Strict environment isolation: data access from one environment to another is prevented.
nfr_refs: [SEC-005]
status: draft
---

## Description

Implement and validate NFR `SEC-005` for domain `security`.

## Acceptance Criteria

- 100% denial; audit logs prove enforcement
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `SEC-005`
- Domain: security
- Control ID: `cross-env-access-denied`
- Measure: Cross-env data access attempts denied and logged
- Threshold: 100% denial; audit logs prove enforcement
- Tooling: IAM policies + SCP guardrails + audit log queries
- Cadence: CI policy checks + monthly audit review
- Environments: dev, int, ref, prod


## Traceability

- Domain registry: requirements/nfrs/security/nfrs.yaml
