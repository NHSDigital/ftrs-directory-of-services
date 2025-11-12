---
id: STORY-012
title: Enforce least-privilege network rules
nfr_refs:
  - SEC-007
type: security
status: draft
owner: platform-team
summary: Implement deny-by-default security groups / network ACLs with minimal allowed ports and sources.
---

## Description
Review and refactor all network rules to a principle of deny-by-default; allow only required protocol/port/source combinations for each component.

## Acceptance Criteria
- Inventory of existing rules baseline documented.
- Automated lint flags wide CIDR (0.0.0.0/0) except approved exceptions.
- Removal of unused ingress/egress rules confirmed.
- Negative test: blocked unauthorized port access attempt.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| sg_acl_inventory | automated | Complete current rule list |
| wide_cidr_lint | automated | No unapproved wide CIDRs |
| unused_rule_detection | automated | Unused rules identified & removed |
| unauthorized_port_attempt | automated | Connection denied & logged |

## Traceability
NFRs: SEC-007
