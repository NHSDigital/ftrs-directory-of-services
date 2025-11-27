---
story_id: STORY-ACC-004
jira_key:
title: Focus trap tests pass for modals/overlays
role: UX Engineer
goal: Implement and validate: Focus trap tests pass for modals/overlays
value: Ensures accessible modal behaviour
nfr_refs: [ACC-010]
status: draft
---

## Description

Implement automated validation for: Focus trap tests pass for modals/overlays.

## Acceptance Criteria

1. Focus trap contains focus within modal; Esc key restores focus correctly (WCAG 2.1 SC 2.4.3)
2. Tab cycles within modal; Shift+Tab cycles backward
3. Esc key closes modal and returns focus to trigger element
4. Tooling: Automated focus tests + manual checks operational
5. Cadence: CI per build + pre-release validated
6. Environments: int, ref covered
7. Monitoring configured and alerting tested

## Non-Functional Acceptance

- Control ID: `focus-trap-tests`\n- Threshold: 100% modals trap focus; 100% allow Esc key escape; focus restoration verified\n- Tooling: Automated focus tests + manual checks\n- Cadence: CI per build + pre-release\n- Environments: int, ref

## Test Strategy

| Test Type   | Tooling           | Focus                 |
| ----------- | ----------------- | --------------------- |
| Compliance  | Automated tooling | Policy enforcement    |
| Integration | CI pipeline       | Continuous validation |
| Audit       | Manual review     | Compliance assessment |

## Out of Scope

Implementation details to be refined during sprint planning

## Implementation Notes

- Ensures accessible modal behaviour
- Cadence: CI per build + pre-release
- Status: draft

## Monitoring & Metrics

- `focus_trap_tests_compliance_status` gauge
- `focus_trap_tests_violations_total` counter

## Risks & Mitigation

| Risk                | Impact            | Mitigation            |
| ------------------- | ----------------- | --------------------- |
| Configuration drift | Non-compliance    | Automated remediation |
| Tool failures       | Missed violations | Redundant checks      |

## Traceability

- NFR: ACC-010
- Registry: accessibility/expectations.yaml v1.0

## Open Questions

None
