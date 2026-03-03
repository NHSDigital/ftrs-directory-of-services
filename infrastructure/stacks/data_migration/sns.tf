resource "aws_sns_topic" "data_migration_sns_topic" {
  # TODO restore after test
  # count = local.is_primary_environment ? 1 : 0
  name              = "${local.resource_prefix}-sns-topic"
  kms_master_key_id = data.aws_kms_key.sqs_kms_alias.arn
}

resource "aws_sns_topic_subscription" "alarms_to_slack" {
  # TODO restore after test
  # count = local.is_primary_environment ? 1 : 0

  topic_arn  = aws_sns_topic.data_migration_sns_topic.arn
  protocol   = "lambda"
  endpoint   = data.aws_lambda_function.slack_notifier.arn
  depends_on = [aws_lambda_permission.allow_sns_invoke]
}

resource "aws_lambda_permission" "allow_sns_invoke" {
  # TODO restore after test
  # count = local.is_primary_environment ? 1 : 0

  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = data.aws_lambda_function.slack_notifier.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.data_migration_sns_topic.arn
}

