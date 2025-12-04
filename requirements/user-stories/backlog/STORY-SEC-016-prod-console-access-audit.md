---
story_id: STORY-SEC-016
jira_key:
title: No direct prod console queries detected in audit period
role: Security Engineer
goal: "Implement and validate: No direct prod console queries detected in audit period"
value: Detects improper direct access to production consoles
nfr_refs: [SEC-006]
status: draft
---

## Description

Implement automated validation for: No direct prod console queries detected in audit period.

## Acceptance Criteria

1. 0 non-approved console queries in audit period
2. Tooling: CloudTrail + SIEM audit queries operational
3. Cadence: Weekly audit and alerting validated
4. Environments: prod covered
5. Monitoring configured and alerting tested

## Non-Functional Acceptance

- Control ID: `prod-console-access-audit`
- Threshold: 0 non-approved console queries in audit period
- Tooling: CloudTrail and SIEM audit queries
- Cadence: Weekly audit and alerting
- Environments: prod

## Test Strategy

| Test Type   | Tooling           | Focus                 |
| ----------- | ----------------- | --------------------- |
| Compliance  | Automated tooling | Policy enforcement    |
| Integration | CI pipeline       | Continuous validation |
| Audit       | Manual review     | Compliance assessment |

## Out of Scope

Implementation details to be refined during sprint planning

## Implementation Notes

- Detects improper direct access to production consoles
- Cadence: Weekly audit + alerting
- Status: draft

## Monitoring & Metrics

- `prod_console_access_audit_compliance_status` gauge
- `prod_console_access_audit_violations_total` counter

## Risks & Mitigation

| Risk                | Impact            | Mitigation            |
| ------------------- | ----------------- | --------------------- |
| Configuration drift | Non-compliance    | Automated remediation |
| Tool failures       | Missed violations | Redundant checks      |

## Traceability

- NFR: SEC-006
- Registry: security/expectations.yaml v1.0

## Open Questions

None
