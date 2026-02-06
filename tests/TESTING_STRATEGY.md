# FTRS Directory of Services - Testing Strategy

This document provides a comprehensive overview of the testing approach for the FTRS Directory of Services project.

## Testing Philosophy

We follow a **testing pyramid** approach with three layers:

```asciidoc
                    ╭───────────────────╮
                   ╱                     ╲
                  ╱    AWS Smoke Tests    ╲      ← Fewer, slower, infrastructure verification
                 ╱       (7 scenarios)     ╲
                ╱─────────────────────────────╲
               ╱                               ╲
              ╱   LocalStack Integration Tests  ╲   ← Comprehensive business logic (114+ tests)
             ╱          (Docker-based)           ╲
            ╱─────────────────────────────────────╲
           ╱                                       ╲
          ╱         Per-Service Unit Tests          ╲  ← Fast, isolated, per-service
         ╱            (In each service)              ╲
        ╰─────────────────────────────────────────────╯
```

**Key Principles:**

- **Shift Left**: Catch bugs early with fast, local tests
- **LocalStack for Business Logic**: Test real AWS service interactions without AWS costs
- **AWS for Smoke Testing**: Verify infrastructure is correctly deployed, not business logic
- **Fast Feedback**: LocalStack tests run before deployment (~5-10 min vs ~20+ min)

---

## Test Categories

### 1. Unit Tests (Per-Service)

| Aspect          | Details                                      |
| --------------- | -------------------------------------------- |
| **Location**    | `services/<service-name>/tests/`             |
| **Framework**   | pytest                                       |
| **Run Command** | `make unit-test` (in each service directory) |
| **CI Trigger**  | Every push, runs in `build-project.yaml`     |
| **Duration**    | ~1-2 minutes per service                     |

**Services with unit tests:**

- `services/crud-apis/` - CRUD API handlers
- `services/data-migration/` - Data migration logic
- `services/dos-search/` - Search functionality
- `services/etl-ods/` - ETL processing
- `services/dos-ui/` - Frontend tests
- `services/read-only-viewer/` - Read-only viewer

---

### 2. LocalStack Integration Tests

| Aspect              | Details                                                        |
| ------------------- | -------------------------------------------------------------- |
| **Location**        | `tests/service_automation/tests/step_definitions/local_steps/` |
| **Framework**       | pytest + testcontainers + LocalStack                           |
| **Run Command**     | `make test-local-all` (in `tests/service_automation/`)         |
| **CI Trigger**      | Every push, runs in `local-integration-tests.yaml`             |
| **Duration**        | ~5-10 minutes                                                  |
| **AWS Required**    | No                                                             |
| **Docker Required** | Yes                                                            |

**What's Tested:**

```bash
tests/service_automation/tests/step_definitions/local_steps/
├── test_local_data_migration_s3_integration.py   # S3 & DynamoDB operations
├── test_local_crud_apis_integration.py           # Basic CRUD API tests
└── test_crud_apis_organization_comprehensive.py  # 114 comprehensive tests
```

**Comprehensive Test Coverage (CRUD APIs):**

| Test Class                 | Tests | What's Validated                          |
| -------------------------- | ----- | ----------------------------------------- |
| `TestBasicCrudOperations`  | 9     | Create, read, update, delete              |
| `TestNameSanitization`     | 12    | HTML/JS injection, Unicode, special chars |
| `TestRoleValidation`       | 12    | Valid/invalid organization roles          |
| `TestTelecomValidation`    | 16    | Phone, email, fax, URL formats            |
| `TestIdentifierValidation` | 12    | ODS codes, identifiers                    |
| `TestLegalDatesValidation` | 12    | Date formats, future dates, ranges        |
| `TestErrorHandling`        | 7     | HTTP errors, malformed requests           |
| `TestExtensionValidation`  | 10    | Active flags, extensions                  |
| `TestDatabaseConsistency`  | 24    | Concurrent operations, isolation          |

---

### 3. AWS Integration Tests (BDD Feature Files)

| Aspect           | Details                                    |
| ---------------- | ------------------------------------------ |
| **Location**     | `tests/service_automation/tests/features/` |
| **Framework**    | pytest-bdd (Gherkin syntax)                |
| **Run Command**  | `make test MARKERS="<tag>"`                |
| **CI Trigger**   | After successful deployment                |
| **Duration**     | ~10-20 minutes                             |
| **AWS Required** | Yes                                        |

