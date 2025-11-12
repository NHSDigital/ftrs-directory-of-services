---
id: STORY-085
title: Achieve RTO ≤2 hours
nfr_refs:
  - AVAIL-006
  - AVAIL-002
type: availability
status: draft
owner: platform-team
summary: Demonstrate disaster recovery exercise restores full service within 2 hours.
---

## Description
Conduct full DR exercise simulating region-level failure, executing failover procedures, validating service restoration, and measuring elapsed time against RTO target.

## Acceptance Criteria
- Exercise start & end timestamps recorded; total <120 minutes.
- All critical services reachable post-restoration.
- Data integrity checks pass (no data loss beyond RPO target).
- Post-exercise report includes improvement actions.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| dr_exercise_timing | manual/automated | <120 minutes |
| service_reachability_scan | automated | 100% critical endpoints healthy |
| data_integrity_check | automated | Pass; RPO target maintained |
| post_exercise_report_presence | manual | Report committed |

## Traceability
NFRs: AVAIL-006, AVAIL-002
