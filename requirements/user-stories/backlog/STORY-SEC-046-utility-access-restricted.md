---
story_id: STORY-SEC-046
title: Utility program access restricted to approved roles
role: Security Engineer
goal: Deliver: Utility program access restricted to approved roles
value: Access to powerful utility programs is restricted to approved roles.
nfr_refs: [SEC-022]
status: draft
---

## Description

Implement and validate NFR `SEC-022` for domain `security`.

## Acceptance Criteria

- Only approved roles can access utility programs
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `SEC-022`
- Domain: security
- Control ID: `utility-access-restricted`
- Measure: Utility program access restricted to approved roles
- Threshold: Only approved roles can access utility programs
- Tooling: RBAC policy checks + audit logs
- Cadence: CI policy checks + monthly audit
- Environments: dev, int, ref, prod


## Traceability

- Domain registry: requirements/nfrs/security/nfrs.yaml
