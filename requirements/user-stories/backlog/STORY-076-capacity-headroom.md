---
id: STORY-076
title: Maintain capacity headroom for growth
nfr_refs:
  - SCAL-007
  - SCAL-010
type: scalability
status: draft
owner: platform-team
summary: Ensure sustained utilisation remains below threshold and predictive alerts fire prior to headroom breach.
---

## Description
Implement dashboards and forecasting to track utilisation and predict when capacity will exceed 80%. Keep average utilisation below 70% to maintain ≥30% headroom and trigger proactive scale planning.

## Acceptance Criteria
- Dashboard visualises utilisation vs headroom threshold.
- Forecast model predicts breach ≥30min in advance.
- Alert triggers when forecast utilisation >80% sustained 15min.
- Monthly report confirms average utilisation <70%.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| utilisation_dashboard_presence | manual | Dashboard accessible |
| forecast_breach_simulation | automated | Alert triggered |
| sustained_high_utilisation_test | automated | Alert after 15min >80% |
| monthly_utilisation_report | manual | <70% average utilisation |

## Traceability
NFRs: SCAL-007, SCAL-010
