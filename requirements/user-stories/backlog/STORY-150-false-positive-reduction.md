---
id: STORY-150
title: Reduce accessibility scan false positives
nfr_refs:
  - ACC-022
  - ACC-002
type: accessibility
status: draft
owner: accessibility-team
summary: Minimise false positive accessibility findings through tooling configuration and rule tuning.
---

## Description
Analyse recurring false positives; adjust scanner configuration, suppress confirmed non-issues responsibly, and track false positive ratio trend.

## Acceptance Criteria
- False positive ratio <10% over rolling 30 days.
- Suppression list reviewed monthly; no unjustified entries.
- New false positive classification documented & linked to config change.
- Trend chart shows improving or stable ratio.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| ratio_calculation_job | automated | Ratio <10% |
| suppression_list_audit | manual | All entries justified |
| new_false_positive_documentation_test | automated | Doc entry created |
| trend_chart_presence | automated | Chart shows data |

## Traceability
NFRs: ACC-022, ACC-002
