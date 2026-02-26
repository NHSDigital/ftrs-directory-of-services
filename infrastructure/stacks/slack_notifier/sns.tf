resource "aws_sns_topic" "slack_notifications" {
  count             = local.stack_enabled
  name              = local.sns_topic_name
  display_name      = "Slack Notifications for ${var.environment}"
  kms_master_key_id = data.aws_kms_key.sns[0].id

  tags = {
    Name = local.sns_topic_name
  }
}

resource "aws_sns_topic_policy" "slack_notifications" {
  count  = local.stack_enabled
  arn    = aws_sns_topic.slack_notifications[0].arn
  policy = data.aws_iam_policy_document.sns_topic_policy[0].json
}

resource "aws_sns_topic_subscription" "slack_notification" {
  count     = local.stack_enabled
  topic_arn = aws_sns_topic.slack_notifications[0].arn
  protocol  = "lambda"
  endpoint  = module.slack_lambda[0].lambda_function_arn
}
