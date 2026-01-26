# Availability NFRs

Terminology:

- RTO: Maximum time to restore service after disruption (target ≤ 2h).
- RPO: Maximum acceptable data loss interval (target ~0s via continuous replication; set ≤60s for verification).
- Maintenance Window: Predefined period for preventive or upgrade tasks that may reduce resilience or partially impair functionality.

Background:
FtRS aims for high availability (minimal interruption) with trajectory toward fault tolerance (zero interruption) by leveraging multi-AZ deployment in a single region and disciplined DR/BC planning.

Scope:

- Production environment only.
- Includes core application services, APIs, UI, messaging & persistence components.

Legend: Code | Requirement | Rationale | Verification | Tags

## NFR Table

| Code      | Requirement                                                                                     | Rationale                                   | Verification                                                   | Tags                                 |
| --------- | ----------------------------------------------------------------------------------------------- | ------------------------------------------- | -------------------------------------------------------------- | ------------------------------------ |
| AVAIL-001 | Achieve ≥99.90% monthly service availability via multi-AZ deployment in single region           | Meet user demand & SLA                      | Monitoring availability report; multi-AZ configuration audit          | availability, sla, multi-az          |
| AVAIL-002 | Scope disaster recovery scenarios at region level with documented DR plan                       | Ensure regional failure preparedness        | DR run book + region failure simulation results                 | availability, dr, region             |
| AVAIL-003 | Provide 24x7 (24\*7) operational availability excluding scheduled maintenance windows           | Continuous service access                   | Uptime monitoring covering all hours; no unexpected gaps       | availability, 24x7                   |
| AVAIL-004 | Limit total scheduled maintenance to ≤150 min/month and any single activity ≤60 min             | Minimise planned downtime impact            | Change calendar audit; duration metrics                        | availability, maintenance, limits    |
| AVAIL-005 | Maintain weekly scheduled maintenance window Tue 09:00-10:00 with minimal functional impairment | Predictable maintenance & user comms        | Calendar entry + user notice; functional smoke tests pass      | availability, maintenance, schedule  |
| AVAIL-006 | Meet Recovery Time Objective (RTO) ≤2h for Platinum classification                              | Rapid restoration reduces disruption        | DR exercise recovery timing ≤2h                                | availability, rto, dr                |
| AVAIL-007 | Meet Recovery Point Objective (RPO) ≤60s (target near-zero) via continuous replication          | Minimise permanent data loss                | Replication lag metrics show ≤60s; fail-over data delta test    | availability, rpo, replication       |
| AVAIL-008 | External & internal APIs align with core availability periods (24x7, maintenance constraints)   | Consistent external experience              | API uptime report matches core service uptime                  | availability, api                    |
| AVAIL-009 | Restrict access to UK registered IP addresses + auth for UI & APIs                              | First-line defence & jurisdiction alignment | Geo-IP access logs; blocked non-UK access test                 | availability, geo, security          |
| AVAIL-010 | Employ zero-downtime blue/green deployments for planned releases                                | Avoid user-facing deployment interruption   | Deployment audit shows traffic shift with zero failed requests | availability, deployment, blue-green |

## Verification Strategy Summary

- Synthetic & real user monitoring for availability percentage.
- DR simulation (region-level) for RTO timing.
- Replication lag dashboards & controlled fail-over for RPO measurement.
- Change management calendar parsing for maintenance duration totals.
- Blue/green deployment logs & canary health checks.
- Geo-IP filtering tests & audit logs.

## Follow-Up Items

- Define precise measurement methodology for availability (exclude approved maintenance?).
- Automate monthly maintenance minute aggregation & alert at 75% budget usage.
- Integrate replication lag alerting threshold (e.g. >45s sustained 5min).
- Publish public status page referencing AVAIL-001..AVAIL-010 metrics.
