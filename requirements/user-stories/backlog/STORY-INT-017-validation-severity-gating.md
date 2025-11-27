---
story_id: STORY-INT-017
title: Validation severity gating coverage and behavior assertions
role: Interoperability Engineer
goal: Ensure fatal/error halt; warnings continue
value: Predictable pipeline control flow
nfr_refs: [INT-017]
status: draft
---

## Acceptance Criteria
1. Fixtures include fatal, error, warning, information cases.
2. `should_continue` halts on fatal; `is_valid` reflects non-error states.
3. Coverage ≥90% on validator modules.
