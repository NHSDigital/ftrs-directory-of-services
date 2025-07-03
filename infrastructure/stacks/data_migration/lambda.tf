resource "aws_lambda_layer_version" "python_dependency_layer" {
  layer_name          = "${local.resource_prefix}-python-dependency-layer${local.workspace_suffix}"
  compatible_runtimes = [var.lambda_runtime]
  description         = "Common Python dependencies for Lambda functions"

  s3_bucket = local.artefacts_bucket
  s3_key    = "${terraform.workspace}/${var.commit_hash}/${var.project}-${var.stack_name}-python-dependency-layer-${var.application_tag}.zip"
}

resource "aws_lambda_layer_version" "data_layer" {
  layer_name          = "ftrs_data_layer"
  compatible_runtimes = [var.lambda_runtime]
  description         = "Common data dependencies for Lambda functions"

  s3_bucket = local.artefacts_bucket
  s3_key    = "${terraform.workspace}/${var.commit_hash}/${var.project}-python-packages-layer-${var.application_tag}.zip"
}

module "extract_lambda" {
  source                  = "../../modules/lambda"
  function_name           = "${local.resource_prefix}-${var.extract_name}"
  description             = "Lambda to extract data for the DoS migration"
  handler                 = var.extract_lambda_handler
  runtime                 = var.lambda_runtime
  s3_bucket_name          = local.artefacts_bucket
  s3_key                  = "${terraform.workspace}/${var.commit_hash}/${var.project}-${var.stack_name}-lambda-${var.application_tag}.zip"
  ignore_source_code_hash = false
  timeout                 = var.extract_lambda_connection_timeout
  memory_size             = var.extract_lambda_memory_size

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.extract_lambda_security_group.id]

  number_of_policy_jsons = "2"
  policy_jsons = [
    data.aws_iam_policy_document.s3_access_policy.json,
    data.aws_iam_policy_document.secrets_access_policy.json,
  ]

  layers = concat(
    [aws_lambda_layer_version.python_dependency_layer.arn],
    [aws_lambda_layer_version.data_layer.arn],
    var.aws_lambda_layers
  )

  environment_variables = {
    "ENVIRONMENT"  = var.environment
    "PROJECT_NAME" = var.project
  }
  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
}

module "transform_lambda" {
  source                  = "../../modules/lambda"
  function_name           = "${local.resource_prefix}-${var.transform_name}"
  description             = "Lambda to transform data for the DoS migration"
  handler                 = var.transform_lambda_handler
  runtime                 = var.lambda_runtime
  s3_bucket_name          = local.artefacts_bucket
  s3_key                  = "${terraform.workspace}/${var.commit_hash}/${var.project}-${var.stack_name}-lambda-${var.application_tag}.zip"
  ignore_source_code_hash = false
  timeout                 = var.transform_lambda_connection_timeout
  memory_size             = var.transform_lambda_memory_size

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.extract_lambda_security_group.id]

  number_of_policy_jsons = "2"
  policy_jsons = [
    data.aws_iam_policy_document.s3_access_policy.json,
    data.aws_iam_policy_document.secrets_access_policy.json,
  ]

  layers = concat(
    [aws_lambda_layer_version.python_dependency_layer.arn],
    [aws_lambda_layer_version.data_layer.arn],
    var.aws_lambda_layers
  )

  environment_variables = {
    "ENVIRONMENT"  = var.environment
    "PROJECT_NAME" = var.project
  }
  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
}

module "load_lambda" {
  source                  = "../../modules/lambda"
  function_name           = "${local.resource_prefix}-${var.load_name}"
  description             = "Lambda to load data for the DoS migration"
  handler                 = var.load_lambda_handler
  runtime                 = var.lambda_runtime
  s3_bucket_name          = local.artefacts_bucket
  s3_key                  = "${terraform.workspace}/${var.commit_hash}/${var.project}-${var.stack_name}-lambda-${var.application_tag}.zip"
  ignore_source_code_hash = false
  timeout                 = var.load_lambda_connection_timeout
  memory_size             = var.load_lambda_memory_size

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.load_lambda_security_group.id]

  number_of_policy_jsons = "3"
  policy_jsons = [
    data.aws_iam_policy_document.s3_access_policy.json,
    data.aws_iam_policy_document.secrets_access_policy.json,
    data.aws_iam_policy_document.dynamodb_access_policy.json,
  ]

  layers = concat(
    [aws_lambda_layer_version.python_dependency_layer.arn],
    [aws_lambda_layer_version.data_layer.arn],
    var.aws_lambda_layers
  )

  environment_variables = {
    "ENVIRONMENT"  = var.environment
    "PROJECT_NAME" = var.project
  }
  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
}

resource "aws_lambda_permission" "allow_s3_to_invoke_load_lambda" {
  statement_id  = "AllowS3InvokeLoad"
  action        = "lambda:InvokeFunction"
  function_name = module.load_lambda.lambda_function_name
  principal     = "s3.amazonaws.com"
  source_arn    = module.migration_store_bucket.s3_bucket_arn
}

resource "aws_lambda_permission" "allow_s3_to_invoke_transform_lambda" {
  statement_id  = "AllowS3InvokeTransform"
  action        = "lambda:InvokeFunction"
  function_name = module.transform_lambda.lambda_function_name
  principal     = "s3.amazonaws.com"
  source_arn    = module.migration_store_bucket.s3_bucket_arn
}
