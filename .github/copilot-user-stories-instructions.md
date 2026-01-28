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
- auditability: No invented codes; rationale present for target changes

Copilot outputs must never introduce not validated targets or fabricate IDs.

---

## 2. Artefact Overview

| Artefact               | Location                                                   | Purpose                                             |
| ---------------------- | ---------------------------------------------------------- | --------------------------------------------------- |
| NFR YAML (canonical)   | `requirements/nfrs/<domain>/nfrs.yaml`                     | Canonical list of NFR codes & linked story IDs      |
| NFR explanations       | `requirements/nfrs/cross-references/nfr-explanations.yaml` | Plain-language code descriptions                    |
| Performance operations | `requirements/nfrs/performance/expectations.yaml`          | Latency & throughput targets per API/flow           |
| Domain controls        | `requirements/nfrs/<domain>/expectations.yaml`             | Measurable governance controls mapping to NFR codes |
| Stories (backlog)      | `requirements/user-stories/backlog/`                       | Candidate / unstarted user stories                  |
| Story templates        | `requirements/user-stories/templates/`                     | Boilerplate scaffolds for new stories               |
| Simplified NFR page    | `docs/developer-guides/nfr-all-simplified.md`              | Generated consolidated view (run script to refresh) |

---

## 3. Story ID & File Naming Conventions

Two categories:

1. NFR-aligned implementation stories (still functional) – keep normal story pattern.
2. Functional feature stories.

Recommended patterns (do not rename existing historical IDs):

- General functional story: `STORY-<SERVICE>-NNN-<short-slug>.md` (e.g. `STORY-CRUD-021-update-dos-entry.md`)
- If a neutral system-wide story: `STORY-SYS-NNN-<slug>.md`
- Keep existing NFR implementation stories as generated: `FTRS-887`, `STORY-SEC-003`, etc.

Numeric sequence per scope should be strictly monotonic (no reuse). Slug should be short, kebab‑case, value‑oriented.

---

## 4. Story Front Matter Schema

All stories use structured YAML front matter at top of the markdown file:

```yaml
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

Copilot must verify each proposed NFR code exists in the domain `nfrs.yaml` before including it. If user signals intent to add a new code:

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

| Scenario                       | Skeleton                                                                                                                                |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| New functional story           | "Draft story for <role> needing <capability> to achieve <value>; propose 4 acceptance criteria and relevant NFR codes (list: <codes>)." |
| Refine latency criteria        | "Given current gp-list p95=910ms and target 850ms, refine acceptance criteria ensuring progressive deployment and monitoring steps."       |
| Add security control           | "Suggest control entry for build-time dependency scanning referencing SEC-003 with measurable threshold & rationale."                   |
| Generate explanation           | "Plain-language (≤40 words) explanation for NFR REL-005 emphasising user impact if unmet."                                              |
| Threshold adjustment rationale | "Provide concise rationale for tightening gp-nearby p95 from 950ms to 900ms referencing user behavioural impact."                       |
| Negative path criteria         | "Add one negative acceptance criterion for STORY-CRUD-021 handling invalid DoS entry update request (validation failure)."              |
| Exception handling             | "Draft exception rationale for control tls-endpoints due to legacy endpoint; include mitigation + review date."                         |

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

| Check                 | Action                              |
| --------------------- | ----------------------------------- |
| NFR codes valid       | Cross-check matrix presence         |
| Unique story ID       | Ensure not previously used          |
| Front matter complete | Mandatory keys present (see schema) |
| Acceptance measurable | All criteria objective              |
| Threshold rationale   | Present for any numeric target      |
| Updated timestamp     | Reflects latest edit                |
| Links added           | Matrix row updated with story ID    |

---

## 11. Matrix & Registry Updates

After creating or refining a story:

1. Insert story ID into the relevant matrix NFR row (append, preserve ordering).
2. If adding new control/operation, ensure `nfr_code` or story `nfr_refs` remain consistent.
3. Run the simplified page generator in the external NFR toolkit if the registry changed (see that repository for the exact command).

Copilot should remind user if matrix not yet updated.

## 11a. Jira Ticket Creation & Update (FtRS)

Copilot must not call Jira directly; instead it should guide users to the
existing helper scripts and keep YAML/markdown in sync.

### 11a.1 Jira configuration

All Jira helpers share the same configuration pattern (also used by
`fetch_jira_stories.py`). Environment variables (all optional, with
defaults):

- `JIRA_BASE_URL` – default `https://nhsd-jira.digital.nhs.uk`
- `JIRA_AUTH` – `basic` or `bearer` (default `basic`)
- `JIRA_USER` – Jira username (for `basic`)
- `JIRA_TOKEN` – Jira password / PAT (required)

Helpers now live in the central Jira tooling repository rather than this repo:

- `create_issue.py` – create issues and export to
  `requirements/user-stories/backlog/jira/KEY.md`
- `update_issue.py` – update summary, type, description, and Epic link

Always assume project key `FTRS` unless the user explicitly asks
otherwise.

### 11a.2 Naming conventions for NFR Jira tickets

