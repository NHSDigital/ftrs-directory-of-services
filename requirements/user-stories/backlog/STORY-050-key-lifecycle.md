---
id: STORY-050
title: Managed cryptographic key lifecycle
nfr_refs:
  - SEC-013
type: security
status: draft
owner: security-team
summary: Implement generation, rotation, archival, deletion processes for all cryptographic keys under RBAC control.
---

## Description
Keys must be created securely, rotated per policy (e.g. annually or on compromise), archived when superseded and securely deleted when retired. Access restricted via least-privilege policies.

## Acceptance Criteria
- Rotation schedule documented & automated for all CMKs.
- Access audit shows only authorised principals using keys.
- Key archival procedure executed for one test key.
- Deletion process logs and confirms unrecoverability of retired test key.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| rotation_schedule_check | manual | Schedule present & tooling configured |
| key_access_audit | automated | No unauthorised principals |
| archival_procedure_test | manual | Archived state recorded |
| deletion_procedure_test | manual | Deletion confirmed; no access possible |

## Traceability
NFRs: SEC-013
