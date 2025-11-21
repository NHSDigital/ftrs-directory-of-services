# Copilot Instructions: Generating & Refining User Stories (Functional + NFR)

These instructions guide Tech Leads and Business Analysts using Copilot (and future MCP agents) to create or refine:
- Atomic Non-Functional Requirement (NFR) stories
- Functional product/user stories that reference NFR codes
- Registry entries (performance operations, domain controls)

Copilot must follow the guardrails below; humans remain accountable for thresholds, rationale, and governance sign‑off.

---
## 1. Scope & Goals
Copilot assistance should accelerate drafting while preserving:
- Traceability: Story ↔ NFR codes ↔ Registries ↔ Tests / Telemetry
- Consistency: Naming, front matter schema, commit messages
- Auditability: No invented codes; rationale present for target changes

Copilot outputs must never introduce unvalidated targets or fabricate IDs.

---
## 2. Artefact Overview
| Artefact | Location | Purpose |
|----------|----------|---------|
| NFR matrix | `requirements/nfrs/cross-references/nfr-matrix.md` | Canonical list of NFR codes & linked story IDs |
| NFR explanations | `requirements/nfrs/cross-references/nfr-explanations.yaml` | Plain-language code descriptions |
| Performance operations | `requirements/nfrs/performance/expectations.yaml` | Latency & throughput targets per API/flow |
| Domain controls | `requirements/nfrs/<domain>/expectations.yaml` | Measurable governance controls mapping to NFR codes |
| Stories (backlog) | `requirements/user-stories/backlog/` | Candidate / unstarted user stories |
| Story templates | `requirements/user-stories/templates/` | Boilerplate scaffolds for new stories |
| Simplified NFR page | `docs/developer-guides/nfr-all-simplified.md` | Generated consolidated view (run script to refresh) |

---
## 3. Story ID & File Naming Conventions
Two categories:
1. NFR-aligned implementation stories (still functional) – keep normal story pattern.
2. Functional feature stories.

Recommended patterns (do not rename existing historical IDs):
- General functional story: `STORY-<SERVICE>-NNN-<short-slug>.md` (e.g. `STORY-CRUD-021-update-dos-entry.md`)
- If a neutral system-wide story: `STORY-SYS-NNN-<slug>.md`
- Keep existing NFR implementation stories as generated: `STORY-PERF-001`, `STORY-SEC-003`, etc.

Numeric sequence per scope should be strictly monotonic (no reuse). Slug should be short, kebab‑case, value‑oriented.

---
## 4. Story Front Matter Schema
All stories use structured YAML front matter at top of the markdown file:
```
story_id: STORY-CRUD-021
as_a: <role>
i_want: <capability>
so_that: <business value>
business_value: <concise measurable impact>
status: draft|refined|in-progress|done
priority: P1|P2|P3
owner: <owner name or team>
created: YYYY-MM-DD
updated: YYYY-MM-DD
nfr_refs: [PERF-001, SEC-003]
related_operations: [gp-list, gp-nearby]
related_controls: [dependency-vuln-scan, tls-endpoints]
acceptance_criteria:
  - <Objective criterion>
  - <Edge / negative path>
metrics:
  - name: <metric-id>
    target: <value + unit>
    rationale: <why target>
risks:
  - <concise risk + mitigation>
traceability_notes:
  - <extra links or evidence placeholders>
```
Rules:
- `story_id` immutable once published.
- Update `updated:` whenever materially changing content.
- `nfr_refs` only list direct NFR codes impacted (no speculative additions).
- Each acceptance criterion must be objectively testable (binary pass/fail).

---
## 5. Acceptance Criteria Guidelines
Copilot should:
- Prefer bullet criteria; optionally Gherkin for complex flows.
- Include at least one negative / error handling case if applicable.
- Avoid subjective phrases ("fast", "easy", "intuitive"). Use measurable terms referencing operations or controls when relevant.
- Tie performance criteria to operation IDs (e.g. gp-list p95 ≤ 850ms in prod).

Bad: "System should be fast" → Replace with measurable target.

---
## 6. Linking NFR Codes
Copilot must verify each proposed NFR code exists in `nfr-matrix.md` before including it. If user signals intent to add a new code:
1. Reserve code manually first (human action).
2. Use placeholder `(placeholder)` in matrix until story created.
3. Only then may Copilot reference the new code.

Never invent codes; reject prompts that implicitly ask to create unreserved codes.

---
## 7. Performance Operations & Domain Controls (Context for Stories)
When story acceptance depends on latency / throughput or governance checks, surface these in criteria referencing:
- `operation_id` (performance) – e.g. gp-nearby p95 ≤ target.
- `control_id` (security, reliability, etc.) – e.g. `dependency-vuln-scan` passes with 0 critical CVEs.

