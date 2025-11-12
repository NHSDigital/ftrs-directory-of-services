---
id: STORY-107
title: Cross-platform CIS2 MFA compatibility
nfr_refs:
  - COMP-002
  - COMP-001
type: compatibility
status: draft
owner: auth-team
summary: Ensure CIS2 MFA login flows function across all supported OS/browser platforms without platform-specific failures.
---

## Description
Execute automated authentication scenarios (initial login, session renewal) across each supported OS/browser combination to validate CIS2 compatibility and capture pass rates. Failures block release until resolved.

## Acceptance Criteria
- ≥99.9% MFA auth pass rate per platform across test runs.
- No platform-specific UI rendering issues causing login failure.
- Correlation IDs logged for all auth attempts.
- Failures produce actionable diagnostic output (screenshot/log snippet).

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| cross_platform_auth_suite | automated | Pass rate ≥99.9% |
| ui_render_check | automated | No blocking visual defects |
| correlation_id_logging_test | automated | ID present in all attempts |
| failure_diagnostics_capture | automated | Artifacts stored on failure |

## Traceability
NFRs: COMP-002, COMP-001
