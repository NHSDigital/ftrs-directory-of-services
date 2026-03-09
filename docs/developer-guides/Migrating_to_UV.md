# Migrating to uv Workspaces

This guide covers the migration of `ftrs-directory-of-services` from fragmented per-service **Poetry** setups to a unified **uv** workspace.

The previous approach required you to maintain separate virtual environments, `poetry.lock` files, and `poetry install` runs for each service. This migration consolidates everything into a **single virtual environment** at the repository root, with one unified lockfile (`uv.lock`), giving you correct cross-package intellisense and a dramatically faster dependency install.

---

## What Changed

| Area | Before | After |
| ---- | ------ | ----- |
| Package manager | `poetry 2.1.1` | `uv 0.10.9` |
| Virtual environments | One per service (e.g. `services/crud-apis/.venv`) | One at repo root (`.venv`) |
| Lockfile | Per-service `poetry.lock` | Single `uv.lock` at repo root |
| Build backend | `poetry-core` | `hatchling` |
| Internal dependencies | `{path = "../../...", develop = true}` | `{workspace = true}` |
| Dev dependency groups | `[tool.poetry.group.dev.dependencies]` | `[dependency-groups] dev = [...]` |
| Run a tool | `poetry run ruff check` | `uv run ruff check` |
| Install | `poetry install --no-interaction` | `uv sync` |
| Build wheel | `poetry build -f wheel -o <dir>` | `uv build --wheel --out-dir <dir>` |
| Export requirements | `poetry export --without dev --without-hashes` | `uv export --no-dev --no-hashes --no-emit-workspace` |
| `.tool-versions` per service | Present (Python + poetry) | Deleted — inherits from repo root |
| Root `pyproject.toml` | Did not exist | New — defines the uv workspace |

---

## Prerequisites

### 1. Install uv via asdf

The root `.tool-versions` specifies the correct `uv` version. Install it using asdf from the repository root:

```bash
# Add the uv plugin if you don't already have it
asdf plugin add uv

# Install all tools declared in .tool-versions (including uv)
asdf install
```

Verify the installation:

```bash
uv --version
# uv 0.10.9 (or later)
```

If you are not using asdf, install `uv` manually as a fallback:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Remove old Poetry artefacts (one-time cleanup)

Poetry left behind per-service virtual environments and lockfiles. Clean these up before syncing to avoid confusion:

```bash
# Remove all per-service .venv directories
find . -mindepth 2 -maxdepth 4 -name '.venv' -type d \
  -not -path './.venv' \
  -exec rm -rf {} +

# Remove per-service poetry.lock files (now replaced by the root uv.lock)
find . -mindepth 2 -maxdepth 4 -name 'poetry.lock' -delete
```

You can also uninstall Poetry if you no longer need it outside this project:

```bash
pipx uninstall poetry   # if installed via pipx
# or
asdf uninstall poetry 2.1.1
```

---

## Step 1: Sync the Workspace

From the **repository root**, run:

```bash
uv sync
```

`uv` will:

1. Read the root `pyproject.toml` which declares all workspace members.
2. Resolve every member's dependencies against the single `uv.lock`.
3. Create `.venv` at the repo root.
4. Install all internal packages (`ftrs-python-packages`, `ftrs-aws-local`, etc.) as editable installs inside that `.venv`.

This replaces running `poetry install` inside each service directory.

> **Note:** `uv sync` must be run from the repo root. Running it from inside a service directory will work but only installs that service's slice of the workspace.

---

## Step 2: VS Code Integration

Because there is now a single `.venv` at the repository root, VS Code only needs to be pointed at it once:

1. Open the Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`).
2. Choose **Python: Select Interpreter**.
3. Select `./.venv/bin/python` (the root virtual environment).

VS Code will now resolve cross-package imports correctly — for example, `services/dos-search` importing from `application/packages/python` will work without any workspace-settings tricks.

---

## Step 3: Day-to-Day Commands

All `poetry run <tool>` invocations are replaced with `uv run <tool>`. You do **not** need to activate the virtual environment first.

### Linting and formatting

```bash
# Check for lint issues
uv run ruff check .

# Auto-fix lint issues
uv run ruff check --fix .

# Format code
uv run ruff format .

# Check formatting without writing changes
uv run ruff format --check .
```

### Running tests

```bash
# Run tests for a specific service
uv run pytest services/dos-search/tests/unit
uv run pytest services/crud-apis/tests/unit
uv run pytest services/data-migration/tests/unit

# Run tests for a shared package
uv run pytest application/packages/python

# Run with coverage (as used by make test)
uv run pytest --cov-report xml:coverage-dos-search.xml services/dos-search/tests/unit
```

You can also use the existing `make test` targets from within each service directory — the Makefile targets have been updated to use `uv run` internally.

### Running local services

The services expose `[project.scripts]` entry points that can be launched via `uv run` directly:

```bash
# crud-apis
uv run start-organisations-api
uv run start-healthcare-api
uv run start-location-api
uv run start-all-apis

