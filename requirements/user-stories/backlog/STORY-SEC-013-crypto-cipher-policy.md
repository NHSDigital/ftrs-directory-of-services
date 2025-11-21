---
story_id: STORY-SEC-013
jira_key:
title: Crypto algorithms conform; weak ciphers rejected
role: Security Engineer
goal: Implement and validate: Crypto algorithms conform; weak ciphers rejected
value: Enforces modern TLS standards; automated scans detect drift
nfr_refs: [SEC-001]
status: draft
---

## Description
Implement automated validation for: Crypto algorithms conform; weak ciphers rejected.

## Acceptance Criteria
1. TLS1.2+ only; no weak/legacy ciphers enabled
2. Tooling: TLS scanner + configuration policy checks operational
3. Cadence: CI per change + monthly scan validated
4. Environments: dev, int, ref, prod covered
5. Monitoring configured and alerting tested

## Non-Functional Acceptance
- Control ID: `crypto-cipher-policy`\n- Threshold: TLS1.2+ only; no weak/legacy ciphers enabled\n- Tooling: TLS scanner + configuration policy checks\n- Cadence: CI per change + monthly scan\n- Environments: dev, int, ref, prod

## Test Strategy
| Test Type | Tooling | Focus |
|-----------|---------|-------|
| Compliance | Automated tooling | Policy enforcement |
| Integration | CI pipeline | Continuous validation |
| Audit | Manual review | Compliance assessment |

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
| Risk | Impact | Mitigation |
|------|--------|-----------|
| Configuration drift | Non-compliance | Automated remediation |
| Tool failures | Missed violations | Redundant checks |

## Traceability
- NFR: SEC-001
- Registry: security/expectations.yaml v1.0

## Open Questions
None
