---
story_id: STORY-COST-004
jira_key:
title: CloudHealth optimisation & tag compliance reports
role: FinOps Engineer
goal: Implement and validate: CloudHealth optimisation & tag compliance reports
value: Drives optimisation and tag hygiene
nfr_refs: [COST-004]
status: draft
---

## Description

Implement automated validation for: CloudHealth optimisation & tag compliance reports.

## Acceptance Criteria

1. Reports generated; tracked actions created
2. Tooling: CloudHealth reporting + tracker operational
3. Cadence: Monthly validated
4. Environments: prod covered
5. Monitoring configured and alerting tested

## Non-Functional Acceptance

- Control ID: `optimisation-reports`\n- Threshold: Reports generated; tracked actions created\n- Tooling: CloudHealth reporting + tracker\n- Cadence: Monthly\n- Environments: prod

## Test Strategy

| Test Type   | Tooling           | Focus                 |
| ----------- | ----------------- | --------------------- |
| Compliance  | Automated tooling | Policy enforcement    |
| Integration | CI pipeline       | Continuous validation |
| Audit       | Manual review     | Compliance assessment |

## Out of Scope

Implementation details to be refined during sprint planning

## Implementation Notes

- Drives optimisation and tag hygiene
- Cadence: Monthly
- Status: draft

## Monitoring & Metrics

- `optimisation_reports_compliance_status` gauge
- `optimisation_reports_violations_total` counter

## Risks & Mitigation

| Risk                | Impact            | Mitigation            |
| ------------------- | ----------------- | --------------------- |
| Configuration drift | Non-compliance    | Automated remediation |
| Tool failures       | Missed violations | Redundant checks      |

## Traceability

- NFR: COST-004
- Registry: cost/expectations.yaml v1.0

## Open Questions

None
