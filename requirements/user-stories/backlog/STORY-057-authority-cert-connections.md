---
id: STORY-057
title: Authority-issued certificates for remote connections
nfr_refs:
  - SEC-020
type: security
status: draft
owner: supplier-team
summary: Authenticate remote server/app connections using Authority-issued digital certificates.
---

## Description
Implement certificate-based authentication for remote connections, ensuring certificates are issued by Authority CA and rotated per policy.

## Acceptance Criteria
- Certificate inventory lists Authority-issued certs for remote connections.
- Non-Authority certificate handshake rejected.
- Rotation schedule documented and tested.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| cert_inventory_presence | manual | Inventory committed |
| non_authority_cert_attempt | automated | Handshake fails & logged |
| rotation_schedule_test | manual | Rotation executed successfully |

## Traceability
NFRs: SEC-020
