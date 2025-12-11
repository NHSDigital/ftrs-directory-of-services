# FtRS NFR – Accessibility

This page is auto-generated; do not hand-edit.

## NFR Codes

| Code | Requirement | Explanation | Stories |
|------|-------------|-------------|---------|
| ACC-001 | WCAG 2.2 AA scan & manual audit pass | Product passes WCAG 2.2 AA via automated and manual audits. | STORY-ACC-001 |
| ACC-002 | Automated scans run across critical pages & browsers | Automated scans run across critical pages and browser variants. | STORY-ACC-002 |
| ACC-003 | Manual accessibility test executed per release | Manual accessibility tests are executed for each release cycle. | STORY-ACC-003 |
| ACC-004 | Defects tracked with parity priority & SLA | Accessibility defects tracked with equal priority and defined SLAs. | STORY-ACC-004 |
| ACC-005 | Tooling operational in dev/int/reference envs | Accessibility tooling operates correctly in dev, int, and reference environments. | STORY-ACC-005 |
| ACC-006 | Assistive tech not blocked by headers/CSP | Assistive technologies are not blocked by headers or Content Security Policy (CSP). | STORY-ACC-006 |
| ACC-007 | Test dataset covers tables/forms/status messages | Test dataset covers common components: tables, forms, status messages. | STORY-ACC-007 |
| ACC-008 | CI accessibility stage completes <5min | CI accessibility scan stage completes quickly (under target time). | STORY-ACC-008 |
| ACC-009 | Keyboard tab order regression test passes | Keyboard-only navigation preserves logical tab order without traps. | STORY-ACC-003, STORY-ACC-009 |
| ACC-010 | Focus trap tests pass for modals/overlays | Focus handling works for modals and overlays without trapping user. | STORY-ACC-004, STORY-ACC-010 |
| ACC-011 | Screen reader ARIA role announcements verified | Screen reader announces ARIA roles and states correctly. | STORY-ACC-011 |
| ACC-012 | Accessibility results documented with feature tests | Accessibility results are documented alongside feature tests. | STORY-ACC-012 |
| ACC-013 | Central issue log maintained & current | Centralised accessibility issue log is maintained and current. | STORY-ACC-013 |
| ACC-014 | Accessibility champion/workgroup active | Active champion or workgroup drives accessibility practice. | STORY-ACC-014 |
| ACC-015 | Monthly accessibility report published | Monthly accessibility report is published for stakeholders. | STORY-ACC-005, STORY-ACC-015 |
| ACC-016 | Exception process documented & used | Exception process for accessibility deviations is documented. | STORY-ACC-016 |
| ACC-017 | Exception record contains required fields | Exception records include required fields (impact, mitigation, expiry). | STORY-ACC-017 |
| ACC-018 | Pre-commit checks complete <30s | Pre-commit accessibility checks finish within target duration. | STORY-ACC-018 |
| ACC-019 | CI accessibility stage completes <5min | CI accessibility stage completes within target time window. | STORY-ACC-019 |
| ACC-020 | Overnight full scan duration <2h | Overnight full scan finishes under defined maximum duration. | STORY-ACC-020 |
| ACC-021 | Accessibility regression triggers alert | Regression in accessibility triggers automated alert. | STORY-ACC-021 |
| ACC-022 | False positive ratio report shows improvement | False positive ratio is measured and trending toward improvement. | STORY-ACC-022 |

## Controls

### ACC-001

