# GitHub Copilot Instructions

## GitHub Copilot Commit Message Guidelines

We are using **Conventional Commits** for all commit messages. Please follow these rules when generating commit messages.

---

### 1. Format

`<type>(<scope>): <jira> <description>`

- Place the Jira ticket immediately after the colon, before the description.
- If no scope, omit the parentheses: `<type>: <jira> <description>`
- **Example:** `feat(crud-apis): FTRS-123 Add login button`

---

### 2. Types

- `feat:` → New feature (**MINOR** version bump)
- `fix:` → Bug fix (**PATCH** version bump)
- `chore:` → Maintenance or tooling changes (no version bump)
- `docs:` → Documentation updates (no version bump)
- `style:` → Formatting or linting (no version bump)
- `refactor:` → Code restructuring (no version bump)
- `performance:` → Performance improvements (no version bump)
- `test:` → Adding or updating tests (no version bump)
- `feat!:` → Breaking change (**MAJOR** version bump)
- `ci:` → Changes to CI configuration or scripts (no version bump)
- `build:` → Changes affecting the build system or external dependencies (no version bump)
- `revert:` → Reverts a previous commit (no version bump)
- `style:` → Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc) (no version bump)

---

### 3. Scope

Optional — usually the module, feature, or area affected.

- Example: `(crud-apis)`, `(search)`, `(data-migration)`

---

### 4. Description

- Short, imperative, and written in present tense (e.g., “Add login validation logic”)
- Capitalize the first word.
- Avoid punctuation at the end.
- Always include the correct Jira ticket immediately after the colon (e.g., `feat(scope): FTRS-123 ...`).
- Be concise but descriptive.
- **CRITICAL:** The total length of `<type>(<scope>): <description>` MUST be under 100 characters.
- If approaching the limit, prioritize clarity over detail. Abbreviate where reasonable.

---

## 5. Validation Rule

Before generating a commit message, verify:
1. Count the total characters in the format: `<type>(<scope>): <description>`
2. If count ≥ 100, abbreviate the description
3. Never sacrifice the type or required punctuation to meet the limit

---

### Example Commit Messages Copilot Should Generate

- `feat(data-migration): Add user sync logic`
- `fix(crud-apis): Resolve token refresh issue`
- `docs(readme): Update installation instructions`
- `chore(ci): Update build pipeline`

---

When generating commit messages, always follow these rules.

## Confluence Publishing Runbook

Use this process to publish NFR pages to Confluence, including creating new Service pages (e.g., Programme) when first introduced.

### 1) Create and use a Python venv

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install markdown requests
```

### 2) Load Confluence environment and secrets

These environment and secrets scripts are now maintained in the external NFRs/Confluence toolkit repository. Consult that repository for the latest script names and locations before publishing.

### 3) Publish generated pages

- Prefer storage conversion (default) and enable Jira macro substitution.
- Publish domain and service indexes and children in one go:

Use the external NFRs/Confluence publishing toolkit (in the dedicated documentation tooling repository) to publish domain and service indexes and their children in one go.

### 4) Creating missing Service pages (first-time only)

If a new Service (folder under `docs/nfrs/nfr-by-service/`) doesn’t yet exist in Confluence, create it and its child pages under the Service category using `--allow-create-if-missing`:

Use the same external toolkit to create/ensure service top-level pages (index.md) exist and to publish each service’s child NFR pages.

Examples for Programme should use the external toolkit’s equivalent commands (see that repository’s README for exact syntax).

### 5) Optional: prune auto-generated pages

Removes auto-generated pages in Confluence that are no longer present locally under the configured parents.

Use the external toolkit’s prune functionality to remove auto-generated pages in Confluence that are no longer present locally.

### Notes

- Parent page resolution uses the titles “NFRs by Domain” and “NFRs by Service” under the configured top parent.
- Service folder names are mapped to Confluence page titles; unknown folders are title-cased (e.g., `programme` → `Programme`).
- To force using the Markdown macro instead of storage conversion, pass `--use-markdown-macro` (normally not needed).
- Jira macro substitution can be toggled via `--jira-macro` or `CONFLUENCE_USE_JIRA_MACRO=true`.

## Testing Standards

When generating or updating test functions, always include explicit type annotations for all function arguments.

`def test_example_function(input_data: dict, expected: int) -> None:`
This applies to all test files and all test functions, including fixtures and parameterized tests.
