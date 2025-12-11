---
story_id: STORY-INT-023
title: Version-controlled integration contract published
role: Integration Engineer
goal: Deliver: Version-controlled integration contract published
value: Integration contract is version-controlled and published.
nfr_refs: [INT-010]
status: draft
---

## Description

Implement and validate NFR `INT-010` for domain `interoperability`.

## Acceptance Criteria

- Contract published under version control; lint passes; updated \u22645 business days after change
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `INT-010`
- Domain: interoperability
- Control ID: `version-controlled-contract`
- Measure: Version-controlled integration contract published
- Threshold: Contract published under version control; lint passes; updated \u22645 business days after change
- Tooling: Spec repo + Spectral lint + diff job
- Cadence: CI per build + weekly audit
- Environments: int, ref, prod

## Traceability

- Domain registry: requirements/nfrs/interoperability/nfrs.yaml
