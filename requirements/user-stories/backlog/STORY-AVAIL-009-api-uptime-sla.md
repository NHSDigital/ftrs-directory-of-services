---
story_id: STORY-AVAIL-009
title: API uptime aligns with core service
role: SRE
goal: Deliver: API uptime aligns with core service
value: API uptime aligns with overall service availability target.
nfr_refs: [AVAIL-008]
status: draft
---

## Description

Implement and validate NFR `AVAIL-008` for domain `availability`.

## Acceptance Criteria

- API uptime \u2265 99.90% monthly; maintenance excluded per policy
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `AVAIL-008`
- Domain: availability
- Control ID: `api-uptime-sla`
- Measure: API uptime aligns with core service
- Threshold: API uptime \u2265 99.90% monthly; maintenance excluded per policy
- Tooling: Uptime monitors + SLA calculator
- Cadence: Monthly
- Environments: prod


## Traceability

- Domain registry: requirements/nfrs/availability/nfrs.yaml
