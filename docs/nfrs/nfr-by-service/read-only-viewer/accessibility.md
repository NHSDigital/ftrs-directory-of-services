# FtRS NFR – Service: Read-only Viewer – Domain: Accessibility

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Accessibility NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066471135/Accessibility)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Accessibility | [ACC-001](../../explanations.md#Explanations-ACC-001) | WCAG 2.2 AA scan & manual audit pass | Product passes WCAG 2.2 AA via automated and manual audits. | (none) |
| Accessibility | [ACC-002](../../explanations.md#Explanations-ACC-002) | Automated scans run across critical pages & browsers | Automated scans run across critical pages and browser variants. | (none) |
| Accessibility | [ACC-003](../../explanations.md#Explanations-ACC-003) | Manual accessibility test executed per release | Manual accessibility tests are executed for each release cycle. | (none) |
| Accessibility | [ACC-004](../../explanations.md#Explanations-ACC-004) | Defects tracked with parity priority & SLA | Accessibility defects tracked with equal priority and defined SLAs. | (none) |
| Accessibility | [ACC-005](../../explanations.md#Explanations-ACC-005) | Tooling operational in dev/int/reference envs | Accessibility tooling operates correctly in dev, int, and reference environments. | (none) |
| Accessibility | [ACC-006](../../explanations.md#Explanations-ACC-006) | Assistive tech not blocked by headers/CSP | Assistive technologies are not blocked by headers or Content Security Policy (CSP). | (none) |
| Accessibility | [ACC-007](../../explanations.md#Explanations-ACC-007) | Test dataset covers tables/forms/status messages | Test dataset covers common components: tables, forms, status messages. | (none) |
| Accessibility | [ACC-008](../../explanations.md#Explanations-ACC-008) | CI accessibility stage completes <5min | CI accessibility scan stage completes quickly (under target time). | (none) |
| Accessibility | [ACC-009](../../explanations.md#Explanations-ACC-009) | Keyboard tab order regression test passes | Keyboard-only navigation preserves logical tab order without traps. | (none) |
| Accessibility | [ACC-010](../../explanations.md#Explanations-ACC-010) | Focus trap tests pass for modals/overlays | Focus handling works for modals and overlays without trapping user. | (none) |
| Accessibility | [ACC-011](../../explanations.md#Explanations-ACC-011) | Screen reader ARIA role announcements verified | Screen reader announces ARIA roles and states correctly. | (none) |
| Accessibility | [ACC-012](../../explanations.md#Explanations-ACC-012) | Accessibility results documented with feature tests | Accessibility results are documented alongside feature tests. | (none) |
| Accessibility | [ACC-013](../../explanations.md#Explanations-ACC-013) | Central issue log maintained & current | Centralised accessibility issue log is maintained and current. | (none) |
| Accessibility | [ACC-014](../../explanations.md#Explanations-ACC-014) | Accessibility champion/workgroup active | Active champion or workgroup drives accessibility practice. | (none) |
| Accessibility | [ACC-015](../../explanations.md#Explanations-ACC-015) | Monthly accessibility report published | Monthly accessibility report is published for stakeholders. | (none) |
| Accessibility | [ACC-016](../../explanations.md#Explanations-ACC-016) | Exception process documented & used | Exception process for accessibility deviations is documented. | (none) |
| Accessibility | [ACC-017](../../explanations.md#Explanations-ACC-017) | Exception record contains required fields | Exception records include required fields (impact, mitigation, expiry). | (none) |
| Accessibility | [ACC-018](../../explanations.md#Explanations-ACC-018) | Pre-commit checks complete <30s | Pre-commit accessibility checks finish within target duration. | [FTRS-1778](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1778), [FTRS-898](https://nhsd-jira.digital.nhs.uk/browse/FTRS-898) |
| Accessibility | [ACC-019](../../explanations.md#Explanations-ACC-019) | CI accessibility stage completes <5min | CI accessibility stage completes within target time window. | (none) |
| Accessibility | [ACC-020](../../explanations.md#Explanations-ACC-020) | Overnight full scan duration <2h | Overnight full scan finishes under defined maximum duration. | (none) |
| Accessibility | [ACC-021](../../explanations.md#Explanations-ACC-021) | Accessibility regression triggers alert | Regression in accessibility triggers automated alert. | (none) |
| Accessibility | [ACC-022](../../explanations.md#Explanations-ACC-022) | False positive ratio report shows improvement | False positive ratio is measured and trending toward improvement. | (none) |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### ACC-001

WCAG 2.2 AA scan & manual audit pass

See explanation: [ACC-001](../../explanations.md#Explanations-ACC-001)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| wcag-aa-pass | WCAG 2.2 AA scan & manual audit pass | Automated AA scan passes; manual audit issues triaged and resolved | Quarterly + pre-release | int,ref | Read-only Viewer | draft | (none) | Ensures accessibility conformance for UI surfaces |

### ACC-002

Automated scans run across critical pages & browsers

See explanation: [ACC-002](../../explanations.md#Explanations-ACC-002)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| automated-scans-coverage | Automated scans run across critical pages & browsers | Critical pages covered across supported browsers | CI per build | int,ref | Read-only Viewer | draft | (none) | Automated checks catch regressions early |

### ACC-003

Manual accessibility test executed per release

See explanation: [ACC-003](../../explanations.md#Explanations-ACC-003)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| manual-accessibility-test | Manual accessibility test executed per release | Release includes manual accessibility audit; issues triaged within 5 business days | Per release | ref | Read-only Viewer | draft | (none) | Ensures human validation beyond automation |

### ACC-004

Defects tracked with parity priority & SLA

See explanation: [ACC-004](../../explanations.md#Explanations-ACC-004)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| accessibility-defect-sla | Defects tracked with parity priority & SLA | Accessibility defects use same priority/SLA scheme; monthly compliance report | Monthly | int,ref | Read-only Viewer | draft | (none) | Enforces parity with functional defects |

### ACC-005

Tooling operational in dev/int/reference envs

See explanation: [ACC-005](../../explanations.md#Explanations-ACC-005)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| accessibility-tooling-operational | Tooling operational in dev/int/reference envs | CI scanners and browser runners functional in dev/int/ref | CI per build | dev,int,ref | Read-only Viewer | draft | (none) | Guarantees tooling readiness across envs |

### ACC-006

Assistive tech not blocked by headers/CSP

See explanation: [ACC-006](../../explanations.md#Explanations-ACC-006)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| assistive-tech-headers-csp | Assistive tech not blocked by headers/CSP | Headers/CSP allow screen readers; tests pass for supported AT | Pre-release | ref | Read-only Viewer | draft | (none) | Prevents accidental blocking via security headers |

### ACC-007

Test dataset covers tables/forms/status messages

See explanation: [ACC-007](../../explanations.md#Explanations-ACC-007)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| accessibility-test-dataset-coverage | Test dataset covers tables/forms/status messages | Dataset includes representative components; annual review | Annual | int | Read-only Viewer | draft | (none) | Ensures coverage of common interactive components |

### ACC-008

CI accessibility stage completes <5min

See explanation: [ACC-008](../../explanations.md#Explanations-ACC-008)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| ci-accessibility-duration | CI accessibility stage completes <5min | CI accessibility job completes < 5 minutes | CI per build | int | Read-only Viewer | draft | (none) | Keeps pipeline fast while ensuring checks |

### ACC-009

Keyboard tab order regression test passes

See explanation: [ACC-009](../../explanations.md#Explanations-ACC-009)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| keyboard-tab-order | Keyboard tab order regression test passes | Tab order matches expected flow; no focus loss | CI per build + pre-release | int,ref | Read-only Viewer | draft | (none) | Supports keyboard-only navigation |

### ACC-010

Focus trap tests pass for modals/overlays

See explanation: [ACC-010](../../explanations.md#Explanations-ACC-010)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| focus-trap-tests | Focus trap tests pass for modals/overlays | No escape from focus trap; correct focus restoration | CI per build + pre-release | int,ref | Read-only Viewer | draft | (none) | Ensures accessible modal behaviour |

### ACC-011

Screen reader ARIA role announcements verified

See explanation: [ACC-011](../../explanations.md#Explanations-ACC-011)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| aria-role-announcements | Screen reader ARIA role announcements verified | ARIA roles/states announced correctly across key flows | Quarterly | ref | Read-only Viewer | draft | (none) | Validates semantic accessibility |

### ACC-012

Accessibility results documented with feature tests

See explanation: [ACC-012](../../explanations.md#Explanations-ACC-012)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| accessibility-results-documented | Accessibility results documented with feature tests | Docs stored with tests; updated on change | CI per build | int | Read-only Viewer | draft | (none) | Maintains traceable evidence |

### ACC-013

Central issue log maintained & current

See explanation: [ACC-013](../../explanations.md#Explanations-ACC-013)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| accessibility-issue-log-current | Central issue log maintained & current | Log updated within 5 business days of finding; monthly review | Monthly | int | Read-only Viewer | draft | (none) | Ensures visibility of accessibility work |

### ACC-014

Accessibility champion/workgroup active

See explanation: [ACC-014](../../explanations.md#Explanations-ACC-014)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| accessibility-champion-active | Accessibility champion/workgroup active | Named champion/workgroup; quarterly minutes published | Quarterly | int | Read-only Viewer | draft | (none) | Sustains practice through leadership |

### ACC-015

Monthly accessibility report published

See explanation: [ACC-015](../../explanations.md#Explanations-ACC-015)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| monthly-accessibility-report | Monthly accessibility report published | Report produced and published monthly with tracked actions | Monthly | int,ref | Read-only Viewer | draft | (none) | Maintains visibility and accountability |

### ACC-016

Exception process documented & used

See explanation: [ACC-016](../../explanations.md#Explanations-ACC-016)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| accessibility-exception-process | Exception process documented & used | Exceptions recorded with impact, mitigation, expiry; reviewed monthly | Monthly | int | Read-only Viewer | draft | (none) | Manages deviations responsibly |

### ACC-017

Exception record contains required fields

See explanation: [ACC-017](../../explanations.md#Explanations-ACC-017)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| accessibility-exception-record-fields | Exception record contains required fields | 100% exceptions include fields; expiry monitored | Monthly | int | Read-only Viewer | draft | (none) | Ensures actionable exception management |

### ACC-018

Pre-commit checks complete <30s

See explanation: [ACC-018](../../explanations.md#Explanations-ACC-018)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| precommit-accessibility-duration | Pre-commit checks complete <30s | Pre-commit accessibility checks complete < 30s | On commit | dev | Read-only Viewer | draft | [FTRS-1778](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1778), [FTRS-898](https://nhsd-jira.digital.nhs.uk/browse/FTRS-898) | Keeps local workflow efficient |

### ACC-019

CI accessibility stage completes <5min

See explanation: [ACC-019](../../explanations.md#Explanations-ACC-019)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| ci-accessibility-duration-policy | CI accessibility stage completes <5min | CI job < 5 minutes; breaches trigger optimisation ticket | CI per build | int | Read-only Viewer | draft | (none) | Enforces pipeline performance policy |

### ACC-020

Overnight full scan duration <2h

See explanation: [ACC-020](../../explanations.md#Explanations-ACC-020)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| overnight-scan-duration | Overnight full scan duration <2h | Full scan completes < 2 hours | Nightly | int | Read-only Viewer | draft | (none) | Keeps nightly checks practical |

### ACC-021

Accessibility regression triggers alert

See explanation: [ACC-021](../../explanations.md#Explanations-ACC-021)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| accessibility-regression-alert | Accessibility regression triggers alert | Alert fires on score drop or new critical issue | CI per build | int | Read-only Viewer | draft | (none) | Fast feedback on regressions |

### ACC-022

False positive ratio report shows improvement

See explanation: [ACC-022](../../explanations.md#Explanations-ACC-022)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| accessibility-false-positive-ratio | False positive ratio report shows improvement | False positive ratio decreasing quarter over quarter | Quarterly | int | Read-only Viewer | draft | (none) | Improves signal quality of automated scans |
