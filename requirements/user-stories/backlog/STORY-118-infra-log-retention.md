---
id: STORY-118
title: Infrastructure log retention compliance
nfr_refs:
  - OBS-015
  - OBS-013
type: observability
status: draft
owner: compliance-team
summary: Ensure infrastructure log retention meets NHS Records Management requirements.
---

## Description
Configure and validate retention policies for infra logs according to records management guidelines; provide audit evidence.

## Acceptance Criteria
- Retention period matches policy config.
- Expired logs archived or purged per schedule.
- Compliance report generated & stored.
- Unauthorized retention change attempt logged & denied.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| retention_period_scan | automated | Matches policy |
| expiry_purge_job_test | automated | Purge executes |
| compliance_report_generation | automated | Report stored |
| unauthorized_change_attempt | automated | Denied & logged |

## Traceability
NFRs: OBS-015, OBS-013
