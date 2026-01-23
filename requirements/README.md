# Requirements Workspace

This workspace holds product User Stories and Non-Functional Requirements (NFRs) in source-controlled form so Copilot (and later MCP-linked tooling) can:

- Suggest acceptance criteria based on tagged NFRs
- Generate story boilerplate and traceability links
- Provide cross-references for compliance, audit and release readiness

## Structure

Key requirement artefacts:

- `nfrs/` domain folders each with `expectations.yaml`
- `nfrs/cross-references/nfr-matrix.md` – NFR code → story ID mapping

## Role-Based Step-by-Step Guides

### 1. Add a New Atomic NFR (Business Analyst / Tech Lead)

1. Identify the domain (e.g. Performance, Security).
2. Pick next unused numeric code (e.g. if PERF-013 exists, new is PERF-014). Do NOT reuse codes.
3. Create draft acceptance anchor line (succinct, testable) – one sentence, no conjunctions.
4. Update cross reference matrix: append a row in `nfrs/cross-references/nfr-matrix.md` with `(placeholder)` for stories if none exist yet.
5. (Optional) Add plain-language explanation in `nfrs/cross-references/nfr-explanations.yaml` under `explanations:`.
6. Link to any initial story(s) once created by adding their IDs into the matrix row.
7. Run the refresh script to verify the NFR appears with its explanation.
8. Commit (`feat(requirements): Add PERF-014 <JIRA-ID>`).

### 2. Create / Refine a Story Referencing NFRs (Business Analyst)

1. Fill `as_a`, `i_want`, `so_that`, and `business_value` fields.
2. Add `nfr_refs: [PERF-001, SEC-003]` referencing codes actually impacted.
3. Draft acceptance criteria: each must be objectively verifiable; avoid subjective language.

### 3. Add a Performance Operation Entry (Tech Lead)

1. Open `performance/expectations.yaml`.
2. Duplicate an existing operation block as a starting template.
3. Set `service`, unique `operation_id` (kebab-case, stable), and `performer_class` (FAST/STANDARD/SLOW).
4. Define `p50_target_ms`, `p95_target_ms`, `absolute_max_ms` based on design & user impact.
5. (Optional) Add `burst_tps_target`, `sustained_tps_target`, `max_request_payload_bytes`.
6. Leave `status: draft` initially; change to `accepted` after review.
7. Increment the file `version` if targets materially change (not for adding a new draft entry alone).
8. Run refresh script and confirm new operation in the Performance table.
9. Commit (`feat(performance): Add gp-list operation targets <JIRA-ID>`).

### 4. Add or Update a Domain Control (Tech Lead)

1. Open relevant domain `expectations.yaml` (e.g. `security/expectations.yaml`).
2. Add new object under `controls:` with unique `control_id` (kebab-case).
3. Map `nfr_code` (ensure it exists in the matrix).
4. Define `measure` (what is checked) and `threshold` (quantified target).
5. List `environments` and restrict `services` if not universal.

## Requirements Workspace (AI assistants overview)

This workspace holds product User Stories and Non-Functional Requirements (NFRs) in source control so AI assistants and automation can:

- Suggest acceptance criteria based on tagged NFRs
- Generate story scaffolds and traceability links
- Surface governance gaps (draft / exception) before release

---

## 1. Structure Overview

```text
requirements/
  README.md                     (this guide)
  nfrs/                         Domain expectation registries
    performance/                Latency & throughput targets (operation-centric)
    security/                   Security controls
    reliability/                Reliability controls
    availability/               Availability controls
    scalability/                Scalability controls
    interoperability/           Interoperability controls
    accessibility/              Accessibility controls
    cost/                       Cost controls
    governance/                 Governance controls
    compatibility/              Compatibility controls
    cross-references/           Linkage & explanations
      nfr-matrix.md             NFR code → story IDs
      nfr-explanations.yaml     Plain-language explanations
  user-stories/                 Story markdown files
scripts/
```

Generated summary: `docs/developer-guides/nfr-all-simplified.md`.

1. Pick domain (Performance, Security, etc.).
2. Determine next unused code (e.g. PERF-014). Do not recycle.
3. Draft anchor sentence (succinct, testable, single outcome).
4. Add row to `nfrs/cross-references/nfr-matrix.md` (use `(placeholder)` for story IDs if none yet).
5. (Optional) Add explanation in `nfr-explanations.yaml` under `explanations:`.
6. Run generator; confirm appearance.
7. Commit: `feat(requirements): Add PERF-014 <JIRA-ID>`.

