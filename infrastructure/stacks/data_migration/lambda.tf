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

module "processor_lambda" {
  source                  = "../../modules/lambda"
  function_name           = "${local.resource_prefix}-${var.processor_lambda_name}"
  description             = "Lambda to handle DoS data migration update events"
  handler                 = var.processor_lambda_handler
  runtime                 = var.lambda_runtime
  s3_bucket_name          = local.artefacts_bucket
  s3_key                  = "${terraform.workspace}/${var.commit_hash}/${var.project}-${var.stack_name}-lambda-${var.application_tag}.zip"
  ignore_source_code_hash = false
  timeout                 = var.processor_lambda_timeout
  memory_size             = var.processor_lambda_memory_size

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.processor_lambda_security_group.id]

  number_of_policy_jsons = "3"
  policy_jsons = [
    data.aws_iam_policy_document.secrets_access_policy.json,
    data.aws_iam_policy_document.dynamodb_access_policy.json,
    data.aws_iam_policy_document.sqs_access_policy.json
  ]

  layers = concat(
    [aws_lambda_layer_version.python_dependency_layer.arn],
    [aws_lambda_layer_version.data_layer.arn],
    var.aws_lambda_layers
  )

  environment_variables = {
    "ENVIRONMENT"  = var.environment
    "WORKSPACE"    = terraform.workspace == "default" ? "" : terraform.workspace
    "PROJECT_NAME" = var.project
  }
  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc.id

  cloudwatch_logs_retention = var.processor_lambda_logs_retention

  depends_on = [aws_sqs_queue_policy.dms_event_queue_policy]
}

resource "aws_lambda_permission" "allow_sqs_invoke" {
  statement_id  = "AllowSQSTrigger"
  action        = "lambda:InvokeFunction"
  function_name = module.processor_lambda.lambda_function_name
  principal     = "sqs.amazonaws.com"
  source_arn    = aws_sqs_queue.dms_event_queue.arn
}

resource "aws_lambda_event_source_mapping" "migration_event_source_mapping" {
  event_source_arn                   = aws_sqs_queue.dms_event_queue.arn
  function_name                      = module.processor_lambda.lambda_function_name
  enabled                            = var.dms_event_queue_enabled
  batch_size                         = var.dms_event_queue_batch_size
  maximum_batching_window_in_seconds = var.dms_event_queue_maximum_batching_window_in_seconds

  scaling_config {
    maximum_concurrency = var.dms_event_queue_maximum_concurrency
  }

  depends_on = [
    aws_sqs_queue_policy.dms_event_queue_policy,
    module.processor_lambda
  ]
}

module "queue_populator_lambda" {
  source                  = "../../modules/lambda"
  function_name           = "${local.resource_prefix}-${var.queue_populator_lambda_name}"
  description             = "Lambda to populate the SQS queue with DoS services"
  handler                 = var.queue_populator_lambda_handler
  runtime                 = var.lambda_runtime
  s3_bucket_name          = local.artefacts_bucket
  s3_key                  = "${terraform.workspace}/${var.commit_hash}/${var.project}-${var.stack_name}-lambda-${var.application_tag}.zip"
  ignore_source_code_hash = false
  timeout                 = var.queue_populator_lambda_timeout
  memory_size             = var.queue_populator_lambda_memory_size

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.queue_populator_lambda_security_group.id]

  number_of_policy_jsons = "2"
  policy_jsons = [
    data.aws_iam_policy_document.secrets_access_policy.json,
    data.aws_iam_policy_document.sqs_access_policy.json,
  ]

  layers = concat(
    [aws_lambda_layer_version.python_dependency_layer.arn],
    [aws_lambda_layer_version.data_layer.arn],
    var.aws_lambda_layers
  )

  environment_variables = {
    "ENVIRONMENT"   = var.environment
    "WORKSPACE"     = terraform.workspace == "default" ? "" : terraform.workspace
    "SQS_QUEUE_URL" = aws_sqs_queue.dms_event_queue.url
    "PROJECT_NAME"  = var.project
  }
  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc.id

  cloudwatch_logs_retention = var.queue_populator_lambda_logs_retention

  depends_on = [aws_sqs_queue_policy.dms_event_queue_policy]
}

module "rds_event_listener_lambda" {
  count              = local.is_primary_environment ? 1 : 0
  source             = "../../modules/lambda"
  function_name      = "${local.resource_prefix}-${var.rds_event_listener_lambda_name}"
  description        = "Lambda to listen for database events and send notifications"
  handler            = var.migration_copy_db_lambda_trigger
  runtime            = var.lambda_runtime
  timeout            = var.rds_event_listener_lambda_connection_timeout
  memory_size        = var.rds_event_listener_lambda_memory_size
  s3_bucket_name     = local.artefacts_bucket
  s3_key             = "${terraform.workspace}/${var.commit_hash}/${var.project}-${var.stack_name}-lambda-${var.application_tag}.zip"
  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.rds_event_listener_lambda_security_group[0].id]

  number_of_policy_jsons = "2"
  policy_jsons = [
    data.aws_iam_policy_document.rds_event_listener_sqs_access_policy[0].json,
    data.aws_iam_policy_document.ssm_access_policy[0].json,
  ]

  environment_variables = {
    "ENVIRONMENT"  = var.environment
    "PROJECT_NAME" = var.project
    "SQS_SSM_PATH" = "${var.sqs_ssm_path_for_ids}${var.environment}/"
  }

  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc.id

  cloudwatch_logs_retention = var.rds_event_listener_lambda_logs_retention

  depends_on = [aws_sqs_queue.dms_event_queue]
}

module "dms_db_lambda" {
  count              = local.is_primary_environment ? 1 : 0
  source             = "../../modules/lambda"
  function_name      = "${local.resource_prefix}-${var.dms_db_lambda_name}"
  description        = "Lambda to set up DMS target RDS instance"
  handler            = var.dms_db_lambda_trigger
  runtime            = var.lambda_runtime
  timeout            = var.dms_db_lambda_connection_timeout
  memory_size        = var.dms_db_lambda_memory_size
  s3_bucket_name     = local.artefacts_bucket
  s3_key             = "${terraform.workspace}/${var.commit_hash}/${var.project}-${var.stack_name}-lambda-${var.application_tag}.zip"
  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.dms_db_setup_lambda_security_group[0].id]

  number_of_policy_jsons = "3"
  policy_jsons = [
    data.aws_iam_policy_document.secrets_access_policy_for_dms[0].json,
    data.aws_iam_policy_document.lambda_rds_policy[0].json,
    data.aws_iam_policy_document.rds_connect_policy[0].json,
  ]

  environment_variables = {
    "ENVIRONMENT"        = var.environment
    "PROJECT_NAME"       = var.project
    "TARGET_RDS_DETAILS" = "/${var.project}/${var.environment}/${var.target_rds_credentials}"
    "DMS_USER_DETAILS"   = "/${var.project}/${var.environment}/${var.dms_user_password}-${random_id.dms_user_password_suffix[0].hex}"
    "TRIGGER_LAMBDA_ARN" = module.rds_event_listener_lambda[0].lambda_function_arn
  }

  layers = [aws_lambda_layer_version.python_dependency_layer.arn]

  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc.id

  cloudwatch_logs_retention = var.dms_db_lambda_logs_retention

  depends_on = [aws_sqs_queue.dms_event_queue]
}
