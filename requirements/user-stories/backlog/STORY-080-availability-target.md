---
id: STORY-080
title: Achieve ≥99.90% monthly availability
nfr_refs:
  - AVAIL-001
  - REL-001
type: availability
status: draft
owner: platform-team
summary: Ensure production multi-AZ deployment meets or exceeds 99.90% availability SLA.
---

## Description
Leverage multi-AZ architecture, health checks, and failover automation to guarantee measured monthly availability ≥99.90% excluding approved maintenance windows.

## Acceptance Criteria
- Architecture diagram shows all critical components multi-AZ.
- Monthly availability report (excluding scheduled maintenance) ≥99.90%.
- Single AZ failure simulation maintains service availability.
- Alert triggers if projected monthly availability drops below 99.90%.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| az_failure_simulation | automated | Service remains operational |
| availability_report_generation | automated | Report shows ≥99.90% |
| projection_alert_simulation | automated | Alert fired on threshold breach |
| architecture_diagram_presence | manual | Diagram committed |

## Traceability
NFRs: AVAIL-001, REL-001
