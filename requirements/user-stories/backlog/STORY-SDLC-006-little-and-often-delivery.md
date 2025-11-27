---
code: STORY-SDLC-006
as_a: Product_Manager
i_want: maintain_little_and_often_delivery_principle
so_that: value_is_released_incrementally_and_risk_reduced
business_value: Faster feedback loops and lower batch risk
nfr_refs: [NFR-SDLC-LITTLE-OFTEN-01]
nfr_tags: [sdlc, delivery]
acceptance_criteria:
  - GIVEN release cadence WHEN measured THEN >4 production releases per month per active service (where appropriate)
  - GIVEN large change WHEN identified THEN decomposed into stories <= 3 days effort
  - GIVEN retro WHEN performed THEN delivery metrics reviewed and improvement actions tracked
out_of_scope:
  - Portfolio-level funding model changes
notes: |
  Evidence: deployment dashboard, decomposition examples, retro summary.
---

# Summary

Principle of frequent small releases tracked and reinforced.
