data "aws_lambda_function" "slack_notifier" {
  provider      = aws.lambda
  function_name = var.slack_notifier_function_name
}

resource "aws_lambda_permission" "allow_sns_invoke" {
  provider = aws.lambda

  statement_id  = "AllowExecutionFromSNS-${var.resource_prefix}"
  action        = "lambda:InvokeFunction"
  function_name = data.aws_lambda_function.slack_notifier.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.alarms.arn
}
