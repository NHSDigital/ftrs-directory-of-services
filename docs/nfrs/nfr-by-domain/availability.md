# FtRS NFR – Availability

Source: requirements/nfrs/cross-references/nfr-matrix.md

This page is auto-generated; do not hand-edit.

## NFR Codes

| Code | Requirement | Explanation | Stories |
|------|-------------|-------------|---------|
| AVAIL-001 | Availability report shows ≥99.90% multi-AZ uptime | Multi-AZ deployment achieves target uptime (e.g., ≥99.90%). | STORY-AVAIL-001 |
| AVAIL-002 | Region DR simulation meets plan objectives | Disaster recovery (DR) simulation meets documented objectives. | STORY-AVAIL-002 |
| AVAIL-003 | Uptime monitoring confirms 24x7 coverage | Continuous uptime monitoring covers 24x7 operations. | STORY-AVAIL-003 |
| AVAIL-004 | Monthly maintenance minutes ≤150; single ≤60 | Maintenance windows stay within monthly and per-event minute limits. | STORY-AVAIL-004 |
| AVAIL-005 | Tuesday window executed; smoke tests pass | Scheduled maintenance executes successfully with passing smoke tests afterward. | STORY-AVAIL-006 |
| AVAIL-006 | DR exercise restores service <2h | DR exercise restores service within target recovery time (< defined hours). | STORY-AVAIL-007 |
| AVAIL-007 | Replication lag ≤60s; fail-over data delta minimal | Data replication lag remains under target ensuring minimal failover delta. | STORY-AVAIL-008 |
| AVAIL-008 | API uptime aligns with core service | API uptime aligns with overall service availability target. | STORY-AVAIL-009 |
| AVAIL-009 | Non-UK access attempts blocked & logged | Access from non-approved geographic regions is blocked and logged. | STORY-AVAIL-010 |
| AVAIL-010 | Blue/green deployment produces 0 failed requests | Blue/green deployments complete with zero failed user requests. | STORY-AVAIL-005, STORY-AVAIL-011 |

