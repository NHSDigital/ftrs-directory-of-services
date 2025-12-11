---
story_id: STORY-INT-026
title: Null vs absent data handled per FHIR
role: Integration Engineer
goal: Deliver: Null vs absent data handled per FHIR
value: Null vs absent data semantics follow FHIR specification rules.
nfr_refs: [INT-014]
status: draft
---

## Description

Implement and validate NFR `INT-014` for domain `interoperability`.

## Acceptance Criteria

- Responses follow FHIR rules; conformance tests pass
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `INT-014`
- Domain: interoperability
- Control ID: `null-vs-absent-semantics`
- Measure: Null vs absent data handled per FHIR
- Threshold: Responses follow FHIR rules; conformance tests pass
- Tooling: Contract tests + response validators
- Cadence: CI per build
- Environments: int, ref, prod

## Traceability

- Domain registry: requirements/nfrs/interoperability/nfrs.yaml
