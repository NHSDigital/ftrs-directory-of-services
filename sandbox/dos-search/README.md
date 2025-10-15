# dos-search sandbox (canned responses)

## Overview

- A lightweight FastAPI app that serves the canned responses defined in `docs/specification/dos-search-sandbox.yaml` for the
  Organization (FHIR resource) search endpoint.
- Intended for APIM Sandbox usage to support example requests and responses without backend services.

## Endpoints (served by the container)

- GET /_status -> 200 (health check)
- GET /Organization
  - 200 example: `?identifier=odsOrganisationCode|ABC123&_revinclude=Endpoint:organization`
  - 400 invalid-identifier-value: `?identifier=odsOrganisationCode|ABC&_revinclude=Endpoint:organization`
  - 400 missing-revinclude: `?identifier=odsOrganisationCode|ABC123`
  - 400 invalid-identifier-system: `?identifier=foo|ABC123&_revinclude=Endpoint:organization`

## Quick start (local)

1. Navigate to the service directory (recommended)

```bash
# From the repository root
cd sandbox/dos-search
```

Or build from the repository root without changing directories:

```bash
# Run from the repository root
docker build -t dos-search:local sandbox/dos-search
```

1. Build (when inside `sandbox/dos-search`)

```bash
docker build -t dos-search:local .
```

1. Run

```bash
docker run --rm -p 9000:9000 dos-search:local
```

Tip: Add `-d` to run in detached mode so you can use the same terminal to run the curl commands below:

```bash
docker run -d --rm -p 9000:9000 dos-search:local
```

1. Try it

```bash
# 200 success
curl -i -H "Accept: application/fhir+json" \
  "http://localhost:9000/Organization?identifier=odsOrganisationCode|ABC123&_revinclude=Endpoint:organization"

# 400 invalid-identifier-value
curl -i -H "Accept: application/fhir+json" \
  "http://localhost:9000/Organization?identifier=odsOrganisationCode|ABC&_revinclude=Endpoint:organization"

# 400 missing-revinclude
curl -i -H "Accept: application/fhir+json" \
  "http://localhost:9000/Organization?identifier=odsOrganisationCode|ABC123"

# 400 invalid-identifier-system
curl -i -H "Accept: application/fhir+json" \
  "http://localhost:9000/Organization?identifier=foo|ABC123&_revinclude=Endpoint:organization"
```

1. Run smoke tests (optional)

```bash
# From the sandbox/dos-search directory
test -x scripts/smoke.sh || chmod +x scripts/smoke.sh
BASE_URL=http://localhost:9000 ./scripts/smoke.sh
```

## Using Podman (alternative to Docker)

You can use Podman with equivalent commands.

- Build from the service directory:

```bash
# From the repository root
cd sandbox/dos-search
podman build -t dos-search:local .
```

- Or build from the repository root without changing directories:

```bash
podman build -t dos-search:local sandbox/dos-search
```

- Run the container:

```bash
podman run --rm -p 9000:9000 dos-search:local
```

Tip: Add `-d` to run in detached mode so you can use the same terminal to run the curl commands below:

```bash
podman run -d --rm -p 9000:9000 dos-search:local
```

- Smoke test (optional):

```bash
# From the sandbox/dos-search directory
BASE_URL=http://localhost:9000 ./scripts/smoke.sh
```

Note for macOS and Windows users (non-Linux hosts):

On macOS and Windows, Podman runs containers inside a lightweight Linux VM, so you need to ensure the Podman machine is running. On Linux hosts, you can skip this step.

```bash
# First-time setup (only once)
podman machine init

# Start the Podman machine (per session)
podman machine start
```

## Expected sandbox requests (via APIM)

```bash
# 200 example
curl --location 'https://sandbox.api.service.nhs.uk/dos-search/FHIR/R4//Organization?identifier=odsOrganisationCode|ABC123&_revinclude=Endpoint:organization'

# 400 invalid-identifier-value
curl --location 'https://sandbox.api.service.nhs.uk/dos-search/FHIR/R4/Organization?identifier=odsOrganisationCode|ABC&_revinclude=Endpoint:organization'

# 400 missing-revinclude
curl --location 'https://sandbox.api.service.nhs.uk/dos-search/FHIR/R4//Organization?identifier=odsOrganisationCode|ABC123'

# 400 invalid-identifier-system
curl --location 'https://sandbox.api.service.nhs.uk/dos-search/FHIR/R4//Organization?identifier=foo|ABC123&_revinclude=Endpoint:organization'
```

## Notes

- Authentication/authorisation errors (401/403) and server errors (500) are intentionally not generated in sandbox as
  per the specification notes.
- Media type is application/fhir+json for all responses.
