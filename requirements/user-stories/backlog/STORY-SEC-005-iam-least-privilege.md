---
story_id: STORY-SEC-005
jira_key:
title: IAM policy review confirms least privilege for system roles
role: Security Engineer
goal: "Implement and validate: IAM policy review confirms least privilege for system roles"
value: Continuous analysis prevents privilege creep; periodic review catches drift
nfr_refs: [SEC-012]
status: draft
---

## Description

Implement automated validation for: IAM policy review confirms least privilege for system roles.

## Acceptance Criteria

1. > = 95% policies compliant; no wildcard resource; explicit actions only
2. Tooling: IAM Access Analyzer and policy linters operational
3. Cadence: CI per change and quarterly audit validated
4. Environments: dev, int, ref, prod covered
5. Monitoring configured and alerting tested

## Non-Functional Acceptance

- Control ID: `iam-least-privilege`
- Threshold: ≥95% policies compliant; no wildcard resource; explicit actions only
- Tooling: IAM Access Analyzer and policy linters
- Cadence: CI per change and quarterly audit
- Environments: dev, int, ref, prod

## Test Strategy

| Test Type   | Tooling           | Focus                 |
| ----------- | ----------------- | --------------------- |
| Compliance  | Automated tooling | Policy enforcement    |
| Integration | CI pipeline       | Continuous validation |
| Audit       | Manual review     | Compliance assessment |

## Out of Scope

Implementation details to be refined during sprint planning

## Implementation Notes

- Continuous analysis prevents privilege creep; periodic review catches drift
- Cadence: CI per change + quarterly audit
- Status: draft

## Monitoring & Metrics

- `iam_least_privilege_compliance_status` gauge
- `iam_least_privilege_violations_total` counter

## Risks & Mitigation

| Risk                | Impact            | Mitigation            |
| ------------------- | ----------------- | --------------------- |
| Configuration drift | Non-compliance    | Automated remediation |
| Tool failures       | Missed violations | Redundant checks      |

## Traceability

- NFR: SEC-012
- Registry: security/expectations.yaml v1.0

## Open Questions

None
