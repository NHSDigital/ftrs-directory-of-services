code: STORY-SOFT-006
as_a: Platform_Engineer

i_want: maintain_inventory_and_decommission_unused_resources
so_that: cost_and_security_surface_are_minimized
business_value: Reduces waste and potential attack vectors
nfr_refs: [NFR-SOFT-INVENTORY-DECOMMISSION-01]
nfr_tags: [software-management, ops]
acceptance_criteria:

- GIVEN resource inventory WHEN monthly scan completes THEN orphaned resources flagged
- GIVEN orphaned resource WHEN validated THEN decommission plan executed within 30 days
- GIVEN cost report WHEN reviewed THEN savings from decommission tracked
  out_of_scope:
- Real-time asset tracking across all cloud accounts
  notes: |
  Evidence: inventory scan output, decommission ticket, cost savings report.

---

# Summary

Inventory management and timely decommissioning of unused resources.
