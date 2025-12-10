---
story_id: STORY-ACC-019
title: CI accessibility stage completes <5min
role: UX Engineer
goal: Deliver: CI accessibility stage completes <5min
value: CI accessibility stage completes within target time window.
nfr_refs: [ACC-019]
status: draft
---

## Description

Implement and validate NFR `ACC-019` for domain `accessibility`.

## Acceptance Criteria

- CI job < 5 minutes; breaches trigger optimisation ticket
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `ACC-019`
- Domain: accessibility
- Control ID: `ci-accessibility-duration-policy`
- Measure: CI accessibility stage completes <5min
- Threshold: CI job < 5 minutes; breaches trigger optimisation ticket
- Tooling: CI timer + policy
- Cadence: CI per build
- Environments: int


## Traceability

- Domain registry: requirements/nfrs/accessibility/nfrs.yaml
