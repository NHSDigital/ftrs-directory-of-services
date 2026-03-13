resource "aws_sns_topic" "alarms" {
  provider = aws.sns

  name              = var.sns_topic_name
  display_name      = var.sns_display_name
  kms_master_key_id = var.kms_key_id

  tags = var.tags
}

data "aws_iam_policy_document" "alarms_cloudwatch_policy" {
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
    resources = [
      aws_sns_topic.alarms.arn,
    ]
  }
}

resource "aws_sns_topic_policy" "alarms" {
  provider = aws.sns

  arn    = aws_sns_topic.alarms.arn
  policy = data.aws_iam_policy_document.alarms_cloudwatch_policy.json
}

# The subscription is created in the SNS topic's region (aws.sns).
# When aws.sns differs from aws.lambda (e.g. SNS in us-east-1, Lambda in eu-west-2)
# AWS supports cross-region SNS → Lambda subscriptions.
resource "aws_sns_topic_subscription" "alarms_to_slack" {
  provider = aws.sns

  topic_arn = aws_sns_topic.alarms.arn
  protocol  = "lambda"
  endpoint  = data.aws_lambda_function.slack_notifier.arn

  depends_on = [aws_lambda_permission.allow_sns_invoke]
}