# ftrs-aws-local (local DynamoDB utilities)
uv run ftrs-aws-local

# data-migration CLI
uv run dos-etl
```

---

## Step 4: Adding New Dependencies

### Add a third-party package to a specific service

```bash
uv add requests --project ./services/crud-apis
```

This adds `requests` to `services/crud-apis/pyproject.toml` and updates the root `uv.lock`.

### Add a dev-only dependency

```bash
uv add --dev freezegun --project ./services/crud-apis
```

This adds `freezegun` to the `[dependency-groups] dev` table in that service's `pyproject.toml`.

### Add an internal workspace dependency

```bash
uv add ftrs-python-packages --project ./services/crud-apis
```

`uv` detects that `ftrs-python-packages` is a workspace member and writes `{workspace = true}` as the source automatically — no path wrangling or PyPI lookup required.

### Remove a dependency

```bash
uv remove requests --project ./services/crud-apis
```

Always commit both the changed `pyproject.toml` **and** the updated `uv.lock` together.

---

## Step 5: Building Lambda Artefacts

The `make build` targets in each service directory have been updated. For reference, the underlying commands are:

### Build a wheel

```bash
uv build --wheel --out-dir build/services/dos-search
```

### Export a requirements file (no dev deps, for Lambda layers)

```bash
uv export \
  --no-dev \
  --no-hashes \
  --no-emit-workspace \
  -o build/services/dos-search/dependency-layer/requirements.txt
```

`--no-emit-workspace` ensures internal packages (which are editable workspace installs) are not listed in the requirements file — they are bundled separately as part of the wheel build.

---

## Workspace Structure

The root `pyproject.toml` declares all workspace members. `uv` resolves and locks all of their dependencies together.

### Included members

| Member | Description |
|---|---|
| `services/crud-apis` | CRUD operations service |
| `services/dos-search` | DoS search Lambda |
| `services/data-migration` | Migration from DOS to FTRS |
| `services/etl-ods` | ETL for ODS data |
| `services/slack-notifier` | Slack notification Lambda |
| `services/sandbox-dos-ingest` | Sandbox ingest service |
| `application/packages/python` | Shared Python packages (`ftrs-python-packages`) |
| `application/packages/ftrs_aws_local` | Local AWS utilities (`ftrs-aws-local`) |
| `tests/service_automation` | Service test automation framework |
| `scripts/workflow/tests/open_search_index` | Workflow OpenSearch index tests |
| `sandbox/dos-ingest-sandbox` | Ingest sandbox service |

### Explicitly excluded

| Path | Reason |
|---|---|
| `services/dos-ui` | JavaScript/TypeScript — not a Python project |
| `services/read-only-viewer` | JavaScript/TypeScript — not a Python project |
| `sandbox/dos-search` | No `pyproject.toml` |
| `application/packages/utilities` | Container directory, not a package itself |
| `tests/performance/scripts/data_generation` | Pins `pandas==3.0.0`, incompatible with `awswrangler>=3.x` used elsewhere. Manage its virtual environment independently |

---

## Performance Tests (Excluded from Workspace)

`tests/performance/scripts/data_generation` is excluded from the uv workspace due to a dependency conflict (`pandas==3.0.0` vs `awswrangler>=3.x`). To work on it locally, manage its environment independently:

```bash
cd tests/performance/scripts/data_generation
uv sync
uv run pytest
```

The rest of `tests/performance` (JMeter / Allure) is not Python-managed — see the performance test README.

---

## Troubleshooting

### `uv sync` fails with a resolution conflict

A `pyproject.toml` in one of the workspace members likely pins a version that conflicts with another member. Check the error output for the conflicting packages and adjust constraints.

### VS Code shows import errors after syncing

Re-run **Python: Select Interpreter** and confirm `./.venv/bin/python` is selected. If it still fails, reload the VS Code window (`Cmd+Shift+P → Developer: Reload Window`).

### `uv run` says a command is not found

The entry point script may not have been installed yet. Run `uv sync` from the repo root to ensure all workspace packages and their entry points are registered in `.venv`.

### A service's `make test` still calls `poetry`

The per-service Makefile includes `scripts/services/python-service.mk`, which has been updated. If you see `poetry` being called, verify you have pulled the latest changes on this branch and that the Makefile's `include` path resolves correctly.

### Old `poetry.lock` files appearing in `git status`

The per-service `poetry.lock` files have been deleted in this branch. If they reappear, you may have an older branch checked out or a stale file not tracked by git. Remove them manually:

```bash
find . -mindepth 2 -name 'poetry.lock' -delete
```
