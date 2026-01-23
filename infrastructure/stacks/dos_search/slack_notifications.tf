################################################################################
# Slack Notification Lambda Function
# Flattens CloudWatch alarm JSON and sends to Slack
################################################################################

# Lambda function for Slack notifications
module "slack_notification_lambda" {
  source                  = "../../modules/lambda"
  function_name           = "${local.resource_prefix}-slack-notification"
  description             = "Lambda to send CloudWatch alarms to Slack"
  handler                 = "index.lambda_handler"
  runtime                 = "python3.11"
  s3_bucket_name          = local.artefacts_bucket
  s3_key                  = "${local.artefact_base_path}/${var.project}-${var.stack_name}-slack-notification-lambda-${var.application_tag}.zip"
  ignore_source_code_hash = false
  timeout                 = 30
  memory_size             = 128
  tracing_mode            = "Active"
  attach_tracing_policy   = true

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.dos_search_lambda_security_group.id]

  number_of_policy_jsons = "1"
  policy_jsons = [
    data.aws_iam_policy_document.slack_notification_policy.json,
  ]

  environment_variables = {
    "SLACK_WEBHOOK_URL" = var.slack_webhook_url
    "ENVIRONMENT"       = var.environment
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
}

# Dead Letter Queue for Slack notification Lambda
resource "aws_sqs_queue" "slack_notification_dlq" {
  name                      = "${local.resource_prefix}-slack-notification-dlq${local.workspace_suffix}"
  message_retention_seconds = 1209600 # 14 days
  kms_master_key_id         = local.kms_aliases.sqs

  tags = {
    Name = "${local.resource_prefix}-slack-notification-dlq${local.workspace_suffix}"
  }
}

# Update Lambda DLQ configuration
resource "aws_lambda_function_event_invoke_config" "slack_notification" {
  function_name                = module.slack_notification_lambda.lambda_function_name
  maximum_event_age_in_seconds = 3600
  maximum_retry_attempts       = 0

  destination_config {
    on_failure {
      type        = "SQS"
      destination = aws_sqs_queue.slack_notification_dlq.arn
    }
  }
}

# SNS subscription for Slack notification Lambda
resource "aws_sns_topic_subscription" "slack_notification" {
  topic_arn = module.sns.topic_arn
  protocol  = "lambda"
  endpoint  = module.slack_notification_lambda.lambda_function_arn
}
