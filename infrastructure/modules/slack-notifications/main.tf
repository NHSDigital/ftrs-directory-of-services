module "slack_lambda" {
  source = "github.com/NHSDigital/ftrs-directory-of-services//infrastructure/modules/lambda?ref=dc4c3a23857cb7b60e87dcc0ebb5f808e48094c8"

  function_name         = "${var.resource_prefix}-slack-notification"
  description           = "Lambda to send CloudWatch alarms to Slack"
  handler               = var.lambda_handler
  runtime               = var.lambda_runtime
  s3_bucket_name        = var.lambda_s3_bucket
  s3_key                = var.lambda_s3_key
  attach_tracing_policy = var.enable_xray_tracing
  tracing_mode          = var.enable_xray_tracing ? "Active" : "PassThrough"
  timeout               = var.lambda_timeout
  memory_size           = var.lambda_memory_size

  layers = var.lambda_layers

  subnet_ids         = var.subnet_ids
  security_group_ids = var.security_group_ids

  environment_variables = merge(
    {
      "SLACK_WEBHOOK_ALARMS_URL" = var.slack_webhook_url
      "ENVIRONMENT"              = var.environment
      "PROJECT_NAME"             = var.project_name
      "WORKSPACE"                = var.workspace
    },
    var.additional_environment_variables
  )

  allowed_triggers = {
    AllowExecutionFromSNS = {
      service    = "sns"
      source_arn = var.sns_topic_arn
    }
  }

  account_id     = var.account_id
  account_prefix = var.account_prefix
  aws_region     = var.aws_region
  vpc_id         = var.vpc_id

  cloudwatch_logs_retention = var.cloudwatch_logs_retention_days

  policy_jsons = var.additional_policy_jsons
}

resource "aws_sns_topic_subscription" "slack_notification" {
  topic_arn = var.sns_topic_arn
  protocol  = "lambda"
  endpoint  = module.slack_lambda.lambda_function_arn
}
