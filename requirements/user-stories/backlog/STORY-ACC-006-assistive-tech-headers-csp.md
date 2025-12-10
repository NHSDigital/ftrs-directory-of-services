---
story_id: STORY-ACC-006
title: Assistive tech not blocked by headers/CSP
role: UX Engineer
goal: Deliver: Assistive tech not blocked by headers/CSP
value: Assistive technologies are not blocked by headers or Content Security Policy (CSP).
nfr_refs: [ACC-006]
status: draft
---

## Description

Implement and validate NFR `ACC-006` for domain `accessibility`.

## Acceptance Criteria

- Headers/CSP allow screen readers; tests pass for supported AT
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `ACC-006`
- Domain: accessibility
- Control ID: `assistive-tech-headers-csp`
- Measure: Assistive tech not blocked by headers/CSP
- Threshold: Headers/CSP allow screen readers; tests pass for supported AT
- Tooling: AT test harness + response header checks
- Cadence: Pre-release
- Environments: ref


## Traceability

- Domain registry: requirements/nfrs/accessibility/nfrs.yaml
