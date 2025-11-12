---
id: STORY-073
title: Bidirectional scaling efficiency
nfr_refs:
  - SCAL-004
  - SCAL-005
  - SCAL-008
type: scalability
status: draft
owner: platform-team
summary: Demonstrate automated scale-out and scale-down responding to demand changes with guardrails and no manual intervention.
---

## Description
Configure autoscaling policies with min/max bounds, cooldowns, and utilisation metrics. Simulate demand spike and subsequent trough verifying scale-out & scale-in events are triggered automatically without oscillation or manual action.

## Acceptance Criteria
- Autoscaling policy defines min/max, target utilisation, cooldown.
- Spike simulation increases replicas; trough simulation decreases replicas.
- No more than one scale action per defined cooldown window (no thrash).
- Ops log has zero manual scaling tickets for test period.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| policy_config_lint | automated | Policy meets guardrail schema |
| spike_simulation_event | automated | Scale-out event logged |
| trough_simulation_event | automated | Scale-in event logged |
| cooldown_thrash_check | automated | No rapid alternating events |
| ops_manual_ticket_scan | automated | Zero manual interventions |

## Traceability
NFRs: SCAL-004, SCAL-005, SCAL-008
