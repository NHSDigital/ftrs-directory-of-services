---
id: STORY-045
title: Secure inbound and outbound connectivity
nfr_refs:
  - SEC-008
type: security
status: draft
owner: platform-team
summary: Ensure all external connectivity uses authenticated encrypted channels with minimal exposure.
---

## Description
Audit all ingress/egress paths; enforce TLS/VPN/IPsec where applicable; remove broad subnet allowances; document approved exceptions.

## Acceptance Criteria
- Connectivity inventory listing all external links.
- No broad (0.0.0.0/0) allow rules except documented exceptions.
- TLS verified for all public endpoints.
- VPN/IPsec tunnels show active encryption and auth.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| connectivity_inventory | manual | Inventory committed |
| perimeter_rule_scan | automated | No unauthorized broad rules |
| tls_public_endpoints_scan | automated | 100% TLS compliance |
| vpn_ipsec_status_check | automated | All tunnels encrypted/authenticated |

## Traceability
NFRs: SEC-008
