---
story_id: STORY-SEC-039
title: IAM policy review confirms least privilege for system roles
role: Security Engineer
goal: Deliver: IAM policy review confirms least privilege for system roles
value: IAM roles and policies grant least privilege; periodic reviews confirm minimal access.
nfr_refs: [SEC-012]
status: draft
---

## Description

Implement and validate NFR `SEC-012` for domain `security`.

## Acceptance Criteria

- >= 95% policies compliant; no wildcard resource; explicit actions only
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `SEC-012`
- Domain: security
- Control ID: `iam-least-privilege`
- Measure: IAM policy review confirms least privilege for system roles
- Threshold: >= 95% policies compliant; no wildcard resource; explicit actions only
- Tooling: IAM Access Analyzer + policy linters
- Cadence: CI per change + quarterly audit
- Environments: dev, int, ref, prod

## Traceability

- Domain registry: requirements/nfrs/security/nfrs.yaml
