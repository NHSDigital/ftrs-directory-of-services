---
id: STORY-138
title: Focus trap regression tests for modals and overlays
nfr_refs:
  - ACC-010
  - ACC-009
type: accessibility
status: draft
owner: qa-team
summary: Ensure modals and overlays do not trap focus and allow escape.
---

## Description
Automate opening/closing modals and overlays verifying focus entry point, tab-cycle boundaries, and ability to exit using standard interactions (Esc, close button).

## Acceptance Criteria
- Modal focus starts on first interactive element inside.
- Tab cycling does not leave modal until closed.
- Esc key closes modal and restores prior focus.
- Overlay focus behavior matches modal rules.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| modal_focus_entry_test | automated | First element focused |
| focus_cycle_boundary_test | automated | Cycle contained |
| esc_key_exit_test | automated | Focus restored |
| overlay_focus_behavior_test | automated | Matches modal rules |

## Traceability
NFRs: ACC-010, ACC-009
