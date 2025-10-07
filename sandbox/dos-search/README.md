# dos-search sandbox (canned responses)

## Overview

- A lightweight FastAPI app that serves the canned responses defined in `docs/specification/dos-search-sandbox.yaml` for the
  Organization search endpoint.
- Intended for APIM Sandbox usage to support example requests and responses without backend services.

## Endpoints (served by the container)

- GET /_status -> 200 (health check)
- GET /Organization
  - 200 example: `?identifier=odsOrganisationCode|ABC123&_revinclude=Endpoint:organization`
  - 400 invalid-identifier-value: `?identifier=odsOrganisationCode|ABC&_revinclude=Endpoint:organization`
  - 400 missing-revinclude: `?identifier=odsOrganisationCode|ABC123`
  - 400 invalid-identifier-system: `?identifier=foo|ABC123&_revinclude=Endpoint:organization`

## Quick start (local)

1. Build

```bash
docker build -t dos-search:local .
```

1. Run

```bash
docker run --rm -p 9000:9000 dos-search:local
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

## Expected sandbox requests (via APIM)

```bash
# 200 example
GET https://sandbox.api.service.nhs.uk/dos-search/FHIR/R4/Organization?identifier=odsOrganisationCode|ABC123&_revinclude=Endpoint:organization

# 400 invalid-identifier-value
GET https://sandbox.api.service.nhs.uk/dos-search/FHIR/R4/Organization?identifier=odsOrganisationCode|ABC&_revinclude=Endpoint:organization

# 400 missing-revinclude
GET https://sandbox.api.service.nhs.uk/dos-search/FHIR/R4/Organization?identifier=odsOrganisationCode|ABC123

# 400 invalid-identifier-system
GET https://sandbox.api.service.nhs.uk/dos-search/FHIR/R4/Organization?identifier=foo|ABC123&_revinclude=Endpoint:organization
```

## Notes

- Authentication/authorisation errors (401/403) and server errors (500) are intentionally not generated in sandbox as
  per the specification notes.
- Media type is application/fhir+json for all responses.
