---
id: STORY-168
title: Versioned performance expectations table
nfr_refs:
  - PERF-003
  - PERF-010
type: performance
status: draft
owner: performance-team
summary: Publish and version a table of P95 latency expectations for significant user actions.
---

## Description
Create performance expectations table (request, action, spec link, endpoint URI, P95 target ms, notes). Enforce schema validation and version diff review in PRs.

## Acceptance Criteria
- Table file present with required columns.
- Schema validation passes in CI.
- Version diff shows changes to targets explicitly.
- Each action mapped to existing endpoint contract.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| table_schema_validation | automated | Pass |
| version_diff_target_change_test | automated | Diff output present |
| endpoint_mapping_verification | automated | All URIs valid |
| missing_column_failure_test | automated | Build fails |

## Traceability
NFRs: PERF-003, PERF-010
