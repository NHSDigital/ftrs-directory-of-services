---
id: STORY-052
title: Certificate expiry alerting & renewal
nfr_refs:
  - SEC-015
type: security
status: draft
owner: platform-team
summary: Provide proactive alerts for certificate expiry and seamless automated renewal.
---

## Description
Monitor certificate expiry dates; issue alert before threshold; execute automated renewal procedure without service interruption.

## Acceptance Criteria
- Monitoring shows certificates with expiry timeline.
- Alert triggers at configurable threshold (e.g. 30 days).
- Renewal automation tested successfully with staging cert.
- Post-renewal service endpoints remain uninterrupted.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| cert_inventory_monitor | automated | Dashboard lists expiries |
| expiry_threshold_alert_test | automated | Alert delivered at threshold |
| renewal_automation_dry_run | manual | Renewal completes w/o downtime |
| post_renewal_availability_check | automated | Endpoints healthy |

## Traceability
NFRs: SEC-015
