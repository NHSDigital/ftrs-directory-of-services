---
id: STORY-090
title: Multi-AZ resilience without single points of failure
nfr_refs:
  - REL-002
  - AVAIL-001
type: reliability
status: draft
owner: architecture-team
summary: Validate multi-AZ deployment eliminates single points of failure and sustains service during AZ outage.
---

## Description
Perform AZ failure simulation (e.g., disable network access or terminate instances in one AZ) ensuring traffic reroutes and core functionality continues without SLA breach.

## Acceptance Criteria
- Architecture diagram highlights redundancy for each critical component.
- AZ failure simulation maintains service availability & latency SLAs.
- No data loss or write failures during simulation.
- Post-simulation report lists any residual SPOF and remediation actions.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| az_failure_simulation | automated | Service healthy |
| latency_comparison | automated | Within SLA thresholds |
| data_integrity_check | automated | No loss |
| spof_report_presence | manual | Remediation items listed |

## Traceability
NFRs: REL-002, AVAIL-001
