code: STORY-SOFT-002
as_a: Architecture_Lead

i_want: evaluate_and_outsource_non_differentiating_capabilities_bottom_up
so_that: teams_focus_on_core_value
business_value: Frees engineering capacity for strategic work
nfr_refs: [NFR-SOFT-OUTSOURCE-BOTTOM-UP-01]
nfr_tags: [software-management, sourcing]
acceptance_criteria:

- GIVEN capability inventory WHEN updated THEN classification (core/commodity) maintained
- GIVEN commodity capability WHEN candidate THEN outsourcing decision includes cost-benefit and exit plan
- GIVEN review cycle WHEN quarterly THEN at least one candidate assessed for potential outsourcing
  out_of_scope:
- Vendor contract negotiation details
  notes: |
  Evidence: inventory, decision record, quarterly review summary.

---

# Summary

Structured evaluation and outsourcing of commodity capabilities.
