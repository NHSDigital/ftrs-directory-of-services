---
id: STORY-139
title: ARIA role announcements verified for custom components
nfr_refs:
  - ACC-011
  - ACC-001
type: accessibility
status: draft
owner: frontend-team
summary: Validate screen reader role announcements for custom UI components.
---

## Description
Add automated and manual tests verifying that custom components (tabs, accordions, dropdowns) expose correct ARIA roles/states and are announced properly by screen readers.

## Acceptance Criteria
- Components have appropriate role, state attributes (aria-expanded, aria-selected, etc.).
- Screen reader test logs correct announcements for each component.
- Missing role/state triggers linter failure.
- Dynamic state changes announced within 2s.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| component_role_attribute_scan | automated | Required attributes present |
| screen_reader_announcement_session | manual | Correct announcements |
| missing_attribute_lint_test | automated | Build fails |
| dynamic_state_change_announcement | automated | Announcement <2s |

## Traceability
NFRs: ACC-011, ACC-001
