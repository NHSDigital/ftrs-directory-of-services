---
id: STORY-063
title: Block release on critical unresolved vulnerabilities
nfr_refs:
  - SEC-028
  - SEC-027
type: security
status: draft
owner: devsecops-team
summary: Integrate pen test & dependency scanning results into release gates; prevent deployment with critical open issues.
---

## Description
CI/CD pipeline must evaluate latest pen test findings and dependency scan results. Release fails if any critical severity vulnerability lacks an approved and documented exception.

## Acceptance Criteria
- Dependency scan runs each build; report artifact stored.
- Critical CVE causes pipeline stage failure without exception ticket.
- Pen test results ingested; unresolved critical findings fail release gate.
- Exception workflow documented and auditable.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| dependency_scan_cve_injection | automated | Build fails with clear message |
| pen_test_findings_gate | manual | Release blocked; log & notification sent |
| exception_ticket_test | manual | Approved exception allows pass |
| artifact_storage_verification | automated | Reports present & immutable |

## Traceability
NFRs: SEC-028, SEC-027
