---
id: STORY-136
title: CI accessibility scan step
nfr_refs:
  - ACC-008
  - ACC-002
type: accessibility
status: draft
owner: devops-team
summary: Add accessibility scan stage to CI pipeline executing automated checks.
---

## Description
Integrate accessibility scanning job into CI pipeline triggered on pull request and main branch merges with configurable thresholds.

## Acceptance Criteria
- CI stage runs on PR and main merges.
- Stage fails on critical violations.
- Configurable thresholds (warn vs fail) versioned.
- Execution time logged.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| pipeline_stage_presence | automated | Stage detected |
| violation_injection_failure | pipeline | Stage fails |
| threshold_config_validation | automated | File schema valid |
| execution_time_logging_check | automated | Time metric present |

## Traceability
NFRs: ACC-008, ACC-002
