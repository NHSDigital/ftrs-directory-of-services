---
id: STORY-115
title: Aggregate latency across all endpoints recorded
nfr_refs:
  - OBS-010
  - OBS-009
type: observability
status: draft
owner: api-team
summary: Provide aggregate latency metrics across all API endpoints.
---

## Description
Aggregate per-endpoint latency into global metrics for overall performance view and SLA monitoring.

## Acceptance Criteria
- Aggregate latency panel present (avg, p95, p99).
- Discrepancy between aggregate and endpoint roll-up ≤2%.
- SLA breach triggers alert.
- Data retention ≥30 days.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| aggregate_panel_presence | automated | Panel visible |
| rollup_discrepancy_check | automated | ≤2% difference |
| sla_breach_alert_test | automated | Alert emitted |
| retention_verification | automated | ≥30d data |

## Traceability
NFRs: OBS-010, OBS-009
