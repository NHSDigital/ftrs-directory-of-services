resource "aws_lambda_layer_version" "common_packages_layer" {
  layer_name          = "${local.resource_prefix}-common-packages-layer${local.workspace_suffix}"
  compatible_runtimes = [var.lambda_runtime]
  description         = "Common packages for Lambda functions"

  s3_bucket = local.artefacts_bucket
  s3_key    = "${terraform.workspace}/${var.commit_hash}/${var.project}-python-packages-layer-${var.application_tag}.zip"
}

resource "aws_lambda_layer_version" "python_dependency_layer" {
  layer_name          = "${local.resource_prefix}-python-dependency-layer${local.workspace_suffix}"
  compatible_runtimes = [var.lambda_runtime]
  description         = "Common Python dependencies for Lambda functions"

  s3_bucket = local.artefacts_bucket
  s3_key    = "${terraform.workspace}/${var.commit_hash}/${var.project}-${var.stack_name}-python-dependency-layer-${var.application_tag}.zip"
}

module "lambda" {
  source                 = "github.com/NHSDigital/ftrs-directory-of-services?ref=57b53f778381f3c4cfaded5770a5eddd3ff8f6f5/infrastructure/modules/lambda"
  function_name          = "${local.resource_prefix}-${var.lambda_name}"
  description            = "This lambda provides search logic to returns an organisation and its endpoints"
  handler                = "functions/dos_search_function.lambda_handler"
  runtime                = var.lambda_runtime
  s3_bucket_name         = local.artefacts_bucket
  s3_key                 = "${terraform.workspace}/${var.commit_hash}/${var.project}-${var.stack_name}-lambda-${var.application_tag}.zip"
  attach_tracing_policy  = true
  tracing_mode           = "Active"
  number_of_policy_jsons = "2"
  policy_jsons           = [data.aws_iam_policy_document.dynamodb_access_policy.json]
  timeout                = var.lambda_timeout
  memory_size            = var.lambda_memory_size

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

  allowed_triggers = {
    AllowExecutionFromAPIGateway = {
      service    = "apigateway"
      source_arn = "${module.api_gateway.api_execution_arn}/*/*"
    }
  }

  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc.id

  cloudwatch_logs_retention = var.lambda_cloudwatch_logs_retention_days
}
