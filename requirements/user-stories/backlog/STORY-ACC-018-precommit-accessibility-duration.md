---
story_id: STORY-ACC-018
title: Pre-commit checks complete <30s
role: UX Engineer
goal: Deliver: Pre-commit checks complete <30s
value: Pre-commit accessibility checks finish within target duration.
nfr_refs: [ACC-018]
status: draft
---

## Description

Implement and validate NFR `ACC-018` for domain `accessibility`.

## Acceptance Criteria

- Pre-commit accessibility checks complete < 30s
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `ACC-018`
- Domain: accessibility
- Control ID: `precommit-accessibility-duration`
- Measure: Pre-commit checks complete <30s
- Threshold: Pre-commit accessibility checks complete < 30s
- Tooling: Pre-commit runner
- Cadence: On commit
- Environments: dev

## Traceability

- Domain registry: requirements/nfrs/accessibility/nfrs.yaml
