---
id: STORY-163
title: SIRO sign-off
nfr_refs:
  - GOV-013
type: governance
status: draft
owner: risk-management
summary: Obtain SIRO sign-off acknowledging information risk posture.
---

## Description
Present risk register, mitigation status, and residual risk narrative to SIRO; capture formal sign-off artifact.

## Acceptance Criteria
- Risk register current (updated <30 days).
- Residual risk summary documented.
- SIRO sign-off artifact stored (signature/date).
- No unowned high risks.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| risk_register_recency_check | automated | Updated <30d |
| residual_risk_summary_presence | automated | File exists |
| signoff_artifact_scan | automated | Signature/date |
| unowned_high_risk_alert_test | automated | Alert if any |

## Traceability
NFRs: GOV-013
