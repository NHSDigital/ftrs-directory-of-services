---
id: STORY-001
title: Enforce approved cryptographic algorithms
nfr_refs:
  - SEC-001
type: security
status: draft
owner: security-team
summary: Ensure only NHSE approved algorithms (GPG v4.0 list) are used across all encryption contexts.
---

## Description
Audit and enforce cryptographic configurations for all services, storage, and network channels to guarantee only approved cipher suites, key sizes, and algorithms are employed.

## Acceptance Criteria
- Inventory of all cryptographic usages produced (services, storage, transport).
- Automated scan flags any non-approved cipher suite/key size.
- Remediation pipeline replaces non-compliant configs.
- Quarterly crypto compliance report stored.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| crypto_inventory_generation | automated | Complete list of usages |
| cipher_suite_scan | automated | No disallowed suites detected |
| key_size_validation | automated | All keys meet minimum sizes |
| quarterly_report_presence | manual | Report file committed |

## Traceability
NFRs: SEC-001
