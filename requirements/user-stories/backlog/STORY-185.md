---
id: STORY-185
title: Obtain full governance & assurance approvals for GP Search go-live
status: draft
type: functional
owner: gp-search-team
nfr_refs:
  - GOV-001
  - GOV-002
  - GOV-003
  - GOV-004
  - GOV-005
  - GOV-006
  - GOV-007
  - GOV-008
  - GOV-009
  - GOV-010
  - GOV-011
  - GOV-012
  - GOV-013
  - GOV-014
  - GOV-015
  - GOV-016
summary: As a programme lead I need all mandated approvals so that the service can legally and safely operate in production.
---

### Acceptance Criteria
1. Signed artifacts present for each governance code GOV-001..GOV-016.
2. Outstanding remediation actions (if any) tracked and closed before live date.
3. Live Services Board approval includes confirmation of prior approvals sequence.
4. Scope reassessment triggers documented if material change occurs (GOV-006).

### Test Notes
| Scenario | Tool | Data | Expected |
|----------|------|------|----------|
| Artifact presence | script | Repo paths | All approval docs found |
| Remediation closure | manual review | Action logs | All critical actions closed |
| Scope change | simulated change | Updated doc | Re-assessment record added |

### Traceability
Governance chain completeness for go-live.
