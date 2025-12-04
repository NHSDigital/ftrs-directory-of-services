---
story_id: STORY-OBS-014
title: Structured logging schema validated in CI for DM_ETL_* events
role: Platform Engineer
goal: Prevent log schema drift and guarantee required fields for observability
value: Ensures reliable queries and dashboards; reduces forensic gaps
nfr_refs: [OBS-014, OBS-019]
status: draft
---

## Acceptance Criteria

1. Required fields for DM*ETL*\*: `run_id`, `environment`, `workspace`, `record_id`, `transformer_name`, `elapsed_time`, `counts`.
2. CI job validates samples/full logs; fails on missing fields or bad types.
3. 1% sampled runs auto-validated; failures alert.
4. Dashboard queries rely on validated fields; zero schema errors in 2 consecutive runs.
5. Documentation lists schema with examples.

## Non-Functional Acceptance

- Control: OBS-014
- Cadence: CI per commit and nightly sample validation
- Environments: int, ref, prod