**Feature Files by Category:**

```bash
tests/service_automation/tests/features/
├── crud_api_features/
│   └── organization_api.feature        # @crud-org-api @ftrs-pipeline @aws-smoke
├── data_migration_features/
│   ├── data_migration.feature          # @data-migration
│   └── data_migration_e2e.feature      # @data-migration-e2e
├── etl_ods_features/
│   ├── etl_ods_happy.feature           # @etl-ods @ftrs-pipeline
│   ├── etl_ods_mock.feature            # @etl-ods-mock @ftrs-pipeline
│   └── etl_ods_unhappy.feature         # @etl-ods @ftrs-pipeline
├── infra_features/
│   ├── s3.feature                      # @is-infra @ftrs-pipeline @is-s3
│   ├── data_repository.feature         # @is-infra @ftrs-pipeline @data-repo
│   └── dos-search-ods-code-lambda.feature  # @is-infra @ftrs-pipeline
└── is_api_features/
    └── dos_search_backend.feature      # @is-api @ftrs-pipeline
```

**Test Tags:**

| Tag               | Description                     | When Run         |
| ----------------- | ------------------------------- | ---------------- |
| `@ftrs-pipeline`  | Core pipeline tests             | Every deployment |
| `@data-migration` | Data migration tests            | Every deployment |
| `@aws-smoke`      | Infrastructure smoke tests only | After deployment |
| `@is-infra`       | Infrastructure verification     | After deployment |
| `@is-api`         | API endpoint tests              | After deployment |
| `@etl-ods`        | ETL ODS processing tests        | After deployment |
| `@ui`             | UI/Playwright tests             | After deployment |

---

## CI/CD Pipeline Flow

### Application Deployment Pipeline

```asciidoc
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         pipeline-deploy-application.yaml                        │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                            ┌─────────────────┐
                            │    metadata     │
                            └────────┬────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
              ▼                      ▼                      ▼
    ┌─────────────────┐   ┌──────────────────────┐   ┌───────────────┐
    │ quality-checks  │   │ local-integration-   │   │ build-services│
    │                 │   │ tests (LocalStack)   │   │               │
    │ • Linting       │   │                      │   │ • crud-apis   │
    │ • Formatting    │   │ • S3/DynamoDB tests  │   │ • data-migrate│
    │ • Security      │   │ • CRUD API tests     │   │ • dos-search  │
    │ • Terraform     │   │ • 114+ scenarios     │   │ • etc.        │
    └────────┬────────┘   └──────────┬───────────┘   └───────┬───────┘
             │                       │                       │
             └───────────────────────┼───────────────────────┘
                                     │
                                     ▼
                        ┌────────────────────────┐
                        │   prepare-toggle-      │
                        │   artifacts            │◄── Blocked until quality
                        └───────────┬────────────┘    checks AND local tests pass
                                    │
                                    ▼
                        ┌────────────────────────┐
                        │   deploy-application-  │
                        │   infrastructure       │
                        └───────────┬────────────┘
                                    │
                                    ▼
                        ┌────────────────────────┐
                        │   service-automation-  │
                        │   tests (AWS)          │
                        │                        │
                        │   Matrix:              │
                        │   • ftrs-pipeline      │◄── AWS smoke tests only
                        │   • data-migration     │
                        └────────────────────────┘
```

### Release Candidate Pipeline

```asciidoc
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          pipeline-build-release.yaml                            │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                            ┌─────────────────┐
                            │    metadata     │
                            └────────┬────────┘
                                     │
              ┌──────────────────────┴──────────────────────┐
              │                                             │
              ▼                                             ▼
    ┌─────────────────────┐                    ┌────────────────────┐
    │    tag-release      │                    │ local-integration- │
    │                     │                    │ tests (LocalStack) │
    │ • Semantic version  │                    │                    │
    │ • RC tag creation   │                    │ • Full test suite  │
    └─────────┬───────────┘                    └──────────┬─────────┘
              │                                           │
              └─────────────────────┬─────────────────────┘
                                    │
                                    ▼
                        ┌────────────────────────┐
                        │  promote-release-      │◄── Blocked until local
                        │  candidate             │    tests pass
                        └───────────┬────────────┘
                                    │
                                    ▼
                        ┌────────────────────────┐
                        │   Deploy to test       │
                        │   environment          │
                        └───────────┬────────────┘
                                    │
                                    ▼
                        ┌────────────────────────┐
                        │   service-automation-  │
                        │   tests (AWS)          │◄── Smoke tests on RC
                        └────────────────────────┘
```

