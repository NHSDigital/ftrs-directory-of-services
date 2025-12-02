---
code: STORY-REUSE-003
as_a: Identity_Engineer
i_want: integrate_with_nhs_login_for_user_authentication
so_that: users_have_secure_and_familiar_access_method
business_value: Reduces credential management overhead and improves trust
nfr_refs: [NFR-IDENTITY-NHS-LOGIN-01]
nfr_tags: [reuse, identity, security]
acceptance_criteria:
  - GIVEN user authentication WHEN login initiated THEN redirected through NHS Login OAuth flow
  - GIVEN successful auth WHEN completed THEN identity assertions stored with session and PII minimized
  - GIVEN assurance level requirement WHEN enforced THEN flows adapt to IAL2+ where specified
out_of_scope:
  - Federation with non-NHS identity providers
notes: |
  Evidence: sequence diagram, configuration, successful test tokens redacted.
---

# Summary

NHS Login integration for secure authentication at required assurance level.

## Detail

Integrates NHS Login OAuth/OpenID Connect flow for user authentication, capturing only minimal required identity assertions and adapting flows based on required identity assurance level (IAL) for sensitive features. Enhances trust while reducing credential management overhead.

## Deriving Acceptance Criteria from NFRs

- NFR-IDENTITY-NHS-LOGIN-01: Redirect through NHS Login, store assertions with PII minimisation, enforce elevated IAL where specified.

## INVEST Checklist

- Independent: Can be delivered separate from cohorting integration.
- Negotiable: Exact session attribute storage format.
- Valuable: Improves security and reduces auth maintenance.
- Estimable: Flow integration + session handling tasks.
- Small: Limited to auth integration & test verification.
- Testable: Auth sequence diagram, test tokens, assurance enforcement evidence.
