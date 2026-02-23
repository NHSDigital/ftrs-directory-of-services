
resource "aws_lambda_layer_version" "python_dependency_layer" {
  count               = local.version_history_enabled
  layer_name          = "${local.resource_prefix}-python-dependency-layer${local.workspace_suffix}"
  compatible_runtimes = [var.version_history_lambda_runtime]
  description         = "Common Python dependencies for Lambda functions"

  s3_bucket         = local.artefacts_bucket
  s3_key            = "${local.artefact_base_path}/${var.project}-data-migration-python-dependency-layer.zip"
  s3_object_version = data.aws_s3_object.python_dependency_layer[0].version_id
}

resource "aws_lambda_layer_version" "data_layer" {
  count               = local.version_history_enabled
  layer_name          = "${local.resource_prefix}-data-layer${local.workspace_suffix}"
  compatible_runtimes = [var.version_history_lambda_runtime]
  description         = "Common data dependencies for Lambda functions"

  s3_bucket         = local.artefacts_bucket
  s3_key            = "${local.artefact_base_path}/${var.project}-python-packages-layer.zip"
  s3_object_version = data.aws_s3_object.data_layer[0].version_id
}

module "version_history_lambda" {
  count                   = local.version_history_enabled
  source                  = "../../modules/lambda"
  function_name           = "${local.resource_prefix}-${var.version_history_lambda_name}"
  description             = "Lambda to track version history for Organisation, Location, and HealthcareService table changes"
  handler                 = var.version_history_lambda_handler
  runtime                 = var.version_history_lambda_runtime
  s3_bucket_name          = local.artefacts_bucket
  s3_key                  = "${local.artefact_base_path}/${var.project}-data-migration-lambda.zip"
  ignore_source_code_hash = false
  s3_key_version_id       = data.aws_s3_object.data_migration_lambda_package[0].version_id
  timeout                 = var.version_history_lambda_timeout
  memory_size             = var.version_history_lambda_memory_size

  subnet_ids         = [for subnet in values(data.aws_subnet.private_subnets_details) : subnet.id if endswith(subnet.cidr_block, "/24")]
  security_group_ids = [try(aws_security_group.version_history_lambda_security_group[0].id, data.aws_security_group.version_history_lambda_security_group[0].id)]

  number_of_policy_jsons = "2"
  policy_jsons = [
    data.aws_iam_policy_document.version_history_dynamodb_access_policy[0].json,
    data.aws_iam_policy_document.dynamodb_stream_access_policy[0].json
  ]

  layers = [
    aws_lambda_layer_version.python_dependency_layer[0].arn,
    aws_lambda_layer_version.data_layer[0].arn
  ]

  environment_variables = {
    "ENVIRONMENT"  = var.environment
    "WORKSPACE"    = terraform.workspace == "default" ? "" : terraform.workspace
    "PROJECT_NAME" = var.project
  }
  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc.id

  cloudwatch_logs_retention = var.version_history_lambda_logs_retention
}

resource "aws_lambda_event_source_mapping" "version_history_streams" {
  for_each = local.version_history_enabled == 1 ? local.table_streams : {}

  event_source_arn        = each.value.stream_arn
  function_name           = module.version_history_lambda[0].lambda_function_name
  starting_position       = "LATEST"
  batch_size              = var.version_history_batch_size
  enabled                 = true
  function_response_types = ["ReportBatchItemFailures"]

  filter_criteria {
    filter {
      pattern = jsonencode({
        eventName = ["MODIFY"]
      })
    }
  }

  depends_on = [
    module.version_history_lambda
  ]
}
