resource "aws_sns_topic" "alarms" {
  name              = "${local.resource_prefix}-${var.sns_topic_name}"
  kms_master_key_id = data.aws_kms_key.sns_kms_key[0].arn

  tags = {
    Name = "${local.resource_prefix}-${var.sns_topic_name}"
  }
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
