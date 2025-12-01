---
code: STORY-CLOUD-007
as_a: Reliability_Engineer
i_want: perform_scheduled_active_passive_region_swap
so_that: we_validate_failover_and_detect_configuration_drifts
business_value: Increases confidence in regional resiliency
nfr_refs: [NFR-DR-ACTIVE-PASSIVE-SWAP-01]
nfr_tags: [dr, reliability, multi-region]
acceptance_criteria:
  - GIVEN passive region readiness WHEN quarterly window THEN swap initiated via automated runbook
  - GIVEN swap completion WHEN traffic cutover THEN key SLOs unchanged and error rate < baseline + 5%
  - GIVEN drift findings WHEN discrepancies detected THEN remediation backlog item created
out_of_scope:
  - Multi-active architectural redesign
notes: |
  Evidence: runbook, monitoring screenshots pre/post swap, drift report.
  Checklist: requirements/user-stories/checklists/active-passive-swap-checklist.md
---
# Summary
Quarterly active-passive regional swap to exercise failover path.

## Detail
Executes scheduled cutover from active to passive region/site to validate failover readiness, uncover configuration drift, and ensure resilience targets remain stable. Drift findings are captured for remediation planning.

## Deriving Acceptance Criteria from NFRs
- NFR-OPERATIONS-ACTIVE-PASSIVE-01: Periodic swap execution; unchanged SLOs; drift detection and ticketing.

## INVEST Checklist
- Independent: Only requires existing passive environment readiness.
- Negotiable: Exact swap frequency (quarterly vs semiannual).
- Valuable: Confirms true operability of DR path & config parity.
- Estimable: Runbook execution + monitoring comparison.
- Small: Single scheduled swap & analysis.
- Testable: Swap logs, SLO metrics diff, drift report.
