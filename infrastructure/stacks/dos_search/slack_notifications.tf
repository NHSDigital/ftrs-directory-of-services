################################################################################
# Slack Notification Lambda Function
# Flattens CloudWatch alarm JSON and sends to Slack
################################################################################

# IAM Policy for Slack notification Lambda
data "aws_iam_policy_document" "slack_notification_policy" {
  statement {
    sid    = "AllowKMSEncryption"
    effect = "Allow"
    actions = [
      "kms:Decrypt",
      "kms:GenerateDataKey"
    ]
    resources = [
      "arn:aws:kms:${var.aws_region}:${data.aws_caller_identity.current.account_id}:alias/aws/lambda"
    ]
  }
}

# Lambda function for Slack notifications
module "slack_notification_lambda" {
  source                 = "github.com/NHSDigital/ftrs-directory-of-services?ref=dc4c3a23857cb7b60e87dcc0ebb5f808e48094c8/infrastructure/modules/lambda"
  function_name          = "${local.resource_prefix}-slack-notification"
  description            = "Lambda to send CloudWatch alarms to Slack"
  handler                = "functions.slack_alarm_handler.lambda_handler"
  runtime                = var.lambda_runtime
  s3_bucket_name         = local.artefacts_bucket
  s3_key                 = "${local.artefact_base_path}/${var.project}-${var.stack_name}-lambda-${var.application_tag}.zip"
  attach_tracing_policy  = true
  tracing_mode           = "Active"
  number_of_policy_jsons = "1"
  policy_jsons           = [data.aws_iam_policy_document.slack_notification_policy.json]
  timeout                = 30
  memory_size            = 128

  layers = [
    aws_lambda_layer_version.python_dependency_layer.arn,
    aws_lambda_layer_version.common_packages_layer.arn,
  ]

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.dos_search_lambda_security_group.id]

  environment_variables = {
    "SLACK_WEBHOOK_URL" = var.slack_webhook_alarms_url
    "ENVIRONMENT"       = var.environment
    "PROJECT_NAME"      = var.project
    "WORKSPACE"         = terraform.workspace == "default" ? "" : terraform.workspace
  }

  allowed_triggers = {
    AllowExecutionFromSNS = {
      service    = "sns"
      source_arn = module.sns.topic_arn
    }
  }

  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc.id

  cloudwatch_logs_retention = var.lambda_cloudwatch_logs_retention_days
}

# SNS subscription for Slack notification Lambda
resource "aws_sns_topic_subscription" "slack_notification" {
  topic_arn = module.sns.topic_arn
  protocol  = "lambda"
  endpoint  = module.slack_notification_lambda.lambda_function_arn
}
