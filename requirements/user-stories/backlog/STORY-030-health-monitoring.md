---
id: STORY-030
title: Health monitoring across layers
nfr_refs:
  - OBS-001
type: observability
status: draft
owner: platform-team
summary: Implement unified health monitoring for app, infra, OS, and system layers.
---

## Description
Expose consolidated health endpoints and dashboards showing status for application services, infrastructure components, operating system metrics, and supporting system dependencies.

## Acceptance Criteria
- Health dashboard panels for app, infra, OS, system all green under nominal conditions.
- Synthetic probe failure reflects in dashboard within 60s.
- Health endpoint returns JSON with component statuses & timestamps.
- Failed component transitions panel to warning/critical state.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| synthetic_probe_injection | automated | Dashboard updates <60s |
| health_endpoint_contract | automated | JSON schema valid |
| component_failure_simulation | automated | Status = critical |
| dashboard_panel_presence | automated | All four layer panels present |

## Traceability
NFRs: OBS-001
