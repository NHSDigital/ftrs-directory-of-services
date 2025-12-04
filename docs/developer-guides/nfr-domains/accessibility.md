# FtRS NFR – Accessibility

Source: requirements/nfrs/cross-references/nfr-matrix.md

This page is auto-generated; do not hand-edit.

## NFR Codes

| Code | Requirement | Explanation | Stories |
|------|-------------|-------------|---------|
| ACC-001 | WCAG 2.2 AA scan & manual audit pass | Product passes WCAG 2.2 AA via automated and manual audits. | STORY-ACC-001 |
| ACC-002 | Automated scans run across critical pages & browsers | Automated scans run across critical pages and browser variants. | STORY-ACC-002 |
| ACC-003 | Manual accessibility test executed per release | Manual accessibility tests are executed for each release cycle. | STORY-ACC-003 |
| ACC-004 | Defects tracked with parity priority & SLA | Accessibility defects tracked with equal priority and defined SLAs. | STORY-ACC-004 |
| ACC-005 | Tooling operational in dev/int/reference envs | Accessibility tooling operates correctly in dev, int, and reference environments. | STORY-ACC-005 |
| ACC-006 | Assistive tech not blocked by headers/CSP | Assistive technologies are not blocked by headers or Content Security Policy (CSP). | (none) |
| ACC-007 | Test dataset covers tables/forms/status messages | Test dataset covers common components: tables, forms, status messages. | (none) |
| ACC-008 | CI accessibility stage completes <5min | CI accessibility scan stage completes quickly (under target time). | (none) |
| ACC-009 | Keyboard tab order regression test passes | Keyboard-only navigation preserves logical tab order without traps. | (none) |
| ACC-010 | Focus trap tests pass for modals/overlays | Focus handling works for modals and overlays without trapping user. | (none) |
| ACC-011 | Screen reader ARIA role announcements verified | Screen reader announces ARIA roles and states correctly. | (none) |
| ACC-012 | Accessibility results documented with feature tests | Accessibility results are documented alongside feature tests. | (none) |
| ACC-013 | Central issue log maintained & current | Centralised accessibility issue log is maintained and current. | (none) |
| ACC-014 | Accessibility champion/working group active | Active champion or working group drives accessibility practice. | (none) |
| ACC-015 | Monthly accessibility report published | Monthly accessibility report is published for stakeholders. | (none) |
| ACC-016 | Exception process documented & used | Exception process for accessibility deviations is documented. | (none) |
| ACC-017 | Exception record contains required fields | Exception records include required fields (impact, mitigation, expiry). | (none) |
| ACC-018 | Pre-commit checks complete <30s | Pre-commit accessibility checks finish within target duration. | (none) |
| ACC-019 | CI accessibility stage completes <5min | CI accessibility stage completes within target time window. | (none) |
| ACC-020 | Overnight full scan duration <2h | Overnight full scan finishes under defined maximum duration. | (none) |
| ACC-021 | Accessibility regression triggers alert | Regression in accessibility triggers automated alert. | (none) |
| ACC-022 | False positive ratio report shows improvement | False positive ratio is measured and trending toward improvement. | (none) |

## Controls

### ACC-001

Product passes WCAG 2.2 AA via automated and manual audits.
| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| wcag-aa-pass | WCAG 2.2 AA scan & manual audit pass | Automated AA scan passes; manual audit issues prioritized and resolved | Accessibility scanner + manual audit checklist | Quarterly + pre-release | int,ref | read-only-viewer | draft | Ensures accessibility conformance for UI surfaces |

### ACC-002

Automated scans run across critical pages and browser variants.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| automated-scans-coverage | Automated scans run across critical pages & browsers | Critical pages covered across supported browsers | CI accessibility suite + cross-browser runners | CI per build | int,ref | read-only-viewer | draft | Automated checks catch regressions early |

### ACC-009

Keyboard-only navigation preserves logical tab order without traps.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| keyboard-tab-order | Keyboard tab order regression test passes | Tab order matches expected flow; no focus loss | Automated tab order tests + manual verification | CI per build + pre-release | int,ref | read-only-viewer | draft | Supports keyboard-only navigation |

### ACC-010

Focus handling works for modals and overlays without trapping user.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| focus-trap-tests | Focus trap tests pass for modals/overlays | No escape from focus trap; correct focus restoration | Automated focus tests + manual checks | CI per build + pre-release | int,ref | read-only-viewer | draft | Ensures accessible modal behaviour |

### ACC-015

Monthly accessibility report is published for stakeholders.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| monthly-accessibility-report | Monthly accessibility report published | Report produced and published monthly with tracked actions | Reporting automation + issue tracker | Monthly | int,ref | read-only-viewer | draft | Maintains visibility and accountability |
