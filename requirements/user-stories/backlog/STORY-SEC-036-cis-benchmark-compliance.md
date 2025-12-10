---
story_id: STORY-SEC-036
title: ASVS & CIS benchmark automation reports pass thresholds
role: Security Engineer
goal: Deliver: ASVS & CIS benchmark automation reports pass thresholds
value: Automated ASVS and CIS benchmark scans meet pass thresholds; failures trigger remediation.
nfr_refs: [SEC-009]
status: draft
---

## Description

Implement and validate NFR `SEC-009` for domain `security`.

## Acceptance Criteria

- >= 95% controls passing; all high-severity findings remediated or exceptioned
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `SEC-009`
- Domain: security
- Control ID: `cis-benchmark-compliance`
- Measure: CIS benchmark automation reports meet pass thresholds for targeted services
- Threshold: >= 95% controls passing; all high-severity findings remediated or exceptioned
- Tooling: CIS benchmark tooling integrated in CI and periodic audits
- Cadence: CI per change + monthly full audit
- Environments: dev, int, ref, prod


## Traceability

- Domain registry: requirements/nfrs/security/nfrs.yaml
