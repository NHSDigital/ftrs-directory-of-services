---
story_id: STORY-ACC-009
title: Keyboard tab order regression test passes
role: UX Engineer
goal: Deliver: Keyboard tab order regression test passes
value: Keyboard-only navigation preserves logical tab order without traps.
nfr_refs: [ACC-009]
status: draft
---

## Description

Implement and validate NFR `ACC-009` for domain `accessibility`.

## Acceptance Criteria

- Tab order matches expected flow; no focus loss
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `ACC-009`
- Domain: accessibility
- Control ID: `keyboard-tab-order`
- Measure: Keyboard tab order regression test passes
- Threshold: Tab order matches expected flow; no focus loss
- Tooling: Automated tab order tests + manual verification
- Cadence: CI per build + pre-release
- Environments: int, ref

## Traceability

- Domain registry: requirements/nfrs/accessibility/nfrs.yaml