Product passes WCAG 2.2 AA via automated and manual audits.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [ACC-001](#acc-001) | wcag-aa-pass | WCAG 2.2 AA scan & manual audit pass | Automated AA scan passes; manual audit issues triaged and resolved | Accessibility scanner + manual audit checklist | Quarterly + pre-release | int,ref | read-only-viewer | draft | Ensures accessibility conformance for UI surfaces |

### ACC-002

Automated scans run across critical pages and browser variants.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [ACC-002](#acc-002) | automated-scans-coverage | Automated scans run across critical pages & browsers | Critical pages covered across supported browsers | CI accessibility suite + cross-browser runners | CI per build | int,ref | read-only-viewer | draft | Automated checks catch regressions early |

### ACC-003

Manual accessibility tests are executed for each release cycle.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [ACC-003](#acc-003) | manual-accessibility-test | Manual accessibility test executed per release | Release includes manual accessibility audit; issues triaged within 5 business days | Manual checklist + report | Per release | ref | read-only-viewer | draft | Ensures human validation beyond automation |

### ACC-004

Accessibility defects tracked with equal priority and defined SLAs.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [ACC-004](#acc-004) | accessibility-defect-sla | Defects tracked with parity priority & SLA | Accessibility defects use same priority/SLA scheme; monthly compliance report | Issue tracker + SLA report | Monthly | int,ref | read-only-viewer | draft | Enforces parity with functional defects |

### ACC-005

Accessibility tooling operates correctly in dev, int, and reference environments.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [ACC-005](#acc-005) | accessibility-tooling-operational | Tooling operational in dev/int/reference envs | CI scanners and browser runners functional in dev/int/ref | CI accessibility suite | CI per build | dev,int,ref | read-only-viewer | draft | Guarantees tooling readiness across envs |

### ACC-006

Assistive technologies are not blocked by headers or Content Security Policy (CSP).

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [ACC-006](#acc-006) | assistive-tech-headers-csp | Assistive tech not blocked by headers/CSP | Headers/CSP allow screen readers; tests pass for supported AT | AT test harness + response header checks | Pre-release | ref | read-only-viewer | draft | Prevents accidental blocking via security headers |

### ACC-007

Test dataset covers common components: tables, forms, status messages.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [ACC-007](#acc-007) | accessibility-test-dataset-coverage | Test dataset covers tables/forms/status messages | Dataset includes representative components; annual review | Dataset repo + checklist | Annual | int | read-only-viewer | draft | Ensures coverage of common interactive components |

### ACC-008

CI accessibility scan stage completes quickly (under target time).

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [ACC-008](#acc-008) | ci-accessibility-duration | CI accessibility stage completes <5min | CI accessibility job completes < 5 minutes | CI job timer | CI per build | int | read-only-viewer | draft | Keeps pipeline fast while ensuring checks |

### ACC-009

Keyboard-only navigation preserves logical tab order without traps.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [ACC-009](#acc-009) | keyboard-tab-order | Keyboard tab order regression test passes | Tab order matches expected flow; no focus loss | Automated tab order tests + manual verification | CI per build + pre-release | int,ref | read-only-viewer | draft | Supports keyboard-only navigation |

### ACC-010

Focus handling works for modals and overlays without trapping user.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [ACC-010](#acc-010) | focus-trap-tests | Focus trap tests pass for modals/overlays | No escape from focus trap; correct focus restoration | Automated focus tests + manual checks | CI per build + pre-release | int,ref | read-only-viewer | draft | Ensures accessible modal behaviour |

### ACC-011

Screen reader announces ARIA roles and states correctly.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [ACC-011](#acc-011) | aria-role-announcements | Screen reader ARIA role announcements verified | ARIA roles/states announced correctly across key flows | Screen reader scripts + audit | Quarterly | ref | read-only-viewer | draft | Validates semantic accessibility |

### ACC-012

Accessibility results are documented alongside feature tests.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [ACC-012](#acc-012) | accessibility-results-documented | Accessibility results documented with feature tests | Docs stored with tests; updated on change | Test reports + docs repo | CI per build | int | read-only-viewer | draft | Maintains traceable evidence |

### ACC-013

Centralised accessibility issue log is maintained and current.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [ACC-013](#acc-013) | accessibility-issue-log-current | Central issue log maintained & current | Log updated within 5 business days of finding; monthly review | Issue tracker + report | Monthly | int | read-only-viewer | draft | Ensures visibility of accessibility work |

### ACC-014

Active champion or workgroup drives accessibility practice.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [ACC-014](#acc-014) | accessibility-champion-active | Accessibility champion/workgroup active | Named champion/workgroup; quarterly minutes published | Meeting notes + tracker | Quarterly | int | read-only-viewer | draft | Sustains practice through leadership |

### ACC-015

Monthly accessibility report is published for stakeholders.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [ACC-015](#acc-015) | monthly-accessibility-report | Monthly accessibility report published | Report produced and published monthly with tracked actions | Reporting automation + issue tracker | Monthly | int,ref | read-only-viewer | draft | Maintains visibility and accountability |

### ACC-016

Exception process for accessibility deviations is documented.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [ACC-016](#acc-016) | accessibility-exception-process | Exception process documented & used | Exceptions recorded with impact, mitigation, expiry; reviewed monthly | Exception log | Monthly | int | read-only-viewer | draft | Manages deviations responsibly |

### ACC-017

Exception records include required fields (impact, mitigation, expiry).

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [ACC-017](#acc-017) | accessibility-exception-record-fields | Exception record contains required fields | 100% exceptions include fields; expiry monitored | Exception log + report | Monthly | int | read-only-viewer | draft | Ensures actionable exception management |

### ACC-018

Pre-commit accessibility checks finish within target duration.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [ACC-018](#acc-018) | precommit-accessibility-duration | Pre-commit checks complete <30s | Pre-commit accessibility checks complete < 30s | Pre-commit runner | On commit | dev | read-only-viewer | draft | Keeps local workflow efficient |

### ACC-019

CI accessibility stage completes within target time window.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [ACC-019](#acc-019) | ci-accessibility-duration-policy | CI accessibility stage completes <5min | CI job < 5 minutes; breaches trigger optimisation ticket | CI timer + policy | CI per build | int | read-only-viewer | draft | Enforces pipeline performance policy |

### ACC-020

Overnight full scan finishes under defined maximum duration.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [ACC-020](#acc-020) | overnight-scan-duration | Overnight full scan duration <2h | Full scan completes < 2 hours | Scan scheduler + timer | Nightly | int | read-only-viewer | draft | Keeps nightly checks practical |

### ACC-021

Regression in accessibility triggers automated alert.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [ACC-021](#acc-021) | accessibility-regression-alert | Accessibility regression triggers alert | Alert fires on score drop or new critical issue | Accessibility scanner + alerting | CI per build | int | read-only-viewer | draft | Fast feedback on regressions |

### ACC-022

False positive ratio is measured and trending toward improvement.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [ACC-022](#acc-022) | accessibility-false-positive-ratio | False positive ratio report shows improvement | False positive ratio decreasing quarter over quarter | Scanner report + trend analysis | Quarterly | int | read-only-viewer | draft | Improves signal quality of automated scans |