If thresholds not yet accepted (status: draft), mark criterion as "subject to review" and prompt human validation.

---
## 8. Prompt Skeletons (For Users / Copilot)
| Scenario | Skeleton |
|----------|----------|
| New functional story | "Draft story for <role> needing <capability> to achieve <value>; propose 4 acceptance criteria and relevant NFR codes (list: <codes>)." |
| Refine latency criteria | "Given current gp-list p95=910ms and target 850ms, refine acceptance criteria ensuring progressive rollout and monitoring steps." |
| Add security control | "Suggest control entry for build-time dependency scanning referencing SEC-003 with measurable threshold & rationale." |
| Generate explanation | "Plain-language (≤40 words) explanation for NFR REL-005 emphasising user impact if unmet." |
| Threshold adjustment rationale | "Provide concise rationale for tightening gp-nearby p95 from 950ms to 900ms referencing user behavioural impact." |
| Negative path criteria | "Add one negative acceptance criterion for STORY-CRUD-021 handling invalid DoS entry update request (validation failure)." |
| Exception handling | "Draft exception rationale for control tls-endpoints due to legacy endpoint; include mitigation + review date." |

---
## 9. Guardrails Copilot Must Enforce
1. No invented IDs (story, NFR, operation, control).
2. Threshold proposals must include rationale (source: telemetry, benchmark, regulation, SLA).
3. Explanations ≤ 40 words; differentiate from acceptance anchor.
4. One outcome per acceptance criterion; no compound "and" requirements unless stepwise Gherkin used.
5. Risks include mitigation plan.
6. Changes to existing thresholds require human approval note (comment or commit message context).
7. Avoid speculative future metrics unless instrumentation exists or is planned (state plan if not yet live).

If guardrail breached, Copilot should respond: "Constraint issue: <reason>. Please supply missing validated inputs." and not produce content.

---
## 10. Validation Checklist (Pre-Commit)
| Check | Action |
|-------|--------|
| NFR codes valid | Cross-check matrix presence |
| Unique story ID | Ensure not previously used |
| Front matter complete | Mandatory keys present (see schema) |
| Acceptance measurable | All criteria objective |
| Threshold rationale | Present for any numeric target |
| Updated timestamp | Reflects latest edit |
| Links added | Matrix row updated with story ID |

---
## 11. Matrix & Registry Updates
After creating or refining a story:
1. Insert story ID into the relevant matrix NFR row (append, preserve ordering).
2. If adding new control/operation, ensure `nfr_code` or story `nfr_refs` remain consistent.
3. Run simplified page generator if registry changed: `python3 scripts/nfr/refresh_simplified_nfr_page.py`.

Copilot should remind user if matrix not yet updated.

---
## 12. Commit Message Guidance (Conventional Commits)
Follow existing commit rules from `.github/copilot-instructions.md`.
Examples:
- `feat(crud-apis): Add STORY-CRUD-021 DoS entry update story JIRA-1234`
- `docs(requirements): Add explanation for REL-005 JIRA-2345`
- `fix(performance): Tighten gp-nearby p95 target JIRA-3456`
- `refactor(requirements): Restructure story front matter for consistency JIRA-4567`

Always:
- Imperative mood; capitalise first word after colon.
- Include Jira ticket key.
- No trailing period.

---
## 13. Quality Bar for Copilot Output
Reject if any of:
- Vague criteria ("system responds quickly")
- Mixed concerns in one criterion (e.g. latency + security)
- Unjustified threshold changes
- Story duplicates existing one without clear delta
- Risk lacks mitigation or review cadence

Accept only when:
- Criteria are atomically testable
- IDs match registry/matrix
- Rationale ties to data or stakeholder value

---
## 14. Example Full Story (Condensed)
```
---
story_id: STORY-CRUD-021
as_a: Directory Editor
i_want: to update a DoS entry's opening hours
so_that: service consumers see accurate availability
business_value: Reduces patient misdirection and rework
status: draft
priority: P2
owner: dos-team
created: 2025-11-21
updated: 2025-11-21
nfr_refs: [PERF-001, SEC-003, REL-002]
related_operations: [dos-update]
related_controls: [dependency-vuln-scan]
acceptance_criteria:
  - Valid update with all required fields returns 200 and persists changes
  - Attempt with missing mandatory field returns 400 with structured error body
  - Update latency p95 for dos-update operation ≤ target in prod
  - Audit log entry created referencing story_id and user principal
metrics:
  - name: dos-update-p95
    target: 850ms
    rationale: Aligns with PERF-001 user perceived snappiness target
risks:
  - Incomplete validation may allow inconsistent state; mitigation: schema validation + contract tests
traceability_notes:
  - Will link evidence dashboard once operational metrics live
---
Additional narrative/context here.
```

