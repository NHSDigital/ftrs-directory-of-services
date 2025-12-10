---
story_id: STORY-OBS-034
title: Infra log query returns expected fields
role: SRE
goal: Deliver: Infra log query returns expected fields
value: Infrastructure logs return expected structured fields for queries.
nfr_refs: [OBS-013]
status: draft
---

## Description

Implement and validate NFR `OBS-013` for domain `observability`.

## Acceptance Criteria

- Queries return required fields (timestamp, severity, host, correlation_id)
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `OBS-013`
- Domain: observability
- Control ID: `infra-log-query-fields`
- Measure: Infra log query returns expected fields
- Threshold: Queries return required fields (timestamp, severity, host, correlation_id)
- Tooling: Log query tests + schema
- Cadence: CI per build + weekly audit
- Environments: int, ref, prod


## Traceability

- Domain registry: requirements/nfrs/observability/nfrs.yaml
