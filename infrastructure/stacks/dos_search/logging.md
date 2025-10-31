# Logging standards for `dos_search` Terraform stack

## Purpose

This document describes the CloudWatch logging configuration for the `gp_search` stack: where retention is configured, the naming convention for log groups, how API Gateway access logs are created now (behaviour of the HTTP API / api-gateway-v2 module), how to verify logging, and how to change retention per environment.

## Naming convention

We standardise CloudWatch log group names using the pattern:

/aw s/{AWS_RESOURCE}/{PROJECT}-{ENV}-{STACK}-{RESOURCE_NAME}

Examples:

- API Gateway access logs: /aws/apigateway/ftrs-dos-dev-gp_search-api-gateway
- Lambda functions: /aws/lambda/ftrs-dos-dev-gp_search-<lambda-name>

## Notes

- Lambda log group names are created automatically by the Lambda service from the Lambda function name. The project uses the function-name pattern `${local.resource_prefix}-${var.lambda_name}`, so the resulting log group will follow the standardised naming (unless an explicit `logging_log_group` is provided).

- API Gateway (HTTP API / api-gateway-v2) access logs for the `gp_search` stack are created and managed by the API Gateway module used by this stack. The stack supplies the access-log name and retention; the module configures stage access logging via its `stage_access_log_settings` and will create the CloudWatch log group when requested.

## How `gp_search` configures API Gateway access logs (current behaviour)

- The `gp_search` stack computes the API name and log-group name in `api-gateway.tf`:

  - `local.api_name` = "${local.resource_prefix}-api-gateway${local.workspace_suffix != "" ? local.workspace_suffix : ""}"
  - `local.api_log_group` = "/aws/apigateway/${local.api_name}"

- The stack passes the log-group name and retention to the API Gateway module invocation. In this stack those inputs are:

  - `api_gateway_access_logs_log_group_name` (log group name)
  - `api_gateway_access_logs_retention_days` (retention in days)

  The module maps those inputs into its `stage_access_log_settings` (for example: `log_group_name` and `log_group_retention_in_days`) and, when configured to do so, will create the `aws_cloudwatch_log_group` for the stage and set the configured retention.

- In short: `gp_search` uses the module-level pattern — the APIGW module (wrapper) creates and manages the API Gateway access log group and its retention.

## Parameterisation

The stack exposes variables and passes module inputs to parameterise logging behaviour (see `variables.tf` and `api-gateway.tf` in the stack):

- Stack variable: `api_gateway_access_logs_retention_days` (number) — retention for API Gateway access logs (declared in `variables.tf`).
- Module input (computed in the stack and passed into the module): `api_gateway_access_logs_log_group_name` (string) — the computed CloudWatch log group name for API Gateway access logs (set to `local.api_log_group` in `api-gateway.tf`).
- Stack variables: `lambda_cloudwatch_logs_retention_days` (number) — retention for main search Lambda logs; and `health_check_lambda_cloudwatch_logs_retention_days` (number) — retention for health-check Lambda logs.

## Where retention lives

- Per-environment retention values live in environment-specific tfvars under `infrastructure/environments/<env>/gp_search.tfvars` (for example, `infrastructure/environments/dev/gp_search.tfvars`).

- Keep environment-specific configuration in the environment tfvars. The stack's `variables.tf` contains the variables and defaults; set per-environment values in the environment tfvars.

## How logging is wired (two supported patterns)

1) **Module-level pattern** (recommended and currently used by `gp_search`):

   - The stack passes the desired log-group name and retention into the APIGW module invocation (the wrapper/module sets `stage_access_log_settings` accordingly).
   - The module creates and manages the CloudWatch log group with the requested name and retention.
   - Benefits: a single place that enforces naming and retention for all stacks; easier to maintain and to attach subscriptions or cross-account access.

2) **Stack-level pattern** (also supported):

   - The stack creates an `aws_cloudwatch_log_group` resource itself and passes the log group's ARN into the module via `stage_access_log_settings.destination_arn` with `create_log_group = false`.
   - Benefits: the stack fully controls naming and retention without changing the module; useful if you need special lifecycle/skip-destroy behaviour.

## Which pattern is active for this stack

- `gp_search` uses the module-level pattern for API Gateway access logs: `api-gateway.tf` sets `api_gateway_access_logs_log_group_name` to `local.api_log_group` and passes `api_gateway_access_logs_retention_days` to the module, so the module will create and manage the log group and retention for the API stage.

## Important notes — log-group deletion & migration risk for API Gateway

- Changing where the canonical log-group name is constructed (for example, moving the name from per-stack configuration into a central wrapper module or changing the exact `log_group_name`) will change the resource identity of the `aws_cloudwatch_log_group`. Terraform will therefore plan to create the new log group and destroy the old one.

- If the old log-group resource is currently managed by Terraform, that destroy will remove the resource from your Terraform state and will attempt to delete it in AWS. CloudWatch will still retain the stored log events until their configured retention period expires, but the managed resource will be gone and any subscriptions or resource-based access attached to the old resource will be lost.

## Recommendations / short checklist when changing logging configuration

- Prefer the module-level pattern unless you need special lifecycle behaviour.
- If you must change the log-group name or move ownership, plan for a migration window and verify subscriptions/permissions are recreated on the new resource.
- Keep per-environment retention values in `infrastructure/environments/<env>/gp_search.tfvars`.
