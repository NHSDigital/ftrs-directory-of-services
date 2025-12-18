# FtRS NFR – Service: ODS ETL – Domain: Interoperability

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Interoperability NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066471146/Interoperability)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Interoperability | [INT-008](#int-008) | Reference data sync latency ≤24h | Reference data synchronises within defined latency (e.g., ≤24h). | (none) |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### INT-008

Reference data sync latency ≤24h

See explanation: [INT-008](../../explanations.md#int-008)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| reference-data-sync-latency | Reference data sync latency ≤24h | Sync completes within 24 hours | Daily | prod | ODS ETL | draft | (none) | Timely reference data ensures correct behaviour |
