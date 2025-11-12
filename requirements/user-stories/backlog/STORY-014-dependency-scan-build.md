---
id: STORY-014
title: Automated dependency scanning each build
nfr_refs:
  - SEC-027
type: security
status: draft
owner: devsecops-team
summary: Integrate SCA tool to scan dependencies for vulnerabilities on every build.
---

## Description
Configure SCA (e.g. OWASP Dependency-Check or Snyk) in CI pipeline; fail build on high severity vulnerabilities lacking approved exceptions.

## Acceptance Criteria
- Scan job executes for all build pipelines.
- High severity vulnerability produces failed build.
- Exception workflow documented and referenced by ticket.
- Report artifacts archived for 12 months.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| build_scan_execution | automated | Job runs & outputs report |
| high_severity_fail_test | automated | Build blocked |
| exception_workflow_simulation | manual | Approved ticket allows pass |
| artifact_retention_check | automated | Reports present for period |

## Traceability
NFRs: SEC-027
