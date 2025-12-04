---
story_id: STORY-SEC-013
jira_key:
title: NHSE approved cryptographic algorithms (GPG v4.0) enforced across encryption features
role: Security Engineer
goal: Implement and validate NHSE approved cryptographic algorithms including GPG v4.0 for all encryption features
value: Aligns with organizational policy; prevents weak cipher adoption
nfr_refs: [SEC-001]
status: draft
---

## Description

Implement automated validation for NHSE approved cryptographic algorithms (GPG v4.0) across application and cloud provider encryption features.

## Acceptance Criteria

1. GPG v4.0 compliance verified for applicable encryption use cases
2. Cloud provider encryption algorithms align with NHSE approved list
3. TLS1.2+ only; no weak/legacy ciphers enabled
4. Tooling: Crypto policy audit scanner + configuration checks operational
5. Cadence: CI per change + monthly scan validated
6. Environments: dev, int, ref, prod covered
7. Monitoring configured and alerting tested

## Non-Functional Acceptance

- Control ID: `crypto-cipher-policy`\n- Threshold: 100% GPG v4.0 compliance; cloud algorithms on approved list; TLS1.2+ only\n- Tooling: Crypto policy audit scanner + TLS scanner + configuration checks\n- Cadence: CI per change + monthly scan\n- Environments: dev, int, ref, prod

## Test Strategy

| Test Type   | Tooling           | Focus                 |
| ----------- | ----------------- | --------------------- |
| Compliance  | Automated tooling | Policy enforcement    |
| Integration | CI pipeline       | Continuous validation |
| Audit       | Manual review     | Compliance assessment |

## Out of Scope

Implementation details to be refined during sprint planning

## Implementation Notes

- Enforces modern TLS standards; automated scans detect drift
- Cadence: CI per change + monthly scan
- Status: draft

## Monitoring & Metrics

- `crypto_cipher_policy_compliance_status` gauge
- `crypto_cipher_policy_violations_total` counter

## Risks & Mitigation

| Risk                | Impact            | Mitigation            |
| ------------------- | ----------------- | --------------------- |
| Configuration drift | Non-compliance    | Automated remediation |
| Tool failures       | Missed violations | Redundant checks      |

## Traceability

- NFR: SEC-001
- Registry: security/expectations.yaml v1.0

## Open Questions

None