### Explanation Guidelines

- ≤ 40 words, plain language
- Describe stakeholder value, not implementation
- Avoid repeating anchor verbatim

---

## 4. User Stories Referencing NFRs

1. Copy template from `user-stories/templates/` into `user-stories/backlog/` (`STORY-###-slug.md`).
2. Populate front matter: `as_a`, `i_want`, `so_that`, `business_value`.
3. Draft objective acceptance criteria (include edge / negative cases).
4. Move to `in-progress/` when work starts; `done/` when accepted.

Story front matter expected keys:

```yaml
business_value: <why>
acceptance_criteria:
  - <criterion>
out_of_scope:
  | Check | Action |
  |-------|--------|
  | Codes valid | Cross-check against `nfr-matrix.md` |
  | Fields present | Compare with schema section above |
  | Threshold realism | Peer review (Tech Lead) |
  | Rationale clarity | Ensure assumption + source present |
  | YAML parse | Run quick Python one-liner |
  | Explanation uniqueness | Avoid repeating anchor verbatim |

```

1. Duplicate an existing operation block.
2. Set `service`, unique `operation_id` (kebab-case), `performer_class` (FAST|STANDARD|SLOW).
3. Define `p50_target_ms`, `p95_target_ms`, `absolute_max_ms`.
4. (Optional) Add `burst_tps_target`, `sustained_tps_target`, `max_request_payload_bytes`.
5. Start with `status: draft`; shift to `accepted` after review.
6. Bump `version` only when changing existing targets materially.
7. Run generator and verify.
8. Commit: `feat(performance): Add gp-list operation targets <JIRA-ID>`.

```yaml
version: <semver>
operations:
  - service: <name>
    operation_id: <kebab-case>
    performer_class: FAST|STANDARD|SLOW
    p50_target_ms: <int>
    p95_target_ms: <int>
    absolute_max_ms: <int>
    burst_tps_target: <int?>
    sustained_tps_target: <int?>
    max_request_payload_bytes: <int?>
    status: draft|accepted
    rationale: <text>
```

## 6. Domain Control Entries (Tech Lead)

Non-performance domains use control-centric schema (`expectations.yaml`).

1. Add object under `controls:` with unique `control_id`.
2. Map valid `nfr_code`.
3. Define `measure` & quantified `threshold`.
4. Set `tooling`, `cadence`, `environments`, optional `services`.
5. Provide `rationale`.
6. `status`: `draft` → `accepted` (or `exception` with mitigation & review date).
7. Bump `version` when changing thresholds/rationale meaningfully.
8. Run generator; verify table entry.
9. Commit: `feat(security): Add build CVE gate control <JIRA-ID>`.

Control schema:

```yaml
version: <semver>
controls:
  - control_id: <kebab-case>
    nfr_code: <CODE>
    measure: <description>
    threshold: <quantified>
    tooling: <scanner|policy|test>
    cadence: <CI|daily|monthly|per-release>
    environments: [dev, int, ref, prod]
    services: [optional, if scoped]
    status: draft|accepted|exception
    rationale: <text>
```

Exception rationale format suggestion: `reason; mitigation; review YYYY-MM-DD`.

---

## 7. Validation Checklist (Pre-Commit)

| Check             | Action                                             |
| ----------------- | -------------------------------------------------- |
| Codes valid       | Ensure every `nfr_code` exists in `nfr-matrix.md`  |
| Unique IDs        | No duplicate `operation_id` / `control_id`         |
| Versioning        | Bump `version` only for changed existing targets   |
| Explanations      | All codes have entries (generator warns otherwise) |
| YAML parse        | Run quick one-liner below                          |
| Draft vs Accepted | Governance sign-off recorded before status change  |

One-liner parse:

```bash
python3 - <<'PY'
import yaml, pathlib, sys
root = pathlib.Path('requirements/nfrs')
errors = 0
for p in root.rglob('expectations.yaml'):
  try:
    yaml.safe_load(p.read_text())
  except Exception as e:
    errors += 1
    print(f'YAML ERROR {p}: {e}')
print('Done with', errors, 'errors')
sys.exit(1 if errors else 0)
PY
```

