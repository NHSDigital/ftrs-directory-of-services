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
- Stay under 100 characters for readability.

---

### Example Commit Messages Copilot Should Generate

- `feat(data-migration): FTRS-1607 Add user sync logic`
- `fix(crud-apis): FTRS-1711 Resolve token refresh issue`
- `docs(readme): FTRS-1680 Update installation instructions`
- `chore(ci): FTRS-1654 Update build pipeline`

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

These scripts define base URL, space, parent IDs, auth, and Jira macro settings.

```bash
source scripts/nfr/confluence_env.sh
source scripts/nfr/confluence_secrets.sh
```

### 3) Publish generated pages

- Prefer storage conversion (default) and enable Jira macro substitution.
- Publish domain and service indexes and children in one go:

```bash
python scripts/confluence/publish_markdown.py \
	--jira-macro \
	docs/nfrs/nfr-by-domain.md \
	docs/nfrs/nfr-by-domain/*.md \
	docs/nfrs/nfr-by-service.md \
	docs/nfrs/nfr-by-service/*/*.md
```

### 4) Creating missing Service pages (first-time only)

If a new Service (folder under `docs/nfrs/nfr-by-service/`) doesn’t yet exist in Confluence, create it and its child pages under the Service category using `--allow-create-if-missing`:

```bash
# Create/ensure all service top-level pages (index.md) exist
python scripts/confluence/publish_markdown.py \
	--jira-macro \
	--allow-create-if-missing \
	docs/nfrs/nfr-by-service/*/index.md

# Then publish the specific service’s child NFR pages
python scripts/confluence/publish_markdown.py \
	--jira-macro \
	--allow-create-if-missing \
	docs/nfrs/nfr-by-service/<service-folder>/*.md
```

Examples for Programme:

```bash
python scripts/confluence/publish_markdown.py --jira-macro --allow-create-if-missing docs/nfrs/nfr-by-service/programme/index.md
python scripts/confluence/publish_markdown.py --jira-macro --allow-create-if-missing docs/nfrs/nfr-by-service/programme/*.md
```

### 5) Optional: prune auto-generated pages

Removes auto-generated pages in Confluence that are no longer present locally under the configured parents.

```bash
python scripts/confluence/publish_markdown.py \
	--jira-macro \
	--prune-missing --prune-scope all \
	docs/nfrs/nfr-by-domain.md docs/nfrs/nfr-by-domain/*.md \
	docs/nfrs/nfr-by-service.md docs/nfrs/nfr-by-service/*/*.md
```

### Notes

- Parent page resolution uses the titles “NFRs by Domain” and “NFRs by Service” under the configured top parent.
- Service folder names are mapped to Confluence page titles; unknown folders are title-cased (e.g., `programme` → `Programme`).
- To force using the Markdown macro instead of storage conversion, pass `--use-markdown-macro` (normally not needed).
- Jira macro substitution can be toggled via `--jira-macro` or `CONFLUENCE_USE_JIRA_MACRO=true`.

## Testing Standards

When generating or updating test functions, always include explicit type annotations for all function arguments.

`def test_example_function(input_data: dict, expected: int) -> None:`
This applies to all test files and all test functions, including fixtures and parameterized tests.
