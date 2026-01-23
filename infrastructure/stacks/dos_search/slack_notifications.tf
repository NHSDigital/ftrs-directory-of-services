################################################################################
# Slack Notification Lambda Function
# Flattens CloudWatch alarm JSON and sends to Slack
################################################################################

# IAM Role for Slack notification Lambda
resource "aws_iam_role" "slack_notification_lambda_role" {
  name = "${local.resource_prefix}-slack-notification-lambda-role${local.workspace_suffix}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name = "${local.resource_prefix}-slack-notification-lambda-role${local.workspace_suffix}"
  }
}

# IAM Policy for basic Lambda execution (CloudWatch logs)
resource "aws_iam_role_policy_attachment" "slack_notification_lambda_basic_execution" {
  role       = aws_iam_role.slack_notification_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# IAM Policy for X-Ray write access
resource "aws_iam_role_policy_attachment" "slack_notification_lambda_xray_write" {
  role       = aws_iam_role.slack_notification_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess"
}

# IAM Policy for accessing Slack webhook URL from environment
resource "aws_iam_role_policy" "slack_notification_lambda_secrets_policy" {
  name = "${local.resource_prefix}-slack-notification-env-policy${local.workspace_suffix}"
  role = aws_iam_role.slack_notification_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
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

# Lambda function for Slack notifications
resource "aws_lambda_function" "slack_notification" {
  filename      = "${path.module}/../../lambda_functions/slack_notification.zip"
  function_name = "${local.resource_prefix}-slack-notification${local.workspace_suffix}"
  role          = aws_iam_role.slack_notification_lambda_role.arn
  handler       = "index.lambda_handler"
  runtime       = "python3.11"
  timeout       = 30
  tracing_config {
    mode = "Active"
  }
  dead_letter_config {
    target_arn = aws_sqs_queue.slack_notification_dlq.arn
  }

  environment {
    variables = {
      SLACK_WEBHOOK_URL = var.slack_webhook_url
      ENVIRONMENT       = var.environment
    }
  }

  kms_key_arn = "arn:aws:kms:${var.aws_region}:${data.aws_caller_identity.current.account_id}:alias/aws/lambda"

  reserved_concurrent_executions = 10
  code_signing_config_arn        = aws_lambda_code_signing_config.slack_notification.arn

  vpc_config {
    subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
    security_group_ids = [aws_security_group.dos_search_lambda_security_group.id]
  }

  tags = {
    Name = "${local.resource_prefix}-slack-notification${local.workspace_suffix}"
  }

  depends_on = [aws_iam_role_policy_attachment.slack_notification_lambda_basic_execution]
}

# Lambda Code Signing Configuration
resource "aws_lambda_code_signing_config" "slack_notification" {
  allowed_publishers {
    signing_profile_version_arns = ["arn:aws:signer:${var.aws_region}:${data.aws_caller_identity.current.account_id}:signing-profile/*"]
  }
  description = "Code signing config for slack notification Lambda"
}

# SNS subscription for Slack notification Lambda
resource "aws_sns_topic_subscription" "slack_notification" {
  topic_arn = module.sns.topic_arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.slack_notification.arn
}

# Permission for SNS to invoke the Lambda function
resource "aws_lambda_permission" "slack_notification_sns" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.slack_notification.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.sns.topic_arn
}

# CloudWatch log group for Slack notification Lambda
resource "aws_cloudwatch_log_group" "slack_notification_lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.slack_notification.function_name}"
  retention_in_days = var.lambda_cloudwatch_logs_retention_days
  kms_key_id        = "arn:aws:kms:${var.aws_region}:${data.aws_caller_identity.current.account_id}:alias/aws/logs"

  tags = {
    Name = "/aws/lambda/${aws_lambda_function.slack_notification.function_name}"
  }
}