---

## 8. Handling Exceptions

1. Set `status: exception`.
2. Update `rationale` with cause, mitigation, review date.
3. Link follow-up remediation story ID(s).
4. Keep temporary thresholds explicit.
5. Commit: `fix(requirements): Record exception for burst throughput gp-nearby <JIRA-ID>`.

---

## 9. Governance Review Packet

Inputs: refreshed simplified page + registries.

Include:

- Domain status counts (draft / accepted / exception)
- Notable changes since last review (version bumps)
- Exceptions with review dates
- Upcoming remediation stories

Summary prompt skeleton:

```text
Produce governance summary: accepted=<A> draft=<D> exception=<E>. Two paragraphs: Overview + Recommended actions. <= 180 words.
```

---

## 10. AI Assistance (Prompt Patterns & Guardrails)

### Core Guardrails

- Never invent NFR codes – reserve manually first.
- AI proposals require human threshold validation.
- Reject changes lacking rationale.
- Keep explanation ≤ 40 words, stakeholder-focused.
- Rerun generator after edits to catch omissions.
- Parse YAML for any registry modifications.

### Prompt Skeleton Table

| Scenario                  | Prompt Skeleton                                                                                                                               |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| New NFR                   | "Draft succinct, testable acceptance anchor for new Performance NFR about [topic]; propose p50/p95/absolute_max targets + 20-word rationale." |
| Threshold refinement      | "Given current p50=320ms/p95=780ms for operation gp-list, propose realistic FAST targets balancing UX and backend limits."                    |
| Story acceptance criteria | "Generate 3 objective acceptance criteria for STORY-123 referencing PERF-004 and SEC-003; include one negative path."                         |
| Explanation authoring     | "Write a plain-language (<35 words) explanation for NFR REL-005 emphasizing user impact if unmet."                                            |
| Control ideation          | "Suggest two Security controls for dependency scanning with measurable thresholds and tooling options."                                       |
| Exception rationale       | "Provide concise exception rationale for control tls-encryption-endpoints not met due to legacy endpoint; include mitigation & review date."  |

### Rapid Evaluation Checklist

| Aspect              | Accept If                                   |
| ------------------- | ------------------------------------------- |
| Schema completeness | All mandatory fields present                |
| Code validity       | Codes exist in matrix                       |
| Threshold realism   | Anchored by current telemetry or benchmarks |
| Rationale clarity   | States driver + assumption/source           |
| Explanation value   | Adds clarity beyond anchor                  |

### YAML Safety Pre-Lint Prompt

````text
Content:
```yaml
<PASTE BLOCK>
```

List syntax/formatting issues (indent, tabs, quoting, lists). Return fixes + reasoning.
````

### Anti-Patterns (Reject)

- Vague thresholds ("improve latency")
- Multiple disparate outcomes in one control
- Jargon-heavy explanations
- Invented tooling names

---

## 11. Commit Guidance (Conventional Commits)

| Type | Example |
|------|---------|
| feat | feat(performance):  <JIRA-ID> Add gp-bulk-search operation targets |
| fix | fix(requirements):  <JIRA-ID> Correct p95 target for gp-list |
| docs | docs(requirements):  <JIRA-ID> Add explanation for PERF-014 |
| chore | chore(scripts):  <JIRA-ID> Refactor NFR page generator |
| refactor | refactor(requirements):  <JIRA-ID> Consolidate duplicated README sections |

Include Jira key; capitalize first word after colon; no trailing period.

---

## 12. Refreshing the Simplified NFR Page

Use the external NFR toolkit to regenerate the simplified NFR page
(`docs/developer-guides/nfr-all-simplified.md`). See that repository
for the exact command and options. The generator still warns for
missing explanations; commit only with substantive registry/content
changes.

---

## 13. Quick Reference Schemas

Performance (operations) and other domains (controls) are documented above; keep fields ordered for readability.

---

## 14. Future Enhancements (Backlog Ideas)

| Idea | Value |
|------|-------|
| Linter for NFR codes in stories | Prevents typos & orphan references |
| Automated diff-based governance summary | Speeds review packet creation |
| Evidence link field in control schema | Direct audit trace |
| CI job to fail on missing explanations | Maintains coverage |
| Story acceptance criteria template generator | Reduces manual drafting time |

