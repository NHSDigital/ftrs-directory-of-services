---
code: STORY-REUSE-001
as_a: Integration_Engineer
i_want: register_service_dependencies_in_shared_service_catalog
so_that: support_and_governance_teams_have_visibility
business_value: Reduces hidden dependencies and accelerates incident triage
nfr_refs: [NFR-REUSE-SHARED-SERVICES-REG-01]
nfr_tags: [reuse, shared-services, governance]
acceptance_criteria:
  - GIVEN new dependency WHEN integration approved THEN entry added to catalog with owner and SLA
  - GIVEN catalog audit WHEN monthly review THEN stale or unused entries flagged
  - GIVEN incident WHEN dependency involved THEN catalog data enables contact within 15 minutes
out_of_scope:
  - Automated dependency discovery via tracing
notes: |
  Evidence: catalog entry, audit report, incident timeline showing lookup.
---
# Summary
Catalog registration for all shared service dependencies.

## Detail
Establishes mandatory catalog registration for each external or shared service dependency, capturing owner, SLA, and contact data to improve support responsiveness and reduce hidden coupling. Monthly audits surface stale or unused dependencies for remediation or removal.

## Deriving Acceptance Criteria from NFRs
- NFR-REUSE-SHARED-SERVICES-REG-01: Ensures dependency entries exist with ownership & SLA; audit identifies stale items; incident response time benefit validated.

## INVEST Checklist
- Independent: Does not require design system alignment work.
- Negotiable: Audit tooling approach.
- Valuable: Speeds incident triage and governance insight.
- Estimable: Inventory pass + audit workflow tasks.
- Small: Catalog updates and one audit cycle.
- Testable: Catalog entries, audit report, incident timeline.
