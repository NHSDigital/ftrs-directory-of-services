data "aws_lambda_function" "slack_notifier" {
  # count         = var.slack_notifier_enabled ? 1 : 0
  function_name = var.slack_notifier_function_name
}

resource "aws_lambda_permission" "allow_sns_invoke" {
  # count         = var.slack_notifier_enabled ? 1 : 0
  statement_id  = "AllowExecutionFromSNS-${var.resource_prefix}"
  action        = "lambda:InvokeFunction"
  function_name = data.aws_lambda_function.slack_notifier.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.alarms.arn
}

resource "aws_sns_topic_subscription" "alarms_to_slack" {
  # count     = var.slack_notifier_enabled ? 1 : 0
  topic_arn = aws_sns_topic.alarms.arn
  protocol  = "lambda"
  endpoint  = data.aws_lambda_function.slack_notifier.arn

  depends_on = [aws_lambda_permission.allow_sns_invoke]
}
