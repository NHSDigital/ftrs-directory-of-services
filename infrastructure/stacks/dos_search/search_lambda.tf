resource "aws_lambda_layer_version" "common_packages_layer" {
  layer_name          = "${local.resource_prefix}-common-packages-layer${local.workspace_suffix}"
  compatible_runtimes = [var.lambda_runtime]
  description         = "Common packages for Lambda functions"

  s3_bucket         = local.artefacts_bucket
  s3_key            = "${local.artefact_base_path}/${var.project}-python-packages-layer.zip"
  s3_object_version = data.aws_s3_object.common_packages_layer.version_id
}

resource "aws_lambda_layer_version" "python_dependency_layer" {
  layer_name          = "${local.resource_prefix}-python-dependency-layer${local.workspace_suffix}"
  compatible_runtimes = [var.lambda_runtime]
  description         = "Common Python dependencies for Lambda functions"

  s3_bucket         = local.artefacts_bucket
  s3_key            = "${local.artefact_base_path}/${var.project}-${var.stack_name}-python-dependency-layer.zip"
  s3_object_version = data.aws_s3_object.python_dependency_layer.version_id
}

module "lambda" {
  source                  = "../../modules/lambda"
  function_name           = "${local.resource_prefix}-${var.lambda_name}"
  description             = "This lambda provides search logic to returns an organisation and its endpoints"
  handler                 = "functions/dos_search_ods_code_function.lambda_handler"
  runtime                 = var.lambda_runtime
  s3_bucket_name          = local.artefacts_bucket
  s3_key                  = "${local.artefact_base_path}/${var.project}-${var.stack_name}-lambda.zip"
  ignore_source_code_hash = false
  s3_key_version_id       = data.aws_s3_object.dos_search_lambda_package.version_id
  attach_tracing_policy   = true
  tracing_mode            = "Active"
  number_of_policy_jsons  = "2"
  policy_jsons            = [data.aws_iam_policy_document.dynamodb_access_policy.json]
  timeout                 = var.lambda_timeout
  memory_size             = var.lambda_memory_size

  layers = [
    aws_lambda_layer_version.python_dependency_layer.arn,
    aws_lambda_layer_version.common_packages_layer.arn,
  ]

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [try(aws_security_group.dos_search_lambda_security_group[0].id, data.aws_security_group.dos_search_lambda_security_group[0].id)]

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
  build_splunk_subscription = var.build_splunk_subscription
  firehose_role_arn         = data.aws_iam_role.firehose_role.arn
  firehose_arn              = data.aws_kinesis_firehose_delivery_stream.firehose_stream.arn
}
