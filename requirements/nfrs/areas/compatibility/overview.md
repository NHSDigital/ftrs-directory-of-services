# Compatibility NFRs Overview

## Background

Compatibility assesses how well FtRS interacts with other applications, processes, and user platforms (OS, browsers) without introducing conflicts that degrade functionality or experience. It ensures predictable behaviour across the warranted environment and sustains secure access via CIS2 MFA.

## Scope & Assumptions

- Applies to Production environment (direct user interaction).
- Focus on ongoing operation (not initial deployment only).
- CIS2 provides MFA; FtRS must remain compatible with NHS Spine Warrantied Environment specification (OS/browser list).

## Domain Goals

| Goal                      | Description                                                                                          |
| ------------------------- | ---------------------------------------------------------------------------------------------------- |
| Platform Predictability   | Users know supported OS & browser combinations and receive a consistent experience.                  |
| Secure Access Consistency | MFA/login flows work uniformly across supported platforms with negligible platform-induced failures. |
| Early Breakage Detection  | Automated regression tests catch platform-specific UI failures before release.                       |

## Atomic Requirements

| Code     | Title                                                                | Intent                                                    | Verification                                       |
| -------- | -------------------------------------------------------------------- | --------------------------------------------------------- | -------------------------------------------------- |
| COMP-001 | Supported OS & browser matrix aligns with NHS Spine Warrantied spec  | Ensure predictable end-user platform experience           | Published compatibility doc & test report coverage |
| COMP-002 | MFA (CIS2) login flows function across all supported platforms       | Maintain secure access without platform-specific failures | Cross-platform auth test pass rate ≥99.9%          |
| COMP-003 | Regression tests cover ≥90% critical journeys per supported platform | Detect platform-specific breakage early                   | Test coverage report & failing journey alerts      |

## Traceability Workflow

1. Maintain compatibility matrix document (versioned) listing OS/browser combos.
2. Map each critical user journey to automated UI test scenarios per platform.
3. Cross-platform CIS2 MFA test executed each build; failure blocks release.
4. Coverage tooling produces per-platform journey pass %; alert <90%.
5. Matrix & test reports archived for audit.

## Metrics & Thresholds

| Metric                                           | Target                                         |
| ------------------------------------------------ | ---------------------------------------------- |
| Auth pass rate per platform                      | ≥99.9%                                         |
| Critical journey automated coverage per platform | ≥90%                                           |
| Unsupported platform access error clarity        | User receives guidance message (non-technical) |

## Verification Activities

- Scheduled compatibility test suite run (CI pipeline).
- Periodic review of NHS Spine Warrantied Environment spec updates.
- Authentication flow audit when CIS2 changes.
- Release gate enforcing thresholds.

## Maturity

All COMP codes currently in draft pending wider review. Transition to `review` after initial test suite stabilises; `approved` after two release cycles meeting thresholds.
