---
code: STORY-XXX
as_a: <role>
i_want: <capability>
so_that: <outcome>
business_value: <qual/quant justification>
nfr_refs: [SEC-001, PERF-001]
nfr_tags: [security, performance]
acceptance_criteria:
  - GIVEN <precondition> WHEN <action> THEN <observable outcome>
  - GIVEN <error path> WHEN <action> THEN <graceful degradation>
out_of_scope:
  - <explicit exclusions>
notes: |
  Context, decisions, links.
---

# Summary

Provide a concise explanation.

## Detail

Elaborate behaviour, edge cases, constraints.

## Deriving Acceptance Criteria from NFRs

For each referenced NFR:

- SEC-001: Include test verifying TLS enforced and HTTP downgraded requests rejected.
- PERF-001: Include latency assertion in performance test harness.

## INVEST Checklist

- Independent: Yes/No
- Negotiable: Items needing refinement
- Valuable: Stakeholder value described
- Estimable: Open questions listed
- Small: Target size <= sprint
- Testable: Acceptance criteria map clearly
