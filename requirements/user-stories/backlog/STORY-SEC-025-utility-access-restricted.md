---
story_id: STORY-SEC-025
jira_key:
title: Utility program access restricted to approved roles
role: Security Engineer
goal: Implement and validate: Utility program access restricted to approved roles
value: Prevents misuse of diagnostic utilities
nfr_refs: [SEC-022]
status: draft
---

## Description
Implement automated validation for: Utility program access restricted to approved roles.

## Acceptance Criteria
1. Only approved roles can access utility programs
2. Tooling: RBAC policy checks + audit logs operational
3. Cadence: CI policy checks + monthly audit validated
4. Environments: dev, int, ref, prod covered
5. Monitoring configured and alerting tested

## Non-Functional Acceptance
- Control ID: `utility-access-restricted`\n- Threshold: Only approved roles can access utility programs\n- Tooling: RBAC policy checks + audit logs\n- Cadence: CI policy checks + monthly audit\n- Environments: dev, int, ref, prod

## Test Strategy
| Test Type | Tooling | Focus |
|-----------|---------|-------|
| Compliance | Automated tooling | Policy enforcement |
| Integration | CI pipeline | Continuous validation |
| Audit | Manual review | Compliance assessment |

## Out of Scope
Implementation details to be refined during sprint planning

## Implementation Notes
- Prevents misuse of diagnostic utilities
- Cadence: CI policy checks + monthly audit
- Status: draft

## Monitoring & Metrics
- `utility_access_restricted_compliance_status` gauge
- `utility_access_restricted_violations_total` counter

## Risks & Mitigation
| Risk | Impact | Mitigation |
|------|--------|-----------|
| Configuration drift | Non-compliance | Automated remediation |
| Tool failures | Missed violations | Redundant checks |

## Traceability
- NFR: SEC-022
- Registry: security/expectations.yaml v1.0

## Open Questions
None
