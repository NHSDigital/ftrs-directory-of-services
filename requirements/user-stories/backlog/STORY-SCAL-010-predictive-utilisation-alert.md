---
story_id: STORY-SCAL-010
title: Predictive alert fires at utilisation forecast threshold
role: Platform Engineer
goal: Deliver: Predictive alert fires at utilisation forecast threshold
value: Predictive alerts fire before utilisation reaches critical thresholds.
nfr_refs: [SCAL-010]
status: draft
---

## Description

Implement and validate NFR `SCAL-010` for domain `scalability`.

## Acceptance Criteria

- Forecasted utilisation > 80% in 15m triggers alert; MTT Alert < 2m
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `SCAL-010`
- Domain: scalability
- Control ID: `predictive-utilisation-alert`
- Measure: Predictive alert fires at utilisation forecast threshold
- Threshold: Forecasted utilisation > 80% in 15m triggers alert; MTT Alert < 2m
- Tooling: Forecasting job + alerting rules
- Cadence: Continuous + monthly tuning
- Environments: prod

## Traceability

- Domain registry: requirements/nfrs/scalability/nfrs.yaml