---

## 15. Glossary (Selected Terms)

| Term | Definition |
|------|------------|
| Anchor | Single-sentence testable NFR expression |
| Control | Automatable check enforcing part of an NFR |
| Operation | Discrete API/flow measured for performance |
| Exception | Temporarily unmet target with mitigation plan |
| Performer Class | FAST/STANDARD/SLOW latency classification |

---

## 16. Minimal Parsing Sanity (One-Liner)

```bash
python3 - <<'PY'
import yaml, sys; yaml.safe_load(open('requirements/nfrs/performance/expectations.yaml').read()); print('performance OK')
PY
```

Extend pattern for other domains as needed.

---

## 17. Getting Started Checklist

1. Read this README once end-to-end.
2. Add first domain NFR (e.g. PERF-001) + explanation.
3. Create initial story referencing it.
4. Define first performance operation targets.
5. Run generator; inspect summary.
6. Iterate with AI assist + human review.

---

## 18. Anti-Regressions

Before merging any README rewrite ensure:

- Schemas remain accurate.
- Traceability flow ordering intact.
- AI guardrails section present.
- Commit guidance table retained.

---

End of README.
| Type | When to Use |
|------|-------------|
| feat | New NFR code, new operation, new control |
| fix | Correct thresholds, typos impacting meaning |
| docs | README or explanation updates, regenerated summary |
| chore | Script housekeeping, non-functional tooling |
| refactor | Structural code/script changes without feature addition |

Always append Jira ticket key at the end or in scope: `feat(performance): Add gp-bulk-search operation JIRA-1234`.

### 12. Quick Reference Flow Summary

Immutable NFR codes → Capability specs → Atomic stories → Acceptance & operational specs (registries) → Telemetry → Automated validation → Evidence.

---

End of role guides.
\n+## AI Assistance (Prompt Patterns & Guardrails)
\n+Use AI (Copilot / future MCP agents) to accelerate drafting while keeping humans accountable. Always validate generated output against the registry, matrix, and codebase before committing.\n+\n+### Core Guardrails

1. Never invent NFR codes — only use those present in `nfr-matrix.md` or newly reserved by a human first.\n+2. Verify thresholds with a human; AI can propose but not approve governance values.\n+3. Reject any prompt output lacking rationale when changing a target.\n+4. Keep explanations stakeholder-friendly (avoid jargon beyond necessary domain terms).\n+5. Re-run the refresh script after accepting AI changes to detect omissions (explanation coverage, missing control fields).\n+6. Treat AI suggestions as drafts: run the YAML parse quick check if modifying registries.\n+\n+### Prompt Pattern Syntax
   Use angle brackets `<placeholder>` to indicate items to substitute. Provide context snippets (NFR codes, existing entries) inline for higher accuracy.\n+\n+### 1. Generate Plain-Language Explanations for New NFR Codes

```text
You are helping update an explanations file. Given these NFR codes and anchors:
# Requirements Workspace

This workspace holds product User Stories and Non-Functional Requirements (NFRs) in source-controlled form so AI assistants and future automated tooling can:

* Suggest acceptance criteria based on tagged NFRs
* Generate story boilerplate and traceability links
* Provide cross-references for compliance, audit and release readiness

## Structure

Key requirement artefacts live under `requirements/`:
* `nfrs/` – domain folders (performance, security, etc.) each with an `expectations.yaml`
* `nfrs/cross-references/nfr-matrix.md` – canonical list of NFR codes → story IDs
* `nfrs/cross-references/nfr-explanations.yaml` – plain-language descriptions shown in rendered tables
* `user-stories/` – (templates, backlog, in-progress, done) story markdown files with `nfr_refs:` arrays
* `scripts/nfr/refresh_simplified_nfr_page.py` – generator producing consolidated view (`docs/developer-guides/nfr-all-simplified.md`)

## Role-Based Step-by-Step Guides

### 1. Add a New Atomic NFR (Business Analyst / Tech Lead)
1. Identify the domain (Performance, Security, etc.).
2. Pick next unused numeric code (if PERF-013 exists, new is PERF-014). Never reuse codes.
3. Draft an acceptance anchor line (succinct, testable, one sentence, no conjunctions).
4. Append a row in `nfrs/cross-references/nfr-matrix.md` (use `(placeholder)` for stories if none yet).
5. (Optional) Add an explanation in `nfr-explanations.yaml` under `explanations:`.
6. Link initial story IDs once created by adding them to the matrix row.
7. Run the refresh script; verify NFR appears with its explanation.
8. Commit (`feat(requirements): Add PERF-014 <JIRA-ID>`).

### 2. Create or Refine a Story Referencing NFRs (Business Analyst)
1. Copy a template from `user-stories/templates/` to `user-stories/backlog/` (rename `STORY-###-slug.md`).
2. Fill `as_a`, `i_want`, `so_that`, `business_value`.
3. Add `nfr_refs: [PERF-001, SEC-003]` referencing impacted codes only.
4. Draft objective acceptance criteria (avoid subjective wording).
5. Include edge and negative paths when relevant.
6. (Future) Run linter to validate referenced NFR codes exist.
7. Move story to `in-progress/` when work starts; to `done/` when accepted.

