---
id: STORY-106
title: Publish supported OS & browser matrix
nfr_refs:
  - COMP-001
  - COMP-003
type: compatibility
status: draft
owner: product-team
summary: Provide and maintain a documented matrix of supported OS/browser combinations aligned with NHS Spine Warrantied spec.
---

## Description
Create a versioned compatibility document listing supported operating systems and browsers (including versions) matching the NHS Spine Warrantied Environment specification. Integrate automated UI regression coverage reporting per combination.

## Acceptance Criteria
- Compatibility matrix published in docs & version-controlled.
- Each listed OS/browser has at least one automated critical journey test.
- Coverage report shows ≥90% of critical journeys per platform.
- Matrix update triggers test suite run & results archived.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| matrix_document_presence | automated | File exists & version header present |
| platform_test_presence_scan | automated | At least one test per matrix entry |
| coverage_threshold_enforcement | automated | All platforms ≥90% coverage |
| matrix_update_trigger | automated | CI run triggered & results stored |

## Traceability
NFRs: COMP-001, COMP-003
