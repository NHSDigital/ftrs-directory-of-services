---
story_id: STORY-OBS-005
jira_key:
title: Distributed trace spans cover end-to-end request
role: SRE
goal: Implement and validate: Distributed trace spans cover end-to-end request
value: Enables end-to-end diagnosis and correlation across layers
nfr_refs: [OBS-030]
status: draft
---

## Description
Implement automated validation for: Distributed trace spans cover end-to-end request.

## Acceptance Criteria
1. ≥95% of requests include spans across key tiers
2. Tooling: Tracing SDKs + sampling config operational
3. Cadence: Continuous + monthly sampling review validated
4. Environments: int, ref, prod covered
5. Monitoring configured and alerting tested

## Non-Functional Acceptance
- Control ID: `distributed-trace-coverage`\n- Threshold: ≥95% of requests include spans across key tiers\n- Tooling: Tracing SDKs + sampling config\n- Cadence: Continuous + monthly sampling review\n- Environments: int, ref, prod

## Test Strategy
| Test Type | Tooling | Focus |
|-----------|---------|-------|
| Compliance | Automated tooling | Policy enforcement |
| Integration | CI pipeline | Continuous validation |
| Audit | Manual review | Compliance assessment |

## Out of Scope
Implementation details to be refined during sprint planning

## Implementation Notes
- Enables end-to-end diagnosis and correlation across layers
- Cadence: Continuous + monthly sampling review
- Status: draft

## Monitoring & Metrics
- `distributed_trace_coverage_compliance_status` gauge
- `distributed_trace_coverage_violations_total` counter

## Risks & Mitigation
| Risk | Impact | Mitigation |
|------|--------|-----------|
| Configuration drift | Non-compliance | Automated remediation |
| Tool failures | Missed violations | Redundant checks |

## Traceability
- NFR: OBS-030
- Registry: observability/expectations.yaml v1.0

## Open Questions
None