---
## 15. Copilot Response Style
When asked to generate content:
- Provide only the requested section(s) (e.g. acceptance criteria list).
- Use canonical casing & formatting as shown.
- Offer a brief rationale paragraph ONLY if user request includes threshold changes or performance governance aspects.
- Suggest next governance action if gap detected (e.g. "Control not yet accepted; schedule review.").

---
## 16. Escalation & Exceptions
If a governance control cannot be met:
1. Story may carry interim exception criteria.
2. Registry control `status: exception` with rationale (cause; mitigation; review date).
3. Copilot may draft exception text but must label clearly and request human review.

---
## 17. Future Automation Hooks (Informational)
Copilot placeholders anticipating tooling:
- NFR code linter (validate `nfr_refs`)
- Story template CLI generator
- Threshold telemetry diff annotator

Until implemented, Copilot should not claim these checks occurred—only recommend them.

---
## 18. Minimal Prompt to Generate New Story
```
Generate a new functional story for Directory Editor to update DoS entry opening hours improving accuracy. Reference NFR codes PERF-001 (latency), REL-002 (consistency), SEC-003 (audit). Provide 4 acceptance criteria (one negative), metrics section (p95 target + rationale), risks, and front matter with today's date.
```

---
## 19. Final Reminders for Copilot
- Never silently add or alter registry thresholds.
- Always surface rationale for any numeric target.
- Prefer conservative initial values; optimisation stories can tighten later.
- Encourage evidence linkage (dashboards, scan reports) in traceability notes.

---
End of Copilot User Story Instructions.
\n+## 20. Manual Jira Synchronisation (Interim Process)\n+Jira API access is not yet available. All story handling is manual copy/paste. Keep repository stories present to enable AI-assisted implementation until automation lands.\n+\n+### Additional Front Matter Field\n+Add after `story_id:` line: `jira_key: <JIRA-1234>` once the Jira issue is created.\n+\n+### Extended Status Values\n+Acceptable `status:` values now: `draft|refined|in-progress|done|synced`. Use `synced` only after Jira key added and acceptance criteria stabilised.\n+\n+### Workflow Steps\n+1. Author or refine story in repo (status `draft`).\n+2. Copy entire front matter + body into Jira to create issue.\n+3. Obtain Jira issue key (e.g. `ABC-1234`).\n+4. Update story front matter: add `jira_key:` and set `updated:` date; optionally move status to `refined` if criteria improved.\n+5. Commit: `chore(story-sync): Add jira_key for STORY-CRUD-021 ABC-1234`.\n+6. (Optional) When delivery starts, change status to `in-progress`; on acceptance set to `done`.\n+7. If fully mirrored and stable, optionally mark `synced` (retain file; do NOT delete).\n+\n+### Matrix Handling\n+Matrix (`nfr-matrix.md`) continues to list local `story_id` values; do not replace them with Jira keys. The local ID remains traceability anchor for automation.\n+\n+### Deletion Policy\n+Do NOT delete story files after Jira creation. They are required for:\n+- AI-assisted implementation guidance\n+- Future automated sync tooling\n+- Batch governance / traceability analysis\n+\n+### Guardrails Specific to Jira Sync\n+- Never invent Jira keys; only add after actual issue creation.\n+- Do not change `story_id` to match Jira key; keep them distinct.\n+- If Jira acceptance criteria differ, reconcile by updating repo version (maintain single source of truth here).\n+\n+### Example Updated Front Matter\n+```\n+story_id: STORY-CRUD-021\n+jira_key: ABC-1234\n+as_a: Directory Editor\n+i_want: to update a DoS entry's opening hours\n+so_that: service consumers see accurate availability\n+business_value: Reduces patient misdirection and rework\n+status: synced\n+priority: P2\n+owner: dos-team\n+created: 2025-11-21\n+updated: 2025-11-21\n+nfr_refs: [PERF-001, SEC-003, REL-002]\n+related_operations: [dos-update]\n+related_controls: [dependency-vuln-scan]\n+acceptance_criteria:\n+  - Valid update with all required fields returns 200 and persists changes\n+  - Attempt with missing mandatory field returns 400 with structured error body\n+  - Update latency p95 for dos-update operation ≤ target in prod\n+  - Audit log entry created referencing story_id and user principal\n+metrics:\n+  - name: dos-update-p95\n+    target: 850ms\n+    rationale: Aligns with PERF-001 user perceived snappiness target\n+risks:\n+  - Incomplete validation may allow inconsistent state; mitigation: schema validation + contract tests\n+traceability_notes:\n+  - Jira ABC-1234 mirrors these criteria; future evidence dashboard link pending\n+```\n+\n+### Future Automation Placeholder\n+Planned: script to scan stories lacking `jira_key` and emit a sync checklist. Until then, rely on manual review.\n+\n+End Jira Sync Interim Section.\n*** End Patch
