---
story_id: STORY-INT-025
title: Terminology bindings validated
role: Integration Engineer
goal: Deliver: Terminology bindings validated
value: Terminology bindings are validated to ensure correct coding.
nfr_refs: [INT-012]
status: draft
---

## Description

Implement and validate NFR `INT-012` for domain `interoperability`.

## Acceptance Criteria

- 100% required bindings validated against value sets
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `INT-012`
- Domain: interoperability
- Control ID: `terminology-binding-validation`
- Measure: Terminology bindings validated
- Threshold: 100% required bindings validated against value sets
- Tooling: Terminology server + validators
- Cadence: CI per build + monthly audit
- Environments: int, ref, prod

## Traceability

- Domain registry: requirements/nfrs/interoperability/nfrs.yaml
