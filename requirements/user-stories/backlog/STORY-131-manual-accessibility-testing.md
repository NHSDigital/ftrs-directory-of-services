---
id: STORY-131
title: Manual accessibility test per feature release
nfr_refs:
  - ACC-003
  - ACC-004
type: accessibility
status: draft
owner: accessibility-team
summary: Conduct manual accessibility testing for each feature or major UI release.
---

## Description
Execute manual test scripts (screen reader navigation, keyboard-only flows, zoom/contrast adjustments) for each feature; record findings; ensure remediation before release.

## Acceptance Criteria
- Manual test session report stored per release.
- Screen reader test covers primary user journeys.
- Keyboard-only navigation succeeds for interactive elements.
- Contrast ratio issues remediated (AA minimum).

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| screen_reader_journey_test | manual | All steps announced |
| keyboard_navigation_traversal | manual | All focusable elements reachable |
| contrast_ratio_scan | automated | Ratios meet AA |
| remediation_verification | manual | All issues resolved |

## Traceability
NFRs: ACC-003, ACC-004
