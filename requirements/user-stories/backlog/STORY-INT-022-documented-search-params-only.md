---
story_id: STORY-INT-022
title: Only documented FHIR search params accepted
role: Integration Engineer
goal: Deliver: Only documented FHIR search params accepted
value: Only documented FHIR search parameters are accepted; unknown ones rejected.
nfr_refs: [INT-009]
status: draft
---

## Description

Implement and validate NFR `INT-009` for domain `interoperability`.

## Acceptance Criteria

- Unknown search params rejected with OperationOutcome
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `INT-009`
- Domain: interoperability
- Control ID: `documented-search-params-only`
- Measure: Only documented FHIR search params accepted
- Threshold: Unknown search params rejected with OperationOutcome
- Tooling: API gateway policy + contract tests
- Cadence: CI per build
- Environments: int, ref, prod

## Traceability

- Domain registry: requirements/nfrs/interoperability/nfrs.yaml
