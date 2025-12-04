---
story_id: STORY-SEC-018
jira_key:
title: Perimeter scan shows no broad whitelist & secure channels
role: Security Engineer
goal: Implement and validate: Perimeter scan shows no broad whitelist & secure channels
value: Confirms perimeter hygiene and secure external exposure
nfr_refs: [SEC-008]
status: draft
---

## Description

Implement automated validation for: Perimeter scan shows no broad whitelist & secure channels.

## Acceptance Criteria

1. No broad whitelists; only secure channels reported
2. Tooling: External perimeter scanner + configuration validation operational
3. Cadence: Monthly + on change validated
4. Environments: int, ref, prod covered
5. Monitoring configured and alerting tested

## Non-Functional Acceptance

- Control ID: `perimeter-scan`\n- Threshold: No broad whitelists; only secure channels reported\n- Tooling: External perimeter scanner + configuration validation\n- Cadence: Monthly + on change\n- Environments: int, ref, prod

## Test Strategy

| Test Type   | Tooling           | Focus                 |
| ----------- | ----------------- | --------------------- |
| Compliance  | Automated tooling | Policy enforcement    |
| Integration | CI pipeline       | Continuous validation |
| Audit       | Manual review     | Compliance assessment |

## Out of Scope

Implementation details to be refined during sprint planning

## Implementation Notes

- Confirms perimeter hygiene and secure external exposure
- Cadence: Monthly + on change
- Status: draft

## Monitoring & Metrics

- `perimeter_scan_compliance_status` gauge
- `perimeter_scan_violations_total` counter

## Risks & Mitigation

| Risk                | Impact            | Mitigation            |
| ------------------- | ----------------- | --------------------- |
| Configuration drift | Non-compliance    | Automated remediation |
| Tool failures       | Missed violations | Redundant checks      |

## Traceability

- NFR: SEC-008
- Registry: security/expectations.yaml v1.0

## Open Questions

None
