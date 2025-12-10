---
story_id: STORY-COMP-006
title: ≥90% critical journeys test pass per platform
role: QA Engineer
goal: Deliver: ≥90% critical journeys test pass per platform
value: Critical user journeys pass across all supported platforms at target success rate.
nfr_refs: [COMP-003]
status: draft
---

## Description

Implement and validate NFR `COMP-003` for domain `compatibility`.

## Acceptance Criteria

- >= 90% pass rate for critical journeys on each supported platform
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `COMP-003`
- Domain: compatibility
- Control ID: `journeys-pass-rate`
- Measure: ≥90% critical journeys test pass per platform
- Threshold: >= 90% pass rate for critical journeys on each supported platform
- Tooling: Cross-platform automated E2E tests
- Cadence: CI per build + release candidate validation
- Environments: int, ref


## Traceability

- Domain registry: requirements/nfrs/compatibility/nfrs.yaml