---

## Running Tests Locally

### Prerequisites

```bash
# Docker must be running for LocalStack tests
docker --version

# Install dependencies
cd tests/service_automation
make install
```

### Quick Commands

```bash
# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                         LOCAL TESTS (No AWS)                               ║
# ╠════════════════════════════════════════════════════════════════════════════╣
# ║ Run all LocalStack tests                                                   ║
# ╚════════════════════════════════════════════════════════════════════════════╝
make test-local-all

# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                       SPECIFIC LOCAL TESTS                                 ║
# ╠════════════════════════════════════════════════════════════════════════════╣
# ║ S3/DynamoDB smoke tests                                                    ║
make test-local-smoke

# ║ Data migration with LocalStack                                             ║
make test-local-data-migration

# ║ CRUD APIs comprehensive (114 tests)                                        ║
make test-local-crud-apis-comprehensive

# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                         AWS TESTS (Requires deployment)                    ║
# ╠════════════════════════════════════════════════════════════════════════════╣
# ║ Set environment first                                                      ║
export ENVIRONMENT=dev
export WORKSPACE=dr-xxx  # Your feature branch workspace

# ║ Run specific test categories                                               ║
make test MARKERS="ftrs-pipeline"    # All pipeline tests
make test MARKERS="data-migration"   # Data migration tests
make test MARKERS="is-infra"         # Infrastructure tests
make test MARKERS="is-api"           # API tests
make test MARKERS="ui"               # UI/Playwright tests
```

---

## Test Reports

### Allure Reports

All tests generate Allure reports:

```bash
# Generate report after tests
make report

# View in browser
open allure-reports/index.html
```

### CI Artifacts

| Artifact            | Retention | Location                           |
| ------------------- | --------- | ---------------------------------- |
| LocalStack results  | 7 days    | `localstack-test-results` artifact |
| AWS test results    | 10 days   | `allure-report-<tag>` artifact     |
| S3 archived reports | Permanent | S3 artefacts bucket                |

---

## Adding New Tests

### LocalStack Tests (Recommended for business logic)

1. Create test file in `tests/step_definitions/local_steps/`
2. Use the `localstack_services` fixture for AWS resources
3. Add appropriate pytest markers

```python
import pytest

@pytest.mark.local
@pytest.mark.crud_apis_local_comprehensive
class TestMyNewFeature:
    def test_something(self, localstack_services):
        s3_client, dynamodb_resource, endpoint_url = localstack_services
        # Your test here
```

### AWS BDD Tests (For infrastructure verification)

1. Create/update feature file in `tests/features/`
2. Add appropriate tags (e.g., `@ftrs-pipeline`)
3. Implement step definitions in `tests/step_definitions/`

```gherkin
@my-feature @ftrs-pipeline
Feature: My Feature Smoke Test

  Scenario: Verify feature is deployed correctly
    Given the infrastructure is deployed
    When I call the feature endpoint
    Then the response status should be 200
```

---

## Troubleshooting

| Issue                           | Solution                                                      |
| ------------------------------- | ------------------------------------------------------------- |
| LocalStack tests hang           | Ensure Docker is running and has enough resources             |
| AWS tests fail with credentials | Run `aws sso login --profile <profile>`                       |
| Tests can't find workspace      | Check `WORKSPACE` and `ENVIRONMENT` are set                   |
| Allure report blank             | Run `make report` in the `tests/service_automation` directory |
| Python version mismatch         | Run `asdf install` to install correct Python version          |

---

## Related Documentation

- [Service Automation README](service_automation/README.MD) - Detailed test framework usage
- [Developer Guides](../docs/developer-guides/) - General development practices
- [CI/CD Workflows](../.github/workflows/) - GitHub Actions configuration
