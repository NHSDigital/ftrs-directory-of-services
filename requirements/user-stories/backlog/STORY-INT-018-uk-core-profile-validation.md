---
story_id: STORY-INT-018
title: Resources validated against UK Core profiles
role: Integration Engineer
goal: Deliver: Resources validated against UK Core profiles
value: Resources conform to UK Core profiles ensuring national standard alignment.
nfr_refs: [INT-001]
status: draft
---

## Description

Implement and validate NFR `INT-001` for domain `interoperability`.

## Acceptance Criteria

- 100% resources pass UK Core validation in CI and pre-release audit
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `INT-001`
- Domain: interoperability
- Control ID: `uk-core-profile-validation`
- Measure: Resources validated against UK Core profiles
- Threshold: 100% resources pass UK Core validation in CI and pre-release audit
- Tooling: FHIR validators + contract test suite
- Cadence: CI per build + quarterly audit
- Environments: int, ref, prod


## Traceability

- Domain registry: requirements/nfrs/interoperability/nfrs.yaml
