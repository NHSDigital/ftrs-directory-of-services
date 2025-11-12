---
id: STORY-054
title: Eliminate long-lived unmanaged credentials
nfr_refs:
  - SEC-017
type: security
status: draft
owner: devsecops-team
summary: Remove unmanaged static credentials; enforce rotation and short TTL secrets.
---

## Description
Scan for hard-coded or long-lived secrets; migrate to managed secret store with rotation; enforce TTL policies and alert on violations.

## Acceptance Criteria
- Secret inventory shows zero unmanaged long-lived credentials.
- Rotation policy configured for managed secrets.
- Static secret commit attempt blocked by pre-commit hook.
- Alert triggers on secret older than policy threshold.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| secret_inventory_scan | automated | No long-lived unmanaged secrets |
| rotation_policy_check | automated | Rotation config present |
| commit_hook_secret_block_test | automated | Commit rejected |
| secret_age_alert_simulation | automated | Alert delivered |

## Traceability
NFRs: SEC-017
