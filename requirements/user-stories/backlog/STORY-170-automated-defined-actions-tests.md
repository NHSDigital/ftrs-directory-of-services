---
id: STORY-170
title: Automated performance tests for defined actions
nfr_refs:
  - PERF-005
  - PERF-003
type: performance
status: draft
owner: qa-performance
summary: Implement automated performance test suite covering only defined actions and excluding agreed non-scope actions.
---

## Description
Create manifest enumerating included actions referencing performance expectations table; maintain exclusion list; generate load profiles and run tests using JMeter/k6.

## Acceptance Criteria
- Manifest file references all table actions.
- Exclusion list present & justified.
- Test run results stored with P95 metrics per action.
- CI gate fails if missing action or unapproved inclusion.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| manifest_alignment_validation | automated | All actions mapped |
| exclusion_list_schema_test | automated | Justification field present |
| p95_metrics_export_check | automated | Metrics file created |
| missing_action_gate_failure | pipeline | Build fails |

## Traceability
NFRs: PERF-005, PERF-003
