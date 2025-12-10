---
story_id: STORY-INT-021
title: Identifier normalization applied (uppercase, trimmed)
role: Integration Engineer
goal: Deliver: Identifier normalization applied (uppercase, trimmed)
value: Identifiers are normalised (case, trimming) for consistent matching.
nfr_refs: [INT-006]
status: draft
---

## Description

Implement and validate NFR `INT-006` for domain `interoperability`.

## Acceptance Criteria

- 100% identifiers normalised; mismatches \u2264 0.1%
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `INT-006`
- Domain: interoperability
- Control ID: `identifier-normalization-enforced`
- Measure: Identifier normalization applied (uppercase, trimmed)
- Threshold: 100% identifiers normalised; mismatches \u2264 0.1%
- Tooling: Normalization middleware + validation tests
- Cadence: CI per build + monthly audit
- Environments: int, ref, prod

## Traceability

- Domain registry: requirements/nfrs/interoperability/nfrs.yaml
