# GitHub Copilot Commit Message Guidelines

We are using **Conventional Commits** for all commit messages. Please follow these rules when generating commit messages.

---

### 1. Format

`<type>(<scope>): <description>`

- **Example:** `feat(crud-apis): Add login button`

---

### 2. Types

- `feat:` → New feature (**MINOR** version bump)
- `fix:` → Bug fix (**PATCH** version bump)
- `chore:` → Maintenance or tooling changes (no version bump)
- `docs:` → Documentation updates (no version bump)
- `style:` → Formatting or linting (no version bump)
- `refactor:` → Code restructuring (no version bump)
- `perf:` → Performance improvements (no version bump)
- `test:` → Adding or updating tests (no version bump)
- `feat!:` → Breaking change (**MAJOR** version bump)

---

### 3. Scope

Optional — usually the module, feature, or area affected.

- Example: `(crud-apis)`, `(search)`, `(data-migration)`

---

### 4. Description

- Short, imperative, and written in present tense.
- Capitalize the first word.
- Avoid punctuation at the end.
- Example: “Add login validation logic”

---

### 5. Guidelines

- Always include the correct Jira ticket.
- Be concise but descriptive.
- Ensure consistency and readability.

---

### Example Commit Messages Copilot Should Generate

- `feat(data-migration): Add user sync logic`
- `fix(crud-apis): Resolve token refresh issue`
- `docs(readme): Update installation instructions`
- `chore(ci): Update build pipeline`

---

When generating commit messages, always follow these rules.
