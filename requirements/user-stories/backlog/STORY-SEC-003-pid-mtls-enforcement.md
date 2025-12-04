---
story_id: STORY-SEC-003
jira_key:
title: "Requests carrying PID fields require mutual TLS; plain text requests blocked"
role: Security Engineer
goal: "Implement and validate: Requests carrying PID fields require mutual TLS; plain text requests blocked"
value: Ensures transport security for sensitive data; test coverage verifies enforcement
nfr_refs: [SEC-025]
status: draft
---

## Description

Implement automated validation for: Requests carrying PID fields require mutual TLS; plain text requests blocked.

## Acceptance Criteria

1. 100% enforcement on designated endpoints
2. Tooling: API gateway/WAF policy and integration tests operational
3. Cadence: CI policy validation and continuous enforcement validated
4. Environments: int, ref, production covered
5. Monitoring configured and alerting tested

## Non-Functional Acceptance

- Control ID: `pid-mtls-enforcement`
- Threshold: 100% enforcement on designated endpoints
- Tooling: API gateway/WAF policy and integration tests
- Cadence: CI policy validation and continuous enforcement
- Environments: int, ref, production

## Test Strategy

| Test Type   | Tooling           | Focus                 |
| ----------- | ----------------- | --------------------- |
| Compliance  | Automated tooling | Policy enforcement    |
| Integration | CI pipeline       | Continuous validation |
| Audit       | Manual review     | Compliance assessment |

## Out of Scope

Implementation details to be refined during sprint planning

## Implementation Notes

- Ensures transport security for sensitive data; test coverage verifies enforcement
- Cadence: CI policy validation + continuous enforcement
- Status: draft

## Monitoring & Metrics

- `pid_mtls_enforcement_compliance_status` gauge
- `pid_mtls_enforcement_violations_total` counter

## Risks & Mitigation

| Risk                | Impact            | Mitigation            |
| ------------------- | ----------------- | --------------------- |
| Configuration drift | Non-compliance    | Automated remediation |
| Tool failures       | Missed violations | Redundant checks      |

## Traceability

- NFR: SEC-025
- Registry: security/expectations.yaml v1.0

## Open Questions

None
