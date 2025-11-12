---
id: STORY-082
title: 24x7 uptime monitoring coverage
nfr_refs:
  - AVAIL-003
type: availability
status: draft
owner: platform-team
summary: Implement comprehensive uptime monitoring across all hours excluding scheduled maintenance.
---

## Description
Deploy synthetic and real user monitoring to verify continuous availability. Ensure monitoring schedule covers nights/weekends and excludes scheduled maintenance periods in SLA calculations.

## Acceptance Criteria
- Monitoring configuration shows probes every minute 24x7.
- SLA calculation excludes approved maintenance window periods only.
- Random spot checks at night/weekend show probe success.
- Alert triggers on consecutive failures >SLA threshold.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| monitoring_schedule_validation | automated | All intervals covered |
| maintenance_exclusion_logic_test | automated | Window excluded from SLA calc |
| night_weekend_spot_checks | manual | Probes succeed |
| consecutive_failure_alert_test | automated | Alert raised correctly |

## Traceability
NFRs: AVAIL-003
