---
code: STORY-SDLC-004
as_a: Architecture_Lead
i_want: validate_components_against_internal_tech_radar
so_that: we_limit_sprawl_and_encourage_standardization
business_value: Reduces maintenance overhead and risk from deprecated tech
nfr_refs: [NFR-SDLC-TECH-RADAR-01]
nfr_tags: [sdlc, architecture]
acceptance_criteria:
  - GIVEN dependency addition WHEN reviewed THEN radar status (Adopt/Trial/Assess/Hold) recorded
  - GIVEN Hold technology WHEN detected THEN exception with exit plan filed
  - GIVEN quarterly review WHEN performed THEN deprecated components list published with owners
out_of_scope:
  - Creation of new radar categories
notes: |
  Evidence: review log, exception record, quarterly report.
---
# Summary
Tech Radar compliance validation for new and existing components.
