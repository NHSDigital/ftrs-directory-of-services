# Per-endpoint Lambdas

This folder contains Lambda entrypoints for `dos-search`.

`dos-search` now standardises on `functions/<lambda_name>/handler.py` for endpoint lambdas.

Lambda ZIP artefacts are built by `scripts/package_endpoint_lambdas.py`.

The only remaining handler under `lambdas/` is the `_status` endpoint:

- `GET /_status` -> `lambdas/status_get/handler.py`
