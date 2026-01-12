# Per-endpoint Lambdas

This folder demonstrates the **"one Lambda per endpoint"** approach for `dos-search`.

## What problem this solves

Historically, multiple endpoints could be shipped in a single Lambda zip. That couples deployment:
changing one endpoint redeploys all of them.

With this approach:

- each endpoint gets its **own Lambda handler entrypoint**
- each endpoint gets its **own zip artifact**
- Terraform can point each AWS Lambda at a **different S3 key**

## Endpoints implemented (example)

- `lambdas/organization_get/handler.py`: entrypoint for `GET /Organization`
- `lambdas/status_get/handler.py`: entrypoint for `GET /_status`

## How the code is structured

- `lambdas/**` contains **thin entrypoints** only (wiring: logging/tracing + router inclusion)
- shared business logic remains in:
  - `functions/` (main endpoint logic and shared helpers)
  - `health_check/` (health check route)

The entrypoints use Powertools' `APIGatewayRestResolver` and mount shared routers via:

- `app.include_router(...)`

This keeps endpoint handler files small and consistent.

## Handler naming convention

Each endpoint lives in its own folder:

- `lambdas/<endpoint_name>/handler.py`
- exported handler function: `lambda_handler`

For this spike we use:

- `organization_get` (resource `Organization`, method `GET`)
- `status_get` (path `_status`, method `GET`)

## Deployment artifact naming

The packaging script creates separate Lambda zip files for each endpoint.

Current names (see `scripts/package_endpoint_lambdas.py`):

- `ftrs-dos-dos-search-organization-get-lambda-<application_tag>.zip`
- `ftrs-dos-dos-search-status-get-lambda-<application_tag>.zip`

> Note: Third-party dependencies are provided via the existing dependency layer.
> These endpoint zips include only handler + shared service code.

## Terraform wiring (dos_search stack)

The `dos_search` Terraform stack is configured to point each Lambda at a separate handler and S3 key.

- `/Organization` Lambda:
  - handler: `lambdas/organization_get/handler.lambda_handler`
  - S3 key includes: `...-organization-get-lambda-<application_tag>.zip`

- `/_status` Lambda:
  - handler: `lambdas/status_get/handler.lambda_handler`
  - S3 key includes: `...-status-get-lambda-<application_tag>.zip`

## Local build (zip artifacts)

From `services/dos-search` you can build the endpoint zips into the normal build output directory:

```zsh
make build-endpoint-lambdas APPLICATION_TAG=local
```

Or run the script directly:

```zsh
poetry run python scripts/package_endpoint_lambdas.py \
  --out ../../build/services/dos-search \
  --application-tag local
```

## Adding a new endpoint

1. Create a new folder under `lambdas/`, e.g. `lambdas/some_new_endpoint_get/handler.py`.
2. In the handler, create a resolver and `include_router()` for your shared router.
3. Update `scripts/package_endpoint_lambdas.py` to add a new entry so it builds a new zip.
4. Add a new Lambda module in the `dos_search` Terraform stack pointing to:
   - the new handler string
   - the new per-endpoint S3 key
5. Add an API Gateway integration to invoke the new Lambda.

## Testing

Unit tests live under `tests/unit` and still run at the service level (shared code + handlers).

```zsh
poetry run pytest tests/unit
```
