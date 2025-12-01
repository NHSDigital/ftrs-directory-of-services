---
code: STORY-CLOUD-002
as_a: Network_Architect
i_want: all_services_internet_first_with_documented_legacy_exceptions
so_that: we_reduce_cost_complexity_and_enable_modern_access_patterns
business_value: Lower operational overhead and faster integration
nfr_refs: [CTRL-NET-INTERNET-FIRST-01]
nfr_tags: [network, cloud]
acceptance_criteria:
  - GIVEN a new service WHEN initial architecture reviewed THEN ingress/egress defined for public internet with no default HSCN dependency
  - GIVEN a legacy integration requiring HSCN WHEN exception requested THEN approval ticket stored with justification and expiry date
  - GIVEN monitoring WHEN quarterly audit runs THEN report lists zero unapproved HSCN connections
out_of_scope:
  - VPN tunnel implementation details
notes: |
  Implements CTRL-NET-INTERNET-FIRST-01. Evidence: architecture decision records (ADR), connection inventory, quarterly audit script output.
---
# Summary
Internet-first design with managed legacy HSCN exceptions.

## Detail
Implements network design principle that all new services expose and consume capabilities via secure internet channels rather than private legacy networks. Legacy HSCN connectivity is only permitted where formally approved and tracked with an expiry for migration. Provides auditable evidence of principle adherence and exception governance.

## Deriving Acceptance Criteria from NFRs
- CTRL-NET-INTERNET-FIRST-01: Criteria assert default internet path, existence of exception ticket for any HSCN use, and periodic audit confirming no unapproved private links.

## INVEST Checklist
- Independent: Can proceed separate from other cloud governance stories.
- Negotiable: Audit frequency specifics.
- Valuable: Reduces network complexity & increases accessibility.
- Estimable: Network config + audit script tasks scoped.
- Small: Limited to configuration + exception register.
- Testable: Config diff, exception ticket, audit output.

## Detail
Services default to public internet connectivity; any legacy network dependency requires a time-bound exception record.
