---
code: STORY-REUSE-005
as_a: Communications_Engineer
i_want: use_nhs_notify_for_transactional_messages
so_that: we_deliver_reliable_and_governed_email_sms
business_value: Reduces custom messaging overhead and ensures compliance
nfr_refs: [NFR-REUSE-NOTIFY-01]
nfr_tags: [reuse, communications]
acceptance_criteria:
  - GIVEN message dispatch WHEN triggered THEN sent via NHS Notify API with template ID
  - GIVEN delivery failure WHEN occurs THEN retry policy applied and metrics recorded
  - GIVEN message audit WHEN requested THEN log shows recipient, template, status with PII minimized
out_of_scope:
  - Bulk marketing campaigns
notes: |
  Evidence: API configuration, delivery metrics dashboard, audit log sample.
---
# Summary
Adopt NHS Notify for governed transactional messaging.

## Detail
Integrates NHS Notify API for all transactional email/SMS, standardising template usage, delivery reliability, and audit logging. Implements retry and delivery metrics to ensure communication effectiveness and governance compliance.

## Deriving Acceptance Criteria from NFRs
- NFR-REUSE-NOTIFY-01: Template-based dispatch; retry and failure metrics; auditable log with minimal PII.

## INVEST Checklist
- Independent: Separate from cohorting or design system stories.
- Negotiable: Retry policy parameters.
- Valuable: Improves reliability and governance of messaging.
- Estimable: API integration + metrics + logging tasks.
- Small: Limited to transactional path adoption.
- Testable: API config, metrics dashboard, audit log sample.
