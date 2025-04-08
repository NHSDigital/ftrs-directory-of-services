resource "aws_lambda_layer_version" "python_dependency_layer" {
  layer_name          = "${local.prefix}-python-dependency-layer${local.workspace_suffix}"
  compatible_runtimes = [var.lambda_runtime]
  description         = "Common Python dependencies for Lambda functions"

  s3_bucket = local.artefacts_bucket
  s3_key    = "${terraform.workspace}/${var.commit_hash}/${var.project}-python-dependency-layer-${var.application_tag}.zip"
}

module "extract_lambda" {
  source                  = "../../modules/lambda"
  function_name           = "${local.prefix}-${var.extract_name}"
  description             = "Lambda to extract data for the DoS migration"
  handler                 = var.extract_lambda_handler
  runtime                 = var.lambda_runtime
  s3_bucket_name          = local.artefacts_bucket
  s3_key                  = "${terraform.workspace}/${var.commit_hash}/${var.project}-lambda-${var.application_tag}.zip"
  ignore_source_code_hash = false
  timeout                 = var.extract_lambda_connection_timeout
  memory_size             = var.extract_lambda_memory_size

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.extract_lambda_security_group.id]

  number_of_policy_jsons = "2"
  policy_jsons           = [data.aws_iam_policy_document.s3_access_policy.json, data.aws_iam_policy_document.vpc_access_policy.json]

  layers = concat(
    [aws_lambda_layer_version.python_dependency_layer.arn],
    var.aws_lambda_layers
  )

  environment_variables = {
    "ENVIRONMENT"   = var.environment
    "PROJECT_NAME"  = var.project
    "S3_OUTPUT_URI" = "${module.migration_store_bucket.s3_bucket_arn}/${terraform.workspace}/extract/${var.data_collection_date}/"
  }
}

module "transform_lambda" {
  source                  = "../../modules/lambda"
  function_name           = "${local.prefix}-${var.transform_name}"
  description             = "Lambda to transform data for the DoS migration"
  handler                 = var.transform_lambda_handler
  runtime                 = var.lambda_runtime
  s3_bucket_name          = local.artefacts_bucket
  s3_key                  = "${terraform.workspace}/${var.commit_hash}/${var.project}-lambda-${var.application_tag}.zip"
  ignore_source_code_hash = false
  timeout                 = var.transform_lambda_connection_timeout
  memory_size             = var.transform_lambda_memory_size

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.extract_lambda_security_group.id]

  number_of_policy_jsons = "2"
  policy_jsons           = [data.aws_iam_policy_document.s3_access_policy.json, data.aws_iam_policy_document.vpc_access_policy.json]

  layers = concat(
    [aws_lambda_layer_version.python_dependency_layer.arn],
    var.aws_lambda_layers
  )

  environment_variables = {
    "ENVIRONMENT"   = var.environment
    "PROJECT_NAME"  = var.project
    "S3_INPUT_URI"  = "${module.migration_store_bucket.s3_bucket_arn}/${terraform.workspace}/extract/${var.data_collection_date}/"
    "S3_OUTPUT_URI" = "${module.migration_store_bucket.s3_bucket_arn}/${terraform.workspace}/transform/${var.data_collection_date}/"
  }
}

module "load_lambda" {
  source                  = "../../modules/lambda"
  function_name           = "${local.prefix}-${var.load_name}"
  description             = "Lambda to load data for the DoS migration"
  handler                 = var.load_lambda_handler
  runtime                 = var.lambda_runtime
  s3_bucket_name          = local.artefacts_bucket
  s3_key                  = "${terraform.workspace}/${var.commit_hash}/${var.project}-lambda-${var.application_tag}.zip"
  ignore_source_code_hash = false
  timeout                 = var.load_lambda_connection_timeout
  memory_size             = var.load_lambda_memory_size

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.load_lambda_security_group.id]

  number_of_policy_jsons = "2"
  policy_jsons           = [data.aws_iam_policy_document.s3_access_policy.json, data.aws_iam_policy_document.vpc_access_policy.json]

  layers = concat(
    [aws_lambda_layer_version.python_dependency_layer.arn],
    var.aws_lambda_layers
  )

  environment_variables = {
    "ENVIRONMENT"  = var.environment
    "PROJECT_NAME" = var.project
    "S3_INPUT_URI" = "${module.migration_store_bucket.s3_bucket_arn}/${terraform.workspace}/transform/${var.data_collection_date}/"
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
      "${module.migration_store_bucket.s3_bucket_arn}/",
      "${module.migration_store_bucket.s3_bucket_arn}/*",
    ]
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
