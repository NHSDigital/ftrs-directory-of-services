---
story_id: STORY-SEC-001
jira_key: FTRS-1563
title: All public/private API endpoints enforce TLS encryption in transit
role: Security Engineer
goal: Implement and validate TLS encryption (TLS 1.3, TLS 1.2 with permission) for all API endpoints
value: Prevents interception and tampering; aligns with NHS security policy
nfr_refs: [SEC-003]
status: draft
---
## Description

Implement automated validation for TLS encryption in transit between all components (internal and external).

## Acceptance Criteria

1. 100% endpoints using TLS 1.3 (TLS 1.2 with permission); no TLS 1.0/1.1
2. Tooling: AWS Configuration rules and Terraform policy checks and automated endpoint scan operational
3. Cadence: Continuous (real-time) with CI enforcement on change validated
4. Environments: dev, int, ref, prod covered
5. Monitoring configured and alerting tested
6. Failed HTTP downgrade tests confirm TLS enforcement

## Non-Functional Acceptance

- Control ID: `tls-encryption-endpoints`
- Threshold: 100% endpoints TLS 1.3 and above (if permission granted 1.2); 0 endpoints TLS 1.0/1.1
- Tooling: AWS Configuration rules and Terraform policy checks and TLS scanner
- Cadence: Continuous (real-time) with CI enforcement on change
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

- Aligns with NHS policy; Configuration provides continuous guardrails; CI blocks drift
- Cadence: Continuous (real-time) with CI enforcement on change
- Status: draft

## Monitoring & Metrics

- `tls_encryption_endpoints_compliance_status` gauge
- `tls_encryption_endpoints_violations_total` counter

## Risks & Mitigation

| Risk                | Impact            | Mitigation            |
| ------------------- | ----------------- | --------------------- |
| Configuration drift | Non-compliance    | Automated remediation |
| Tool failures       | Missed violations | Redundant checks      |

## Traceability

- NFR: SEC-003
- Jira: FTRS-1563

## Open Questions

None
