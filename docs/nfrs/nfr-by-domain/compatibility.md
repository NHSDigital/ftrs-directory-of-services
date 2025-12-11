# FtRS NFR – Compatibility

This page is auto-generated; do not hand-edit.

## NFR Codes

| Code | Requirement | Explanation | Stories |
|------|-------------|-------------|---------|
| COMP-001 | Published OS/browser list matches warranted spec | Supported OS/browser list matches published specification. | STORY-COMP-001, STORY-COMP-004 |
| COMP-002 | MFA (CIS2) succeeds across supported platforms | Multi-factor authentication (CIS2) works across supported platforms. | STORY-COMP-002, STORY-COMP-005 |
| COMP-003 | ≥90% critical journeys test pass per platform | Critical user journeys pass across all supported platforms at target success rate. | STORY-COMP-003, STORY-COMP-006 |

## Controls

### COMP-001

Supported OS/browser list matches published specification.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [COMP-001](#comp-001) | published-supported-platforms | Published OS/browser list matches warranted spec | Supported platform list published and current | Documentation repo + review checklist | Quarterly | prod | read-only-viewer | draft | Sets clear compatibility expectations for users |

### COMP-002

Multi-factor authentication (CIS2) works across supported platforms.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [COMP-002](#comp-002) | mfa-platforms | MFA (CIS2) succeeds across supported platforms | MFA journeys pass across supported platforms | Cross-platform test suite + identity provider logs | Release cycle | int,ref,prod | crud-apis,read-only-viewer | draft | Ensures authentication compatibility |

### COMP-003

Critical user journeys pass across all supported platforms at target success rate.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [COMP-003](#comp-003) | journeys-pass-rate | ≥90% critical journeys test pass per platform | >= 90% pass rate for critical journeys on each supported platform | Cross-platform automated E2E tests | CI per build + release candidate validation | int,ref | read-only-viewer | draft | Protects user experience across platforms |
