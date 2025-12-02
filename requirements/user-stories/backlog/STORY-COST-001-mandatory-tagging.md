---
story_id: STORY-COST-001
jira_key:
title: Mandatory tagging set present on 100% resources
role: FinOps Engineer
goal: Implement and validate: Mandatory tagging set present on 100% resources
value: Enables cost visibility and accountability
nfr_refs: [COST-001]
status: draft
---

## Description

Implement automated validation for: Mandatory tagging set present on 100% resources.

## Acceptance Criteria

1. 100% resources carry mandatory tags
2. Tooling: AWS Config rules + tag audit automation operational
3. Cadence: Continuous + monthly report validated
4. Environments: dev, int, ref, prod covered
5. Monitoring configured and alerting tested

## Non-Functional Acceptance

- Control ID: `mandatory-tagging`\n- Threshold: 100% resources carry mandatory tags\n- Tooling: AWS Config rules + tag audit automation\n- Cadence: Continuous + monthly report\n- Environments: dev, int, ref, prod

## Test Strategy

| Test Type   | Tooling           | Focus                 |
| ----------- | ----------------- | --------------------- |
| Compliance  | Automated tooling | Policy enforcement    |
| Integration | CI pipeline       | Continuous validation |
| Audit       | Manual review     | Compliance assessment |

## Out of Scope

Implementation details to be refined during sprint planning

## Implementation Notes

- Enables cost visibility and accountability
- Cadence: Continuous + monthly report
- Status: draft

## Monitoring & Metrics

- `mandatory_tagging_compliance_status` gauge
- `mandatory_tagging_violations_total` counter

## Risks & Mitigation

| Risk                | Impact            | Mitigation            |
| ------------------- | ----------------- | --------------------- |
| Configuration drift | Non-compliance    | Automated remediation |
| Tool failures       | Missed violations | Redundant checks      |

## Traceability

- NFR: COST-001
- Registry: cost/expectations.yaml v1.0

## Open Questions

None
