data "aws_lambda_function" "slack_notifier" {
  count         = var.enable_slack_notifications ? 1 : 0
  function_name = "${local.resource_prefix}-slack-notifier${local.workspace_suffix}"
}

resource "aws_lambda_permission" "allow_sns_invoke" {
  count         = var.enable_slack_notifications ? 1 : 0
  statement_id  = "AllowExecutionFromSNS-${local.resource_prefix}"
  action        = "lambda:InvokeFunction"
  function_name = data.aws_lambda_function.slack_notifier[0].function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.lambda_monitoring.sns_topic_arn
}

resource "aws_sns_topic_subscription" "lambda_alarms_to_slack" {
  count     = var.enable_slack_notifications ? 1 : 0
  topic_arn = module.lambda_monitoring.sns_topic_arn
  protocol  = "lambda"
  endpoint  = data.aws_lambda_function.slack_notifier[0].arn

  depends_on = [aws_lambda_permission.allow_sns_invoke]
}
