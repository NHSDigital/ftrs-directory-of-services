---
story_id: STORY-SEC-023
jira_key:
title: MFA enforced for all privileged infra roles
role: Security Engineer
goal: Implement and validate: MFA enforced for all privileged infra roles
value: Strong authentication for privileged accounts reduces risk
nfr_refs: [SEC-016]
status: draft
---

## Description
Implement automated validation for: MFA enforced for all privileged infra roles.

## Acceptance Criteria
1. 100% privileged roles require MFA
2. Tooling: IAM policy checks + directory audit operational
3. Cadence: CI policy checks + quarterly audit validated
4. Environments: dev, int, ref, prod covered
5. Monitoring configured and alerting tested

## Non-Functional Acceptance
- Control ID: `privileged-mfa-enforced`\n- Threshold: 100% privileged roles require MFA\n- Tooling: IAM policy checks + directory audit\n- Cadence: CI policy checks + quarterly audit\n- Environments: dev, int, ref, prod

## Test Strategy
| Test Type | Tooling | Focus |
|-----------|---------|-------|
| Compliance | Automated tooling | Policy enforcement |
| Integration | CI pipeline | Continuous validation |
| Audit | Manual review | Compliance assessment |

## Out of Scope
Implementation details to be refined during sprint planning

## Implementation Notes
- Strong authentication for privileged accounts reduces risk
- Cadence: CI policy checks + quarterly audit
- Status: draft

## Monitoring & Metrics
- `privileged_mfa_enforced_compliance_status` gauge
- `privileged_mfa_enforced_violations_total` counter

## Risks & Mitigation
| Risk | Impact | Mitigation |
|------|--------|-----------|
| Configuration drift | Non-compliance | Automated remediation |
| Tool failures | Missed violations | Redundant checks |

## Traceability
- NFR: SEC-016
- Registry: security/expectations.yaml v1.0

## Open Questions
None
