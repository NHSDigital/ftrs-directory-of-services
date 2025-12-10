---
story_id: STORY-ACC-010
title: Focus trap tests pass for modals/overlays
role: UX Engineer
goal: Deliver: Focus trap tests pass for modals/overlays
value: Focus handling works for modals and overlays without trapping user.
nfr_refs: [ACC-010]
status: draft
---

## Description

Implement and validate NFR `ACC-010` for domain `accessibility`.

## Acceptance Criteria

- No escape from focus trap; correct focus restoration
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `ACC-010`
- Domain: accessibility
- Control ID: `focus-trap-tests`
- Measure: Focus trap tests pass for modals/overlays
- Threshold: No escape from focus trap; correct focus restoration
- Tooling: Automated focus tests + manual checks
- Cadence: CI per build + pre-release
- Environments: int, ref


## Traceability

- Domain registry: requirements/nfrs/accessibility/nfrs.yaml
