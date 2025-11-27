---
story_id: STORY-AVAIL-001
jira_key:
title: Availability report shows ≥99.90% multi-AZ uptime
role: SRE
goal: Implement and validate: Availability report shows ≥99.90% multi-AZ uptime
value: Tracks SLA against multi-AZ deployment goals
nfr_refs: [AVAIL-001]
status: draft
---

## Description
Implement automated validation for: Availability report shows ≥99.90% multi-AZ uptime.

## Acceptance Criteria
1. >= 99.90% monthly uptime across multi-AZ deployment
2. Tooling: Uptime monitoring + monthly report automation operational
3. Cadence: Monthly validated
4. Environments: prod covered
5. Monitoring configured and alerting tested

## Non-Functional Acceptance
- Control ID: `multi-az-uptime-report`\n- Threshold: >= 99.90% monthly uptime across multi-AZ deployment\n- Tooling: Uptime monitoring + monthly report automation\n- Cadence: Monthly\n- Environments: prod

## Test Strategy
| Test Type | Tooling | Focus |
|-----------|---------|-------|
| Compliance | Automated tooling | Policy enforcement |
| Integration | CI pipeline | Continuous validation |
| Audit | Manual review | Compliance assessment |

## Out of Scope
Implementation details to be refined during sprint planning

## Implementation Notes
- Tracks SLA against multi-AZ deployment goals
- Cadence: Monthly
- Status: draft

## Monitoring & Metrics
- `multi_az_uptime_report_compliance_status` gauge
- `multi_az_uptime_report_violations_total` counter

## Risks & Mitigation
| Risk | Impact | Mitigation |
|------|--------|-----------|
| Configuration drift | Non-compliance | Automated remediation |
| Tool failures | Missed violations | Redundant checks |

## Traceability
- NFR: AVAIL-001
- Registry: availability/expectations.yaml v1.0

## Open Questions
None
