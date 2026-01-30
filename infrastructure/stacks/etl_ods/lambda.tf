resource "aws_lambda_layer_version" "python_dependency_layer" {
  layer_name          = "${local.resource_prefix}-python-dependency-layer${local.workspace_suffix}"
  compatible_runtimes = [var.lambda_runtime]
  description         = "Common Python dependencies for Lambda functions"

  s3_bucket        = local.artefacts_bucket
  s3_key           = "${local.artefact_base_path}/${var.project}-${var.stack_name}-python-dependency-layer.zip"
  source_code_hash = data.aws_s3_object.python_dependency_layer.checksum_sha256
}

resource "aws_lambda_layer_version" "common_packages_layer" {
  layer_name          = "${local.resource_prefix}-common-packages-layer${local.workspace_suffix}"
  compatible_runtimes = [var.lambda_runtime]
  description         = "Common Python dependencies for Lambda functions"

  s3_bucket        = local.artefacts_bucket
  s3_key           = "${local.artefact_base_path}/${var.project}-python-packages-layer.zip"
  source_code_hash = data.aws_s3_object.common_packages_layer.checksum_sha256
}

module "extractor_lambda" {
  source         = "../../modules/lambda"
  function_name  = "${local.resource_prefix}-${var.extractor_name}"
  description    = "Lambda to extract ODS organizations and send to transform queue"
  handler        = var.extractor_lambda_handler
  runtime        = var.lambda_runtime
  s3_bucket_name = local.artefacts_bucket
  s3_key         = "${local.artefact_base_path}/${var.project}-${var.stack_name}-${var.extractor_name}.zip"

  ignore_source_code_hash = false
  timeout                 = var.extractor_lambda_connection_timeout
  memory_size             = var.lambda_memory_size

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.extractor_lambda_security_group.id]

  number_of_policy_jsons = var.environment == "dev" ? "6" : "5"
  policy_jsons = var.environment == "dev" ? [
    data.aws_iam_policy_document.s3_access_policy.json,
    data.aws_iam_policy_document.sqs_access_policy.json,
    data.aws_iam_policy_document.ssm_access_policy.json,
    data.aws_iam_policy_document.secretsmanager_jwt_credentials_access_policy.json,
    data.aws_iam_policy_document.lambda_kms_access.json,
    data.aws_iam_policy_document.ods_mock_api_access_policy[0].json
    ] : [
    data.aws_iam_policy_document.s3_access_policy.json,
    data.aws_iam_policy_document.sqs_access_policy.json,
    data.aws_iam_policy_document.ssm_access_policy.json,
    data.aws_iam_policy_document.secretsmanager_jwt_credentials_access_policy.json,
    data.aws_iam_policy_document.lambda_kms_access.json
  ]

  layers = concat(
    [aws_lambda_layer_version.common_packages_layer.arn],
    [aws_lambda_layer_version.python_dependency_layer.arn]
  )

  environment_variables = {
    "ENVIRONMENT"        = var.environment
    "WORKSPACE"          = terraform.workspace == "default" ? "" : terraform.workspace
    "PROJECT_NAME"       = var.project
    "APIM_URL"           = "${var.apim_base_url}/${var.apim_dos_ingest_path_segment}${local.workspace_suffix}/FHIR/R4"
    "ODS_URL"            = var.ods_url
    "ODS_API_PAGE_LIMIT" = tostring(var.ods_api_page_limit)
  }

  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc.id

  cloudwatch_logs_retention = var.extractor_lambda_logs_retention
}

