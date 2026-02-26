module "slack_lambda" {
  count  = local.stack_enabled
  source = "../../modules/lambda"

  function_name         = local.resource_prefix
  description           = "Lambda to send CloudWatch alarms to Slack"
  handler               = "functions.slack_alarm_handler.lambda_handler"
  runtime               = var.lambda_runtime
  s3_bucket_name        = local.artefacts_bucket
  s3_key                = local.lambda_s3_key
  attach_tracing_policy = var.enable_xray_tracing
  tracing_mode          = var.enable_xray_tracing ? "Active" : "PassThrough"
  timeout               = var.lambda_timeout
  memory_size           = var.lambda_memory_size

  layers = [
    aws_lambda_layer_version.python_dependency_layer[0].arn,
    aws_lambda_layer_version.common_packages_layer[0].arn,
  ]

  subnet_ids         = data.aws_subnets.private[0].ids
  security_group_ids = [aws_security_group.slack_notifier_lambda_sg[0].id]

  environment_variables = {
    "SLACK_WEBHOOK_ALARMS_URL" = var.slack_webhook_alarms_url
    "ENVIRONMENT"              = var.environment
    "PROJECT_NAME"             = var.project
    "WORKSPACE"                = ""
  }

  allowed_triggers = {
    AllowExecutionFromSNS = {
      service    = "sns"
      source_arn = aws_sns_topic.slack_notifications[0].arn
    }
  }

  account_id     = local.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc[0].id

  cloudwatch_logs_retention = var.cloudwatch_logs_retention_days

  policy_jsons = []
}
