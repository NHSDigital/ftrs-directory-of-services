resource "aws_lambda_layer_version" "python_dependency_layer" {
  layer_name          = "${local.resource_prefix}-python-dependency-layer${local.workspace_suffix}"
  compatible_runtimes = [var.lambda_runtime]
  description         = "Common Python dependencies for Lambda functions"

  s3_bucket = local.artefacts_bucket
  s3_key    = "${terraform.workspace}/${var.commit_hash}/${var.gp_search_service_name}-python-dependency-layer-${var.application_tag}.zip"
}

module "lambda" {
  source                 = "github.com/NHSDigital/ftrs-directory-of-services?ref=ebe96e5/infrastructure/modules/lambda"
  function_name          = "${local.resource_prefix}-${var.lambda_name}"
  description            = "This lambda provides search logic to returns an organisation and its endpoints"
  handler                = "functions/gp_search_function.lambda_handler"
  runtime                = var.lambda_runtime
  s3_bucket_name         = local.artefacts_bucket
  s3_key                 = "${terraform.workspace}/${var.commit_hash}/${var.gp_search_service_name}-lambda-${var.application_tag}.zip"
  attach_tracing_policy  = true
  tracing_mode           = "Active"
  number_of_policy_jsons = "2"
  policy_jsons           = [data.aws_iam_policy_document.vpc_access_policy.json, data.aws_iam_policy_document.dynamodb_access_policy.json]
  timeout                = var.lambda_timeout
  memory_size            = var.lambda_memory_size

  layers = (
    [aws_lambda_layer_version.python_dependency_layer.arn]
  )

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.gp_search_lambda_security_group.id]

  environment_variables = {
    "ENVIRONMENT"         = var.environment
    "PROJECT_NAME"        = var.project
    "NAMESPACE"           = "${var.gp_search_service_name}${local.workspace_suffix}"
    "DYNAMODB_TABLE_NAME" = "${var.project}-${var.environment}-database-${var.gp_search_organisation_table_name}"
  }
}

module "search_api_gateway_permissions" {
  source = "../../modules/api-gateway-permissions"

  account_id           = local.account_id
  aws_region           = var.aws_region
  lambda_function_name = "${local.resource_prefix}-${var.lambda_name}"
  rest_api_id          = module.search_rest_api.rest_api_id
}

data "aws_iam_policy_document" "vpc_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "ec2:CreateNetworkInterface",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DeleteNetworkInterface"
    ]
    resources = [
      "*"
    ]
  }
}

data "aws_iam_policy_document" "dynamodb_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:Scan",
      "dynamodb:Query",
    ]
    resources = [
      "${local.gp_search_organisation_table_arn}/",
      "${local.gp_search_organisation_table_arn}/*"
    ]
  }
}
