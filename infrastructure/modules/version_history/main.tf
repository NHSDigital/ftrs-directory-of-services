module "version_history_lambda" {
  source                  = "../lambda"
  function_name           = "${var.resource_prefix}-${var.lambda_name}"
  description             = "Lambda to track version history for Organisation, Location, and HealthcareService table changes"
  handler                 = var.lambda_handler
  runtime                 = var.lambda_runtime
  s3_bucket_name          = var.artefacts_bucket
  s3_key                  = var.lambda_s3_key
  ignore_source_code_hash = false
  s3_key_version_id       = var.lambda_s3_key_version_id
  timeout                 = var.lambda_timeout
  memory_size             = var.lambda_memory_size

  subnet_ids         = var.subnet_ids
  security_group_ids = var.security_group_ids

  number_of_policy_jsons = "2"
  policy_jsons = [
    data.aws_iam_policy_document.version_history_dynamodb_access_policy.json,
    data.aws_iam_policy_document.dynamodb_stream_access_policy.json
  ]

  layers = var.lambda_layers

  environment_variables = {
    "ENVIRONMENT"                = var.environment
    "WORKSPACE"                  = var.workspace
    "PROJECT_NAME"               = var.project
    "VERSION_HISTORY_TABLE_NAME" = var.version_history_table_name
  }
  account_id     = var.account_id
  account_prefix = var.account_prefix
  aws_region     = var.aws_region
  vpc_id         = var.vpc_id

  cloudwatch_logs_retention = var.lambda_logs_retention
}

resource "aws_lambda_event_source_mapping" "version_history_organisation_stream" {
  event_source_arn        = var.organisation_stream_arn
  function_name           = module.version_history_lambda.lambda_function_name
  starting_position       = "LATEST"
  batch_size              = var.batch_size
  enabled                 = true
  function_response_types = ["ReportBatchItemFailures"]

  filter_criteria {
    filter {
      pattern = jsonencode({
        eventName = ["MODIFY"]
      })
    }
  }

  scaling_config {
    maximum_concurrency = var.maximum_concurrency
  }

  depends_on = [
    module.version_history_lambda
  ]
}

resource "aws_lambda_event_source_mapping" "version_history_location_stream" {
  event_source_arn        = var.location_stream_arn
  function_name           = module.version_history_lambda.lambda_function_name
  starting_position       = "LATEST"
  batch_size              = var.batch_size
  enabled                 = true
  function_response_types = ["ReportBatchItemFailures"]

  filter_criteria {
    filter {
      pattern = jsonencode({
        eventName = ["MODIFY"]
      })
    }
  }

  scaling_config {
    maximum_concurrency = var.maximum_concurrency
  }

  depends_on = [
    module.version_history_lambda
  ]
}

resource "aws_lambda_event_source_mapping" "version_history_healthcare_service_stream" {
  event_source_arn        = var.healthcare_service_stream_arn
  function_name           = module.version_history_lambda.lambda_function_name
  starting_position       = "LATEST"
  batch_size              = var.batch_size
  enabled                 = true
  function_response_types = ["ReportBatchItemFailures"]

  filter_criteria {
    filter {
      pattern = jsonencode({
        eventName = ["MODIFY"]
      })
    }
  }

  scaling_config {
    maximum_concurrency = var.maximum_concurrency
  }

  depends_on = [
    module.version_history_lambda
  ]
}

data "aws_iam_policy_document" "version_history_dynamodb_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:PutItem",
      "dynamodb:Query"
    ]
    resources = [
      var.version_history_table_arn,
      "${var.version_history_table_arn}/index/*"
    ]
  }
}

data "aws_iam_policy_document" "dynamodb_stream_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:DescribeStream",
      "dynamodb:GetRecords",
      "dynamodb:GetShardIterator",
      "dynamodb:ListStreams"
    ]
    resources = [
      "${var.organisation_table_arn}/stream/*",
      "${var.location_table_arn}/stream/*",
      "${var.healthcare_service_table_arn}/stream/*"
    ]
  }
}
