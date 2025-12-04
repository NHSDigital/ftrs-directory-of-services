---
story_id: STORY-SEC-017
jira_key:
title: SG rules audited; attempt broad ingress denied
role: Security Engineer
goal: Implement and validate: SG rules audited; attempt broad ingress denied
value: Prevents risky network exposure via security groups
nfr_refs: [SEC-007]
status: draft
---

## Description

Implement automated validation for: SG rules audited; attempt broad ingress denied.

## Acceptance Criteria

1. 0 broad (0.0.0.0/0) ingress on restricted ports
2. Tooling: AWS Configuration + IaC linter operational
3. Cadence: CI per change + monthly audit validated
4. Environments: dev, int, ref, prod covered
5. Monitoring configured and alerting tested

## Non-Functional Acceptance

- Control ID: `sg-broad-ingress-denied`\n- Threshold: 0 broad (0.0.0.0/0) ingress on restricted ports\n- Tooling: AWS Configuration + IaC linter\n- Cadence: CI per change + monthly audit\n- Environments: dev, int, ref, prod

## Test Strategy

| Test Type   | Tooling           | Focus                 |
| ----------- | ----------------- | --------------------- |
| Compliance  | Automated tooling | Policy enforcement    |
| Integration | CI pipeline       | Continuous validation |
| Audit       | Manual review     | Compliance assessment |

## Out of Scope

Implementation details to be refined during sprint planning

## Implementation Notes

- Prevents risky network exposure via security groups
- Cadence: CI per change + monthly audit
- Status: draft

## Monitoring & Metrics

- `sg_broad_ingress_denied_compliance_status` gauge
- `sg_broad_ingress_denied_violations_total` counter

## Risks & Mitigation

| Risk                | Impact            | Mitigation            |
| ------------------- | ----------------- | --------------------- |
| Configuration drift | Non-compliance    | Automated remediation |
| Tool failures       | Missed violations | Redundant checks      |

## Traceability

- NFR: SEC-007
- Registry: security/expectations.yaml v1.0

## Open Questions

None
