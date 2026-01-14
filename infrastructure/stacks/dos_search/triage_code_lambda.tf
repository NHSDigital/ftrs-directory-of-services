# Triage code lambda (placeholder)
#
# This publishes a dedicated Lambda artefact for the forthcoming triage_code endpoint.
# API Gateway wiring is intentionally not added yet until the endpoint contract is finalised.

module "triage_code_lambda" {
  source         = "github.com/NHSDigital/ftrs-directory-of-services?ref=dc4c3a23857cb7b60e87dcc0ebb5f808e48094c8/infrastructure/modules/lambda"
  function_name  = "${local.resource_prefix}-triage-code"
  description    = "Lambda for triage_code endpoint (placeholder until contract finalised)"
  handler        = "functions/triage_code/handler.lambda_handler"
  runtime        = var.lambda_runtime
  s3_bucket_name = local.artefacts_bucket

  s3_key = "${local.artefact_base_path}/${var.project}-${var.stack_name}-triage-code-${var.application_tag}.zip"

  attach_tracing_policy  = true
  tracing_mode           = "Active"
  number_of_policy_jsons = "0"
  # No extra policies required for placeholder; update when endpoint needs AWS access
  policy_jsons = []

  timeout     = var.lambda_timeout
  memory_size = var.lambda_memory_size

  layers = [
    aws_lambda_layer_version.python_dependency_layer.arn,
    aws_lambda_layer_version.common_packages_layer.arn,
  ]

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.dos_search_lambda_security_group.id]

  environment_variables = {
    "ENVIRONMENT"  = var.environment
    "PROJECT_NAME" = var.project
    "WORKSPACE"    = terraform.workspace == "default" ? "" : terraform.workspace
  }

  # Not exposed via API Gateway yet
  allowed_triggers = {}

  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc.id

  cloudwatch_logs_retention = var.lambda_cloudwatch_logs_retention_days
}
