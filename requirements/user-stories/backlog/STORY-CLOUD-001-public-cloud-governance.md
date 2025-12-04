---
code: STORY-CLOUD-001
as_a: Platform_Engineer
i_want: governed_public_cloud_accounts_and_internet_first_design
so_that: services_are_secure_scalable_and_aligned_with_org_policies
business_value: Reduced operational risk; faster onboarding; consistent compliance posture
nfr_refs: [NFR-CLOUD-GOV-01]
nfr_tags: [cloud, governance, security]
acceptance_criteria:
  - GIVEN a new product WHEN provisioning cloud accounts THEN accounts exist separately for prod and non-prod under mandated org units
  - GIVEN AWS usage WHEN accounts created THEN they reside within NHS AWS Landing Zone
  - GIVEN Azure usage WHEN subscriptions created THEN they reside within NHSE-LZ-Root MG structure
  - GIVEN service network design WHEN reviewed THEN solution is internet-first with HSCN only for approved legacy exception documented
  - GIVEN gold_or_platinum classification WHEN deployment occurs THEN blue/green method used with zero failed requests during switch
  - GIVEN DR policy WHEN scheduled THEN full isolated restore test executed at least once per 24 months producing evidence artifact
  - GIVEN autoscaling windows WHEN off-peak hour reached THEN cost footprint shows >=40% reduction from same-day peak hour
out_of_scope:
  - Detailed network CIDR planning
notes: |
  Aligns to NFR-CLOUD-GOV-01. Evidence sources: Org account registry, landing zone configuration, deployment pipeline logs, DR test run book, cost explorer reports.
---

# Summary

Public cloud governance enforcing account separation, landing zone placement, internet-first, scaling and DR testing.

## Detail

Covers structural guardrails ensuring consistent placement inside enterprise landing zones and subscription MG hierarchy. Enforces blue/green for high-tier services and periodic DR validation.

## INVEST Checklist

- Independent: Yes
- Negotiable: Autoscale % threshold tooling details
- Valuable: Reduces compliance exceptions
- Estimable: Requires infrastructure and cost analysis tasks
- Small: Fits sprint with provisioning automation
- Testable: Each criterion has observable artifact.
