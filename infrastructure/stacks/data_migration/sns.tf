resource "aws_sns_topic" "data_migration_sns_topic" {
  count = local.is_primary_environment ? 1 : 0

  name              = "${local.resource_prefix}-sns-topic"
  kms_master_key_id = data.aws_kms_key.sns_kms_alias.arn
}

resource "aws_sns_topic_subscription" "alarms_to_slack" {
  count = local.is_primary_environment ? 1 : 0

  topic_arn  = aws_sns_topic.data_migration_sns_topic[0].arn
  protocol   = "lambda"
  endpoint   = data.aws_lambda_function.slack_notifier[0].arn
  depends_on = [aws_lambda_permission.allow_sns_invoke]
}

resource "aws_lambda_permission" "allow_sns_invoke" {
  count = local.is_primary_environment ? 1 : 0

  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = data.aws_lambda_function.slack_notifier[0].function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.data_migration_sns_topic[0].arn
}

data "aws_iam_policy_document" "data_migration_sns_topic_cloudwatch_policy" {
  count = local.is_primary_environment ? 1 : 0
  statement {
    sid    = "AllowCloudWatchToPublish"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["cloudwatch.amazonaws.com"]
    }
    actions = [
      "SNS:Publish",
    ]
    resources = local.is_primary_environment ? [
      aws_sns_topic.data_migration_sns_topic[0].arn,
    ] : []
  }
}
resource "aws_sns_topic_policy" "data_migration_sns_topic_cloudwatch_policy" {
  count  = local.is_primary_environment ? 1 : 0
  arn    = aws_sns_topic.data_migration_sns_topic[0].arn
  policy = data.aws_iam_policy_document.data_migration_sns_topic_cloudwatch_policy[0].json
}
