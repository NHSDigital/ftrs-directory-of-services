---
story_id: STORY-AVAIL-004
jira_key:
title: "Monthly maintenance minutes ≤150; single ≤60"
role: SRE
goal: "Implement and validate: Monthly maintenance minutes ≤150; single ≤60"
value: Controls maintenance impact to meet availability objectives
nfr_refs: [AVAIL-004]
status: draft
---

## Description

Implement automated validation for monthly maintenance minutes ≤150; single ≤60.

## Acceptance Criteria

1. Monthly total ≤150 minutes; single window ≤60 minutes
2. Tooling: Maintenance logs + reporting operational
3. Cadence: Monthly validated
4. Environments: prod covered
5. Monitoring configured and alerting tested

## Non-Functional Acceptance

- Control ID: `maintenance-window-minutes`
- Threshold: Monthly total ≤150 minutes; single window ≤60 minutes
- Tooling: Maintenance logs and reporting
- Cadence: Monthly
- Environments: prod

## Test Strategy

| Test Type   | Tooling           | Focus                 |
| ----------- | ----------------- | --------------------- |
| Compliance  | Automated tooling | Policy enforcement    |
| Integration | CI pipeline       | Continuous validation |
| Audit       | Manual review     | Compliance assessment |

## Out of Scope

Implementation details to be refined during sprint planning

## Implementation Notes

- Controls maintenance impact to meet availability objectives
- Cadence: Monthly
- Status: draft

## Monitoring & Metrics

- `maintenance_window_minutes_compliance_status` gauge
- `maintenance_window_minutes_violations_total` counter

## Risks & Mitigation

| Risk                | Impact            | Mitigation            |
| ------------------- | ----------------- | --------------------- |
| Configuration drift | Non-compliance    | Automated remediation |
| Tool failures       | Missed violations | Redundant checks      |

## Traceability

- NFR: AVAIL-004
- Registry: availability/expectations.yaml v1.0

## Open Questions

None
