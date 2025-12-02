# Accessibility NFRs Overview

## Summary

Accessibility ensures all users — including those with physical, cognitive, or situational impairments — can use FtRS services effectively. We must meet legal obligations (Public Sector Bodies Accessibility Regulations 2018, Equality Act 2010) and adopt inclusive design practices by default.

## Scope & Assumptions

- Applies to all user-facing components: public/internal web apps, documentation portals, onboarding/self-service, feedback/support forms.
- Internal tools still require reasonable accessibility even if not strictly in public scope.
- Path-to-live environments (dev, integration, reference, prod) support accessibility testing to catch regressions early.
- Assistive technologies considered: screen readers (JAWS, NVDA, VoiceOver), keyboard-only navigation, zoom/text resizing, high-contrast modes.

## Domain Goals

| Goal                   | Description                                                          |
| ---------------------- | -------------------------------------------------------------------- |
| Legal Compliance       | Achieve and maintain WCAG 2.2 Level AA across UIs.                   |
| Early Detection        | Integrate automated scans & regression tests into pipeline stages.   |
| Inclusive Data         | Provide representative test data enabling full a11y evaluations.     |
| Transparent Governance | Track issues, exceptions & remediation with clear reporting.         |
| Efficient Tooling      | Ensure a11y automation performance doesn't erode developer velocity. |

## Atomic Requirements

| Code    | Title                                                           | Intent                                               | Verification                                    |
| ------- | --------------------------------------------------------------- | ---------------------------------------------------- | ----------------------------------------------- |
| ACC-001 | WCAG 2.2 Level AA compliance for all web UIs                    | Ensure inclusive & legally compliant user experience | Automated scan reports & manual audit checklist |
| ACC-002 | Automated accessibility scans on critical pages across browsers | Detect common accessibility issues early             | CI scan artifacts (axe/pa11y/lighthouse)        |
| ACC-003 | Manual accessibility test per feature or major UI release       | Catch issues beyond automated tooling scope          | Test session report & defect tickets            |
| ACC-004 | Accessibility defects tracked with parity                       | Prevent neglect of critical accessibility issues     | Defect tracker priority & SLA comparison        |
| ACC-005 | Tooling available in dev/integration/reference                  | Enable early accessibility validation                | Tool execution logs                             |
| ACC-006 | Assistive tech not blocked by headers/CSP                       | Maintain accessibility features functionality        | CSP/header scan & AT tests                      |
| ACC-007 | Representative dummy test data patterns                         | Valid assessment across UI patterns                  | Dataset review & coverage checklist             |
| ACC-008 | CI pipeline accessibility scan step                             | Prevent regressions entering main                    | CI job presence & status                        |
| ACC-009 | Keyboard tab order regression tests                             | Ensure logical navigation sequence                   | Automated traversal results                     |
| ACC-010 | Focus trap regression tests                                     | Prevent user lock-in within components               | Modal focus simulation tests                    |
| ACC-011 | ARIA role announcements verified                                | Provide semantic context to AT                       | Screen reader announcement logs                 |
| ACC-012 | Accessibility results documented                                | Maintain transparency & audit trail                  | Repo artifacts presence                         |
| ACC-013 | Central accessibility issue log                                 | Track defects & remediation progress                 | Log review & update cadence                     |
| ACC-014 | Champion/workgroup oversight                                    | Provide governance & improvement                     | Meeting notes & role assignment                 |
| ACC-015 | Monthly accessibility reporting                                 | Stakeholder visibility & risk management             | Report artifact & distribution                  |
| ACC-016 | Documented exception process                                    | Controlled handling of unavoidable gaps              | Exception records & approvals                   |
| ACC-017 | Exception record completeness                                   | Minimise impact of exceptions                        | Template completeness audit                     |
| ACC-018 | Pre-commit checks <30s                                          | Preserve developer velocity                          | Hook timing benchmark                           |
| ACC-019 | CI accessibility stage <5min                                    | Efficient pipeline performance                       | Job duration metrics                            |
| ACC-020 | Overnight full scan <2h                                         | Timely comprehensive coverage                        | Duration logs                                   |
| ACC-021 | Monitoring & alert integration                                  | Prompt notification of regressions                   | Alert firing on regression                      |
| ACC-022 | False positive ratio minimized                                  | Improve signal quality & reduce noise                | Periodic FP ratio report                        |

## Workflow

1. Define critical pages & map to scan configuration.
2. Run automated scans in CI (quick) and nightly (full).
3. Perform manual audits per major UI change; log defects with parity to functional.
4. Maintain keyboard/focus/ARIA regression test suite.
5. Produce monthly report; update issue log & exceptions.
6. Monitor performance timings & tune tooling to meet execution SLAs.

## Metrics & Thresholds

| Metric                                     | Target                              |
| ------------------------------------------ | ----------------------------------- |
| WCAG violations (AA)                       | 0 blocking issues before release    |
| Pre-commit scan duration                   | <30s                                |
| CI scan duration                           | <5min                               |
| Overnight full scan                        | <2h                                 |
| False positive ratio (FP / total findings) | <10% (improve over time)            |
| Keyboard traversal success                 | 100% interactive elements reachable |
| Focus trap escape success                  | 100% modals/overlays escapable      |

## Exception Handling

Exceptions require: justification, alternative access, mitigation plan, review schedule & approvals (product, accessibility, compliance). Tracked centrally and included in monthly reporting until resolved.

## Tooling Stack (Examples)

axe-core, Pa11y, Lighthouse CI, eslint-plugin-jsx-a11y, Storybook A11y, BrowserStack, Skynet, WAVE, Colour Contrast Analyser, Accessibility Insights.

## Governance

Accessibility champion/workgroup meets monthly; reviews metrics, issue backlog, and exception statuses; updates risk register.

## Maturity

All ACC codes draft; advance to review after initial implementation & two consecutive compliant reports; approve following successful external audit.