### 3. Add a Performance Operation Entry (Tech Lead)
1. Open `performance/expectations.yaml`.
2. Duplicate an existing operation block.
3. Set `service`, unique `operation_id` (kebab-case), `performer_class` (FAST/STANDARD/SLOW).
4. Define `p50_target_ms`, `p95_target_ms`, `absolute_max_ms`.
5. (Optional) Add `burst_tps_target`, `sustained_tps_target`, `max_request_payload_bytes`.
6. Provide concise `rationale` (drivers, assumptions).
7. Start with `status: draft`; change to `accepted` after review.
8. Increment `version` if targets materially change.
9. Run refresh script; confirm operation appears.
10. Commit (`feat(performance): Add gp-list operation targets <JIRA-ID>`).

### 4. Add or Update a Domain Control (Tech Lead)
1. Open domain `expectations.yaml` (e.g. `security/expectations.yaml`).
2. Add object under `controls:` with unique `control_id` (kebab-case).
3. Map `nfr_code` (must exist in matrix).
4. Define `measure` (what is checked) & `threshold` (quantified target).
5. Set `tooling` (scanner/test/policy) & `cadence` (CI, daily, per-release, etc.).
6. List `environments` and restrict `services` if not universal.
7. Provide clear `rationale`.
8. Bump `version` if changing threshold or scope of existing control.
9. Run refresh script; verify domain table entry.
10. Commit (`feat(security): Add build CVE gate control <JIRA-ID>`).

### 5. Provide Plain-Language Explanations (Business Analyst)
1. Open `nfr-explanations.yaml`.
2. Add any missing code under `explanations:` with a concise description.
3. Keep wording user-centric; avoid deep technical jargon unless essential.
4. Run refresh script (warns on gaps).
5. Commit (`docs(requirements): Add explanation for PERF-014 <JIRA-ID>`).

### 6. Regenerate Simplified NFR Page (Any)
1. Run `python3 scripts/nfr/refresh_simplified_nfr_page.py`.
2. Inspect `docs/developer-guides/nfr-all-simplified.md` for new rows & warnings.
3. Commit (`docs(nfr): Regenerate simplified NFR page <JIRA-ID>`).

## AI Assistance (Prompt Patterns & Guardrails)

Use structured prompts to maximise high‑quality outputs:

| Scenario | Prompt Skeleton |
|----------|-----------------|
| Add new NFR | "Propose a succinct, testable acceptance anchor for a new Performance NFR about [topic]; include p50/p95/absolute max targets with rationale." |
| Refine thresholds | "Given current p50=300ms/p95=800ms logs for operation gp-list, suggest realistic FAST-class targets balancing user experience and backend limits." |
| Story drafting | "Generate 3 objective acceptance criteria for story STORY-123 referencing PERF-004 and SEC-003; include one negative path." |
| Explanation authoring | "Write a plain-language explanation (<40 words) for NFR PERF-012 focused on sustained throughput value to end users." |
| Control ideation | "List two candidate Security controls for build-time dependency scanning with measurable thresholds and tooling options." |

Guardrails:
* Never fabricate story IDs or NFR codes – verify in matrix first.
* Prefer conservative initial thresholds; escalate only with profiling data.
* Separate performance (latency/throughput) from capacity (scalability) in wording.
* Keep explanations ≤ 40 words; avoid unbounded adjectives.

