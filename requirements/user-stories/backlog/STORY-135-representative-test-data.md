---
id: STORY-135
title: Representative accessibility test data
nfr_refs:
  - ACC-007
  - ACC-001
type: accessibility
status: draft
owner: data-team
summary: Provide dummy test data covering tables, forms, and status messages for accessibility validation.
---

## Description
Create and maintain seeded datasets enabling meaningful accessibility scans (layout structures, form flows, varied status messages) across environments.

## Acceptance Criteria
- Dataset includes at least: 3 complex tables, 5 multi-step forms, success/warning/error status examples.
- Versioned dataset definition file present.
- Accessibility scans confirm elements present.
- Missing element triggers dataset completeness alert.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| dataset_structure_validation | automated | Required elements present |
| accessibility_scan_element_presence | automated | Elements detected |
| dataset_version_file_check | automated | Version info present |
| missing_element_alert_test | automated | Alert fired |

## Traceability
NFRs: ACC-007, ACC-001