For NFR-related Jira issues (SEC-xxx, PERF-xxx, etc.):

- Summary format: `NFR - <CODE> - <description>`
  - Example: `NFR - SEC-004 - Storage services show encryption enabled`
- Issue type: `Task` (unless the user specifies a different type)
- Priority: `Medium` by default (unless specified otherwise)
- Project: `FTRS`
- Epic: link to the epic "Search by ODS code Beta NFR Testing" for
  private-beta NFR work.

`create_issue.py` has a dedicated `--nfr-code` flag which ensures the
summary prefix is applied automatically.

### 11a.3 Description files

Each NFR Jira ticket should use a dedicated description file under:

- `requirements/user-stories/jira/<lowercase-code>-description.txt` or
  `.html`

Examples:

- `requirements/user-stories/jira/sec-004-description.txt`
- `requirements/user-stories/jira/sec-031-description.txt`

Guidance for descriptions:

- 3–5 short paragraphs.
- Plain text is preferred; HTML is allowed when explicitly requested.
- Explain what must be evidenced (controls, scans, tests) and what
  constitutes success.

### 11a.4 Creating a new NFR Jira Task

Copilot should propose a concrete command for the user to run using the
central Jira tooling repository (typically from that repo’s root, in the FtRS venv):

```bash
source .venv/bin/activate
python path/to/jira-tooling/create_issue.py \
  --nfr-code SEC-004 \
  --summary "Storage services show encryption enabled" \
  --description-file requirements/user-stories/jira/sec-004-description.txt \
  --issue-type Task \
  --priority Medium \
  --epic-summary "Search by ODS code Beta NFR Testing"
```

Rules:

- Use `--nfr-code` so the Jira summary is prefixed correctly.
- Use `--epic-summary` (or `--epic-key` if known) so the Task is linked
  to the NFR testing epic.
- Avoid `--labels` and `--components` unless the user insists; some
  fields are not present on all create screens and can cause HTTP 400
  errors.
- Keep `--project` at its default (`FTRS`) unless the user clearly
  wants another project.

On success, the script prints `Created issue: FTRS-XXXX` and exports a
Markdown copy to `requirements/user-stories/backlog/jira/`.

### 11a.5 Updating an existing Jira issue

`update_issue.py` can change summary, description, type, and Epic link.

Typical patterns Copilot may suggest:

- Rename to follow NFR convention:

  ```bash
  python path/to/jira-tooling/update_issue.py \
    --key FTRS-2132 \
    --summary "NFR - SEC-004 - Storage services show encryption enabled"
  ```

- Attach an existing issue to the NFR testing epic by summary:

  ```bash
  python path/to/jira-tooling/update_issue.py \
    --key FTRS-2132 \
    --epic-summary "Search by ODS code Beta NFR Testing"
  ```

- Update description from a local file, optionally stripping HTML:

  ```bash
  python path/to/jira-tooling/update_issue.py \
    --key FTRS-2127 \
    --description-file requirements/user-stories/jira/sec-001-description.html \
    --strip-html
  ```

Guardrails:

- Do not suggest changing issue type unless the user understands Jira
  workflow constraints; some transitions are blocked and must be done
  via the UI.
- Always include `--key` (e.g. `FTRS-2127`).
- Prefer `--epic-summary` over hard-coding custom field ids; the script
  discovers the `Epic Link` field automatically.

### 11a.6 When to create NFR Jira Tasks

For the Security domain, current practice is:

- Create NFR Jira Tasks only when the NFR has a `private-beta`
  milestone in `requirements/nfrs/security/nfrs.yaml`.
- Link the new Jira key in two places:
  - NFR-level `stories:` list under the relevant `code: SEC-xxx`
  - The associated `control_id:` entry's `stories:` list.

Copilot should:

- Check for existing `stories:` entries before proposing a new ticket.
- If a Jira key already exists, do **not** propose another create
  command; instead, suggest updating/renaming via `update_issue.py` if
  alignment is needed.

### 11a.7 Keeping YAML and docs in sync

After creating or wiring Jira tickets:

1. Update `requirements/nfrs/<domain>/nfrs.yaml` with the new Jira keys
   at both NFR and control level.
2. Regenerate NFR pages:

   ```bash
   python scripts/nfr/build_all_nfr_pages.py
   ```

3. Publish to Confluence (if appropriate for the change) using the
  external NFRs/Confluence publishing toolkit and NFR toolkit scripts
  (see those repositories for exact commands).

Copilot should propose these commands but **not** assume they have been
run; it must be clear that a human executes them.

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

```yaml
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

```text
Generate a new functional story for Directory Editor to update DoS entry opening hours improving accuracy. Reference NFR codes PERF-001 (latency), REL-002 (consistency), SEC-003 (audit). Provide 4 acceptance criteria (one negative), metrics section (p95 target + rationale), risks, and front matter with today's date.
```

---

## 19. Final Reminders for Copilot

- Never silently add or alter registry thresholds.
- Always surface rationale for any numeric target.
- Prefer conservative initial values; optimisation stories can tighten later.
- Encourage evidence linkage (dashboards, scan reports) in traceability notes.

---
