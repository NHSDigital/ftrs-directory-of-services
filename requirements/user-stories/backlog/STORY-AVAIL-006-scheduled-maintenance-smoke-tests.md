---
story_id: STORY-AVAIL-006
title: Tuesday window executed; smoke tests pass
role: SRE
goal: Deliver: Tuesday window executed; smoke tests pass
value: Scheduled maintenance executes successfully with passing smoke tests afterward.
nfr_refs: [AVAIL-005]
status: draft
---

## Description

Implement and validate NFR `AVAIL-005` for domain `availability`.

## Acceptance Criteria

- Maintenance completes; post-window smoke tests 100% pass; no Sev-1/2 incidents
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `AVAIL-005`
- Domain: availability
- Control ID: `scheduled-maintenance-smoke-tests`
- Measure: Tuesday window executed; smoke tests pass
- Threshold: Maintenance completes; post-window smoke tests 100% pass; no Sev-1/2 incidents
- Tooling: Deployment controller + smoke test suite + incident log
- Cadence: Weekly maintenance window
- Environments: prod

## Traceability

- Domain registry: requirements/nfrs/availability/nfrs.yaml