## Traceability Flow

`NFR code → capability spec → atomic user stories → operational/acceptance specs → automated tests & telemetry → evidence (dashboards, scans)`

Each stage should reference upstream identifiers (e.g. story lists its NFR codes; test names include operation_id or control_id).

## Domain Registries & Schemas

All non-performance domains use a control-centric schema in their `expectations.yaml`:

```yaml
version: <semantic-version>
controls:

- control_id: <kebab-case-unique>
  nfr_code: <CODE>
  measure: <what is examined>
  threshold: <quantified target>
  tooling: <scanner/test/policy>
  cadence: <CI|daily|monthly|per-release>
  environments: [dev, int, prod]
  services: [optional service list]
  status: draft|accepted|exception
  rationale: <brief justification>

```

Performance uses an operation-centric schema:

```yaml
version: <semantic-version>
operations:

- service: <service-name>
  operation_id: <kebab-case-unique>
  performer_class: FAST|STANDARD|SLOW
  p50_target_ms: <int>
  p95_target_ms: <int>
  absolute_max_ms: <int>
  burst_tps_target: <int?>
  sustained_tps_target: <int?>
  max_request_payload_bytes: <int?>
  status: draft|accepted
  rationale: <brief justification>
```

## Refreshing the Simplified NFR Page

Run the generator to produce the consolidated markdown tables summarising domains, operations, and explanations.

- Command: `python3 scripts/nfr/refresh_simplified_nfr_page.py`
- Output: `docs/developer-guides/nfr-all-simplified.md`
- Includes warnings if explanations are missing for any NFR code.

## Commit Guidance

Follow Conventional Commits with Jira ticket IDs:

- `feat(requirements): Add security expectations registry <JIRA-ID>`
- `chore(scripts): Render domain registries in simplified NFR page <JIRA-ID>`
- `docs(nfr): Regenerate simplified NFR page <JIRA-ID>`

See `.github/copilot-instructions.md` for full commit rules.

### Governance Packet Summary Draft

Provide a concise summary of NFR governance status counts given:
accepted=<N_ACCEPTED> draft=<N_DRAFT> exception=<N_EXCEPTION>
Produce 2 paragraphs: Overview + Action Focus. Max 180 words.

### 12. YAML Safety Check (AI Pre-Lint)

Content:

```yaml
<PASTE BLOCK>
```

Identify likely syntax / formatting issues (unquoted comparators, tabs, inconsistent indentation, missing commas in lists). Return list of issues and fixed YAML.

### Evaluating AI Output Quickly

| Check | Action |
|-------|--------|
| Codes valid | Cross-check against `nfr-matrix.md` |
| Fields present | Compare with schema section above |
| Threshold realism | Peer review (Tech Lead) |
| Rationale clarity | Ensure assumption + source present |
| YAML parse | Run quick Python one-liner |
| Explanation uniqueness | Avoid repeating anchor verbatim |

### Example One-Liner to Parse Modified Snippet

