---
story_id: STORY-SEC-021
jira_key:
title: Key rotation events logged; unauthorized access denied
role: Security Engineer
goal: Implement and validate: Key rotation events logged; unauthorized access denied
value: Audit trail confirms rotation compliance and denial of unauthorized access
nfr_refs: [SEC-013]
status: draft
---

## Description

Implement automated validation for: Key rotation events logged; unauthorized access denied.

## Acceptance Criteria

1. 100% rotation events logged; 0 unauthorized key access
2. Tooling: KMS/AWS logs + SIEM correlation operational
3. Cadence: Quarterly audit + CI checks on policy validated
4. Environments: dev, int, ref, prod covered
5. Monitoring configured and alerting tested

## Non-Functional Acceptance

- Control ID: `key-rotation-logging`\n- Threshold: 100% rotation events logged; 0 unauthorized key access\n- Tooling: KMS/AWS logs + SIEM correlation\n- Cadence: Quarterly audit + CI checks on policy\n- Environments: dev, int, ref, prod

## Test Strategy

| Test Type   | Tooling           | Focus                 |
| ----------- | ----------------- | --------------------- |
| Compliance  | Automated tooling | Policy enforcement    |
| Integration | CI pipeline       | Continuous validation |
| Audit       | Manual review     | Compliance assessment |

## Out of Scope

Implementation details to be refined during sprint planning

## Implementation Notes

- Audit trail confirms rotation compliance and denial of unauthorized access
- Cadence: Quarterly audit + CI checks on policy
- Status: draft

## Monitoring & Metrics

- `key_rotation_logging_compliance_status` gauge
- `key_rotation_logging_violations_total` counter

## Risks & Mitigation

| Risk                | Impact            | Mitigation            |
| ------------------- | ----------------- | --------------------- |
| Configuration drift | Non-compliance    | Automated remediation |
| Tool failures       | Missed violations | Redundant checks      |

## Traceability

- NFR: SEC-013
- Registry: security/expectations.yaml v1.0

## Open Questions

None
