# Copilot Jira Story Automation Instructions

These instructions define the workflow Copilot follows when a Jira ticket key (e.g. `FTRS-1607`) is provided for an existing repository story.

## Principles

- `story_id` in repository is immutable and remains the primary traceability anchor.
- Jira key augments; it never replaces `story_id` in matrix or registries.
- File rename to `<JIRA-KEY>-<kebab-summary>.md` is optional (discoverability), not mandatory.
- Acceptance criteria and `nfr_refs` must not change unless the user explicitly requests refinement.

## Standard Workflow

1. Add or update `jira_key: <KEY>` in story front matter (retain existing `story_id`).
2. OPTIONAL: Rename file to `<KEY>-<kebab-summary>.md` (content unchanged). Verify with `git diff` the change is purely a rename.
3. Add/Update traceability note: `Jira: <KEY>` if not present.
4. Update `requirements/nfrs/cross-references/nfr-matrix.md` row: append Jira key in parentheses after story ID, e.g. `STORY-OBS-006 (FTRS-1607)`.
5. If any registry (expectations YAML) was edited as part of the change, regenerate pages using the external NFR toolkit (see that repository for the equivalent command).
6. Remove legacy filename only after successful rename and verification.
7. Suggest (do not auto-run) a Conventional Commit using existing rules, e.g. `chore(observability): annotate STORY-OBS-006 with Jira FTRS-1607`.
8. Batch multiple Jira updates; perform regeneration once.
9. Summarise changes (renames, matrix update, regeneration) before offering commit command.

## Guardrails

- NEVER overwrite or replace `story_id` with Jira key.
- NEVER invent Jira keys; only use those explicitly provided by the user.
- ASK for clarification if proposed filename already exists.
- REJECT requests to delete the original story after sync (story file stays canonical source).

## Checklist (Post-Update)

- Front matter now includes `jira_key`.
- Matrix row updated with optional `(JIRA-KEY)` annotation.
- Pages regenerated (if registry touched).
- Old filename removed (if rename chosen).
- Commit suggestion prepared (not executed unless directed).

## Commit Examples

- `chore(observability): annotate STORY-OBS-006 with Jira FTRS-1607`
- `chore(security): annotate STORY-SEC-015 with Jira FTRS-1604`
- `chore(performance): add Jira key FTRS-1610 to FTRS-887`

## FAQ

**Q: Should matrix replace story IDs with Jira keys?** No. Keep `story_id` and optionally append the Jira key.
**Q: What if Jira criteria differ from repository?** Reconcile by updating the repository version; repository remains source of truth.
**Q: Can I rename without adding `jira_key`?** Discouraged. Add the key first to avoid ambiguity.

## Example Front Matter After Sync

```yaml
story_id: STORY-OBS-006
jira_key: FTRS-1607
as_a: Platform Observer
i_want: to detect repeated unauthorized API access attempts
so_that: we can alert and block malicious actors
status: refined
priority: P2
owner: observability-team
created: 2025-11-10
updated: 2025-11-26
nfr_refs: [OBS-033]
acceptance_criteria:
  - Unauthorized access events counted per credential per 5m window
  - Alert raised when attempts exceed threshold within window
  - Dashboard shows rolling 24h unauthorized attempt rate
  - False positives <2% validated against baseline sample
traceability_notes:
  - Jira FTRS-1607 mirrors criteria; anomaly script path scripts/observability/unauth_access_monitoring.py
```

## Future Automation Placeholder

Planned: script to scan stories lacking `jira_key` and emit a sync checklist. Until implemented, rely on manual review.

End of Jira Automation Instructions.

## Registry Synchronization (Expectations Updates)

When a story (new or refined, with or without Jira key) introduces new measurable constraints for an existing NFR control or performance operation:

1. Identify target registry file:

- Domain control: `requirements/nfrs/<domain>/expectations.yaml`
- Performance operation: `requirements/nfrs/performance/expectations.yaml`

1. Locate the matching `control_id` or `operation_id` block.
2. Update only the changed fields (`measure`, `threshold`, `tooling`, `cadence`, `rationale`) – preserve other keys.
3. Ensure consistent service naming (e.g. `dos-search`, not legacy names) and unit formatting.
4. Add rationale if tightening or adding thresholds (reference telemetry, benchmark, regulation, SLA, or user impact).
5. Batch multiple related edits, then regenerate pages once using the external NFR toolkit (see that repository for the equivalent command).
6. Suggest a Conventional Commit referencing both domain and story/Jira key, e.g.:

- `feat(security): Expand SEC-014 mTLS control with ITOC CA chain enforcement (FTRS-1600)`

1. Never delete existing controls without explicit instruction – changes are incremental.
2. If multiple stories refine same control in one session, aggregate rationale (list story IDs/Jira keys).

Validation Checklist After Edit:

- Control/operation exists and was not duplicated.
- Threshold format consistent (e.g. `p95 <= 850ms`).
- Rationale present for numeric changes.
- Regeneration script executed successfully.
- Proposed commit message prepared (not auto-run).

Guardrails:

- Reject attempts to invent new domain codes or operation IDs without prior reservation.
- Do not silently tighten thresholds – always surface rationale.
- If telemetry source absent, mark threshold as `draft` and note verification plan.

Example Commit:
`feat(performance): Add dm-record-transform p95 baseline (FTRS-887 FTRS-1612)`

End Registry Synchronization Section.