```bash
python3 - <<'PY'
import yaml, sys; yaml.safe_load(open('<FILE>').read()); print('YAML OK')
PY
````

### Anti-Patterns to Reject

- Vague thresholds ("improve latency")
- Multiple outcomes in one control/story
- Jargon-heavy explanations not simplifying anchor
- Invented tooling names or unsupported environment labels

### When to Prefer Manual Over AI

  | Scenario | Reason |
  |----------|--------|
  | Regulatory wording | Compliance nuance requires human legal review |
  | Novel domain risk | No training data context; high hallucination risk |
  | Final sign-off thresholds | Governance requires human accountability |
  \n+### Minimal Acceptance of AI Suggestions
  Accept only if: schema complete + rationale present + codes valid + no contradiction with existing registry entries.
  \n+---
  End of AI assistance section.
  requirements/
  README.md Overview
  nfrs/
  areas/ Top-level NFR domains
  security/
  performance/
  reliability/
  scalability/
  operability/
  maintainability/
  accessibility/
  privacy/
  compliance/
  cost/
  cross-references/ Matrices & linkage files
  index.yaml Canonical NFR registry
  nfr-matrix.md Table linking domains → stories
  tags.md Tagging & coding conventions
  user-stories/
  templates/ Story & acceptance criteria templates
  backlog/ New / unprioritised stories
  in-progress/ Active development
  done/ Accepted & merged stories

## Conventions

### File Naming

- NFR high-level domain overviews: `overview.md` inside each domain directory.
- Atomic NFRs (testable statements): `NFR-CODE.md` (e.g. `PERF-001.md`).
- User stories: `STORY-<increment>-<slug>.md` (e.g. `STORY-042-search-gp-endpoints.md`).

### Codes

| Domain | Prefix |
|--------|--------|
| Security | SEC |
| Performance | PERF |
| Reliability | REL |
| Scalability | SCALE |
| Operability | OPER |
| Maintainability | MAINT |
| Accessibility | A11Y |
| Privacy | PRIV |
| Compliance | COMP |
| Cost Optimisation | COST |

Each atomic NFR increments (e.g. `SEC-001`, `SEC-002`). Do not recycle codes.

### Linking Stories → NFRs

In a story front-matter block include `nfr_refs: [SEC-003, PERF-002]`. Copilot can then surface acceptance criteria scaffolds.

### Story Template Keys

- `as_a`
- `i_want`
- `so_that`
- `business_value`
- `nfr_refs` (array)
- `acceptance_criteria`
- `out_of_scope`
- `notes`

## Cross Reference Flow

1. Add or refine an atomic NFR in the relevant domain.
2. Update `nfrs/cross-references/index.yaml` registry.
3. Reference the NFR code(s) in story front-matter.
4. Generate acceptance criteria using template - Copilot can expand by pulling test phrases aligned to each NFR.

## Next Steps

- Populate each domain with initial NFRs.
- Add story examples referencing them.
- Automate validation (lint) to ensure referenced NFR codes exist.

## Expectations Registries (operational controls)

We use simple, versioned YAML registries to define concrete, automatable expectations per domain. These power the auto-generated summary in `docs/developer-guides/nfr-all-simplified.md` and guide test automation and governance.

### Where they live

- Performance: `requirements/nfrs/performance/expectations.yaml`
- Security: `requirements/nfrs/security/expectations.yaml`
- Observability: `requirements/nfrs/observability/expectations.yaml`
- Reliability: `requirements/nfrs/reliability/expectations.yaml`
- Availability: `requirements/nfrs/availability/expectations.yaml`
- Scalability: `requirements/nfrs/scalability/expectations.yaml`
- Interoperability: `requirements/nfrs/interoperability/expectations.yaml`
- Accessibility: `requirements/nfrs/accessibility/expectations.yaml`
- Cost: `requirements/nfrs/cost/expectations.yaml`
- Governance: `requirements/nfrs/governance/expectations.yaml`
- Compatibility: `requirements/nfrs/compatibility/expectations.yaml`

### Common schema (controls)

Each `expectations.yaml` (other than Performance, which is per-operation) contains:

- `version`: registry version string (increment on meaningfully changed targets)
- `generated`: ISO date to record last authoring
- `controls`: array of objects where each control includes:
  - `control_id`: stable identifier for the check (e.g., `tls-encryption-endpoints`)
  - `nfr_code`: mapped domain NFR (e.g., `SEC-003`, `OBS-009`)
  - `measure`: short description of what is verified
  - `threshold`: quantified acceptance (e.g., `>= 95%`, `0 critical findings`)
  - `tooling`: primary automation used to verify (scanners, policies, tests)
  - `cadence`: how often the check runs (CI, daily, monthly, per release)
  - `environments`: list of envs covered (e.g., `[int, ref, prod]`)
  - `services`: list of targeted services (blank or list of all for universal controls)
  - `status`: governance state (`draft`, `accepted`, `exception`)
  - `rationale`: brief notes supporting the target/tool choice

Performance uses an operation-centric schema in `requirements/nfrs/performance/expectations.yaml` with keys like `service`, `operation_id`, `performer_class`, `p50_target_ms`, `p95_target_ms`, `absolute_max_ms` and optional `burst_tps_target`, `sustained_tps_target`, `max_request_payload_bytes`.

---

## Offline Jira Workflow & Tooling

Until direct Jira API access is available, treat the repository as the authoritative source:

### Flow

1. Create service spec from template: `requirements/service-specs/_template.md` → new spec file.
2. Derive atomic stories using `requirements/user-stories/_story-template.md` → place in `requirements/user-stories/backlog/`.
3. Populate front matter, acceptance criteria (≥3), and `nfr_refs` (must exist in `nfr-matrix.md`).
4. Validate using the Jira tooling in the dedicated requirements/Jira helper repository (checks front matter, mandatory spec sections, criteria count, NFR codes).
5. Export paste-ready text using the same external Jira tooling so it can be copied into Jira when available.
6. Once Jira keys exist, start including them in commit messages and (optionally) rename story files with real keys.

### Templates

| Type | Path |
|------|------|
| Service Spec | `requirements/service-specs/_template.md` |
| Story | `requirements/user-stories/_story-template.md` |

### Scripts

Validation and export scripts now live in the central Jira tooling repository rather than this repo. Use that toolkit for offline validation and export, keeping this repository as the source of requirements content only.

### Commit Message Hook

`scripts/githooks/commit-msg` warns if Conventional Commit format or Jira key absent (advisory only until keys available).

### Quick Commands

Use the commands provided by the external Jira tooling repository to validate artifacts and export paste-ready text for Jira.

````

### Review Checklist Before Paste

| Item               | Check                                              |
| ------------------ | -------------------------------------------------- |
| Story completeness | Front matter present; ≥3 criteria                  |
| NFR refs           | Codes valid & minimal                              |
| Spec sections      | All mandatory headers retained                     |
| Export text        | Contains Description + Acceptance + Non-Functional |
| Commit advisory    | Decide if placeholder key acceptable               |

### Copy/Paste Guidance

- Jira Summary = story title.
- Jira Description = exported block (trim internal-only notes if undesired).
- Labels (optional): `spec-derived`, `nfr:<CODE>`.
- Link EPIC manually; include relative repository path to spec for traceability.

### After Keys Allocated

1. Amend commit messages going forward to include Jira key.
2. Optionally interactive rebase to retrofit past commits (only if governance demands).
3. Keep repository artefacts as canonical even after Jira population.

### Future Enhancements

| Enhancement             | Benefit                            |
| ----------------------- | ---------------------------------- |
| CI validation step      | Prevents invalid artefacts merging |
| HTML export             | Better Jira formatting fidelity    |
| Bulk create script      | Reduces manual ticket entry        |
| Test scaffold generator | Speeds coverage alignment          |

---

## Governance & Quality Quick Reference

| Category       | Good                       | Poor                   |
| -------------- | -------------------------- | ---------------------- |
| NFR anchor     | Single outcome, testable   | Multi-clause, vague    |
| Rationale      | States driver + assumption | Restates anchor only   |
| Threshold      | Numeric/time-bound         | "Fast", "secure"       |
| Story criteria | Objective, measurable      | Subjective, untestable |
| Explanation    | Adds context               | Duplicates anchor      |

---

## One-Liner YAML Parse (All registries)

```bash
python3 - <<'PY'
import yaml, pathlib, sys
root=pathlib.Path('requirements/nfrs')
bad=0
for f in root.rglob('expectations.yaml'):
  try: yaml.safe_load(f.read_text())
  except Exception as e:
    bad+=1; print('YAML ERROR', f, e)
print('Done with', bad, 'errors'); sys.exit(1 if bad else 0)
PY
```

---

## Conventional Commit Reminder

`<type>(<scope>): <Description> <JIRA-ID>`

Examples:

- `feat(requirements): Add PERF-014 latency target PERF-321`
- `docs(requirements): Update offline Jira workflow PERF-322`
- `chore(scripts): Add story export script PERF-323`

---

### Refreshing the simplified NFR page

- Run: `python3 scripts/nfr/refresh_simplified_nfr_page.py`
- Output: `docs/developer-guides/nfr-all-simplified.md`
- The generator automatically includes domain registry summaries if the respective YAML file exists.

### Adding or refining controls

- Edit the relevant domain `expectations.yaml`, following the schema above.
- Prefer concrete thresholds and named tooling.
- Use `services` to scope controls to specific services when not universal.
- Increment `version` when materially changing targets or scope.

### Commit guidance

- Use Conventional Commits and include the Jira ticket ID, e.g.:
  - `feat(requirements): Add security expectations registry`
  - `chore(scripts): Render domain registries in simplified NFR page`
  - `docs(nfr): Regenerate simplified NFR page`
- See `.github/copilot-instructions.md` for full commit rules.
