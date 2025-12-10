---
story_id: STORY-SEC-035
title: Perimeter scan shows no broad whitelist & secure channels
role: Security Engineer
goal: Deliver: Perimeter scan shows no broad whitelist & secure channels
value: Perimeter scans show secure transport, no open broad whitelists, and hardened edge configuration.
nfr_refs: [SEC-008]
status: draft
---

## Description

Implement and validate NFR `SEC-008` for domain `security`.

## Acceptance Criteria

- No broad whitelists; only secure channels reported
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `SEC-008`
- Domain: security
- Control ID: `perimeter-scan`
- Measure: Perimeter scan shows no broad whitelist & secure channels
- Threshold: No broad whitelists; only secure channels reported
- Tooling: External perimeter scanner + config validation
- Cadence: Monthly + on change
- Environments: int, ref, prod


## Traceability

- Domain registry: requirements/nfrs/security/nfrs.yaml
