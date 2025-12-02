---
story_id: STORY-INT-004
jira_key:
title: Correlation IDs preserved across calls
role: Integration Engineer
goal: Implement and validate: Correlation IDs preserved across calls
value: Enables end-to-end tracing and diagnostics
nfr_refs: [INT-013]
status: draft
---

## Description

Implement automated validation for: Correlation IDs preserved across calls.

## Acceptance Criteria

1. 100% requests preserve transaction_id/correlation_id in logs and headers
2. Tooling: Middleware + log correlation tests operational
3. Cadence: CI per build + monthly audit validated
4. Environments: int, ref, prod covered
5. Monitoring configured and alerting tested

## Non-Functional Acceptance

- Control ID: `correlation-id-preserved`\n- Threshold: 100% requests preserve transaction_id/correlation_id in logs and headers\n- Tooling: Middleware + log correlation tests\n- Cadence: CI per build + monthly audit\n- Environments: int, ref, prod

## Test Strategy

| Test Type   | Tooling           | Focus                 |
| ----------- | ----------------- | --------------------- |
| Compliance  | Automated tooling | Policy enforcement    |
| Integration | CI pipeline       | Continuous validation |
| Audit       | Manual review     | Compliance assessment |

## Out of Scope

Implementation details to be refined during sprint planning

## Implementation Notes

- Enables end-to-end tracing and diagnostics
- Cadence: CI per build + monthly audit
- Status: draft

## Monitoring & Metrics

- `correlation_id_preserved_compliance_status` gauge
- `correlation_id_preserved_violations_total` counter

## Risks & Mitigation

| Risk                | Impact            | Mitigation            |
| ------------------- | ----------------- | --------------------- |
| Configuration drift | Non-compliance    | Automated remediation |
| Tool failures       | Missed violations | Redundant checks      |

## Traceability

- NFR: INT-013
- Registry: interoperability/expectations.yaml v1.0

## Open Questions

None
