---
id: STORY-079
title: Predictive scaling alerts
nfr_refs:
  - SCAL-010
  - SCAL-007
type: scalability
status: draft
owner: platform-team
summary: Generate proactive alerts based on forecasted utilisation thresholds before capacity exhaustion.
---

## Description
Implement forecasting engine (e.g., Holt-Winters) to predict utilisation. Trigger alert when forecasted utilisation exceeds 80% for sustained 15 minutes; verify planning actions initiated.

## Acceptance Criteria
- Forecast model parameters documented.
- Simulated rising utilisation triggers predictive alert before breach.
- Alert includes recommended scale action & time window.
- Planning ticket automatically created referencing alert.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| forecast_model_config_presence | manual | Config committed |
| predictive_alert_simulation | automated | Alert emitted pre-breach |
| alert_recommendation_content | manual | Contains action & window |
| planning_ticket_creation | automated | Ticket exists & linked |

## Traceability
NFRs: SCAL-010, SCAL-007
