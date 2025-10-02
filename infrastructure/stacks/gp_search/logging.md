Logging standards for gp_search Terraform stack

Purpose

This document describes the CloudWatch logging configuration for the gp_search stack, where retention is configured, the naming convention for log groups, how to verify logging, and how to change retention per environment.

Naming convention

We standardise CloudWatch log group names using the pattern:

/aws/{AWS_RESOURCE}/{PROJECT}-{ENV}-{STACK}-{RESOURCE_NAME}

Examples:

- API Gateway access logs: /aws/apigateway/ftrs-dos-dev-gp_search-api-gateway
- Lambda functions: /aws/lambda/ftrs-dos-dev-gp_search-<lambda-name>

Notes:
- Lambda log group names are created by the Lambda service using the Lambda function name. The project uses the function name pattern "${local.resource_prefix}-${var.lambda_name}" so the resulting log group will follow the standardised naming (unless an explicit `logging_log_group` is provided).
- API Gateway access logs are managed by the module invocation in this stack. The stack instructs the APIGW module to create a log group using the name `/aws/apigateway/${local.resource_prefix}-api-gateway${local.workspace_suffix}` (the stack includes the workspace suffix when applicable) and sets retention via `api_gateway_access_logs_retention_days`.

Parameterisation

The stack exposes variables to parameterise logging behaviour:

- `api_gateway_access_logs_retention_days` (number) — retention for API Gateway access logs
- `lambda_cloudwatch_logs_retention_days` (number) — retention for main search Lambda logs
- `health_check_lambda_cloudwatch_logs_retention_days` (number) — retention for health check Lambda logs

Where retention lives

- Per-environment retention values live in environment-specific tfvars under:
  `infrastructure/environments/<env>/gp_search.tfvars`
  (e.g. `infrastructure/environments/dev/gp_search.tfvars`).

- There is NOT a requirement to duplicate those values in the top-level
  `infrastructure/stacks/gp_search/variables.tf`. The recommended pattern is to keep
  environment-specific configuration in the environment tfvars and use
  the stack tfvars only for non-environmented defaults if needed.

How logging is wired (two supported patterns)

1) Module-level pattern (recommended):
   - The module creates and manages the CloudWatch log group with the requested
     name and retention. The stack instructs the module which log-group name to use.
   - Benefits: single place that enforces naming/retention for all stacks,
     easier to maintain and to attach subscriptions or cross-account access.

2) Stack-level pattern (also supported):
   - The stack creates an `aws_cloudwatch_log_group` resource and passes the
     log group's ARN into the module via `stage_access_log_settings.destination_arn`
     with `create_log_group = false`.
   - Benefits: no module change required; the stack fully controls naming/retention.

Which pattern is active for this stack
- gp_search uses the module-level pattern for API Gateway access logs: the stack configures the APIGW module with `create_log_group = true` and sets `log_group_name` to `/aws/apigateway/${local.resource_prefix}-api-gateway${local.workspace_suffix}` so the module will create and manage the log group and retention.

Important notes — log-group deletion & migration risk for API Gateway
- Changing where the canonical log-group name is constructed (for example, moving
  the name from per-stack configuration into a central wrapper module) will change
  the resource identity of the `aws_cloudwatch_log_group`. Terraform will therefore
  plan to create the new log group and destroy the old one.

- If the old log-group resource is currently managed by Terraform, that destroy will
  remove the resource from your terraform state and will attempt to delete it in AWS.
  CloudWatch will still retain the stored log events until their configured retention
  period expires, but the managed resource will be gone and any subscriptions or
  resource-based access attached to the old resource will be lost.

