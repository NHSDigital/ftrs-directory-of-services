---
story_id: STORY-OBS-033
title: Error percentage metric & alert configured
role: SRE
goal: Deliver: Error percentage metric & alert configured
value: Error rate metric and alert exist to highlight reliability issues.
nfr_refs: [OBS-012]
status: draft
---

## Description

Implement and validate NFR `OBS-012` for domain `observability`.

## Acceptance Criteria

- Alert triggers when error% > 1% over 5m; playbook linked
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `OBS-012`
- Domain: observability
- Control ID: `error-percentage-alert`
- Measure: Error percentage metric & alert configured
- Threshold: Alert triggers when error% > 1% over 5m; playbook linked
- Tooling: Metrics backend + alerting rules
- Cadence: Continuous + monthly tuning
- Environments: prod

## Traceability

- Domain registry: requirements/nfrs/observability/nfrs.yaml
