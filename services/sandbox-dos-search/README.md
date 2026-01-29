# dos-search sandbox (canned responses)

## Overview

- A lightweight FastAPI app that serves the canned responses defined in `docs/specification/dos-search.yaml` for the
  `Organization` (a FHIR resource) search endpoint.
- Intended for APIM Sandbox usage; provides example requests and responses without backend services.

## Endpoints (served by the container)

- `GET /_status` — 200 (health check)
- `GET /_ping` — 200 (health check)
- `GET /Organization`
  - 200 example: `?identifier=odsOrganisationCode|ABC123&_revinclude=Endpoint:organization`
  - 400 invalid identifier value: `?identifier=odsOrganisationCode|ABC&_revinclude=Endpoint:organization`
  - 400 missing `_revinclude`: `?identifier=odsOrganisationCode|ABC123`
  - 400 invalid identifier system: `?identifier=foo|ABC123&_revinclude=Endpoint:organization`

## Quick start (local)

1. From the repository root, change into the service directory:

```bash
cd services/sandbox-dos-search
```

Alternatively, build from the repository root without changing directories:

```bash
DOCKER_BUILDKIT=1 docker build -t dos-search:local services/sandbox-dos-search
```

Build (when inside `services/sandbox-dos-search`):

```bash
docker build -t dos-search:local .
```

Run the service locally:

```bash
# Run the container (foreground)
docker run --rm -p 9000:9000 dos-search:local

# Or run in detached mode
docker run -d --rm -p 9000:9000 dos-search:local
```

## Try it

```bash
# /_status: 200 (empty response)
curl -i -H "Accept: application/fhir+json" \
  "http://localhost:9000/_status"

# /_ping: 200 (empty response)
curl -i -H "Accept: application/fhir+json" \
  "http://localhost:9000/_ping"

# Organization search — success (200)
curl -i -H "Accept: application/fhir+json" \
  "http://localhost:9000/Organization?identifier=odsOrganisationCode|ABC123&_revinclude=Endpoint:organization"

# Organization search — invalid identifier value (400)
curl -i -H "Accept: application/fhir+json" \
  "http://localhost:9000/Organization?identifier=odsOrganisationCode|ABC&_revinclude=Endpoint:organization"

# Organization search — missing _revinclude (400)
curl -i -H "Accept: application/fhir+json" \
  "http://localhost:9000/Organization?identifier=odsOrganisationCode|ABC123"

# Organization search — invalid identifier system (400)
curl -i -H "Accept: application/fhir+json" \
  "http://localhost:9000/Organization?identifier=foo|ABC123&_revinclude=Endpoint:organization"
```

1. Run smoke tests (optional)

```bash
# From the services/dos-search/sandbox directory
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
# From the services/dos-search/sandbox directory
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
# 200 status healthcheck
curl --location 'https://sandbox.api.service.nhs.uk/dos-search/_status'

# 200 ping healthcheck
curl --location 'https://sandbox.api.service.nhs.uk/dos-search/_ping'

# 200 example (Organization search)
curl --location 'https://sandbox.api.service.nhs.uk/dos-search/FHIR/R4/Organization?identifier=odsOrganisationCode|ABC123&_revinclude=Endpoint:organization'

# 400 invalid-identifier-value
curl --location 'https://sandbox.api.service.nhs.uk/dos-search/FHIR/R4/Organization?identifier=odsOrganisationCode|ABC&_revinclude=Endpoint:organization'

# 400 missing-revinclude
curl --location 'https://sandbox.api.service.nhs.uk/dos-search/FHIR/R4/Organization?identifier=odsOrganisationCode|ABC123'

# 400 invalid-identifier-system
curl --location 'https://sandbox.api.service.nhs.uk/dos-search/FHIR/R4/Organization?identifier=foo|ABC123&_revinclude=Endpoint:organization'
```

## Behind a corporate proxy (Zscaler) — `Dockerfile` snippet

If you're building Docker images behind a corporate TLS-inspecting proxy (e.g., Zscaler), add the proxy's CA certificate to the image and update Python's certificate store so that `pip` and the `requests` library (via `certifi`) trust it.

Add the following to your `Dockerfile` (Debian/Ubuntu-based images):

```dockerfile
# Add corporate CA cert and ensure Python/pip/certifi use it
COPY cert.pem /usr/local/share/ca-certificates/cert.pem
ENV PIP_CERT="/usr/local/share/ca-certificates/cert.pem"
RUN update-ca-certificates \
    && pip install --upgrade certifi \
    && cat /usr/local/share/ca-certificates/cert.pem >> "$(python -c 'import certifi; print(certifi.where())')"
```

Notes and alternatives:

- Ensure `cert.pem` is available during `docker build`.

- The `cat` command appends your certificate to the Python CA bundle used by the `requests` library (this is preferable to specifying a hard‑coded path such as `/usr/local/lib/python3.12/site-packages/certifi/cacert.pem`, which can vary). The command uses Python to locate the correct bundle at build time.

- You can also set additional environment variables (optional) to help other tools pick up the custom bundle:

```dockerfile
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```

- If your base image uses a different CA store location (Alpine, etc.), adjust the path and `update-ca-certificates` step accordingly.
