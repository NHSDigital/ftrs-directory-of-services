---
code: STORY-REUSE-007
as_a: Security_Architect
i_want: enforce_identity_assurance_levels_in_user_flows
so_that: sensitive_features_have_appropriate_identity_rigor
business_value: Reduces fraud and protects sensitive operations
nfr_refs: [NFR-IDENTITY-ASSURANCE-LEVELS-01]
nfr_tags: [reuse, identity, security]
acceptance_criteria:
  - GIVEN feature classification WHEN marked sensitive THEN requires IAL2+ authentication evidence
  - GIVEN session downgrade WHEN assurance insufficient THEN access blocked with remediation guidance
  - GIVEN audit WHEN performed THEN assurance level decision traceable to policy
out_of_scope:
  - Biometric identity verification enhancements
notes: |
  Evidence: policy doc, feature classification matrix, audit log excerpt.
---

# Summary

Identity assurance enforcement aligned to classification and policy.

## Detail

Implements enforcement of identity assurance based on feature sensitivity, requiring higher IAL for critical operations and blocking access when assurance is insufficient. Provides auditable mapping from feature classification to required assurance level.

## Deriving Acceptance Criteria from NFRs

- NFR-IDENTITY-ASSURANCE-LEVELS-01: Sensitive features require IAL2+; downgrade blocks access; audit trace links decision to policy.

## INVEST Checklist

- Independent: Separate from NHS Login integration specifics.
- Negotiable: Classification matrix granularity.
- Valuable: Reduces fraud risk and misuse of sensitive features.
- Estimable: Classification mapping + enforcement logic.
- Small: One mapping artifact and enforcement checks.
- Testable: Policy doc, classification matrix, audit log excerpt.
