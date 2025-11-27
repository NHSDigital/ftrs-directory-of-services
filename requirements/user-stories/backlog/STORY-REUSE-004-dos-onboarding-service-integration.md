---
code: STORY-REUSE-004
as_a: Service_Manager
i_want: integrate_with_digital_onboarding_service
so_that: onboarding_and_governance_processes_are_streamlined
business_value: Accelerates time-to-market and standardizes compliance checks
nfr_refs: [NFR-REUSE-DOS-ONBOARD-01]
nfr_tags: [reuse, governance]
acceptance_criteria:
  - GIVEN new service onboarding WHEN initiated THEN DOS workflow started with mandatory metadata captured
  - GIVEN governance checklist WHEN completed THEN artifacts stored in central repository
  - GIVEN onboarding completion WHEN approved THEN status updated and notifications sent to stakeholders
out_of_scope:
  - Automated decommissioning flow
notes: |
  Evidence: onboarding ticket, metadata record, approval audit trail.
---

# Summary

Integrate with Digital Onboarding Service to standardize governance.

## Detail

Automates initiation of Digital Onboarding Service (DOS) workflow for each new service, capturing mandatory metadata and governance artifacts centrally. Provides consistent approval tracking, accelerates readiness evaluation, and reduces manual variance.

## Deriving Acceptance Criteria from NFRs

- NFR-REUSE-DOS-ONBOARD-01: Workflow start with required metadata; governance artifacts stored; completion status update & stakeholder notifications.

## INVEST Checklist

- Independent: Does not depend on NHS Login integration.
- Negotiable: Notification channels specifics.
- Valuable: Speeds compliance and onboarding consistency.
- Estimable: API calls + metadata schema + notification tasks.
- Small: Single integration path and artifact storage.
- Testable: Onboarding ticket, metadata record, approval audit trail.
