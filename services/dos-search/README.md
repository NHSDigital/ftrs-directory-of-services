# Directory of Services Search API

This service provides FHIR-compliant API endpoints for healthcare system integrations.

## Endpoints

### `/Organization`

The Organization endpoint retrieves healthcare organization endpoints from a DynamoDB database based on ODS (Organization Data Service) codes and returns them in a FHIR-compliant Bundle format. This allows healthcare systems to discover electronic communication endpoints for specific organizations.

Key capabilities:

- Retrieval of organization and endpoint data by ODS code
- Mapping of DynamoDB records to FHIR resources (Organization, Endpoint)
- Combining related resources into a FHIR Bundle
- Error handling with FHIR OperationOutcome responses

## Architecture

The service uses:

- **AWS Lambda** for serverless execution
- **DynamoDB** for data storage
- **FHIR R4 resources** for healthcare data representation
- **Pydantic** for data validation and serialization
- **AWS Lambda Powertools** for logging and utilities

## Prerequisites

- [asdf](https://asdf-vm.com/) for runtime version management
- Access to appropriate AWS services
- You have read and followed the root `README.md` for first steps

## Getting Started

### Initial Setup

1. Clone the repository

   ```shell
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install all dependencies

   ```shell
   # From root directory
   make config

   # Then in the service directory
   cd services/dos-search
   make config
   ```

### Environment Configuration

1. Create an environment file by copying the template

   ```shell
   cp .env.sample .env
   ```

2. Fill in required values in the `.env` file

3. Activate environment variables

   ```shell
   export $(cat .env | xargs)
   ```

## Development

### Code Structure

```plain
├── src/
│   ├── common/                         # Shared code and utilities
│   │   ├── fhir_mapper/                # FHIR resource mapping
│   │   ├── model/                      # Data models and validation
│   │   └── error_util.py               # Error handling
│   ├── health_check/                   # /_status endpoint
│   │   └── handler.py
│   └── organization/                   # /Organization endpoint
│       ├── handler.py
│       └── service.py
├── tests/
│   └── unit/                           # Unit tests
├── tools/
│   └── manual_test_organization.py     # Local testing script
└── ...                                 # Configuration files
```

### Testing

#### Unit Testing

```shell
# Run all tests with coverage report
make test

# Run specific test file
poetry run pytest tests/unit/src/organization/test_service.py
```

#### Manual Testing

Use the `manual_test_organization.py` script to test the Lambda function locally:

```shell
PYTHONPATH=$(git rev-parse --show-toplevel)/services/dos-search poetry run python tools/manual_test_organization.py
```

This will use the ODS_CODE from your environment variables to make a test request.

### Linting and Formatting

The project uses [ruff](https://github.com/charliermarsh/ruff) for linting and formatting.

```shell
# Check for linting and formatting issues
make lint

# Attempt to fix linting and formatting issues
make lint-fix
```

IDE Integration: Configure your IDE to use ruff for linting and formatting. See [ruff documentation](https://docs.astral.sh/ruff/editors/setup/) for details.

### Pre-commit Hooks

Pre-commit hooks are set up to automatically run linting and formatting checks before each commit.

```shell
# Pre-commit hooks will run automatically on commit
git commit

# To manually run pre-commit hooks
pre-commit run --all-files -c $(git rev-parse --show-toplevel)/scripts/config/pre-commit.yaml
```

## Deployment

Push your latest changes to the repository.
The GitHub Actions workflow will automatically build the Lambda function packages and dependency layers, perform tests, and deploy onto the development environment.

To manually test the build process, from `services/dos-search`:

```shell
# Build per-endpoint artefacts into the build dir
make build

# Publish (example; CI normally does this)
make publish APPLICATION_TAG=test-tag
```

## Contributing

1. Set up development environment as described in [Getting Started](#getting-started)
2. Make code changes
3. Add tests for new functionality
4. Ensure all tests pass with `make test`
5. Check for linting/formatting issues with `make lint`
6. Create a pull request with your changes
7. Ensure GitHub Actions pass

## Dependency Management

Update dependencies:

```shell
# Update lock file with changes from pyproject.toml
poetry lock --no-update

# Update all dependencies to latest versions
poetry lock

# Update poetry environment with lock file changes
poetry install

# Update poetry environment with lock file changes, removing unused dependencies
poetry sync
```

## Troubleshooting

### Common Issues

1. **Missing environment variables**
   - Ensure all required environment variables are set in `.env` and exported

2. **AWS connectivity issues**
   - Verify AWS credentials are properly configured
   - Re-assume the correct AWS profile if necessary

     ```shell
     assume <role-name>
     ```
