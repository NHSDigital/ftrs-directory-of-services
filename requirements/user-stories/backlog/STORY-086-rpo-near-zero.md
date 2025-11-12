---
id: STORY-086
title: Achieve RPO ≤60 seconds (near-zero)
nfr_refs:
  - AVAIL-007
type: availability
status: draft
owner: platform-team
summary: Ensure continuous replication keeps data loss window ≤60s in region failover scenarios.
---

## Description
Implement and validate continuous replication strategy. Measure replication lag and perform controlled failover showing recovered data freshness within 60 seconds of incident time.

## Acceptance Criteria
- Replication lag dashboard shows steady lag ≤60s.
- Controlled failover data delta test reveals loss window ≤60s.
- Alert triggers if lag >45s sustained for 5 minutes.
- Documentation of replication topology committed.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| replication_lag_monitoring | automated | Lag ≤60s |
| failover_data_delta_test | manual/automated | Delta ≤60s |
| lag_threshold_alert_test | automated | Alert at >45s sustained |
| topology_docs_presence | manual | Diagram/file committed |

## Traceability
NFRs: AVAIL-007
