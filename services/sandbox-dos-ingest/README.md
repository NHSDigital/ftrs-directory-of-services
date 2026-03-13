# dos-ingest sandbox (canned responses)

## Overview

- A lightweight FastAPI app that serves the canned responses defined in `docs/specification/dos-ingest.yaml` for the
  Organization (FHIR resource) endpoints.
- Intended for APIM Sandbox usage to support example requests and responses without backend services.

## Endpoints (served by the container)

- GET /_status -> 200 (health check)
- GET /Organization
  - 200 success: `?identifier=https://fhir.nhs.uk/Id/ods-organization-code|ABC123`
  - 400 missing-identifier: (no identifier query parameter)
  - 400 missing-identifier-separator: `?identifier=ABC123`
  - 400 invalid-identifier-system: `?identifier=foo|ABC123`
  - 400 invalid-identifier-value: `?identifier=https://fhir.nhs.uk/Id/ods-organization-code|ABC@#`
  - 404 not-found: `?identifier=https://fhir.nhs.uk/Id/ods-organization-code|DEF456` (any other valid code)
  - 500 internal-server-error: `?identifier=https://fhir.nhs.uk/Id/ods-organization-code|GHI789`
- PUT /Organization/{id}
  - 200 success: PUT to `/Organization/04393ec4-198f-42dd-9507-f4fa5e9ebf96` (matches GET response)
  - 422 validation-error: PUT to `/Organization/trigger-422-validation-error`
  - 404 not-found: PUT to any other ID

## Quick start (local)

1. Navigate to the service directory (recommended)

```bash
# From the repository root
cd services/sandbox-dos-ingest
```

Or build from the repository root without changing directories:

```bash
# Run from the repository root
DOCKER_BUILDKIT=1 docker build -t dos-ingest:local services/sandbox-dos-ingest
```

1. Build (when inside `services/sandbox-dos-ingest`)

```bash
make build API_NAME=uec-dos-ingest
# or docker build -t dos-ingest:local .
```

1. Run

```bash
make unit-test # runs the container and smoke tests locally
# or run the container manually:
docker run --rm -p 9000:9000 dos-ingest:local
```

Tip: Add `-d` to run in detached mode so you can use the same terminal to run the curl commands below:

```bash
docker run --rm -d -p 9000:9000 dos-ingest:local
```

## Example curl commands

### 200 Success

```bash
curl -H "Accept: application/fhir+json" \
  "http://localhost:9000/Organization?identifier=https://fhir.nhs.uk/Id/ods-organization-code|ABC123"
```

### 400 Missing identifier parameter

```bash
curl -H "Accept: application/fhir+json" \
  "http://localhost:9000/Organization"
```

### 400 Missing identifier separator

```bash
curl -H "Accept: application/fhir+json" \
  "http://localhost:9000/Organization?identifier=ABC123"
```

### 400 Invalid identifier system

```bash
curl -H "Accept: application/fhir+json" \
  "http://localhost:9000/Organization?identifier=foo|ABC123"
```

### 400 Invalid identifier format

```bash
curl -H "Accept: application/fhir+json" \
  "http://localhost:9000/Organization?identifier=https://fhir.nhs.uk/Id/ods-organization-code|ABC%40%23"
```

### 404 Not Found

```bash
curl -H "Accept: application/fhir+json" \
  "http://localhost:9000/Organization?identifier=https://fhir.nhs.uk/Id/ods-organization-code|DEF456"
```

### PUT Organization (200 Success)

```bash
curl -X PUT \
  -H "Content-Type: application/fhir+json" \
  -H "Accept: application/fhir+json" \
  -d '{"resourceType": "Organization", "id": "04393ec4-198f-42dd-9507-f4fa5e9ebf96", "active": true, "name": "Test Org"}' \
  "http://localhost:9000/Organization/04393ec4-198f-42dd-9507-f4fa5e9ebf96"
```

### PUT Organization (422 Validation Error)

```bash
curl -X PUT \
  -H "Content-Type: application/fhir+json" \
  -H "Accept: application/fhir+json" \
  -d '{"resourceType": "Organization", "id": "trigger-422-validation-error", "active": true, "name": "Test Org"}' \
  "http://localhost:9000/Organization/trigger-422-validation-error"
```

### PUT Organization (404 Not Found)

```bash
curl -X PUT \
  -H "Content-Type: application/fhir+json" \
  -H "Accept: application/fhir+json" \
  -d '{"resourceType": "Organization", "id": "unknown-id", "active": true, "name": "Test Org"}' \
  "http://localhost:9000/Organization/unknown-id"
```

## Development

### Local development (without docker)

```bash
# Install dependencies
poetry install

# Run locally
poetry run uvicorn src.app.main:app --host 0.0.0.0 --port 9000 --reload
```

### Running tests

```bash
# Install dev dependencies
poetry install --with dev

# Run tests
poetry run pytest
```

## Pipeline deployment

This sandbox is deployed via the APIM sandbox deployment pipeline. To deploy:

1. Ensure your changes are merged to `main`
2. Create a tag in the format: `sandbox-dos-ingest-X.Y.Z` (e.g., `sandbox-dos-ingest-1.0.0`)
3. The pipeline will automatically build and deploy the sandbox image

Alternatively, for internal-dev-sandbox deployment:

- Use the tag format: `internal-dev-sandbox-dos-ingest-X.Y.Z`

## Canned responses

The canned responses are defined in [src/router/responses.py](src/router/responses.py) and align with the examples
in [docs/specification/dos-ingest.yaml](../../docs/specification/dos-ingest.yaml).

## Related documentation

- [DoS Ingest API Specification](../../docs/specification/dos-ingest.yaml)
- [APIM Sandbox Deployment Pipeline](.github/workflows/pipeline-deploy-sandbox.yaml)
