resource "aws_sns_topic" "alarms" {
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
  arn    = aws_sns_topic.alarms.arn
  policy = data.aws_iam_policy_document.alarms_cloudwatch_policy.json
}
