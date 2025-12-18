# FtRS NFR – Availability

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Availability NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066471107/Availability)

## NFR Codes

| Code | Requirement | Explanation | Stories |
|------|-------------|-------------|---------|
| AVAIL-001 | Availability report shows ≥99.90% multi-AZ uptime | Multi-AZ deployment achieves target uptime (e.g., ≥99.90%). | (none) |
| AVAIL-002 | Region DR simulation meets plan objectives | Disaster recovery (DR) simulation meets documented objectives. | [FTRS-11](https://nhsd-jira.digital.nhs.uk/browse/FTRS-11) |
| AVAIL-003 | Uptime monitoring confirms 24x7 coverage | Continuous uptime monitoring covers 24x7 operations. | (none) |
| AVAIL-004 | Monthly maintenance minutes ≤150; single ≤60 | Maintenance windows stay within monthly and per-event minute limits. | (none) |
| AVAIL-005 | Tuesday window executed; smoke tests pass | Scheduled maintenance executes successfully with passing smoke tests afterward. | [FTRS-1004](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1004), [FTRS-1693](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1693) |
| AVAIL-006 | DR exercise restores service <2h | DR exercise restores service within target recovery time (< defined hours). | [FTRS-11](https://nhsd-jira.digital.nhs.uk/browse/FTRS-11), [FTRS-751](https://nhsd-jira.digital.nhs.uk/browse/FTRS-751) |
| AVAIL-007 | Replication lag ≤60s; fail-over data delta minimal | Data replication lag remains under target ensuring minimal failover delta. | (none) |
| AVAIL-008 | API uptime aligns with core service | API uptime aligns with overall service availability target. | (none) |
| AVAIL-009 | Non-UK access attempts blocked & logged | Access from non-approved geographic regions is blocked and logged. | (none) |
| AVAIL-010 | Blue/green deployment produces 0 failed requests | Blue/green deployments complete with zero failed user requests. | (none) |
