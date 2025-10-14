# GitHub Copilot Commit Message Guidelines

We are using **Conventional Commits** for all commit messages. Please follow these rules when generating commit messages.

---

## 1. Format

`<type>(<scope>): <description>`

- **Example:** `feat(crud-apis): Add login button`
- **Character Limit:** The entire commit message (including type, scope, and description) MUST NOT exceed 100 characters.

---

## 2. Types

- `feat:` → New feature (**MINOR** version bump)
- `fix:` → Bug fix (**PATCH** version bump)
- `chore:` → Maintenance or tooling changes (no version bump)
- `docs:` → Documentation updates (no version bump)
- `style:` → Formatting or linting (no version bump)
- `refactor:` → Code restructuring (no version bump)
- `perf:` → Performance improvements (no version bump)
- `test:` → Adding or updating tests (no version bump)
- `feat!:` → Breaking change (**MAJOR** version bump)
- `ci:` → Changes to CI configuration or scripts (no version bump)
- `build:` → Changes affecting the build system or external dependencies (no version bump)
- `revert:` → Reverts a previous commit (no version bump)
- `style:` → Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc) (no version bump)

---

## 3. Scope

Optional — usually the module, feature, or area affected.

- Example: `(crud-apis)`, `(search)`, `(data-migration)`

---

## 4. Description

- Short, imperative, and written in present tense (e.g., “Add login validation logic”)
- Capitalize the first word.
- Avoid punctuation at the end.
- Always include the correct Jira ticket.
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

## Example Commit Messages Copilot Should Generate

- `feat(data-migration): Add user sync logic` (43 characters)
- `fix(crud-apis): Resolve token refresh issue` (46 characters)
- `docs(readme): Update installation instructions` (49 characters)
- `chore(ci): Update build pipeline` (35 characters)

---

When generating commit messages, always follow these rules.
