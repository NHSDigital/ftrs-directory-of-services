---
id: STORY-130
title: Automated scans for critical pages & browsers
nfr_refs:
  - ACC-002
  - ACC-001
type: accessibility
status: draft
owner: qa-team
summary: Integrate automated accessibility scanning for all critical pages across supported browsers.
---

## Description
Define critical page list and configure automated scans (axe/pa11y/lighthouse) in CI for Chrome, Edge, Safari. Archive scan artifacts and fail build on critical issues.

## Acceptance Criteria
- Critical page manifest versioned.
- CI job runs scans across all supported browsers.
- Build fails on new critical violations.
- Scan artifacts stored for 6 months.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| manifest_validation | automated | File exists & schema valid |
| multi_browser_scan_execution | pipeline | All browsers scanned |
| critical_violation_injection | pipeline | Build fails |
| artifact_retention_check | automated | Older artifacts present |

## Traceability
NFRs: ACC-002, ACC-001
