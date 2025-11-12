---
id: STORY-128
title: Anonymised end user behaviour metrics
nfr_refs:
  - OBS-031
  - OBS-026
type: observability
status: draft
owner: product-team
summary: Capture product usage metrics with anonymisation preserving privacy while enabling insight.
---

## Description
Implement pseudonymisation & aggregation for user behaviour metrics (feature usage, session length) ensuring no direct identifiers stored.

## Acceptance Criteria
- Metrics stored without personal identifiers; pseudonymisation validated.
- Differential privacy / aggregation prevents single-user inference.
- Re-identification attempt fails.
- Metrics available for analytics pattern queries.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| pseudonymisation_validation_test | automated | No direct IDs |
| reidentification_attempt_simulation | automated | Fails |
| aggregation_boundary_check | automated | Min cohort size enforced |
| analytics_query_integration_test | automated | Metrics usable |

## Traceability
NFRs: OBS-031, OBS-026
