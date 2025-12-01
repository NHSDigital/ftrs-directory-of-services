---
code: STORY-CLOUD-003
as_a: Cost_Analyst
i_want: enforce_minimum_40_percent_off_peak_scale_down_and_utilisation_visibility
so_that: we_optimise_spend_and_reduce_waste
business_value: Direct cloud cost savings and improved efficiency
nfr_refs: [NFR-CAPACITY-UTIL-01]
nfr_tags: [capacity, cost, cloud]
acceptance_criteria:
  - GIVEN production workloads WHEN off-peak window reached THEN aggregated running cost shows >=40% reduction vs same-day peak hour
  - GIVEN scaling events WHEN analysed THEN utilisation metrics (CPU, memory, I/O) show >60% average occupancy during peak
  - GIVEN dashboards WHEN viewed THEN utilisation and cost reduction panels display last 30 days trend
out_of_scope:
  - Rightsizing individual instance families
notes: |
  Supports NFR-CAPACITY-UTIL-01. Evidence: cost explorer export, utilisation monitoring dashboard snapshots.
---
# Summary
Visibility and enforcement of utilisation and mandated scale-down threshold.

## Detail
Ensures horizontal/vertical autoscaling policies reduce off-peak capacity footprint while maintaining performance SLOs. Establishes utilisation dashboard surfacing peak vs off-peak trends and validates scaling events achieve targeted cost reduction. Acceptance verifiable via cost metrics and utilisation telemetry.

## Deriving Acceptance Criteria from NFRs
- NFR-CAPACITY-UTIL-01: Criteria map to cost reduction percentage, utilisation >60% at peak, and dashboard visibility for trend over selected period.

## INVEST Checklist
- Independent: Only depends on metrics export availability.
- Negotiable: Exact % targets and dashboard fields.
- Valuable: Direct cloud spend reduction & efficiency insight.
- Estimable: Scaling policy config + dashboard build.
- Small: Constrained to metrics + policy tuning.
- Testable: Cost report, utilisation panel, scaling event logs.
