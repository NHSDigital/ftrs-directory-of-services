---
id: STORY-156
title: Medical Device Directive scope assessment
nfr_refs:
  - GOV-006
type: governance
status: draft
owner: compliance-team
summary: Confirm FtRS remains out of scope of Medical Device Directive and establish trigger for reassessment.
---

## Description
Perform scope assessment documenting functional boundaries; define trigger conditions for re-assessment if clinical decision features emerge.

## Acceptance Criteria
- Scope statement stored & versioned.
- Trigger conditions file lists feature patterns.
- Periodic review log updated (quarterly).
- Alert configured on commit introducing trigger keyword.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| scope_statement_presence | automated | File exists |
| trigger_conditions_validation | automated | Keywords & patterns present |
| review_log_recent_entry | automated | Entry within quarter |
| commit_keyword_alert_test | automated | Alert fired on keyword commit |

## Traceability
NFRs: GOV-006
