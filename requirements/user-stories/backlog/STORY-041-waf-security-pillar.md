---
id: STORY-041
title: Apply Well-Architected Security Pillar Practices
nfr_refs:
  - SEC-002
  - SEC-009
type: security
status: draft
owner: architecture-team
summary: Embed AWS/GCP Well-Architected security pillar and OWASP ASVS controls into design & delivery lifecycle.
---

## Description
Formalise adoption of cloud Well-Architected Framework security pillar recommendations alongside OWASP ASVS L1+L2 controls. Maintain living checklist, reviewed each release and quarterly.

## Acceptance Criteria
- Design review checklist created referencing SECURITY pillar sections.
- Each service maps to relevant ASVS controls (documented matrix).
- Quarterly gap analysis produces remediation actions for any non-conformant control.
- CIS benchmark scan integrated in CI with report artifact.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| design_checklist_presence | manual | Checklist file committed |
| asvs_mapping_validation | automated | All endpoints mapped; no orphan controls |
| cis_benchmark_scan | automated | Report stored; high findings < threshold |
| quarterly_gap_analysis | manual | Actions logged & tracked |

## Traceability
NFRs: SEC-002, SEC-009
