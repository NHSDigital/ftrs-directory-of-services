# Per-endpoint Lambdas

This folder contains Lambda entrypoints for `dos-search`.

## Design goal

We want to keep the default pattern of **one Lambda per endpoint**, but also support a
**set of Lambdas behind an endpoint** when needed (for separation, scaling, or
future orchestration).

## Patterns supported

### 1) One Lambda per endpoint (default)

- API Gateway integrates directly with a single Lambda.

Examples:
- `GET /_status` -> `lambdas/status_get/handler.py`
- `GET /Organization` -> `functions/dos_search_ods_code_function.lambda_handler`

### 2) Set of Lambdas per endpoint (optional)

For endpoints that may grow in complexity, you can enable a stable *router* lambda
(API-facing) and one or more internal *worker* lambdas.

Example for `GET /Organization` (only when enabled):

- API Gateway -> `organization_get_router` (API-facing)
- router -> `organization_get_worker` (internal)
- (optional) router -> additional worker lambdas

Enabling is controlled at deploy-time via Terraform (`organization_use_internal_workers`).
At runtime, routing is controlled via environment variables.

- `DOS_SEARCH_ORCHESTRATION_MODE=inline|lambda` (default: `inline`)
- `DOS_SEARCH_ORG_WORKER_LAMBDA_NAMES=<comma-separated names>`

## Router+workers vs Step Functions

For multi-step implementations, we prefer:

- **Router + internal worker lambdas** for simple, synchronous request/response flows.
  This keeps API Gateway integration stable while allowing internal separation.

- **Step Functions** once the endpoint becomes a true workflow (retries, branching,
  long-running steps, fan-out/fan-in). Step Functions provides better visibility
  and declarative error handling at the cost of extra infrastructure.

## Folder layout

- `lambdas/organization_get_router/handler.py`
- `lambdas/organization_get_worker/handler.py`
- `lambdas/status_get/handler.py`

Shared business logic remains in `functions/` and `health_check/`.
