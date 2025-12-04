---
story_id: STORY-SEC-010
jira_key:
title: "Scan reports zero unmanaged long-lived credentials"
role: Security Engineer
goal: "Implement and validate: Scan reports zero unmanaged long-lived credentials"
value: Reduces risk from forgotten credentials; continuous scanning plus scheduled audits
nfr_refs: [SEC-017]
status: draft
---

## Description

Implement automated validation for: Scan reports zero unmanaged long-lived credentials.

## Acceptance Criteria

1. 0 unmanaged long-lived credentials
2. Tooling: Secret scanners and IAM credential report audit operational
3. Cadence: CI per build and weekly audit validated
4. Environments: dev, int, ref, production covered
5. Monitoring configured and alerting tested

## Non-Functional Acceptance

- Control ID: `zero-long-lived-credentials`
- Threshold: 0 unmanaged long-lived credentials
- Tooling: Secret scanners and IAM credential report audit
- Cadence: CI per build and weekly audit
- Environments: dev, int, ref, production

## Test Strategy

| Test Type   | Tooling           | Focus                 |
| ----------- | ----------------- | --------------------- |
| Compliance  | Automated tooling | Policy enforcement    |
| Integration | CI pipeline       | Continuous validation |
| Audit       | Manual review     | Compliance assessment |

## Out of Scope

Implementation details to be refined during sprint planning

## Implementation Notes

- Reduces risk from forgotten credentials; continuous scanning plus scheduled audits
- Cadence: CI per build + weekly audit
- Status: draft

## Monitoring & Metrics

- `zero_long_lived_credentials_compliance_status` gauge
- `zero_long_lived_credentials_violations_total` counter

## Risks & Mitigation

| Risk                | Impact            | Mitigation            |
| ------------------- | ----------------- | --------------------- |
| Configuration drift | Non-compliance    | Automated remediation |
| Tool failures       | Missed violations | Redundant checks      |

## Traceability

- NFR: SEC-017
- Registry: security/expectations.yaml v1.0

## Open Questions

None
