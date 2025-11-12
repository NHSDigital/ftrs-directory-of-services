---
id: STORY-078
title: Audit scaling actions
nfr_refs:
  - SCAL-009
  - SCAL-005
type: scalability
status: draft
owner: platform-team
summary: Ensure each scaling action (auto or manual) is logged with timestamp, actor, reason, and target resources.
---

## Description
Implement structured audit logging for scaling actions; integrate with autoscaling controllers and manual override workflows to record context.

## Acceptance Criteria
- Audit log schema documented and versioned.
- Sample scale-out and scale-in entries show all required fields.
- Manual override includes justification field.
- Query tool returns scale actions filtered by actor and time range.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| audit_schema_presence | manual | Schema committed |
| scale_out_audit_entry_test | automated | Entry contains fields |
| manual_override_entry_test | automated | Justification recorded |
| audit_query_filter_test | manual | Query returns correct subset |

## Traceability
NFRs: SCAL-009, SCAL-005
