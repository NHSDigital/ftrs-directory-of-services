module "health_check_lambda" {
  source                 = "../../modules/lambda"
  function_name          = "${local.resource_prefix}-${var.health_check_lambda_name}"
  description            = "This lambda provides a health check for the search lambda"
  handler                = "health_check/health_check_function.lambda_handler"
  runtime                = var.lambda_runtime
  s3_bucket_name         = local.artefacts_bucket
  s3_key                 = "${terraform.workspace}/${var.commit_hash}/${var.gp_search_service_name}-lambda-${var.application_tag}.zip"
  attach_tracing_policy  = true
  tracing_mode           = "Active"
  number_of_policy_jsons = "2"
  policy_jsons           = [data.aws_iam_policy_document.health_check_dynamodb_access_policy.json]
  timeout                = var.lambda_timeout
  memory_size            = var.lambda_memory_size

  layers = [
    aws_lambda_layer_version.python_dependency_layer.arn,
    aws_lambda_layer_version.common_packages_layer.arn,
  ]

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.gp_search_lambda_security_group.id]

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

  cloudwatch_logs_retention = var.health_check_lambda_cloudwatch_logs_retention_days
}

data "aws_iam_policy_document" "health_check_dynamodb_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:DescribeTable",
    ]
    resources = [
      "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${var.project}-${var.environment}-database-${var.gp_search_organisation_table_name}*"
    ]
  }
}
