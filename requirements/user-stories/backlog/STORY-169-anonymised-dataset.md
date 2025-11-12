---
id: STORY-169
title: Anonymised live-like performance test dataset
nfr_refs:
  - PERF-004
  - PERF-003
type: performance
status: draft
owner: data-team
summary: Provide anonymised dataset approximating production usage patterns for performance testing.
---

## Description
Generate dataset preserving structural distributions (record counts, field lengths, cardinalities) while removing/obfuscating any PID or sensitive identifiers; audit anonymisation.

## Acceptance Criteria
- Dataset generation script present & reproducible.
- Anonymisation audit report passes (no PID leakage).
- Distribution comparison vs production stats within tolerance (≤5% variance key metrics).
- Dataset version & hash recorded.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| generation_script_execution | automated | Exit 0 & artifact produced |
| anonymisation_audit_scan | automated | No sensitive fields |
| distribution_variance_check | automated | ≤5% variance metrics |
| dataset_version_hash_test | automated | Hash & version logged |

## Traceability
NFRs: PERF-004, PERF-003
