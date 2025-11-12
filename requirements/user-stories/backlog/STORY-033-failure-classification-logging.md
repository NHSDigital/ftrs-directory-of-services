---
id: STORY-033
title: Failure classification logging
nfr_refs:
  - OBS-011
type: observability
status: draft
owner: api-team
summary: Classify and log failures with type, code, and detail for rapid root cause analysis.
---

## Description
Extend error handling to record structured failure classification (error_type, code, detail, correlation_id) and surface breakdown in dashboard.

## Acceptance Criteria
- Error logs include required classification fields.
- Dashboard shows error types distribution & top 5 codes.
- Missing classification field triggers lint failure in CI.
- Sample injected error appears in dashboard <60s.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| injected_error_visibility | automated | Appears <60s |
| log_schema_validation | automated | All fields present |
| dashboard_distribution_panel | automated | Panel returns data |
| ci_lint_missing_field | automated | Build fails if field absent |

## Traceability
NFRs: OBS-011
