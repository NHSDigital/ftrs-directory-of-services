resource "aws_lambda_layer_version" "python_dependency_layer" {
  layer_name          = "${local.resource_prefix}-python-dependency-layer${local.workspace_suffix}"
  compatible_runtimes = [var.lambda_runtime]
  description         = "Common Python dependencies for Lambda functions"

  s3_bucket = local.artefacts_bucket
  s3_key    = "${terraform.workspace}/${var.commit_hash}/${var.project}-${var.stack_name}-python-dependency-layer-${var.application_tag}.zip"
}

module "processor_lambda" {
  source                  = "../../modules/lambda"
  function_name           = "${local.resource_prefix}-${var.processor_name}"
  description             = "Lambda to process data from ods for etl pipeline"
  handler                 = var.processor_lambda_handler
  runtime                 = var.lambda_runtime
  s3_bucket_name          = local.artefacts_bucket
  s3_key                  = "${terraform.workspace}/${var.commit_hash}/${var.project}-${var.stack_name}-lambda-${var.application_tag}.zip"
  ignore_source_code_hash = false
  timeout                 = var.lambda_connection_timeout
  memory_size             = var.lambda_memory_size

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.processor_lambda_security_group.id]

  number_of_policy_jsons = "3"
  policy_jsons           = [data.aws_iam_policy_document.s3_access_policy.json, data.aws_iam_policy_document.vpc_access_policy.json, data.aws_iam_policy_document.sqs_access_policy.json]

  layers = concat(
    [aws_lambda_layer_version.python_dependency_layer.arn],
    var.aws_lambda_layers
  )

  environment_variables = {
    "ENVIRONMENT"          = var.environment
    "PROJECT_NAME"         = var.project
    "ORGANISATION_API_URL" = data.aws_ssm_parameter.organisation_api_function_url.value
  }
}

module "consumer_lambda" {
  source                  = "../../modules/lambda"
  function_name           = "${local.resource_prefix}-${var.consumer_name}"
  description             = "Lambda to consume queue data in the etl pipeline"
  handler                 = var.consumer_lambda_handler
  runtime                 = var.lambda_runtime
  s3_bucket_name          = local.artefacts_bucket
  s3_key                  = "${terraform.workspace}/${var.commit_hash}/${var.project}-${var.stack_name}-lambda-${var.application_tag}.zip"
  ignore_source_code_hash = false
  timeout                 = var.lambda_connection_timeout
  memory_size             = var.lambda_memory_size

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.consumer_lambda_security_group.id]

  number_of_policy_jsons = "3"
  policy_jsons           = [data.aws_iam_policy_document.s3_access_policy.json, data.aws_iam_policy_document.vpc_access_policy.json, data.aws_iam_policy_document.sqs_access_policy.json]

  layers = concat(
    [aws_lambda_layer_version.python_dependency_layer.arn],
    var.aws_lambda_layers
  )

  environment_variables = {
    "ENVIRONMENT"          = var.environment
    "PROJECT_NAME"         = var.project
    "ORGANISATION_API_URL" = data.aws_ssm_parameter.organisation_api_function_url.value
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
      "${module.etl_ods_store_bucket.s3_bucket_arn}/",
      "${module.etl_ods_store_bucket.s3_bucket_arn}/*",
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

data "aws_iam_policy_document" "sqs_access_policy" {
  statement {
    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:SendMessage",
      "sqs:GetQueueUrl"
    ]
    resources = [
      aws_sqs_queue.transformed_queue.arn,
    ]
  }
}

resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = aws_sqs_queue.transformed_queue.arn
  function_name    = module.consumer_lambda.lambda_function_name
  batch_size       = 10
  enabled          = true
}
