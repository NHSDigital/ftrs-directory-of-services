---
code: STORY-REUSE-002
as_a: UX_Engineer
i_want: align_ui_components_with_nhs_design_system
so_that: users_experience_consistent_and_accessible_interfaces
business_value: Improves usability and reduces custom maintenance
nfr_refs: [NFR-DESIGN-SYSTEM-ALIGN-01]
nfr_tags: [reuse, ux, accessibility]
acceptance_criteria:
  - GIVEN component build WHEN feasible THEN use approved Design System component variant
  - GIVEN accessibility audit WHEN performed THEN zero WCAG AA violations attributable to custom components
  - GIVEN new component request WHEN divergence needed THEN exception record including rationale and expiry
out_of_scope:
  - Full redesign of legacy feature flows
notes: |
  Evidence: component inventory, accessibility audit report, exception log.
---
# Summary
Adopt NHS Design System components and manage exceptions.

## Detail
Ensures UI implementation aligns with centrally governed NHS Design System improving accessibility and consistency. Exceptions are time-bound with rationale and expiry to prevent divergence from shared patterns. Accessibility audits validate no custom component introduces WCAG AA issues.

## Deriving Acceptance Criteria from NFRs
- NFR-DESIGN-SYSTEM-ALIGN-01: Each acceptance criterion maps to conformance (component usage, audit result, managed exception) and provides evidence through inventory, audit, exception register.

## INVEST Checklist
- Independent: Can be delivered separate from backend changes.
- Negotiable: Specific exception lifecycle tooling details.
- Valuable: Reduces maintenance overhead and improves accessibility compliance.
- Estimable: Inventory review + audit scope defined.
- Small: Bounded to inventory update & exception governance.
- Testable: Audit report + exception log + component diff.
