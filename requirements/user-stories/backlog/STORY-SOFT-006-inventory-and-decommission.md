---
story_id: STORY-SOFT-006
title: "Inventory and decommission unused resources"
role: Platform Engineer
goal: "Maintain inventory and decommission unused resources"
value: Reduces waste and potential attack vectors
nfr_refs: [NFR-SOFT-INVENTORY-DECOMMISSION-01]
status: draft
---

## Description

Inventory management and timely decommissioning of unused resources.

## Acceptance Criteria

1. GIVEN a resource inventory WHEN a monthly scan completes THEN orphaned resources are flagged
2. GIVEN an orphaned resource WHEN validated THEN the decommission plan is executed within 30 days
3. GIVEN a cost report WHEN reviewed THEN savings from decommission are tracked

## Out of Scope

- Real-time asset tracking across all cloud accounts

## Implementation Notes

- Evidence: inventory scan output, decommission ticket, cost savings report

## Summary

Inventory management and timely decommissioning of unused resources.
