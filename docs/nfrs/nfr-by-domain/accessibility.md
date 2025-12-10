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