module "transformer_lambda" {
  source                         = "../../modules/lambda"
  function_name                  = "${local.resource_prefix}-${var.transformer_name}"
  description                    = "Lambda to transform individual ODS organizations and send to consumer queue"
  handler                        = var.transformer_lambda_handler
  runtime                        = var.lambda_runtime
  s3_bucket_name                 = local.artefacts_bucket
  s3_key                         = "${local.artefact_base_path}/${var.project}-${var.stack_name}-${var.transformer_name}.zip"
  ignore_source_code_hash        = false
  timeout                        = var.transformer_lambda_connection_timeout
  memory_size                    = var.lambda_memory_size
  reserved_concurrent_executions = 5


  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.transformer_lambda_security_group.id]

  number_of_policy_jsons = "5"
  policy_jsons = [
    data.aws_iam_policy_document.s3_access_policy.json,
    data.aws_iam_policy_document.sqs_access_policy.json,
    data.aws_iam_policy_document.ssm_access_policy.json,
    data.aws_iam_policy_document.secretsmanager_jwt_credentials_access_policy.json,
    data.aws_iam_policy_document.lambda_kms_access.json
  ]

  layers = concat(
    [aws_lambda_layer_version.common_packages_layer.arn],
    [aws_lambda_layer_version.python_dependency_layer.arn]
  )

  environment_variables = {
    "ENVIRONMENT"       = var.environment
    "WORKSPACE"         = terraform.workspace == "default" ? "" : terraform.workspace
    "PROJECT_NAME"      = var.project
    "APIM_URL"          = "${var.apim_base_url}/${var.apim_dos_ingest_path_segment}${local.workspace_suffix}/FHIR/R4"
    "MAX_RECEIVE_COUNT" = tostring(var.max_receive_count)
  }

  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc.id

  cloudwatch_logs_retention = var.transformer_lambda_logs_retention
}

resource "aws_lambda_event_source_mapping" "transform_queue_trigger" {
  event_source_arn        = aws_sqs_queue.transform_queue.arn
  function_name           = module.transformer_lambda.lambda_function_name
  batch_size              = 10
  enabled                 = true
  function_response_types = ["ReportBatchItemFailures"]

  scaling_config {
    maximum_concurrency = 5
  }

  maximum_batching_window_in_seconds = 5

  depends_on = [
    module.transformer_lambda
  ]
}

module "consumer_lambda" {
  source         = "../../modules/lambda"
  function_name  = "${local.resource_prefix}-${var.consumer_name}"
  description    = "Lambda to consume queue data in the etl pipeline"
  handler        = var.consumer_lambda_handler
  runtime        = var.lambda_runtime
  s3_bucket_name = local.artefacts_bucket
  s3_key         = "${local.artefact_base_path}/${var.project}-${var.stack_name}-${var.consumer_name}.zip"

  ignore_source_code_hash = false
  timeout                 = var.consumer_lambda_connection_timeout
  memory_size             = var.lambda_memory_size

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.consumer_lambda_security_group.id]

  number_of_policy_jsons = "5"
  policy_jsons = [
    data.aws_iam_policy_document.s3_access_policy.json,
    data.aws_iam_policy_document.sqs_access_policy.json,
    data.aws_iam_policy_document.ssm_access_policy.json,
    data.aws_iam_policy_document.secretsmanager_jwt_credentials_access_policy.json,
    data.aws_iam_policy_document.lambda_kms_access.json
  ]

  layers = concat(
    [aws_lambda_layer_version.common_packages_layer.arn],
    [aws_lambda_layer_version.python_dependency_layer.arn]
  )

  environment_variables = {
    "ENVIRONMENT"       = var.environment
    "WORKSPACE"         = terraform.workspace == "default" ? "" : terraform.workspace
    "PROJECT_NAME"      = var.project
    "APIM_URL"          = "${var.apim_base_url}/${var.apim_dos_ingest_path_segment}${local.workspace_suffix}/FHIR/R4"
    "MAX_RECEIVE_COUNT" = tostring(var.max_receive_count)
  }

  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc.id

  cloudwatch_logs_retention = var.consumer_lambda_logs_retention
}


resource "aws_lambda_event_source_mapping" "consumer_queue_trigger" {
  event_source_arn        = aws_sqs_queue.load_queue.arn
  function_name           = module.consumer_lambda.lambda_function_name
  batch_size              = 10
  enabled                 = true
  function_response_types = ["ReportBatchItemFailures"]

  scaling_config {
    maximum_concurrency = 5
  }

  maximum_batching_window_in_seconds = 5

  depends_on = [
    module.consumer_lambda
  ]
}
