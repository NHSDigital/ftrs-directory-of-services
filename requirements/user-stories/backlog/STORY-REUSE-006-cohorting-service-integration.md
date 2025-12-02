---
code: STORY-REUSE-006
as_a: Data_Service_Engineer
i_want: integrate_with_cohorting_as_a_service
so_that: we_can_target_specific_patient_or_provider_segments
business_value: Enables personalized interventions while reducing bespoke cohort logic
nfr_refs: [NFR-REUSE-COHORTING-01]
nfr_tags: [reuse, data]
acceptance_criteria:
  - GIVEN cohort definition WHEN created THEN stored via service API with versioning
  - GIVEN targeting run WHEN executed THEN results available within agreed SLA and logged
  - GIVEN cohort change WHEN updated THEN previous version retained for audit
out_of_scope:
  - Predictive cohort generation via ML
notes: |
  Evidence: API calls, version history sample, SLA metrics.
---

# Summary

Cohorting Service integration for versioned segment targeting.

## Detail

Adds integration with Cohorting As A Service to define, version, and execute targeting of specific user/provider segments. Supports auditability by preserving historical versions and logging execution results against SLAs.

## Deriving Acceptance Criteria from NFRs

- NFR-REUSE-COHORTING-01: Cohort versioning, SLA-bound execution logging, and audit trail for changes.

## INVEST Checklist

- Independent: Does not rely on Notify integration.
- Negotiable: Version metadata detail level.
- Valuable: Enables targeted interventions efficiently.
- Estimable: API calls + version storage + logging tasks.
- Small: Single integration and reporting features.
- Testable: Version history sample, execution log, SLA metrics.
