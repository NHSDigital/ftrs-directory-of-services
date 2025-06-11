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

module "organisation_api_lambda" {
  source                  = "../../modules/lambda"
  function_name           = "${local.resource_prefix}-${var.organisation_api_lambda_name}"
  description             = "Lambda to expose CRUD apis for organisations"
  handler                 = var.organisation_api_lambda_handler
  runtime                 = var.organisation_api_lambda_runtime
  s3_bucket_name          = local.artefacts_bucket
  s3_key                  = "${terraform.workspace}/${var.commit_hash}/${var.project}-${var.stack_name}-lambda-${var.application_tag}.zip"
  ignore_source_code_hash = false
  timeout                 = var.organisation_api_lambda_timeout
  memory_size             = var.organisation_api_lambda_memory_size

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.organisation_api_lambda_security_group.id]

  number_of_policy_jsons = "3"
  policy_jsons = [
    data.aws_iam_policy_document.s3_access_policy.json,
    data.aws_iam_policy_document.vpc_access_policy.json,
    data.aws_iam_policy_document.dynamodb_access_policy.json
  ]
  layers = [
    aws_lambda_layer_version.python_dependency_layer.arn,
    aws_lambda_layer_version.common_packages_layer.arn,
  ]

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
}

module "healthcare_service_api_lambda" {
  source                  = "../../modules/lambda"
  function_name           = "${local.resource_prefix}-${var.healthcare_service_api_lambda_name}"
  description             = "Lambda to expose CRUD apis for healthcare services"
  handler                 = var.healthcare_service_api_lambda_handler
  runtime                 = var.healthcare_service_api_lambda_runtime
  s3_bucket_name          = local.artefacts_bucket
  s3_key                  = "${terraform.workspace}/${var.commit_hash}/${var.project}-${var.stack_name}-lambda-${var.application_tag}.zip"
  ignore_source_code_hash = false
  timeout                 = var.healthcare_service_api_lambda_timeout
  memory_size             = var.healthcare_service_api_lambda_memory_size

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.healthcare_service_api_lambda_security_group.id]

  number_of_policy_jsons = "3"
  policy_jsons = [
    data.aws_iam_policy_document.s3_access_policy.json,
    data.aws_iam_policy_document.vpc_access_policy.json,
    data.aws_iam_policy_document.dynamodb_access_policy.json
  ]
  layers = [
    aws_lambda_layer_version.python_dependency_layer.arn,
    aws_lambda_layer_version.common_packages_layer.arn,
  ]


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
}

module "location_api_lambda" {
  source                  = "../../modules/lambda"
  function_name           = "${local.resource_prefix}-${var.location_api_lambda_name}"
  description             = "Lambda to expose CRUD apis for locations"
  handler                 = var.location_api_lambda_handler
  runtime                 = var.location_api_lambda_runtime
  s3_bucket_name          = local.artefacts_bucket
  s3_key                  = "${terraform.workspace}/${var.commit_hash}/${var.project}-${var.stack_name}-lambda-${var.application_tag}.zip"
  ignore_source_code_hash = false
  timeout                 = var.location_api_lambda_timeout
  memory_size             = var.location_api_lambda_memory_size

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.location_api_lambda_security_group.id]

  number_of_policy_jsons = "3"
  policy_jsons = [
    data.aws_iam_policy_document.s3_access_policy.json,
    data.aws_iam_policy_document.vpc_access_policy.json,
    data.aws_iam_policy_document.dynamodb_access_policy.json
  ]
  layers = [
    aws_lambda_layer_version.python_dependency_layer.arn,
    aws_lambda_layer_version.common_packages_layer.arn,
  ]

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

data "aws_iam_policy_document" "s3_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject"
    ]
    resources = [
      "${module.crud_apis_bucket.s3_bucket_arn}/",
      "${module.crud_apis_bucket.s3_bucket_arn}/*",
    ]
  }
}

data "aws_iam_policy_document" "dynamodb_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:PutItem",
      "dynamodb:GetItem",
      "dynamodb:UpdateItem",
      "dynamodb:DeleteItem",
      "dynamodb:Scan",
      "dynamodb:Query"
    ]
    resources = flatten([
      for table in local.dynamodb_tables : [
        table.arn,
        "${table.arn}/index/*"
      ]
    ])
  }
}
