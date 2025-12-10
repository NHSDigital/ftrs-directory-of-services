---
story_id: STORY-ACC-021
title: Accessibility regression triggers alert
role: UX Engineer
goal: Deliver: Accessibility regression triggers alert
value: Regression in accessibility triggers automated alert.
nfr_refs: [ACC-021]
status: draft
---

## Description

Implement and validate NFR `ACC-021` for domain `accessibility`.

## Acceptance Criteria

- Alert fires on score drop or new critical issue
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `ACC-021`
- Domain: accessibility
- Control ID: `accessibility-regression-alert`
- Measure: Accessibility regression triggers alert
- Threshold: Alert fires on score drop or new critical issue
- Tooling: Accessibility scanner + alerting
- Cadence: CI per build
- Environments: int

## Traceability

- Domain registry: requirements/nfrs/accessibility/nfrs.yaml
