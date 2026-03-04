data "aws_lambda_function" "slack_notifier" {
  count         = local.is_primary_environment ? 1 : 0
  function_name = "${local.project_prefix}-slack-notifier"
}

resource "aws_lambda_permission" "allow_sns_invoke" {
  count         = local.is_primary_environment ? 1 : 0
  statement_id  = "AllowExecutionFromSNS-${local.resource_prefix}"
  action        = "lambda:InvokeFunction"
  function_name = data.aws_lambda_function.slack_notifier[0].function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.lambda_monitoring[0].sns_topic_arn
}

resource "aws_sns_topic_subscription" "alarms_to_slack" {
  count     = local.is_primary_environment ? 1 : 0
  topic_arn = module.lambda_monitoring[0].sns_topic_arn
  protocol  = "lambda"
  endpoint  = data.aws_lambda_function.slack_notifier[0].arn

  depends_on = [aws_lambda_permission.allow_sns_invoke]
}
