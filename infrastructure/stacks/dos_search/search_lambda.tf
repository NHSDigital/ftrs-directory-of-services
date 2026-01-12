resource "aws_lambda_layer_version" "common_packages_layer" {
  layer_name          = "${local.resource_prefix}-common-packages-layer${local.workspace_suffix}"
  compatible_runtimes = [var.lambda_runtime]
  description         = "Common packages for Lambda functions"

  s3_bucket = local.artefacts_bucket
  s3_key    = "${local.artefact_base_path}/${var.project}-python-packages-layer-${var.application_tag}.zip"
}

resource "aws_lambda_layer_version" "python_dependency_layer" {
  layer_name          = "${local.resource_prefix}-python-dependency-layer${local.workspace_suffix}"
  compatible_runtimes = [var.lambda_runtime]
  description         = "Common Python dependencies for Lambda functions"

  s3_bucket = local.artefacts_bucket
  s3_key    = "${local.artefact_base_path}/${var.project}-${var.stack_name}-python-dependency-layer-${var.application_tag}.zip"
}

# API-facing lambda for GET /Organization
module "lambda" {
  source                 = "github.com/NHSDigital/ftrs-directory-of-services?ref=dc4c3a23857cb7b60e87dcc0ebb5f808e48094c8/infrastructure/modules/lambda"
  function_name          = "${local.resource_prefix}-${var.lambda_name}"
  description            = var.organization_use_internal_workers ? "Router lambda for /Organization (delegates to internal workers)" : "Lambda for /Organization"
  handler                = var.organization_use_internal_workers ? "lambdas/organization_get_router/handler.lambda_handler" : "functions/dos_search_ods_code_function.lambda_handler"
  runtime                = var.lambda_runtime
  s3_bucket_name         = local.artefacts_bucket
  s3_key                 = var.organization_use_internal_workers ? "${local.artefact_base_path}/${var.project}-${var.stack_name}-organization-get-router-lambda-${var.application_tag}.zip" : "${local.artefact_base_path}/${var.project}-${var.stack_name}-organization-get-lambda-${var.application_tag}.zip"
  attach_tracing_policy  = true
  tracing_mode           = "Active"
  number_of_policy_jsons = "2"
  policy_jsons = var.organization_use_internal_workers ? [
    data.aws_iam_policy_document.dynamodb_access_policy.json,
    data.aws_iam_policy_document.org_worker_invoke_policy.json,
    ] : [
    data.aws_iam_policy_document.dynamodb_access_policy.json,
  ]

  timeout     = var.lambda_timeout
  memory_size = var.lambda_memory_size

  layers = [
    aws_lambda_layer_version.python_dependency_layer.arn,
    aws_lambda_layer_version.common_packages_layer.arn,
  ]

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.dos_search_lambda_security_group.id]

  environment_variables = merge(
    {
      "ENVIRONMENT"  = var.environment
      "PROJECT_NAME" = var.project
      "WORKSPACE"    = terraform.workspace == "default" ? "" : terraform.workspace
    },
    var.organization_use_internal_workers ? {
      "DOS_SEARCH_ORCHESTRATION_MODE"      = "inline"
      "DOS_SEARCH_ORG_WORKER_LAMBDA_NAMES" = "${local.resource_prefix}-${var.lambda_name}-org-worker${local.workspace_suffix},${local.resource_prefix}-${var.lambda_name}-org-worker-2${local.workspace_suffix},${local.resource_prefix}-${var.lambda_name}-org-worker-3${local.workspace_suffix}"
    } : {},
  )

  allowed_triggers = {
    AllowExecutionFromAPIGateway = {
      service    = "apigateway"
      source_arn = "${aws_api_gateway_rest_api.api_gateway.execution_arn}/*/*"
    }
  }

  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc.id

  cloudwatch_logs_retention = var.lambda_cloudwatch_logs_retention_days
}

# Internal worker lambda for GET /Organization
module "organization_get_worker_lambda" {
  count                  = var.organization_use_internal_workers ? 1 : 0
  source                 = "github.com/NHSDigital/ftrs-directory-of-services?ref=dc4c3a23857cb7b60e87dcc0ebb5f808e48094c8/infrastructure/modules/lambda"
  function_name          = "${local.resource_prefix}-${var.lambda_name}-org-worker"
  description            = "Worker lambda for /Organization"
  handler                = "lambdas/organization_get_worker/handler.lambda_handler"
  runtime                = var.lambda_runtime
  s3_bucket_name         = local.artefacts_bucket
  s3_key                 = "${local.artefact_base_path}/${var.project}-${var.stack_name}-organization-get-worker-lambda-${var.application_tag}.zip"
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
      source_arn = "${aws_api_gateway_rest_api.api_gateway.execution_arn}/*/*"
    }
  }

  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc.id

  cloudwatch_logs_retention = var.lambda_cloudwatch_logs_retention_days
}

module "organization_get_worker_lambda_2" {
  count                  = var.organization_use_internal_workers ? 1 : 0
  source                 = "github.com/NHSDigital/ftrs-directory-of-services?ref=dc4c3a23857cb7b60e87dcc0ebb5f808e48094c8/infrastructure/modules/lambda"
  function_name          = "${local.resource_prefix}-${var.lambda_name}-org-worker-2"
  description            = "Worker lambda 2 for /Organization"
  handler                = "lambdas/organization_get_worker/handler.lambda_handler"
  runtime                = var.lambda_runtime
  s3_bucket_name         = local.artefacts_bucket
  s3_key                 = "${local.artefact_base_path}/${var.project}-${var.stack_name}-organization-get-worker-2-lambda-${var.application_tag}.zip"
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
      source_arn = "${aws_api_gateway_rest_api.api_gateway.execution_arn}/*/*"
    }
  }

  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc.id

  cloudwatch_logs_retention = var.lambda_cloudwatch_logs_retention_days
}

module "organization_get_worker_lambda_3" {
  count                  = var.organization_use_internal_workers ? 1 : 0
  source                 = "github.com/NHSDigital/ftrs-directory-of-services?ref=dc4c3a23857cb7b60e87dcc0ebb5f808e48094c8/infrastructure/modules/lambda"
  function_name          = "${local.resource_prefix}-${var.lambda_name}-org-worker-3"
  description            = "Worker lambda 3 for /Organization"
  handler                = "lambdas/organization_get_worker/handler.lambda_handler"
  runtime                = var.lambda_runtime
  s3_bucket_name         = local.artefacts_bucket
  s3_key                 = "${local.artefact_base_path}/${var.project}-${var.stack_name}-organization-get-worker-3-lambda-${var.application_tag}.zip"
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
      source_arn = "${aws_api_gateway_rest_api.api_gateway.execution_arn}/*/*"
    }
  }

  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc.id

  cloudwatch_logs_retention = var.lambda_cloudwatch_logs_retention_days
}
