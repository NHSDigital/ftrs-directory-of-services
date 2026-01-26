# dos-search sandbox (canned responses)

## Overview

- A lightweight FastAPI app that serves the canned responses defined in `docs/specification/dos-search.yaml` for the
  Organization (FHIR resource) search endpoint.
- Intended for APIM Sandbox usage to support example requests and responses without backend services.

## Corporate proxy / TLS interception note (Docker builds)

If you're on a network that intercepts TLS (for example, Zscaler), `docker build` may fail during `pip` installs with:

- `SSLCertVerificationError: unable to get local issuer certificate`

This Dockerfile supports two build modes:

- **Default (no corporate CA)**: suitable for non-intercepting networks
- **Opt-in corporate CA**: installs a provided CA bundle into the container trust store

### Default build (no corporate CA)

```bash
cd services/sandbox-dos-search
docker build -t dos-search:local .
```

### Corporate CA build (Zscaler / TLS interception)

1) Copy your corporate root CA bundle PEM into the Docker build context (this folder).

Use any filename you like (example uses `corp-proxy-ca.pem`):

```bash
cd services/sandbox-dos-search
cp -f ../../your-corp-ca.pem ./corp-proxy-ca.pem
```

2) Build the corporate-CA target:

```bash
docker build --target runtime-with-corp-ca -t dos-search:local .
```

Note: if your CA bundle has a different filename, pass it via `--build-arg CORP_CA_PEM=...`.

```bash
docker build --target runtime-with-corp-ca --build-arg CORP_CA_PEM=my-ca.pem -t dos-search:local .
```

## Endpoints (served by the container)

- GET /_status -> 200 (health check)
- GET /_ping -> 200 (liveness)
- GET /Organization
  - 200 example: `?identifier=odsOrganisationCode|ABC123&_revinclude=Endpoint:organization`
  - 400 invalid-identifier-value: `?identifier=odsOrganisationCode|ABC&_revinclude=Endpoint:organization`
  - 400 missing-revinclude: `?identifier=odsOrganisationCode|ABC123`
  - 400 invalid-identifier-system: `?identifier=foo|ABC123&_revinclude=Endpoint:organization`

## Quick start (local)

1. Navigate to the service directory (recommended)

```bash
# From the repository root
cd services/sandbox-dos-search
```

1. Build

```bash
docker build -t dos-search:local .
```

Or build from the repository root without changing directories:

```bash
DOCKER_BUILDKIT=1 docker build -t dos-search:local services/sandbox-dos-search
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
# 200 status
curl -i "http://localhost:9000/_status"

# 200 ping
curl -i "http://localhost:9000/_ping"

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
# From the services/sandbox-dos-search directory
BASE_URL=http://localhost:9000 ./scripts/smoke.sh
```

## Using Podman (alternative to Docker)

You can use Podman with equivalent commands.

- Build from the service directory:

```bash
# From the repository root
cd services/sandbox-dos-search
podman build -t dos-search:local .
```

- Or build from the repository root without changing directories:

```bash
podman build -t dos-search:local services/sandbox-dos-search
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
# From the services/sandbox-dos-search directory
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
# 200 status
curl --location 'https://sandbox.api.service.nhs.uk/dos-search/FHIR/R4/_status'

# 200 ping
curl --location 'https://sandbox.api.service.nhs.uk/dos-search/FHIR/R4/_ping'

# 200 example
curl --location 'https://sandbox.api.service.nhs.uk/dos-search/FHIR/R4/Organization?identifier=odsOrganisationCode|ABC123&_revinclude=Endpoint:organization'

# 400 invalid-identifier-value
curl --location 'https://sandbox.api.service.nhs.uk/dos-search/FHIR/R4/Organization?identifier=odsOrganisationCode|ABC&_revinclude=Endpoint:organization'

# 400 missing-revinclude
curl --location 'https://sandbox.api.service.nhs.uk/dos-search/FHIR/R4/Organization?identifier=odsOrganisationCode|ABC123'

# 400 invalid-identifier-system
curl --location 'https://sandbox.api.service.nhs.uk/dos-search/FHIR/R4/Organization?identifier=foo|ABC123&_revinclude=Endpoint:organization'
```

## Notes

- Authentication/authorisation errors (401/403) and server errors (500) are intentionally not generated in sandbox as
  per the specification notes.
- Media type is application/fhir+json for all responses.
