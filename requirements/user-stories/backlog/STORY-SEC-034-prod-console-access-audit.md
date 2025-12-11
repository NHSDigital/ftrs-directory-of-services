---
story_id: STORY-SEC-034
title: No direct prod console queries detected in audit period
role: Security Engineer
goal: Deliver: No direct prod console queries detected in audit period
value: No direct production console queries by engineers outside approved, audited break-glass processes.
nfr_refs: [SEC-006]
status: draft
---

## Description

Implement and validate NFR `SEC-006` for domain `security`.

## Acceptance Criteria

- 0 non-approved console queries in audit period
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `SEC-006`
- Domain: security
- Control ID: `prod-console-access-audit`
- Measure: No direct prod console queries detected in audit period
- Threshold: 0 non-approved console queries in audit period
- Tooling: CloudTrail + SIEM audit queries
- Cadence: Weekly audit + alerting
- Environments: prod

## Traceability

- Domain registry: requirements/nfrs/security/nfrs.yaml
