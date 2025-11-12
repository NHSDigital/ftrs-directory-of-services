---
id: STORY-087
title: Align API availability with core service
nfr_refs:
  - AVAIL-008
type: availability
status: draft
owner: platform-team
summary: Ensure external and internal APIs meet core 24x7 availability periods excluding scheduled maintenance.
---

## Description
Instrument APIs with uptime probes & integrate maintenance window exclusion logic; confirm API availability metrics match core service availability figures.

## Acceptance Criteria
- API uptime dashboard mirrors core availability timeline.
- Maintenance window exclusion logic applied consistently.
- Random API probe checks succeed during off-peak hours.
- Alert triggers on deviation in API vs core availability >0.1% monthly.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| api_vs_core_availability_diff | automated | Diff ≤0.1% |
| maintenance_exclusion_consistency | automated | Exclusions match core logic |
| off_peak_probe_tests | manual | Success |
| deviation_alert_simulation | automated | Alert when diff threshold crossed |

## Traceability
NFRs: AVAIL-008
