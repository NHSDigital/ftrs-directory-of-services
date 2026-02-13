# Find the Right Service

[![CI/CD Pull Request](https://github.com/nhs-england-tools/repository-template/actions/workflows/cicd-1-pull-request.yaml/badge.svg)](https://github.com/nhs-england-tools/repository-template/actions/workflows/cicd-1-pull-request.yaml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=repository-template&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=repository-template)

Find the Right Service (FtRS) helps direct patients to the most appropriate NHS service for their urgent care needs. The system is commissioned, developed, and hosted by NHS England.

## Table of Contents

- [Overview](#overview)
- [Key Components](#key-components)
- [Repository Structure](#repository-structure)
- [Technologies](#technologies)
- [Setup](#setup)
- [Contributing](#contributing)
- [Testing](#testing)
- [License](#license)

## Overview

FtRS provides a comprehensive platform for managing and searching healthcare service information across the NHS. The system enables healthcare professionals and patients to quickly find appropriate care services based on clinical need, location, and availability.

## Key Components

### Directory of Services (DoS)

The DoS maintains comprehensive data for healthcare services across:

- Urgent and Emergency care
- Primary care services
- Secondary and Tertiary care

Each service record includes location, availability, and treatment/care details. Data is maintained through an admin interface and APIs.

### Search APIs

FHIR-compliant APIs that interrogate the DoS to find clinically appropriate services. The primary use case is triage search supporting 111 and 999 call handlers in directing patients to the right care.

### Data Sourcing

Automated ingestion of service data from third-party sources where clinically safe and appropriate, reducing manual data entry and improving data accuracy.

## Repository Structure

```text
ftrs-directory-of-services/
├── infrastructure/    # Terraform IaC for AWS resources
├── services/          # Application services and APIs
├── scripts/           # Build, deployment, and utility scripts
├── tests/             # Integration and performance tests
└── docs/              # Additional documentation
```

### Services

Application services organised by function:

- **crud-apis**: Internal APIs for data management
- **data-migration**: Migration tooling from legacy DoS
- **dos-search**: FHIR-compliant search API
- **dos-ui**: React-based user interface
- **etl-ods**: ETL pipeline for ODS data
- **read-only-viewer**: Database testing utility
- **sandbox-dos-search**: Mock API for testing
- **slack-notifier**: CloudWatch alarm notifications

[View services documentation](services/README.md)

### Infrastructure

Terraform infrastructure as code:

- **stacks**: Deployable infrastructure components
- **modules**: Reusable Terraform modules
- **environments**: Environment-specific configurations

[View infrastructure documentation](infrastructure/README.md)

## Technologies

- **Infrastructure**: Terraform, AWS (Lambda, DynamoDB, OpenSearch, API Gateway)
- **Backend**: Python 3.12+, Poetry
- **Frontend**: React, TypeScript, TanStack Router
- **Containers**: Docker, Podman
- **CI/CD**: GitHub Actions

## Setup

### Prerequisites

Required software:

- [Docker](https://www.docker.com/) or [Podman](https://podman.io/)
- [asdf](https://asdf-vm.com/) version manager ([configured for your shell](https://asdf-vm.com/guide/getting-started.html#_2-configure-asdf))
- [GNU make](https://www.gnu.org/software/make/) 3.82 or later
- [Python](https://www.python.org/) for Git hooks
- [`jq`](https://jqlang.github.io/jq/) for JSON processing

**macOS users**:

- [Homebrew](https://brew.sh/) for package management
- [GNU sed](https://www.gnu.org/software/sed/), [GNU grep](https://www.gnu.org/software/grep/), [GNU coreutils](https://www.gnu.org/software/coreutils/), [GNU binutils](https://www.gnu.org/software/binutils/)

> [!NOTE]
> macOS ships with GNU make < 3.82. Install via Homebrew:
>
> ```shell
> brew install make
> ```
>
> Then update your `$PATH` as instructed. The [dotfiles](https://github.com/nhs-england-tools/dotfiles) project automates this setup.

### Installation

1. Clone the repository:

   ```shell
   git clone https://github.com/NHSDigital/ftrs-directory-of-services.git
   cd ftrs-directory-of-services
   ```

2. Install toolchain dependencies:

   ```shell
   make configuration
   ```

3. Configure Git commit signing:

   ```shell
   git config --global commit.gpgsign true
   ```

4. Set up Git hooks:

   ```shell
   pre-commit install --configuration scripts/configuration/pre-commit.yaml --install-hooks
   make githooks-commit-msg
   ```

   > [!NOTE]
   > If `make githooks-configuration` doesn't work, run the commands above directly (from `scripts/init.mk` lines 34-37).

### Service-Specific Setup

Each service has its own setup requirements. See individual service READMEs:

- [DoS Search setup](services/dos-search/README.md#getting-started)
- [DoS UI setup](services/dos-ui/README.md#getting-started)
- [Data Migration setup](services/data-migration/README.md)
- [ETL ODS setup](services/etl-ods/README.md#installation)

## Contributing

### Branch Naming Convention

**Format**: `{type}/{JIRA-REF}_{description}`

**Components**:

- **type**: `task` or `hotfix`
- **JIRA-REF**: Jira ticket identifier (e.g., `XXX-123`)
- **description**: 10-45 alphanumeric characters, hyphens, or underscores

**Valid examples**:

- `task/XXX-123_My_valid_branch_name`
- `task/XXX-123-My-valid-branch-name`
- `hotfix/XXX-456_Fix_critical_bug`

**Invalid examples**:

- `XXX-123_My_branch` (missing type)
- `task/MyBranchName` (missing JIRA reference)
- `task/XXX-123MyBranch` (missing separator)

### Commit Message Convention

Commit messages must:

- Start with a valid type: `feat`, `fix`, `chore`, `docs`, `style`, `refactor`, `test`
- Include a Jira reference (auto-inserted from branch name if missing)
- Contain at least three words
- Not exceed 100 characters

**Example**: `feat: XXX-123 Add search endpoint for organisation lookup`

### Workflow

1. Create a branch following the naming convention
2. Make changes and commit with descriptive messages
3. Ensure tests pass: `make test`
4. Push and create a pull request
5. Address review feedback
6. Merge after approval

## Testing

Integration and performance tests are located in `tests/` with individual READMEs for each test suite.

**Run tests for a specific service**:

```shell
cd services/{service-name}
make test
```

**Common test commands**:

```shell
make test          # Run all tests
make test-unit     # Run unit tests only
make test-coverage # Generate coverage report
make lint          # Run linting
```

## License

> The [LICENCE.md](./LICENCE.md) file will need to be updated with the correct year and owner

Unless stated otherwise, the codebase is released under the MIT License. This covers both the codebase and any sample code in the documentation.

Any HTML or Markdown documentation is [© Crown Copyright](https://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/uk-government-licensing-framework/crown-copyright/) and available under the terms of the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
