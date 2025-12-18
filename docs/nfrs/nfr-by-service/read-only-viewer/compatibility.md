# FtRS NFR – Service: Read-only Viewer – Domain: Compatibility

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Compatibility NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066471126/Compatibility)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Compatibility | [COMP-001](#comp-001) | Published OS/browser list matches warranted spec | Supported OS/browser list matches published specification. | (none) |
| Compatibility | [COMP-002](#comp-002) | MFA (CIS2) succeeds across supported platforms | Multi-factor authentication (CIS2) works across supported platforms. | (none) |
| Compatibility | [COMP-003](#comp-003) | ≥90% critical journeys test pass per platform | Critical user journeys pass across all supported platforms at target success rate. | (none) |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### COMP-001

Published OS/browser list matches warranted spec

See explanation: [COMP-001](../../explanations.md#comp-001)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| published-supported-platforms | Published OS/browser list matches warranted spec | Supported platform list published and current | Quarterly | prod | Read-only Viewer | draft | (none) | Sets clear compatibility expectations for users |

### COMP-002

MFA (CIS2) succeeds across supported platforms

See explanation: [COMP-002](../../explanations.md#comp-002)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| mfa-platforms | MFA (CIS2) succeeds across supported platforms | MFA journeys pass across supported platforms | Release cycle | int,ref,prod | Read-only Viewer | draft | (none) | Ensures authentication compatibility |

### COMP-003

≥90% critical journeys test pass per platform

See explanation: [COMP-003](../../explanations.md#comp-003)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| journeys-pass-rate | ≥90% critical journeys test pass per platform | >= 90% pass rate for critical journeys on each supported platform | CI per build + release candidate validation | int,ref | Read-only Viewer | draft | (none) | Protects user experience across platforms |
