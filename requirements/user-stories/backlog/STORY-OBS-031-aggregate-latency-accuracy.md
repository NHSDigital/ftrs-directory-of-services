---
story_id: STORY-OBS-031
title: Aggregate latency panel accurate within 2% roll-up
role: SRE
goal: Deliver: Aggregate latency panel accurate within 2% roll-up
value: Aggregate latency panel roll-ups remain within acceptable accuracy margin (e.g., ≤2%).
nfr_refs: [OBS-010]
status: draft
---

## Description

Implement and validate NFR `OBS-010` for domain `observability`.

## Acceptance Criteria

- Roll-up accuracy within \u22642% vs raw series
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `OBS-010`
- Domain: observability
- Control ID: `aggregate-latency-accuracy`
- Measure: Aggregate latency panel accurate within 2% roll-up
- Threshold: Roll-up accuracy within \u22642% vs raw series
- Tooling: Dashboard query tests + calibration script
- Cadence: Monthly calibration
- Environments: prod


## Traceability

- Domain registry: requirements/nfrs/observability/nfrs.yaml
