---
story_id: STORY-SEC-006
jira_key:
title: "mTLS handshake succeeds between designated services"
role: Security Engineer
goal: "Implement and validate: mTLS handshake succeeds between designated services"
value: Service-to-service trust enforced via mutual TLS; tests validate certificates and chain
nfr_refs: [SEC-014]
status: draft
---

## Description

Implement automated validation for: mTLS handshake succeeds between designated services.

## Acceptance Criteria

1. 100% handshake success in integration tests
2. Tooling: Integration tests and gateway certificate management operational
3. Cadence: CI per build and certificate rotation checks validated
4. Environments: int, ref, production covered
5. Monitoring configured and alerting tested

## Non-Functional Acceptance

- Control ID: `mtls-service-handshake`
- Threshold: 100% handshake success in integration tests
- Tooling: Integration tests and gateway certificate management
- Cadence: CI per build and certificate rotation checks
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

- Service-to-service trust enforced via mutual TLS; tests validate certificates and chain
- Cadence: CI per build + cert rotation checks
- Status: draft

## Monitoring & Metrics

- `mtls_service_handshake_compliance_status` gauge
- `mtls_service_handshake_violations_total` counter

## Risks & Mitigation

| Risk                | Impact            | Mitigation            |
| ------------------- | ----------------- | --------------------- |
| Configuration drift | Non-compliance    | Automated remediation |
| Tool failures       | Missed violations | Redundant checks      |

## Traceability

- NFR: SEC-014
- Registry: security/expectations.yaml v1.0

## Open Questions

None
