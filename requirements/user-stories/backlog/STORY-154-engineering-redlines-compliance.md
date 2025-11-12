---
id: STORY-154
title: Engineering Red-lines compliance confirmation
nfr_refs:
  - GOV-004
type: governance
status: draft
owner: principal-engineering
summary: Demonstrate adherence to NHS England Engineering Red-lines.
---

## Description
Compile compliance checklist mapping red-line requirements to implementation evidence; capture Principal System Engineer sign-off.

## Acceptance Criteria
- Checklist shows 100% requirements addressed or exception logged.
- Exception count & mitigation plan documented.
- Principal sign-off recorded with date.
- Automated diff highlights changes since last review.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| checklist_completion_scan | automated | All items addressed |
| exception_presence_test | automated | Exceptions have mitigation |
| signoff_record_scan | automated | Principal signature present |
| diff_generation_validation | automated | Diff output stored |

## Traceability
NFRs: GOV-004
