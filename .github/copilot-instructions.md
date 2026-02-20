# GitHub Copilot Instructions

## Find the Right Service (FTRS) - General

Our core programming languages are **Python** and **Terraform**, with infrastructure managed via AWS.

Our documentation is in [docs/](../docs) including developer guides, FHIR specifications, and user guides.

Services are located in [services/](../services) and include:

- `crud-apis` - CRUD operations for service data
- `data-migration` - migration from current DOS to FTRS
- `dos-search` - search functionality
- `dos-ui` - user interface
- `etl-ods` - ETL for ODS data
- `read-only-viewer` - test utility for the database

Architecture diagrams are in [architecture/](../architecture) and can be started with `npx likec4 start`.

---

## Copilot Instructions for Development

**When working on this codebase, follow these guidelines:**

1. **ALWAYS check current directory before path-specific commands** - Run `pwd` before executing any commands that depend on file paths or directory locations. Never assume you're in the repository root or any specific directory.

2. **ALWAYS use absolute paths with cd command** - Never use relative paths like `cd services/crud-apis` or `cd ../..`. Always use absolute paths. This prevents navigation errors when the current directory is uncertain.

3. **Use proper markdown code fence language specifiers** - Never use just ` ``` `, always specify the language (e.g., ` ```bash `, ` ```python `, ` ```terraform `, ` ```makefile `, ` ```plain `).

4. **Run pre-commit hooks before committing** - Always stage modified files with `git add <files>`, then ensure you're in the repository root directory, and run `git commit -m "message"` which will automatically trigger the pre-commit hooks. All hooks must pass successfully before the commit completes.

5. **Python environment setup** - For Python projects, always use `configure_python_environment` tool to set up the Python environment before running tests or installing dependencies.

6. **Always add or update tests** - When implementing new features or fixing bugs:
   - Write unit tests for all new functionality
   - Update existing tests when modifying behaviour
   - Ensure tests cover edge cases and error scenarios
   - Verify tests pass locally before committing (`make test`)
   - Aim for 80%+ code coverage on new code

7. **Document PRs appropriately** - When creating or updating pull requests, use the PR template at `.github/PULL_REQUEST_TEMPLATE.md`:
   - **Description**: Describe changes in detail - what was changed and why
   - **Context**: Explain why the change is required and what problem it solves
   - **Sensitive Information Declaration**: Confirm no PII/PID or sensitive data is included
   - **Title**: Use conventional commit format (e.g., `feat(crud-apis): FTRS-123 Add endpoint`)
   - Reference the Jira ticket in the title and description
   - List any breaking changes or migration steps required
   - Highlight areas that need particular review attention

---

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

## FHIR Standards

When working with FHIR resources:

1. **FHIR Version** - This API conforms to FHIR UK Core STU3 v0.0.6, based on FHIR R4 v4.0.1

2. **Resources** - Primary resources: `Organization`, `Endpoint`, `Bundle`, `OperationOutcome`

3. **Extensions** - Custom NHS England extensions are in [docs/fhir/structuredefinitions/](../docs/fhir/structuredefinitions/)

4. **Naming conventions** - Resource names are capitalised and singular (e.g., `/Organization` not `/organizations`)

---

## NHS API Management (APIM)

When working with APIs and specifications:

1. **OpenAPI Specs** - Located in [docs/specification/](../docs/specification/)

2. **Environments**:
   - `internal-dev` - Development environment
   - `internal-qa` - QA/Test environment
   - `int` - Integration environment
   - `sandbox` - Public sandbox for developer testing
   - `ref` - For regression testing
   - Production

3. **Authentication** - APIs use JWT Private Key authentication (application-restricted)

4. **Base URLs** - Format: `https://{environment}.api.service.nhs.uk/{api-path}/FHIR/R4`

---

## Testing Standards

When generating or updating test functions, follow these guidelines:

1. **Always include explicit type annotations** for all function arguments:

   ```python
   def test_example_function(input_data: dict, expected: int) -> None:
       ...
   ```

   This applies to all test files and all test functions, including fixtures and parameterized tests.

2. **Follow ruff linter rules** - The project uses ruff with the following enabled rules:
   - **ANN** - All functions must have type annotations (parameters and return types)
   - **I** - Imports must be sorted (standard library, third-party, local) with blank lines between groups
   - **E4, E7, E9** - Follow pycodestyle conventions
   - **F** - No unused imports or variables
   - **PL** - Follow pylint conventions
   - **TRY** - Proper exception handling patterns
   - **FURB** - Use modern Python patterns

3. **Code formatting requirements**:
   - Line length: 88 characters maximum
   - Indent: 4 spaces
   - Quote style: double quotes (`"`)
   - Target Python version: 3.12

4. **Test location** - Service automation tests and performance tests are stored in [tests/](../tests) and contain individual READMEs addressing their usage.

5. **Coverage target** - Aim for 80%+ coverage for all projects.

6. **Test command** - Use `make test` in each project/service directory.

---

## Appendix: Confluence Publishing Runbook

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
