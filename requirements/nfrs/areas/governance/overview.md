# Governance & Compliance NFRs Overview

## Background

Governance ensures structured decision making, accountability, and adherence to architectural, engineering, and operational policies. Compliance enforces alignment with statutory and regulatory obligations (e.g. UK GDPR, medical device scope assessment). Together they underpin safe, lawful, and well-managed delivery of FtRS.

## Scope & Assumptions

- Applies across all environments (pre-production & production) to catch issues early.
- NHS England Technical Review & Governance (TRG) implicitly includes Cyber Security oversight.
- Service Acceptance Criteria (SAC) are required prior to production transition.
- Medical Device Directive re-assessment is triggered if functional scope changes towards clinical decision support features.

## Domain Goals

| Goal                       | Description                                                                     |
| -------------------------- | ------------------------------------------------------------------------------- |
| Readiness Assurance        | Formal acceptance before go-live ensures operational preparedness.              |
| Architectural Integrity    | Independent reviews validate scalability, reliability & adherence to standards. |
| Regulatory Compliance      | Continuous alignment with data protection & scope regulations.                  |
| Stakeholder Accountability | Explicit approvals distribute ownership & risk management.                      |
| Transparent Traceability   | Signed artifacts & logs retained for audit and improvement cycles.              |

## Atomic Requirements

| Code    | Title                                               | Intent                                  | Verification                            |
| ------- | --------------------------------------------------- | --------------------------------------- | --------------------------------------- |
| GOV-001 | Pre-live acceptance by Service Management           | Confirm readiness for transition        | Signed acceptance checklist             |
| GOV-002 | Well-Architected review by Cloud Expert             | Validate cloud architecture quality     | Review report & action closure          |
| GOV-003 | Solution Architecture Framework assessment approved | Align with maturity criteria            | Approved assessment artifact            |
| GOV-004 | Engineering Red-lines compliance confirmed          | Enforce best-practice engineering       | Compliance checklist & sign-off         |
| GOV-005 | GDPR compliance sign-off                            | Lawful data handling assurance          | IG assessment & approval record         |
| GOV-006 | Medical Device out-of-scope confirmation            | Maintain regulatory clarity             | Formal scope statement & review log     |
| GOV-007 | FtRS Architects approval                            | Validate technical correctness          | Review minutes & sign-off               |
| GOV-008 | Cloud Expert deployment approval                    | Confirm implemented design fidelity     | Deployment checklist signed             |
| GOV-009 | Solution Assurance approval                         | Meet organisational assurance standards | Assurance ticket closure                |
| GOV-010 | Clinical Safety approval                            | Mitigate clinical safety risks          | Safety case & approval record           |
| GOV-011 | Information Governance approval                     | Uphold data governance & privacy        | IG approval ticket & evidences          |
| GOV-012 | TRG approval                                        | Adhere to technical standards           | TRG session notes & outcome             |
| GOV-013 | SIRO sign-off                                       | Senior accountability for info risk     | SIRO signed record                      |
| GOV-014 | Caldicott Principles Guardian approval                         | Ethical handling of confidential data   | Approval statement & minutes            |
| GOV-015 | DUEC Assurance Board acceptance                     | Satisfy domain-specific criteria        | Board decision log & conditions tracked |
| GOV-016 | Live Services Board go-live approval                | Authorise production operation          | Board approval record & action closure  |
| GOV-017 | ITOC approval                                       | Ensure oversight by ITOC                | ITOC decision log & sign-off            |
| GOV-018 | CSOC approval                                       | Ensure cyber security operations sign-off | CSOC onboarding / approval record     |

## Workflow

1. Initiate review calendar early in delivery cycle.
2. Produce architectural & compliance artifacts (diagrams, data flows, DPIA, risk logs).
3. Execute Well-Architected & solution framework assessments; track remediation actions to closure.
4. Collect stakeholder approvals sequentially or in parallel; log timestamps & versions.
5. Store all signed artifacts in version-controlled repository location.
6. Trigger re-assessment if scope change (e.g. feature possibly entering medical device classification).

## Metrics & Thresholds

| Metric                                              | Target                                        |
| --------------------------------------------------- | --------------------------------------------- |
| Outstanding remediation actions pre-go-live         | 0 critical; ≤5 minor with owner/date          |
| Approval artifact completeness                      | 100% required stakeholders signed             |
| Time from remediation action raised to closed       | ≤30 days for standard, expedited for critical |
| Re-assessment latency after scope change trigger    | ≤14 days                                      |
| Audit discoverability (time to locate any approval) | <2 minutes                                    |

## Verification Activities

- Periodic audit of approval artifacts & checklists.
- Remediation action tracker automated status reporting.
- GDPR compliance reassessment annually or on data model change.
- Medical device scope re-evaluation on feature classification change.

## Maturity

All GOV codes start at draft. Progress to review after first full cycle of approvals; approved after two consecutive releases with zero critical remediation actions outstanding.
