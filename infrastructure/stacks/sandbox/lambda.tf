resource "aws_lambda_layer_version" "common_packages_layer" {
  layer_name          = "${local.resource_prefix}-common-packages-layer${local.workspace_suffix}"
  compatible_runtimes = [var.organisation_api_lambda_runtime]
  description         = "Common Python dependencies for Lambda functions"

  s3_bucket = local.artefacts_bucket
  s3_key    = "${terraform.workspace}/${var.commit_hash}/${var.project}-python-packages-layer-${var.application_tag}.zip"
}

resource "aws_lambda_layer_version" "python_dependency_layer" {
  layer_name          = "${local.resource_prefix}-python-dependency-layer${local.workspace_suffix}"
  compatible_runtimes = [var.organisation_api_lambda_runtime]
  description         = "Common Python dependencies for Lambda functions"

  s3_bucket = local.artefacts_bucket
  s3_key    = "${terraform.workspace}/${var.commit_hash}/${var.project}-${var.stack_name}-python-dependency-layer-${var.application_tag}.zip"
}

module "mock_api_lambda" {
  source                  = "../../modules/lambda"
  function_name           = "${local.resource_prefix}-${var.mock_api_lambda_name}"
  description             = "Lambda to return mock responses"
  handler                 = var.mock_api_lambda_handler
  runtime                 = var.mock_api_lambda_runtime
  s3_bucket_name          = local.artefacts_bucket
  s3_key                  = "${terraform.workspace}/${var.commit_hash}/${var.project}-${var.stack_name}-lambda-${var.application_tag}.zip"
  ignore_source_code_hash = false
  timeout                 = var.mock_api_lambda_timeout
  memory_size             = var.mock_api_lambda_memory_size
  # create                  = var.environment == "sandbox"

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.organisation_api_lambda_security_group.id]

  number_of_policy_jsons = "1"
  policy_jsons = [
    data.aws_iam_policy_document.s3_access_policy.json,
  ]
  layers = []

  environment_variables = {
    "ENVIRONMENT"  = var.environment
    "WORKSPACE"    = terraform.workspace == "default" ? "" : terraform.workspace
    "PROJECT_NAME" = var.project
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
}
